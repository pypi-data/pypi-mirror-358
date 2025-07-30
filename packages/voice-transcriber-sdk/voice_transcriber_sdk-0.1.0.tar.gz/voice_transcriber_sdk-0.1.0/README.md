# Voice Transcriber SDK

Python SDK for interacting with the Voice Transcriber Service API.

## Installation

You can install the SDK using pip:

```bash
pip install voice_transcriber_sdk
```

## Usage

### Initialize the Client

```python
from voice_transcriber_sdk import VoiceTranscriberClient

# Initialize with API key
client = VoiceTranscriberClient(api_key="your_api_key_here")

# Or set environment variable
# export VOICE_TRANSCRIBER_API_KEY=your_api_key_here
# client = VoiceTranscriberClient()
```

### Process Audio

```python
# Process an audio file
result = client.process_audio("https://example.com/audio.mp3")
print(f"Processed messages: {result.messages}")
```

### Generate Summary

```python
# Generate summary for a conversation
summary = client.generate_summary("""Your conversation text here""")
print(f"Summary: {summary.summary}")
```

### Validate API Key

```python
# Check if API key is valid
is_valid = client.validate_api_key()
print(f"API key is valid: {is_valid}")
```

## Requirements

- Python 3.8 or higher
- requests >= 2.31.0
- python-dotenv >= 1.0.0

## Error Handling

The SDK uses standard Python exceptions. Common exceptions include:
- `requests.exceptions.RequestException`: For network-related errors
- `ValueError`: For invalid input parameters
- `HTTPError`: For HTTP errors from the API

## API Documentation

For full API documentation, visit: https://conversation-from-audio.onrender.com/docs

## License

MIT License - see LICENSE file for details
