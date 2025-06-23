"""Example code to demonstrate graph invocation."""


def add(number_a: int, number_b: int) -> int:
    """Adds two integers and returns the result."""
    #
    if type(number_a) is not int or type(number_b) is not int:
        raise TypeError(
            "Parameter(s) "
            f"(a: {number_a}, number_b: {number_b}) "
            "of invalid type"
        )

    return number_a + number_b
