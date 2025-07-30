import ast
import inspect
import types
import os
import sys
import unittest
import re
import importlib
import importlib.util
import linecache
import asyncio
from typing import Union, Callable, Dict, Any, Optional
from functools import partial

def filter_after_comment_by(comment: str|re.Pattern) -> Callable[[str], str]:
    return partial(filter_after_comment, comment=comment)

def filter_after_comment(code: str, comment: Union[str, re.Pattern]) -> str:
    """
    Remove all code after finding a specified comment line in the source code.
    Only looks for lines that start with '#' (comment-only lines).
    
    Args:
        code: Source code string
        comment: Comment text to search for (string or regex pattern)
                String: substring match in comment text
                Pattern: regex match in comment text
                
    Returns:
        Code string with everything after the matched comment line removed,
        or original code if comment not found
        
    Example:
        ::

            code = '''
            def func():
                return "before"
            
            # MARKER: remove everything after this
            def func2():
                return "after"
            '''
            result = filter_after_comment(code, "MARKER: remove everything after this")
            # Returns code up to (but not including) the marker comment line
    """
    if not isinstance(comment, (str, re.Pattern)):
        raise TypeError(f"comment must be str or re.Pattern, got {type(comment)}")
    
    if not code.strip():
        return code
    
    lines = code.splitlines()
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # Check if this is a comment-only line
        if stripped_line.startswith('#'):
            # Extract the comment text (after '#' and leading whitespace)
            comment_text = stripped_line[1:].lstrip()
            
            # Check if this comment matches our search criteria
            if isinstance(comment, str):
                match = comment_text.startswith(comment)
            else:  # re.Pattern
                match = bool(comment.search(comment_text))
            
            if match:
                # Found the matching comment, return everything before this line
                result_lines = lines[:i]
                # Remove trailing empty lines
                while result_lines and not result_lines[-1].strip():
                    result_lines.pop()
                return '\n'.join(result_lines)
    
    # Comment not found, return original code
    return code

def load_module(module: Union[str, types.ModuleType]) -> types.ModuleType:
    """
    Resolve a module from string (module name or file path) or return the module if already loaded.
    
    Args:
        module: Either a module object, module name (e.g., "os.path"), or file path (e.g., "/path/to/module.py")
        
    Returns:
        The resolved module object
        
    Raises:
        ImportError: If module cannot be imported or loaded
        FileNotFoundError: If file path doesn't exist
        
    Example:
        ::

            # Import by name
            mod = resolve_module("os.path")
            
            # Import by file path
            mod = resolve_module("/path/to/mymodule.py")
            
            # Return existing module
            import os
            mod = resolve_module(os)  # returns os module
    """
    if isinstance(module, types.ModuleType):
        return module
    
    if not isinstance(module, str):
        raise TypeError("module must be a string (module name or file path) or ModuleType")
    
    # Check if it's a file path
    if os.path.exists(module) and module.endswith('.py'):
        # Dynamic import from file path
        module_name = os.path.splitext(os.path.basename(module))[0]
        spec = importlib.util.spec_from_file_location(module_name, module)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create module spec for {module}")
        
        resolved_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(resolved_module)
        return resolved_module
    
    # Try to import as module name
    try:
        return importlib.import_module(module)
    except ImportError as e:
        # If import fails, check if it might be a file path that doesn't exist
        if '/' in module or '\\' in module:
            raise FileNotFoundError(f"File not found: {module}")
        else:
            raise ImportError(f"Cannot import module '{module}': {e}")

def collect_module_attr(
        module: Union[str, types.ModuleType], 
        *,
        all: bool = False,
        names: Dict[str, Union[str, re.Pattern]]|list[str, re.Pattern]|None = None,
        classes: list[type]|bool|None = None,
        functions: bool = False,
        names_mapping: Dict|Callable|None = None,
    ) -> Dict[str, Any]:
    """
    Collect attributes from a module to construct a globals dictionary.
    
    Args:
        module: Module object or module name/path to resolve
        names: Dictionary mapping source names to target names, or list of names to collect
        classes: List of class types to collect instances of using isinstance, 
                or True to collect all classes
        functions: If True, collect all top-level functions (callable but not class)
        names_mapping: Additional name mapping after collection (dict or callable)
        
    Returns:
        Dictionary of collected attributes suitable for use as globals
        
    """
    # Resolve the module
    resolved_module = load_module(module)
    result = {}

    if all:
        result.update(resolved_module.__dict__)
        return result
    
    # Collect by names or patterns
    if names:
        if isinstance(names, dict):
            for pattern, result_name in names.items():  # key is source pattern, value is target name
                if isinstance(pattern, str):
                    if hasattr(resolved_module, pattern):
                        # direct name mapping: source_name -> target_name
                        result[result_name] = getattr(resolved_module, pattern)
                elif isinstance(pattern, re.Pattern):
                    # Regex pattern matching - ignore result_name, use original names
                    for attr_name in dir(resolved_module):
                        if pattern.match(attr_name):
                            # use the original name when key is regex
                            result[attr_name] = getattr(resolved_module, attr_name)
                else:
                    raise TypeError(f"Pattern must be str or re.Pattern, got {type(pattern)}")
        elif isinstance(names, list):
            for pattern in names:
                if isinstance(pattern, str):
                    if hasattr(resolved_module, pattern):
                        # use the origin name
                        result[pattern] = getattr(resolved_module, pattern)
                elif isinstance(pattern, re.Pattern):
                    matched_attrs = {}
                    for attr_name in dir(resolved_module):
                        if pattern.match(attr_name):
                            # use the origin name
                            matched_attrs[attr_name] = getattr(resolved_module, attr_name)
                    result.update(matched_attrs)
                else:
                    raise TypeError(f"Pattern must be str or re.Pattern, got {type(pattern)}")
        else:
            raise TypeError(f"names must be dict or list, got {type(names)}")
    
    # Collect instances of specific classes or all classes
    if classes is not None:
        for attr_name in dir(resolved_module):
            if not attr_name.startswith('_'):  # Skip private attributes
                attr_value = getattr(resolved_module, attr_name)
                
                if classes is True:
                    # Collect all classes
                    if inspect.isclass(attr_value):
                        result[attr_name] = attr_value
                else:
                    # Collect instances of specific classes
                    for cls in classes:
                        if isinstance(attr_value, cls):
                            result[attr_name] = attr_value
                            break
    
    # Collect functions
    if functions:
        for attr_name in dir(resolved_module):
            if not attr_name.startswith('_'):  # Skip private attributes
                attr_value = getattr(resolved_module, attr_name)
                if callable(attr_value) and not inspect.isclass(attr_value):
                    result[attr_name] = attr_value

    if names_mapping:
        if isinstance(names_mapping, dict):
            for name_from, name_to in names_mapping.items():
                if name_from in result:
                    result[name_to] = result.pop(name_from)
        elif callable(names_mapping):
            # Create a copy of keys to avoid modifying dict during iteration
            keys_to_remap = list(result.keys())
            for name_from in keys_to_remap:
                name_to = names_mapping(name_from)
                if (name_to != name_from) and name_from in result: # Only remap if the name actually changes
                    result[name_to] = result.pop(name_from)

    return result

def _extract_main_block(tree: ast.AST, file_content: str) -> Optional[tuple[str, int]]:
    """
    Extract the code from 'if __name__ == "__main__"' block.
    
    Args:
        tree: AST tree of the file
        file_content: Original file content
        
    Returns:
        Tuple of (extracted_code, start_line_number) or None if not found
    """
    def _is_main_check(node: ast.If) -> bool:
        """Check if this is an 'if __name__ == "__main__"' condition."""
        if not isinstance(node.test, ast.Compare):
            return False
        
        left = node.test.left
        if not (isinstance(left, ast.Name) and left.id == '__name__'):
            return False
        
        if len(node.test.ops) != 1 or not isinstance(node.test.ops[0], ast.Eq):
            return False
        
        if len(node.test.comparators) != 1:
            return False
        
        comp = node.test.comparators[0]
        return isinstance(comp, ast.Constant) and comp.value == "__main__"
    
    # Find the if __name__ == "__main__" block
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _is_main_check(node):
            # Get the source lines for the body of the if block
            file_lines = file_content.splitlines()
            
            # Find the start and end line numbers for the if block body
            body_start = node.body[0].lineno if node.body else node.lineno + 1
            body_end = node.end_lineno if hasattr(node, 'end_lineno') else len(file_lines)
            
            # Extract lines from the body (convert to 0-based indexing)
            main_lines = []
            base_indent = None
            
            for line_num in range(body_start - 1, body_end):
                if line_num >= len(file_lines):
                    break
                    
                line = file_lines[line_num]
                
                # Skip empty lines
                if not line.strip():
                    main_lines.append('')
                    continue
                    
                # Determine base indentation from first non-empty line
                if base_indent is None:
                    base_indent = len(line) - len(line.lstrip())
                
                # Remove base indentation
                if line.startswith(' ' * base_indent):
                    main_lines.append(line[base_indent:])
                else:
                    main_lines.append(line.lstrip())
            
            return '\n'.join(main_lines), body_start
    
    return None

def _add_source_info_to_objects(code: str, namespace: Dict[str, Any], original_file: str, line_offset: int) -> None:
    """
    Add source code information to functions and classes in the namespace
    so that inspect.getsource() can work with them.
    
    Args:
        code: The source code that was executed
        namespace: The namespace containing the executed objects
        original_file: The original file path for reference
        line_offset: The line offset to apply to the source code
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return  # Skip if code can't be parsed
    
    code_lines = code.splitlines()
    
    # Create a virtual filename for this code block
    virtual_filename = f"<load_main:{os.path.basename(original_file)}>"
    
    # Read the complete original file for linecache
    # This ensures inspect.getsource() can find the correct lines
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        original_lines = [line + '\n' for line in original_content.splitlines()]
        
        # Cache the complete original file content in linecache
        linecache.cache[virtual_filename] = (
            len(original_content),
            None,  # mtime
            original_lines,  # Complete original file with newline characters
            virtual_filename
        )
    except (OSError, IOError):
        # Fallback: use main_code if original file can't be read
        lines_with_newlines = [line + '\n' for line in code_lines]
        linecache.cache[virtual_filename] = (
            len(code),
            None,  # mtime
            lines_with_newlines,
            virtual_filename
        )
    
    # Find all function and class definitions
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            obj_name = node.name
            if obj_name in namespace:
                obj = namespace[obj_name]
                
                # Set source information for the object
                _set_source_info(obj, node, virtual_filename, code_lines, line_offset)
                
                # If it's a class, also process its methods
                if isinstance(node, ast.ClassDef) and inspect.isclass(obj):
                    _add_method_source_info(obj, node, virtual_filename, code_lines, line_offset)

def _set_source_info(obj: Any, node: ast.AST, filename: str, code_lines: list, line_offset: int) -> None:
    """
    Set source information for a function or class object.
    
    Args:
        obj: The function or class object
        node: The AST node representing the definition
        filename: The virtual filename to use
        code_lines: The source code lines
        line_offset: The line offset to add to get original file line numbers
    """
    # Get the source lines for this object (relative to extracted main code)
    start_line = node.lineno - 1  # Convert to 0-based
    end_line = getattr(node, 'end_lineno', len(code_lines)) - 1
    
    # Create the source code string
    obj_source = '\n'.join(code_lines[start_line:end_line + 1])
    
    # Store the source directly as a custom attribute
    obj.__source__ = obj_source
    
    # Set __module__ to our virtual filename so inspect can find it
    obj.__module__ = filename
    
    # For functions, update the code object with original file line number
    if hasattr(obj, '__code__') and callable(obj) and not inspect.isclass(obj):
        old_code = obj.__code__
        # Calculate the actual line number in the original file
        original_line_number = line_offset + node.lineno - 1
        new_code = old_code.replace(
            co_filename=filename,
            co_firstlineno=original_line_number
        )
        
        # Update the function's code object
        if hasattr(obj, '__func__'):
            # For methods
            obj.__func__.__code__ = new_code
        else:
            # For functions
            obj.__code__ = new_code
    
    # For classes, we need special handling
    elif inspect.isclass(obj):
        # Set the class's __file__ attribute
        obj.__file__ = filename
        # Set line number information
        if hasattr(obj, '__qualname__'):
            obj.__qualname__ = obj.__name__

def _add_method_source_info(cls: type, class_node: ast.ClassDef, filename: str, code_lines: list, line_offset: int) -> None:
    """
    Add source information to methods of a class.
    
    Args:
        cls: The class object
        class_node: The AST node representing the class definition
        filename: The virtual filename to use
        code_lines: The source code lines
        line_offset: The line offset to apply to the source code
    """
    # Find all method definitions in the class
    for node in class_node.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method_name = node.name
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                
                # Handle different types of methods
                if hasattr(method, '__func__'):
                    # Instance method
                    _set_method_source_info(method.__func__, node, filename, code_lines, line_offset)
                elif callable(method) and hasattr(method, '__code__'):
                    # Static method or class method
                    _set_method_source_info(method, node, filename, code_lines, line_offset)

def _set_method_source_info(method_obj: Any, node: ast.AST, filename: str, code_lines: list, line_offset: int) -> None:
    """
    Set source information for a method object.
    
    Args:
        method_obj: The method object
        node: The AST node representing the method definition
        filename: The virtual filename to use
        code_lines: The source code lines
        line_offset: The line offset to add to get original file line numbers
    """
    # Get the source lines for this method (relative to extracted main code)
    start_line = node.lineno - 1  # Convert to 0-based
    end_line = getattr(node, 'end_lineno', len(code_lines)) - 1
    
    # Create the source code string
    method_source = '\n'.join(code_lines[start_line:end_line + 1])
    
    # Store the source directly as a custom attribute
    method_obj.__source__ = method_source
    
    # Set __module__ to our virtual filename
    method_obj.__module__ = filename
    
    # Update the method's code object with original file line number
    if hasattr(method_obj, '__code__'):
        old_code = method_obj.__code__
        # Calculate the actual line number in the original file
        original_line_number = line_offset + node.lineno - 1
        new_code = old_code.replace(
            co_filename=filename,
            co_firstlineno=original_line_number
        )
        method_obj.__code__ = new_code

def load_main(
        somemodule: Union[str, types.ModuleType], 
        code_filter: Optional[Callable[[str], str]] = None,
        locals: Optional[Dict[str, Any]] = None,
        globals: Optional[Dict[str, Any]] = None,
        add_code_object: bool = False,
    ) -> Dict[str, Any]:
    """
    Load and execute the code from `if __name__ == "__main__"` block of a module.
    
    This function allows you to execute the code that would normally only run when
    a module is executed directly (i.e., code within if __name__ == "__main__" block).
    
    IMPORTANT: Users are responsible for providing the correct locals and globals
    environment. Typically, you should import the module first to make its functions
    and variables available.
    
    NOTE: This function does NOT automatically execute the module code. This is by
    design because modules often use relative imports (e.g., from .submodule import foo),
    making automatic module execution non-trivial and error-prone. The user should
    handle the module import process properly according to their package structure.
    
    Args:
        somemodule: Either a module object or a file path string
        code_filter: Optional function to modify the code before execution
        locals: Local variables for code execution
        globals: Global variables for code execution (should contain module's functions/vars)
        add_code_object: If True, add source code information to functions and classes
                        so that inspect.getsource() can work with them
        
    Returns:
        Dictionary containing the locals after execution
        
    Example:
    ::

        # Typical usage pattern:
        import somemodule
        from somemodule import *
        
        # Execute the __main__ block with proper environment
        main_vars = load_main(somemodule, locals=locals(), globals=globals())
        
        # With source code support for inspect.getsource():
        main_vars = load_main(somemodule, add_code_object=True, globals=globals())
        func = main_vars['some_function']
        source = inspect.getsource(func)  # This will work!
        
        # Or with a file path:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mymodule", "path/to/module.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Prepare globals with module's functions and variables
        module_globals = globals().copy()
        module_globals.update(module.__dict__)
        
        main_vars = load_main("path/to/module.py", globals=module_globals)
    """
    # Get the file path from module
    if isinstance(somemodule, types.ModuleType):
        if not hasattr(somemodule, '__file__') or somemodule.__file__ is None:
            raise ValueError("Module does not have a __file__ attribute")
        file_path = somemodule.__file__
    elif isinstance(somemodule, str):
        file_path = somemodule
    else:
        raise TypeError("somemodule must be a module object or file path string")
    
    # Ensure the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # Parse the AST
    try:
        tree = ast.parse(file_content)
    except SyntaxError as e:
        raise SyntaxError(f"Failed to parse {file_path}: {e}")
    
    # Find the if __name__ == "__main__" block
    main_result = _extract_main_block(tree, file_content)
    
    if main_result is None:
        raise ValueError(f"No 'if __name__ == \"__main__\"' block found in {file_path}")
    
    main_code, main_start_line = main_result
    
    # Apply code filter if provided
    if code_filter is not None:
        main_code = code_filter(main_code)
    
    # Prepare execution environment
    exec_locals = locals.copy() if locals else {}
    exec_globals = globals.copy() if globals else {}
    
    # Execute the main code
    try:
        exec(main_code, exec_globals, exec_locals)
    except Exception as e:
        raise RuntimeError(f"Failed to execute main code from {file_path}: {e}")
    
    # Fix closure issue: merge exec_locals into exec_globals so that 
    # functions defined in main block can access dynamically imported variables
    exec_globals.update(exec_locals)
    
    # Update __globals__ for all functions in exec_locals to include the merged globals
    for name, obj in exec_locals.items():
        if callable(obj) and hasattr(obj, '__globals__'):
            # Update function's __globals__ to include merged environment
            obj.__globals__.update(exec_globals)
    
    # Add source code information for inspect.getsource() if requested
    if add_code_object:
        _add_source_info_to_objects(main_code, exec_locals, original_file=file_path, line_offset=main_start_line)
    
    return exec_locals

if __name__ == "__main__":
    import tempfile
    from textwrap import dedent

    class TestExecTool(unittest.TestCase):
        """ Test case by load_main
            -----------------------------

            In the AI era, large language models have dramatically improved our coding efficiency.
            Our use of LLMs for coding has evolved through three stages:
            
            * **Ask**: Using web interfaces or APIs, we submit requirements or code snippets to LLMs and receive code output
            * **Compose**: LLMs gain the ability to view and modify local code, but interaction remains in a question-and-answer format  
            * **Agent**: LLMs not only have the ability to view and modify local code, but also possess local shell privileges, enabling them to execute any shell commands
            
            Agent-based coding represents a qualitative transformation in programming.
            Previously, we might have found LLMs occasionally unreliable or cumbersome to use because
            we had to constantly review their output for correctness.
            However, in Agent mode, specifically for program development scenarios,
            we can guide LLMs to write unit tests and instruct them to repeatedly
            execute these tests while modifying the program.
            Unit tests can, to a significant extent, replace human oversight in iterative reviews,
            dramatically improving the efficiency of AI code iteration.
            
            In Agent mode, we can attempt to decouple code logic by decomposing it into many small modules.
            Each module contains only functions and classes with specific functionality, structured as follows::
            
                # some module.py
                import something
                
                class SomeClass:
                    '''detailed document'''
                    pass
                
                def someFunc():
                    '''detailed document'''
                    pass
                
                SOME_CONSTANT = ''
                
                if __name__ == "__main__":
                    import unittest
                    class TestCase(unittest.TestCase):
                        pass
                    unittest.main()
            
            This structure encompasses complete program implementation, comprehensive documentation, and full unit testing.
            Agents can focus on a single file, continuously testing, modifying,
            and refining it until achieving high-quality, fully-tested code.
            
            However, this structure presents a challenge: 
            we cannot use other methods like pytest to discover and run the TestCases contained within for batch testing.
            Our example below will use some helper functions, employing Unittest2doc to load, run, and document the test cases
            in the ``if __name__ == "__main__"`` block.

            In normal case, you really should follow other CI/CD guidelines to

            * put code under ``src/package/module/to/code.py`` (the module part)
            * put test code under ``tests/somewhere/to/test_code.py`` (all the test cases and a possible one line ``unittest.main()`` code in the ``if __name__ == "__main__"`` block)
            In this way, pytest can discover and run the test cases, this is the standard way to do unit testing.

            But here we CAN run the test cases in the ``if __name__ == "__main__"`` block, using the following code::

                from pathlib import Path
                import unittest2doc
                from unittest2doc import Unittest2Doc
                from unittest2doc.utils.exec_tool import filter_after_comment_by, load_module, collect_module_attr, load_main

                if __name__ == "__main__":
                    test_module = "unittest2doc.utils.exec_tool"
                    module = load_module(test_module)
                    module_globals = collect_module_attr(module, all=True)

                    main = load_main(
                             module,
                             code_filter=filter_after_comment_by("Run unittests"),
                             globals=module_globals,
                             add_code_object=True,
                           )

                    t = unittest2doc.Unittest2Doc(
                        testcase=main['TestExecTool'](),
                        name='unittest2doc.utils.exec_tool',
                        ref=':mod:`unittest2doc.utils.exec_tool`',
                        doc_root=Path(__file__).absolute().parent.parent / 'sphinx-docs/source/unittests',
                        open_input=False,
                    )
                    t.generate_docs()
        """

        # Test filter_after_comment
        def test_filter_after_comment_string_match(self):
            """Test filter_after_comment with string matching."""
            code = dedent('''
                def func1():
                    return "before"
                
                def func2():
                    return "middle"
                
                # REMOVE: everything after this comment
                def func3():
                    return "after"
                
                class AfterClass:
                    pass
            ''').strip()
            
            result = filter_after_comment(code, "REMOVE: everything after this comment")
            
            self.assertIn('def func1():', result)
            self.assertIn('def func2():', result)
            self.assertNotIn('def func3():', result)
            self.assertNotIn('class AfterClass:', result)
            self.assertNotIn('REMOVE:', result)
        def test_filter_after_comment_regex_match(self):
            """Test filter_after_comment with regex pattern."""
            code = dedent('''
                import os
                import sys
                
                def main():
                    print("Hello")
                
                # TODO: implement feature xyz
                def unfinished_function():
                    pass
                
                # NOTE: this is important
                def another_function():
                    pass
            ''').strip()
            
            # Use regex to match any TODO comment
            pattern = re.compile(r'TODO:.*')
            result = filter_after_comment(code, pattern)
            
            self.assertIn('def main():', result)
            self.assertNotIn('def unfinished_function():', result)
            self.assertNotIn('def another_function():', result)
            self.assertNotIn('TODO:', result)
        def test_filter_after_comment_no_match(self):
            """Test filter_after_comment when comment is not found."""
            code = dedent('''
                def func1():
                    return "test"
                
                # Some other comment
                def func2():
                    return "test2"
            ''').strip()
            
            result = filter_after_comment(code, "NONEXISTENT COMMENT")
            
            # Should return original code unchanged
            self.assertEqual(result, code)
        def test_filter_after_comment_multiple_matches(self):
            """Test filter_after_comment with multiple matching comments."""
            code = dedent('''
                def func1():
                    return 1
                
                # STOP here first time
                def func2():
                    return 2
                
                # STOP here second time  
                def func3():
                    return 3
            ''').strip()
            
            result = filter_after_comment(code, "STOP")
            
            # Should stop at the first match
            self.assertIn('def func1():', result)
            self.assertNotIn('def func2():', result)
            self.assertNotIn('def func3():', result)
            self.assertNotIn('STOP here first time', result)
        def test_filter_after_comment_empty_code(self):
            """Test filter_after_comment with empty code."""
            result = filter_after_comment("", "any comment")
            self.assertEqual(result, "")
            
            result = filter_after_comment("   ", "any comment")
            self.assertEqual(result, "   ")
        def test_filter_after_comment_comment_at_end(self):
            """Test filter_after_comment when comment is at the last line."""
            code = dedent('''
                def func():
                    return "test"
                
                x = 1
                # END: this is the last line
            ''').strip()
            
            result = filter_after_comment(code, "END: this is the last line")
            
            self.assertIn('def func():', result)
            self.assertIn('x = 1', result)
            self.assertNotIn('END:', result)
        def test_filter_after_comment_regex_complex(self):
            """Test filter_after_comment with complex regex."""
            code = dedent('''
                import math
                
                def calculate():
                    return math.pi
                
                # Version: 1.2.3 - remove from here
                def version_specific():
                    pass
                
                # Version: 2.0.0 - and this too
                def newer_version():
                    pass
            ''').strip()
            
            # Match any version comment
            pattern = re.compile(r'Version:\s+\d+\.\d+\.\d+')
            result = filter_after_comment(code, pattern)
            
            self.assertIn('def calculate():', result)
            self.assertNotIn('def version_specific():', result)
            self.assertNotIn('def newer_version():', result)
            self.assertNotIn('Version:', result)
        def test_filter_after_comment_invalid_pattern_type(self):
            """Test filter_after_comment with invalid pattern type."""
            code = dedent('''
                def func():
                    return "test"
                
                # Some comment here
                def another_func():
                    pass
            ''').strip()
            
            with self.assertRaises(TypeError):
                filter_after_comment(code, 123)  # Invalid type

        # Test load_module
        def test_load_module_with_module_name(self):
            """Test load_module with standard module name."""
            # Test with built-in module
            os_module = load_module("os")
            import os
            self.assertEqual(os_module, os)
            
            # Test with sub-module
            path_module = load_module("os.path")
            import os.path
            self.assertEqual(path_module, os.path)
        def test_load_module_with_file_path(self):
            """Test load_module with file path."""
            test_content = dedent('''
                def test_function():
                    return "from file path"
                
                TEST_CONSTANT = 42
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                resolved_module = load_module(f.name)
                
                self.assertTrue(hasattr(resolved_module, 'test_function'))
                self.assertTrue(hasattr(resolved_module, 'TEST_CONSTANT'))
                self.assertEqual(resolved_module.test_function(), "from file path")
                self.assertEqual(resolved_module.TEST_CONSTANT, 42)
        def test_load_module_with_module_object(self):
            """Test load_module with existing module object."""
            import math
            resolved_module = load_module(math)
            self.assertEqual(resolved_module, math)
        def test_load_module_errors(self):
            """Test load_module error cases."""
            # Non-existent module
            with self.assertRaises(ImportError):
                load_module("non_existent_module_12345")
            
            # Non-existent file path  
            with self.assertRaises(FileNotFoundError):
                load_module("/non/existent/path.py")
            
            # Invalid type
            with self.assertRaises(TypeError):
                load_module(123)

        # Test collect_module_attr
        def test_collect_module_attr_all(self):
            """Test collect_module_attr with all=True."""
            test_content = dedent('''
                def test_func():
                    return "test"
                
                TEST_VAR = 42
                TEST_STR = "hello"
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                attrs = collect_module_attr(f.name, all=True)
                
                # Should contain all module attributes
                self.assertIn('test_func', attrs)
                self.assertIn('TEST_VAR', attrs)
                self.assertIn('TEST_STR', attrs)
                self.assertEqual(attrs['TEST_VAR'], 42)
                self.assertEqual(attrs['test_func'](), 'test')
                self.assertEqual(attrs['TEST_STR'], "hello")
        def test_collect_module_attr_names_dict(self):
            """Test collect_module_attr with names as dict (source->target mapping)."""
            import math
            
            # Test direct name mapping: source_name -> target_name
            attrs = collect_module_attr(math, names={'pi': 'PI', 'sqrt': 'SQRT'})
            
            self.assertIn('PI', attrs)
            self.assertIn('SQRT', attrs)
            self.assertEqual(attrs['PI'], math.pi)
            self.assertEqual(attrs['SQRT'], math.sqrt)
            # Original names should not be present
            self.assertNotIn('pi', attrs)
            self.assertNotIn('sqrt', attrs)
        def test_collect_module_attr_names_list(self):
            """Test collect_module_attr with names as list (original names)."""
            import math
            
            # Test list format uses original names
            attrs = collect_module_attr(math, names=['pi', 'sqrt'])
            
            self.assertIn('pi', attrs)
            self.assertIn('sqrt', attrs)
            self.assertEqual(attrs['pi'], math.pi)
            self.assertEqual(attrs['sqrt'], math.sqrt)
        def test_collect_module_attr_names_regex_dict(self):
            """Test collect_module_attr with regex patterns in dict."""
            import math
            
            # Test regex pattern in dict - should use original names (value is ignored)
            attrs = collect_module_attr(
                math, 
                names={re.compile(r'^(sin|cos|tan)$'): 'ignored_value'}
            )
            
            # With regex in dict, matched attributes use original names
            self.assertIn('sin', attrs)
            self.assertIn('cos', attrs)
            self.assertIn('tan', attrs)
            self.assertEqual(attrs['sin'], math.sin)
            self.assertEqual(attrs['cos'], math.cos)
            self.assertEqual(attrs['tan'], math.tan)
        def test_collect_module_attr_names_regex_list(self):
            """Test collect_module_attr with regex patterns in list."""
            import math
            
            # Test regex pattern in list - should use original names
            attrs = collect_module_attr(
                math, 
                names=[re.compile(r'^(sin|cos|tan)$')]
            )
            
            # With regex in list, matched attributes use original names
            self.assertIn('sin', attrs)
            self.assertIn('cos', attrs)
            self.assertIn('tan', attrs)
            self.assertEqual(attrs['sin'], math.sin)
            self.assertEqual(attrs['cos'], math.cos)
            self.assertEqual(attrs['tan'], math.tan)
        def test_collect_module_attr_names_mapping_dict(self):
            """Test collect_module_attr with names_mapping as dict."""
            import math
            
            # First collect, then remap
            attrs = collect_module_attr(
                math, 
                names=['pi', 'sqrt'],
                names_mapping={'pi': 'PI_VALUE', 'sqrt': 'SQRT_FUNC'}
            )
            
            self.assertIn('PI_VALUE', attrs)
            self.assertIn('SQRT_FUNC', attrs)
            self.assertEqual(attrs['PI_VALUE'], math.pi)
            self.assertEqual(attrs['SQRT_FUNC'], math.sqrt)
            # Original names should be removed after mapping
            self.assertNotIn('pi', attrs)
            self.assertNotIn('sqrt', attrs)
        def test_collect_module_attr_names_mapping_callable(self):
            """Test collect_module_attr with names_mapping as callable."""
            import math
            
            # Define a mapping function
            def to_upper_mapping(name):
                return name.upper()
            
            attrs = collect_module_attr(
                math, 
                names=['pi', 'sqrt'],
                names_mapping=to_upper_mapping
            )
            
            self.assertIn('PI', attrs)
            self.assertIn('SQRT', attrs)
            self.assertEqual(attrs['PI'], math.pi)
            self.assertEqual(attrs['SQRT'], math.sqrt)
        def test_collect_module_attr_by_classes(self):
            """Test collect_module_attr with class filtering."""
            test_content = dedent('''
                test_int = 42
                test_str = "hello"
                test_float = 3.14
                test_list = [1, 2, 3]
                
                class TestClass:
                    pass
                
                def test_func():
                    pass
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                attrs = collect_module_attr(f.name, classes=[int, str])
                
                self.assertIn('test_int', attrs)
                self.assertIn('test_str', attrs)
                self.assertNotIn('test_float', attrs)  # float not in classes list
                self.assertNotIn('test_list', attrs)   # list not in classes list
                self.assertEqual(attrs['test_int'], 42)
                self.assertEqual(attrs['test_str'], "hello")
        
        def test_collect_module_attr_all_classes(self):
            """Test collect_module_attr with classes=True to collect all classes."""
            test_content = dedent('''
                class FirstClass:
                    def method1(self):
                        return "first"
                
                class SecondClass:
                    def method2(self):
                        return "second"
                
                class _PrivateClass:  # Should be skipped
                    pass
                
                # These should not be collected
                test_int = 42
                test_str = "hello"
                
                def test_func():
                    pass
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                attrs = collect_module_attr(f.name, classes=True)
                
                # Should contain all public classes
                self.assertIn('FirstClass', attrs)
                self.assertIn('SecondClass', attrs)
                
                # Should not contain private class (starts with _)
                self.assertNotIn('_PrivateClass', attrs)
                
                # Should not contain non-class attributes
                self.assertNotIn('test_int', attrs)
                self.assertNotIn('test_str', attrs)
                self.assertNotIn('test_func', attrs)
                
                # Verify they are actually classes
                self.assertTrue(inspect.isclass(attrs['FirstClass']))
                self.assertTrue(inspect.isclass(attrs['SecondClass']))
                
                # Test instantiation
                first_instance = attrs['FirstClass']()
                second_instance = attrs['SecondClass']()
                self.assertEqual(first_instance.method1(), "first")
                self.assertEqual(second_instance.method2(), "second")
        def test_collect_module_attr_functions(self):
            """Test collect_module_attr with function collection."""
            test_content = dedent('''
                def function_one():
                    return 1
                
                def function_two():
                    return 2
                
                class NotAFunction:
                    pass
                
                variable = "not a function"
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                attrs = collect_module_attr(f.name, functions=True)
                
                self.assertIn('function_one', attrs)
                self.assertIn('function_two', attrs)
                self.assertNotIn('NotAFunction', attrs)  # Class, not function
                self.assertNotIn('variable', attrs)      # Variable, not function
                
                # Test that functions are callable
                self.assertEqual(attrs['function_one'](), 1)
                self.assertEqual(attrs['function_two'](), 2)
        def test_collect_module_attr_combined(self):
            """Test collect_module_attr with multiple criteria and mapping."""
            test_content = dedent('''
                def helper_func():
                    return "helper"
                
                def main_func():
                    return "main"
                
                CONSTANT = 100
                message = "hello world"
                
                class MyClass:
                    pass
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                attrs = collect_module_attr(
                    f.name,
                    names={'message': 'MSG', 'CONSTANT': 'CONST'},  # source->target mapping
                    classes=[str, int],
                    functions=True,
                    names_mapping={'helper_func': 'HELPER', 'main_func': 'MAIN'}
                )
                
                # Check remapped names from names dict
                self.assertIn('MSG', attrs)
                self.assertIn('CONST', attrs)
                self.assertEqual(attrs['MSG'], "hello world")
                self.assertEqual(attrs['CONST'], 100)
                
                # Check classes (should also include the ones from names)
                self.assertIn('message', attrs)  # str instance from classes
                self.assertIn('CONSTANT', attrs)  # int instance from classes
                
                # Check functions with mapping
                self.assertIn('HELPER', attrs)  # mapped from helper_func
                self.assertIn('MAIN', attrs)    # mapped from main_func
                self.assertNotIn('helper_func', attrs)  # original should be removed
                self.assertNotIn('main_func', attrs)    # original should be removed
                
                # Check that class is not included
                self.assertNotIn('MyClass', attrs)
        def test_collect_module_attr_errors(self):
            """Test collect_module_attr error cases."""
            import math
            
            # Invalid names type
            with self.assertRaises(TypeError):
                collect_module_attr(math, names="invalid_string")
            
            # Invalid pattern type in dict (key should be str or re.Pattern)
            with self.assertRaises(TypeError):
                collect_module_attr(math, names={123: 'target_name'})
            
            # Invalid pattern type in list
            with self.assertRaises(TypeError):
                collect_module_attr(math, names=[123])
        
        # Test load_main
        def test_load_main_basic(self):
            """Test basic load_main functionality using helper functions."""
            test_content = dedent('''
                def greet(name):
                    return f"Hello, {name}!"
                
                value = 100
                
                if __name__ == "__main__":
                    message = greet("World")
                    doubled = value * 2
                    test_result = "success"
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)
                
                result = load_main(f.name, globals=test_globals)
                
                self.assertIn('message', result)
                self.assertIn('doubled', result) 
                self.assertIn('test_result', result)
                self.assertEqual(result['message'], 'Hello, World!')
                self.assertEqual(result['doubled'], 200)
                self.assertEqual(result['test_result'], 'success')
        def test_load_main_with_import(self):
            """Test basic load_main functionality using helper functions."""
            test_content = dedent('''
                if __name__ == "__main__":
                    import numpy as np
                    from textwrap import dedent
                    def test_func():
                        return np.array([1, 2, 3])

            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)
                
                result = load_main(f.name, globals=test_globals)
                
                self.assertIn('np', result)
                self.assertIn('dedent', result)
                self.assertIn('test_func', result)
                import numpy as np
                # Use numpy array comparison instead of assertEqual to avoid ambiguous truth value
                np.testing.assert_array_equal(result['test_func'](), np.array([1, 2, 3]))
        def test_load_main_with_classes(self):
            """Test load_main with class definitions using helper functions."""
            test_content = dedent('''
                class Calculator:
                    def __init__(self, name):
                        self.name = name
                    
                    def add(self, a, b):
                        return a + b
                
                DEFAULT_NAME = "MyCalc"
                
                if __name__ == "__main__":
                    calc = Calculator(DEFAULT_NAME)
                    result = calc.add(10, 20)
                    calc_name = calc.name + "_used"
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)
                
                result = load_main(f.name, globals=test_globals)
                
                self.assertIn('calc', result)
                self.assertIn('result', result)
                self.assertIn('calc_name', result)
                self.assertEqual(result['result'], 30)
                self.assertEqual(result['calc_name'], 'MyCalc_used')
                self.assertIsInstance(result['calc'], module.Calculator)
        def test_load_main_with_selective_collection(self):
            """Test load_main with selective attribute collection using helper functions."""
            test_content = dedent('''
                def greet(name):
                    return f"Hello, {name}!"
                
                def calculate(a, b):
                    return a * b
                
                BASE_VALUE = 10
                SECRET = "should not be visible"
                
                if __name__ == "__main__":
                    greeting = greet("World")
                    result = calculate(BASE_VALUE, 5)
                    total = BASE_VALUE + result
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions to selectively collect
                module = load_module(f.name)
                test_globals = collect_module_attr(
                    module,
                    names=['BASE_VALUE'],  # use list format for original names
                    functions=True
                )

                self.assertNotIn('SECRET', test_globals)
                
                result = load_main(f.name, globals=test_globals)
                
                self.assertIn('greeting', result)
                self.assertIn('result', result)
                self.assertIn('total', result)
                self.assertEqual(result['greeting'], 'Hello, World!')
                self.assertEqual(result['result'], 50)  # 10 * 5
                self.assertEqual(result['total'], 60)   # 10 + 50
        def test_load_main_with_custom_locals(self):
            """Test load_main with custom locals using helper functions."""
            test_content = dedent('''
                def multiply(a, b):
                    return a * b
                
                BASE_VALUE = 5
                
                if __name__ == "__main__":
                    result = multiply(BASE_VALUE, existing_multiplier)
                    final_value = result + existing_offset
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions with specific classes and functions
                module = load_module(f.name)
                test_globals = collect_module_attr(module, functions=True, classes=[int])
                
                custom_locals = {
                    'existing_multiplier': 3,
                    'existing_offset': 10
                }
                
                result = load_main(f.name, locals=custom_locals, globals=test_globals)
                
                self.assertIn('existing_multiplier', result)
                self.assertIn('existing_offset', result)
                self.assertIn('result', result)
                self.assertIn('final_value', result)
                self.assertEqual(result['result'], 15)  # 5 * 3
                self.assertEqual(result['final_value'], 25)  # 15 + 10
        def test_load_main_with_code_filter(self):
            """Test load_main with code filter using helper functions."""
            test_content = dedent('''
                def process_data(data):
                    return data.upper()
                
                DEFAULT_DATA = "hello world"
                
                if __name__ == "__main__":
                    processed = process_data(DEFAULT_DATA)
                    length = len(processed)
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)
                
                def add_prefix_filter(code: str) -> str:
                    return f"prefix_var = 'code_filtered'\n{code}"
                
                result = load_main(f.name, code_filter=add_prefix_filter, globals=test_globals)
                
                self.assertIn('prefix_var', result)
                self.assertIn('processed', result)
                self.assertIn('length', result)
                self.assertEqual(result['prefix_var'], 'code_filtered')
                self.assertEqual(result['processed'], 'HELLO WORLD')
                self.assertEqual(result['length'], 11)
        def test_load_main_with_name_mapping(self):
            """Test load_main with name mapping using helper functions."""
            test_content = dedent('''
                def calculate_area(radius):
                    import math
                    return math.pi * radius ** 2
                
                def calculate_volume(radius, height):
                    import math
                    return math.pi * radius ** 2 * height
                
                DEFAULT_RADIUS = 5
                DEFAULT_HEIGHT = 10
                
                if __name__ == "__main__":
                    area = calculate_area(DEFAULT_RADIUS)
                    volume = calculate_volume(DEFAULT_RADIUS, DEFAULT_HEIGHT)
                    summary = f"Area: {area:.2f}, Volume: {volume:.2f}"
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions with selective collection (without name mapping to avoid conflicts)
                module = load_module(f.name)
                test_globals = collect_module_attr(
                    module,
                    functions=True,  # Get all functions with original names
                    classes=[int]    # Get integer constants
                )
                
                result = load_main(f.name, globals=test_globals)
                
                self.assertIn('area', result)
                self.assertIn('volume', result)
                self.assertIn('summary', result)
                self.assertAlmostEqual(result['area'], 78.53981633974483, places=5)
                self.assertAlmostEqual(result['volume'], 785.3981633974483, places=4)
        def test_load_main_complex_main_block(self):
            """Test load_main with complex main block using helper functions."""
            test_content = dedent('''
                def fibonacci(n):
                    if n <= 1:
                        return n
                    return fibonacci(n-1) + fibonacci(n-2)
                
                def is_even(num):
                    return num % 2 == 0
                
                LIMIT = 8
                
                if __name__ == "__main__":
                    fib_numbers = []
                    for i in range(LIMIT):
                        fib_numbers.append(fibonacci(i))
                    
                    even_fibs = [num for num in fib_numbers if is_even(num)]
                    
                    if len(even_fibs) > 0:
                        max_even_fib = max(even_fibs)
                        result_status = "found_evens"
                    else:
                        max_even_fib = 0
                        result_status = "no_evens"
                    
                    total_sum = sum(fib_numbers)
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)
                
                result = load_main(f.name, globals=test_globals)
                
                self.assertIn('fib_numbers', result)
                self.assertIn('even_fibs', result)
                self.assertIn('max_even_fib', result)
                self.assertIn('result_status', result)
                self.assertIn('total_sum', result)
                
                # Check fibonacci sequence: [0, 1, 1, 2, 3, 5, 8, 13]
                expected_fibs = [0, 1, 1, 2, 3, 5, 8, 13]
                self.assertEqual(result['fib_numbers'], expected_fibs)
                self.assertEqual(result['even_fibs'], [0, 2, 8])
                self.assertEqual(result['max_even_fib'], 8)
                self.assertEqual(result['result_status'], 'found_evens')
                self.assertEqual(result['total_sum'], 33)
        def test_load_main_with_module_object(self):
            """Test load_main with actual module object using helper functions."""
            test_content = dedent('''
                def get_message():
                    return "from module object"
                
                CONFIG_VALUE = "test_config"
                
                if __name__ == "__main__":
                    message = get_message()
                    config = CONFIG_VALUE.upper()
                    combined = f"{message}_{config}"
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)
                
                # Test with module object instead of file path
                result = load_main(module, globals=test_globals)
                
                self.assertIn('message', result)
                self.assertIn('config', result)
                self.assertIn('combined', result)
                self.assertEqual(result['message'], 'from module object')
                self.assertEqual(result['config'], 'TEST_CONFIG')
                self.assertEqual(result['combined'], 'from module object_TEST_CONFIG')
        def test_load_main_integration_complex(self):
            """Test complex integration example with all features using helper functions."""
            test_content = dedent('''
                import math
                
                def fibonacci(n):
                    if n <= 1:
                        return n
                    return fibonacci(n-1) + fibonacci(n-2)
                
                def is_prime(num):
                    if num < 2:
                        return False
                    for i in range(2, int(math.sqrt(num)) + 1):
                        if num % i == 0:
                            return False
                    return True
                
                PI_APPROX = 3.14
                LIMIT = 10
                
                if __name__ == "__main__":
                    # Calculate fibonacci numbers
                    fib_numbers = [fibonacci(i) for i in range(LIMIT)]
                    
                    # Find prime fibonacci numbers
                    prime_fibs = [num for num in fib_numbers if is_prime(num)]
                    
                    # Use math module
                    circle_area = math.pi * (5 ** 2)
                    pi_accuracy = abs(math.pi - PI_APPROX) < 0.01
                    
                    # Summary
                    result_summary = {
                        'fibonacci_count': len(fib_numbers),
                        'prime_fibonacci': prime_fibs,
                        'circle_area': round(circle_area, 2),
                        'pi_is_accurate': pi_accuracy
                    }
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions - need to include math module
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)  # Include everything including imported modules
                
                result = load_main(f.name, globals=test_globals)
                
                # Verify results
                self.assertIn('fib_numbers', result)
                self.assertIn('prime_fibs', result)
                self.assertIn('circle_area', result)
                self.assertIn('result_summary', result)
                
                expected_fibs = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
                self.assertEqual(result['fib_numbers'], expected_fibs)
                
                # Prime fibonacci numbers up to 34: [2, 3, 5, 13]
                self.assertEqual(result['prime_fibs'], [2, 3, 5, 13])
                
                summary = result['result_summary']
                self.assertEqual(summary['fibonacci_count'], 10)
                self.assertEqual(summary['prime_fibonacci'], [2, 3, 5, 13])
                self.assertEqual(summary['circle_area'], 78.54)
                self.assertTrue(summary['pi_is_accurate'])
        def test_load_main_error_cases(self):
            """Test load_main error cases."""
            # Non-existent file
            with self.assertRaises(FileNotFoundError):
                load_main("nonexistent_file_12345.py")
            
            # File with no main block
            test_content = dedent('''
                def function():
                    return "no main block"
                
                variable = 42
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                with self.assertRaises(ValueError) as cm:
                    load_main(f.name)
                self.assertIn("No 'if __name__ == \"__main__\"' block found", str(cm.exception))
            
            # Syntax error
            test_content_broken = dedent('''
                def broken_function(
                    # Missing closing parenthesis
                
                if __name__ == "__main__":
                    result = "never reached"
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content_broken)
                f.flush()
                
                with self.assertRaises(SyntaxError):
                    load_main(f.name)
        
        # Test load_main with add_code_object=True for inspect.getsource() support
        def test_load_main_with_add_code_object(self):
            """Test load_main with add_code_object=True for inspect.getsource() support."""
            test_content = dedent('''
                def helper_function(x):
                    """A helper function."""
                    return x * 2
                
                BASE_VALUE = 10
                
                if __name__ == "__main__":
                    def main_function(y):
                        """Function defined in main block."""
                        return helper_function(y) + BASE_VALUE
                    
                    class MainClass:
                        """Class defined in main block."""
                        def __init__(self, value):
                            self.value = value
                        
                        def get_value(self):
                            return self.value * 2
                    
                    result = main_function(5)
                    instance = MainClass(10)
                    class_result = instance.get_value()
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)
                
                # Test with add_code_object=True
                result = load_main(f.name, add_code_object=True, globals=test_globals)
                
                # Verify objects exist
                self.assertIn('main_function', result)
                self.assertIn('MainClass', result)
                self.assertIn('result', result)
                self.assertIn('instance', result)
                self.assertIn('class_result', result)
                
                # Test function
                main_func = result['main_function']
                self.assertEqual(main_func(5), 20)  # 5*2 + 10 = 20
                self.assertEqual(result['result'], 20)
                
                # Test class
                main_class = result['MainClass']
                instance = main_class(15)
                self.assertEqual(instance.get_value(), 30)  # 15 * 2 = 30
                self.assertEqual(result['class_result'], 20)  # 10 * 2 = 20
                
                # Test comprehensive source code information for all objects
                print("\n=== Detailed source code info test ===")
                
                # Test all functions and classes
                test_objects = {
                    'main_function': main_func,
                    'MainClass': main_class
                }
                
                for obj_name, obj in test_objects.items():
                    print(f"\n--- Testing {obj_name} ---")
                    
                    if inspect.isclass(obj):
                        print(f"Type: class")
                        # Test class source
                        self.assertTrue(hasattr(obj, '__source__'), f"{obj_name} missing __source__ attribute")
                        class_source = obj.__source__
                        self.assertIn(f'class {obj.__name__}:', class_source)
                        print(f"✓ Class source length: {len(class_source)} chars")
                        print(f"✓ Virtual file: {getattr(obj, '__module__', 'N/A')}")
                        print(f"✓ File attribute: {getattr(obj, '__file__', 'N/A')}")
                        
                        # Test all methods in the class
                        for method_name in dir(obj):
                            method = getattr(obj, method_name)
                            # Check if it's a method we want to test
                            if callable(method):
                                # Include special methods like __init__ and user-defined methods
                                should_test = (
                                    method_name in ['__init__', 'method', 'get_value', 'static_method'] or
                                    (not method_name.startswith('__') and not method_name.startswith('_'))
                                )
                                
                                if should_test:
                                    print(f"  Testing method: {method_name}")
                                    # Check if it's an instance method with __func__
                                    if hasattr(method, '__func__'):
                                        try:
                                            method_source = inspect.getsource(method)
                                            print(f"    ✓ inspect.getsource() success: {len(method_source)} chars")
                                            if hasattr(method.__func__, '__code__'):
                                                code = method.__func__.__code__
                                                print(f"    ✓ Filename: {code.co_filename}")
                                                print(f"    ✓ First line: {code.co_firstlineno}")
                                            print("===source===")
                                            print(method_source)
                                            print("============")
                                        except (OSError, TypeError) as e:
                                            print(f"    ✗ inspect.getsource() failed: {e}")
                                    # Check if it's a static method or other callable
                                    elif hasattr(method, '__code__'):
                                        try:
                                            method_source = inspect.getsource(method)
                                            print(f"    ✓ inspect.getsource() success: {len(method_source)} chars")
                                            code = method.__code__
                                            print(f"    ✓ Filename: {code.co_filename}")
                                            print(f"    ✓ First line: {code.co_firstlineno}")
                                            print("===source===")
                                            print(method_source)
                                            print("============")
                                        except (OSError, TypeError) as e:
                                            print(f"    ✗ inspect.getsource() failed: {e}")
                                    else:
                                        print(f"    • Skipped built-in method or attribute")
                        
                        # Try inspect.getsource on class (may fail for dynamic classes)
                        try:
                            inspect_class_source = inspect.getsource(obj)
                            print(f"✓ Class inspect.getsource() success: {len(inspect_class_source)} chars")
                        except (OSError, TypeError) as e:
                            print(f"✗ Class inspect.getsource() failed: {e} (expected)")
                    
                    elif callable(obj):
                        print(f"Type: function")
                        # Test function source
                        self.assertTrue(hasattr(obj, '__source__'), f"{obj_name} missing __source__ attribute")
                        func_source = obj.__source__
                        self.assertIn(f'def {obj.__name__}(', func_source)
                        print(f"✓ Function source length: {len(func_source)} chars")
                        print(f"✓ Virtual module: {getattr(obj, '__module__', 'N/A')}")
                        
                        if hasattr(obj, '__code__'):
                            code = obj.__code__
                            print(f"✓ Code object filename: {code.co_filename}")
                            print(f"✓ Code object first line: {code.co_firstlineno}")
                        
                        # Test inspect.getsource for functions (should work)
                        try:
                            inspect_func_source = inspect.getsource(obj)
                            print(f"✓ inspect.getsource() success: {len(inspect_func_source)} chars")
                            self.assertIn(f'def {obj.__name__}(', inspect_func_source)
                        except (OSError, TypeError) as e:
                            print(f"✗ inspect.getsource() failed: {e}")
                            self.fail(f"Function {obj_name} inspect.getsource() should work")
                
                print("\n=== Source code info test complete ===\n")
        def test_load_main_add_code_object_complex(self):
            """Test add_code_object with nested functions and async functions."""
            test_content = dedent('''
                import asyncio
                
                def outer_function():
                    return "outer"
                
                if __name__ == "__main__":
                    def nested_function():
                        def inner_function():
                            return "inner"
                        return inner_function
                    
                    async def async_function():
                        return "async"
                    
                    class ComplexClass:
                        def __init__(self):
                            self.value = "complex"
                        
                        def method(self):
                            return self.value
                        
                        @staticmethod
                        def static_method():
                            return "static"
                    
                    inner_func = nested_function()
                    complex_instance = ComplexClass()
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                # Use helper functions
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)
                
                result = load_main(f.name, add_code_object=True, globals=test_globals)
                
                # Test nested function
                nested_func = result['nested_function']
                inner_func = nested_func()
                self.assertEqual(inner_func(), "inner")
                
                # Test async function
                async_func = result['async_function']
                self.assertTrue(asyncio.iscoroutinefunction(async_func))
                
                # Test complex class
                complex_class = result['ComplexClass']
                instance = complex_class()
                self.assertEqual(instance.method(), "complex")
                self.assertEqual(complex_class.static_method(), "static")
                
                # Test comprehensive source code information for all complex objects
                print("\n=== Detailed source code info test ===")
                
                # Test all functions and classes
                test_objects = {
                    'nested_function': nested_func,
                    'async_function': async_func,
                    'ComplexClass': complex_class
                }
                
                for obj_name, obj in test_objects.items():
                    print(f"\n--- Testing {obj_name} ---")
                    
                    if inspect.isclass(obj):
                        print(f"Type: complex class")
                        # Test class source
                        self.assertTrue(hasattr(obj, '__source__'), f"{obj_name} missing __source__ attribute")
                        class_source = obj.__source__
                        self.assertIn(f'class {obj.__name__}:', class_source)
                        print(f"✓ Class source length: {len(class_source)} chars")
                        print(f"✓ Virtual file: {getattr(obj, '__module__', 'N/A')}")
                        print(f"✓ File attribute: {getattr(obj, '__file__', 'N/A')}")
                        
                        # Test all methods in the class
                        for method_name in dir(obj):
                            method = getattr(obj, method_name)
                            # Check if it's a method we want to test
                            if callable(method):
                                # Include special methods like __init__ and user-defined methods
                                should_test = (
                                    method_name in ['__init__', 'method', 'get_value', 'static_method'] or
                                    (not method_name.startswith('__') and not method_name.startswith('_'))
                                )
                                
                                if should_test:
                                    print(f"  Testing method: {method_name}")
                                    # Check if it's an instance method with __func__
                                    if hasattr(method, '__func__'):
                                        try:
                                            method_source = inspect.getsource(method)
                                            print(f"    ✓ inspect.getsource() success: {len(method_source)} chars")
                                            if hasattr(method.__func__, '__code__'):
                                                code = method.__func__.__code__
                                                print(f"    ✓ Filename: {code.co_filename}")
                                                print(f"    ✓ First line: {code.co_firstlineno}")
                                        except (OSError, TypeError) as e:
                                            print(f"    ✗ inspect.getsource() failed: {e}")
                                    # Check if it's a static method or other callable
                                    elif hasattr(method, '__code__'):
                                        try:
                                            method_source = inspect.getsource(method)
                                            print(f"    ✓ inspect.getsource() success: {len(method_source)} chars")
                                            code = method.__code__
                                            print(f"    ✓ Filename: {code.co_filename}")
                                            print(f"    ✓ First line: {code.co_firstlineno}")
                                        except (OSError, TypeError) as e:
                                            print(f"    ✗ inspect.getsource() failed: {e}")
                                    else:
                                        print(f"    • Skipped built-in method or attribute")
                        
                        print(f"   Total methods tested: {len(dir(obj))}")
                        
                        # Try inspect.getsource on class (may fail for dynamic classes)
                        try:
                            inspect_class_source = inspect.getsource(obj)
                            print(f"✓ Class inspect.getsource() success: {len(inspect_class_source)} chars")
                        except (OSError, TypeError) as e:
                            print(f"✗ Class inspect.getsource() failed: {e} (expected)")
                    
                    elif callable(obj):
                        if asyncio.iscoroutinefunction(obj):
                            print(f"Type: async function")
                        else:
                            print(f"Type: nested function")
                        
                        # Test function source
                        self.assertTrue(hasattr(obj, '__source__'), f"{obj_name} missing __source__ attribute")
                        func_source = obj.__source__
                        print(f"✓ Function source length: {len(func_source)} chars")
                        print(f"✓ Virtual module: {getattr(obj, '__module__', 'N/A')}")
                        
                        # Verify function definition exists in source
                        if obj_name == 'nested_function':
                            self.assertIn('def nested_function():', func_source)
                            self.assertIn('def inner_function():', func_source)
                            print("✓ Contains nested function definition")
                        elif obj_name == 'async_function':
                            self.assertIn('async def async_function():', func_source)
                            print("✓ Contains async function definition")
                        
                        if hasattr(obj, '__code__'):
                            code = obj.__code__
                            print(f"✓ Code object filename: {code.co_filename}")
                            print(f"✓ Code object first line: {code.co_firstlineno}")
                            print(f"✓ Function name: {code.co_name}")
                        
                        # Test inspect.getsource for functions (should work)
                        try:
                            inspect_func_source = inspect.getsource(obj)
                            print(f"✓ inspect.getsource() success: {len(inspect_func_source)} chars")
                            if obj_name == 'nested_function':
                                self.assertIn('def nested_function():', inspect_func_source)
                            elif obj_name == 'async_function':
                                self.assertIn('async def async_function():', inspect_func_source)
                        except (OSError, TypeError) as e:
                            print(f"✗ inspect.getsource() failed: {e}")
                            # For complex nested functions, inspect.getsource might fail
                            if obj_name != 'nested_function':
                                self.fail(f"Function {obj_name} inspect.getsource() should work")
                
                # Additional test: verify inner function from nested_function
                print(f"\n--- Testing nested inner function ---")
                inner_func = nested_func()
                if callable(inner_func):
                    print(f"Type: nested inner function")
                    print(f"Function name: {inner_func.__name__}")
                    if hasattr(inner_func, '__code__'):
                        code = inner_func.__code__
                        print(f"✓ Inner function filename: {code.co_filename}")
                        print(f"✓ Inner function first line: {code.co_firstlineno}")
                    
                    try:
                        inner_source = inspect.getsource(inner_func)
                        print(f"✓ Inner function inspect.getsource() success: {len(inner_source)} chars")
                    except (OSError, TypeError) as e:
                        print(f"✗ Inner function inspect.getsource() failed: {e} (possible)")
                
                print("\n=== Detailed source code info test complete ===\n")
        def test_load_main_add_code_object_disabled(self):
            """Test that add_code_object=False doesn't break anything."""
            test_content = dedent('''
                def helper():
                    return "helper"
                
                if __name__ == "__main__":
                    def main_func():
                        return "main"
                    
                    result = main_func()
            ''').strip()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
                f.write(test_content)
                f.flush()
                
                module = load_module(f.name)
                test_globals = collect_module_attr(module, all=True)
                
                # Test with add_code_object=False (default)
                result = load_main(f.name, add_code_object=False, globals=test_globals)
                
                # Verify function works normally
                main_func = result['main_func']
                self.assertEqual(main_func(), "main")
                self.assertEqual(result['result'], "main")
                
                # inspect.getsource should fail as expected for dynamically created functions
                with self.assertRaises((OSError, TypeError)):
                    inspect.getsource(main_func)

    # Run unittests, DO NOT DELETE THIS COMMENT
    unittest.main(argv=[''], exit=False, verbosity=2)