# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import os
from typing import Annotated, Optional

from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

from .decorators import log_io


def _is_python_repl_enabled() -> bool:
    """Check if Python REPL tool is enabled from configuration."""
    # Check environment variable first
    env_enabled = os.getenv("ENABLE_PYTHON_REPL", "false").lower()
    if env_enabled in ("true", "1", "yes", "on"):
        return True
    return False


# Initialize REPL and logger
repl: Optional[PythonREPL] = PythonREPL() if _is_python_repl_enabled() else None
logger = logging.getLogger(__name__)


def _clean_code(code: str) -> str:
    """
    Clean and fix common code formatting issues that might cause indentation errors.
    """
    import re
    
    # Split code into lines
    lines = code.split('\n')
    cleaned_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        
        # If line is empty, just add it
        if not stripped_line:
            cleaned_lines.append(line)
            i += 1
            continue
        
        # Check if this line might be a continuation of the previous line
        # Look for operators at the beginning of the line (indicating a broken expression)
        # But only if it's not part of a string or f-string
        if (stripped_line.startswith(('+ ', '- ', '* ', '/ ', '// ', '% ', '** ', '& ', '| ', '^ ', '<< ', '>> ', 'and ', 'or ')) and
            not _is_in_string_context(line)):
            # This line is likely a continuation of the previous line
            # We need to merge it with the previous line
            if cleaned_lines:
                prev_line = cleaned_lines.pop()
                # Join the previous line with the current line (removing the leading operator space)
                merged_line = prev_line.rstrip() + ' ' + stripped_line.lstrip()
                cleaned_lines.append(merged_line)
            else:
                # If there's no previous line, just add the current line
                cleaned_lines.append(line)
        elif ((stripped_line.endswith(('+', '-', '*', '/', '//', '%', '**', '&', '|', '^', '<<', '>>', 'and', 'or')) or
              stripped_line.endswith(('+\\', '-\\', '*\\', '/\\', '//\\', '%\\', '**\\', '&\\', '|\\', '^\\', '<<\\', '>>\\'))) and
              not _is_in_string_context(line)):
            # This line ends with an operator, likely to be continued in next line
            # We'll handle this together with the next line
            current_line = line.rstrip()
            i += 1
            # Keep collecting continuation lines
            while i < len(lines):
                next_line = lines[i].strip()
                if (next_line.startswith(('+ ', '- ', '* ', '/ ', '// ', '% ', '** ', '& ', '| ', '^ ', '<< ', '>> ', 'and ', 'or ')) and
                    not _is_in_string_context(next_line)):
                    # This is a continuation, merge it
                    current_line += ' ' + next_line.lstrip()
                    i += 1
                else:
                    break
            cleaned_lines.append(current_line)
            continue  # Skip incrementing i since we already did it in the loop
        else:
            # Normal line, add as is
            cleaned_lines.append(line)
        
        i += 1
    
    return '\n'.join(cleaned_lines)


def _is_in_string_context(line: str) -> bool:
    """
    Check if the given line contains string literals that might be continued.
    """
    # Count quotes to determine if we're in a string context
    # This is a simplified check for single and double quotes
    in_single_quote = False
    in_double_quote = False
    in_triple_single_quote = False
    in_triple_double_quote = False
    escape_next = False
    
    i = 0
    while i < len(line):
        char = line[i]
        
        if escape_next:
            escape_next = False
        elif char == '\\':
            escape_next = True
        elif char == '"' and not in_single_quote and not in_triple_single_quote:
            if i + 2 < len(line) and line[i:i+3] == '"""':
                if not in_triple_double_quote:
                    in_triple_double_quote = True
                    i += 2  # Skip the next two quotes
                else:
                    in_triple_double_quote = False
                    i += 2  # Skip the next two quotes
            elif not in_triple_double_quote:
                if not in_double_quote:
                    in_double_quote = True
                else:
                    in_double_quote = False
        elif char == "'" and not in_double_quote and not in_triple_double_quote:
            if i + 2 < len(line) and line[i:i+3] == "'''":
                if not in_triple_single_quote:
                    in_triple_single_quote = True
                    i += 2  # Skip the next two quotes
                else:
                    in_triple_single_quote = False
                    i += 2  # Skip the next two quotes
            elif not in_triple_single_quote:
                if not in_single_quote:
                    in_single_quote = True
                else:
                    in_single_quote = False
        i += 1
    
    return in_single_quote or in_double_quote or in_triple_single_quote or in_triple_double_quote


@tool
@log_io
def python_repl_tool(
    code: Annotated[
        str, "The python code to execute to do further analysis or calculation."
    ],
):
    """Use this to execute python code and do data analysis or calculation. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""

    # Check if the tool is enabled
    if not _is_python_repl_enabled():
        error_msg = "Python REPL tool is disabled. Please enable it in environment configuration."
        logger.warning(error_msg)
        return f"Tool disabled: {error_msg}"

    if not isinstance(code, str):
        error_msg = f"Invalid input: code must be a string, got {type(code)}"
        logger.error(error_msg)
        return f"Error executing code:\n```python\n{code}\n```\nError: {error_msg}"

    # Clean the code to fix common formatting issues
    cleaned_code = _clean_code(code)
    
    logger.info("Executing Python code")
    try:
        result = repl.run(cleaned_code)
        # Check if the result is an error message by looking for typical error patterns
        if isinstance(result, str) and ("Error" in result or "Exception" in result):
            logger.error(result)
            return f"Error executing code:\n```python\n{cleaned_code}\n```\nError: {result}"
        logger.info("Code execution successful")
    except SyntaxError as e:
        # Handle specific syntax errors like unterminated string literals
        error_msg = f"SyntaxError: {str(e)}"
        logger.error(error_msg)
        return f"Error executing code:\n```python\n{cleaned_code}\n```\nError: {error_msg}"
    except BaseException as e:
        error_msg = repr(e)
        logger.error(error_msg)
        return f"Error executing code:\n```python\n{cleaned_code}\n```\nError: {error_msg}"

    result_str = f"Successfully executed:\n```python\n{cleaned_code}\n```\nStdout: {result}"
    return result_str