from loguru import logger
from openai import OpenAI
from wikiaudify.llmnode import LLMNode

class BaseOpenAINode(LLMNode):
    def __init__(self):
        self.client = None
        self.model = None
        super().__init__()

    def create(
            self, prompt:str, role:str = "user", temperature:int = 1,
            n:int = 1, max_tokens:int | None = None
        ) -> list:

        if not max_tokens:
            max_tokens = 200

        logger.info(f"🤖 Getting completion for: {prompt}, max_tokens: {max_tokens}")

        args = {
            "model" : self.model,
            "messages" : [
                {
                    "role" : "system",
                    "content" : self.system_prompt
                },
                {
                    "role" : role,
                    "content" : prompt
                }
            ],
            "temperature" : temperature,
            "n" : n # Number of replies
        }

        if max_tokens:
            args["max_tokens"] = max_tokens

        completion = self.client.chat.completions.create(**args)

        return completion.choices

    def create_single(self, *args, **kwargs) -> str:
        kwargs["n"] = 1
        completions = self.create(*args, **kwargs)
        return completions[0].message.content

class OpenAINode(BaseOpenAINode):
    def __init__(self, model:str, api_key:str):
        super().__init__()
        self.model = model
        self.api_key = api_key
        self.client = OpenAI(api_key = self.api_key)

class OpenAILocalNode(BaseOpenAINode):
    def __init__(self, model:str, api_key:str, base_url:str):
        super().__init__()
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(base_url = self.base_url, api_key = self.api_key)

if __name__ == "__main__":
    conf = Config()
    llm = OpenAINode(
        conf.config["openai"]["chatgpt_model"],
        conf.secret["openai_api_key"]
    )
    text = llm.create_single("Tell me a very stupid joke", max_tokens = 100)
    print(text)