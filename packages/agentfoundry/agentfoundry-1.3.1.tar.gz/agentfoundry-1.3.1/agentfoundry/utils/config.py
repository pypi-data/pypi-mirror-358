"""Singleton configuration loader for AgentFoundry."""

from __future__ import annotations

import os
import logging
from importlib import resources
from pathlib import Path
import tomllib
from typing import Optional
from jinja2 import Template

logger = logging.getLogger(__name__)


class Config:
    """Singleton config manager."""

    _instance: Optional[Config] = None

    def __new__(cls, config_path: Optional[str] = None):
        if cls._instance is None:
            logger.info(f"Creating Config singleton with config_path: {config_path}")
            cls._instance = super().__new__(cls)
            cls._instance._initialize(config_path)
        return cls._instance

    def _initialize(self, config_path: Optional[str]):
        logger.debug("Initializing Config (config_path=%r)", config_path)
        xdg_config_home = Path(os.getenv(
            "XDG_CONFIG_HOME", str(Path.home() / ".config")
        ))
        logger.debug("Using XDG_CONFIG_HOME=%s", xdg_config_home)
        if config_path:
            cfg_file = Path(config_path)
            cfg_dir = cfg_file.parent
            logger.debug("Using provided config file: %s", cfg_file)
        else:
            cfg_dir = xdg_config_home / "agentfoundry"
            cfg_dir.mkdir(parents=True, exist_ok=True)
            cfg_file = cfg_dir / "agentfoundry.toml"
            logger.debug("Default config file path: %s", cfg_file)

        if not cfg_file.exists():
            default_toml = resources.files("agentfoundry.resources").joinpath("default_agentfoundry.toml")
            logger.info("Config file %s not found; copying default from %s", cfg_file, default_toml)
            cfg_dir.mkdir(parents=True, exist_ok=True)
            with default_toml.open("rb") as src, cfg_file.open("wb") as dst:
                dst.write(src.read())
            logger.debug("Created config file: %s", cfg_file)

        logger.info("Loading configuration from %s", cfg_file)
        with cfg_file.open("rb") as f:
            self._config = tomllib.load(f)
        logger.debug("Configuration loaded, keys: %s", list(self._config.keys()))

    def get(self, key: str, default=None):
        """Get a configuration value by key, checking env var override."""
        env_key = key.upper().replace(".", "_")
        logger.debug("Retrieving key %r (env override=%r)", key, env_key)
        val = os.getenv(env_key)
        if val is not None:
            logger.debug("Found environment override: %s=%s", env_key, val)
            return val

        # Traverse nested keys in TOML
        parts = key.split(".")
        cfg = self._config
        for part in parts:
            if not isinstance(cfg, dict) or part not in cfg:
                logger.debug("Key %r not found in config; checking fallback for default", key)
                # fallback defaults for well-known paths
                # use top-level DATA_DIR (flattened PATHS section)
                data_dir = self.get("DATA_DIR")
                if key == "AUTH_CACHE_FILE":
                    return os.path.expanduser(self._render(f"{data_dir}/auth_tokens.json"))
                if key == "MEMORY_CACHE_FILE":
                    return os.path.expanduser(self._render(f"{data_dir}/memory_cache.db"))
                if key == "registry_db_path":
                    # support top-level or legacy [PATHS] section
                    reg = self.get("REGISTRY_DB") or self.get("PATHS.REGISTRY_DB")
                    return os.path.expanduser(reg)
                if key == "TOOLS_DIR":
                    return os.path.expanduser(self.get("TOOLS_DIR"))
                val = self._render(default)
                if default is not None:
                    logger.debug("Key %r not found; returning default value: %r", key, default)
                return os.path.expanduser(val) if isinstance(val, str) else val
            cfg = cfg[part]
        logger.debug("Found config[%r] = %r", key, cfg)
        val = self._render(cfg)
        return os.path.expanduser(val) if isinstance(val, str) else val

    def _render(self, val):
        """Render any {{ VAR }} placeholders using the current config context."""
        if isinstance(val, str) and "{{" in val and "}}" in val:
            return Template(val).render(**self._config)
        return val


def load_config(config_path: Optional[str] = None) -> Config:
    """Return the singleton Config instance."""
    logger.debug("load_config called with config_path=%r", config_path)
    return Config(config_path)


if __name__ == "__main__":
    # Example usage
    config = load_config()
    print(f"CONFIG_DIR: {config.get('CONFIG_DIR', 'NONE')}")
    print(f"DATA_DIR: {config.get('DATA_DIR', 'NONE')}")
    print(f"TOOLS_DIR: {config.get('TOOLS_DIR', 'NONE')}")
    print(f"REGISTRY_DB: {config.get('REGISTRY_DB', 'NONE')}")
    print(f"CHROMA.PERSIST_DIR: {config.get('CHROMA.PERSIST_DIR', 'NONE')}")
    print(f"CODING_MODEL: {config.get('CODING_MODEL', 'NONE')}")
    print(f"OPENAI_MODEL: {config.get('OPENAI_MODEL', 'NONE')}")
    print(f"OPENAI_API_KEY: {config.get('OPENAI_API_KEY', 'NONE')}")
    print(f"CHROMA.COLLECTION_NAME: {config.get('CHROMA.COLLECTION_NAME', 'NONE')}")
    print(f"MS.CLIENT_ID: {config.get('MS.CLIENT_ID', 'NONE')}")
    print(f"MS.TENANT_ID: {config.get('MS.TENANT_ID', 'NONE')}")
    print(f"MS.CLIENT_SECRET: {config.get('MS.CLIENT_SECRET', 'NONE')}")
    print(f"FAISS.INDEX_PATH: {config.get('FAISS.INDEX_PATH', 'NONE')}")
    print(f"OLLAMA.HOST: {config.get('OLLAMA.HOST', 'NONE')}")
    print(f"OLLAMA.MODEL: {config.get('OLLAMA.MODEL', 'NONE')}")
    print(config.get("EMBEDDING.MODEL_NAME", "default_value"))
