# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2024-12-19

### 🔧 Format Support Improvements

This release focuses on fixing audio format handling and improving format delivery optimization.

### ✨ Added

- **Smart Header Selection**: Intelligent HTTP header selection to optimize format delivery from openai.fm service
- **Format Mapping Functions**: Helper functions for better format handling and optimization
- **Enhanced Web Interface**: Improved format selection with detailed descriptions for each format
- **Comprehensive Format Documentation**: Updated README and documentation with complete format information

### 🔄 Changed

- **File Naming Logic**: Files are now saved with extensions based on the actual returned format, not the requested format
- **Enhanced Logging**: Added format-specific log messages for better debugging
- **Web API Enhancement**: `/api/formats` endpoint now provides detailed information about all supported formats
- **Documentation Updates**: README and package documentation now include comprehensive format guides

### 🐛 Fixed

- **MAJOR FIX**: Resolved file naming issue where files were saved with incorrect double extensions (e.g., `test.wav.mp3`, `test.opus.wav`)
- **Correct File Extensions**: Files now save with proper single extensions based on actual audio format (e.g., `test.mp3`, `test.wav`)
- **Format Optimization**: Improved format delivery through smart request optimization
- **Format Handling**: Better handling of all supported audio formats

### 📝 Technical Details

- **Format Optimization**: Smart request optimization to deliver the best quality for each format
- **Backward Compatibility**: Existing code continues to work unchanged
- **Enhanced Format Support**: Improved support for all 6 audio formats (MP3, WAV, OPUS, AAC, FLAC, PCM)

## [3.0.0] - 2025-06-06

### 🎉 First Python Package Release

This is the first release of TTSFM as an installable Python package. Previous versions (v1.x and v2.x) were service-only releases that provided the API server but not a pip-installable package.

### ✨ Added

- **Complete Package Restructure**: Modern Python package structure with proper typing
- **Async Support**: Full asynchronous client implementation with `asyncio`
- **OpenAI API Compatibility**: Drop-in replacement for OpenAI TTS API
- **Type Hints**: Complete type annotation support throughout the codebase
- **CLI Interface**: Command-line tool for easy TTS generation
- **Web Application**: Optional Flask-based web interface
- **Docker Support**: Multi-architecture Docker images (linux/amd64, linux/arm64)
- **Comprehensive Error Handling**: Detailed exception hierarchy
- **Multiple Audio Formats**: Support for MP3, WAV, FLAC, and more
- **Voice Options**: Multiple voice models (alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer)
- **Text Processing**: Automatic text length validation and splitting
- **Rate Limiting**: Built-in rate limiting and retry mechanisms
- **Configuration**: Environment variable and configuration file support

### 🔧 Technical Improvements

- **Modern Build System**: Using `pyproject.toml` with setuptools
- **GitHub Actions**: Automated Docker builds and PyPI publishing
- **Development Tools**: Pre-commit hooks, linting, testing setup
- **Documentation**: Comprehensive README and inline documentation
- **Package Management**: Proper dependency management with optional extras

### 🌐 API Changes

- **Breaking**: Complete API redesign for better usability
- **OpenAI Compatible**: `/v1/audio/speech` endpoint compatibility
- **RESTful Design**: Clean REST API design
- **Health Checks**: Built-in health check endpoints
- **CORS Support**: Cross-origin resource sharing enabled

### 📦 Installation Options

```bash
# Basic installation
pip install ttsfm

# With web application support
pip install ttsfm[web]

# With development tools
pip install ttsfm[dev]

# Docker
docker run -p 8000:8000 ghcr.io/dbccccccc/ttsfm:latest
```

### 🚀 Quick Start

```python
from ttsfm import TTSClient, Voice

client = TTSClient()
response = client.generate_speech(
    text="Hello! This is TTSFM v3.0.0",
    voice=Voice.CORAL
)

with open("speech.mp3", "wb") as f:
    f.write(response.audio_data)
```

### 📦 Package vs Service History

**Important Note**: This v3.0.0 is the first release of TTSFM as a Python package available on PyPI. Previous versions (v1.x and v2.x) were service/API server releases only and were not available as installable packages.

- **v1.x - v2.x**: Service releases (API server only, not pip-installable)
- **v3.0.0+**: Full Python package releases (pip-installable with service capabilities)

### 🐛 Bug Fixes

- Fixed Docker build issues with dependency resolution
- Improved error handling and user feedback
- Better handling of long text inputs
- Enhanced stability and performance

### 📚 Documentation

- Complete API documentation
- Usage examples and tutorials
- Docker deployment guide
- Development setup instructions

---

## Previous Service Releases (Not Available as Python Packages)

The following versions were service/API server releases only and were not available as pip-installable packages:

### [2.0.0-alpha9] - 2025-04-09
- Service improvements (alpha release)

### [2.0.0-alpha8] - 2025-04-09
- Service improvements (alpha release)

### [2.0.0-alpha7] - 2025-04-07
- Service improvements (alpha release)

### [2.0.0-alpha6] - 2025-04-07
- Service improvements (alpha release)

### [2.0.0-alpha5] - 2025-04-07
- Service improvements (alpha release)

### [2.0.0-alpha4] - 2025-04-07
- Service improvements (alpha release)

### [2.0.0-alpha3] - 2025-04-07
- Service improvements (alpha release)

### [2.0.0-alpha2] - 2025-04-07
- Service improvements (alpha release)

### [2.0.0-alpha1] - 2025-04-07
- Alpha release (DO NOT USE)

### [1.3.0] - 2025-03-28
- Support for additional audio file formats in the API
- Alignment with formats supported by the official API

### [1.2.2] - 2025-03-28
- Fixed Docker support

### [1.2.1] - 2025-03-28
- Color change for indicator for status
- Voice preview on webpage for each voice

### [1.2.0] - 2025-03-26
- Enhanced stability and availability by implementing advanced request handling mechanisms
- Removed the proxy pool

### [1.1.2] - 2025-03-26
- Version display on webpage
- Last version of 1.1.x

### [1.1.1] - 2025-03-26
- Build fixes

### [1.1.0] - 2025-03-26
- Project restructuring for better future development experiences
- Added .env settings

### [1.0.0] - 2025-03-26
- First service release
