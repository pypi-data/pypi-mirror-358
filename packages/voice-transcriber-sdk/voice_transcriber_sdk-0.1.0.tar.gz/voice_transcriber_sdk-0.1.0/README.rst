=================
Voice Transcriber SDK
=================

A Python SDK for interacting with the Voice Transcriber Service API.

Features
========

* Process audio files
* Generate conversation summaries
* Validate API keys
* Get service health status

Installation
============

Install the latest stable version:

.. code-block:: bash

    pip install voice_transcriber_sdk

Install with development tools:

.. code-block:: bash

    pip install voice_transcriber_sdk[dev]

Install with documentation tools:

.. code-block:: bash

    pip install voice_transcriber_sdk[docs]

Basic Usage
===========

.. code-block:: python

    from voice_transcriber_sdk import VoiceTranscriberClient

    # Initialize client with API key
    client = VoiceTranscriberClient(api_key="your_api_key_here")

    # Process audio
    result = client.process_audio("https://example.com/audio.mp3")
    print(f"Processed messages: {result.messages}")

    # Generate summary
    summary = client.generate_summary("Your conversation text here")
    print(f"Summary: {summary.summary}")

Requirements
============

* Python 3.8 or higher
* requests >= 2.31.0
* python-dotenv >= 1.0.0
* httpx >= 0.24.1
* pydantic >= 2.0.0

Documentation
=============

For full API documentation, visit: https://conversation-from-audio.onrender.com/docs

License
========

MIT License - see LICENSE file for details
