from pathlib import Path
import tomli

class Config:
    data:dict

    def __init__(self, path:str) -> None:
        p = Path(path)

        with open(p, "rb") as f:
            self.data = tomli.load(f)

    @property
    def guest_name(self) -> str:
        return self.summary["guest_name"]

    @property
    def guest_firstname(self) -> str:
        return self.guest_name.split(" ")[0]

    @property
    def language(self) -> str:
        return self.summary["language"]

    @property
    def llm(self) -> dict:
        return self.data["llm"]

    @property
    def summary(self) -> dict:
        return self.data["summary"]

    @property
    def tts(self) -> dict:
        return self.data["tts"]