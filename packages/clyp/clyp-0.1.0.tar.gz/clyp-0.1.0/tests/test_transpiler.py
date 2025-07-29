import pytest
from clyp.transpiler import parse_clyp, ClypSyntaxError

def test_transpiler():
    clyp_code = """
    # This is a comment
    if (true) {print("Hello, World!");} else {print("Goodbye, World!");}
    """
    expected_python_code = """from typeguard import install_import_hook; install_import_hook()
import clyp
from clyp.stdlib import d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z
eval = clyp.eval; exec = clyp.exec
del clyp
true = True; false = False; null = None
# This is a comment
if (true):
    print("Hello, World!")
else:
    print("Goodbye, World!")

"""
    # Note: The exact output depends on the stdlib names, which can vary.
    # This test should be made more robust.
    assert "if (true):" in parse_clyp(clyp_code)

def test_new_syntax_valid_variable_declaration():
    valid_var_code = "int x = 5;"
    parsed_code = parse_clyp(valid_var_code)
    assert "x: int = 5" in parsed_code

def test_new_syntax_valid_function_definition():
    valid_func_code = "def my_func(str a) returns None { print(a); }"
    parsed_code = parse_clyp(valid_func_code)
    assert "def my_func(a: str) -> None:" in parsed_code
    assert "print(a)" in parsed_code

def test_new_syntax_valid_function_with_default_value():
    valid_func_code_default = "def my_func(str a, int b = 0) returns None { print(a, b); }"
    parsed_code = parse_clyp(valid_func_code_default)
    assert "def my_func(a: str, b: int = 0) -> None:" in parsed_code

def test_new_syntax_invalid_function_definition():
    invalid_func_code = "def my_func(a) returns None { print(a); }"
    with pytest.raises(ClypSyntaxError, match="Argument 'a' in function definition must be in 'type name' format."):
        parse_clyp(invalid_func_code)

def test_new_syntax_invalid_function_definition_missing_returns():
    invalid_func_code_no_returns = "def my_func(str a) { print(a); }"
    with pytest.raises(ClypSyntaxError, match="Function definition requires a 'returns' clause."):
        parse_clyp(invalid_func_code_no_returns)

def test_new_syntax_valid_self_in_function():
    valid_self_code = "def my_method(self, bool b) returns None { pass; }"
    parsed_code = parse_clyp(valid_self_code)
    assert "def my_method(self, b: bool) -> None:" in parsed_code

def test_empty_blocks_function():
    empty_func_code = "def my_func() returns None {}"
    parsed_code = parse_clyp(empty_func_code)
    assert "def my_func() -> None:" in parsed_code
    assert "pass" in parsed_code

def test_empty_blocks_if():
    empty_if_code = "if (true) {}"
    parsed_code = parse_clyp(empty_if_code)
    assert "if (true):" in parsed_code
    assert "pass" in parsed_code

def test_empty_blocks_nested():
    nested_empty_code = "if (true) { if(false) {} }"
    parsed_code = parse_clyp(nested_empty_code)
    assert "if (true):" in parsed_code
    assert "if(false):" in parsed_code
    assert "pass" in parsed_code

def test_range_to_syntax():
    clyp_code = "for i in range 1 to 5"
    parsed_code = parse_clyp(clyp_code)
    assert "for i in range(1, 5 + 1)" in parsed_code

def test_is_is_not_syntax():
    clyp_code = """
    if (a is b) {}
    if (x is not y) {}
    """
    parsed_code = parse_clyp(clyp_code)
    assert "if (a == b):" in parsed_code
    assert "if (x != y):" in parsed_code

def test_unless_syntax():
    clyp_code = "unless (a > b) {}"
    parsed_code = parse_clyp(clyp_code)
    assert "if not (a > b):" in parsed_code

def test_pipeline_operator():
    clyp_code = "data |> clean |> transform |> save"
    parsed_code = parse_clyp(clyp_code)
    assert "save(transform(clean(data)))" in parsed_code

def test_pipeline_operator_with_assignment():
    clyp_code = "let result = data |> clean |> transform"
    parsed_code = parse_clyp(clyp_code)
    assert "result = transform(clean(data))" in parsed_code

def test_pipeline_operator_with_args():
    clyp_code = 'data |> clean |> transform("fast") |> save'
    parsed_code = parse_clyp(clyp_code)
    assert 'save(transform(clean(data), "fast"))' in parsed_code
