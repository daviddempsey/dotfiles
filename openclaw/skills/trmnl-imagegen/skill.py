#!/usr/bin/env python3
"""
TRMNL Image Generator - OpenClaw Skill
Generates AI images optimized for TRMNL e-ink displays
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import requests

# Configuration
OUTPUT_DIR = Path("/home/ubuntu/trmnl-images")
HISTORY_FILE = OUTPUT_DIR / "image_history.json"
WEBHOOK_URL = os.getenv("TRMNL_WEBHOOK", "")
IMAGE_HOST = os.getenv("TRMNL_IMAGE_HOST", "https://openclaw.daviddempsey.dev/trmnl-images")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class TRMNLImageGenerator:
    """Generates and manages images for TRMNL devices"""

    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.history_file = HISTORY_FILE
        self.webhook_url = WEBHOOK_URL
        self.image_host = IMAGE_HOST
        self.api_key = OPENAI_API_KEY
        self.history = self._load_history()

    def _load_history(self) -> Dict[str, Any]:
        """Load image generation history"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {"generations": [], "latest": None}

    def _save_history(self):
        """Save image generation history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def _generate_filename(self, prompt: str) -> str:
        """Generate a unique filename based on prompt and timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:6]
        return f"t_{timestamp}_{prompt_hash}.png"

    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt for e-ink optimization"""
        style_modifiers = {
            "minimalist": "minimalist design, clean lines, simple shapes, high contrast black and white",
            "abstract": "abstract art, bold shapes, stark contrast, monochrome",
            "nature": "nature scene, high contrast, silhouette style, black and white",
            "geometric": "geometric patterns, clean lines, mathematical beauty, monochrome",
            "vintage": "vintage newspaper style, halftone, high contrast, black ink on white"
        }

        modifier = style_modifiers.get(style, style_modifiers["vintage"])
        return f"{prompt}. {modifier}. Optimized for 1-bit black and white e-ink display, pure black and pure white only."

    def generate_image(self, prompt: str, style: str = "vintage") -> Optional[Path]:
        """Generate an image and return the file path"""
        enhanced_prompt = self._enhance_prompt(prompt, style)
        filename = self._generate_filename(prompt)
        output_path = self.output_dir / filename

        # Try OpenAI DALL-E
        if self.api_key:
            try:
                response = requests.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": enhanced_prompt,
                        "size": "1792x1024",
                        "quality": "standard",
                        "n": 1
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    image_url = data["data"][0]["url"]
                    img_response = requests.get(image_url, timeout=30)

                    # Save raw image
                    raw_path = output_path.with_suffix('.raw.png')
                    with open(raw_path, 'wb') as f:
                        f.write(img_response.content)

                    # Optimize for e-ink
                    self._optimize_for_eink(raw_path, output_path)

                    # Clean up raw file
                    raw_path.unlink(missing_ok=True)

                    # Update history
                    self._add_to_history(filename, prompt, style)

                    return output_path

            except Exception as e:
                print(f"Error generating image: {e}")

        # Fallback: create placeholder
        return self._create_placeholder(prompt, output_path)

    def _optimize_for_eink(self, input_path: Path, output_path: Path):
        """Optimize image for e-ink display"""
        try:
            from PIL import Image, ImageEnhance

            # Open image
            img = Image.open(input_path)
            img = img.convert('RGB')

            # TRMNL aspect ratio: 800x480 = 1.67:1 (landscape)
            # Crop to this aspect ratio instead of stretching
            target_ratio = 800 / 480  # 1.67
            current_ratio = img.width / img.height

            if current_ratio > target_ratio:
                # Image is too wide, crop width
                new_width = int(img.height * target_ratio)
                left = (img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img.height))
            else:
                # Image is too tall, crop height
                new_height = int(img.width / target_ratio)
                top = (img.height - new_height) // 2
                img = img.crop((0, top, img.width, top + new_height))

            # Now resize to exact TRMNL dimensions
            img = img.resize((800, 480), Image.Resampling.LANCZOS)

            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)

            # Convert to grayscale and dither
            img = img.convert('L')
            img = img.convert('1', dither=Image.FLOYDSTEINBERG)

            # Save
            img.save(output_path, 'PNG')

        except ImportError:
            # If PIL not available, just copy
            from shutil import copy
            copy(input_path, output_path)
        except Exception as e:
            print(f"Error optimizing: {e}")
            from shutil import copy
            copy(input_path, output_path)

    def _create_placeholder(self, prompt: str, output_path: Path) -> Path:
        """Create a placeholder image"""
        try:
            from PIL import Image, ImageDraw, ImageFont

            # Create white image
            img = Image.new('1', (800, 480), color=1)  # 1 = white in 1-bit
            draw = ImageDraw.Draw(img)

            # Add text
            draw.text((400, 200), "TRMNL Image", fill=0, anchor='mm')  # 0 = black
            draw.text((400, 240), prompt[:40] + "...", fill=0, anchor='mm')
            draw.text((400, 280), datetime.now().strftime("%Y-%m-%d %H:%M"), fill=0, anchor='mm')

            img.save(output_path, 'PNG')

        except ImportError:
            # Create minimal valid PNG
            with open(output_path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n')  # Minimal PNG header

        self._add_to_history(output_path.name, prompt, "placeholder")
        return output_path

    def _add_to_history(self, filename: str, prompt: str, style: str):
        """Add generation to history"""
        record = {
            "filename": filename,
            "prompt": prompt,
            "style": style,
            "timestamp": datetime.now().isoformat(),
            "url": f"{self.image_host}/{filename}"
        }

        self.history["generations"].append(record)
        self.history["generations"] = self.history["generations"][-10:]
        self.history["latest"] = record
        self._save_history()

    def generate_html(self, image_filename: str, caption: str) -> str:
        """Generate HTML for TRMNL display"""
        date_str = datetime.now().strftime("%b %d, %Y")
        image_url = f"{self.image_host}/{image_filename}"
        display_caption = (caption[:35] + "...") if len(caption) > 35 else caption

        html = (
            '<div class="layout layout--col gap--space-between">'
            f'<img src="{image_url}" style="width:100%;height:auto;image-rendering:pixelated;" alt="{display_caption}">'
            '</div>'
            '<div class="title_bar">'
            '<img class="image" src="https://usetrmnl.com/assets/plugins/icons/image.svg">'
            f'<span class="title">{display_caption}</span>'
            f'<span class="instance">{date_str}</span>'
            '</div>'
        )
        return html


    def send_to_trmnl(self, html: str) -> bool:
        """Send HTML to TRMNL via webhook"""
        if not self.webhook_url:
            print("Error: TRMNL_WEBHOOK not set")
            return False

        payload = {
            "merge_variables": {
                "content": html
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )

            if response.status_code in [200, 201, 204]:
                return True
            else:
                print(f"Webhook error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error sending to TRMNL: {e}")
            return False

    def process_request(self, prompt: str, style: str = "vintage", caption: str = "") -> str:
        """Main entry point: generate image and send to TRMNL

        Args:
            prompt: Full prompt for image generation (including style)
            style: Image style
            caption: Short caption for display (if empty, extracted from prompt)
        """
        # Generate image
        image_path = self.generate_image(prompt, style)

        if not image_path:
            return "Error: Failed to generate image"

        # Use provided caption or extract from prompt
        display_caption = caption if caption else prompt

        # Generate HTML
        html = self.generate_html(image_path.name, display_caption)

        # Send to TRMNL
        if self.send_to_trmnl(html):
            return "Image sent to TRMNL"
        else:
            return f"Image generated but failed to send to TRMNL. Hosted at: {self.image_host}/{image_path.name}"


# OpenClaw integration
skill = TRMNLImageGenerator()

def generate_trmnl_image(prompt: str, style: str = "vintage") -> str:
    """Generate and send an image to TRMNL - callable by OpenClaw"""
    return skill.process_request(prompt, style)

# For testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        print(f"Generating: {prompt}")
        result = skill.process_request(prompt)
        print(result)
    else:
        print("Usage: python skill.py <prompt>")
        print("Example: python skill.py 'A peaceful mountain landscape'")
