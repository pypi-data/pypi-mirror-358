from __future__ import annotations

import argparse
import ast
import os
from collections import defaultdict
from collections.abc import Collection
from typing import NamedTuple
from typing import TypeAlias

ModuleUsageTypes: TypeAlias = dict[str, dict[int, set[str]]]


class ListType(NamedTuple):
    element_types: frozenset[InferredType] = frozenset()

    def __str__(self) -> str:
        if not self.element_types:
            return "list[]"
        return f"list[{' | '.join(sorted(str(x) for x in self.element_types))}]"

    @classmethod
    def from_set(cls, s: set[InferredType]) -> ListType:
        return cls(element_types=frozenset(s))


class TupleType(NamedTuple):
    element_types: tuple[InferredType, ...] = ()
    # Use union types if it's not possible to determine
    # the # of args and their exact type by position
    use_union_types: bool = False

    def __str__(self) -> str:
        if self.use_union_types:
            unique_types = sorted({str(x) for x in self.element_types})
            return f"tuple[{' | '.join(unique_types)}]"
        else:
            return f"tuple[{', '.join(str(x) for x in self.element_types)}]"


class DictType(NamedTuple):
    key_types: frozenset[InferredType] = frozenset()
    value_types: frozenset[InferredType] = frozenset()

    def __str__(self) -> str:
        if not self.key_types and not self.value_types:
            return "dict[]"
        key_type = ' | '.join(sorted(str(x) for x in self.key_types))
        value_type = ' | '.join(sorted(str(x) for x in self.value_types))
        return f"dict[{key_type}, {value_type}]"

    @classmethod
    def from_sets(cls, keys: set[InferredType], values: set[InferredType]) -> DictType:
        return cls(key_types=frozenset(keys), value_types=frozenset(values))


class VarType(NamedTuple):
    name: str

    def __str__(self) -> str:
        return f"var:{self.name}"


InferredType = str | ListType | TupleType | DictType | VarType


def _extract_collection_types(inferred_type: InferredType) -> Collection[InferredType]:
    if isinstance(inferred_type, (ListType, TupleType)):
        return inferred_type.element_types
    return [inferred_type]


def _infer_list_type(node: ast.List, var_types: dict[str, InferredType] | None = None) -> ListType:
    if not node.elts:
        return ListType()

    element_types: set[InferredType] = set()

    for elt in node.elts:
        if isinstance(elt, ast.Starred):
            expanded_type = infer_type(elt.value, var_types)
            inner_types = _extract_collection_types(expanded_type)
            element_types.update(inner_types)
        else:
            element_types.add(infer_type(elt, var_types))

    return ListType.from_set(element_types)


def _infer_tuple_type(
    node: ast.Tuple, var_types: dict[str, InferredType] | None = None,
) -> TupleType:
    """
    If we can infer the exact number of arguments and types of the tuple
    arguments then return an exact representation (tuple[int, int, int, str])
    whereas if we can't, then return a unionized representation of the
    tuple types (tuple[int | str]).
    """
    if not node.elts:
        return TupleType()

    tuple_types = []
    use_union_types = False

    for elt in node.elts:
        if isinstance(elt, ast.Starred):
            if isinstance(elt.value, (ast.List, ast.Tuple)):
                for sub_elt in elt.value.elts:
                    tuple_types.append(infer_type(sub_elt, var_types))
            else:
                expanded_type = infer_type(elt.value, var_types)
                inner_types = _extract_collection_types(expanded_type)
                tuple_types.extend(inner_types)
                if isinstance(expanded_type, ListType):
                    use_union_types = True
        else:
            tuple_types.append(infer_type(elt, var_types))

    return TupleType(
        element_types=tuple(tuple_types),
        use_union_types=use_union_types,
    )


def _infer_dict_type(node: ast.Dict, var_types: dict[str, InferredType] | None = None) -> DictType:
    if not node.keys and not node.values:
        return DictType()

    key_types: set[InferredType] = set()
    value_types: set[InferredType] = set()

    for key, value in zip(node.keys, node.values):
        if key is None:
            # If the key is None, we have a dict-unpacking expression (**dict)
            # and need to recursively infer the inner types and determine
            # if they are part of the key types or value types.
            expanded_type = infer_type(value, var_types)
            if isinstance(expanded_type, DictType):
                key_types.update(expanded_type.key_types)
                value_types.update(expanded_type.value_types)

        else:
            key_types.add(infer_type(key, var_types))
            value_types.add(infer_type(value, var_types))

    return DictType.from_sets(key_types, value_types)


def infer_type(node: ast.AST, var_types: dict[str, InferredType] | None = None) -> InferredType:
    if isinstance(node, ast.Constant):
        return type(node.value).__name__
    elif isinstance(node, ast.List):
        return _infer_list_type(node, var_types)
    elif isinstance(node, ast.Dict):
        return _infer_dict_type(node, var_types)
    elif isinstance(node, ast.Tuple):
        return _infer_tuple_type(node, var_types)
    elif isinstance(node, ast.Name):
        if var_types and node.id in var_types:
            return var_types[node.id]
        return VarType(node.id)
    return "unknown"


def find_import_aliases(
    tree: ast.AST,
    module_name: str,
) -> tuple[set[str], dict[str, str]]:
    module_aliases: set[str] = set()
    direct_imports: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == module_name:
                    module_aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith(module_name):
                for alias in node.names:
                    local_name = alias.asname or alias.name
                    direct_imports[local_name] = alias.name

    return module_aliases, direct_imports


class ModuleCallVisitor(ast.NodeVisitor):
    def __init__(
        self,
        lib_aliases: set[str],
        direct_imports: dict[str, str],
        filepath: str | None = None,
        verbose: bool = False,
    ) -> None:
        self.lib_aliases = lib_aliases
        self.direct_imports = direct_imports
        self.filepath = filepath
        self.verbose = verbose
        self.calls: list[tuple[str, int, InferredType]] = []
        self.var_types: dict[str, InferredType] = {}

    def visit_Assign(self, node: ast.Assign) -> None:
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            var_type = infer_type(node.value, self.var_types)
            if not isinstance(var_type, VarType):
                self.var_types[var_name] = var_type

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func_name: str | None = None

        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
        ):
            if node.func.value.id in self.lib_aliases:
                func_name = node.func.attr

        elif isinstance(node.func, ast.Name) and node.func.id in self.direct_imports:
            func_name = self.direct_imports[node.func.id]

        if func_name:
            arg_types: list[InferredType] = []
            for i, arg in enumerate(node.args):
                arg_type = infer_type(arg, self.var_types)
                arg_types.append(arg_type)
                self.calls.append((func_name, i, arg_type))

            if self.verbose:
                args_str = ', '.join(str(t) for t in arg_types)
                print(
                    f"[{self.filepath}:{node.lineno}] {func_name}({args_str})",
                )

        self.generic_visit(node)


def analyze_file(filepath: str, module_name: str, verbose: bool = False) -> ModuleUsageTypes:
    with open(filepath, encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)
    module_aliases, direct_imports = find_import_aliases(tree, module_name)

    usages: ModuleUsageTypes = defaultdict(lambda: defaultdict(set))
    if module_aliases or direct_imports:
        visitor = ModuleCallVisitor(
            module_aliases, direct_imports, filepath, verbose,
        )
        visitor.visit(tree)
        for func_name, arg_pos, arg_type in visitor.calls:
            usages[func_name][arg_pos].add(str(arg_type))

    return usages


def walk_repo(
    root_dir: str,
    module_name: str,
    verbose: bool = False,
) -> ModuleUsageTypes:
    usages: ModuleUsageTypes = defaultdict(lambda: defaultdict(set))
    for dirpath, _, filenames in os.walk(root_dir):
        filenames = [x for x in filenames if x.endswith(".py")]
        for filename in filenames:
            for func_name, args_data in analyze_file(
                    os.path.join(dirpath, filename),
                    module_name, verbose,
            ).items():
                for arg_pos, types in args_data.items():
                    usages[func_name][arg_pos].update(types)
    return usages


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze function call type information",
    )
    parser.add_argument(
        "module_names", nargs="+",
        help="Name of the modules to analyze",
    )
    parser.add_argument(
        "dir", help="Path to the root directory of repositories",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print function calls with file locations",
    )
    args = parser.parse_args()

    module_usages: dict[str, ModuleUsageTypes] = {}

    for module in args.module_names:
        usages = walk_repo(
            args.dir, module, verbose=args.verbose,
        )
        module_usages[module] = usages

    for module, usages in module_usages.items():
        print(f"=== Module <{module}> summary ===")
        for func, args_types in usages.items():
            print(f"Function: {func}")
            for pos, types in args_types.items():
                print(f"  Arg {pos}: {', '.join(sorted(types))}")
            print()
    return 0


if __name__ == "__main__":
    SystemExit(main())
