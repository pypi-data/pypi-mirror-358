"""
This module contains functions for working with the filesystem.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def write_to_file(directory: str, about_content: str, output: str = "__about__.py") -> str:
    """
    Write the content to the __about__.py file.
    Args:
        directory (str): Directory to write the file to.
        about_content (str): Content to write to the file.
        output (str): Name of the file to write to.

    Returns:
        str: Path to the file that was written.
    """
    # Define the path for the __about__.py file
    about_file_path = os.path.join(directory, output)

    if output.endswith(".py"):
        combined_directory = Path(about_file_path).parent

    else:
        combined_directory = Path(about_file_path)
    logger.debug(f"Looking for __about__.py at {combined_directory}")
    # if directory doesn't exist check to see if the directory with - replaced with _ exists
    # if the directory with - replaced with _ exists use that directory
    # if the directory with - replaced with _ doesn't exist create the directory
    if not os.path.exists(str(combined_directory)):
        if os.path.exists(str(combined_directory).replace("-", "_")):
            combined_directory = Path(str(combined_directory).replace("-", "_"))
            logger.debug(f"Looking for __about__.py at {combined_directory}")
        else:
            # check if it is in a /src/ directory
            if "src" in str(combined_directory):
                # if it is in a /src/ directory check to see if the directory with - replaced with _ exists
                # if the directory with - replaced with _ exists use that directory
                # if the directory with - replaced with _ doesn't exist create the directory
                if os.path.exists(str(combined_directory).replace("-", "_")):
                    combined_directory = Path(str(combined_directory).replace("-", "_"))
                    logger.debug(f"Looking for __about__.py at {combined_directory}")

    # This still doesn't handle when the package name doesn't match the directory name.
    os.makedirs(str(combined_directory), exist_ok=True)

    # Write the content to the __about__.py file
    with open(about_file_path, "w", encoding="utf-8") as file:
        logger.debug(f"Writing __about__.py at {about_file_path}")
        file.write(about_content)
    return about_file_path
