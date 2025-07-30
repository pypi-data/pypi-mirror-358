"""
Configuration management for Cloudflare Images Migration Tool
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any


class Config:
    """Configuration manager for the migration tool."""
    
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """
        Initialize configuration from various sources.
        
        Priority order:
        1. Command line arguments (kwargs)
        2. Configuration file
        3. Environment variables
        4. Default values
        """
        
        # Load environment variables
        load_dotenv()
        
        # Default configuration
        self.defaults = {
            'account_id': None,
            'api_token': None,
            'output_dir': None,
            'dry_run': False,
            'backup': True,
            'file_types': [
                '.html', '.htm', '.css', '.js', '.jsx', '.ts', '.tsx',
                '.md', '.json', '.xml', '.yaml', '.yml', '.scss', '.sass', '.less'
            ],
            'exclude_dirs': [
                'node_modules', '.git', '.vscode', '.idea', '__pycache__',
                'venv', 'env', '.env', 'dist', 'build', 'target'
            ],
            'supported_image_formats': ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'],
            'max_file_size_mb': 10,
            'batch_size': 10,
            'retry_count': 3,
            'timeout': 30
        }
        
        # Load configuration from file
        if config_file:
            self._load_config_file(config_file)
        
        # Override with command line arguments
        self._load_from_kwargs(kwargs)
        
        # Load from environment variables
        self._load_from_env()
    
    def _load_config_file(self, config_file: str):
        """Load configuration from YAML file."""
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        for key, value in file_config.items():
                            if key in self.defaults:
                                setattr(self, key, value)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
    
    def _load_from_kwargs(self, kwargs: Dict[str, Any]):
        """Load configuration from command line arguments."""
        for key, value in kwargs.items():
            if value is not None:
                if key == 'file_types' and isinstance(value, str):
                    value = [ext.strip() for ext in value.split(',')]
                elif key == 'exclude_dirs' and isinstance(value, str):
                    value = [dir.strip() for dir in value.split(',')]
                setattr(self, key, value)
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'CLOUDFLARE_ACCOUNT_ID': 'account_id',
            'CLOUDFLARE_API_TOKEN': 'api_token',
            'CF_ACCOUNT_ID': 'account_id',
            'CF_API_TOKEN': 'api_token'
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value and not hasattr(self, config_key):
                setattr(self, config_key, env_value)
        
        # Set defaults for any missing values
        for key, default_value in self.defaults.items():
            if not hasattr(self, key):
                setattr(self, key, default_value)
    
    def validate(self) -> bool:
        """Validate configuration and return True if valid."""
        errors = []
        
        if not self.account_id:
            errors.append("Cloudflare Account ID is required")
        
        if not self.api_token:
            errors.append("Cloudflare API Token is required")
        
        if self.output_dir and not os.path.exists(os.path.dirname(self.output_dir)):
            errors.append(f"Output directory parent does not exist: {self.output_dir}")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def get_cloudflare_api_url(self) -> str:
        """Get the Cloudflare Images API URL."""
        return f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/images/v1"
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Cloudflare API requests."""
        return {
            'Authorization': f'Bearer {self.api_token}',
            'User-Agent': 'Cloudflare-Images-Migration-Tool/1.0'
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = {}
        for key in self.defaults.keys():
            config_dict[key] = getattr(self, key, self.defaults[key])
        return config_dict
    
    def save_config_template(self, file_path: str):
        """Save a configuration template file."""
        template_config = {
            'account_id': 'your_cloudflare_account_id',
            'api_token': 'your_cloudflare_api_token',
            'file_types': self.defaults['file_types'],
            'exclude_dirs': self.defaults['exclude_dirs'],
            'dry_run': False,
            'backup': True,
            'batch_size': 10,
            'retry_count': 3,
            'timeout': 30
        }
        
        with open(file_path, 'w') as f:
            yaml.dump(template_config, f, default_flow_style=False, indent=2)
        
        print(f"Configuration template saved to: {file_path}")
        print("Please edit the file with your Cloudflare credentials.") 