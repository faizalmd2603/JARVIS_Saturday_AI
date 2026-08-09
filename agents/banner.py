import os
import sys
import requests
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api_router import router

OUTPUT_DIR = os.path.join("ui", "generated_designs")

class BannerAgent:
    """
    BANNER / Design Agent: Takes design concepts, calls Pollinations AI for base imagery,
    and uses Python Pillow (PIL) for auto-layout, overlay gradients, and typography.
    """
    def __init__(self):
        self.name = "BANNER"
        self.role = "Creative Design & Graphic Generation Specialist"
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def execute(self, command: str) -> dict:
        prompt = f"""You are BANNER, the creative design agent for JARVIS.
Analyze the user design prompt: "{command}".
Extract a creative image prompt and overlay title text.
Return JSON:
{{
  "image_prompt": "creative concept description for AI image generation",
  "title_text": "Main Overlay Title"
}}
"""
        res = router.generate_completion(prompt, json_mode=True)
        try:
            import json
            parsed = json.loads(res)
            img_prompt = parsed.get("image_prompt", command)
            title_text = parsed.get("title_text", "JARVIS DESIGN PROTOCOL")
            return self.generate_design(img_prompt, title_text)
        except Exception:
            return self.generate_design(command, "JARVIS CREATIVE SUITE")

    def generate_design(self, prompt: str, title_text: str = "AVENGERS PROTOCOL") -> dict:
        try:
            filename = f"design_{abs(hash(prompt + title_text)) % 1000000}.png"
            output_path = os.path.join(OUTPUT_DIR, filename)

            # Step 1: Pollinations AI Image Generation
            encoded_prompt = requests.utils.quote(prompt)
            pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

            logging.info(f"[BANNER] Fetching base image from Pollinations AI: {pollinations_url}")
            resp = requests.get(pollinations_url, timeout=20)
            
            if resp.status_code == 200:
                base_img = Image.open(BytesIO(resp.content)).convert("RGBA")
            else:
                logging.warning(f"[BANNER] Pollinations request returned {resp.status_code}. Generating fallback canvas.")
                base_img = self._create_gradient_canvas(1024, 1024)

            # Step 2: Pillow Layout, Gradient Overlay & Typography
            final_img = self._apply_hud_typography(base_img, title_text, prompt)
            final_img.save(output_path, "PNG")

            return {
                "status": "success",
                "agent": self.name,
                "action": "generate_design",
                "filename": filename,
                "filepath": output_path,
                "web_url": f"/generated_designs/{filename}",
                "prompt": prompt,
                "title": title_text,
                "message": f"Design graphic generated successfully: {filename}"
            }
        except Exception as e:
            # Local PIL Fallback
            return self._create_local_canvas_fallback(prompt, title_text)

    def _apply_hud_typography(self, base_img: Image.Image, title_text: str, subtitle: str) -> Image.Image:
        W, H = base_img.size
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Semi-transparent dark banner at bottom
        draw.rectangle([0, H - 240, W, H], fill=(10, 15, 25, 200))
        # Cyan Sci-Fi Accent Line
        draw.line([0, H - 240, W, H - 240], fill=(0, 229, 255, 255), width=4)

        # Typography
        try:
            font_title = ImageFont.truetype("arial.ttf", 48)
            font_sub = ImageFont.truetype("arial.ttf", 24)
        except Exception:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()

        draw.text((40, H - 200), title_text.upper(), font=font_title, fill=(255, 255, 255, 255))
        draw.text((40, H - 130), f"PROMPT: {subtitle[:60]}...", font=font_sub, fill=(0, 229, 255, 255))
        draw.text((40, H - 80), "AVENGERS HUD | BANNER CREATIVE ENGINE", font=font_sub, fill=(255, 215, 0, 255))

        return Image.alpha_composite(base_img, overlay)

    def _create_gradient_canvas(self, W: int, H: int) -> Image.Image:
        img = Image.new("RGBA", (W, H), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)
        for i in range(H):
            r = int(15 + (i / H) * 20)
            g = int(23 + (i / H) * 80)
            b = int(42 + (i / H) * 120)
            draw.line([(0, i), (W, i)], fill=(r, g, b, 255))
        return img

    def _create_local_canvas_fallback(self, prompt: str, title_text: str) -> dict:
        filename = f"fallback_{abs(hash(prompt)) % 10000}.png"
        output_path = os.path.join(OUTPUT_DIR, filename)
        img = self._create_gradient_canvas(1024, 768)
        img = self._apply_hud_typography(img, title_text, prompt)
        img.save(output_path, "PNG")
        return {
            "status": "success",
            "agent": self.name,
            "filename": filename,
            "filepath": output_path,
            "web_url": f"/generated_designs/{filename}",
            "message": "Local PIL layout fallback generated."
        }
