import json
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".kodo_context"
        self.config_file = self.config_dir / "settings.json"
        self.console = Console()
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def ensure_config_dir(self):
        """Ensure config directory exists"""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
            else:
                self._config = self.get_default_config()
            return self._config
        except Exception as e:
            self.console.print(f"Error loading config: {e}")
            self._config = self.get_default_config()
            return self._config
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            self.ensure_config_dir()
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            self.console.print(f"Error saving config: {e}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "llm": {
                "provider": None,
                "model": None,
                "api_key": None,
                "base_url": None
            },
            "behavior": {
                "auto_backup": True,
                "require_confirmation": True,
                "max_context_files": 10,
                "max_file_size": 10240
            },
            "version": "1.0.0"
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        return self.save_config()
    
    def is_configured(self) -> bool:
        """Check if LLM provider is configured"""
        provider = self.get('kodo.llm.provider')
        api_key = self.get('kodo.llm.api_key')
        model = self.get('kodo.llm.model')
        
        if provider == 'ollama':
            return bool(provider and model)
        else:
            return bool(provider and api_key and model)
    
    def setup_interactive(self):
        """Interactive setup for LLM configuration"""
        from kodo.llm.providers import LLMManager
        
        llm_manager = LLMManager()
        
        self.console.print("\n🚀 Welcome to Kōdō CLI Setup!")
        self.console.print("Let's configure your LLM provider.\n")
        
        # Show available providers
        self.show_providers_table(llm_manager)
        
        # Get provider choice
        providers = list(llm_manager.get_available_providers().keys())
        provider_choice = Prompt.ask(
            "Choose your LLM provider",
            choices=providers,
            default="ollama"
        )
        
        # Get provider info for suggestions
        provider_info = llm_manager.get_provider_info(provider_choice)
        default_model = provider_info.get("default_model", "")
        description = provider_info.get("description", "")
        
        # Let user enter any model name
        self.console.print(f"\nEnter model name for {provider_choice}")
        if description:
            self.console.print(f"Available models: {description}")
        
        model_choice = Prompt.ask(
            f"Choose model for {provider_choice}",
            default=default_model
        )
        
        # Get provider-specific configuration
        config = {"model": model_choice}
        
        if provider_choice != "ollama":
            # API-based providers need API key
            api_key = Prompt.ask(f"Enter your {provider_choice.upper()} API key", password=True)
            config["api_key"] = api_key
        else:
            # Ollama needs base URL
            base_url = Prompt.ask(
                "Enter Ollama base URL",
                default="http://localhost:11434"
            )
            config["base_url"] = base_url
        
        # Test the configuration
        self.console.print("\n🧪 Testing configuration...")
        try:
            provider = llm_manager.create_provider(provider_choice, config)
            llm_manager.set_provider(provider)
            
            # Test with a simple query
            test_response = llm_manager.get_completion([
                {"role": "user", "content": "Say 'Configuration test successful!'"}
            ])
            
            self.console.print("Configuration test passed!")
            
        except Exception as e:
            self.console.print(f"Configuration test failed: {e} \n If you are using Ollama, make sure it is running and the model is available. If you are using Huggingface, use models listed here: https://huggingface.co/models?pipeline_tag=text-generation&inference_provider=hf-inference&sort=modified")
            if not Confirm.ask("Save configuration anyway?"):
                return False
        
        # Save configuration
        self.set('kodo.llm.provider', provider_choice)
        self.set('kodo.llm.model', model_choice)
        
        if provider_choice != "ollama":
            self.set('kodo.llm.api_key', api_key)
            self.set('kodo.llm.base_url', None)
        else:
            self.set('kodo.llm.api_key', None)
            self.set('kodo.llm.base_url', base_url)
        
        self.console.print("Configuration saved successfully!")
        self.console.print(f"Config location: {self.config_file}")
        
        return True
    
    def show_providers_table(self, llm_manager):
        """Show available providers in a table"""
        table = Table(title="Available LLM Providers")
        table.add_column("Key", style="cyan")
        table.add_column("Name", style="green") 
        table.add_column("Type", style="yellow")
        table.add_column("Example Models", style="magenta")
        
        for key in llm_manager.get_available_providers().keys():
            provider_info = llm_manager.get_provider_info(key)
            name = provider_info.get("name", "")
            description = provider_info.get("description", "")
            provider_type = "Local" if key == "ollama" else "API"
            
            table.add_row(key, name, provider_type, description)
        
        self.console.print(table)
        self.console.print("\n💡 You can enter any model name supported by the provider!")
        self.console.print("If the model doesn't exist, LiteLLM will show you an error with available options.")
        self.console.print()
    
    def show_current_config(self):
        """Display current configuration"""
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        provider = self.get('kodo.llm.provider', 'Not configured')
        model = self.get('kodo.llm.model', 'Not configured')
        api_key = self.get('kodo.llm.api_key')
        base_url = self.get('kodo.llm.base_url')
        
        table.add_row("Provider", provider)
        table.add_row("Model", model)
        
        if api_key:
            masked_key = f"{api_key[:8]}..." if len(api_key) > 8 else "***"
            table.add_row("API Key", masked_key)
        
        if base_url:
            table.add_row("Base URL", base_url)
        
        table.add_row("Auto Backup", str(self.get('behavior.auto_backup', True)))
        table.add_row("Require Confirmation", str(self.get('behavior.require_confirmation', True)))
        
        self.console.print(table)
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for provider creation"""
        config = {}
        
        provider = self.get('kodo.llm.provider')
        if not provider:
            return config
        
        config['model'] = self.get('kodo.llm.model')
        
        if provider != 'ollama':
            config['api_key'] = self.get('kodo.llm.api_key')
        else:
            config['base_url'] = self.get('kodo.llm.base_url', 'http://localhost:11434')
        
        return config