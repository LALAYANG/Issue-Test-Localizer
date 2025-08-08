import ast
import os
from typing import Dict, List, Tuple


def find_tests_calling_function(
    repo_dir: str, target_funcs: Dict[str, List[str]]
) -> List[Tuple[str, str, str, str]]:
    # repo_dir: Root of the codebase
    # target_funcs: Dict mapping source files to function names, e.g.,
    #         {"src/module.py": ["Class.method", "func", "Class"]}

    # List of (test_file_path, test_func_name, matched_name, func_source_file)
    results = []

    match_funcs = set()
    fallback_classes = set()

    for file_path, funcs in target_funcs.items():
        for f in funcs:
            parts = f.split(".")
            if len(parts) == 2 and parts[0][0].isupper():
                class_name, func_name = parts
                match_funcs.add((class_name, func_name, f, file_path))
                fallback_classes.add((class_name, f, file_path))
            elif len(parts) == 1:
                if parts[0][0].isupper():
                    fallback_classes.add((parts[0], f, file_path))  # just class
                else:
                    match_funcs.add(
                        (None, parts[0], f, file_path)
                    )  # top-level function

    for root, _, files in os.walk(repo_dir):
        for file in files:
            if not file.endswith(".py"):
                continue

            full_path = os.path.join(root, file)

            if "test" not in os.path.basename(full_path).lower():
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=full_path)
            except Exception as e:
                print(f"Skipping {full_path} due to parse error: {e}")
                continue

            current_func = None
            import_aliases = {}  # e.g., {'u': 'astropy.units'}

            class TestVisitor(ast.NodeVisitor):
                def visit_ImportFrom(self, node):
                    for alias in node.names:
                        if alias.asname:
                            import_aliases[alias.asname] = (
                                f"{node.module}.{alias.name}"
                                if node.module
                                else alias.name
                            )
                        else:
                            import_aliases[alias.name] = (
                                f"{node.module}.{alias.name}"
                                if node.module
                                else alias.name
                            )

                def visit_Import(self, node):
                    for alias in node.names:
                        if alias.asname:
                            import_aliases[alias.asname] = alias.name
                        else:
                            import_aliases[alias.name] = alias.name

                def visit_FunctionDef(self, node):
                    nonlocal current_func
                    current_func = node.name
                    self.generic_visit(node)

                def visit_Call(self, node):
                    nonlocal current_func

                    resolved_name = None

                    if isinstance(node.func, ast.Attribute):
                        if isinstance(node.func.value, ast.Name):
                            alias = node.func.value.id
                            attr = node.func.attr
                            base = import_aliases.get(alias)
                            if base:
                                resolved_name = f"{base}.{attr}"
                            else:
                                resolved_name = f"{alias}.{attr}"
                        else:
                            resolved_name = node.func.attr
                    elif isinstance(node.func, ast.Name):
                        resolved_name = node.func.id

                    for class_name, func_name, full_name, func_file in match_funcs:
                        if resolved_name:
                            if class_name:
                                if resolved_name.endswith(f"{class_name}.{func_name}"):
                                    results.append(
                                        (full_path, current_func, full_name, func_file)
                                    )
                            else:
                                if resolved_name.endswith(func_name):
                                    results.append(
                                        (full_path, current_func, full_name, func_file)
                                    )

                    # Also detect instantiations like ClassName(...)
                    if isinstance(node.func, ast.Name):
                        class_name = node.func.id
                        for fallback_class, full_name, func_file in fallback_classes:
                            if class_name == fallback_class:
                                results.append(
                                    (full_path, current_func, full_name, func_file)
                                )

                    self.generic_visit(node)

                def visit_Attribute(self, node):
                    nonlocal current_func
                    if isinstance(node.value, ast.Name):
                        class_candidate = node.value.id
                        for fallback_class, full_name, func_file in fallback_classes:
                            if class_candidate == fallback_class:
                                results.append(
                                    (full_path, current_func, full_name, func_file)
                                )
                    self.generic_visit(node)

            visitor = TestVisitor()
            visitor.visit(tree)

    return results
