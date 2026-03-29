import os
import boto3
import json
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class AWSSecurity:
    @staticmethod
    def get_session():
        return boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )

class BedrockHardened:
    def __init__(self):
        self.client = AWSSecurity.get_session().client('bedrock-runtime')

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def invoke(self, model_id: str, prompt: str):
        body = json.dumps({'prompt': prompt, 'max_tokens': 2048})
        response = self.client.invoke_model(modelId=model_id, body=body)
        return json.loads(response['body'].read()).get('completion', '')
