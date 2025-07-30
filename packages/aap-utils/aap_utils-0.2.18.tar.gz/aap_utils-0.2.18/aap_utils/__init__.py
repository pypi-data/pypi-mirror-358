from .register import register_demo, get_config, get_mlflow_url

# CLI should not interfere with normal imports
__all__ = ["register_demo", "get_config", "get_mlflow_url"]
