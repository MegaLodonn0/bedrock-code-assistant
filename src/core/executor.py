import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from src.config.settings import settings
from src.core.security.config import BedrockHardened
from src.core.security.docker_sandbox import DockerSandbox
from src.core.security.hitl_gate import HITLGate
from src.core.analysis.call_graph import DependencyAnalyzer
from src.core.security.cost_monitor import CostMonitor
import json

logger = logging.getLogger(__name__)

class Executor:
    def __init__(self):
        self.bedrock = BedrockHardened()
        self.sandbox = DockerSandbox(settings.docker_image)
        self.analyzer = DependencyAnalyzer()
        self.cost_monitor = CostMonitor()

    async def ask_ai(self, query: str, model_id: Optional[str] = None):
        model_id = model_id or settings.bedrock_models.get(settings.default_model, 'amazon.nova-lite-v1:0')
        response = self.bedrock.invoke(model_id, query)
        # Estimate tokens (for cost monitor)
        self.cost_monitor.update(model_id, len(query.split()) * 1.3, len(response.split()) * 1.3)
        return response

    async def analyze_file(self, filepath: str):
        try:
            if not os.path.exists(filepath):
                return f"⌸ File not found: {filepath}"
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            impact = self.analyzer.get_impact_files(filepath)
            prompt = f"Analyze this code:\n\n{content}\n\nIt affects these files: {impact}\n\n Provide insights and suggest improvements."
            return await self.ask_ai(prompt)
        except Exception as e:
            return f"⌼ Error analyzing file: {e}"
    
    async def execute_code(self, code: str):
        return self.sandbox.execute(code)
