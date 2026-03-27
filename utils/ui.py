"""Advanced UI components for model selection and display"""

from typing import List, Dict, Tuple
from utils.output import Colors


class ModelSelector:
    """Interactive model selection UI"""
    
    def __init__(self, models: List[Dict]):
        """
        Initialize model selector.
        
        Args:
            models: List of model dictionaries from Bedrock
        """
        self.models = models
        self.providers = self._group_by_provider()
    
    def _group_by_provider(self) -> Dict[str, List[Dict]]:
        """Group models by provider"""
        providers = {}
        for model in self.models:
            provider = model.get('providerName', 'Unknown')
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model)
        return dict(sorted(providers.items()))
    
    def select_provider(self) -> Tuple[str, List[Dict]]:
        """
        Show provider selection menu.
        
        Returns:
            Tuple of (provider_name, provider_models)
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}Select Provider:{Colors.END}\n")
        
        provider_list = list(self.providers.keys())
        for i, provider in enumerate(provider_list, 1):
            count = len(self.providers[provider])
            print(f"  {Colors.BOLD}{i}{Colors.END}. {provider} ({count} models)")
        
        while True:
            try:
                choice = input(f"\n{Colors.YELLOW}Choose provider (1-{len(provider_list)}): {Colors.END}")
                idx = int(choice) - 1
                if 0 <= idx < len(provider_list):
                    provider = provider_list[idx]
                    return provider, self.providers[provider]
                else:
                    print(f"{Colors.RED}Invalid selection{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number{Colors.END}")
    
    def select_model(self, provider: str = None) -> Dict:
        """
        Show model selection menu with detailed formatting.
        
        Args:
            provider: If specified, show only models from this provider
        
        Returns:
            Selected model dictionary
        """
        if provider:
            models = self.providers.get(provider, [])
            provider_name = provider
        else:
            provider_name, models = self.select_provider()
        
        self._display_models(models, provider_name)
        
        while True:
            try:
                choice = input(f"\n{Colors.YELLOW}Choose model (1-{len(models)}): {Colors.END}")
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    return models[idx]
                else:
                    print(f"{Colors.RED}Invalid selection{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number{Colors.END}")
    
    def _display_models(self, models: List[Dict], provider: str):
        """Display models with formatted list view"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{provider} Models:{Colors.END}\n")
        
        for i, model in enumerate(models, 1):
            model_id = model.get('modelId', 'N/A')
            model_name = model.get('modelName', 'N/A')
            
            print(f"  {Colors.BOLD}{i}{Colors.END}. {Colors.GREEN}{model_name}{Colors.END}")
            print(f"     {Colors.CYAN}ID: {model_id}{Colors.END}")
            
            if i < len(models):
                print(f"  {Colors.CYAN}{'-' * 60}{Colors.END}")
            
            print()


class UsageTracker:
    """Track and display API usage limits"""
    
    def __init__(self):
        """Initialize usage tracker"""
        self.daily_requests = 0
        self.daily_limit = 1000  # Default limit
        self.monthly_requests = 0
        self.monthly_limit = 100000  # Default limit
    
    def increment_request(self):
        """Increment request counters"""
        self.daily_requests += 1
        self.monthly_requests += 1
    
    def get_daily_usage_percentage(self) -> int:
        """Get daily usage as percentage"""
        return int((self.daily_requests / self.daily_limit) * 100)
    
    def get_monthly_usage_percentage(self) -> int:
        """Get monthly usage as percentage"""
        return int((self.monthly_requests / self.monthly_limit) * 100)
    
    def get_usage_bar(self, percentage: int, width: int = 10) -> str:
        """Get visual usage bar"""
        filled = int((percentage / 100) * width)
        empty = width - filled
        
        if percentage < 50:
            color = Colors.GREEN
        elif percentage < 80:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        return f"{color}[{'=' * filled}{'-' * empty}]{Colors.END} {percentage}%"
    
    def display_usage_right_panel(self, terminal_width: int = 80):
        """Display usage panel on right side of terminal"""
        panel_width = 20
        right_padding = terminal_width - panel_width
        
        daily_pct = self.get_daily_usage_percentage()
        monthly_pct = self.get_monthly_usage_percentage()
        
        # Daily usage
        daily_bar = self.get_usage_bar(daily_pct, width=8)
        daily_text = f"Daily: {self.daily_requests}/{self.daily_limit}"
        
        # Monthly usage
        monthly_bar = self.get_usage_bar(monthly_pct, width=8)
        monthly_text = f"Monthly: {self.monthly_requests}/{self.monthly_limit}"
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}Usage Limits:{Colors.END}")
        print(f"  {daily_text:.<20} {daily_bar}")
        print(f"  {monthly_text:.<20} {monthly_bar}")


class TableFormatter:
    """Format data as tables with separators"""
    
    @staticmethod
    def format_models_table(models: List[Dict]) -> str:
        """Format models as a table with separator lines"""
        output = []
        
        # Header
        header = f"{Colors.BOLD}{Colors.CYAN}{'#':<3} {'Model Name':<40} {'Provider':<20}{Colors.END}"
        output.append(header)
        output.append(f"{Colors.CYAN}{'-' * 65}{Colors.END}")
        
        # Rows
        for i, model in enumerate(models, 1):
            model_name = model.get('modelName', 'N/A')[:38]
            provider = model.get('providerName', 'N/A')[:18]
            
            row = f"{i:<3} {model_name:<40} {provider:<20}"
            output.append(row)
            
            if i < len(models):
                output.append(f"{Colors.CYAN}{'-' * 65}{Colors.END}")
        
        return "\n".join(output)
