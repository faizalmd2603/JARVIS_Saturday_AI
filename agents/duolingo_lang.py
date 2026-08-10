import os
import sys
import json
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

SUPPORTED_LANGUAGES = {
    "tamil": {"name": "Tamil (தமிழ்)", "flag": "🇮🇳", "sample": "வணக்கம் (Vanakkam)"},
    "english": {"name": "English", "flag": "🇬🇧", "sample": "Hello! Welcome to Mentro AI."},
    "hindi": {"name": "Hindi (हिंदी)", "flag": "🇮🇳", "sample": "नमस्ते (Namaste)"},
    "urdu": {"name": "Urdu (اردو)", "flag": "🇵🇰", "sample": "سلام (Salam)"},
    "french": {"name": "French (Français)", "flag": "🇫🇷", "sample": "Bonjour! Comment allez-vous?"}
}

class DuolingoAgent:
    """
    Mentro Duolingo Language Learning Sub-Agent (LINGUA_DUO):
    Supports Tamil, English, Hindi, Urdu, and French.
    Generates gamified interactive lessons, vocabulary quizzes, pronunciation guides,
    and conversational translations with XP and streak rewards.
    """
    def __init__(self):
        self.name = "LINGUA_DUO"
        self.role = "Duolingo Interactive Multilingual Learning Coach"

    def execute(self, payload: dict, action: str = "lesson", model: str = "gemini-3.5-flash-lite") -> dict:
        target_lang = payload.get("language", "tamil").lower()
        if target_lang not in SUPPORTED_LANGUAGES:
            target_lang = "tamil"

        lang_info = SUPPORTED_LANGUAGES[target_lang]
        logging.info(f"[LINGUA_DUO] Processing '{action}' for language: {lang_info['name']}")

        if action == "quiz":
            topic = payload.get("topic", "Common Greetings & Daily Expressions")
            system_instruction = f"""You are Duolingo AI Language Tutor for {lang_info['name']}.
Generate an interactive 3-question vocabulary quiz in JSON:
{{
  "language": "{lang_info['name']}",
  "flag": "{lang_info['flag']}",
  "topic": "{topic}",
  "xp_reward": 15,
  "questions": [
    {{
      "id": 1,
      "question": "How do you say 'Hello' in {lang_info['name']}?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "pronunciation_guide": "Pronunciation phonetic",
      "english_translation": "Hello"
    }},
    {{
      "id": 2,
      "question": "What is the meaning of phrase X?",
      "options": ["Opt A", "Opt B", "Opt C", "Opt D"],
      "correct_answer": "Opt B",
      "pronunciation_guide": "Phonetic guide",
      "english_translation": "Thank you"
    }},
    {{
      "id": 3,
      "question": "Translate: 'Good morning' to {lang_info['name']}",
      "options": ["Opt A", "Opt B", "Opt C", "Opt D"],
      "correct_answer": "Opt C",
      "pronunciation_guide": "Phonetic guide",
      "english_translation": "Good morning"
    }}
  ]
}}
"""
            res = router.generate_completion(f"Generate quiz for topic: {topic}", system_instruction=system_instruction, json_mode=True, preferred_model=model)
            try:
                parsed = json.loads(res)
                return {"status": "success", "agent": self.name, "quiz": parsed, "message": f"Generated Duolingo {lang_info['name']} quiz."}
            except Exception:
                pass

        # Action: Interactive Lesson
        topic = payload.get("topic", "Basics & Travel Essentials")
        prompt = f"Target Language: {lang_info['name']}. Topic: {topic}."
        system_instruction = f"""You are Duolingo AI Language Coach for {lang_info['name']}.
Provide a rich, beautifully formatted Markdown lesson including:
1. 🌟 **{lang_info['flag']} Lesson Title & Overview**
2. 🗣️ **Key Vocabulary Table** (Original Script | Phonetic Pronunciation | English Meaning)
3. 💬 **Example Dialogues** with line-by-line translation
4. 💡 **Grammar & Cultural Tip**
5. 🎯 **Quick Practice Challenge**
"""
        lesson_md = router.generate_completion(prompt, system_instruction=system_instruction, preferred_model=model)
        return {
            "status": "success",
            "agent": self.name,
            "language": lang_info["name"],
            "flag": lang_info["flag"],
            "lesson_markdown": lesson_md,
            "message": f"Generated Duolingo {lang_info['name']} lesson."
        }
