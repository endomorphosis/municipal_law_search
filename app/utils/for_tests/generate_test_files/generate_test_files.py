import argparse
from pathlib import Path
import sys
from typing import Any, Callable, Optional


import tqdm


from configs import Configs
from logger import logger


from ._generate_test_files._parse_file import parse_file
from ._generate_test_files._check_if_target_dir_exists import check_if_target_dir_exists
from ._generate_test_files._make_init_file import make_init_file
from ._generate_test_files._make_output_dir import make_output_dir
from ._generate_test_files._except_for_the_files_in_these_dirs import except_for_the_files_in_these_dirs
from ._generate_test_files._get_all_python_files_in import get_all_python_files_in
from ._generate_test_files._generate_test_file_path import generate_test_file_path
from ._generate_test_files._write_test_file import write_test_file
from ._generate_test_files._generate_test_content import generate_test_content


class TestFileGenerator:

    def __init__(self, 
                resources: dict[str, Callable] = None, 
                configs: Configs = None
                ):
        self.configs = configs
        self.resources = resources

        # Initialize resources
        self._parse_file = self.resources['parse_file']
        self._make_init_file = self.resources['make_init_file']
        self._check_if_target_dir_exists = self.resources['check_if_target_dir_exists']
        self._make_output_dir = self.resources['make_output_dir']
        self._get_all_python_files_in = self.resources['get_all_python_files_in']
        self._generate_test_file_path = self.resources['generate_test_file_path']
        self._write_test_file = self.resources['write_test_file']
        self._generate_test_files = self.resources['generate_test_files']
        self._except_for_the_files_in_these_dirs = self.resources['except_for_the_files_in_these_dirs']
        self._generate_test_content = self.resources['generate_test_content']


    @staticmethod
    def _turn_args_into_paths(
            target_dir: str, 
            output_dir:str, 
            ignore_dir_list: list[str]
            ) -> tuple[Path, Path, list[Path]]:
        """
        Convert string arguments to Path objects for target_dir, output_dir, and ignore_dir_list.
        """
        return Path(target_dir), Path(output_dir), [Path(dir) for dir in ignore_dir_list]

    def run(self, 
            target_dir: str, 
            output_dir: str = "tests", 
            ignore_dir_list: Optional[list[str]] = []
            ) -> bool:
        """
        Generate unit test files for all python files in the target directory and its sub directories.
        The tests are generated per file, and each callable in the file has its own unit tests. This includes:
            - standalone functions
            - standalone coroutines
            - classes
                - explicitly defined dunder methods
                - methods
                - coroutine methods
                - class methods
                - static methods
                - properties
                - attributes
        NOTE Tests are not generated for:
            - dunder methods that are not explicitly defined in the class
            - imports from other files

        Args:
            target_dir (str): The target directory containing the python files.
            output_dir (str): The output directory for the test files. Defaults to "tests".

        Returns: 
            bool: True if the test files were generated successfully, False otherwise.
        
        Raises:
            FileNotFoundError: If the target directory does not exist.
            NotADirectoryError: If the target directory is not a directory.

        Example:
            resources = {"some_resource": some_callable}
            configs = Configs()
            generator = TestFileGenerator(resources=resources, configs=configs)
            generator.run(target_dir="app")

            os.listdir("tests")
        '['__init__.py', 'test_file_1.py', 'test_file_2.py', ...]'
        """
        num_files_generated = 0

        target_dir, output_dir, ignore_dir_list = self._turn_args_into_paths(target_dir, output_dir, ignore_dir_list)

        self._check_if_target_dir_exists(target_dir)

        self._make_output_dir(output_dir)
        self._make_init_file(output_dir)

        python_files_paths: list[Path] = self._get_all_python_files_in(target_dir)

        if not python_files_paths:
            logger.info(f"No python files found in '{target_dir}'")
            return False

        python_files_paths: list[Path] = self._except_for_the_files_in_these_dirs(python_files_paths, ignore_dir_list)

        if not python_files_paths:
            logger.info(f"All python files were filtered out in'{target_dir}'")
            return False
        else:
            total_files = len(python_files_paths)
            logger.info(f"Found {total_files} python files in '{target_dir}'")

        # Process each python file
        for file_path in tqdm.tqdm(python_files_paths):
            try:
                # Define the test file directory based on the target directory.
                # The test file should be in the output directory,
                #  but with the same structure as the target directory.
                if file_path.is_relative_to(target_dir):
                    relative_path = file_path.parent.relative_to(target_dir)
                    test_file_dir = output_dir / relative_path
                else:
                    # Fallback for files that aren't within target_dir
                    test_file_dir = output_dir / file_path.parent.relative_to(Path.cwd())

                self._make_output_dir(test_file_dir)
                if not (test_file_dir / "__init__.py").exists():
                    self._make_init_file(test_file_dir)

                # Parse the file to extract module information
                module_info: dict[str, Any] = self._parse_file(file_path)

                # Generate test file path
                # The test file should be named "test_[original_filename].py"
                test_file_path: Path = self._generate_test_file_path(file_path, output_dir)

                if test_file_path.exists():
                    continue

                # Generate test file content
                test_content: str = self._generate_test_content(module_info)

                # Write the test file
                success: bool = self._write_test_file(test_file_path, test_content)

                logger.info(f"Test file generated at '{test_file_path}'.")
                if success:
                    num_files_generated += 1

            except Exception as e:
                logger.exception(f"Failed to generate test file for '{file_path}': {e}")
                continue

        logger.info(f"Generated {num_files_generated} tests out of {total_files}") 
        # Return success status
        return num_files_generated


def main():
    parser = argparse.ArgumentParser(description="Generate python test files for a give codebase.")
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="The target directory containing the python files.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="tests",
        help="The output directory for the test files.",
    )
    parser.add_argument(
        "--ignore_dir_list",
        type=str,
        nargs="*",
        default=[],
        help="List of directories to ignore.",
    )
    args = parser.parse_args()

    resources = {
        "parse_file": parse_file,
        "make_output_dir": make_output_dir,
        "generate_test_file_path": generate_test_file_path,
        "make_init_file": make_init_file,
        "check_if_target_dir_exists": check_if_target_dir_exists,
        "get_all_python_files_in": get_all_python_files_in,
        "write_test_file": write_test_file,
        "except_for_the_files_in_these_dirs": except_for_the_files_in_these_dirs,
        "generate_test_content": generate_test_content,
    }

    generator = TestFileGenerator(resources=resources)
    num_files_generated = generator.run(
        target_dir=args.target_dir, 
        output_dir=args.output_dir,
        ignore_dir_list=args.ignore_dir_list,
    )
    if num_files_generated > 0:
        logger.info("Successfully generated test files.")
        sys.exit(0)
    else:
        logger.info("Failed to generate test files.")
        sys.exit(1)


if __name__ == "__main__":
    main()
