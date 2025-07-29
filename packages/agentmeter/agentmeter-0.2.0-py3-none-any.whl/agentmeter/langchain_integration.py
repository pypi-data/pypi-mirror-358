try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    BaseCallbackHandler = object

class LangChainAgentMeterCallback(BaseCallbackHandler):
    def __init__(self, client, project_id, agent_id, **kwargs):
        super().__init__()
        self.client = client