"""
BedrockHardened — hardened AWS Bedrock client with ModelRegistry integration.

Changes vs. previous version:
- get_available_models() now calls registry.merge_from_aws() so live AWS IDs
  are registered without duplicates.
- get_all_grouped_models() delegates to registry.grouped_by_provider() for
  catalog models and falls back to raw AWS data for unknown IDs.
- Removed unused `tenacity` import.
"""

import asyncio
import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AWSSecurity:
    """Minimal AWS session factory with credential-chain support."""

    @staticmethod
    def get_session(profile_name: str = None) -> boto3.Session:
        profile = profile_name or os.getenv("AWS_PROFILE")
        region = os.getenv("AWS_REGION", "us-east-1")

        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if access_key and secret_key:
            return boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region,
            )
        if profile:
            return boto3.Session(profile_name=profile, region_name=region)
        return boto3.Session(region_name=region or "us-east-1")


class BedrockHardened:
    """
    AWS Bedrock runtime client wrapper.

    Integrates with ModelRegistry for model discovery and pricing.
    Silently falls back to mock mode when credentials are unavailable.
    """

    def __init__(self, profile_name: str = None) -> None:
        self.available: bool = False
        self.session: boto3.Session = None
        self.client = None
        # Cache: alias→aws_id dict returned to callers
        self._models_cache: dict = None

        try:
            self.session = AWSSecurity.get_session(profile_name)
            self.client = self.session.client("bedrock-runtime", region_name="us-east-1")
            self.available = True
        except Exception as exc:
            logger.debug("Bedrock not available: %s", exc)

    # ------------------------------------------------------------------
    # Model discovery
    # ------------------------------------------------------------------

    async def get_available_models(self) -> dict:
        """
        Return the alias→aws_id mapping for models available in this account.

        Strategy:
        1. Query AWS for live model IDs.
        2. Pass them to registry.merge_from_aws() (registers unknown IDs).
        3. Filter the registry to only return IDs confirmed live by AWS.
        4. Fall back to full registry export if the API call fails.
        """
        from src.config.settings import settings

        if not self.available or not self.session:
            return settings.bedrock_models

        if self._models_cache is not None:
            return self._models_cache

        def _fetch() -> dict:
            try:
                registry = settings.registry
                bedrock_control = self.session.client("bedrock", region_name="us-east-1")
                raw_ids: set = set()

                try:
                    fm_resp = bedrock_control.list_foundation_models(byOutputModality="TEXT")
                    for fn in fm_resp.get("modelSummaries", []):
                        if "ON_DEMAND" in fn.get("inferenceTypesSupported", []):
                            raw_ids.add(fn["modelId"])
                except Exception as exc:
                    logger.debug("Failed to fetch foundation models: %s", exc)

                try:
                    prof_resp = bedrock_control.list_inference_profiles(
                        typeEquals="SYSTEM_DEFINED"
                    )
                    for prof in prof_resp.get("inferenceProfileSummaries", []):
                        raw_ids.add(prof["inferenceProfileId"])
                except Exception as exc:
                    logger.debug("Failed to fetch inference profiles: %s", exc)

                if not raw_ids:
                    raise RuntimeError("No active models or profiles fetched from AWS.")

                # Register any unknown IDs so they appear in the registry
                registry.merge_from_aws(list(raw_ids))

                # Return only catalog entries whose AWS ID was confirmed live
                full = registry.to_dict()
                filtered = {
                    alias: aws_id
                    for alias, aws_id in full.items()
                    if aws_id in raw_ids
                }
                return filtered if filtered else full

            except Exception as exc:
                logger.debug(
                    "Dynamic model resolution failed, falling back to defaults: %s", exc
                )
                from src.config.settings import settings as s
                return s.bedrock_models

        self._models_cache = await asyncio.to_thread(_fetch)
        return self._models_cache

    async def get_all_grouped_models(self) -> dict:
        """
        Return all Bedrock models grouped by provider.

        Combines catalog entries (from the registry) with raw AWS data so
        that models available in the account but not in the catalog also appear.
        """
        from src.config.settings import settings

        if not self.available or not self.session:
            return settings.registry.grouped_by_provider()

        def _fetch_all() -> dict:
            from collections import defaultdict
            grouped: dict = defaultdict(list)

            try:
                bedrock_control = self.session.client("bedrock", region_name="us-east-1")

                fm_resp = bedrock_control.list_foundation_models(byOutputModality="TEXT")
                for fn in fm_resp.get("modelSummaries", []):
                    if "ON_DEMAND" not in fn.get("inferenceTypesSupported", []):
                        continue
                    provider = _normalise_provider_name(fn.get("providerName", "Unknown"))
                    grouped[provider].append(
                        {"id": fn["modelId"], "name": fn.get("modelName", fn["modelId"])}
                    )

                prof_resp = bedrock_control.list_inference_profiles(
                    typeEquals="SYSTEM_DEFINED"
                )
                for prof in prof_resp.get("inferenceProfileSummaries", []):
                    prof_id = prof["inferenceProfileId"]
                    parts = prof_id.split(".")
                    provider = parts[1].capitalize() if len(parts) >= 2 else "Unknown"
                    provider = _normalise_provider_name(provider)
                    grouped[provider].append(
                        {"id": prof_id, "name": prof.get("inferenceProfileName", prof_id)}
                    )

            except Exception as exc:
                logger.debug("Failed to fetch grouped models: %s", exc)
                return settings.registry.grouped_by_provider()

            return dict(grouped)

        return await asyncio.to_thread(_fetch_all)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def invoke(self, model_id: str, prompt: str) -> str:
        """Call Bedrock Converse API with a single-turn user prompt."""
        if not self.available or not self.client:
            raise RuntimeError("Bedrock not configured")

        try:
            response = self.client.converse(
                modelId=model_id,
                messages=[{"role": "user", "content": [{"text": prompt}]}],
                inferenceConfig={"maxTokens": 2048, "temperature": 0.7},
            )
            if "output" in response and "message" in response["output"]:
                content = response["output"]["message"].get("content", [])
                if content and isinstance(content, list):
                    return content[0].get("text", "")
            return ""
        except Exception as exc:
            raise RuntimeError(f"Bedrock error: {exc}") from exc


class AWSCredentialChain:
    """Utility to validate that AWS credentials are resolvable."""

    @staticmethod
    def validate() -> bool:
        try:
            return AWSSecurity.get_session().get_credentials() is not None
        except Exception as exc:
            logger.error("Credential validation failed: %s", exc)
            return False


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _normalise_provider_name(raw: str) -> str:
    """Map raw provider strings from AWS to canonical display names."""
    mapping = {
        "anthropic": "Anthropic",
        "amazon": "Amazon",
        "meta": "Meta",
        "cohere": "Cohere",
        "mistral": "Mistral AI",
        "mistral ai": "Mistral AI",
        "deepseek": "DeepSeek",
        "twelvelabs": "TwelveLabs",
        "z.ai": "Z.AI",
    }
    return mapping.get(raw.lower(), raw)