"""Defines the nodes for a graph-based Python unit test generation pipeline."""

import json
import logging
import os
from typing import List, Optional, TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .file_io import FunctionDetails, get_function_details
from .prompting import load_prompt_template
from .schemas import TestCase, TestSuite

# Logger
logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """Represents the state of the graph-based code analysis and test
    generation process.

    This structure encapsulates all relevant information for a specific node
    or stage within a directed acyclic graph (DAG) that guides the development
    of unit tests for a given Python function.

    Attributes:
        file_path (str):
            The absolute or relative path to the Python file
            containing the target function. This is a primary
            identifier for the source code context.
        function_name (str):
            The name of the specific function within the
            `file_path` that is the subject of analysis and
            test generation.
        function_code (Optional[str]):
            The complete, raw source code of the
            `function_name` extracted from the
            `file_path`. This is often a prerequisite
            for detailed analysis. `None` if not yet retrieved.
        analysis (Optional[FunctionDetails]):
            A structured dictionary containing
            the results of static code analysis
            for the function. This might include
            its signature, parameter types,
            return type hints, docstring parsing,
            and potentially AST-based insights.
            `None` if analysis has not been performed.
        test_plan (Optional[TestSuite]):
            A high-level, structured plan for testing
            the function. This might outline the
            types of tests, edge cases, and overall
            strategy. It's usually derived from the
            `analysis`. `None` if no test plan exists.
        test_cases_to_generate (List[TestCase]):
            A list of individual test case
            definitions. Each `TestCase` object
            specifies inputs, expected outputs,
            and possibly test case names or
            descriptions. This is the detailed
            blueprint for generating code.
        generated_test_code (Optional[str]):
            The raw Python code string representing
            the unit tests generated based on the
            `test_cases_to_generate`. This is the
            actual output that can be saved or executed.
            `None` if tests have not yet been generated.
        refinement_notes (Optional[str]):
            Feedback or suggestions provided by a
            review agent (e.g., another AI model or
            human reviewer) for improving the generated
            test code, test plan, or analysis. Used to
            guide iterative refinement. `None` if no
            refinement notes are available.
        iteration_count (int):
            A counter to track the number of refinement iterations
            performed on this `GraphState`. Essential for preventing
            infinite loops in iterative processes by setting a
            maximum iteration limit.
        accumulated_test_code (str):
            A string accumulating all generated test code
            across multiple iterations. This ensures that
            progress is not lost and can be used to build
            a comprehensive test suite. Defaults to an
            empty string.
        current_test_case_json (str):
            A JSON string representation of the *current*
            test case being processed or generated. This
            can be useful for intermediate state saving,
            debugging, or passing granular information
            between steps in a complex pipeline.
    """

    file_path: str
    function_name: str
    function_code: Optional[str]
    analysis: FunctionDetails
    test_plan: TestSuite
    test_cases_to_generate: List[TestCase]
    generated_test_code: Optional[str]
    refinement_notes: Optional[str]
    iteration_count: int
    accumulated_test_code: str
    current_test_case_json: str


MODEL: str = "gpt-4.1-mini"


def analyze_function(state: GraphState) -> GraphState:
    """Performs static analysis on the function specified in the GraphState.

    This function retrieves the source code, docstring, and signature of the
    target function. It then updates the `state` with this information and
    increments the `iteration_count`.

    Args:
        state (GraphState):
            The current state of the graph analysis, containing
            `file_path` and `function_name`.

    Returns:
        GraphState:
            The updated state with `function_code`, `analysis` populated,
            and `iteration_count` incremented.
    """
    logger.info("--- Executing Node: analyze_function ---")
    logger.debug(
        f"Analyzing function '{state['function_name']}'"
        f" from file '{state['file_path']}'"
    )
    function_analysis_details = get_function_details(
        file_path=state["file_path"], function_name=state["function_name"]
    )

    if (
        function_analysis_details.get("code") is None
        or function_analysis_details.get("signature") is None
    ):
        logger.error(
            f"Function '{state['function_name']}' not found in file "
            f"'{state['file_path']}'."
        )
        raise ValueError(
            f"Function '{state['function_name']}' not found in file "
        )

    updated_state = state.copy()

    code_str = function_analysis_details.get("code")
    signature_str = function_analysis_details.get("signature")

    if code_str is None or signature_str is None:
        logger.error(
            f"Function '{state['function_name']}' not found in file "
            f"'{state['file_path']}'."
        )
        raise ValueError(
            f"Function '{state['function_name']}' not found in file "
        )
    updated_state["function_code"] = code_str

    updated_state["analysis"] = {
        "docstring": function_analysis_details.get("docstring"),
        "signature": signature_str,
        "code": code_str,
    }
    updated_state["iteration_count"] = 0
    logger.info(
        f"Successfully analyzed function '{state['function_name']}'."
        " Code and analysis updated."
    )
    logger.debug(
        f"Analysis results for '{state['function_name']}':"
        f" {updated_state['analysis']}"
    )
    return updated_state


def plan_tests(state: GraphState) -> GraphState:
    """Generates a high-level test plan based on the function's analysis.

    This function utilizes a language model to create a structured test plan,
    including happy path cases, edge cases, and error conditions. It parses
    the analysis details from the `GraphState` and then processes the
    language model's output to ensure test case inputs are properly formatted.

    Args:
        state (GraphState): The current state of the graph analysis, containing
                            `function_code` and `analysis` details.

    Returns:
        GraphState: The updated state with the `test_plan` populated.

    Raises:
        Exception: For any errors encountered during language model interaction
                   or test plan parsing.
    """
    logger.info("--- Executing Node: plan_tests ---")

    try:
        llm = ChatOpenAI(MODEL, temperature=0)
        prompt = load_prompt_template(prompt_name="test_planner")
        planner_chain = prompt | llm.with_structured_output(TestSuite)

        # Prepare analysis data, ensuring it's in a string
        # format if needed by the prompt.
        analysis_json = json.dumps(
            {
                "docstring": state["analysis"].get(
                    "docstring", "No docstring provided."
                ),
                "signature": state["analysis"].get(
                    "signature", "Unknown signature."
                ),
            },
            indent=2,
        )

        logger.debug(
            f"Invoking test planner with analysis: {analysis_json[:200]}..."
        )

        # Invoke the chain with the necessary data from the state
        test_plan: TestSuite = planner_chain.invoke(
            {
                "function_code": state["function_code"],
                "analysis": analysis_json,
            }
        )

        # Post-process the results to parse the
        # 'inputs' string for each test case
        for test_case_list in [
            test_plan.happy_path_cases,
            test_plan.edge_cases,
            test_plan.error_conditions,
        ]:
            if not test_case_list:
                continue
            for test_case in test_case_list:
                try:
                    # Safely parse JSON inputs if needed
                    if isinstance(test_case.inputs, str):
                        test_case.inputs = json.loads(test_case.inputs)
                    elif not isinstance(test_case.inputs, dict):
                        logger.warning(
                            f"Test case input for '{test_case.name}' "
                            "is neither a string nor a dict, "
                            "attempting to interpret as raw. Input: "
                            f"{test_case.inputs}"
                        )
                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to decode JSON for test case "
                        f"'{test_case.name}'"
                        f" input: '{test_case.inputs}'. Error: {e}"
                    )
                    test_case.inputs = None
                except Exception as e:
                    logger.error(
                        "An unexpected error occurred during JSON parsing for"
                        f" test case '{test_case.name}': {e}",
                        exc_info=True,
                    )
                    test_case.inputs = None
        logger.info(
            "Successfully generated test plan with"
            f"{len(test_plan.happy_path_cases)}"
            f" happy path, {len(test_plan.edge_cases)} edge,"
            f" and {len(test_plan.error_conditions)} error test cases."
        )

        # Return a new state dictionary to ensure
        # immutability of the input state
        updated_state: GraphState = state.copy()
        updated_state["test_plan"] = test_plan
        updated_state["iteration_count"] = state.get("iteration_count", 0) + 1
        logger.debug(
            "Iteration count for test planning node is now "
            f"{updated_state['iteration_count']}."
        )

    except Exception as e:
        logger.error(
            f"An unexpected error occurred during test planning: {e}",
            exc_info=True,
        )
        # Re-raise as a Runtime Error or a more specific exception if known.
        raise RuntimeError("Failed to generate test plan.") from e

    return updated_state


def prepare_iteration(state: GraphState) -> GraphState:
    """Prepares for the next iteration of test generation by flattening test
    cases and initializing the accumulated test code with necessary imports.

    This function takes the structured test plan from the `GraphState`,
    combines all defined test cases (happy path, edge, error) into a
    single list, and creates an initial Python code string that includes
    necessary imports for the target function and the testing framework
    (pytest).

    Args:
        state (GraphState):
            The current state of the graph analysis,
            containing the `test_plan`, `file_path`,
            and `function_name`.

    Returns:
        GraphState:
            An updated state dictionary containing:
            - `test_cases_to_generate`: A flattened list of all test cases.
            - `accumulated_test_code`: The initial code string with imports.
            - `iteration_count`: Incremented by 1.

    Raises:
        AttributeError:
            If expected attributes like `happy_path_cases` are missing
            from the `TestSuite` object.
    """
    logger.info("--- Executing Node: prepare_iteration ---")

    test_suite: TestSuite = state["test_plan"]

    # Flatten all test cases into a single list for processing.
    # Safely access lists, providing empty lists if they are None or missing.
    happy_cases = getattr(test_suite, "happy_path_cases", []) or []
    edge_cases = getattr(test_suite, "edge_cases", []) or []
    error_cases = getattr(test_suite, "error_conditions", []) or []

    all_test_cases: List[TestCase] = happy_cases + edge_cases + error_cases

    if not all_test_cases:
        logger.warning(
            "No test cases found in the test plan."
            " Proceeding with empty test case list."
        )
    logger.debug(
        f"Flattened {len(happy_cases)} happy path, "
        f"{len(edge_cases)} edge, and {len(error_cases)}"
        " error test cases."
    )
    # Prepare the initial code block with necessary imports
    module_path = (
        state["file_path"].replace(os.path.sep, ".").replace(".py", "")
    )
    function_name = state["function_name"]
    initial_code = (
        f"import pytest\nfrom {module_path} import {function_name}\n\n"
    )

    logger.info(
        "Initialized test code with imports for "
        f"'{function_name}' from module '{module_path}'."
    )

    # Create a new state dictionary to maintain
    # immutability of the input state.
    updated_state: GraphState = state.copy()
    updated_state["test_cases_to_generate"] = all_test_cases
    updated_state["accumulated_test_code"] = initial_code
    logger.debug(
        "Iteration count for prepare_iteration node is now "
        f"{updated_state['iteration_count']}."
    )

    return updated_state


def generate_single_test(state: GraphState) -> GraphState:
    """Generates the code for a single test case from the queue.

    This function takes the first `TestCase` from the `test_cases_to_generate`
    list, uses a language model to generate the corresponding Python test code,
    and appends this new code to the `accumulated_test_code`. The state is
    updated to reflect the shortened queue and the new accumulated code.

    Args:
        state (GraphState):
            The current state of the graph, which must contain:
            - `test_cases_to_generate`: A non-empty list of TestCase objects.
            - `function_name`: The name of the function under test.
            - `analysis`: The analysis dictionary for the function.
            - `accumulated_test_code`:
                The string of already generated test code.

    Returns:
        GraphState:
            An updated state dictionary with:
            - `test_cases_to_generate`:
                The queue with the processed test case removed.
            - `accumulated_test_code`:
                The code string with the new test appended.
            - `current_test_case_json`:
                The JSON representation of the processed test case.
            - `iteration_count`: Incremented by 1.

    Raises:
        RuntimeError: If an error occurs during the language model invocation.
    """
    logger.info("--- Executing Node: generate_single_test ---")
    try:
        # Create a mutable copy of the state to
        # avoid side effects on the input object.
        updated_state = state.copy()

        # Pop the next test case to work on from the copied state's queue.
        current_case = updated_state["test_cases_to_generate"].pop(0)
        current_case_json = current_case.model_dump_json(indent=2)

        # Use getattr for safer access to the description/name field.
        test_case_name = getattr(
            current_case,
            "description",
            getattr(current_case, "name", "Unnamed Test Case"),
        )
        logger.info(f"Generating test for: '{test_case_name}'")
        logger.debug(f"Test case details (JSON):\n{current_case_json}")

        # Initialize LLM and construct the generation chain.
        llm = ChatOpenAI(model=MODEL, temperature=0)
        coder_chain = (
            load_prompt_template("test_writer") | llm | StrOutputParser()
        )

        # Generate just the code for this one test.
        logger.debug(
            "Invoking coder chain with function details and test case..."
        )
        single_test_code = coder_chain.invoke(
            {
                "function_name": updated_state["function_name"],
                "test_case_json": current_case_json,
                "analysis": json.dumps(
                    updated_state["analysis"]
                ),  # Ensure analysis is a string for the prompt
            }
        )
        logger.info("Successfully generated code for a single test case.")

        # Append the new test function to our accumulated code.
        updated_state[
            "accumulated_test_code"
        ] += f"\n\n{single_test_code.strip()}"
        updated_state["current_test_case_json"] = current_case_json

    except Exception as e:
        logger.error(
            f"An unexpected error occurred during single test generation: {e}",
            exc_info=True,
        )
        # Re-raise as a generic runtime error to
        # signal failure to the graph runner.
        raise RuntimeError(
            "Failed to generate test code due to an LLM or processing error."
        ) from e

    return updated_state


def finalize_file(state: GraphState) -> GraphState:
    """Finalizes the test code generation process by moving the accumulated
    test code to the `generated_test_code` field in the state.

    This node signifies the end of the test generation loop. It takes the
    complete test code that has been built up (`accumulated_test_code`)
    and places it into the `generated_test_code` field, which is typically
    the final output of the test generation pipeline.

    Args:
        state (GraphState):
            The current state of the graph, containing the
            `accumulated_test_code`.

    Returns:
        GraphState:
            An updated state dictionary with `generated_test_code` populated.

     Raises:
        ValueError: If `accumulated_test_code` is missing from the state.
    """
    # Validate that the accumulated code exists
    accumulated_code = state.get("accumulated_test_code")
    if accumulated_code is None:
        logger.error(
            "Cannot finalize file: 'accumulated_test_code'"
            " is missing from the state."
        )
        raise ValueError(
            "Missing 'accumulated_test_code' in GraphState for finalization."
        )

    # All tests have been generated, so we move the accumulated code to the
    # final output field.
    # Return a new state dictionary to maintain immutability.
    updated_state: GraphState = state.copy()
    updated_state["generated_test_code"] = accumulated_code
    logger.info("Test code finalized and moved to 'generated_test_code'.")
    return updated_state


def should_continue_generating(state: GraphState) -> str:
    """Decides whether to continue the test generation loop or proceed to
    finalization.

    This function checks if there are any remaining test cases to be generated
    as specified in the `GraphState`. If there are test cases left, it signals
    to continue the generation process. Otherwise, it indicates that the
    process is complete and finalization should occur.

    Args:
        state (GraphState): The current state of the graph analysis, containing
                            the list of `test_cases_to_generate`.

    Returns:
        str: A decision string. Returns "continue_generation" if more tests
             are pending, or "finalize" if all tests have been processed.
    """
    test_cases_list = state.get("test_cases_to_generate")

    if test_cases_list is None:
        logger.error("No test cases to generate.")
        return "finalize"

    if len(test_cases_list) > 0:
        logger.info(
            f"Remaining test cases: {len(test_cases_list)}. "
            "Continuing generation loop."
        )
        return "continue_generation"
    logger.info("No remaining test cases. Proceeding to finalization.")
    return "finalize"
