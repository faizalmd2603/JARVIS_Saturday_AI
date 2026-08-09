import os
import sys
import logging
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

def _speak_worker(text: str):
    """Background thread worker for pyttsx3 speech synthesis with Windows COM initialization"""
    try:
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass

        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 185)
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logging.warning(f"[HERALD TTS Background Thread] Speech synthesis note: {e}")

class HeraldAgent:
    """
    HERALD / Voice Agent: Low-latency voice interface using Groq Whisper API for STT and pyttsx3 for TTS.
    """
    def __init__(self):
        self.name = "HERALD"
        self.role = "Voice Command Interface & Speech Synthesis Agent"

    def execute(self, command: str) -> dict:
        """Process voice string input or trigger speech feedback"""
        self.speak(command)
        return {
            "status": "success",
            "agent": self.name,
            "action": "spoken_response",
            "message": f"HERALD vocalized speech output: '{command}'"
        }

    def process_voice_audio(self, audio_filepath: str) -> dict:
        """Transcribe voice audio using Groq Whisper"""
        if not os.path.exists(audio_filepath):
            return {"status": "error", "agent": self.name, "message": f"Audio file not found: {audio_filepath}"}

        transcription = router.transcribe_audio(audio_filepath)
        return {
            "status": "success",
            "agent": self.name,
            "action": "speech_to_text",
            "transcription": transcription,
            "filepath": audio_filepath,
            "message": f"Voice transcription: '{transcription}'"
        }

    def speak(self, text: str) -> bool:
        """Text-to-speech feedback via pyttsx3 in daemon thread"""
        try:
            threading.Thread(target=_speak_worker, args=(text[:150],), daemon=True).start()
            return True
        except Exception as e:
            logging.warning(f"[HERALD TTS Warning] Local speech output unavailable ({e}). Synthesized log: '{text}'")
            return False
