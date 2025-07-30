# pyw-config ⚙️
[![PyPI](https://img.shields.io/pypi/v/pyw-config.svg)](https://pypi.org/project/pyw-config/)
[![CI](https://github.com/pythonWoods/pyw-config/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-config/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Configuration management utilities for the **pythonWoods** ecosystem.

## Overview

**pyw-config** fornisce un sistema di gestione configurazioni type-safe e flessibile, con supporto per multipli backend (file, environment variables, remote sources) e validazione automatica tramite Pydantic.

## Philosophy

* **Type-safe configs** – Pydantic models per zero errori di configurazione
* **Multiple sources** – YAML, JSON, TOML, .env, environment variables
* **Hierarchical merging** – override intelligente di configurazioni
* **Environment-aware** – profili per dev/staging/prod
* **Validation-first** – errori chiari e actionable per configurazioni invalide

## Installation

```bash
pip install pyw-config
```

Per backend aggiuntivi:

```bash
pip install pyw-config[yaml]      # + PyYAML per file YAML
pip install pyw-config[toml]      # + tomli/tomllib per TOML
pip install pyw-config[vault]     # + hvac per HashiCorp Vault
pip install pyw-config[remote]    # + requests per config remote
pip install pyw-config[full]      # tutti i backend
```

## Quick Start

### Basic Configuration

```python
from pyw.config import BaseConfig, Field
from pyw.config.sources import from_file, from_env

class DatabaseConfig(BaseConfig):
    host: str = Field(default="localhost")
    port: int = Field(default=5432, ge=1, le=65535)
    username: str
    password: str = Field(..., min_length=8)
    database: str
    ssl_enabled: bool = Field(default=True)

class AppConfig(BaseConfig):
    debug: bool = Field(default=False)
    secret_key: str = Field(..., min_length=32)
    db: DatabaseConfig
    api_timeout: float = Field(default=30.0, gt=0)

# Carica da file + environment
config = AppConfig.from_sources(
    from_file("config.yaml"),
    from_env(prefix="MYAPP_")
)

print(f"Connecting to {config.db.host}:{config.db.port}")
```

### Configuration Files

**config.yaml:**
```yaml
debug: false
secret_key: "your-super-secret-key-here-min-32-chars"
db:
  host: "prod-db.example.com"
  username: "myapp"
  database: "production"
  ssl_enabled: true
api_timeout: 60.0
```

**Environment Variables:**
```bash
export MYAPP_DEBUG=true
export MYAPP_DB_PASSWORD=secure_password_123
export MYAPP_DB_PORT=5433
```

## Features

### 🔄 Multiple Configuration Sources

```python
from pyw.config.sources import (
    from_file, from_env, from_dict, 
    from_vault, from_url
)

config = AppConfig.from_sources(
    # 1. File di base
    from_file("config.yaml"),
    
    # 2. Override per environment
    from_file(f"config.{env}.yaml", optional=True),
    
    # 3. Secrets da Vault
    from_vault("secret/myapp", optional=True),
    
    # 4. Environment variables (priorità massima)
    from_env(prefix="MYAPP_"),
    
    # 5. Config remota
    from_url("https://config.myapp.com/api/config", optional=True)
)
```

### 🌍 Environment Profiles

```python
from pyw.config import ConfigProfile

class AppConfig(BaseConfig):
    class Meta:
        profiles = {
            "development": {
                "debug": True,
                "db.host": "localhost",
                "api_timeout": 5.0
            },
            "production": {
                "debug": False,
                "db.ssl_enabled": True,
                "api_timeout": 30.0
            }
        }

# Carica profilo automaticamente da ENV
config = AppConfig.load_profile()  # Legge ENVIRONMENT=production

# Oppure esplicitamente
config = AppConfig.load_profile("development")
```

### 🔒 Secrets Management

```python
from pyw.config import SecretStr, SecretBytes
from pyw.config.secrets import from_keyring, from_1password

class Config(BaseConfig):
    # Secrets non loggati/serializzati
    api_key: SecretStr
    private_key: SecretBytes
    
    # Caricamento da secret manager
    class Meta:
        secret_sources = [
            from_keyring("myapp"),
            from_1password("myapp-vault")
        ]

# I secrets sono automaticamente mascherati
print(config.api_key)  # → SecretStr('**********')
print(config.api_key.get_secret_value())  # → valore reale
```

### 🔄 Dynamic Configuration

```python
from pyw.config import WatchableConfig
import asyncio

class AppConfig(WatchableConfig):
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    rate_limit: int = 100

# Reload automatico su cambio file
config = AppConfig.from_file("config.yaml", watch=True)

@config.on_change
async def config_changed(old_config, new_config):
    if old_config.rate_limit != new_config.rate_limit:
        await update_rate_limiter(new_config.rate_limit)

# Avvia watching
await config.start_watching()
```

### 📊 Configuration Validation

```python
from pyw.config import validator, root_validator
from typing import Optional

class DatabaseConfig(BaseConfig):
    host: str
    port: int = Field(ge=1, le=65535)
    replica_hosts: Optional[list[str]] = None
    
    @validator('host')
    def validate_host(cls, v):
        if not v or v == 'localhost':
            return v
        # Valida formato hostname/IP
        import socket
        try:
            socket.gethostbyname(v)
            return v
        except socket.gaierror:
            raise ValueError(f"Invalid hostname: {v}")
    
    @root_validator
    def validate_replicas(cls, values):
        if values.get('replica_hosts'):
            main_host = values.get('host')
            if main_host in values['replica_hosts']:
                raise ValueError("Main host cannot be in replica list")
        return values
```

### 🧪 Testing Support

```python
from pyw.config.testing import temporary_config, mock_env

class TestApp:
    def test_with_temp_config(self):
        with temporary_config(AppConfig, {"debug": True}):
            config = AppConfig.load()
            assert config.debug is True
    
    def test_with_mock_env(self):
        with mock_env(MYAPP_DEBUG="false"):
            config = AppConfig.from_env(prefix="MYAPP_")
            assert config.debug is False
```

## Advanced Usage

### Custom Configuration Sources

```python
from pyw.config.sources import ConfigSource
import redis

class RedisConfigSource(ConfigSource):
    def __init__(self, redis_client, key_prefix="config:"):
        self.redis = redis_client
        self.prefix = key_prefix
    
    def load(self) -> dict:
        keys = self.redis.keys(f"{self.prefix}*")
        config = {}
        for key in keys:
            config_key = key.decode().replace(self.prefix, "")
            config[config_key] = self.redis.get(key).decode()
        return config

# Utilizzo
redis_client = redis.Redis()
config = AppConfig.from_sources(
    RedisConfigSource(redis_client),
    from_env(prefix="MYAPP_")
)
```

### Configuration Schemas

```python
from pyw.config import ConfigSchema, generate_schema

# Genera JSON Schema
schema = generate_schema(AppConfig)
print(schema)

# Genera esempio di configurazione
example = AppConfig.generate_example()
with open("config.example.yaml", "w") as f:
    yaml.dump(example, f)

# Validazione esterna
from pyw.config.validation import validate_file

errors = validate_file("config.yaml", AppConfig)
if errors:
    for error in errors:
        print(f"❌ {error.location}: {error.message}")
```

### Configuration Migrations

```python
from pyw.config.migrations import ConfigMigration

class Migration001(ConfigMigration):
    """Rename db_host to database.host"""
    version = "0.0.1"
    
    def migrate(self, config: dict) -> dict:
        if "db_host" in config:
            config.setdefault("database", {})
            config["database"]["host"] = config.pop("db_host")
        return config

# Auto-apply migrations
config = AppConfig.from_file("old-config.yaml", 
                           migrations=[Migration001()])
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from pyw.config import inject_config

app = FastAPI()

@app.get("/status")
def get_status(config: AppConfig = Depends(inject_config(AppConfig))):
    return {
        "debug": config.debug,
        "database_host": config.db.host
    }
```

### Django Integration

```python
# settings.py
from pyw.config import django_settings

class DjangoConfig(BaseConfig):
    SECRET_KEY: str
    DEBUG: bool = False
    DATABASES: dict
    ALLOWED_HOSTS: list[str] = Field(default_factory=list)

# Auto-populate Django settings
config = DjangoConfig.from_sources(
    from_file("django.yaml"),
    from_env(prefix="DJANGO_")
)

globals().update(django_settings(config))
```

## CLI Integration

```bash
# Valida configurazione
pyw-config validate config.yaml --schema=myapp.config:AppConfig

# Genera esempio
pyw-config generate-example myapp.config:AppConfig > config.example.yaml

# Merge configurazioni
pyw-config merge base.yaml override.yaml > final.yaml

# Mostra configurazione risolta (con secrets mascherati)
pyw-config show --env=production
```

## Roadmap

- 🔐 **Enhanced secrets**: Integrazione con AWS Secrets Manager, Azure Key Vault
- 🌐 **Remote configs**: Etcd, Consul, Kubernetes ConfigMaps
- 📝 **Configuration UI**: Web interface per editing configurazioni
- 🔄 **Hot reload**: Reload automatico in runtime senza restart
- 📊 **Config analytics**: Metriche di utilizzo e drift detection
- 🧩 **Plugin system**: Custom validators e sources

## Contributing

1. Fork il repo: `git clone https://github.com/pythonWoods/pyw-config.git`
2. Crea virtual-env: `poetry install && poetry shell`  
3. Lancia tests: `pytest`
4. Lancia linter: `ruff check . && mypy`
5. Apri la PR: CI esegue tutti i check

Felice configurazione nella foresta di **pythonWoods**! 🌲⚙️

## Links utili

Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-config/latest/

Issue tracker → https://github.com/pythonWoods/pyw-config/issues

Changelog → https://github.com/pythonWoods/pyw-config/releases

© pythonWoods — MIT License