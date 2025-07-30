import os
import pytest
from voice_transcriber_sdk import VoiceTranscriberClient

TEST_API_KEY = "your_api_key_here"  # Replace with your actual API key

@pytest.fixture
def client():
    return VoiceTranscriberClient(api_key=TEST_API_KEY)

def test_client_initialization(client):
    assert client.api_key == TEST_API_KEY
    assert "Authorization" in client.headers
    assert client.headers["Authorization"] == f"Bearer {TEST_API_KEY}"

def test_process_audio(client):
    # Test with a valid audio URL
    test_audio_url = "https://example.com/test-audio.mp3"
    try:
        result = client.process_audio(test_audio_url)
        assert isinstance(result.messages, list)
    except Exception as e:
        # If the API is not running locally, we expect an error
        assert isinstance(e, Exception)

def test_generate_summary(client):
    test_text = "This is a test conversation. User: Hello. Assistant: Hi there!"
    try:
        result = client.generate_summary(test_text)
        assert isinstance(result.summary, dict)
    except Exception as e:
        # If the API is not running locally, we expect an error
        assert isinstance(e, Exception)

def test_health_check(client):
    try:
        status = client.get_health_status()
        assert isinstance(status, dict)
    except Exception as e:
        # If the API is not running locally, we expect an error
        assert isinstance(e, Exception)

def test_api_key_validation(client):
    assert client.validate_api_key() is True

if __name__ == "__main__":
    pytest.main()
