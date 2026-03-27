"""AWS Bedrock client and integration"""

import json
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from config import get_config


class BedrockClient:
    """Client for AWS Bedrock API"""
    
    def __init__(self, config=None):
        """
        Initialize Bedrock client.
        
        Args:
            config: Config instance. If None, uses global config.
        """
        self.config = config or get_config()
        self._bedrock_client = None
        self._runtime_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize boto3 Bedrock clients"""
        try:
            aws_config = self.config.aws
            
            self._bedrock_client = boto3.client(
                'bedrock',
                region_name=aws_config.get('region', 'us-east-1'),
                aws_access_key_id=aws_config.get('access_key_id'),
                aws_secret_access_key=aws_config.get('secret_access_key')
            )
            
            self._runtime_client = boto3.client(
                'bedrock-runtime',
                region_name=aws_config.get('region', 'us-east-1'),
                aws_access_key_id=aws_config.get('access_key_id'),
                aws_secret_access_key=aws_config.get('secret_access_key')
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Bedrock clients: {e}")
    
    def list_models(self):
        """List available foundation models"""
        try:
            response = self._bedrock_client.list_foundation_models()
            return response.get('modelSummaries', [])
        except ClientError as e:
            raise RuntimeError(f"Failed to list models: {e.response['Error']['Message']}")
    
    def invoke_model(self, model_id: str, prompt: str, **kwargs):
        """
        Invoke a model with a prompt.
        
        Args:
            model_id: The model ID to invoke
            prompt: The prompt/message to send
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            The model's response text
        """
        try:
            bedrock_config = self.config.bedrock
            max_tokens = kwargs.get('max_tokens', bedrock_config.get('max_tokens', 2048))
            temperature = kwargs.get('temperature', bedrock_config.get('temperature', 0.7))
            
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
            else:
                request_body = {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            
            response = self._runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'claude' in model_id:
                return response_body['content'][0]['text']
            else:
                return response_body.get('completion', response_body.get('text', ''))
        
        except ClientError as e:
            raise RuntimeError(f"Model invocation failed: {e.response['Error']['Message']}")
        except BotoCoreError as e:
            raise RuntimeError(f"AWS error: {str(e)}")
    
    @property
    def bedrock_client(self):
        """Get raw bedrock client"""
        return self._bedrock_client
    
    @property
    def runtime_client(self):
        """Get raw runtime client"""
        return self._runtime_client
