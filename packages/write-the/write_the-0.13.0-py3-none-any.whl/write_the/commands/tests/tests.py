from pathlib import Path
from black import format_str, FileMode
from .prompts import write_tests_for_file_prompt
from write_the.llm import LLM


async def write_the_tests(filename: Path, model="gpt-3.5-turbo-instruct") -> str:
    """
    Formats and runs the tests for a given file using a specified model.

    Args:
      filename (Path): The path to the file to be tested.
      model (str): The model to use for the generation. Defaults to "gpt-3.5-turbo-instruct".

    Returns:
      str: The formatted and tested code.

    Examples:
      >>> write_the_tests(Path("test.py"), "gpt-3.5-turbo-instruct")
      "Formatted and tested code"

    Note:
      This function is asynchronous and should be awaited when called.
    """
    with open(filename, "r") as file:
        source_code = file.read()
    source_code = format_str(source_code, mode=FileMode())
    llm = LLM(write_tests_for_file_prompt, model_name=model)
    result = await llm.run(code=source_code, path=filename)
    code = (
        result.strip()
        .lstrip("Test Code:\n```python")
        .lstrip("```python")
        .lstrip("```")
        .rstrip("```")
    )
    return format_str(code, mode=FileMode())
