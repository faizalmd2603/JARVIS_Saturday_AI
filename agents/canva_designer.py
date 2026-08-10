import os
import sys
import json
import logging
import urllib.parse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

OUTPUT_DIR = os.path.join("ui", "generated_designs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class CanvaDesignerAgent:
    """
    Mentro Canva / Figma Design Studio Sub-Agent:
    Generates SVG visual vector graphics, layered design manifests, AI background artwork URLs,
    editable typography elements, and 1-click PNG/SVG export.
    """
    def __init__(self):
        self.name = "CANVA_DESIGNER"
        self.role = "Visual Canva & Figma Graphic Design Studio"

    def execute(self, prompt: str, model: str = "gemini-3.5-flash-lite") -> dict:
        logging.info(f"[CanvaDesigner] Generating visual graphic design for: '{prompt}'")
        
        encoded_bg = urllib.parse.quote(f"Corporate MNC visual poster design: {prompt}, 8k resolution, modern minimalist design")
        bg_url = f"https://image.pollinations.ai/prompt/{encoded_bg}?width=1080&height=1080&nologo=true"

        system_instruction = """You are Mentro Canva/Figma Visual Studio AI.
Generate a structured JSON canvas layout with SVG shapes and editable layers.
Schema:
{
  "title": "Corporate Design Title",
  "width": 1080,
  "height": 1080,
  "background": {
    "color": "#0f172a",
    "gradient": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
    "image_prompt": "Minimalist corporate graphic"
  },
  "layers": [
    {
      "id": "header_1",
      "type": "text",
      "text": "HEADER TITLE",
      "x": 540,
      "y": 180,
      "fontSize": 56,
      "color": "#ffffff",
      "fontWeight": "800",
      "align": "center"
    },
    {
      "id": "sub_1",
      "type": "text",
      "text": "Subheading or tagline phrase",
      "x": 540,
      "y": 280,
      "fontSize": 28,
      "color": "#38bdf8",
      "fontWeight": "500",
      "align": "center"
    },
    {
      "id": "shape_1",
      "type": "shape",
      "shapeType": "rectangle",
      "x": 140,
      "y": 380,
      "width": 800,
      "height": 450,
      "color": "rgba(30, 41, 59, 0.7)",
      "borderColor": "#38bdf8"
    }
  ]
}
"""
        res = router.generate_completion(prompt, system_instruction=system_instruction, json_mode=True, preferred_model=model)
        try:
            design_json = json.loads(res)
            design_json["background"]["image_url"] = bg_url
            
            # Generate standalone SVG graphic markup for direct browser export
            svg_markup = self.build_svg_graphic(design_json, bg_url)

            return {
                "status": "success",
                "agent": self.name,
                "action": "generate_layered_design",
                "design": design_json,
                "svg_graphic": svg_markup,
                "message": f"Generated Canva graphic '{design_json.get('title', 'Design')}' with {len(design_json.get('layers', []))} editable layers."
            }
        except Exception as e:
            logging.error(f"[CanvaDesigner] Error generating design JSON: {e}")
            fallback_design = {
                "title": prompt[:30].title(),
                "width": 1080,
                "height": 1080,
                "background": {
                    "color": "#0f172a",
                    "gradient": "linear-gradient(135deg, #0f172a, #1e293b)",
                    "image_url": bg_url
                },
                "layers": [
                    {"id": "l1", "type": "text", "text": prompt.upper(), "x": 540, "y": 400, "fontSize": 48, "color": "#38bdf8", "align": "center"}
                ]
            }
            return {
                "status": "success",
                "agent": self.name,
                "action": "generate_layered_design",
                "design": fallback_design,
                "svg_graphic": self.build_svg_graphic(fallback_design, bg_url),
                "message": "Generated fallback Canva visual design."
            }

    def build_svg_graphic(self, design: dict, bg_url: str) -> str:
        """Constructs standalone SVG vector graphic for 1-click PNG/SVG download"""
        w = design.get("width", 1080)
        h = design.get("height", 1080)
        title = design.get("title", "Graphic Design")
        bg_color = design.get("background", {}).get("color", "#0f172a")

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">',
            f'<rect width="{w}" height="{h}" fill="{bg_color}"/>',
            f'<image href="{bg_url}" width="{w}" height="{h}" opacity="0.35" preserveAspectRatio="xMidYMid slice"/>'
        ]

        for layer in design.get("layers", []):
            ltype = layer.get("type")
            if ltype == "shape":
                sx = layer.get("x", 100)
                sy = layer.get("y", 100)
                sw = layer.get("width", 400)
                sh = layer.get("height", 200)
                fill = layer.get("color", "rgba(255,255,255,0.1)")
                stroke = layer.get("borderColor", "#38bdf8")
                svg_parts.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')
            elif ltype == "text":
                tx = layer.get("x", w / 2)
                ty = layer.get("y", h / 2)
                size = layer.get("fontSize", 40)
                color = layer.get("color", "#ffffff")
                weight = layer.get("fontWeight", "bold")
                text = layer.get("text", "")
                svg_parts.append(f'<text x="{tx}" y="{ty}" font-family="Inter, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="middle" dominant-baseline="middle">{text}</text>')

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)
