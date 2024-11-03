from loguru import logger
from pathlib import Path
from pydub import AudioSegment
from random import randint
from wikiaudify.chatgpt import OpenAINode, OpenAILocalNode
from wikiaudify.config import Config
from wikiaudify.const import (
    GENERIC_SYSTEM_PROMPT,
    GUEST_SYSTEM,
    GUEST_QUESTION,
    HOST_QUESTION,
    HOST_SYSTEM,
    HOST_INTRODUCTION,
    HOST_USER_QUESTION,
    HOST_OUTRO
)
from wikiaudify.elevenlabs import ElevenLabs
from wikiaudify.wikipedia import Wikipedia

class Generator:
    audio:AudioSegment
    config:Config
    llm:OpenAINode
    transcript:list = []
    tts_host:ElevenLabs
    tts_guest:ElevenLabs
    wikipedia:Wikipedia

    def __init__(self, config:Config):
        self.conf = config
        llm_type = self.conf.llm["llm_type"]
        logger.debug(f"Using llm_type: {llm_type}")

        if llm_type == "external":
            model = self.conf.llm["chatgpt_model"]
            api_key = self.conf.llm["openai_api_key"]
            self.llm_host = OpenAINode(model, api_key)
            self.llm_guest = OpenAINode(model, api_key)
        elif llm_type == "local":
            base_url = self.config.llm["base_url"]
            self.llm_host = OpenAILocalNode(
                base_url = base_url,
                model = "model",
                api_key = "lm-studio"
            )
            self.llm_guest = OpenAILocalNode(
                base_url = base_url,
                model = "model",
                api_key = "lm-studio"
            )

        self.tts_host = ElevenLabs(
            default_language = self.conf.language,
            default_voice_id = self.conf.tts["host_voice_id"],
            api_key = self.conf.tts["elevenlabs_api_key"]
        )

        self.tts_guest = ElevenLabs(
            default_language = self.conf.language,
            default_voice_id = self.conf.tts["guest_voice_id"],
            api_key = self.conf.tts["elevenlabs_api_key"]
        )

        self.wikipedia = Wikipedia(self.conf.language)

    def add_transcript(self, actor:str, text:str):
        self.transcript.append({
            "actor" : actor,
            "text" : text
        })

    def create_conversation(self, subject:str, user_question:str | None = None):
        logger.debug(f"Trying to make a conversation about: {subject}")
        subject_without_underscores = subject.replace("_", " ")
        article = self.wikipedia.get_article(subject)

        self.llm_host.set_system_prompt(HOST_SYSTEM.format(
            generic = GENERIC_SYSTEM_PROMPT,
            subject = subject_without_underscores,
            guest_name = self.conf.guest_name
        ))

        self.llm_guest.set_system_prompt(GUEST_SYSTEM.format(
            generic = GENERIC_SYSTEM_PROMPT,
            guest_name = self.conf.guest_name,
            subject = subject_without_underscores,
            wikipedia_text = article
        ))

        intro_prompt = HOST_INTRODUCTION.format(
            guest_name = self.conf.guest_name,
            subject = subject_without_underscores,
            guest_firstname = self.conf.guest_firstname
        )

        intro_text = self.llm_host.create_single(
            prompt = intro_prompt,
            max_tokens = 50
        )

        self.add_transcript("host", intro_text)
        logger.debug(f"Intro text: {intro_text}")

        answer_prompt = GUEST_QUESTION.format(
            question = intro_text
        )

        answer = self.llm_guest.create_single(
            answer_prompt,
            max_tokens = 100
        )

        self.add_transcript("guest", answer)
        logger.debug(f"Answer to first question: {answer}")

        # Okay, now a bit of back and forth
        question_count = self.conf.summary["question_count"]
        for tries in range(question_count):
            # Do the user question as the last question
            if user_question and (tries == question_count - 1):
                logger.debug(f"user questio: {user_question}")
                question_prompt = HOST_USER_QUESTION.format(
                    answer = user_question
                )
            else:
                question_prompt = HOST_QUESTION.format(
                    answer = answer
            )

            question = self.llm_host.create_single(
                prompt = question_prompt,
                max_tokens = 50
            )

            self.add_transcript("host", question)
            logger.debug(f"Question: {question}")

            answer_prompt = GUEST_QUESTION.format(
                question = question
            )

            answer = self.llm_guest.create_single(
                prompt = answer_prompt,
                max_tokens = 75
            )

            self.add_transcript("guest", answer)
            logger.debug(f"Answer: {answer}")

        # Wrap it up
        outro_prompt = HOST_OUTRO.format()
        outro = self.llm_host.create_single(
            prompt = outro_prompt,
            max_tokens = 50
        )
        self.add_transcript("host", outro)
        logger.debug(f"Outro: {outro}")

    def render_audio(self) -> AudioSegment:
        logger.debug("Rendering audio")
        start_speech = 6000
        audio = AudioSegment.from_mp3(self.conf.summary["background_music_path"])
        audio = audio.fade(to_gain = -15, start = 3000, end = start_speech)
        speech = AudioSegment.silent()

        for line in self.transcript:
            text = line["text"]
            actor = line["actor"]
            logger.debug(f"Rendering '{text}' from {actor}")

            if actor == "host":
                segment = self.tts_host.render(text)
            elif actor == "guest":
                segment = self.tts_guest.render(text)

            speech = speech.append(segment)

            # Add a bit of silence
            speech = speech.append(AudioSegment.silent(duration = randint(200, 600)))

        # Overlay over the audio and fade out
        audio = audio.overlay(speech, position = start_speech)
        end_speech = len(speech) + start_speech

        # And fade out
        end_audio = end_speech + 3000
        audio = audio.fade(to_gain = -120, start = end_speech, end = end_audio)
        logger.debug(f"Audio ending at {end_audio}")

        # Cut to the fade
        audio = audio[0:end_audio]

        logger.debug("Podcast ready!")

        self.audio = audio

    def export_audio(self, path:str):
        self.audio.export(path)
        logger.debug(f"Exported audio to {path}")

    def export_transcript(self, path:str):
        with open(Path(path), "w") as f:
            for line in self.transcript:
                text = line["text"]
                actor = line["actor"]
                f.write(f"{actor.upper()}: {text}\n\n")

        logger.debug(f"Exported transcript to {path}")