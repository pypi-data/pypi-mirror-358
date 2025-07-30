import os
import sys
import yaml
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from tqdm import tqdm
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI


def read_configuration(directory_path: str) -> Dict[str, Any]:
    """
    A1 - Read tool configuration file ".review.conf.yml" in folder specified
    A1.1 - Read `models` section with names of models to use in review
    
    Args:
        directory_path: Path to directory containing .review.conf.yml
        
    Returns:
        Dictionary containing configuration data
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        yaml.YAMLError: If configuration file is invalid YAML
        KeyError: If models section is missing
    """
    config_file_path = Path(directory_path) / ".review.conf.yml"
    
    if not config_file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file_path}")
    
    try:
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in configuration file: {e}")
    
    if not config:
        raise ValueError("Configuration file is empty")
    
    if 'models' not in config:
        raise KeyError("'models' section not found in configuration file")
    
    return config


def get_models_from_config(config: Dict[str, Any]) -> List[str]:
    """
    Extract models list from configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of model names
    """
    models = config['models']
    if not isinstance(models, list):
        raise ValueError("'models' section must be a list")
    
    if not models:
        raise ValueError("'models' section cannot be empty")
    
    return models


def get_summarizer_from_config(config: Dict[str, Any]) -> str:
    """
    Extract summarizer model from configuration with default fallback
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Summarizer model name
    """
    return config.get('summarizer', 'google/gemini-2.5-flash')


def find_markdown_files(directory_path: str) -> List[Path]:
    """
    A2 - Read all markdown files in the directory specified in alphabetical order of file names
    A2.1 - If there are no markdown files - fail with message
    
    Args:
        directory_path: Path to directory containing markdown files
        
    Returns:
        List of Path objects for markdown files in alphabetical order
        
    Raises:
        ValueError: If no markdown files are found
    """
    directory = Path(directory_path)
    
    # Find all .md files in the directory
    markdown_files = list(directory.glob("*.md"))
    
    # A2.1 - If there are no markdown files - fail with message
    if not markdown_files:
        raise ValueError(f"No markdown files found in directory: {directory_path}")
    
    # Sort files alphabetically by filename
    markdown_files.sort(key=lambda x: x.name)
    
    return markdown_files


def merge_markdown_files(markdown_files: List[Path]) -> str:
    """
    A3 - Merge markdown files into one text
    
    Args:
        markdown_files: List of Path objects for markdown files in alphabetical order
        
    Returns:
        String containing merged content of all markdown files
        
    Raises:
        IOError: If any file cannot be read
    """
    merged_content = []
    
    for i, md_file in enumerate(markdown_files):
        # Add filename as a header for each file (except the first one gets a cleaner format)
        if i > 0:
            merged_content.append(f"\n\n---\n\n# File: {md_file.name}\n")
        else:
            merged_content.append(f"# File: {md_file.name}\n")
        
        # Read and add file content
        try:
            with open(md_file, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if content:  # Only add content if file is not empty
                    merged_content.append(content)
        except IOError as e:
            raise IOError(f"Failed to read file {md_file}: {e}")
    
    return "\n".join(merged_content)


def call_model_with_retries(model: str, content: str, api_key: str, max_retries: int = 2) -> Optional[str]:
    """
    A4.3 - Use 2 retries if API call fails
    A4.4 - If some model fails 2 times, print to stderr and ignore the model
    
    Args:
        model: Model name to call
        content: Content to send to the model
        api_key: OpenRouter API key
        max_retries: Maximum number of retries (default 2)
        
    Returns:
        Model response text or None if all retries failed
    """
    # Create OpenAI client configured for OpenRouter
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect and project reviewer. Analyze the provided project specification and provide detailed, constructive feedback and improvement suggestions."
                    },
                    {
                        "role": "user",
                        "content": f"Please review this project specification and provide detailed feedback and improvement suggestions:\n\n{content}"
                    }
                ],
                temperature=0.7,
                max_tokens=8000,
                timeout=60
            )
            
            # Enhanced validation to prevent NoneType iteration errors
            if not response:
                raise ValueError(f"Empty response from {model}")
            
            if not response.choices:
                raise ValueError(f"No choices in response from {model}")
            
            if len(response.choices) == 0:
                raise ValueError(f"Empty choices array in response from {model}")
            
            choice = response.choices[0]
            if not choice or not choice.message:
                raise ValueError(f"Invalid choice structure in response from {model}")
            
            content_text = choice.message.content
            if content_text is None:
                raise ValueError(f"Content is None in response from {model}")
            
            if not isinstance(content_text, str):
                raise ValueError(f"Content is not a string in response from {model}")
            
            if not content_text.strip():
                raise ValueError(f"Content is empty in response from {model}")
            
            return content_text
                
        except Exception as e:
            if attempt == max_retries:
                # A4.4 - If some model fails 2 times, print to stderr and ignore the model
                print(f"Error: Model {model} failed after {max_retries + 1} attempts: {e}", file=sys.stderr)
                return None
            else:
                print(f"Warning: Model {model} attempt {attempt + 1} failed: {e}. Retrying...", file=sys.stderr)
                time.sleep(1)  # Brief delay before retry
    
    return None


def call_models_parallel(models: List[str], content: str, api_key: str) -> List[str]:
    """
    A4 - Send the merged text to multiple LLM models listed in configuration
    A4.2 - Call models in parallel without streaming
    
    Args:
        models: List of model names to call
        content: Content to send to models
        api_key: OpenRouter API key
        
    Returns:
        List of successful model responses
    """
    # Create progress bar for stderr
    progress_bar = tqdm(total=len(models), desc="Calling models", file=sys.stderr, unit="model")
    
    results = []
    
    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=min(len(models), 10)) as executor:
        # Submit all model calls
        future_to_model = {
            executor.submit(call_model_with_retries, model, content, api_key): model 
            for model in models
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_model):
            result = future.result()
            if result is not None:
                results.append(result)
            progress_bar.update(1)
    
    progress_bar.close()
    return results


def aggregate_llm_outputs(outputs: List[str]) -> str:
    """
    A4.5 - Aggregate LLM outputs into one text
    
    Args:
        outputs: List of LLM response texts
        
    Returns:
        Aggregated text combining all outputs
    """
    # Filter out None values and empty strings to prevent iteration errors
    valid_outputs = []
    for output in outputs:
        if output is not None and isinstance(output, str) and output.strip():
            valid_outputs.append(output.strip())
    
    if not valid_outputs:
        return "No successful model responses received."
    
    aggregated = []
    aggregated.append("# Project Review Results")
    aggregated.append(f"\nBased on analysis from {len(valid_outputs)} model(s):\n")
    
    for i, output in enumerate(valid_outputs, 1):
        aggregated.append(f"## Review {i}\n")
        aggregated.append(output)
        aggregated.append("\n---\n")
    
    return "\n".join(aggregated)


def summarize_aggregated_review(aggregated_text: str, summarizer_model: str, api_key: str) -> str:
    """
    A5 - Use another LLM model to summarize recommendations
    
    Args:
        aggregated_text: The aggregated review text from multiple models
        summarizer_model: Model name to use for summarization
        api_key: OpenRouter API key
        
    Returns:
        Summarized review text
        
    Raises:
        Exception: If summarization fails after retries
    """
    # Create OpenAI client configured for OpenRouter
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Create progress bar for summarization
    progress_bar = tqdm(total=1, desc="Summarizing", file=sys.stderr, unit="step")
    
    for attempt in range(3):  # Use 2 retries for summarizer
        try:
            response = client.chat.completions.create(
                model=summarizer_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical writer and project analyst. Your task is to synthesize multiple project reviews into a clear, concise, and actionable summary. Focus on the most important recommendations and present them in a well-structured format."
                    },
                    {
                        "role": "user",
                        "content": f"Please synthesize the following project reviews into a clear, concise summary with actionable recommendations. Organize the feedback by themes and prioritize the most important suggestions:\n\n{aggregated_text}"
                    }
                ],
                temperature=0.3,
                max_tokens=50000,
                timeout=60
            )
            
            # Enhanced validation to prevent NoneType iteration errors
            if not response:
                raise ValueError(f"Empty response from summarizer {summarizer_model}")
            
            if not response.choices:
                raise ValueError(f"No choices in response from summarizer {summarizer_model}")
            
            if len(response.choices) == 0:
                raise ValueError(f"Empty choices array in response from summarizer {summarizer_model}")
            
            choice = response.choices[0]
            if not choice or not choice.message:
                raise ValueError(f"Invalid choice structure in response from summarizer {summarizer_model}")
            
            content_text = choice.message.content
            if content_text is None:
                raise ValueError(f"Content is None in response from summarizer {summarizer_model}")
            
            if not isinstance(content_text, str):
                raise ValueError(f"Content is not a string in response from summarizer {summarizer_model}")
            
            if not content_text.strip():
                raise ValueError(f"Content is empty in response from summarizer {summarizer_model}")
            
            progress_bar.update(1)
            progress_bar.close()
            return content_text
                
        except Exception as e:
            if attempt == 2:  # Last attempt
                progress_bar.close()
                print(f"Warning: Summarizer {summarizer_model} failed after 3 attempts: {e}. Falling back to aggregated review.", file=sys.stderr)
                return aggregated_text  # Fallback to original aggregated text
            else:
                print(f"Warning: Summarizer {summarizer_model} attempt {attempt + 1} failed: {e}. Retrying...", file=sys.stderr)
                time.sleep(1)
    
    progress_bar.close()
    return aggregated_text  # Fallback if all attempts fail


def send_to_models(models: List[str], content: str) -> str:
    """
    A4.1 - Use Openrouter API Key from environment
    
    Args:
        models: List of model names
        content: Content to send to models
        
    Returns:
        Aggregated model outputs
        
    Raises:
        ValueError: If OPENROUTER_API_KEY environment variable is not set
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    # A4.2 - Call models in parallel without streaming
    outputs = call_models_parallel(models, content, api_key)
    
    # A4.5 - Aggregate LLM outputs into one text
    return aggregate_llm_outputs(outputs)


def main():
    """
    Main function to handle the complete workflow
    """
    if len(sys.argv) != 2:
        print("Usage: bootkicker <directory_path>", file=sys.stderr)
        sys.exit(1)
    
    directory_path = sys.argv[1]
    
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found: {directory_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # A1 - Read tool configuration file
        config = read_configuration(directory_path)
        
        # A1.1 - Read models section
        models = get_models_from_config(config)
        
        # Get summarizer model from config
        summarizer_model = get_summarizer_from_config(config)
        
        # A2 - Read all markdown files in the directory specified in alphabetical order
        markdown_files = find_markdown_files(directory_path)
        
        # A3 - Merge markdown files into one text
        merged_content = merge_markdown_files(markdown_files)
        
        # A4 - Send the merged text to multiple LLM models listed in configuration
        aggregated_review = send_to_models(models, merged_content)
        
        # A5 - Use another LLM model to summarize recommendations
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        summarized_review = summarize_aggregated_review(aggregated_review, summarizer_model, api_key)
        
        # Output summarizer result to stdout
        print(summarized_review)
        
    except (FileNotFoundError, yaml.YAMLError, KeyError, ValueError, IOError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
