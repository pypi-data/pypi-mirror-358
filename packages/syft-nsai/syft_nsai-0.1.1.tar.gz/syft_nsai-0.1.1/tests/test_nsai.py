"""
Test suite for syft-nsai package
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import syft_nsai as nsai
from syft_nsai import Chat, ChatCompletion, ChatCompletions, Choice, Message, NSAIClient


class TestMessage:
    """Test Message class"""

    def test_message_creation(self):
        """Test Message object creation"""
        content = "Hello, world!"
        message = Message(content)
        assert message.content == content

    def test_message_empty_content(self):
        """Test Message with empty content"""
        message = Message("")
        assert message.content == ""


class TestChoice:
    """Test Choice class"""

    def test_choice_creation(self):
        """Test Choice object creation"""
        content = "Test response"
        choice = Choice(content)
        assert isinstance(choice.message, Message)
        assert choice.message.content == content


class TestChatCompletion:
    """Test ChatCompletion class"""

    def test_chat_completion_with_string(self):
        """Test ChatCompletion with direct string content"""
        content = "Direct response"
        completion = ChatCompletion(content)

        assert len(completion.choices) == 1
        assert completion.choices[0].message.content == content

    def test_chat_completion_with_project_result(self):
        """Test ChatCompletion with project result"""
        mock_proj_res = Mock()
        completion = ChatCompletion(mock_proj_res)

        # Should have None choices initially (lazy loading)
        assert completion._choices is None
        assert completion._proj_res == mock_proj_res

    @patch("time.sleep")
    @patch("builtins.open")
    @patch("pathlib.Path.exists")
    def test_lazy_loading_success(self, mock_exists, mock_open, mock_sleep):
        """Test successful lazy loading of choices"""
        # Setup mocks
        mock_proj_res = Mock()
        mock_output_path = Mock()
        mock_output_path.absolute.return_value = Path("/fake/path")
        mock_proj_res.output.return_value = mock_output_path

        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.read.return_value = "AI response content"
        mock_open.return_value.__enter__.return_value = mock_file

        # Test
        completion = ChatCompletion(mock_proj_res)
        choices = completion.choices

        # Verify
        assert len(choices) == 1
        assert choices[0].message.content == "AI response content"
        mock_proj_res.output.assert_called_once_with(block=True)

    @patch("time.sleep")
    @patch("pathlib.Path.exists")
    def test_lazy_loading_timeout(self, mock_exists, mock_sleep):
        """Test lazy loading timeout"""
        # Setup mocks
        mock_proj_res = Mock()
        mock_output_path = Mock()
        mock_output_path.absolute.return_value = Path("/fake/path")
        mock_proj_res.output.return_value = mock_output_path

        mock_exists.return_value = False  # File never appears

        # Test
        completion = ChatCompletion(mock_proj_res)
        choices = completion.choices

        # Should return error message after timeout
        assert len(choices) == 1
        assert "Output file not found" in choices[0].message.content

    def test_lazy_loading_exception(self):
        """Test lazy loading with exception"""
        mock_proj_res = Mock()
        mock_proj_res.output.side_effect = Exception("Test error")

        completion = ChatCompletion(mock_proj_res)
        choices = completion.choices

        assert len(choices) == 1
        assert "Error waiting for project completion" in choices[0].message.content


class TestChat:
    """Test Chat class"""

    def test_chat_initialization(self):
        """Test Chat object initialization"""
        chat = Chat()
        assert isinstance(chat.completions, ChatCompletions)


class TestNSAIClient:
    """Test NSAIClient class"""

    def test_client_initialization(self):
        """Test NSAIClient initialization"""
        client = NSAIClient()
        assert isinstance(client.chat, Chat)
        assert isinstance(client.chat.completions, ChatCompletions)


class TestChatCompletions:
    """Test ChatCompletions class"""

    def test_create_method_signature(self):
        """Test create method accepts correct parameters"""
        completions = ChatCompletions()

        # Mock Dataset objects
        mock_dataset1 = Mock()
        mock_dataset1.name = "test_dataset_1"
        mock_dataset1.email = "test@example.com"

        mock_dataset2 = Mock()
        mock_dataset2.name = "test_dataset_2"
        mock_dataset2.email = "test@example.com"

        datasets = [mock_dataset1, mock_dataset2]
        messages = [{"role": "user", "content": "Test message"}]

        # This should not raise an exception
        with patch.object(completions, "_execute_in_enclave") as mock_execute:
            mock_execute.return_value = ChatCompletion("test response")
            result = completions.create(model=datasets, messages=messages)

            assert isinstance(result, ChatCompletion)
            mock_execute.assert_called_once_with(datasets, messages)

    @patch("syft_nsai.connect")
    @patch("syft_nsai.Client")
    @patch("syft_nsai.Path.mkdir")
    @patch("builtins.open")
    @patch("shutil.rmtree")
    def test_execute_in_enclave_success(
        self, mock_rmtree, mock_open, mock_mkdir, mock_client, mock_connect
    ):
        """Test successful enclave execution"""
        # Setup mocks
        mock_enclave_client = Mock()
        mock_connect.return_value = mock_enclave_client

        mock_client_instance = Mock()
        mock_client_instance.email = "user@example.com"
        mock_client.load.return_value = mock_client_instance

        mock_proj_res = Mock()
        mock_enclave_client.create_project.return_value = mock_proj_res

        # Test
        completions = ChatCompletions()
        mock_dataset = Mock()
        mock_dataset.dataset_obj = Mock()

        datasets = [mock_dataset]
        messages = [{"role": "user", "content": "Test"}]

        result = completions._execute_in_enclave(datasets, messages)

        # Verify
        assert isinstance(result, ChatCompletion)
        mock_connect.assert_called_once()
        mock_enclave_client.create_project.assert_called_once()

    @patch("syft_nsai.connect")
    def test_execute_in_enclave_error(self, mock_connect):
        """Test enclave execution error handling"""
        mock_connect.side_effect = Exception("Connection error")

        completions = ChatCompletions()
        mock_dataset = Mock()
        datasets = [mock_dataset]
        messages = [{"role": "user", "content": "Test"}]

        result = completions._execute_in_enclave(datasets, messages)

        assert isinstance(result, ChatCompletion)
        # Should contain error message
        assert result._choices is not None
        assert "Error executing in enclave" in result._choices[0].message.content

    def test_generate_enclave_code(self):
        """Test enclave code generation"""
        completions = ChatCompletions()

        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Analyze data"},
        ]

        code = completions._generate_enclave_code(messages)

        # Verify code contains expected elements
        assert "import pandas as pd" in code
        assert "from tinfoil import TinfoilAI" in code
        assert "Analyze data" in code
        assert "You are helpful" in code
        assert "chat_completion = client.chat.completions.create" in code

    def test_generate_enclave_code_no_messages(self):
        """Test code generation with no messages"""
        completions = ChatCompletions()

        code = completions._generate_enclave_code([])

        # Should use defaults
        assert "Hello!" in code
        assert "You are a helpful assistant" in code


class TestModuleLevel:
    """Test module-level functionality"""

    def test_client_instance(self):
        """Test global client instance"""
        assert isinstance(nsai.client, NSAIClient)

    def test_imports_available(self):
        """Test that all expected imports are available"""
        # Test that we can import key classes
        from syft_nsai import Dataset, NSAIClient, client, datasets

        assert Dataset is not None
        assert datasets is not None
        assert isinstance(client, NSAIClient)
        assert NSAIClient is not None

    def test_version_available(self):
        """Test that version is available"""
        assert hasattr(nsai, "__version__")
        assert isinstance(nsai.__version__, str)
        assert len(nsai.__version__) > 0


class TestIntegration:
    """Integration tests"""

    @patch("syft_nsai.connect")
    @patch("syft_nsai.Client")
    @patch("syft_nsai.Path.mkdir")
    @patch("builtins.open")
    @patch("shutil.rmtree")
    def test_full_workflow(
        self, mock_rmtree, mock_open, mock_mkdir, mock_client, mock_connect
    ):
        """Test full workflow from client to response"""
        # Setup mocks
        mock_enclave_client = Mock()
        mock_connect.return_value = mock_enclave_client

        mock_client_instance = Mock()
        mock_client_instance.email = "user@example.com"
        mock_client.load.return_value = mock_client_instance

        mock_proj_res = Mock()
        mock_enclave_client.create_project.return_value = mock_proj_res

        # Mock Dataset
        mock_dataset = Mock()
        mock_dataset.name = "test_data"
        mock_dataset.email = "test@example.com"
        mock_dataset.dataset_obj = Mock()

        # Test full workflow
        response = nsai.client.chat.completions.create(
            model=[mock_dataset],
            messages=[{"role": "user", "content": "Test analysis"}],
        )

        # Verify response structure
        assert isinstance(response, ChatCompletion)
        assert response._proj_res == mock_proj_res

        # Verify enclave was called correctly
        mock_connect.assert_called_once_with("enclave-organic-coop@openmined.org")
        mock_enclave_client.create_project.assert_called_once()

        # Check project creation parameters
        call_args = mock_enclave_client.create_project.call_args
        assert "NSAI Chat" in call_args[1]["project_name"]
        assert call_args[1]["datasets"] == [mock_dataset.dataset_obj]
        assert call_args[1]["output_owners"] == ["user@example.com"]
        assert call_args[1]["entrypoint"] == "entrypoint.py"


if __name__ == "__main__":
    pytest.main([__file__])
