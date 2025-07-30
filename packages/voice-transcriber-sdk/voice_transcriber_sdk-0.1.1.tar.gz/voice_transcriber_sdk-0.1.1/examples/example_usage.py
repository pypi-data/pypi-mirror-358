from voice_transcriber_sdk import VoiceTranscriberClient

# Replace with your actual API key
API_KEY = "your_api_key_here"

# Initialize the client
client = VoiceTranscriberClient(api_key=API_KEY)

# Test audio processing
try:
    # Replace with a valid audio URL
    audio_url = "https://example.com/test-audio.mp3"
    result = client.process_audio(audio_url)
    print("\nAudio Processing Result:")
    print(f"Messages: {result.messages}")
    print(f"Summary: {result.summary}")
except Exception as e:
    print(f"Error processing audio: {str(e)}")

# Test summary generation
try:
    conversation_text = """
    User: Hi, can you help me with my order?
    Assistant: Of course! What's your order number?
    User: It's 123456
    Assistant: Let me check that for you...
    """
    
    summary = client.generate_summary(conversation_text)
    print("\nConversation Summary:")
    print(f"Summary: {summary.summary}")
except Exception as e:
    print(f"Error generating summary: {str(e)}")

# Test health check
try:
    status = client.get_health_status()
    print("\nService Health Status:")
    print(f"Status: {status}")
except Exception as e:
    print(f"Error checking health: {str(e)}")

# Test API key validation
print("\nAPI Key Validation:")
print(f"API key is valid: {client.validate_api_key()}")
