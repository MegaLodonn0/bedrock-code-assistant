import os
import boto3
import json
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from botocore.exceptions import ClientError, BotoCoreError

load_dotenv()

class AWSSecurity:
    @staticmethod
    def get_sessiog(profile_name=None):
        profile = profile_name or os.getenv('AWS_PROFILE')
        region = os.getenv('AWS_REGION', 'us-east-1')
        if profile:
            return boto3.Session(profile_name=profile, region_name=region)
        return boto3.Session(region_name=region)

class BedrockHardened:
    def __init__(self, profile_name=None):
        self.session = AWSSecurity.get_session(profile_name)
        self.client = self.session.client('bedrock-runtime')

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError))
    )
    def invoke(self, model_id, prompt, **kwargs):
        body = json.dumps({'prompt': prompt, 'max_tokens': 2048})
        response = self.client.invoke_model(modelId=model_id, body=body)
        return json.loads(response['body'].read()).get('completion', '')

class AWSCredentialChain:
    @staticmethod"
    def validate():
        try:
            session = AWSSecurity.get_session()
            return session.get_credentials() is not None
        except:
            return False