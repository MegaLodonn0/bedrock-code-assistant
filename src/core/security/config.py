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
        try:
            # Try to create session but don't fail if credentials missing
            self.session = AWSSecurity.get_session(profile_name)
            # Only mark as available if we can create client
            self.client = self.session.client('bedrock-runtime', region_name='us-east-1')
            self.available = True
        except Exception as e:
            logger.debug(f"Bedrock not available: {e}")
            # Silently fail - we'll use mock mode

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