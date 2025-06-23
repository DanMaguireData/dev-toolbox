"""Contains schemas used throughout code and as part of prompting."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

Primitive = Union[str, int, float, bool, None]


# Define the two possible outcomes for a test case
class ExpectedReturnValue(BaseModel):
    """Represents a test case that should succeed and return a specific
    value."""

    returns: Union[
        Primitive,  # Handles str, int, float, bool, None
        List[Primitive],  # Handles lists of primitives
        Dict[str, Primitive],  # Handles dictionaries with primitive values
    ] = Field(
        ..., description="The exact value the function is expected to return."
    )


class ExpectedError(BaseModel):
    """Represents a test case that should fail by raising a specific
    exception."""

    raises: str = Field(
        ...,
        description=(
            "The name of the exception class that should"
            " be raised (e.g., 'TypeError', 'ValueError')."
        ),
    )


# Define the structure of a single test case
class TestCaseBase(BaseModel):
    """A single, self-contained test case."""

    description: str = Field(
        ...,
        description="A brief, one-sentence description of the test's purpose.",
    )
    expected_outcome: Union[ExpectedReturnValue, ExpectedError] = Field(
        ...,
        description=(
            "The expected result of running "
            "the function with the given inputs."
        ),
    )


class StorageTestCase(TestCaseBase):
    """A test case designed for serialization, where inputs are a JSON
    string."""

    inputs: Optional[str] = Field(
        ...,
        description=(
            "A JSON string representing the dictionary of "
            'function inputs. Example: \'{"a": 1, "b": 2}\''
        ),
    )


# --- 3. Define the runnable version ---
class RunnableTestCase(TestCaseBase):
    """A test case designed for runtime execution, where inputs are a parsed
    dictionary."""

    inputs: Optional[Dict[str, Any]] = Field(
        ...,
        description="A dictionary of function inputs, ready for execution.",
    )


class RunnableTestSuite(BaseModel):
    """A comprehensive test suite for a single function, categorized by test
    type."""

    happy_path_cases: List[RunnableTestCase] = Field(
        ..., alias="Happy Path / Typical Cases"
    )
    edge_cases: List[RunnableTestCase] = Field(..., alias="Edge Cases")
    error_conditions: List[RunnableTestCase] = Field(
        ..., alias="Error Conditions / Invalid Input"
    )


# Define the top-level structure for the entire test suite
class TestSuite(BaseModel):
    """A comprehensive test suite for a single function, categorized by test
    type."""

    happy_path_cases: List[StorageTestCase] = Field(
        ..., alias="Happy Path / Typical Cases"
    )
    edge_cases: List[StorageTestCase] = Field(..., alias="Edge Cases")
    error_conditions: List[StorageTestCase] = Field(
        ..., alias="Error Conditions / Invalid Input"
    )


class ImprovementDetail(BaseModel):
    """Describes a single specific issue found during the review and a
    suggestion to fix it."""

    issue: str = Field(
        ...,
        description=(
            "A concise description of the specific issue "
            "identified in the test code, related to the review criteria."
        ),
    )
    suggestion: str = Field(
        ...,
        description=(
            "A specific, actionable suggestion for how "
            "to modify the test code to address the identified issue."
        ),
    )


class ReviewFeedback(BaseModel):
    """Model used for structuring review feedback."""

    is_perfect: bool = Field(
        ...,
        description=(
            "Indicates if the code is considered perfect "
            "(true) or if improvements are needed (false)."
        ),
    )
    improvements_needed: Optional[List[ImprovementDetail]] = Field(
        default=None,
        description=(
            "A list of specific improvements. This field MUST be populated"
            " with at least one item if 'is_perfect' is false. It MUST be"
            " null or an empty list if 'is_perfect' is true."
        ),
    )

    # pylint: disable=too-few-public-methods
    class Config:
        """Additional config information."""

        json_schema_extra = {
            "example_perfect": {
                "is_perfect": True,
                "improvements_needed": None,
            },
            "example_needs_improvement": {
                "is_perfect": False,
                "improvements_needed": [
                    {
                        "issue": (
                            "The test does not verify "
                            "the exact error message."
                        ),
                        "suggestion": (
                            "Modify `pytest.raises` to "
                            "use `match` for message assertion."
                        ),
                    }
                ],
            },
        }
