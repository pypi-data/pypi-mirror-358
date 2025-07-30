"""
Basic usage example for syft-nsai

This example demonstrates how to:
1. Discover datasets using syft-datasets
2. Select datasets for analysis
3. Use the OpenAI-compatible API to analyze data in secure enclaves
"""

import os

import syft_datasets as syd
import syft_nsai as nsai

# Optional: Set your own Tinfoil API key
# os.environ["TINFOIL_API_KEY"] = "your_api_key_here"


def main():
    """Basic usage example"""
    print("🔍 Discovering datasets...")

    # Show available datasets (this opens an interactive UI in Jupyter)
    # In a script, you'd typically select datasets programmatically
    datasets = syd.datasets
    print(f"Found {len(datasets)} datasets")

    # Select datasets for analysis
    # Option 1: By index
    if len(datasets) > 0:
        selected_datasets = [datasets[0]]
        print(f"Selected dataset: {selected_datasets[0].name}")

        # Option 2: Search for specific datasets
        crop_datasets = datasets.search("crop")
        if crop_datasets:
            selected_datasets.extend(crop_datasets[:1])  # Add first crop dataset

    if not selected_datasets:
        print("No datasets available for analysis")
        return

    print(f"📊 Analyzing {len(selected_datasets)} datasets...")

    # Create chat completion using the datasets
    response = nsai.client.chat.completions.create(
        model=selected_datasets,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful data analyst. Analyze the provided datasets and provide insights.",
            },
            {
                "role": "user",
                "content": "What are the key patterns and insights in this data? Please provide a summary of the main findings.",
            },
        ],
    )

    print("🤖 AI Analysis Results:")
    print("=" * 50)

    # Access the results (this will block until processing is complete)
    insights = response.choices[0].message.content
    print(insights)

    print("=" * 50)
    print("✅ Analysis complete!")


def advanced_example():
    """Advanced usage with multiple datasets and custom prompts"""
    print("🚀 Advanced example with multiple datasets...")

    datasets = syd.datasets

    # Find datasets by different criteria
    crop_data = datasets.search("crop")
    weather_data = datasets.search("weather")
    economic_data = datasets.search("economic")

    # Combine different types of datasets
    analysis_datasets = []
    if crop_data:
        analysis_datasets.extend(crop_data[:2])
    if weather_data:
        analysis_datasets.extend(weather_data[:1])
    if economic_data:
        analysis_datasets.extend(economic_data[:1])

    if not analysis_datasets:
        print("Not enough datasets for advanced analysis")
        return

    print(f"📈 Cross-analyzing {len(analysis_datasets)} datasets...")

    # More sophisticated analysis
    response = nsai.client.chat.completions.create(
        model=analysis_datasets,
        messages=[
            {
                "role": "system",
                "content": """You are an expert agricultural economist. You will be provided with multiple datasets that may include crop data, weather data, and economic indicators. Analyze the relationships between these datasets.""",
            },
            {
                "role": "user",
                "content": """Please perform a comprehensive analysis of the provided datasets:

1. Summarize what data is available in each dataset
2. Identify potential correlations between different data sources
3. Highlight any interesting patterns or anomalies
4. Provide actionable insights for agricultural planning
5. Suggest areas for further investigation

Please structure your response clearly with headers and bullet points.""",
            },
        ],
    )

    print("🧠 Comprehensive Analysis Results:")
    print("=" * 60)

    analysis = response.choices[0].message.content
    print(analysis)

    print("=" * 60)
    print("✅ Advanced analysis complete!")


if __name__ == "__main__":
    print("🌟 syft-nsai Basic Usage Examples\n")

    try:
        # Run basic example
        main()
        print("\n" + "=" * 60 + "\n")

        # Run advanced example
        advanced_example()

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. SyftBox installed and running")
        print("2. Access to datasets through datasites")
        print("3. Proper enclave permissions")
