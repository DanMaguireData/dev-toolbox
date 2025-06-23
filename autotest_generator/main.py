"""Main entry point to execute out graph on a target code/fucntion."""

import logging
import sys

from dotenv import load_dotenv
from src.file_io import save_test_file
from src.graph_builder import build_workflow_graph

# Setup Logger
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more verbose output
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def main():
    """Function executes the flow of the LangGraph graph."""

    logging.info("Building Graph")
    # Build the workflow graph
    graph = build_workflow_graph(save_image_path="graph.png")
    # Define the initial input for the workflow
    initial_input = {
        "file_path": "example_code/code.py",
        "function_name": "add",
    }
    # Invoke the workflow graph
    out = graph.invoke(initial_input)
    # Save the generated test file
    save_test_file(
        generated_code=out["generated_test_code"],
        source_file_path=initial_input["file_path"],
        function_name=initial_input["function_name"],
        base_test_dir="tests",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Unexpected error occured: {e}", exc_info=True)
        sys.exit(1)
