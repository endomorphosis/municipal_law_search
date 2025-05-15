import ast
from pathlib import Path
from typing import Any, Self


from pydantic import BaseModel, DirectoryPath, Field, ValidationError


from configs import Configs, configs
from logger import logger


def _get_item(self: BaseModel, item: Any) -> Any:
    """
    Get the attribute value from the model.

    Args:
        self (Self): The instance of the model.
        item (Any): The name of the attribute to retrieve.

    Returns:
        Any: The value of the requested attribute.
    """
    try:
        return getattr(self, item)
    except AttributeError as e:
        raise KeyError(f"Attribute '{item}' not found.") from e


def _set_item(self: BaseModel, key: str, value: Any) -> None:
    """
    Set the attribute value in the model.

    Args:
        self (BaseModel): The instance of the model.
        key (str): The name of the attribute to set.
        value (Any): The value to set for the attribute.

    Raises:
        ValidationError: If the value does not pass validation.
        AttributeError: If the attribute does not exist.
    """
    try:
        setattr(self, key, value)
        # Re-validate the new value
        self.model_validate()
    except ValidationError as e:
        raise ValidationError(f"Validation error setting '{key}' to '{value}': {e.errors()}")
    except AttributeError as e:
        raise KeyError(f"Attribute '{key}' not found.") from e

def _get(self, key: str, default: Any = None) -> Any:
    """
    Get the attribute value from the model.

    Args:
        self (BaseModel): The instance of the model.
        key (str): The name of the attribute to retrieve.

    Returns:
        Any: The value of the requested attribute.
    """
    try:
        return getattr(self, key)
    except Exception:
        return default


def assign_dict_funcs(self: BaseModel) -> BaseModel:
    self.__getitem__ = _get_item
    self.__setitem__ = _set_item
    self.get = _get
    return self


class Imports(BaseModel):
    """
    A model to represent import statements in a Python file.

    This class is used to store information about the imports found in a
    Python file, including the module name and the imported names.

    Attributes:
        imported_names (list): A list of names imported from the module.
    """
    imported_names: list[str] = Field(default_factory=list)

    def __init__(self, **data) -> Self:
        super().__init__(**data)
        self = assign_dict_funcs(self)

class Functions(BaseModel):
    """
    A model to represent functions in a Python file.

    This class is used to store information about the functions found in a
    Python file, including the function name, arguments, docstring, and
    return type.

    Attributes:
        name (str): The name of the function.
        args (list): A list of argument names for the function.
        docstring (str): The docstring of the function.
        returns (str): The return type of the function.
    """
    name: str
    args: list[str] = Field(default_factory=list)
    docstring: str = None
    returns: str = None
    decorators: list[str] = Field(default_factory=list)

    def __init__(self, **data) -> Self:
        super().__init__(**data)
        self = assign_dict_funcs(self)

class ModelInfo(BaseModel):
    """
    A base model for the test file generator.

    This class defines the structure of the configuration and resources
    used in the test file generation process.

    Attributes:
        configs (Configs): Configuration settings for the application.
        resources (dict): Resources needed for generating test files.
    """
    path: DirectoryPath = Field(default_factory=list)
    imports: Imports = Field(default_factory=list)
    functions: list = Field(default_factory=list)
    coroutines: list = Field(default_factory=list)
    classes: list = Field(default_factory=list)

    def __init__(self, **data) -> Self:
        super().__init__(**data)
        self = assign_dict_funcs(self)



class _AstFileParser:
    """
    A class to parse Python files and extract information about their callables.
    
    This class uses the Abstract Syntax Tree (AST) module to analyze Python code
    and extract information about functions, classes, and their attributes.
    """
    _MODULE_KEYS = ['imports', 'functions', 'coroutines', 'classes']
    _CLASS_KEYS = ['attribute', 'classmethod', 'coroutine', 'dunder', 
                    'method', 'property', 'staticmethod', 'unknown']

    def __init__(self, file_path: str):
        self.file_path = file_path

        # Initialize collections for different types of callables
        self.module_info: dict[str, list] = {key: [] for key in self._MODULE_KEYS}
        self.module_info["module_name"] = Path(file_path).stem

        self.file_content: str = self._open_file()

    def _open_file(self) -> str:
        """Open the file and read its content."""
        with open(self.file_path, 'r') as file:
            return file.read()

    @property
    def nodes(self):
        for node in ast.walk(ast.parse(self.file_content)):
            yield node

    def extract_imports_from(self, node: ast.Import | ast.ImportFrom) -> None:
        """Extract import statements from the AST node.
        
        Args:
            node (ast.Import | ast.ImportFrom): The AST node representing an import statement.
        """
        self.module_info["imports"].append(ast.unparse(node))

    def extract_standalone_functions_and_coroutines(self, node: ast.FunctionDef) -> None:
        """Extract standalone functions and coroutines from the AST node."""
        is_coroutine = any(isinstance(decorator, ast.Name) and decorator.id == "coroutine" for decorator in node.decorator_list)
        key = "coroutines" if is_coroutine else "functions"
        self.module_info[key].append({
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "docstring": ast.get_docstring(node),
            "returns": ast.unparse(node.returns) if node.returns else None,
            "decorators": [ast.unparse(decorator) for decorator in node.decorator_list],
        })

    def _extract_class_methods(self, item: ast.FunctionDef, class_info: dict[str, list]) -> dict[str, Any]:
        method_info = {
            "name": item.name,
            "args": [arg.arg for arg in item.args.args],
            "docstring": ast.get_docstring(item),
            "returns": ast.unparse(item.returns) if item.returns else None,
        }
        # Identify method type
        for dec in item.decorator_list:
            method_name = dec.id if isinstance(dec, ast.Name) else "unknown"
            if isinstance(dec, ast.Name):
                if method_name in self._CLASS_KEYS:
                    if item.name.startswith("__") and item.name.endswith("__"):
                        method_name = "dunder"
                    else:
                        method_name = "method"
                logger.debug(f"Found {method_name} decorator: {dec.id}")
            else:
                logger.warning(f"Unknown decorator: {ast.unparse(dec)}")
                continue
        # Put the method info in the appropriate list
        return class_info[method_name].append(method_info)

    def _extract_class_attributes(self, item: ast.Assign) -> list[dict[str, Any]]:
        """Extract class attributes from the AST node."""
        return [
            {"name": target.id, "value": ast.unparse(item.value)}
            for target in item.targets 
            if isinstance(target, ast.Name)
        ]

    def extract_classes_from(self, node: ast.ClassDef) -> None:
        """Extract class information from the AST node."""

        class_info = {key: [] for key in self._CLASS_KEYS}
        class_info.update({"docstring": ast.get_docstring(node),})

        for item in node.body:
            match item:
                case ast.FunctionDef():
                    class_info = self._extract_class_methods(item, class_info)
                case ast.Assign():
                    class_info["attributes"] = self._extract_class_attributes(item)
                case _:
                    logger.warning(f"Unknown class body item: {ast.unparse(item)}")
                    continue
        self.module_info["classes"][node.name] = class_info


def parse_file(file_path: str) -> dict[str, Any]:
    """
    Parse a Python file to extract information about its callables.
    
    Args:
        file_path (str): Path to the Python file.
        
    Returns:
        dict: A dictionary containing information about the file's callables.
    """
    # Initialize the parser
    parser = _AstFileParser(file_path)

    try:
        # Parse the file content into an AST, then iterate through all nodes.
        for node in parser.nodes:
            match node:
                case ast.Import() | ast.ImportFrom():
                    parser.extract_imports_from(node)

                case ast.FunctionDef() if node.parent_field == "body":
                    parser.extract_standalone_functions_and_coroutines(node)

                case ast.ClassDef() if node.parent_field == "body":
                    parser.extract_classes_from(node)

                case _:
                    logger.warning(f"Unknown AST node: {ast.unparse(node)}")
                    continue
        return parser.module_info

    except (SyntaxError, Exception) as e:
        msg = f"{type(e).__name__} parsing file {file_path}: {e}"
        logger.exception(msg)
        return {
            "module_name": Path(file_path).stem,
            "error": msg,
        }