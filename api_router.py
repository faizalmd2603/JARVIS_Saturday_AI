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

class DualAPIRouter:
    def __init__(self):
        self.gemini_client = None
        self.groq_client = None
        self._init_clients()

    def _init_clients(self):
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                logging.info("[APIRouter] Gemini Client initialized successfully.")
            except Exception as e:
                logging.warning(f"[APIRouter] Could not init Gemini Client: {e}")

        if GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=GROQ_API_KEY)
                logging.info("[APIRouter] Groq Client initialized successfully.")
            except Exception as e:
                logging.warning(f"[APIRouter] Could not init Groq Client: {e}")

    def generate_completion(self, prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
        """
        Multi-tier LLM Execution with Automatic Model Try-Chain:
        Tier 1: Gemini Models (3.1 Pro -> 3.1 Flash -> 3.5 Flash-Lite -> 3.6 Flash -> 2.5 Flash -> 2.0 Flash -> 1.5 Flash)
        Tier 2: Groq Models (Llama 3.3 70B -> Llama 3.1 8B -> Mixtral 8x7B)
        Tier 3: Pollinations AI Free Text REST API (Zero Key Fallback)
        """
        # Tier 1: Gemini Models
        if self.gemini_client:
            gemini_models = [
                "gemini-3.1-pro",
                "gemini-3.1-flash",
                "gemini-3.5-flash-lite",
                "gemini-3.6-flash",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash"
            ]
            for model_name in gemini_models:
                try:
                    logging.info(f"[APIRouter] Dispatching request to Gemini API ({model_name})...")
                    config = {}
                    if system_instruction:
                        config["system_instruction"] = system_instruction
                    if json_mode:
                        config["response_mime_type"] = "application/json"
                    
                    response = self.gemini_client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config if config else None
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    logging.warning(f"[APIRouter] Gemini model '{model_name}' failed: {e}. Trying next model...")

        # Tier 2: Groq Models
        if self.groq_client:
            groq_models = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ]
            for g_model in groq_models:
                try:
                    logging.info(f"[APIRouter] Dispatching request to Groq API ({g_model})...")
                    messages = []
                    if system_instruction:
                        messages.append({"role": "system", "content": system_instruction})
                    messages.append({"role": "user", "content": prompt})

                    kwargs = {
                        "model": g_model,
                        "messages": messages,
                    }
                    if json_mode:
                        kwargs["response_format"] = {"type": "json_object"}

                    completion = self.groq_client.chat.completions.create(**kwargs)
                    if completion.choices and completion.choices[0].message.content:
                        return completion.choices[0].message.content
                except Exception as e:
                    logging.warning(f"[APIRouter] Groq model '{g_model}' failed: {e}. Trying next model...")

        # Tier 3: Zero-Key Pollinations Free Text AI REST Fallback
        try:
            logging.info("[APIRouter] Dispatching request to Pollinations Free Text AI REST API...")
            payload = {
                "messages": [
                    {"role": "system", "content": system_instruction or "You are JARVIS AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            }
            if json_mode:
                payload["jsonMode"] = True

            res = requests.post("https://text.pollinations.ai/", json=payload, timeout=12)
            if res.status_code == 200 and res.text:
                return res.text
        except Exception as e:
            logging.error(f"[APIRouter] Pollinations REST API fallback failed: {e}")

        # Local emergency rule response if all online services fail
        logging.warning("[APIRouter] All online LLM APIs failed. Returning local fallback response.")
        if json_mode:
            return json.dumps({"action": "offline_fallback", "message": "All LLM APIs unavailable", "result": prompt})
        return f"[OFFLINE MODE] Processed locally: {prompt}"

    def transcribe_audio(self, audio_filepath: str) -> str:
        """
        Uses Groq Whisper API for ultra low-latency speech recognition.
        """
        if not self.groq_client:
            return "[Error: Groq API key required for low-latency Whisper STT]"

        try:
            logging.info(f"[APIRouter] Transcribing audio with Groq Whisper: {audio_filepath}")
            with open(audio_filepath, "rb") as file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(audio_filepath, file.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
            return str(transcription).strip()
        except Exception as e:
            logging.error(f"[APIRouter] Groq Whisper transcription error: {e}")
            return f"[Transcription Error: {e}]"

# Singleton instance
router = DualAPIRouter()
