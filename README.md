# AIIP - Annotated Interactive Image Protocol

**Version 3.0**

A universal image format where all content is visible directly in the image.

## Overview

AIIP files (`.aiip`) are PNG images with **all annotations rendered directly into the pixels**. They can be:

- **Opened with ANY image viewer** - Preview, Photos, GIMP, Photoshop, browsers, etc.
- **Renamed to `.png`** if your OS doesn't recognize `.aiip` extension
- **Shared anywhere** - Email, chat, websites - just like any image file

### Key Principle

**No special viewer needed.** Open the file, see everything.

The structured data is also embedded as a custom PNG chunk for programmatic access.

## Quick Start

```bash
# Install Pillow
pip install Pillow

# Create a sample AIIP file
python create-aiip.py

# Open it (rename to .png if needed on your system)
open sample.aiip    # macOS - may need: open sample.png
```

## Usage

### Creating an AIIP Image

Edit `create-aiip.py` to customize:

```python
# Your data
DATA = {
    "title": "Your Title",
    "regions": [
        {
            "name": "Region 1",
            "info": "Details here",
            "bounds": (x1, y1, x2, y2)
        }
    ]
}
```

Run the script:

```bash
python create-aiip.py
```

Output: `sample.aiip` - a PNG file with all content visible.

### Programmatic Access

The structured data is embedded in the PNG as a custom `aiip` chunk:

```python
import zlib
import json

def read_aiip_data(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    # Skip PNG signature (8 bytes)
    pos = 8

    while pos < len(data):
        length = int.from_bytes(data[pos:pos+4], 'big')
        chunk_type = data[pos+4:pos+8].decode('ascii')

        if chunk_type == 'aiip':
            chunk_data = data[pos+8:pos+8+length]
            # Skip compression byte, decompress rest
            json_str = zlib.decompress(chunk_data[1:]).decode('utf-8')
            return json.loads(json_str)

        pos += 12 + length  # length(4) + type(4) + data + crc(4)

    return None

# Usage
data = read_aiip_data('sample.aiip')
print(data['meta']['title'])
```

## File Format

AIIP files are standard PNG files with:

1. **Visual content** - All annotations rendered into pixels
2. **Embedded data** - Structured JSON in custom `aiip` chunk

```
[PNG Signature]
[IHDR chunk]
[aiip chunk]    <- Custom chunk with compressed JSON
[IDAT chunks]   <- Image pixels with visible annotations
[IEND chunk]
```

### Compression

- Byte 0: `0x01` (DEFLATE compression)
- Bytes 1-N: Compressed JSON data

## Example Output

The generated `sample.aiip` displays:

- Title at top
- Color-coded regions with borders
- Labels and data inside each region
- Legend at bottom
- Footer with protocol info

All visible when opened with any image viewer.

## Author

**aezi zhu** - [github.com/aezizhu](https://github.com/aezizhu)

## License

MIT License - See [LICENSE](LICENSE) file.
