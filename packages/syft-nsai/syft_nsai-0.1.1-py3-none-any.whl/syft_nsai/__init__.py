"""
OpenAI-compatible chat completions API using SyftBox datasets

Example usage:
    import syft_datasets as syd
    import syft_nsai as nsai

    # Select datasets using the interactive UI
    syd.datasets

    # Use selected datasets with chat API
    selected_datasets = [syd.datasets[i] for i in [0, 1, 5]]
    response = nsai.client.chat.completions.create(
        model=selected_datasets,
        messages=[{"role": "user", "content": "Analyze this data"}]
    )
"""

__version__ = "0.1.1"

import os
from pathlib import Path
from uuid import uuid4

from syft_core import Client
from syft_datasets import Dataset, datasets
from syft_rds import init_session
from syftbox_enclave.client import connect
import syft_wallet


def _get_tinfoil_api_key() -> str:
    """
    Get the Tinfoil API key using syft-wallet with approval.
    If not found, prompt the user to provide it and save it.
    """
    wallet = syft_wallet.SyftWallet()
    
    # Try to get the API key from syft-wallet with approval
    try:
        api_key = wallet.get(
            name="tinfoil_api_key",
            app_name="syft-nsai", 
            reason="Access Tinfoil AI API for running language models in secure enclaves"
        )
        if api_key:
            return api_key
    except Exception:
        pass  # Key not found, we'll prompt for it
    
    # Check environment variable as fallback
    env_key = os.environ.get("TINFOIL_API_KEY")
    if env_key:
        print("Found Tinfoil API key in environment variable.")
        # Ask if they want to save it to syft-wallet for future use
        try:
            save_choice = input("Would you like to save this key to syft-wallet for future use? (y/n): ").lower().strip()
            if save_choice in ['y', 'yes']:
                wallet.store("tinfoil_api_key", env_key, 
                           description="Tinfoil AI API key for NSAI")
                print("✓ API key saved to syft-wallet")
        except (KeyboardInterrupt, EOFError):
            pass  # User cancelled, just use the environment key
        return env_key
    
    # Neither wallet nor environment has the key, prompt user
    print("\n🔑 Tinfoil API Key Required")
    print("=" * 40)
    print("NSAI needs a Tinfoil API key to run AI models in secure enclaves.")
    print("You can get a free API key at: https://tinfoil.sh/")
    print("")
    
    try:
        # Prompt for the API key
        api_key = input("Please enter your Tinfoil API key: ").strip()
        
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        if not api_key.startswith("tk_"):
            print("⚠️  Warning: Tinfoil API keys typically start with 'tk_'")
            confirm = input("Continue with this key? (y/n): ").lower().strip()
            if confirm not in ['y', 'yes']:
                raise ValueError("API key entry cancelled")
        
        # Save the key to syft-wallet
        success = wallet.store(
            "tinfoil_api_key", 
            api_key,
            description="Tinfoil AI API key for NSAI"
        )
        
        if success:
            print("✓ API key saved securely to syft-wallet")
            print("You won't need to enter it again on this machine.")
        else:
            print("⚠️  Warning: Could not save API key to syft-wallet")
            print("You may need to enter it again next time.")
        
        return api_key
        
    except (KeyboardInterrupt, EOFError):
        print("\n❌ API key setup cancelled")
        raise ValueError("Tinfoil API key is required to use NSAI")
    except Exception as e:
        print(f"❌ Error setting up API key: {e}")
        raise ValueError("Failed to set up Tinfoil API key")


class ChatCompletion:
    """Represents a chat completion response"""

    def __init__(self, content_or_proj_res):
        if isinstance(content_or_proj_res, str):
            # Direct content
            self._choices = [Choice(content_or_proj_res)]
            self._proj_res = None
        else:
            # Project result for lazy loading
            self._choices = None
            self._proj_res = content_or_proj_res

    @property
    def choices(self):
        """Lazy loading of choices - blocks until enclave execution completes"""
        if self._choices is not None:
            return self._choices

        if self._proj_res is None:
            return [Choice("No content available")]

        print("Waiting for enclave execution to complete...")

        import time

        try:
            # This will block until the project completes
            result_path = self._proj_res.output(block=True)

            print(
                f"Project completed. Waiting for output file: {result_path.absolute()}"
            )

            # Now wait for the output file (up to 2 minutes after project completion)
            output_file = result_path.absolute() / "output.txt"

            max_retries = 240  # 240 retries * 0.5 seconds = 2 minutes max
            retry_count = 0

            print(f"Project completed. Waiting for output file: {output_file}")

            while retry_count < max_retries:
                if output_file.exists():
                    try:
                        with open(output_file) as f:
                            content = f.read()
                        if content.strip():  # Make sure we have actual content
                            self._choices = [Choice(content)]  # Cache the result
                            return self._choices
                    except Exception:
                        pass  # File might be in the process of being written

                if retry_count % 20 == 0:  # Print status every 10 seconds
                    print(
                        f"Still waiting for file... ({retry_count * 0.5:.0f}s elapsed)"
                    )

                time.sleep(0.5)  # Wait 0.5 seconds before retrying
                retry_count += 1

            # If we still don't have the file, return error
            error_msg = f"Output file not found at {output_file} after waiting 2 minutes post-completion"
            self._choices = [Choice(error_msg)]
            return self._choices

        except Exception as e:
            error_msg = f"Error waiting for project completion: {str(e)}"
            self._choices = [Choice(error_msg)]
            return self._choices


class Choice:
    """Represents a choice in chat completion"""

    def __init__(self, content):
        self.message = Message(content)


class Message:
    """Represents a message in chat completion"""

    def __init__(self, content):
        self.content = content


class Chat:
    """Chat interface that matches OpenAI's structure"""

    def __init__(self):
        self.completions = ChatCompletions()


class NSAIClient:
    """NSAI Client that handles chat completions using datasets through Tinfoil API"""

    def __init__(self):
        self.chat = Chat()


class ChatCompletions:
    """Handles chat completion operations"""

    def create(
        self, model: list[Dataset], messages: list[dict[str, str]], **kwargs
    ) -> ChatCompletion:
        """
        Create a chat completion using the provided datasets as models

        Args:
            model: List of Dataset objects to use as data sources
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters (including optional tinfoil_api_key)

        Returns:
            ChatCompletion object with the response
        """
        return self._execute_in_enclave(model, messages, **kwargs)

    def _execute_in_enclave(
        self, datasets: list[Dataset], messages: list[dict[str, str]], **kwargs
    ) -> ChatCompletion:
        """Execute the chat completion within an enclave using the Tinfoil API"""

        # Generate unique identifiers
        random_id = str(uuid4())[0:8]
        project_name = f"NSAI Chat - {random_id}"

        # Create the code for the enclave
        code_content = self._generate_enclave_code(messages, **kwargs)

        # Create temporary code directory
        code_path = Path(".") / "temp_nsai_code"
        code_path.mkdir(exist_ok=True)

        code_file = code_path / "entrypoint.py"
        with open(code_file, "w") as f:
            f.write(code_content)

        try:
            # Get enclave client
            enclave = (
                "enclave-organic-coop@openmined.org"  # Default enclave from notebook
            )
            enclave_client = connect(enclave)

            # Get current user as output owner
            current_user = Client.load().email

            # Convert Dataset objects to the format expected by enclave
            dataset_objects = []
            for dataset in datasets:
                if dataset.dataset_obj:
                    dataset_objects.append(dataset.dataset_obj)
                else:
                    # If we don't have the dataset object, try to get it
                    try:
                        datasite_client = init_session(host=dataset.email)
                        dataset_obj = datasite_client.dataset.get(name=dataset.name)
                        dataset_objects.append(dataset_obj)
                    except Exception:
                        print(
                            f"Warning: Could not access dataset {dataset.name} from {dataset.email}"
                        )

            # Create project in enclave
            proj_res = enclave_client.create_project(
                project_name=project_name,
                datasets=dataset_objects,
                output_owners=[current_user],
                code_path=str(code_path),
                entrypoint="entrypoint.py",
            )

            # Return immediately with the project result - content will be loaded lazily
            return ChatCompletion(proj_res)

        except Exception as e:
            return ChatCompletion(f"Error executing in enclave: {str(e)}")

        finally:
            # Clean up temporary files
            import shutil

            if code_path.exists():
                shutil.rmtree(code_path)

    def _generate_enclave_code(self, messages: list[dict[str, str]], **kwargs) -> str:
        """Generate the Python code to run in the enclave"""

        # Extract the user message for the LLM
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        system_messages = [msg for msg in messages if msg.get("role") == "system"]

        user_content = user_messages[0]["content"] if user_messages else "Hello!"
        system_content = (
            system_messages[0]["content"]
            if system_messages
            else "You are a helpful assistant."
        )
        
        # Get the Tinfoil API key using syft-wallet
        try:
            tinfoil_api_key = _get_tinfoil_api_key()
        except Exception as e:
            raise RuntimeError(f"Failed to get Tinfoil API key: {e}")

        code = f'''
import os
from pathlib import Path
from sys import exit
import pandas as pd
import json

# Install tinfoil
v = os.popen('uv pip install tinfoil').read()

from tinfoil import TinfoilAI

DATA_DIR = os.environ.get("DATA_DIR", "")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "")

# Load and analyze datasets
dataset_paths = [Path(dataset_path) for dataset_path in DATA_DIR.split(",")]
dataset_summaries = []
all_data_context = ""

for dataset_path in dataset_paths:
    if not dataset_path.exists():
        print(f"Warning: Dataset path does not exist: {{dataset_path}}")
        continue
    
    try:
        # Try to find CSV files in the dataset directory
        csv_files = list(dataset_path.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in {{dataset_path}}")
            continue
            
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                
                # Create a summary of this dataset
                summary = {{
                    "dataset_path": str(dataset_path),
                    "file_name": csv_file.name,
                    "rows": len(df),
                    "columns": list(df.columns),
                    "head": df.head().to_dict('records') if len(df) > 0 else [],
                    "dtypes": df.dtypes.to_dict()
                }}
                
                # Add statistical summary for numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    summary["numeric_summary"] = df[numeric_cols].describe().to_dict()
                
                dataset_summaries.append(summary)
                
                # Add to context string
                all_data_context += f"\\n\\nDataset: {{csv_file.name}} ({{len(df)}} rows)\\n"
                all_data_context += f"Columns: {{', '.join(df.columns)}}\\n"
                if len(df) > 0:
                    all_data_context += f"Sample data:\\n{{df.head().to_string()}}\\n"
                
            except Exception as e:
                print(f"Error reading {{csv_file}}: {{e}}")
                continue
                
    except Exception as e:
        print(f"Error processing dataset {{dataset_path}}: {{e}}")
        continue

# Initialize Tinfoil client
# API key retrieved from syft-wallet
tinfoil_api_key = "{tinfoil_api_key}"

client = TinfoilAI(
    enclave="deepseek-r1-70b-p.model.tinfoil.sh",
    repo="tinfoilsh/confidential-deepseek-r1-70b-prod",
    api_key=tinfoil_api_key,
)

# Enhance the user prompt with dataset context
enhanced_user_content = f"""{{
DATA CONTEXT:
The following datasets are available for analysis:
{{all_data_context}}

USER QUESTION:
{user_content}

Please analyze the data and answer the question based on the available datasets.
}}"""

# Prepare messages for the chat completion
messages = [
    {{"role": "system", "content": """{system_content}"""}},
    {{"role": "user", "content": enhanced_user_content}}
]

# Create chat completion
try:
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="deepseek-r1-70b",
    )
    
    result_content = chat_completion.choices[0].message.content
    
    # Write output with dataset summary
    with open(os.path.join(OUTPUT_DIR, "output.txt"), "w") as f:
        f.write("=== DATASET ANALYSIS ===\\n")
        f.write(f"Processed {{len(dataset_summaries)}} datasets\\n\\n")
        f.write("=== AI RESPONSE ===\\n")
        f.write(result_content)
        
except Exception as e:
    # Write error to output
    with open(os.path.join(OUTPUT_DIR, "output.txt"), "w") as f:
        f.write(f"Error: {{str(e)}}")
'''

        return code


def set_tinfoil_api_key(api_key: str = None) -> None:
    """
    Set or update the Tinfoil API key in syft-wallet.
    
    Args:
        api_key: The API key to save. If None, will prompt user for input.
    """
    wallet = syft_wallet.SyftWallet()
    
    if api_key is None:
        print("🔑 Set Tinfoil API Key")
        print("=" * 25)
        print("Enter your Tinfoil API key (get one at https://tinfoil.sh/)")
        try:
            api_key = input("API key: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n❌ Cancelled")
            return
    
    if not api_key:
        print("❌ API key cannot be empty")
        return
    
    if not api_key.startswith("tk_"):
        print("⚠️  Warning: Tinfoil API keys typically start with 'tk_'")
    
    success = wallet.store(
        "tinfoil_api_key",
        api_key,
        description="Tinfoil AI API key for NSAI"
    )
    
    if success:
        print("✓ Tinfoil API key saved successfully to syft-wallet")
    else:
        print("❌ Failed to save API key to syft-wallet")


def get_tinfoil_api_key() -> str:
    """
    Get the current Tinfoil API key from syft-wallet with user approval.
    
    Returns:
        The API key if found and approved, raises ValueError if not found or denied.
    """
    wallet = syft_wallet.SyftWallet()
    
    try:
        api_key = wallet.get(
            name="tinfoil_api_key",
            app_name="syft-nsai",
            reason="Direct access to Tinfoil API key for manual inspection or usage"
        )
        if api_key:
            return api_key
        else:
            raise ValueError("Tinfoil API key not found in syft-wallet or access denied")
    except Exception as e:
        raise ValueError(f"Failed to retrieve Tinfoil API key: {e}")


def show_tinfoil_status() -> None:
    """Show the current status of the Tinfoil API key."""
    wallet = syft_wallet.SyftWallet()
    
    # Check if key exists without requesting access (just check metadata)
    try:
        keys = wallet.list_keys(jupyter=False)
        tinfoil_keys = [k for k in keys if k.get('name') == 'tinfoil_api_key']
        if tinfoil_keys:
            print("✓ Tinfoil API key found in syft-wallet")
            print("  (Access requires user approval when requested)")
        else:
            print("❌ No Tinfoil API key found in syft-wallet")
            print("Run nsai.set_tinfoil_api_key() to set one")
    except Exception:
        print("❌ Unable to check Tinfoil API key status")
        print("Run nsai.set_tinfoil_api_key() to set one")


# Global instances
client = NSAIClient()

# Make client available as both `client` and for direct import
__all__ = [
    "datasets", 
    "client", 
    "Dataset", 
    "NSAIClient",
    "set_tinfoil_api_key",
    "get_tinfoil_api_key", 
    "show_tinfoil_status"
]
