from loguru import logger
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import requests

class ElevenLabs:
    NAME = "elevenlabs"

    def __init__(self, api_key, default_language, default_voice_id):
        self.language = default_language
        self.voice_id = default_voice_id
        self.api_key = api_key
        self.api_endpoint = "https://api.elevenlabs.io/v1"

    def _call(self, method, json = None, stream = False):
        url = f"{self.api_endpoint}/{method}"
        logger.debug(f"Getting {url}")

        req = requests.post(url,
            headers = {
                "Accept": "application/json",
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            },
            stream = stream,
            json = json
        )

        return req

    def render(self, text, voice_id:str | None = None, language = None) -> AudioSegment:
        language = language or self.language
        voice_id = voice_id or self.voice_id

        logger.debug(f"Rendering ElevenLabs TTS: {language} / {voice_id} / {text}")

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1"
        }

        req = self._call(
            method = f"text-to-speech/{voice_id}/stream",
            json = data,
            stream = True
        )

        if not req.ok:
            raise Exception(f"Could not get Elevenlabs response", req.status_code, req.text)

        outfile = NamedTemporaryFile(suffix = ".mp3")

        with open(outfile.name, 'wb') as f:
            for chunk in req.iter_content(chunk_size = 1024):
                if chunk:
                    f.write(chunk)

        return AudioSegment.from_mp3(outfile.name)

if __name__ == "__main__":
    elabs = ElevenLabs("en", "nienke")
    audio = elabs.render("Hey this is a small test")
    audio.export("test.mp3")