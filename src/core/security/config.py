import os
import logging
import boto3
import json
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from botocore.exceptions import ClientError, BotoCoreError

load_dotenv()

logger = logging.getLogger(__name__)

class AWSSecurity:
    @staticmethod
    def get_session(profile_name=None):
        profile = profile_name or os.getenv('AWS_PROFILE')
        region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Try direct credentials first from .env
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if access_key and secret_key:
            # Use direct credentials
            return boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        elif profile:
            # Fall back to profile
            return boto3.Session(profile_name=profile, region_name=region)
        else:
            # Default session (credential chain)
            return boto3.Session(region_name=region or 'us-east-1')

class BedrockHardened:
    def __init__(self, profile_name=None):
        self.available = False
        self.session = None
        self.client = None
        self._models_cache = None
        try:
            # Try to create session but don't fail if credentials missing
            self.session = AWSSecurity.get_session(profile_name)
            # Only mark as available if we can create client
            self.client = self.session.client('bedrock-runtime', region_name='us-east-1')
            self.available = True
        except Exception as e:
            logger.debug(f"Bedrock not available: {e}")
            # Silently fail - we'll use mock mode

    async def get_available_models(self) -> dict:
        """Dynamically fetch Bedrock models the user has access to from AWS.
        Falls back to settings.bedrock_models if the list API fails or is blocked."""
        from src.config.settings import settings
        import asyncio
        
        if not self.available or not self.session:
            return settings.bedrock_models

        if self._models_cache is not None:
            return self._models_cache

        def _fetch():
            try:
                # The control plane client (differs from bedrock-runtime)
                bedrock_control = self.session.client('bedrock', region_name='us-east-1')
                raw_ids = set()
                
                # 1. Fetch Foundation Models (must support ON_DEMAND)
                try:
                    fm_resp = bedrock_control.list_foundation_models(byOutputModality="TEXT")
                    for fn in fm_resp.get("modelSummaries", []):
                        if "ON_DEMAND" in fn.get("inferenceTypesSupported", []):
                            raw_ids.add(fn["modelId"])
                except Exception as e:
                    logger.debug(f"Failed to fetch foundation models: {e}")

                # 2. Fetch Inference Profiles (Cross-Region)
                try:
                    prof_resp = bedrock_control.list_inference_profiles(typeEquals="SYSTEM_DEFINED")
                    for prof in prof_resp.get("inferenceProfileSummaries", []):
                        raw_ids.add(prof["inferenceProfileId"])
                except Exception as e:
                    logger.debug(f"Failed to fetch inference profiles: {e}")

                if not raw_ids:
                    raise RuntimeError("No active models or profiles fetched from AWS.")

                # 3. Intersection mapping: Match fetched physical IDs with our human-readable settings aliases
                filtered_models = {}
                for alias, aws_id in settings.bedrock_models.items():
                    if aws_id in raw_ids:
                        filtered_models[alias] = aws_id
                
                if not filtered_models:
                    filtered_models = settings.bedrock_models
                return filtered_models
            except Exception as e:
                logger.debug(f"Dynamic model resolution failed, falling back to defaults: {e}")
                return settings.bedrock_models

        # Run the blocking boto3 calls in a thread pool to avoid freezing the app
        self._models_cache = await asyncio.to_thread(_fetch)
        return self._models_cache

    async def get_all_grouped_models(self) -> dict:
        """Fetches all raw models and cross-region profiles from Bedrock 
        and groups them by their Provider Name."""
        import asyncio
        from collections import defaultdict
        
        if not self.available or not self.session:
            return {}

        def _fetch_all():
            grouped = defaultdict(list)
            try:
                bedrock_control = self.session.client('bedrock', region_name='us-east-1')
                
                # Fetch Foundation Models (Filtered for ON_DEMAND text)
                fm_resp = bedrock_control.list_foundation_models(byOutputModality="TEXT")
                for fn in fm_resp.get("modelSummaries", []):
                    if "ON_DEMAND" in fn.get("inferenceTypesSupported", []):
                        provider = fn.get("providerName", "Unknown")
                        if provider.lower() == "deepseek": provider = "DeepSeek"
                        elif provider.lower() == "mistral" or provider.lower() == "mistral ai": provider = "Mistral AI"
                        elif provider.lower() == "twelvelabs": provider = "TwelveLabs"
                        elif provider.lower() == "z.ai": provider = "Z.AI"
                        
                        item = {"id": fn["modelId"], "name": fn.get("modelName", fn["modelId"])}
                        grouped[provider].append(item)

                # Fetch Inference Profiles
                prof_resp = bedrock_control.list_inference_profiles(typeEquals="SYSTEM_DEFINED")
                for prof in prof_resp.get("inferenceProfileSummaries", []):
                    prof_id = prof["inferenceProfileId"]
                    parts = prof_id.split('.')
                    provider = "Unknown"
                    if len(parts) >= 2:
                        prov_str = parts[1].lower()
                        if prov_str == "anthropic": provider = "Anthropic"
                        elif prov_str == "amazon": provider = "Amazon"
                        elif prov_str == "meta": provider = "Meta"
                        elif prov_str == "cohere": provider = "Cohere"
                        elif prov_str == "mistral": provider = "Mistral AI"
                        elif prov_str == "deepseek": provider = "DeepSeek"
                        elif prov_str == "twelvelabs": provider = "TwelveLabs"
                        else: provider = parts[1].capitalize()
                    
                    item = {"id": prof_id, "name": prof.get("inferenceProfileName", prof_id)}
                    grouped[provider].append(item)

            except Exception as e:
                logger.debug(f"Failed to fetch grouped models: {e}")

            return dict(grouped)

        # Execute off-thread
        return await asyncio.to_thread(_fetch_all)


    def invoke(self, model_id, prompt, **kwargs):
        if not self.available or not self.client:
            raise RuntimeError("Bedrock not configured")
        
        try:
            # Use messages format with proper parameters for Bedrock Converse API
            response = self.client.converse(
                modelId=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 2048,
                    "temperature": 0.7
                }
            )
            
            # Extract text from response
            if "output" in response and "message" in response["output"]:
                content = response["output"]["message"].get("content", [])
                if content and isinstance(content, list):
                    return content[0].get("text", "")
            
            return ""
        except Exception as e:
            raise RuntimeError(f"Bedrock error: {e}")

class AWSCredentialChain:
    @staticmethod
    def validate():
        try:
            return AWSSecurity.get_session().get_credentials() is not None
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False