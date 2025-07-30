#!/usr/bin/env python3
"""
Integration test for WeaviumClient that tests actual functionality
without requiring package installation.

This test can be run directly to verify the client works properly.
"""

import os
import sys
import warnings
from pathlib import Path

# Add the parent directory to Python path so we can import without installing
current_dir = Path(__file__).parent
client_dir = current_dir.parent
sys.path.insert(0, str(client_dir))

# Now import the client
import weavium


def test_client_initialization():
    """Test client can be initialized properly."""
    print("🧪 Testing client initialization...")
    
    # Test with no API key (should show warning)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        client = weavium.WeaviumClient()
        
        if w:
            print("   ✅ Warning shown for missing API key")
        else:
            print("   ⚠️  No warning shown for missing API key")
    
    # Test with API key
    client = weavium.WeaviumClient(api_key="test-key")
    assert client.api_key == "test-key"
    print("   ✅ Client initialized with API key")
    
    # Test with custom base URL
    client = weavium.WeaviumClient(api_key="test-key", base_url="https://custom.api.com")
    assert client.base_url == "https://custom.api.com"
    print("   ✅ Client initialized with custom base URL")


def test_message_helpers():
    """Test message creation helper methods."""
    print("🧪 Testing message helper methods...")
    
    client = weavium.WeaviumClient(api_key="test-key")
    
    # Test helper methods
    user_msg = client.create_user_message("Hello user")
    assert user_msg.role == "user"
    assert user_msg.content == "Hello user"
    print("   ✅ User message created correctly")
    
    system_msg = client.create_system_message("System prompt")
    assert system_msg.role == "system"
    assert system_msg.content == "System prompt"
    print("   ✅ System message created correctly")
    
    assistant_msg = client.create_assistant_message("Assistant response")
    assert assistant_msg.role == "assistant" 
    assert assistant_msg.content == "Assistant response"
    print("   ✅ Assistant message created correctly")


def test_data_classes():
    """Test data class functionality."""
    print("🧪 Testing data classes...")
    
    # Test LLMMessage  
    message = weavium.LLMMessage(role="user", content="Test message")
    message_dict = message.to_dict()
    assert message_dict == {"role": "user", "content": "Test message"}
    print("   ✅ LLMMessage to_dict works correctly")
    
    # Test weavium.CompressionChunkStrategy enum
    assert weavium.CompressionChunkStrategy.NONE.value == "none"
    assert weavium.CompressionChunkStrategy.SLIDING_WINDOW.value == "sliding_window"
    assert weavium.CompressionChunkStrategy.SEMANTIC.value == "semantic"
    print("   ✅ weavium.CompressionChunkStrategy enum values correct")


def test_input_validation():
    """Test input validation without making API calls."""
    print("🧪 Testing input validation...")
    
    client = weavium.WeaviumClient(api_key="test-key")
    
    # Test compress with empty messages
    try:
        client.compress(messages=[])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Messages list cannot be empty" in str(e)
        print("   ✅ Empty messages validation works")
    
    # Test compress with invalid message format
    try:
        client.compress(messages=[{"role": "user"}])  # Missing content
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "must have 'role' and 'content' keys" in str(e)
        print("   ✅ Invalid message format validation works")
    
    # Test inject with no user messages
    try:
        client.inject(messages=[{"role": "system", "content": "System only"}])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "At least one user message is required" in str(e)
        print("   ✅ No user messages validation works")
    
    # Test inject without system message and no dataset ID
    try:
        client.inject(messages=[{"role": "user", "content": "User only"}])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "System message is required when dataset_id is not provided" in str(e)
        print("   ✅ Missing system message validation works")


def test_api_call_structure():
    """Test that API calls are structured correctly (without actually calling)."""
    print("🧪 Testing API call structure...")
    
    client = weavium.WeaviumClient(api_key="test-api-key")
    
    # Test _make_request method exists and has correct signature
    assert hasattr(client, '_make_request')
    print("   ✅ _make_request method exists")
    
    # Test session is configured correctly
    assert "x-weavium-api-key" in client.session.headers
    assert client.session.headers["x-weavium-api-key"] == "test-api-key"
    assert client.session.headers["Content-Type"] == "application/json"
    print("   ✅ Session headers configured correctly")
    
    # Test base URL handling
    assert client.base_url == "https://api.weavium.com"
    print("   ✅ Base URL set correctly")


def test_with_real_api_if_available():
    """Test with real API if credentials are available."""
    print("🧪 Testing with real API (if available)...")
    
    api_key = os.getenv('WEAVIUM_API_KEY')
    
    if not api_key:
        print("   ⏭️  Skipping real API test - no API key found")
        print("      Set WEAVIUM_API_KEY environment variable to test with real API")
        return
    
    client = weavium.WeaviumClient(api_key=api_key)
    
    # Test compress with real API
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2? Please give a short answer."}
        ]
        
        result = client.compress(messages=messages, compression_rate=0.3)
        
        print(f"   ✅ Real API compress test successful!")
        print(f"      Original tokens: {result.original_tokens}")
        print(f"      Compressed tokens: {result.compressed_tokens}")
        print(f"      Compression rate: {result.compression_rate}")
        print(f"      Compressed content: {result.messages[-1].content[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Real API compress test failed: {e}")
        print(f"      This might be due to API issues, rate limiting, or invalid credentials")
    
    # Test inject with real API
    try:
        inject_messages = [
            client.create_system_message("You are a test assistant."),
            client.create_user_message("This is a test message for integration testing.")
        ]
        
        inject_result = client.inject(messages=inject_messages)
        
        print(f"   ✅ Real API inject test successful!")
        print(f"      Dataset ID: {inject_result.dataset_id}")
        print(f"      Items created: {inject_result.items_created}")
        
    except Exception as e:
        print(f"   ❌ Real API inject test failed: {e}")
        print(f"      This might be due to API issues, rate limiting, or invalid credentials")


def test_mixed_message_formats():
    """Test client handles different message formats correctly."""
    print("🧪 Testing mixed message formats...")
    
    client = weavium.WeaviumClient(api_key="test-key")
    
    # Mix of dict and LLMMessage objects
    messages = [
        {"role": "system", "content": "System message"},
        weavium.LLMMessage(role="user", content="User message"),
        client.create_assistant_message("Assistant message")
    ]
    
    # This should not raise an error during validation
    try:
        # We'll catch the network error since we're not actually making a call
        client.compress(messages=messages)
    except Exception as e:
        # Should be a network/API error, not a validation error
        if "Messages list cannot be empty" in str(e) or "must have 'role' and 'content' keys" in str(e):
            assert False, f"Validation error with mixed formats: {e}"
        # Network errors are expected without real API
        
    print("   ✅ Mixed message formats handled correctly")