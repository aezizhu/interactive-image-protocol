#!/usr/bin/env python3
"""
AIIP Creator - Creates Annotated Interactive Image Protocol files

.aiip files are PNG images with all annotations rendered visually.
Open them with ANY image viewer to see the full content.

Usage:
    python create-aiip.py

Output:
    sample.aiip - A PNG file with all annotations visible
"""

from PIL import Image, ImageDraw, ImageFont
import json
import zlib
import struct
import os

# Image dimensions
WIDTH = 800
HEIGHT = 600

# Colors
BG_COLOR = '#1a3a5c'
LAND_COLOR = '#2d5a3d'
REGION_COLORS = {
    'low': '#2ecc71',
    'medium': '#f1c40f',
    'high': '#e74c3c'
}

# Data to embed
DATA = {
    "title": "US Trade Tariffs 2025",
    "regions": [
        {
            "name": "North America",
            "tariff": "25%",
            "level": "medium",
            "countries": [
                {"name": "Canada", "rate": "25%"},
                {"name": "Mexico", "rate": "25%"}
            ],
            "bounds": (50, 100, 250, 250)
        },
        {
            "name": "South America",
            "tariff": "35%",
            "level": "high",
            "countries": [
                {"name": "Brazil", "rate": "50%"},
                {"name": "Argentina", "rate": "15%"}
            ],
            "bounds": (150, 280, 300, 450)
        },
        {
            "name": "Europe",
            "tariff": "15%",
            "level": "low",
            "countries": [
                {"name": "UK", "rate": "10%"},
                {"name": "EU", "rate": "20%"},
                {"name": "Switzerland", "rate": "39%"}
            ],
            "bounds": (350, 80, 500, 220)
        },
        {
            "name": "Asia",
            "tariff": "30%",
            "level": "high",
            "countries": [
                {"name": "China", "rate": "30%"},
                {"name": "Japan", "rate": "15%"},
                {"name": "India", "rate": "50%"}
            ],
            "bounds": (520, 100, 750, 280)
        }
    ]
}


def create_aiip_image():
    """Create the annotated image with all content visible"""

    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to load a nice font, fall back to default
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large

    # Draw title
    title = DATA["title"]
    draw.text((WIDTH // 2, 30), title, fill='white', font=font_large, anchor='mm')

    # Draw subtitle
    draw.text((WIDTH // 2, 55), "Hover regions for details (in AIIP viewer)",
              fill='#888888', font=font_small, anchor='mm')

    # Draw each region with its info box
    for region in DATA["regions"]:
        x1, y1, x2, y2 = region["bounds"]
        color = REGION_COLORS[region["level"]]

        # Draw region outline
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

        # Fill with semi-transparent color (simulate with lighter shade)
        fill_color = tuple(int(c * 0.3 + int(BG_COLOR[1:3], 16) * 0.7)
                          for c in [int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)])
        draw.rectangle([x1+2, y1+2, x2-2, y2-2], fill=fill_color)

        # Region name at top of box
        draw.text(((x1 + x2) // 2, y1 + 15), region["name"],
                  fill='white', font=font_medium, anchor='mm')

        # Tariff rate
        draw.text(((x1 + x2) // 2, y1 + 35), f"Avg: {region['tariff']}",
                  fill=color, font=font_medium, anchor='mm')

        # Country details
        y_offset = y1 + 60
        for country in region["countries"]:
            text = f"{country['name']}: {country['rate']}"
            draw.text(((x1 + x2) // 2, y_offset), text,
                      fill='#cccccc', font=font_small, anchor='mm')
            y_offset += 18

    # Draw legend at bottom
    legend_y = HEIGHT - 50
    legend_items = [
        ("Low (10-15%)", REGION_COLORS['low']),
        ("Medium (20-25%)", REGION_COLORS['medium']),
        ("High (30-50%)", REGION_COLORS['high'])
    ]

    legend_x = 100
    for label, color in legend_items:
        draw.rectangle([legend_x, legend_y, legend_x + 15, legend_y + 15], fill=color)
        draw.text((legend_x + 22, legend_y + 7), label, fill='white', font=font_small, anchor='lm')
        legend_x += 150

    # Footer
    draw.text((WIDTH // 2, HEIGHT - 15),
              "AIIP v3.0 - Annotated Interactive Image Protocol | github.com/aezizhu",
              fill='#666666', font=font_small, anchor='mm')

    return img


def embed_aiip_chunk(img, data):
    """Embed AIIP data as a custom PNG chunk"""

    # Save image to bytes
    import io
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    png_bytes = buffer.getvalue()

    # Create AIIP chunk
    json_str = json.dumps(data)
    compressed = zlib.compress(json_str.encode('utf-8'))

    # Chunk format: [compression_method(1 byte)][compressed_data]
    chunk_data = bytes([0x01]) + compressed  # 0x01 = DEFLATE
    chunk_type = b'aiip'

    # Calculate CRC
    crc = zlib.crc32(chunk_type + chunk_data) & 0xffffffff

    # Build chunk: [length(4)][type(4)][data(n)][crc(4)]
    chunk = struct.pack('>I', len(chunk_data)) + chunk_type + chunk_data + struct.pack('>I', crc)

    # Insert after IHDR (first chunk after 8-byte signature)
    # Find end of IHDR
    ihdr_length = struct.unpack('>I', png_bytes[8:12])[0]
    insert_pos = 8 + 4 + 4 + ihdr_length + 4  # sig + length + type + data + crc

    # Build new PNG
    new_png = png_bytes[:insert_pos] + chunk + png_bytes[insert_pos:]

    return new_png


def main():
    print("Creating AIIP image...")

    # Create the image with visible annotations
    img = create_aiip_image()

    # Embed the structured data
    aiip_data = {
        "version": "3.0",
        "canvas": {"width": WIDTH, "height": HEIGHT},
        "meta": {
            "title": DATA["title"],
            "author": "aezi zhu",
            "created": "2025-01-01"
        },
        "data": DATA
    }

    png_bytes = embed_aiip_chunk(img, aiip_data)

    # Save as .aiip
    output_path = "sample.aiip"
    with open(output_path, 'wb') as f:
        f.write(png_bytes)

    print(f"Created: {output_path}")
    print(f"Size: {len(png_bytes):,} bytes")
    print()
    print("This file can be opened with ANY image viewer.")
    print("Rename to .png if needed: mv sample.aiip sample.png")
    print()
    print("All content is visible directly in the image!")


if __name__ == '__main__':
    main()
