# Language Font Map

A Python package that provides mappings between language codes and their recommended Google Fonts. This package helps applications handle multilingual text by suggesting appropriate fonts for different languages and scripts.

## Features

- No need to download or install fonts
- Works with Google Fonts API
- Supports 200+ languages
- Automatic font loading
- Cross-platform compatibility

## Installation

```bash
pip install lang-font-map
```

## Usage

### Basic Usage
```python
from lang.fonts import get_font_family, get_google_fonts_url

# Get font family name for a language
font_family = get_font_family('hin_Deva')  # Returns "Noto Sans Devanagari" for Hindi
print(f"Font family for Hindi: {font_family}")

# Get Google Fonts URL for a language
font_url = get_google_fonts_url('tam_Taml')  # Returns URL for Tamil font
print(f"Google Fonts URL for Tamil: {font_url}")
```

### Using in Web Applications
```html
<!-- In your HTML file -->
<head>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil&display=swap" rel="stylesheet">
    <style>
        .tamil-text {
            font-family: 'Noto Sans Tamil', sans-serif;
        }
    </style>
</head>
```

### Using in Desktop Applications
```python
# Example with tkinter
import tkinter as tk
from lang.fonts import get_font_family

root = tk.Tk()
label = tk.Label(
    root,
    text="வணக்கம்",  # Tamil text
    font=(get_font_family('tam_Taml'), 12)
)
label.pack()
```

## Language Codes

The package uses language codes in the format `language_Script`, where:
- `language` is the ISO 639-3 language code
- `Script` is the ISO 15924 script code

Examples:
- `eng_Latn`: English (Latin script)
- `hin_Deva`: Hindi (Devanagari script)
- `zho_Hans`: Chinese (Simplified Han script)

## Supported Languages

The package supports 200+ languages including:
- Indian Languages (Hindi, Tamil, Bengali, etc.)
- East Asian Languages (Chinese, Japanese, Korean, etc.)
- Middle Eastern Languages (Arabic, Persian, Urdu, etc.)
- European Languages (English, French, German, etc.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Font mappings are based on Google's Noto Sans font family
- Special thanks to Google Fonts for providing high-quality fonts for all languages 