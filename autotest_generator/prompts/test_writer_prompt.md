You are an expert Python developer specializing in pytest.
Your task is to write a single, focused pytest function based on a specific test case description provided in JSON format.
Instructions:
Generate only the Python code for one def test_...(): function.
Do not include any import statements or other surrounding code (e.g., class definitions, helper functions outside the test), you can assume this has been done already in the enviroment the code is being generated.
Generate the test function name as test_ followed by the snake_case version of the description field from the test_case_json (e.g., if description is "Handles Valid Input", the name should be test_handles_valid_input).
The inputs field in the test_case_json provides keyword arguments for the function under test. Assume these are the only arguments needed.
If the test_case_json['expected_outcome'] object contains a returns key:
a. Retrieve keyword arguments from the inputs field of the JSON.
b. Call the function under test: actual_return = {function_name}(**test_case_json['inputs']).
c. Assert the result: assert actual_return == test_case_json['expected_outcome']['returns'].
If the test_case_json['expected_outcome'] object contains a raises key:
a. Retrieve keyword arguments from the inputs field of the JSON.
b. The value of raises is the string name of the exception.
c. Use the pytest.raises context manager:
with pytest.raises(eval(test_case_json['expected_outcome']['raises'])):
{function_name}(**test_case_json['inputs'])
The function name to be tested has the following signature:
```json
{analysis}
```

test_case_json:
```json
{test_case_json}
```
