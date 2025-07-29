from pathlib import Path
from .prompts import write_converters_for_file_prompt
from write_the.llm import LLM


async def write_the_converters(filename: Path, input_format: str, output_format: str, model: str = "gpt-3.5-turbo-instruct") -> str:
    """
    Formats and runs the tests for a given file.

    Args:
      filename (Path): The path to the file to be tested.
      input_format (str): The input format of the file.
      output_format (str): The format to convert the file to.
      model (str, optional): The model to use for conversion. Defaults to "gpt-3.5-turbo-instruct".

    Returns:
      str: The converted output.

    Examples:
      >>> write_the_converters(Path(".travis.yml"), input_format="Travis CI", output_format="Github Actions", model="gpt-3.5-turbo-instruct")
      "The converted output"
    """
    with open(filename, "r") as file:
        source_text = file.read()

    llm = LLM(write_converters_for_file_prompt, model_name=model)
    result = await llm.run(code=source_text, input_format=input_format, output_format=output_format)

    formatted_text = result.strip()

    if formatted_text.endswith('```') and not source_text.endswith('```'):
        # strip the last line of the code block if the source text didn't end with a code block
        formatted_text = formatted_text[: formatted_text.rfind("\n")]
    if formatted_text.startswith('```') and not source_text.startswith('```'):
        # strip the first line of the code block if the source text didn't start with a code block
        formatted_text = formatted_text[formatted_text.find("\n") + 1 :]
    return formatted_text.strip()
