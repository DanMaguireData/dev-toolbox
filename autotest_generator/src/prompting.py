"""Functions relating to the loading and parsing of prompts."""

from pathlib import Path

from langchain.prompts import ChatPromptTemplate


def load_prompt_template(
    prompt_name: str, prompts_directory: str = "prompts"
) -> ChatPromptTemplate:
    """Loads a chat prompt template from a markdown file.

    This function follows a convention where the prompt file is expected
    to be located at `{prompts_directory}/{prompt_name}_prompt.md`.

    Args:
        prompt_name: The base name of the prompt (e.g., 'planner').
        prompts_directory: The directory where prompt files are stored.
                           Defaults to 'prompts'.

    Returns:
        A ChatPromptTemplate object ready to be used in a chain.

    Raises:
        FileNotFoundError: If the corresponding prompt file does not exist.
    """
    # Construct the full path to the prompt file
    file_path = Path(prompts_directory) / f"{prompt_name}_prompt.md"

    try:
        # Read the entire content of the file into a string
        template_string = file_path.read_text()
    except FileNotFoundError:
        # Raise a more informative error if the file is not found
        raise FileNotFoundError(f"Prompt file not found at: {file_path}")

    # Create and return the ChatPromptTemplate
    return ChatPromptTemplate.from_messages([("system", template_string)])
