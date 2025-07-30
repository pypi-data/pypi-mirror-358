import ast

import pytest

from typespy import ModuleCallVisitor
from typespy import analyze_file
from typespy import find_import_aliases
from typespy import infer_type


@pytest.fixture
def tmp_file(tmp_path):
    yield tmp_path / "a.py"


@pytest.mark.parametrize(
    "content, expected_type", [
        ("'hello'", "str"),
        ("42", "int"),
        ("[1, 2, 3]", "list[int]"),
        ("['a', 'b']", "list[str]"),
        ("[1, 'a']", "list[int | str]"),
        ("[]", "list[]"),
        ("{'a': 1}", "dict[str, int]"),
        ("{'a': 1, 'b': 3.0}", "dict[str, float | int]"),
        ("{}", "dict[]"),
        ("(1, 'a')", "tuple[int, str]"),
        ("()", "tuple[]"),
    ],
)
def test_infer_type_constants(content, expected_type):
    node = ast.parse(content).body[0].value
    assert str(infer_type(node)) == expected_type


@pytest.mark.parametrize(
    "content, var_types, expected_type", [
        ("foo", {}, "var:foo"),
        ("foo", {"foo": "int"}, "int"),
        ("func()", {}, "unknown"),
    ],
)
def test_infer_type_variables(content, var_types, expected_type):
    node = ast.parse(content).body[0].value
    assert str(infer_type(node, var_types)) == expected_type


@pytest.mark.parametrize(
    "content, module_name, expected_aliases, expected_imports", [
        ("import foo", "foo", {"foo"}, {}),
        ("import foo as f", "foo", {"f"}, {}),
        (
            "from foo import bar, baz", "foo",
            set(), {"bar": "bar", "baz": "baz"},
        ),
        (
            "from foo import bar as b, baz", "foo",
            set(), {"b": "bar", "baz": "baz"},
        ),
        ("import unrelated", "foo", set(), {}),
        ("from unrelated import something", "foo", set(), {}),
    ],
)
def test_find_import_aliases(content, module_name, expected_aliases, expected_imports):
    tree = ast.parse(content)
    module_aliases, direct_imports = find_import_aliases(tree, module_name)

    assert module_aliases == expected_aliases
    assert direct_imports == expected_imports


def test_library_call_visitor_module_alias():
    content = """
import foo as f
f.bar([1, 2, 3])
f.baz("hello")
"""
    tree = ast.parse(content)

    lib_aliases = {"f"}
    direct_imports = {}
    visitor = ModuleCallVisitor(lib_aliases, direct_imports)
    visitor.visit(tree)

    # Convert to string representation for comparison
    calls_str = [
        (func, pos, str(arg_type))
        for func, pos, arg_type in visitor.calls
    ]
    assert ("bar", 0, "list[int]") in calls_str
    assert ("baz", 0, "str") in calls_str


def test_library_call_visitor_direct_import():
    content = """
from foo import bar, baz as b
bar({'x': 1})
b(42)
"""
    tree = ast.parse(content)

    lib_aliases = set()
    direct_imports = {"bar": "bar", "b": "baz"}
    visitor = ModuleCallVisitor(lib_aliases, direct_imports)
    visitor.visit(tree)

    # Convert to string representation for comparison
    calls_str = [
        (func, pos, str(arg_type))
        for func, pos, arg_type in visitor.calls
    ]
    assert ("bar", 0, "dict[str, int]") in calls_str
    assert ("baz", 0, "int") in calls_str


def test_library_call_visitor_multiple_args():
    content = """
import foo as f
my_var = "hello"
f.bar([1, 2], 80, my_var)
"""
    tree = ast.parse(content)

    lib_aliases = {"f"}
    direct_imports = {}
    visitor = ModuleCallVisitor(lib_aliases, direct_imports)
    visitor.visit(tree)

    # Convert to string representation for comparison
    calls_str = [
        (func, pos, str(arg_type))
        for func, pos, arg_type in visitor.calls
    ]
    assert ("bar", 0, "list[int]") in calls_str
    assert ("bar", 1, "int") in calls_str
    assert ("bar", 2, "str") in calls_str


def test_analyze_file_simple(tmp_file):
    content = """
import foo as f
from foo import bar

def example():
    data = [{"x": 1}, {"y": 2}]
    f.bar(data, 40)
    bar("string")
    bar(123)
    bar([1, 2, 3])

my_list = [1, 2, 3]
f.bar(my_list)
"""

    tmp_file.write_text(content)
    usages = analyze_file(tmp_file, 'foo')

    assert usages["bar"][0] == {
        'int',
        'list[dict[str, int]]',
        'list[int]',
        'str',
    }

    assert usages["bar"][1] == {"int"}


def test_dict_expansion(tmp_file):
    content = """
import f

dd = {'a': 5.0}
dd2 = {'b': 1, **dd}
dd3 = {'c': True, **dd2}
dd4 = {**dd3}
f.foo(dd2)
f.bar(dd3)
f.foobar(dd4)
"""

    tmp_file.write_text(content)
    usages = analyze_file(tmp_file, 'f')

    assert usages["foo"][0] == {'dict[str, float | int]'}
    assert usages["bar"][0] == {'dict[str, bool | float | int]'}
    assert usages["foobar"][0] == {'dict[str, bool | float | int]'}


def test_list_unpacking(tmp_file):
    content = """
import f

a = [1, 2]
b = [*a, 3.0, "x"]
c = ["y", *a]
f.foo(b)
f.bar(c)
"""

    tmp_file.write_text(content)
    usages = analyze_file(tmp_file, 'f')

    assert usages["foo"][0] == {'list[float | int | str]'}
    assert usages["bar"][0] == {'list[int | str]'}


def test_tuple_unpacking(tmp_file):
    content = """
import f

a = (1, 2)
b = (*a, 3.0, "x")
c = ("y", *a)
f.foo(b)
f.bar(c)
"""

    tmp_file.write_text(content)
    usages = analyze_file(tmp_file, 'f')

    assert usages["foo"][0] == {'tuple[int, int, float, str]'}
    assert usages["bar"][0] == {'tuple[str, int, int]'}


def test_mixed_unpacking(tmp_file):
    content = """
import f

a = [1, 2]
b = (3.0, "x")
c = [*a, *b, True]
d = (*a, *b, False)
f.foo(c)
f.bar(d)
"""

    tmp_file.write_text(content)
    usages = analyze_file(tmp_file, 'f')

    assert usages["foo"][0] == {'list[bool | float | int | str]'}
    assert usages["bar"][0] == {'tuple[bool | float | int | str]'}


def test_exact_tuple_unpacking(tmp_file):
    content = """
import f

# Exact cases - tuple variables and literals give exact positional types
t1 = (1, "x")
t2 = (*t1, 3.0)          # tuple variable expansion - exact
t3 = (*(1, "x"), 3.0)    # tuple literal expansion - exact

f.exact1(t2)
f.exact2(t3)
"""

    tmp_file.write_text(content)
    usages = analyze_file(tmp_file, 'f')

    # Exact positional types (comma-separated)
    assert usages["exact1"][0] == {'tuple[int, str, float]'}
    assert usages["exact2"][0] == {'tuple[int, str, float]'}


def test_inexact_list_to_tuple_unpacking(tmp_file):
    content = """
import f

# Inexact cases - list variables give union types
l1 = [1, 2]
t4 = (*l1, "x")          # list variable expansion - inexact

f.inexact(t4)
"""

    tmp_file.write_text(content)
    usages = analyze_file(tmp_file, 'f')

    # Inexact union types (pipe-separated)
    assert usages["inexact"][0] == {'tuple[int | str]'}
