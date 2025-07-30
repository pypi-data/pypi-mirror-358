import os
import sys
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the parent directory to Python path so we can import without installing
current_dir = Path(__file__).parent
client_dir = current_dir.parent
sys.path.insert(0, str(client_dir))

import weavium


class TestWeaviumClient:
    """Test cases for WeaviumClient class."""
    
    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = weavium.WeaviumClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert "x-weavium-api-key" in client.session.headers
        assert client.session.headers["x-weavium-api-key"] == "test-key"
    
    def test_init_with_env_var(self):
        """Test client initialization with environment variable."""
        with patch.dict(os.environ, {"WEAVIUM_API_KEY": "env-key"}):
            client = weavium.WeaviumClient()
            assert client.api_key == "env-key"
    
    def test_init_without_api_key(self):
        """Test client initialization without API key shows warning."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.warns(UserWarning, match="No API key provided"):
                client = weavium.WeaviumClient()
                assert client.api_key is None
    
    def test_create_message_helpers(self):
        """Test message creation helper methods."""
        client = weavium.WeaviumClient(api_key="test-key")
        
        user_msg = client.create_user_message("Hello")
        assert user_msg.role == "user"
        assert user_msg.content == "Hello"
        
        system_msg = client.create_system_message("System prompt")
        assert system_msg.role == "system"
        assert system_msg.content == "System prompt"
        
        assistant_msg = client.create_assistant_message("Response")
        assert assistant_msg.role == "assistant"
        assert assistant_msg.content == "Response"


class TestCompress:
    """Test cases for compress method."""
    
    @patch('requests.Session.request')
    def test_compress_success(self, mock_request):
        """Test successful compression request."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [
                {"role": "system", "content": "System prompt"},
                {"role": "user", "content": "Compressed content"}
            ]
        }
        mock_response.headers = {
            "X-Compression-Rate": "0.3",
            "X-Compression-Original-Tokens": "100",
            "X-Compression-Compressed-Tokens": "30"
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        client = weavium.WeaviumClient(api_key="test-key")
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Long user message"}
        ]
        
        result = client.compress(messages=messages, compression_rate=0.3)
        
        # Verify result
        assert isinstance(result, weavium.CompressionResult)
        assert len(result.messages) == 2
        assert result.compression_rate == "0.3"
        assert result.original_tokens == 100
        assert result.compressed_tokens == 30
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert "/api/compress" in call_args[1]["url"]
        assert call_args[1]["json"]["messages"] == messages
    
    def test_compress_empty_messages(self):
        """Test compress with empty messages raises ValueError."""
        client = weavium.WeaviumClient(api_key="test-key")
        
        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            client.compress(messages=[])
    
    def test_compress_invalid_message_format(self):
        """Test compress with invalid message format raises ValueError."""
        client = weavium.WeaviumClient(api_key="test-key")
        
        # Missing role
        with pytest.raises(ValueError, match="must have 'role' and 'content' keys"):
            client.compress(messages=[{"content": "test"}])
        
        # Missing content
        with pytest.raises(ValueError, match="must have 'role' and 'content' keys"):
            client.compress(messages=[{"role": "user"}])
        
        # Invalid type
        with pytest.raises(ValueError, match="Invalid message type"):
            client.compress(messages=["invalid"])
    
    def test_compress_with_llm_message_objects(self):
        """Test compress with LLMMessage objects."""
        client = weavium.WeaviumClient(api_key="test-key")
        messages = [
            weavium.LLMMessage(role="system", content="System"),
            weavium.LLMMessage(role="user", content="User message")
        ]
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"messages": []}
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            client.compress(messages=messages)
            
            # Verify the request data
            call_args = mock_request.call_args
            expected_messages = [msg.to_dict() for msg in messages]
            assert call_args[1]["data"]["messages"] == expected_messages


class TestInject:
    """Test cases for inject method."""
    
    @patch('requests.Session.request')
    def test_inject_success(self, mock_request):
        """Test successful inject request."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "dataset_id": "dataset-123",
            "dataset_name": "Test Dataset",
            "items_created": 2,
            "system_prompt_hash": "hash123"
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        client = weavium.WeaviumClient(api_key="test-key")
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message 1"},
            {"role": "user", "content": "User message 2"}
        ]
        
        result = client.inject(messages=messages)
        
        # Verify result
        assert isinstance(result, weavium.InjectResult)
        assert result.dataset_id == "dataset-123"
        assert result.dataset_name == "Test Dataset"
        assert result.items_created == 2
        assert result.system_prompt_hash == "hash123"
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert "/api/inject" in call_args[1]["url"]
    
    def test_inject_with_dataset_id(self):
        """Test inject with specific dataset ID."""
        client = weavium.WeaviumClient(api_key="test-key")
        messages = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "User message"}
        ]
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "dataset_id": "specific-dataset",
                "dataset_name": "Dataset",
                "items_created": 1,
                "system_prompt_hash": "hash"
            }
            mock_request.return_value = mock_response
            
            client.inject(messages=messages, dataset_id="specific-dataset")
            
            # Verify dataset ID header was sent
            call_args = mock_request.call_args
            assert call_args[1]["headers"]["x-weavium-dataset-id"] == "specific-dataset"
    
    def test_inject_empty_messages(self):
        """Test inject with empty messages raises ValueError."""
        client = weavium.WeaviumClient(api_key="test-key")
        
        with pytest.raises(ValueError, match="Messages list cannot be empty"):
            client.inject(messages=[])
    
    def test_inject_no_user_messages(self):
        """Test inject without user messages raises ValueError."""
        client = weavium.WeaviumClient(api_key="test-key")
        messages = [{"role": "system", "content": "System only"}]
        
        with pytest.raises(ValueError, match="At least one user message is required"):
            client.inject(messages=messages)
    
    def test_inject_no_system_message_without_dataset_id(self):
        """Test inject without system message and no dataset ID raises ValueError."""
        client = weavium.WeaviumClient(api_key="test-key")
        messages = [{"role": "user", "content": "User only"}]
        
        with pytest.raises(ValueError, match="System message is required when dataset_id is not provided"):
            client.inject(messages=messages)


class TestMakeRequest:
    """Test cases for _make_request method."""
    
    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        client = weavium.WeaviumClient(api_key="test-key")
        
        result = client._make_request(
            method="POST",
            endpoint="/test",
            data={"key": "value"},
            headers={"Custom": "header"}
        )
        
        assert result == mock_response
        mock_request.assert_called_once()
        
        # Verify call arguments
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["url"] == "https://api.weavium.com/test"
        assert call_args[1]["json"] == {"key": "value"}
        assert "Custom" in call_args[1]["headers"]
        assert "x-weavium-api-key" in call_args[1]["headers"]
    
    @patch('requests.Session.request')
    def test_make_request_failure(self, mock_request):
        """Test API request failure."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.RequestException("API Error")
        mock_request.return_value = mock_response
        
        client = weavium.WeaviumClient(api_key="test-key")
        
        with pytest.raises(requests.RequestException):
            client._make_request(method="GET", endpoint="/test")


class TestDataClasses:
    """Test cases for data classes."""
    
    def test_llm_message_to_dict(self):
        """Test LLMMessage to_dict method."""
        message = weavium.LLMMessage(role="user", content="Hello")
        result = message.to_dict()
        
        assert result == {"role": "user", "content": "Hello"}
    
    def test_compression_result_from_response(self):
        """Test weavium.CompressionResult.from_response class method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [
                {"role": "user", "content": "Compressed content"}
            ]
        }
        mock_response.headers = {
            "X-Compression-Rate": "0.25",
            "X-Compression-Original-Tokens": "100",
            "X-Compression-Compressed-Tokens": "25"
        }
        
        original_messages = [weavium.LLMMessage(role="user", content="Original")]
        result = weavium.CompressionResult.from_response(mock_response, original_messages)
        
        assert len(result.messages) == 1
        assert result.messages[0].content == "Compressed content"
        assert result.compression_rate == "0.25"
        assert result.original_tokens == 100
        assert result.compressed_tokens == 25
    
    def test_inject_result_from_response(self):
        """Test weavium.InjectResult.from_response class method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "dataset_id": "test-id",
            "dataset_name": "Test Dataset",
            "items_created": 5,
            "system_prompt_hash": "abc123"
        }
        
        result = weavium.InjectResult.from_response(mock_response)
        
        assert result.dataset_id == "test-id"
        assert result.dataset_name == "Test Dataset"
        assert result.items_created == 5
        assert result.system_prompt_hash == "abc123"


class TestEnums:
    """Test cases for enums."""
    
    def test_compression_chunk_strategy_values(self):
        """Test weavium.CompressionChunkStrategy enum values."""
        assert weavium.CompressionChunkStrategy.NONE.value == "none"
        assert weavium.CompressionChunkStrategy.SLIDING_WINDOW.value == "sliding_window"
        assert weavium.CompressionChunkStrategy.SEMANTIC.value == "semantic"


if __name__ == "__main__":
    pytest.main([__file__]) 