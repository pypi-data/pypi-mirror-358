"""
Configuration management for the Binalyze AIR SDK.
"""

import os
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class PaginationConfig(BaseModel):
    """Pagination configuration."""
    default_page_size: int = Field(default=10, description="Default page size")
    max_page_size: int = Field(default=100, description="Maximum page size")
    default_sort_by: str = Field(default="createdAt", description="Default sort field")
    default_sort_type: str = Field(default="ASC", description="Default sort type")


class EndpointConfig(BaseModel):
    """API endpoint configuration."""
    acquisitions: Dict[str, str] = Field(default_factory=dict)
    assets: Dict[str, str] = Field(default_factory=dict)
    audit: Dict[str, str] = Field(default_factory=dict)
    auth: Dict[str, str] = Field(default_factory=dict)
    auto_asset_tags: Dict[str, str] = Field(default_factory=dict)
    baseline: Dict[str, str] = Field(default_factory=dict)
    cases: Dict[str, str] = Field(default_factory=dict)
    policies: Dict[str, str] = Field(default_factory=dict)
    tasks: Dict[str, str] = Field(default_factory=dict)
    task_assignments: Dict[str, str] = Field(default_factory=dict)
    triage_rules: Dict[str, str] = Field(default_factory=dict)
    organizations: Dict[str, str] = Field(default_factory=dict)
    users: Dict[str, str] = Field(default_factory=dict)
    repositories: Dict[str, str] = Field(default_factory=dict)


class DefaultFiltersConfig(BaseModel):
    """Default filter configuration."""
    organization_ids: List[int] = Field(default=[0])
    all_organizations: bool = Field(default=True)
    managed_status: List[str] = Field(default=["managed"])
    online_status: List[str] = Field(default=["online"])
    sort_type: str = Field(default="ASC")


class TaskDefaultsConfig(BaseModel):
    """Task default configuration."""
    cpu_limit: int = Field(default=80)
    enable_compression: bool = Field(default=True)
    enable_encryption: bool = Field(default=False)
    bandwidth_limit: int = Field(default=100000)
    chunk_size: int = Field(default=1048576)
    chunk_count: int = Field(default=0)
    start_offset: int = Field(default=0)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file: str = Field(default="air_sdk.log")
    max_file_size: str = Field(default="10MB")
    backup_count: int = Field(default=5)


class CacheConfig(BaseModel):
    """Cache configuration."""
    enabled: bool = Field(default=True)
    ttl: int = Field(default=300)
    max_size: int = Field(default=1000)


class RateLimitingConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = Field(default=True)
    requests_per_minute: int = Field(default=100)
    burst_size: int = Field(default=10)


class AIRConfig(BaseModel):
    """Configuration for the AIR SDK."""
    
    host: str = Field(..., description="AIR instance host URL")
    api_token: str = Field(..., description="API token for authentication")
    api_prefix: str = Field(default="api/public", description="API prefix path")
    organization_id: int = Field(default=0, description="Default organization ID")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")
    retry_attempts: int = Field(default=3, description="Number of retry attempts for failed requests")
    retry_delay: float = Field(default=1.0, description="Delay between retry attempts")
    
    # Enhanced configuration sections
    pagination: PaginationConfig = Field(default_factory=PaginationConfig)
    endpoints: EndpointConfig = Field(default_factory=EndpointConfig)
    default_filters: DefaultFiltersConfig = Field(default_factory=DefaultFiltersConfig)
    task_defaults: TaskDefaultsConfig = Field(default_factory=TaskDefaultsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limiting: RateLimitingConfig = Field(default_factory=RateLimitingConfig)
    
    @field_validator("host")
    @classmethod
    def validate_host(cls, v):
        """Ensure host URL is properly formatted."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Host must start with http:// or https://")
        return v.rstrip("/")
    
    @field_validator("api_token")
    @classmethod
    def validate_api_token(cls, v):
        """Ensure API token is not empty."""
        if not v or not v.strip():
            raise ValueError("API token cannot be empty")
        return v.strip()
    
    @property
    def base_url(self) -> str:
        """Get the full base URL for API requests."""
        return f"{self.host}/{self.api_prefix}"
    
    def get_endpoint(self, category: str, endpoint: str) -> str:
        """Get a specific endpoint URL."""
        category_endpoints = getattr(self.endpoints, category, {})
        if isinstance(category_endpoints, dict):
            return category_endpoints.get(endpoint, "")
        return ""
    
    def get_full_endpoint_url(self, category: str, endpoint: str, **kwargs) -> str:
        """Get the full URL for an endpoint with substitutions."""
        endpoint_path = self.get_endpoint(category, endpoint)
        if not endpoint_path:
            raise ValueError(f"Endpoint not found: {category}.{endpoint}")
        
        # Substitute path parameters
        full_path = endpoint_path.format(**kwargs)
        return f"{self.base_url}{full_path}"
    
    @classmethod
    def from_environment(cls) -> "AIRConfig":
        """Create configuration from environment variables."""
        config_data = {
            "host": os.getenv("AIR_HOST", ""),
            "api_token": os.getenv("AIR_API_TOKEN", ""),
            "api_prefix": os.getenv("AIR_API_PREFIX", "api/public"),
            "organization_id": int(os.getenv("AIR_ORGANIZATION_ID", "0")),
            "timeout": int(os.getenv("AIR_TIMEOUT", "30")),
            "verify_ssl": os.getenv("AIR_VERIFY_SSL", "true").lower() == "true",
            "retry_attempts": int(os.getenv("AIR_RETRY_ATTEMPTS", "3")),
            "retry_delay": float(os.getenv("AIR_RETRY_DELAY", "1.0")),
        }
        
        return cls(**config_data)
    
    @classmethod
    def from_file(cls, config_path: str = "config.json") -> "AIRConfig":
        """Create configuration from JSON file."""
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            return cls(**config_data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    @classmethod
    def create(
        cls,
        host: Optional[str] = None,
        api_token: Optional[str] = None,
        organization_id: Optional[int] = None,
        config_file: Optional[str] = None,
        **kwargs
    ) -> "AIRConfig":
        """Create configuration with precedence: params > env vars > config file."""
        config_data = {}
        
        # 1. Try config file first (lowest precedence)
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass  # Ignore file errors, will try other methods
        elif os.path.exists("config.json"):
            # Try default config.json
            try:
                with open("config.json", "r") as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # 2. Override with environment variables
        env_config = {}
        if os.getenv("AIR_HOST"):
            env_config["host"] = os.getenv("AIR_HOST")
        if os.getenv("AIR_API_TOKEN"):
            env_config["api_token"] = os.getenv("AIR_API_TOKEN")
        if os.getenv("AIR_API_PREFIX"):
            env_config["api_prefix"] = os.getenv("AIR_API_PREFIX")
        
        org_id_env = os.getenv("AIR_ORGANIZATION_ID")
        if org_id_env:
            env_config["organization_id"] = int(org_id_env)
            
        timeout_env = os.getenv("AIR_TIMEOUT")
        if timeout_env:
            env_config["timeout"] = int(timeout_env)
            
        verify_ssl_env = os.getenv("AIR_VERIFY_SSL")
        if verify_ssl_env:
            env_config["verify_ssl"] = verify_ssl_env.lower() == "true"
            
        retry_attempts_env = os.getenv("AIR_RETRY_ATTEMPTS")
        if retry_attempts_env:
            env_config["retry_attempts"] = int(retry_attempts_env)
            
        retry_delay_env = os.getenv("AIR_RETRY_DELAY")
        if retry_delay_env:
            env_config["retry_delay"] = float(retry_delay_env)
        
        config_data.update(env_config)
        
        # 3. Override with explicit parameters (highest precedence)
        if host is not None:
            config_data["host"] = host
        if api_token is not None:
            config_data["api_token"] = api_token
        if organization_id is not None:
            config_data["organization_id"] = organization_id
        
        # Add any additional kwargs
        config_data.update(kwargs)
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()
    
    def save_to_file(self, config_path: str = "config.json") -> None:
        """Save configuration to JSON file."""
        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2) 