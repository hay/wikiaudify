class LLMNode:
    def __init__(self):
        self.system_prompt = "You are a helpful agent"

    def create(self, prompt:str) -> list:
        raise NotImplementedError()

    def create_single(self, prompt:str) -> str:
        raise NotImplementedError()

    def set_system_prompt(self, prompt:str):
        self.system_prompt = prompt