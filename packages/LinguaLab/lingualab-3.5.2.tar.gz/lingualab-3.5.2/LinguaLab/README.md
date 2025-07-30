# LinguaLab

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/lingualab.svg)](https://pypi.org/project/lingualab/)

**LinguaLab** is a specialised Python toolkit designed for multilingual text translation and audio transcription services. Built with robust fallback mechanisms and professional-grade APIs, it provides reliable solutions for language processing tasks including real-time translation, language detection, and speech-to-text conversion using industry-standard services like Google Translate and IBM Watson.

## Features

- **Advanced Text Translation**:
  - Multi-provider translation with automatic fallback (Google Translate → Local Translate)
  - Support for 100+ languages with automatic language detection
  - Batch translation capabilities for multiple texts
  - Configurable service URLs, proxies, and timeout settings
  - Comprehensive error handling and provider switching

- **Professional Audio Transcription**:
  - Speech-to-text conversion using IBM Watson Cloud services
  - Support for various audio formats (WAV, MP3, FLAC, etc.)
  - Batch processing of audio files with automated workflows
  - Customisable output formats and file management
  - Enterprise-grade accuracy and reliability

- **Language Detection Services**:
  - Automatic language identification with confidence scoring
  - Support for single texts and batch processing
  - Fallback mechanisms for service availability issues
  - Detailed attribute reporting and debugging capabilities

- **Robust Architecture**:
  - Intelligent provider switching and error recovery
  - Comprehensive parameter validation and type checking
  - Professional logging and progress reporting
  - Modular design for easy integration and customisation

## Installation

### Prerequisites

Before installing, please ensure the following dependencies are available on your system:

- **Core Translation Libraries**:

  ```bash
  pip install googletrans==4.0.0rc1 translate
  ```

- **Audio Transcription Libraries**:

  ```bash
  pip install ibm-watson ibm-cloud-sdk-core
  ```

- **Internal Package Dependencies**:

  ```bash
  pip install filewise pygenutils
  ```

- **Complete Installation** (all dependencies):

  ```bash
  pip install googletrans==4.0.0rc1 translate ibm-watson ibm-cloud-sdk-core filewise pygenutils
  ```

  Or via Anaconda (recommended for IBM Watson compatibility):

  ```bash
  conda install -c conda-forge googletrans translate
  conda install -c anaconda ibm-watson
  pip install filewise pygenutils
  ```

### Installation (from PyPI)

Install the package using pip:

```bash
pip install lingualab
```

### Development Installation

For development purposes, you can install the package in editable mode:

```bash
git clone https://github.com/yourusername/lingualab.git
cd lingualab
pip install -e .
```

## Usage

### Basic Text Translation

```python
from LinguaLab.text_translations import translate_string

# Simple translation
result = translate_string(
    phrase_or_words="Hello, how are you today?",
    lang_origin="en",
    lang_translation="es",
    procedure="translate"
)
print(result.text)  # "Hola, ¿cómo estás hoy?"

# Batch translation
phrases = [
    "Good morning",
    "Thank you very much",
    "See you later"
]
results = translate_string(
    phrase_or_words=phrases,
    lang_origin="en",
    lang_translation="fr",
    procedure="translate"
)
for result in results:
    print(f"{result.origin} → {result.text}")
```

### Advanced Translation with Fallback

```python
from LinguaLab.text_translations import translate_string

# Translation with custom configuration and automatic fallback
result = translate_string(
    phrase_or_words="Machine learning is transforming technology",
    lang_origin="en",
    lang_translation="de",
    procedure="translate",
    service_urls=['translate.google.com', 'translate.google.co.kr'],
    user_agent="Mozilla/5.0 (custom agent)",
    timeout=10,
    provider="MyMemory",  # Fallback provider
    print_attributes=True  # Show detailed information
)
```

### Language Detection

```python
from LinguaLab.text_translations import translate_string

# Detect language with confidence score
detection = translate_string(
    phrase_or_words=None,  # Not used for detection
    lang_origin=None,      # Not used for detection
    procedure="detect",
    text_which_language_to_detect="Bonjour, comment allez-vous?",
    print_attributes=True
)
# Output: Detected language: fr, Confidence: 0.95
```

### Audio Transcription Setup

```python
from LinguaLab.transcribe_video_files import save_transcription_in_file

# First, configure your IBM Watson credentials
# Set API_KEY and SERVICE_ID in the module or as environment variables

# The module automatically processes audio files in the configured directory
# and provides transcription services with the following features:

# 1. Automatic file discovery and processing
# 2. Support for various audio formats
# 3. Configurable output options (print/save)
# 4. Professional transcription accuracy
```

### Batch Audio Processing Example

```python
# Configuration example for batch transcription
# (Modify the constants in transcribe_video_files.py)

# Set your file path
FILES2TRANSCRIBE_PATH = "/path/to/your/audio/files"

# Configure processing options
PRINT_TRANSCRIPTION = True   # Display transcriptions
SAVE_TRANSCRIPTION = True    # Save to text files

# Set IBM Watson credentials
API_KEY = "your_ibm_watson_api_key"
SERVICE_ID = "your_service_id"

# The module will automatically:
# 1. Find all WAV files in the specified directory
# 2. Process each file through IBM Watson Speech-to-Text
# 3. Save transcriptions with "_transcription.txt" suffix
# 4. Provide progress feedback and error handling
```

### Professional Translation Workflow

```python
from LinguaLab.text_translations import translate_string, get_googletrans_version

# Check service availability
try:
    version = get_googletrans_version()
    print(f"Google Translate version: {version}")
except Exception as e:
    print("Google Translate service may be unavailable")

# Multi-language document processing
documents = {
    "english": "Artificial intelligence is revolutionising industries worldwide.",
    "spanish": "La inteligencia artificial está revolucionando las industrias mundialmente.",
    "french": "L'intelligence artificielle révolutionne les industries dans le monde entier."
}

target_languages = ["de", "it", "pt", "ru"]

for doc_lang, text in documents.items():
    print(f"\nProcessing {doc_lang} document:")
    for target_lang in target_languages:
        try:
            result = translate_string(
                phrase_or_words=text,
                lang_origin="auto",  # Auto-detect source language
                lang_translation=target_lang,
                procedure="translate",
                timeout=15
            )
            print(f"  → {target_lang}: {result.text[:50]}...")
        except Exception as e:
            print(f"  → {target_lang}: Translation failed - {e}")
```

## Project Structure

The package is organised as a focused language processing toolkit:

```text
LinguaLab/
├── text_translations.py        # Multi-provider translation services
├── transcribe_video_files.py   # IBM Watson audio transcription
├── __init__.py                  # Package initialisation
├── CHANGELOG.md                 # Version history and updates
└── README.md                    # Package documentation
```

## Key Functions

### `translate_string()`
**Purpose**: Comprehensive text translation with multi-provider support and automatic fallback

**Key Features**:
- **Multi-provider support**: Google Translate (primary) with local Translate (fallback)
- **Language detection**: Automatic language identification with confidence scoring
- **Batch processing**: Handle single strings or lists of texts
- **Robust error handling**: Automatic provider switching on service failures
- **Flexible configuration**: Custom service URLs, proxies, timeouts, and user agents

**Parameters**:
- `phrase_or_words`: Text(s) to translate (string or list)
- `lang_origin`: Source language code (ISO 639-1)
- `lang_translation`: Target language code (default: "en")
- `procedure`: "translate" or "detect"
- `service_urls`: Custom Google Translate URLs
- `timeout`: Request timeout in seconds
- `provider`: Fallback provider ("MyMemory", "MicrosoftProvider", "LibreTranslate")
- `print_attributes`: Display detailed translation information

### `save_transcription_in_file()`
**Purpose**: Professional audio transcription using IBM Watson Speech-to-Text

**Key Features**:
- **Enterprise-grade accuracy**: IBM Watson Cloud Speech-to-Text service
- **Multiple audio formats**: WAV, MP3, FLAC, and other common formats
- **Batch processing**: Automatic discovery and processing of audio files
- **Flexible output**: Save transcriptions to text files or display results
- **Progress tracking**: Real-time feedback during processing

**Configuration**:
- `API_KEY`: IBM Watson API key
- `SERVICE_ID`: IBM Watson service instance ID
- `FILES2TRANSCRIBE_PATH`: Directory containing audio files
- `PRINT_TRANSCRIPTION`: Display transcriptions in console
- `SAVE_TRANSCRIPTION`: Save transcriptions to files

## Advanced Features

### Multi-Provider Translation Architecture
- **Primary Provider**: Google Translate with unlimited free usage
- **Fallback Provider**: Local Translate package with Microsoft/MyMemory APIs
- **Automatic Switching**: Seamless fallback when primary service is unavailable
- **Error Recovery**: Intelligent handling of service bans and network issues

### Professional Audio Processing
- **IBM Watson Integration**: Enterprise-grade speech recognition accuracy
- **Batch Workflow**: Automated processing of multiple audio files
- **Format Flexibility**: Support for various audio formats and quality levels
- **Output Management**: Configurable file naming and storage options

### Robust Error Handling
- **Service Monitoring**: Automatic detection of service availability issues
- **Graceful Degradation**: Fallback mechanisms for service interruptions
- **Detailed Logging**: Comprehensive error reporting and debugging information
- **Parameter Validation**: Type checking and input validation

## Supported Languages

### Translation Services
- **100+ Languages**: Full support through Google Translate API
- **Popular Languages**: English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Hindi, and many more
- **Language Detection**: Automatic identification of source languages
- **Regional Variants**: Support for regional language variations

### Audio Transcription
- **Multiple Languages**: Support depends on IBM Watson service configuration
- **High Accuracy**: Professional-grade transcription quality
- **Custom Models**: Ability to use domain-specific language models
- **Real-time Processing**: Fast transcription with enterprise SLA

## Version Information

Current version: **3.4.3**

### Recent Updates (v3.4.3)
- Replaced deprecated `catch_shell_prompt_output` with `run_system_command`
- Updated constant naming conventions to uppercase
- Improved import structure and package organisation
- Enhanced variable naming for better code clarity

For detailed version history, see [CHANGELOG.md](CHANGELOG.md).

## API Configuration

### IBM Watson Setup

1. **Create IBM Cloud Account**:
   - Sign up at [IBM Cloud](https://cloud.ibm.com/)
   - Navigate to Watson services

2. **Create Speech-to-Text Service**:
   - Go to IBM Cloud Catalog
   - Search for "Speech to Text"
   - Create a new service instance

3. **Get Credentials**:
   - Access your service instance
   - Go to "Service credentials" tab
   - Copy API key and service URL

4. **Configure LinguaLab**:
   ```python
   # Set in transcribe_video_files.py
   API_KEY = "your_api_key_here"
   SERVICE_ID = "your_service_id_here"
   ```

### Google Translate Configuration

Google Translate integration is automatic, but you can customise:

```python
# Custom service URLs for better reliability
service_urls = [
    'translate.google.com',
    'translate.google.co.kr',
    'translate.google.co.uk'
]

# Custom user agent
user_agent = "Mozilla/5.0 (compatible; LinguaLab/3.4.3)"

# Proxy configuration
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}
```

## Error Handling

The package provides comprehensive error handling for various scenarios:

### Translation Errors
```python
try:
    result = translate_string(
        phrase_or_words="Hello world",
        lang_origin="en",
        lang_translation="invalid_code"
    )
except ValueError as e:
    print(f"Invalid language code: {e}")
except AttributeError as e:
    print("Google Translate service unavailable, trying fallback...")
```

### Transcription Errors
- **Authentication Errors**: Invalid IBM Watson credentials
- **Audio Format Errors**: Unsupported audio file formats
- **Network Errors**: Connection issues with IBM Watson services
- **File Access Errors**: Permission or file not found issues

## Performance Considerations

### Translation Performance
- **Batch Processing**: More efficient for multiple texts
- **Caching**: Consider implementing local caching for repeated translations
- **Rate Limiting**: Be aware of service rate limits for high-volume usage
- **Fallback Latency**: Local providers may have different response times

### Transcription Performance
- **File Size**: Larger audio files take longer to process
- **Audio Quality**: Higher quality audio provides better accuracy
- **Network Speed**: IBM Watson requires stable internet connection
- **Concurrent Processing**: Consider async processing for multiple files

## System Requirements

- **Python**: 3.8 or higher
- **Internet Connection**: Required for translation and transcription services
- **Audio Support**: For transcription features
- **Memory**: Sufficient RAM for processing large audio files

## Dependencies

### Core Dependencies
- **googletrans**: Google Translate API access
- **translate**: Alternative translation provider
- **ibm-watson**: IBM Watson Cloud services
- **ibm-cloud-sdk-core**: IBM Cloud SDK core functionality

### Internal Dependencies
- **filewise**: File operations and path utilities
- **pygenutils**: General utility functions and string handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines
- Follow existing code structure and error handling patterns
- Add comprehensive docstrings with parameter descriptions
- Include error handling for all external service calls
- Test with various languages and audio formats
- Update changelog for significant changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Google Translate Team** for providing accessible translation services
- **IBM Watson Team** for enterprise-grade speech recognition technology
- **Open Source Translation Communities** for alternative translation providers
- **Python Language Processing Community** for tools and best practices

## Contact

For any questions or suggestions, please open an issue on GitHub or contact the maintainers.

## Troubleshooting

### Common Issues

1. **Google Translate "NoneType" Error**:
   ```bash
   # This usually indicates IP-based blocking
   # The package automatically falls back to alternative providers
   # Wait and try again, or use alternative providers directly
   ```

2. **IBM Watson Authentication Error**:
   ```bash
   # Verify your API credentials
   # Check service instance status in IBM Cloud console
   # Ensure sufficient credits/quota available
   ```

3. **Audio File Processing Issues**:
   ```bash
   # Verify audio file format compatibility
   # Check file permissions and accessibility
   # Ensure stable internet connection for IBM Watson
   ```

### Getting Help

- Check the [CHANGELOG.md](CHANGELOG.md) for recent updates
- Review function docstrings for parameter details
- Test with simple examples before complex workflows
- Open an issue on GitHub for bugs or feature requests

### Service Status

- **Google Translate**: Free tier with usage limits
- **IBM Watson**: Paid service with free tier available
- **Alternative Providers**: Various pricing models and capabilities

Monitor service status and plan accordingly for production usage.
