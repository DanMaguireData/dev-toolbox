def add(a: int, b: int) -> int:
    """
    Adds two integers and returns the result.
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError(f"Paramter(s) (a: {a}, b: {b}) of invalid type")

    return a + b

def get_file_contents(filename: str) -> str:
    """
    Function opens a file and returns contents as string 
    """
    with open(filename, 'r') as f:
        source_code = f.read()
    return source_code