import json

class CostMonitor:
    PRICING = {'claude-v3-5-sonnet': {'input': 0.003, 'output': 0.015}, 'nova-micro': {'input': 0.0001, 'output': 0.0004}, 'default': {'input': 0.001, 'output': 0.005}}

    def __init__(self):
        self.total_cost = 0.0
        self.total_tokens = 0

    def update(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        price = self.PRICING.get(next((k for k in self.PRICING if k in model_id), 'default'))
        cost = (input_tokens / 1000 * price['input']) + (output_tokens / 1000 * price['output'])
        self.total_cost += cost
        self.total_tokens += (input_tokens + output_tokens)
        return cost

    def get_summary(self) -> str:
        return f'[COST] Total Tokens: {self.total_tokens} | Total Est. Cost: '
