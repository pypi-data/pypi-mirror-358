import os

def get_env_config():
    return {}

def create_client_from_env():
    from .client import AgentMeterClient
    return AgentMeterClient()