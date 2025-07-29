# Here we do the transpilation of the Clyp code to Python code!!!!! :3
# Cool right? Well actually it is not that cool, but it's a start

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
import typeguard
from typing import List, Optional, Match
import inspect
import clyp.stdlib as stdlib
from clyp.ErrorHandling import ClypSyntaxError

def _process_pipeline_chain(chain: str) -> str:
    parts = [p.strip() for p in chain.split('|>') if p.strip()]
    if len(parts) < 2:
        return chain

    result = parts[0]
    for part in parts[1:]:
        if not part:
            continue
        if '(' in part and part.endswith(')'):
            open_paren_index = part.find('(')
            func_name = part[:open_paren_index].strip()
            args = part[open_paren_index+1:-1].strip()
            if args:
                result = f"{func_name}({result}, {args})"
            else:
                result = f"{func_name}({result})"
        else:
            func_name = part.strip()
            result = f"{func_name}({result})"
    return result

def _process_pipeline_operator(line: str) -> str:
    if '|>' not in line:
        return line

    # This does not handle strings with '|>' correctly, but is consistent with the rest of the transpiler.
    assignment_match = re.match(r"(.*\s*=\s*)(.*)", line)
    if assignment_match:
        lhs = assignment_match.group(1)
        rhs = assignment_match.group(2)
        transformed_rhs = _process_pipeline_chain(rhs)
        return lhs + transformed_rhs
    else:
        return _process_pipeline_chain(line)

def _replace_keywords_outside_strings(line: str) -> str:
    parts = re.split(r'(".*?"|\'.*?\')', line)
    for i in range(0, len(parts), 2):
        part = parts[i]
        part = re.sub(r"\bunless\b", "if not", part)
        part = re.sub(r"\bis not\b", "!=", part)
        part = re.sub(r"\bis\b", "==", part)
        parts[i] = part
    return "".join(parts)

@typeguard.typechecked
def parse_clyp(clyp_code: str, file_path: Optional[str] = None) -> str:
    indentation_level: int = 0
    indentation_sign: str = "    "
    stdlib_names = [
        name for name, member in inspect.getmembers(stdlib)
        if not name.startswith('_') and (inspect.isfunction(member) or inspect.isclass(member)) and member.__module__ == stdlib.__name__
    ]
    python_code: str = (
        "from typeguard import install_import_hook; install_import_hook()\n"
        "import clyp\n"
        "from clyp.importer import clyp_import\n"
        f"from clyp.stdlib import {', '.join(stdlib_names)}\n"
        "del clyp\n"
        "true = True; false = False; null = None\n"
    )

    processed_code: List[str] = []
    in_string: bool = False
    string_char: Optional[str] = None
    in_comment: bool = False
    escape_next: bool = False

    char: str
    for char in clyp_code:
        if escape_next:
            processed_code.append(char)
            escape_next = False
            continue

        if char == '\\':
            processed_code.append(char)
            escape_next = True
            continue

        if in_comment:
            processed_code.append(char)
            if char == '\n':
                in_comment = False
            continue

        if in_string:
            processed_code.append(char)
            if char == string_char:
                in_string = False
            continue

        # Not in string, not in comment
        if char in ('"', "'''"):
            in_string = True
            string_char = char
            processed_code.append(char)
        elif char == '#':
            in_comment = True
            processed_code.append(char)
        elif char == ';':
            processed_code.append('\n')
        elif char == '{':
            processed_code.append('{\n')
        elif char == '}':
            processed_code.append('}\n')
        else:
            processed_code.append(char)
    
    infile_str_raw: str = "".join(processed_code)

    # Handle clyp imports
    processed_import_lines = []
    for line in infile_str_raw.split('\n'):
        stripped_line = line.strip()
        if stripped_line.startswith("clyp import "):
            parts = stripped_line.split()
            if len(parts) == 3:
                module_name = parts[2]
                processed_import_lines.append(f"{module_name} = clyp_import('{module_name}', {repr(file_path)})")
            else:
                raise ClypSyntaxError(f"Invalid clyp import statement: {stripped_line}")
        elif stripped_line.startswith("clyp from "):
            match = re.match(r"clyp from\s+([\w\.]+)\s+import\s+(.*)", stripped_line)
            if match:
                module_name, imports_str = match.groups()
                imported_names = [name.strip() for name in imports_str.split(',')]
                
                processed_import_lines.append(f"_temp_module = clyp_import('{module_name}', {repr(file_path)})")
                for name in imported_names:
                    processed_import_lines.append(f"{name} = _temp_module.{name}")
                processed_import_lines.append("del _temp_module")
            else:
                raise ClypSyntaxError(f"Invalid clyp from import statement: {stripped_line}")
        else:
            processed_import_lines.append(line)
    infile_str_raw = "\n".join(processed_import_lines)

    # Automatically insert 'pass' into empty blocks
    infile_str_raw = re.sub(r'{(\s|#[^\n]*)*}', '{\n    pass\n}', infile_str_raw)

    infile_str_indented: str = ""
    line: str
    for line in infile_str_raw.split("\n"):
        line = _process_pipeline_operator(line)
        m: Optional[Match[str]] = re.search(r"[ \t]*(#.*$)", line)

        if m is not None:
            m2: Optional[Match[str]] = re.search(r'["\'].*#.*["\']', m.group(0))
            if m2 is not None:
                m = None

        if m is not None:
            add_comment: str = m.group(0)
            line = re.sub(r"[ \t]*(#.*$)", "", line)
        else:
            add_comment: str = ""

        if not line.strip():
            infile_str_indented += indentation_level*indentation_sign + add_comment.lstrip() + "\n"
            continue

        stripped_line = line.strip()

        if stripped_line.startswith("let "):
            line = re.sub(r"^\s*let\s+", "", line)
            stripped_line = line.strip()

        keywords = ("def ", "function ", "if ", "for ", "while ", "class ", "return ", "elif ", "else", "{", "}", "print", "repeat ")
        if stripped_line.startswith("except"):
            match = re.match(r"except\s*\((.*)\)", stripped_line)
            if match:
                content = match.group(1).strip()
                parts = content.split()
                if len(parts) == 2:
                    exc_type, exc_var = parts
                    line = re.sub(r"except\s*\(.*\)", f"except {exc_type} as {exc_var}", line)
                elif len(parts) == 1:
                    exc_type = parts[0]
                    line = re.sub(r"except\s*\(.*\)", f"except {exc_type}", line)
                stripped_line = line.strip()
        elif not stripped_line.startswith(keywords):
            # Use a regex that captures an optional type, a name, and the rest of the line
            match = re.match(r"^\s*(?:([a-zA-Z_][\w\.\[\]]*)\s+)?([a-zA-Z_]\w*)\s*=(.*)", line)
            if match:
                var_type, var_name, rest_of_line = match.groups()
                if var_type:
                    # Reconstruct the line in Python's type-hint format
                    line = f"{var_name.strip()}: {var_type.strip()} = {rest_of_line.strip()}"
                else:
                    # It's a regular variable assignment
                    line = f"{var_name.strip()} = {rest_of_line.strip()}"
                stripped_line = line
            else:
                # Handle declarations without assignment (e.g., in classes)
                match_decl = re.match(r"^\s*([a-zA-Z_][\w\.\[\]]*)\s+([a-zA-Z_]\w*)\s*$", line)
                if match_decl:
                    var_type, var_name = match_decl.groups()
                    line = f"{var_name.strip()}: {var_type.strip()}"
                    stripped_line = line

        if stripped_line.startswith("def ") or stripped_line.startswith("function "):
            if stripped_line.startswith("function "):
                line = line.replace("function", "def", 1)
                stripped_line = line.strip()

            return_type_match = re.search(r"returns\s+([a-zA-Z_][\w\.\[\]]*)", stripped_line)
            if not return_type_match:
                raise ClypSyntaxError(f"Function definition requires a 'returns' clause. Found in line: {stripped_line}")

            return_type = return_type_match.group(1)
            line = re.sub(r"\s*returns\s+([a-zA-Z_][\w\.\[\]]*)", "", line)
            stripped_line = line.strip()

            args_match = re.search(r"\(([^)]*)\)", stripped_line)
            if args_match:
                original_args_str = args_match.group(1)
                args_str = original_args_str.strip()
                
                if args_str:
                    args = [arg.strip() for arg in args_str.split(',')]
                    new_args = []
                    for arg in args:
                        if not arg:
                            continue
                        if arg == 'self' or arg.startswith('*'):
                            new_args.append(arg)
                            continue
                        
                        parts = arg.strip().split()
                        if len(parts) >= 2:
                            arg_type = parts[0]
                            arg_name = parts[1]
                            default_value = ' '.join(parts[2:])
                            new_arg_str = f"{arg_name}: {arg_type}"
                            if default_value:
                                new_arg_str += f" {default_value}"
                            new_args.append(new_arg_str)
                        else:
                            raise ClypSyntaxError(f"Argument '{arg}' in function definition must be in 'type name' format. Found in line: {stripped_line}")
                    
                    new_args_str = ", ".join(new_args)
                    line = line.replace(original_args_str, new_args_str)
                    stripped_line = line.strip()
            
            if "{" in line:
                line_before_brace, line_after_brace = line.rsplit('{', 1)
                line = f"{line_before_brace.rstrip()} -> {return_type} {{{line_after_brace}"
            else:
                line = line.strip() + f" -> {return_type}"
                stripped_line = line.strip()

        if stripped_line.startswith("repeat "):
            line = re.sub(r"repeat\s+\[(.*)\]\s+times", r"for _ in range(\1)", line)
            stripped_line = line.strip()

        line = re.sub(r"\brange\s+(\S+)\s+to\s+(\S+)", r"range(\1, \2 + 1)", line)

        line = _replace_keywords_outside_strings(line)

        line = line.lstrip()
        
        line_to_indent = line
        if line.startswith("}"):
            indentation_level -= 1
            line_to_indent = line.lstrip("}").lstrip()

        indented_line = (indentation_level * indentation_sign) + line_to_indent

        if indented_line.rstrip().endswith("{"):
            indentation_level += 1
            line = indented_line.rsplit('{', 1)[0].rstrip() + ":"
        else:
            line = indented_line

        infile_str_indented += line + add_comment + "\n"

    infile_str_indented = re.sub(r"else\s+if", "elif", infile_str_indented)
    infile_str_indented = re.sub(r";\n", "\n", infile_str_indented)

    python_code += infile_str_indented
    return python_code
