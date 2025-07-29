# =============================================================================
#  Divengine Python Vault
# =============================================================================
#  pyvault is a tool that parses a Python codebase and generates an Obsidian-
#  compatible vault. It extracts modules, classes, functions, and internal 
#  relationships (such as inheritance and function calls) and outputs a set of 
#  Markdown files with Obsidian wiki-style links. This enables developers, 
#  educators, and learners to visualize and navigate a codebase as a knowledge 
#  graph using Obsidian.md
# =============================================================================
#          Version: 1.0.2
#           Author: rafageist@divengine.com
#          Company: Divengine Software Solutions
#          License: MIT
#  Project website: https://github.com/divengine/pyvault
# =============================================================================

import os
import ast
import argparse
import warnings
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import sys

def resolve_link(path_str):
    """
    Convert a file path into an Obsidian-compatible wiki link.

    Replaces OS-specific path separators (e.g., backslashes on Windows) with forward slashes
    to ensure compatibility with Obsidian's link syntax.

    Args:
        path_str (str): The file path to convert.

    Returns:
        str: A string formatted as an Obsidian wiki-style link.
    """
    return f"[[{path_str.replace(os.sep, '/') }]]"

def _write_note(note_path, content_lines):
    """
    Write a list of text lines to a Markdown file at the specified path.

    Ensures that the target directory exists. After writing, it clears the
    current terminal line (for cleaner output in progress displays).

    Args:
        note_path (str): Full file path where the Markdown note will be saved.
        content_lines (list of str): List of strings to write to the file.
    """
    # Ensure parent directories exist
    os.makedirs(os.path.dirname(note_path), exist_ok=True)

    # Write all lines to the specified file
    with open(note_path, "w", encoding="utf-8") as f:
        f.writelines(content_lines)

    # Clear the current line in the terminal (ANSI escape code)
    sys.stdout.write("\033[2K\r")


def format_docstring(doc):
    """
    Convert a raw docstring with Sphinx-style tags into a clean Markdown format.

    This function parses lines in the docstring that start with tags like
    :param, :type, :returns, and :rtype, and formats them into a Markdown table.
    Other lines are preserved as general description content.

    Args:
        doc (str): Raw docstring from the source code.

    Returns:
        str: A Markdown-formatted version of the docstring, with a 'Details' table
             for structured tags if applicable.
    """
    # Split docstring into lines and prepare storage
    lines = doc.strip().split("\n")
    formatted = []
    table = []

    # Parse each line
    for line in lines:
        line = line.strip()
        if line.startswith(":param") or line.startswith(":type") or line.startswith(":returns") or line.startswith(":rtype"):
            # Split into 3 parts: tag, name, and description
            parts = line.split(" ", 2)
            if len(parts) == 3:
                label, name, desc = parts
                table.append((label.strip(':'), name, desc))
        else:
            formatted.append(line)

    # Combine main body text
    result = "\n".join(formatted)

    # Add Markdown table if any tagged lines were parsed
    if table:
        result += "\n\n### Details:\n"
        result += "| Tag | Name | Description |\n"
        result += "|-----|------|-------------|\n"
        for tag, name, desc in table:
            result += f"| `{tag}` | `{name}` | {desc} |\n"

    return result

def extract_info(filepath, base_folder, ctx):
    """
    Parse a Python source file to extract imports, classes, and functions.

    This function reads a `.py` file, parses its AST, and updates the context
    dictionary (`ctx`) with information about:
    - Imports (`import` and `from ... import`)
    - Classes (name, base classes, methods, and attributes)
    - Functions (name, arguments, docstrings, and call graph)

    For each class and function found, corresponding Markdown notes are generated.

    Args:
        filepath (str): Path to the Python file to analyze.
        base_folder (str): Root folder of the project (used to calculate relative paths).
        ctx (dict): Context object used to accumulate stats, links, and vault content.
    """
    # Calculate relative path for display
    rel = os.path.relpath(filepath, base_folder)
    sys.stdout.write("\033[2K\r")
    print(f"* Processing file: {rel}", end="", flush=True)

    # Read and parse the file (skip if syntax error)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
        try:
            source_code = file.read()
            node = ast.parse(source_code, filename=filepath)
        except SyntaxError:
            return

    # Path without extension (used as key)
    rel_path = os.path.relpath(filepath, base_folder)
    rel_path_no_ext = os.path.splitext(rel_path)[0]

    # Update file and module statistics
    ctx['stats']['files'] += 1
    ctx['stats']['modules'] += 1

    # Traverse top-level nodes in the AST
    for item in node.body:
        # Handle import statements
        if isinstance(item, ast.Import):
            for alias in item.names:
                ctx['import_data'][rel_path].append(alias.name)
                ctx['stats']['imports'] += 1

        elif isinstance(item, ast.ImportFrom):
            module = item.module if item.module else ""
            for alias in item.names:
                ctx['import_data'][rel_path].append(f"{module}.{alias.name}")
                ctx['stats']['imports'] += 1

        # Handle class definitions
        if isinstance(item, ast.ClassDef):
            ctx['stats']['classes'] += 1
            class_name = item.name
            # Collect base classes
            bases = [base.id if isinstance(base, ast.Name) else ast.unparse(base) for base in item.bases]
            class_path = os.path.join(rel_path_no_ext, class_name)
            ctx['class_index'][class_name] = class_path
            ctx['module_index'][rel_path]["classes"].append(class_path)

            methods = []
            props = []
            for child in item.body:
                # Handle methods
                if isinstance(child, ast.FunctionDef):
                    ctx['stats']['functions'] += 1
                    methods.append(child.name)
                    func_path = os.path.join(class_path, child.name)
                    ctx['function_index'][child.name] = func_path
                    ctx['uses_map'][class_path].add(func_path)
                    write_function_note(child.name, child.args, rel_path, ctx, func_path, ast.get_docstring(child))
                    find_calls(child, func_path, ctx)
                # Handle attributes
                elif isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            props.append(target.id)

            # Generate class note
            write_class_note(class_name, bases, methods, props, rel_path, ctx, class_path, ast.get_docstring(item))

        # Handle standalone function definitions
        elif isinstance(item, ast.FunctionDef):
            ctx['stats']['functions'] += 1
            func_name = item.name
            full_func_path = os.path.join(rel_path_no_ext, func_name)
            ctx['function_index'][func_name] = full_func_path
            ctx['module_index'][rel_path]["functions"].append(full_func_path)
            write_function_note(func_name, item.args, rel_path, ctx, full_func_path, ast.get_docstring(item))
            find_calls(item, full_func_path, ctx)

def write_class_note(name, bases, methods, props, rel_path, ctx, full_path, doc):
    """
    Generate a Markdown note for a class and write it to the Obsidian vault.

    This function creates a Markdown-formatted file describing the given class,
    including its file location, base classes, methods, properties, and docstring.

    Args:
        name (str): The name of the class.
        bases (list of str): Base classes (inheritance).
        methods (list of str): List of method names defined in the class.
        props (list of str): List of attribute names (class-level properties).
        rel_path (str): Relative path to the original .py file.
        ctx (dict): Vault context object containing folder paths and references.
        full_path (str): Logical vault path to the class (used for Markdown note path).
        doc (str): Optional docstring of the class.
    """

    # Determine output file path in the vault
    dest_path = os.path.join(ctx['VAULT_DIR'], full_path + ".md")

    # Start building the content for the Markdown file
    content = [
        f"# Class `{name}`\n",                  # Title
        f"#class\n\n",                          # Tag
        f"**File**: `{rel_path}`\n\n"           # Source file path
    ]

    # Include the docstring, if available
    if doc:
        content.append(f"## Docstring:\n\n{doc}\n\n")

    # List of base classes with links
    content.append("## Inherits from:\n")
    content += [f"- {resolve_link(ctx['class_index'][b])}\n" for b in bases if b in ctx['class_index']] or ["- None\n"]

    # List of method links
    content.append("\n## Methods:\n")
    content += [f"- {resolve_link(os.path.join(full_path, m))}\n" for m in methods] or ["- None\n"]

    # List of class properties
    content.append("\n## Properties:\n")
    content += [f"- `{p}` #property\n" for p in props] or ["- None\n"]

    # Finally, write to disk
    _write_note(dest_path, content)


def write_function_note(name, args_obj, rel_path, ctx, full_path, doc):
    """
    Generate a Markdown note for a function or method and write it to the Obsidian vault.

    This function creates a Markdown file documenting the specified function or method,
    including its name, arguments, origin file, optional docstring, and referenced calls.

    Args:
        name (str): Name of the function or method.
        args_obj (ast.arguments): AST object containing argument definitions.
        rel_path (str): Relative file path where the function is defined.
        ctx (dict): Context with vault path and indexing structures.
        full_path (str): Logical vault path for the function note.
        doc (str): Optional docstring to include.
    """

    # Define the target Markdown note file path
    dest_path = os.path.join(ctx['VAULT_DIR'], full_path + ".md")

    # Extract argument names from AST object
    args = [arg.arg for arg in args_obj.args]

    # Begin note content with title and tag (method or function)
    content = [
        f"# Function `{name}`\n",
        f"#method\n\n" if "/" in full_path else "#function\n\n",
        f"**File**: `{rel_path}`\n\n",
        "## Arguments:\n"
    ]

    # List arguments
    content += [f"- `{arg}`\n" for arg in args] or ["- None\n"]

    # Include docstring if available
    if doc:
        content.append("\n## Docstring:\n\n")
        content.append(format_docstring(doc))
        content.append("\n")

    # Add references to other elements this function uses
    if full_path in ctx['uses_map']:
        content.append("\n## Uses:\n")
        content += [f"- {resolve_link(target)}\n" for target in ctx['uses_map'][full_path]]

    # Write the note to disk
    _write_note(dest_path, content)

def find_calls(node, current_path, ctx):
    """
    Analyze a function/method AST node to find internal calls to other functions within the project.

    This function walks the AST tree of a function or method and detects calls to other known
    functions. It updates the context to reflect which elements are used (called) from the current node.

    Args:
        node (ast.AST): The AST node representing the function or method body.
        current_path (str): Vault path of the current function or method.
        ctx (dict): Context containing function index and usage maps.
    """

    # Walk all subnodes of the given AST node
    for child in ast.walk(node):
        # If the subnode is a function/method call
        if isinstance(child, ast.Call):
            # Direct function call: e.g., foo()
            if isinstance(child.func, ast.Name):
                called = child.func.id
                if called in ctx['function_index']:
                    # Record the usage relationship
                    ctx['uses_map'][current_path].add(ctx['function_index'][called])
                    ctx['stats']['relationships'] += 1
            # Object method call: e.g., obj.foo()
            elif isinstance(child.func, ast.Attribute):
                attr = child.func.attr
                if attr in ctx['function_index']:
                    # Record usage of attribute-named functions if found in index
                    ctx['uses_map'][current_path].add(ctx['function_index'][attr])
                    ctx['stats']['relationships'] += 1

def write_module_and_import_notes(ctx):
    """
    Generate and save Markdown notes for each module and its imports.

    For each Python file (module) in the context, this function creates:
    - A Markdown file summarizing the module's functions and classes.
    - A separate Markdown file listing all the imported modules.

    Args:
        ctx (dict): The context dictionary that holds module index and import data,
                    as well as the output vault directory.
    """

    # Create a note for each module (file)
    for rel_path, items in ctx['module_index'].items():
        module_name = os.path.splitext(os.path.basename(rel_path))[0]
        dest_path = os.path.join(ctx['VAULT_DIR'], os.path.splitext(rel_path)[0] + ".md")

        content = [
            f"# Module `{module_name}.py`\n",
            "#module\n\n",
            f"**Path**: `{rel_path}`\n\n",
        ]

        # List all functions defined in this module
        if items["functions"]:
            content.append("## Functions:\n")
            content += [f"- {resolve_link(f)}\n" for f in items["functions"]]

        # List all classes defined in this module
        if items["classes"]:
            content.append("\n## Classes:\n")
            content += [f"- {resolve_link(c)}\n" for c in items["classes"]]

        _write_note(dest_path, content)

    # Create a separate note for each file's imports
    for rel_path, imports in ctx['import_data'].items():
        dest_path = os.path.join(ctx['VAULT_DIR'], os.path.splitext(rel_path)[0], "imports.md")
        content = [
            f"# Imports in `{rel_path}`\n",
            f"#imports\n\n"
        ]
        content += [f"- `{imp}`\n" for imp in imports]
        _write_note(dest_path, content)

def scan_folder(folder, ctx):
    """
    Recursively scan a folder for Python (.py) files and extract information from each.

    This function walks through all subdirectories of the given folder, finds `.py` files,
    and calls `extract_info` to process each one. It updates the provided context with
    module, function, class, and import information.

    Args:
        folder (str): The root directory to scan.
        ctx (dict): A context dictionary that accumulates scan results and metadata.
    """

    # Recursively walk through the folder and subfolders
    for root, _, files in os.walk(folder):
        for file in files:
            # Only process Python source files
            if file.endswith(".py"):
                # Call extract_info to process and index the file
                extract_info(os.path.join(root, file), folder, ctx)

    # Clear current terminal line and show a final message
    sys.stdout.write("\033[2K\r")
    print("✔️ Done scanning files.")

def main():
    """
    Entry point for the CLI tool 'pyvault'.

    This function sets up the argument parser, initializes the analysis context,
    scans a Python codebase to extract class, function, and import metadata,
    and generates a structured Obsidian-compatible markdown vault.

    It also prints a summary of the extracted content.

    Usage:
        pyvault <project_path> <vault_output>
    """

    # Print banner with tool title, version, and current timestamp
    print("=" * 60)
    print("[[]] Divengine Python Vault – Generate Obsidian.md vault from Python project")
    print(f"- Version: 1.0.3")
    print(f"- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # Suppress SyntaxWarnings that may occur during AST parsing
    warnings.filterwarnings("ignore", category=SyntaxWarning)

    # Set up command-line argument parser
    parser = argparse.ArgumentParser(
        prog="pyvault",
        description="Divengine Python Vault - Generate an Obsidian-compatible vault from a Python codebase.",
        epilog="Example: pyvault ./my_project ./vault_output"
    )

    # First positional argument: path to the Python project folder
    parser.add_argument("project_path", help="Path to the root folder of the Python project")

    # Second positional argument: output folder for the generated vault
    parser.add_argument("vault_output", help="Path to the output folder for the Obsidian vault")

    # Parse command-line arguments into a namespace
    args = parser.parse_args()

    # Initialize the context dictionary to track all scan data and statistics
    ctx = {
        'VAULT_DIR': args.vault_output,
        'class_index': {},  # Map class names to their full path
        'function_index': {},  # Map function names to their full path
        'uses_map': defaultdict(set),  # Track what each function/class uses
        'import_data': defaultdict(list),  # Store all imports per module
        'module_index': defaultdict(lambda: {"functions": [], "classes": []}),  # Per-module structure
        'stats': {
            'files': 0,
            'modules': 0,
            'classes': 0,
            'functions': 0,
            'imports': 0,
            'relationships': 0
        }
    }

    # Create output vault folder if it doesn't already exist
    os.makedirs(ctx['VAULT_DIR'], exist_ok=True)

    # Begin recursive scan of all .py files in the given folder
    scan_folder(args.project_path, ctx)

    print("\nFinishing...")
    # Write module-level and import documentation notes
    write_module_and_import_notes(ctx)

    # Print analysis summary
    print();
    print("\nSummary:")
    print("-----------------------------------------------");
    print(f"- Files:         {ctx['stats']['files']}")
    print(f"- Modules:       {ctx['stats']['modules']}")
    print(f"- Classes:       {ctx['stats']['classes']}")
    print(f"- Functions:     {ctx['stats']['functions']}")
    print(f"- Imports:       {ctx['stats']['imports']}")
    print(f"- Relationships: {ctx['stats']['relationships']}")
    print("-----------------------------------------------");

    print("\nDone!")


if __name__ == "__main__":
    main()
