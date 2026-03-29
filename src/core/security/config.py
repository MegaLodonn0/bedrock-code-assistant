import os
import boto3
import json
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from botocore.exceptions import ClientError, BotoCoreError

load_dotenv()

class AWSSecurity:
    @staticmethod
    def get_session():
        return boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY_ID'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )

class BedrockHardened:
    def __init__(self):
        self.session = AWSSecurity.get_session()
        self.client = self.session.client('bedrock-runtime')

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ClientError, BotoCoreError))
    )
    def invoke(self, model_id: str, prompt: str, **kwargs):
        max_tokens = kwargs.get('max_tokens', 2048)
        temperature = kwargs.get('temperature', 0.7)

        # Claude (Anthropic) format
        if 'claude' in model_id:
            request_body = {
                "anthropic_version": "bedrock-2023-06-01",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        # Amazon Nova format
        elif 'nova' in model_id:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
        # Default format (for other models)
        else:
            request_body = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

        response = self.client.invoke_model(modelId=model_id, body=json.dumps(request_body))
        response_body = json.loads(response['body'].read())

        if 'claude' in model_id:
            return response_body['content'][0]['text']
        elif 'nova' in model_id:
            return response_body['output']['message']['content'][0]['text']
        else:
            return response_body.get('completion', response_body.get('text', ''))
