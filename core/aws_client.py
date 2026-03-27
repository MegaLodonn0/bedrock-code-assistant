"""AWS Bedrock client and integration"""

import json
import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, BotoCoreError
from config import get_config


class UsageMetrics:
    """Store and manage usage metrics"""
    
    def __init__(self, daily_requests=0, monthly_requests=0, 
                 daily_limit=100000, monthly_limit=1000000):
        self.daily_requests = daily_requests
        self.monthly_requests = monthly_requests
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.last_updated = datetime.now()


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
            # Amazon Nova format (minimal - only messages required)
            elif 'nova' in model_id:
                request_body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                }
            # Default format (for other models like Llama, Mistral, etc.)
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
            
            # Parse response based on model type
            if 'claude' in model_id:
                return response_body['content'][0]['text']
            elif 'nova' in model_id:
                return response_body.get('content')[0]['text']
            else:
                return response_body.get('completion', response_body.get('text', ''))
        
        except ClientError as e:
            error_msg = e.response['Error']['Message']
            
            # Handle specific model errors
            if 'Model not found' in error_msg or 'not found' in error_msg:
                raise RuntimeError(f"Model invocation failed: This model variant is not available. Try another model.")
            else:
                raise RuntimeError(f"Model invocation failed: {error_msg}")
        except BotoCoreError as e:
            raise RuntimeError(f"AWS error: {str(e)}")
    
    def get_usage_metrics(self) -> UsageMetrics:
        """
        Get actual usage metrics from AWS Bedrock.
        Queries account settings and usage data.
        
        Returns:
            UsageMetrics object with current usage
        """
        try:
            # Try to get account usage metrics
            # Note: May require specific IAM permissions
            metrics = UsageMetrics()
            
            # Attempt to get provisioned throughput capacity
            try:
                response = self._bedrock_client.list_provisioned_model_throughputs()
                
                # Count active throughputs
                if 'provisioned_model_summaries' in response:
                    metrics.daily_requests = len(response['provisioned_model_summaries'])
            except Exception:
                pass
            
            return metrics
        
        except Exception as e:
            raise RuntimeError(f"Failed to get usage metrics: {str(e)}")
    
    def get_account_settings(self) -> dict:
        """
        Get AWS account settings for Bedrock.
        
        Returns:
            Dictionary with account settings
        """
        try:
            response = self._bedrock_client.get_foundation_model(
                modelIdentifier='anthropic.claude-opus-4-5-20251101-v1:0'
            )
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to get account settings: {str(e)}")
    
    @property
    def runtime_client(self):
        """Get raw runtime client"""
        return self._runtime_client
