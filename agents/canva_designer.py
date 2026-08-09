import os
import sys
import json
import logging
import urllib.parse
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

OUTPUT_DIR = os.path.join("ui", "generated_designs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class CanvaDesignerAgent:
    """
    Mentro Canva Design Studio Agent:
    Generates structured, layered Canva-style design manifests with editable text layers,
    shape layers, typography parameters, background colors, and AI imagery background URLs.
    """
    def __init__(self):
        self.name = "CANVA_DESIGNER"
        self.role = "Layered Graphic Design Studio Agent"

    def execute(self, prompt: str, model: str = "gemini-3.5-flash-lite") -> dict:
        logging.info(f"[CanvaDesigner] Generating layered design manifest for: '{prompt}'")
        
        system_instruction = """You are Mentro Canva Design Studio AI.
Generate a structured JSON canvas layout with editable layers.
Schema:
{
  "title": "Design Title",
  "width": 1080,
  "height": 1080,
  "background": {
    "color": "#0a0f1d",
    "image_prompt": "Futuristic tech background with glowing blue neon circuits"
  },
  "layers": [
    {
      "id": "layer_1",
      "type": "text",
      "text": "HEADER TITLE",
      "x": 540,
      "y": 200,
      "fontSize": 54,
      "color": "#ffffff",
      "fontWeight": "bold",
      "align": "center"
    },
    {
      "id": "layer_2",
      "type": "text",
      "text": "Subheading or tag line description text",
      "x": 540,
      "y": 320,
      "fontSize": 26,
      "color": "#00e5ff",
      "fontWeight": "normal",
      "align": "center"
    },
    {
      "id": "layer_3",
      "type": "shape",
      "shapeType": "rectangle",
      "x": 200,
      "y": 500,
      "width": 680,
      "height": 300,
      "color": "rgba(0, 229, 255, 0.1)",
      "borderColor": "#00e5ff"
    }
  ]
}
"""
        res = router.generate_completion(prompt, system_instruction=system_instruction, json_mode=True, preferred_model=model)
        try:
            design_json = json.loads(res)
            
            # Generate AI Background Image URL via Pollinations
            bg_prompt = design_json.get("background", {}).get("image_prompt", prompt)
            encoded_bg = urllib.parse.quote(bg_prompt)
            bg_url = f"https://image.pollinations.ai/prompt/{encoded_bg}?width=1080&height=1080&nologo=true"
            
            design_json["background"]["image_url"] = bg_url
            
            return {
                "status": "success",
                "agent": self.name,
                "action": "generate_layered_design",
                "design": design_json,
                "message": f"Generated Canva-style layered design '{design_json.get('title', 'Design')}' with {len(design_json.get('layers', []))} editable layers."
            }
        except Exception as e:
            logging.error(f"[CanvaDesigner] Error generating JSON manifest: {e}")
            return {
                "status": "success",
                "agent": self.name,
                "action": "generate_layered_design",
                "design": {
                    "title": prompt[:30],
                    "width": 1080,
                    "height": 1080,
                    "background": {
                        "color": "#0d1117",
                        "image_url": f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1080&height=1080&nologo=true"
                    },
                    "layers": [
                        {"id": "l1", "type": "text", "text": prompt.upper(), "x": 540, "y": 400, "fontSize": 48, "color": "#00e5ff", "align": "center"}
                    ]
                },
                "message": "Generated fallback layered design."
            }
