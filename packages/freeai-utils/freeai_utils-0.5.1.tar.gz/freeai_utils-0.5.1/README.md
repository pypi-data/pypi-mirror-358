# freeai-utils

A lightweight, pip‑installable Python toolkit that wraps popular AI and utility libraries into classes and functions (no external binaries or convoluted setup scripts required). 

Most selected models fall in the **81–242 million parameter** range, which pioritizes real time responsiveness while still delivering solid accuracy. Instead of writing long pipelines or dealing with low level APIs, you get smart defaults out of the box, with the option to customize behavior at init time if needed. 

The first time you use a feature that needs a model (like Whisper, etc...), it will automatically download the model from Hugging Face. After that, it will work offline using the cached version.

**Note**: This library focuses on being simple to use, even if it means sacrificing accuracy. It's great for beginners or anyone who wants to explore AI features without dealing with complex code. Just call the functions, I'll handle the rest.

## Features

- **Audio**: record WAV/MP3 (fixed, toggle, silence-triggered)
- **Audio-to-Text**: OpenAI Whisper transcription & language detection 
- **Speech-to-Text**: Using Vosk models for real-time transcription from a microphone
- **Web Search**: scrape Google results
- **Image**: caption generation & OCR (EasyOCR)
- **TTS**: text-to-speech via gTTS or pyttsx3
- **PDF-DOCX-Reader**: extract text and images from pdf and docx files
- **Document Filter**: extract and rank relevant content from documents using an extractive QA model
- **Translator**: Provides automatic language detection, translating content into your specified target language. (both online and local)
- **LocalLLM**: Small Qwen model for offline use or as a chatbot without an API key.
- **ImageGenerator**: Easy interaction with SDXL Turbo and SD1.5 models for image generation (for UI and performance, consider using AUTOMATIC1111)
* **Gemini API**: Interact with Google Cloud Gemini models via your API key

  * *Note: This works best with Google accounts that have no billing method added yet (completely free to use with limits).*

## Installation

Before installing `freeai-utils`, you need to install PyTorch manually based on your system and desired configuration (CPU or CUDA).

### 🔧 Prerequisite: Install PyTorch

Visit the official PyTorch installation guide:

👉 [https://pytorch.org/get-started/locally](https://pytorch.org/get-started/locally)

Choose your system (OS, package manager, Python version, CUDA version), and copy the appropriate install command.

### 📦 Install `freeai-utils`
```bash
pip install freeai-utils
```

> No need to install extra executables or clone large repositories — everything works out of the box with `pip`.

---

## 📝Models download 
```bash
freeai-utils setup
```
or
```bash
freeai-utils setup A
```

>This will help downloads default models for most functional classes (excluding image generation).

For 🎨 **image generation** models:
```bash
freeai-utils setup ICF
```

For more detailed control over which models to download:
```bash
freeai-utils help
```
>This will displays a list of setup options for specific model types. You can also trigger downloads programmatically by instantiating the relevant class.

### 🚀 Optional GPU Performance Boost

For GPU users, if you want to take advantage of faster attention using `xformers`, install it separately (remember to choose it base on your system and your cuda version):
https://github.com/facebookresearch/xformers

## 📖 Full API Reference

For a detailed list of all classes and methods, see [API.md](https://github.com/truongbaan/Utility-python-library/blob/main/API.md).

## Acknowledgements & References

See [THIRD_PARTY.md](https://github.com/truongbaan/Utility-python-library/blob/main/THIRD_PARTY.md) for a full list of third-party libraries and their licenses.

## Inspiration

This project was inspired by the GitHub repository:
[awesome-python](https://github.com/vinta/awesome-python)

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/truongbaan/Utility-python-library/blob/main/LICENSE) file for details.

## Test Environment

This library has been tested on laptop with the following specifications:

**CPU**: Intel Core i5-12500H
**GPU**: NVIDIA GeForce RTX 3050 4GB GDDR6
**RAM**: 32GB DDR4
**OS**: Windows 11 Home 64-bit
**CUDA Version**: CUDA 12.6

Performance may vary depending on system specs. The selected models and safetensors were intentionally chosen to remain lightweight. All features, including image generation have been tested to run smoothly on GPUs with just 4GB of VRAM, such as the RTX 3050.