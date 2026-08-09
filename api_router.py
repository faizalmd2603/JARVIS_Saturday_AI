import os
import sys
import json
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

AVAILABLE_MODELS = [
    {"id": "gemini-3.5-flash-lite", "name": "Gemini 3.5 Flash-Lite (Fast)", "provider": "Gemini"},
    {"id": "gemini-3.1-pro", "name": "Gemini 3.1 Pro (Reasoning)", "provider": "Gemini"},
    {"id": "gemini-3.1-flash", "name": "Gemini 3.1 Flash (Ultra Fast)", "provider": "Gemini"},
    {"id": "gemini-3.6-flash", "name": "Gemini 3.6 Flash (Latest)", "provider": "Gemini"},
    {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "provider": "Gemini"},
    {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "provider": "Gemini"},
    {"id": "llama-3.3-70b-versatile", "name": "Groq Llama 3.3 70B", "provider": "Groq"},
    {"id": "llama-3.1-8b-instant", "name": "Groq Llama 3.1 8B", "provider": "Groq"},
    {"id": "mixtral-8x7b-32768", "name": "Groq Mixtral 8x7B", "provider": "Groq"},
    {"id": "gemma2-9b-it", "name": "Groq Gemma2 9B", "provider": "Groq"},
    {"id": "pollinations-free", "name": "Pollinations AI (Keyless Free Engine)", "provider": "Pollinations"}
]

class MentroAPIRouter:
    def __init__(self):
        self.gemini_client = None
        self.groq_client = None
        self._init_clients()

    def _init_clients(self):
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                logging.info("[MentroRouter] Gemini Client initialized successfully.")
            except Exception as e:
                logging.warning(f"[MentroRouter] Could not init Gemini Client: {e}")

        if GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=GROQ_API_KEY)
                logging.info("[MentroRouter] Groq Client initialized successfully.")
            except Exception as e:
                logging.warning(f"[MentroRouter] Could not init Groq Client: {e}")

    def generate_completion(self, prompt: str, system_instruction: str = None, json_mode: bool = False, preferred_model: str = "gemini-3.5-flash-lite") -> str:
        """
        Executes completion with user selected model, automatically falling back across providers.
        """
        logging.info(f"[MentroRouter] Requesting model: {preferred_model}")

        # If user explicitly requested a Groq model
        if preferred_model.startswith("llama") or preferred_model.startswith("mixtral") or preferred_model.startswith("gemma"):
            res = self._try_groq(preferred_model, prompt, system_instruction, json_mode)
            if res: return res

        # If user requested Pollinations
        if preferred_model == "pollinations-free":
            res = self._try_pollinations(prompt, system_instruction, json_mode)
            if res: return res

        # Primary Attempt: Gemini with requested or fallback model list
        if self.gemini_client:
            models_to_try = [preferred_model] + [
                "gemini-3.5-flash-lite",
                "gemini-3.1-flash",
                "gemini-3.6-flash",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash"
            ]
            for m in models_to_try:
                if not m.startswith("gemini"): continue
                try:
                    config = {}
                    if system_instruction:
                        config["system_instruction"] = system_instruction
                    if json_mode:
                        config["response_mime_type"] = "application/json"

                    response = self.gemini_client.models.generate_content(
                        model=m,
                        contents=prompt,
                        config=config if config else None
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    logging.warning(f"[MentroRouter] Gemini model '{m}' failed: {e}. Trying fallback...")

        # Secondary Attempt: Groq
        groq_res = self._try_groq("llama-3.3-70b-versatile", prompt, system_instruction, json_mode)
        if groq_res: return groq_res

        # Tertiary Attempt: Pollinations AI Free REST API
        poll_res = self._try_pollinations(prompt, system_instruction, json_mode)
        if poll_res: return poll_res

        logging.warning("[MentroRouter] All online LLM APIs failed. Returning local fallback response.")
        if json_mode:
            return json.dumps({"action": "offline_fallback", "message": "All LLM APIs unavailable", "result": prompt})
        return f"[OFFLINE MODE] Mentro AI Processed: {prompt}"

    def _try_groq(self, model: str, prompt: str, system_instruction: str, json_mode: bool) -> str:
        if not self.groq_client: return None
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            kwargs = {"model": model, "messages": messages}
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            completion = self.groq_client.chat.completions.create(**kwargs)
            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content
        except Exception as e:
            logging.warning(f"[MentroRouter] Groq model '{model}' error: {e}")
        return None

    def _try_pollinations(self, prompt: str, system_instruction: str, json_mode: bool) -> str:
        try:
            payload = {
                "messages": [
                    {"role": "system", "content": system_instruction or "You are Mentro AI Superagent."},
                    {"role": "user", "content": prompt}
                ]
            }
            if json_mode:
                payload["jsonMode"] = True
            res = requests.post("https://text.pollinations.ai/", json=payload, timeout=12)
            if res.status_code == 200 and res.text:
                return res.text
        except Exception as e:
            logging.error(f"[MentroRouter] Pollinations REST error: {e}")
        return None

    def transcribe_audio(self, audio_filepath: str) -> str:
        if not self.groq_client:
            return "[Error: Groq API key required for Whisper STT]"
        try:
            with open(audio_filepath, "rb") as file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(audio_filepath, file.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
            return str(transcription).strip()
        except Exception as e:
            return f"[Transcription Error: {e}]"

router = MentroAPIRouter()
