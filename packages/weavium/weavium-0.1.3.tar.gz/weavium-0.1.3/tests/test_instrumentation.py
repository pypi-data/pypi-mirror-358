import os
import sys
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the parent directory to Python path so we can import without installing
current_dir = Path(__file__).parent
client_dir = current_dir.parent
sys.path.insert(0, str(client_dir))

import weavium

# Skip tests if boto3 is not available
try:
    import boto3
    import botocore.client
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

pytestmark = pytest.mark.skipif(not BOTO3_AVAILABLE, reason="boto3 not available")


class TestBoto3Instrumenter:
    """Test cases for Boto3Instrumenter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.weavium_client = Mock(spec=weavium.WeaviumClient)
        self.instrumenter = weavium.Boto3Instrumenter(
            weavium_client=self.weavium_client,
            auto_inject=True
        )
    
    def test_init_without_boto3(self):
        """Test initialization fails when boto3 is not available."""
        with patch('weavium.instrumentation.BOTO3_AVAILABLE', False):
            with pytest.raises(weavium.instrumentation.Boto3InstrumentationError):
                weavium.Boto3Instrumenter(self.weavium_client)
    
    def test_init_with_parameters(self):
        """Test initialization with various parameters."""
        instrumenter = weavium.Boto3Instrumenter(
            weavium_client=self.weavium_client,
            auto_inject=False,
            capture_requests=True,
            capture_responses=False,
            dataset_id="test-dataset",
            filter_services=['bedrock-runtime', 'sagemaker-runtime']
        )
        
        assert instrumenter.weavium_client == self.weavium_client
        assert instrumenter.auto_inject is False
        assert instrumenter.capture_requests is True
        assert instrumenter.capture_responses is False
        assert instrumenter.dataset_id == "test-dataset"
        assert instrumenter.filter_services == ['bedrock-runtime', 'sagemaker-runtime']
    
    def test_instrument_and_uninstrument(self):
        """Test instrumenting and uninstrumenting boto3."""
        # Test instrument
        self.instrumenter.instrument()
        assert self.instrumenter._is_instrumented is True
        
        # Test uninstrument
        self.instrumenter.uninstrument()
        assert self.instrumenter._is_instrumented is False
    
    def test_double_instrument_warning(self):
        """Test that double instrumentation shows warning."""
        self.instrumenter.instrument()
        
        with patch('weavium.instrumentation.logger') as mock_logger:
            self.instrumenter.instrument()
            mock_logger.warning.assert_called_with("Boto3 instrumentation already active")
    
    def test_extract_messages_anthropic(self):
        """Test message extraction for Anthropic Claude format."""
        body_data = {
            "messages": [
                {"role": "user", "content": "Hello Claude"}
            ],
            "system": "You are a helpful assistant",
            "max_tokens": 100
        }
        api_params = {"modelId": "anthropic.claude-3-sonnet-20240229-v1:0"}
        
        messages = self.instrumenter._extract_messages_from_request(body_data, api_params)
        
        assert len(messages) == 2
        assert messages[0].role == "system"
        assert messages[0].content == "You are a helpful assistant"
        assert messages[1].role == "user"
        assert messages[1].content == "Hello Claude"
    
    def test_extract_messages_anthropic_multipart(self):
        """Test message extraction for Anthropic Claude with multipart content."""
        body_data = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hello"},
                        {"type": "text", "text": "World"}
                    ]
                }
            ]
        }
        api_params = {"modelId": "anthropic.claude-3-sonnet-20240229-v1:0"}
        
        messages = self.instrumenter._extract_messages_from_request(body_data, api_params)
        
        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Hello World"
    
    def test_extract_messages_titan(self):
        """Test message extraction for Amazon Titan format."""
        body_data = {
            "inputText": "Explain machine learning",
            "textGenerationConfig": {"maxTokenCount": 100}
        }
        api_params = {"modelId": "amazon.titan-text-express-v1"}
        
        messages = self.instrumenter._extract_messages_from_request(body_data, api_params)
        
        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Explain machine learning"
    
    def test_extract_messages_ai21(self):
        """Test message extraction for AI21 format."""
        body_data = {
            "prompt": "Write a story about AI",
            "maxTokens": 200
        }
        api_params = {"modelId": "ai21.j2-ultra-v1"}
        
        messages = self.instrumenter._extract_messages_from_request(body_data, api_params)
        
        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Write a story about AI"
    
    def test_extract_messages_cohere(self):
        """Test message extraction for Cohere format."""
        body_data = {
            "message": "What is quantum computing?",
            "chat_history": [
                {"role": "USER", "message": "Hello"},
                {"role": "CHATBOT", "message": "Hi there!"}
            ]
        }
        api_params = {"modelId": "cohere.command-text-v14"}
        
        messages = self.instrumenter._extract_messages_from_request(body_data, api_params)
        
        assert len(messages) == 3
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Hi there!"
        assert messages[2].role == "user"
        assert messages[2].content == "What is quantum computing?"
    
    def test_extract_messages_generic(self):
        """Test message extraction for generic format."""
        body_data = {
            "messages": [
                {"role": "user", "content": "Generic message"}
            ]
        }
        api_params = {"modelId": "unknown.model-v1"}
        
        messages = self.instrumenter._extract_messages_from_request(body_data, api_params)
        
        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Generic message"
    
    def test_extract_assistant_response_anthropic(self):
        """Test assistant response extraction for Anthropic."""
        response_data = {
            "content": [
                {"type": "text", "text": "Hello! How can I help you?"}
            ]
        }
        api_params = {"modelId": "anthropic.claude-3-sonnet-20240229-v1:0"}
        
        message = self.instrumenter._extract_assistant_response(response_data, api_params)
        
        assert message is not None
        assert message.role == "assistant"
        assert message.content == "Hello! How can I help you?"
    
    def test_extract_assistant_response_titan(self):
        """Test assistant response extraction for Titan."""
        response_data = {
            "results": [
                {"outputText": "Machine learning is..."}
            ]
        }
        api_params = {"modelId": "amazon.titan-text-express-v1"}
        
        message = self.instrumenter._extract_assistant_response(response_data, api_params)
        
        assert message is not None
        assert message.role == "assistant"
        assert message.content == "Machine learning is..."
    
    def test_inject_messages(self):
        """Test message injection into Weavium."""
        messages = [
            weavium.LLMMessage(role="user", content="Test message")
        ]
        
        # Mock inject result
        mock_result = Mock()
        mock_result.dataset_id = "test-dataset"
        self.weavium_client.inject.return_value = mock_result
        
        self.instrumenter._inject_messages(messages, "InvokeModel", "request")
        
        # Verify inject was called
        self.weavium_client.inject.assert_called_once()
        call_args = self.weavium_client.inject.call_args
        
        # Should have system message added
        injected_messages = call_args[1]["messages"]
        assert len(injected_messages) == 2
        assert injected_messages[0].role == "system"
        assert "AWS Bedrock" in injected_messages[0].content
        assert injected_messages[1] == messages[0]
    
    def test_conversation_management(self):
        """Test conversation capture and management."""
        # Test with auto_inject=False
        instrumenter = weavium.Boto3Instrumenter(
            weavium_client=self.weavium_client,
            auto_inject=False
        )
        
        # Simulate capturing a conversation
        messages = [weavium.LLMMessage(role="user", content="Test")]
        instrumenter._conversations.append({
            'messages': messages,
            'operation': 'InvokeModel',
            'type': 'request',
            'timestamp': 123456789
        })
        
        # Test get_captured_conversations
        captured = instrumenter.get_captured_conversations()
        assert len(captured) == 1
        assert captured[0]['operation'] == 'InvokeModel'
        
        # Test manual injection
        mock_result = Mock()
        mock_result.dataset_id = "test"
        self.weavium_client.inject.return_value = mock_result
        
        instrumenter.inject_pending_conversations()
        assert len(instrumenter._conversations) == 0
        self.weavium_client.inject.assert_called_once()
        
        # Test clear without injection
        instrumenter._conversations.append({'test': 'data'})
        instrumenter.clear_captured_conversations()
        assert len(instrumenter._conversations) == 0


class TestGlobalInstrumentation:
    """Test cases for global instrumentation functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Clean up any existing global instrumenter
        weavium.instrumentation._global_instrumenter = None
        self.weavium_client = Mock(spec=weavium.WeaviumClient)
    
    def teardown_method(self):
        """Clean up after tests."""
        # Clean up global instrumenter
        if weavium.instrumentation._global_instrumenter:
            weavium.instrumentation._global_instrumenter.uninstrument()
            weavium.instrumentation._global_instrumenter = None
    
    def test_instrument_boto3(self):
        """Test global instrument_boto3 function."""
        instrumenter = weavium.instrument_boto3(self.weavium_client)
        
        assert instrumenter is not None
        assert isinstance(instrumenter, weavium.Boto3Instrumenter)
        assert instrumenter._is_instrumented is True
        assert weavium.instrumentation._global_instrumenter == instrumenter
    
    def test_instrument_boto3_with_parameters(self):
        """Test global instrument_boto3 with parameters."""
        instrumenter = weavium.instrument_boto3(
            weavium_client=self.weavium_client,
            auto_inject=False,
            dataset_id="test-dataset",
            filter_services=['bedrock-runtime']
        )
        
        assert instrumenter.auto_inject is False
        assert instrumenter.dataset_id == "test-dataset"
        assert instrumenter.filter_services == ['bedrock-runtime']
    
    def test_double_instrument_warning(self):
        """Test warning when instrumenting twice."""
        weavium.instrument_boto3(self.weavium_client)
        
        with patch('weavium.instrumentation.logger') as mock_logger:
            weavium.instrument_boto3(self.weavium_client)
            mock_logger.warning.assert_called_with(
                "Boto3 already instrumented. Uninstrumenting previous instance."
            )
    
    def test_uninstrument_boto3(self):
        """Test global uninstrument_boto3 function."""
        # First instrument
        weavium.instrument_boto3(self.weavium_client)
        assert weavium.instrumentation._global_instrumenter is not None
        
        # Then uninstrument
        weavium.uninstrument_boto3()
        assert weavium.instrumentation._global_instrumenter is None
    
    def test_uninstrument_without_instrument(self):
        """Test uninstrument when nothing is instrumented."""
        with patch('weavium.instrumentation.logger') as mock_logger:
            weavium.uninstrument_boto3()
            mock_logger.warning.assert_called_with("No active boto3 instrumentation found")
    
    def test_get_instrumenter(self):
        """Test get_instrumenter function."""
        # No instrumenter initially
        assert weavium.get_instrumenter() is None
        
        # After instrumenting
        instrumenter = weavium.instrument_boto3(self.weavium_client)
        assert weavium.get_instrumenter() == instrumenter
        
        # After uninstrumenting
        weavium.uninstrument_boto3()
        assert weavium.get_instrumenter() is None


class TestAPICallInterception:
    """Test cases for API call interception."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.weavium_client = Mock(spec=weavium.WeaviumClient)
        self.instrumenter = weavium.Boto3Instrumenter(
            weavium_client=self.weavium_client,
            auto_inject=True
        )
        self.instrumenter.instrument()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.instrumenter.uninstrument()
    
    @patch('botocore.client.BaseClient._make_api_call')
    def test_api_call_interception_bedrock(self, mock_original_call):
        """Test that bedrock API calls are intercepted."""
        # Mock client
        mock_client = Mock()
        mock_client._service_model.service_name = 'bedrock-runtime'
        
        # Mock response
        mock_response = {"body": Mock()}
        mock_original_call.return_value = mock_response
        
        # Mock inject result
        mock_inject_result = Mock()
        mock_inject_result.dataset_id = "test"
        self.weavium_client.inject.return_value = mock_inject_result
        
        # Test API call
        api_params = {
            'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0',
            'body': json.dumps({
                'messages': [{'role': 'user', 'content': 'Hello'}],
                'max_tokens': 100
            })
        }
        
        # This should trigger interception
        result = self.instrumenter._handle_api_call(
            mock_client, 'InvokeModel', api_params, mock_original_call
        )
        
        # Verify original call was made
        mock_original_call.assert_called_once_with(mock_client, 'InvokeModel', api_params)
        
        # Verify injection was called (since auto_inject=True)
        self.weavium_client.inject.assert_called_once()
    
    @patch('botocore.client.BaseClient._make_api_call')
    def test_api_call_no_interception_other_service(self, mock_original_call):
        """Test that non-bedrock services are not intercepted."""
        # Mock client for different service
        mock_client = Mock()
        mock_client._service_model.service_name = 's3'
        
        mock_response = {"data": "test"}
        mock_original_call.return_value = mock_response
        
        # Test API call
        result = self.instrumenter._handle_api_call(
            mock_client, 'GetObject', {}, mock_original_call
        )
        
        # Should call original without interception
        mock_original_call.assert_called_once_with(mock_client, 'GetObject', {})
        
        # Should not inject anything
        self.weavium_client.inject.assert_not_called()
    
    def test_error_handling_in_interception(self):
        """Test error handling during API call interception."""
        mock_client = Mock()
        mock_client._service_model.service_name = 'bedrock-runtime'
        
        def mock_original_call(client, operation, params):
            return {"success": True}
        
        # Mock extraction to raise an error
        with patch.object(self.instrumenter, '_capture_request', side_effect=Exception("Test error")):
            with patch('weavium.instrumentation.logger') as mock_logger:
                result = self.instrumenter._handle_api_call(
                    mock_client, 'InvokeModel', {}, mock_original_call
                )
                
                # Should still return the original response
                assert result == {"success": True}
                
                # Should log the error
                mock_logger.error.assert_called() 