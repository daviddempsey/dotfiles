---
name: trmnl-imagegen
description: Generate AI images for TRMNL e-ink display devices. Creates optimized 800x480 black and white images using AI image generation models, hosts them on the local server, and sends the display HTML to TRMNL via webhook. Supports vintage, minimalist, abstract, nature, and geometric styles optimized for e-ink displays.
---

# TRMNL Image Generator

Generate AI images for TRMNL e-ink display devices.

## Quick Start Workflow

1. Check for `$TRMNL_WEBHOOK` environment variable
2. If missing, prompt user for webhook URL
3. **Ask user to verify TRMNL display markup is set to:** `<div>{{content}}</div>`
4. Confirm image generation parameters (prompt, style)
5. Generate image using AI (OpenAI DALL-E or similar)
6. Optimize image for e-ink (800x480, high contrast, dithered)
7. Save image to web-accessible directory
8. Generate HTML using TRMNL framework referencing hosted image
9. Send via POST to webhook (use temp file method)
10. **Send minimal confirmation only** - Do NOT echo content back to chat

## Setup Requirements

**TRMNL Device:** TRMNL OG (7.5" e-ink, 800x480px, 1-bit black & white)

**Display markup required:**
```html
<div>{{content}}</div>
```

**Environment variables:**
```bash
export TRMNL_WEBHOOK="https://trmnl.com/api/custom_plugins/{uuid}"
export OPENAI_API_KEY="your-openai-key"  # For image generation
export TRMNL_IMAGE_HOST="https://openclaw.daviddempsey.dev/trmnl-images"
```

**Image hosting:** Images are hosted at `$HOME/.openclaw/trmnl-images/` and served via Caddy

## Image Generation

**Supported styles:**
- `vintage` - Newspaper/halftone aesthetic (default)
- `minimalist` - Clean lines, simple shapes
- `abstract` - Bold shapes, artistic
- `nature` - High-contrast landscapes
- `geometric` - Patterns, mathematical

**E-ink optimization:**
- 800x480 resolution
- High contrast (1-bit black & white)
- Floyd-Steinberg dithering
- Vintage aesthetic matches e-ink

## Sending Content

**Generate and send image:**
```bash
# The skill will automatically:
# 1. Generate image using AI
# 2. Optimize for e-ink display
# 3. Save to hosted directory
# 4. Generate HTML with image URL
# 5. POST to TRMNL webhook
```

## Webhook Limits

| Tier | Payload Size | Rate Limit |
|------|--------------|------------|
| Free | **2 KB** (2,048 bytes) | 12 requests/hour |
| TRMNL+ | **5 KB** (5,120 bytes) | 30 requests/hour |

**HTML size kept minimal by:**
- Hosting images externally (not embedding)
- Using TRMNL framework classes
- Minified HTML structure

## Example Usage

**User request:**
> "Show a peaceful mountain landscape on my TRMNL"

**Skill actions:**
1. Generate image with prompt: "Peaceful mountain landscape, vintage newspaper style, halftone, high contrast black and white, 800x480 resolution"
2. Save to: `~/.openclaw/trmnl-images/trmnl_20240204_120000_a1b2c3d4.png`
3. Generate HTML:
```html
<div class="layout layout--col gap--space-between">
  <img src="https://openclaw.daviddempsey.dev/trmnl-images/trmnl_20240204_120000_a1b2c3d4.png"
       style="width:100%;height:auto;" alt="Generated image">
</div>
<div class="title_bar">
  <img class="image" src="https://usetrmnl.com/assets/plugins/icons/image.svg">
  <span class="title">AI Generated</span>
  <span class="instance">Peaceful mountain</span>
</div>
```
4. POST to webhook
5. Confirm: "Image sent to TRMNL"

## HTML Structure

**Standard pattern for image display:**
```html
<div class="layout layout--col gap--space-between">
  <img src="{hosted_image_url}" style="width:100%;height:auto;" alt="Generated image">
</div>
<div class="title_bar">
  <img class="image" src="https://usetrmnl.com/assets/plugins/icons/image.svg">
  <span class="title">AI Generated</span>
  <span class="instance">{shortened_prompt}</span>
</div>
```

## User Experience

**Critical:** Do NOT echo content back to chat. Just confirm "Image sent to TRMNL".

**Example confirmations:**
- "Image sent to TRMNL"
- "Generated and sent vintage-style landscape"
- "Your TRMNL should update shortly"

## Technical Details

**Image optimization pipeline:**
1. Generate via OpenAI DALL-E 3 (or fallback)
2. Resize to 800x480
3. Convert to grayscale
4. Apply contrast enhancement (1.5x)
5. Apply Floyd-Steinberg dithering
6. Save as 1-bit PNG

**File naming:**
`trmnl_YYYYMMDD_HHMMSS_{hash}.png`

**Image retention:**
- Last 10 images kept
- Older images auto-deleted

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Webhook fails | Verify TRMNL_WEBHOOK URL, check rate limits |
| Image not showing | Check image is hosted at correct URL, verify Caddy config |
| Generation fails | Verify OPENAI_API_KEY is set |
| Payload too large | Image URL too long - use shorter filenames |
| Display markup error | Ensure TRMNL plugin uses `<div>{{content}}</div>` |

## Anti-Patterns

1. Embedding base64 images (exceeds payload limit)
2. Not optimizing for e-ink (grayscale instead of 1-bit)
3. Using long image URLs (keep filenames short)
4. Echoing HTML content back to chat
5. Not verifying display markup first

## Best Practices

1. Always verify `<div>{{content}}</div>` display markup
2. Use external image hosting (don't embed)
3. Optimize images for 1-bit e-ink display
4. Keep HTML under 2KB (free) or 5KB (TRMNL+)
5. Send minimal confirmations only
6. Use temp file method for curl
7. Shorten prompt text for instance label
