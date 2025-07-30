from pathlib import Path
from maleo_foundation.models.transfers.general.configurations.cache.redis import (
    RedisCacheNamespaces,
    RedisCacheConfigurations
)
from maleo_foundation.models.transfers.general.configurations.cache \
    import CacheConfigurations
from maleo_foundation.models.transfers.general.configurations.database \
    import DatabaseConfigurations
from maleo_foundation.models.transfers.general.configurations import (
    RuntimeConfigurations,
    StaticConfigurations,
    Configurations
)
from maleo_foundation.models.transfers.general.settings import Settings
from maleo_foundation.utils.loaders.yaml import YAMLLoader
from maleo_foundation.utils.merger import deep_merge
from .credential import CredentialManager

class ConfigurationManager:
    def __init__(
        self,
        settings: Settings,
        credential_manager: CredentialManager
    ):
        self.settings = settings
        self.credential_manager = credential_manager

        self._load_configurations()

    def _load_static_configurations(self) -> StaticConfigurations:
        config_path = Path(self.settings.STATIC_CONFIGURATIONS_PATH)
        
        if config_path.exists() and config_path.is_file():
            data = YAMLLoader.load_from_path(str(config_path))
        else:
            secret_data = self.credential_manager.secret_manager.get(
                f"maleo-static-configurations-{self.settings.ENVIRONMENT}"
            )
            data = YAMLLoader.load_from_string(secret_data)
        
        return StaticConfigurations.model_validate(data)
    
    def _load_runtime_configurations(self) -> RuntimeConfigurations:
        config_path = Path(self.settings.RUNTIME_CONFIGURATIONS_PATH)
        
        if config_path.exists() and config_path.is_file():
            data = YAMLLoader.load_from_path(str(config_path))
        else:
            secret_data = self.credential_manager.secret_manager.get(
                f"{self.settings.SERVICE_KEY}-runtime-configurations-{self.settings.ENVIRONMENT}"
            )
            data = YAMLLoader.load_from_string(secret_data)
        
        return RuntimeConfigurations.model_validate(data)
    
    def _load_cache_configurations(self) -> CacheConfigurations:
        namespaces = RedisCacheNamespaces(base=self.settings.SERVICE_KEY)
        host = self.credential_manager.secret_manager.get(
            f"maleo-redis-host-{self.settings.ENVIRONMENT}"
        )
        password = self.credential_manager.secret_manager.get(
            f"maleo-redis-password-{self.settings.ENVIRONMENT}"
        )
        redis = RedisCacheConfigurations(
            namespaces=namespaces, 
            host=host, 
            password=password
        )
        return CacheConfigurations(redis=redis)

    def _load_configurations(self) -> None:
        static_configurations = self._load_static_configurations()
        runtime_configurations = self._load_runtime_configurations()
        cache_configurations = self._load_cache_configurations()

        merged_configurations = deep_merge(
            static_configurations.model_dump(),
            runtime_configurations.model_dump(),
            {"cache": cache_configurations.model_dump()}
        )
        
        self._configurations = Configurations.model_validate(merged_configurations)

    @property
    def configurations(self) -> Configurations:
        return self._configurations