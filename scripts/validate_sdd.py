#!/usr/bin/env python3
"""
validate_sdd.py

以下のアーキテクチャ制約を自動検証する統合Linter（防波堤）です。
1. The "Fake ID" & "Test Deletion" Loophole 防御（双方向トレーサビリティ）:
   - spec.md の要求ID（マスター）と、Unit/Integration テストの要求IDが完全に一致しているか。
2. Application層検証: src/application/ 内に README.md, spec.md, *.py が揃っているか。
3. スクリプトのインデックス検証: scripts/ 内の全スクリプトが scripts/README.md に記載されているか。
"""

import ast
import re
import sys
from pathlib import Path

SCENARIO_PATTERN = re.compile(r"\[[A-Z]+-\d+\]")


def extract_scenarios_from_spec(app_dir: Path) -> set[str]:
    """すべての spec.md から正規の要求IDマスターリストを抽出する"""
    master_scenarios = set()
    for spec_file in app_dir.rglob("spec.md"):
        with open(spec_file, "r", encoding="utf-8") as f:
            content = f.read()
            matches = SCENARIO_PATTERN.findall(content)
            master_scenarios.update(matches)
    return master_scenarios


def extract_scenarios_from_tests(test_dir: Path, is_integration: bool = False) -> tuple[set[str], list[str]]:
    """指定されたディレクトリのテストコードをパースし、ID集合とエラーを返す"""
    scenarios = set()
    errors = []

    if not test_dir.exists():
        return scenarios, errors

    # Pytest Evasion防止: test_*.py と *_test.py の両方を走査
    test_files = list(test_dir.rglob("test_*.py")) + list(test_dir.rglob("*_test.py"))

    for filepath in set(test_files):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            errors.append(f"SyntaxError in {filepath}: {e}")
            continue

        # ファイルレベルのモックインポートチェック (Integration Testのみ)
        if is_integration:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("unittest.mock"):
                            errors.append(
                                f"Mock Usage Detected: {filepath.name} contains 'import {alias.name}'. Mocking is strictly prohibited in integration tests."
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("unittest.mock"):
                        errors.append(
                            f"Mock Usage Detected: {filepath.name} contains 'from {node.module} import ...'. Mocking is strictly prohibited in integration tests."
                        )

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and (node.name.startswith("test_") or node.name.endswith("_test")):
                # 1. Skip / Skipif デコレータの検知
                has_skip = False
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Attribute) and decorator.attr in ("skip", "skipif"):
                        has_skip = True
                    elif (
                        isinstance(decorator, ast.Call)
                        and isinstance(decorator.func, ast.Attribute)
                        and decorator.func.attr in ("skip", "skipif")
                    ):
                        has_skip = True
                    # @patch の検知 (Integration Testのみ)
                    if is_integration:
                        if (
                            isinstance(decorator, ast.Call)
                            and isinstance(decorator.func, ast.Name)
                            and decorator.func.id == "patch"
                        ):
                            errors.append(
                                f"Mock Usage Detected: Function '{node.name}' in {filepath.name} uses '@patch' decorator."
                            )
                        elif (
                            isinstance(decorator, ast.Call)
                            and isinstance(decorator.func, ast.Attribute)
                            and decorator.func.attr == "patch"
                        ):
                            errors.append(
                                f"Mock Usage Detected: Function '{node.name}' in {filepath.name} uses '@patch' decorator."
                            )

                if has_skip:
                    errors.append(
                        f"Skip Evasion Detected: Function '{node.name}' in {filepath.name} is skipped. Skipping tests to bypass coverage is prohibited."
                    )
                    continue

                # 2. Integration Test での mocker / monkeypatch 引数の検知
                if is_integration:
                    for arg in node.args.args:
                        if arg.arg in ("mocker", "monkeypatch"):
                            errors.append(
                                f"Mock Usage Detected: Function '{node.name}' in {filepath.name} uses '{arg.arg}' fixture. Mocking is strictly prohibited in integration tests."
                            )

                # 3. アサーションの空洞化検知 (最低1つの assert 文が含まれているか)
                has_assert = False
                for body_node in ast.walk(node):
                    if isinstance(body_node, ast.Assert):
                        has_assert = True
                        break

                if not has_assert:
                    errors.append(
                        f"Empty Assertion Detected: Function '{node.name}' in {filepath.name} contains no 'assert' statements."
                    )

                # 4. Try-Except Evasion の検知
                for body_node in ast.walk(node):
                    if isinstance(body_node, ast.Try):
                        errors.append(
                            f"Evasion Detected: Function '{node.name}' in {filepath.name} uses 'try...except'. Use 'pytest.raises()' instead."
                        )

                # 5. Fake Mocking の検知
                for body_node in ast.walk(node):
                    if isinstance(body_node, ast.Call):
                        func_name = ""
                        if isinstance(body_node.func, ast.Name):
                            func_name = body_node.func.id
                        elif isinstance(body_node.func, ast.Attribute):
                            func_name = body_node.func.attr

                        if func_name in ("Mock", "MagicMock"):
                            has_spec = any(kw.arg in ("spec", "spec_set", "autospec") for kw in body_node.keywords)
                            if not has_spec:
                                errors.append(
                                    f"Fake Mocking Detected: '{func_name}()' used without 'spec' or 'autospec' in {filepath.name}."
                                )

                docstring = ast.get_docstring(node)
                if not docstring:
                    errors.append(f"Function '{node.name}' in {filepath.name} lacks a docstring entirely.")
                    continue

                matches = SCENARIO_PATTERN.findall(docstring)
                if not matches:
                    errors.append(f"Function '{node.name}' in {filepath.name} lacks spec ID in docstring.")
                else:
                    scenarios.update(matches)

    return scenarios, errors


def check_feature_packaging(app_dir: Path) -> list[str]:
    errors = []
    if not app_dir.exists():
        return [f"Application directory not found: {app_dir}"]

    for item in app_dir.iterdir():
        if item.is_dir() and item.name != "__pycache__":
            readme_path = item / "README.md"
            spec_path = item / "spec.md"
            py_files = list(item.glob("*.py"))

            if not readme_path.exists():
                errors.append(f"Feature package '{item.name}' lacks a README.md.")
            if not spec_path.exists():
                errors.append(f"Feature package '{item.name}' lacks a spec.md.")
            if not py_files:
                errors.append(f"Feature package '{item.name}' lacks a Python implementation file (*.py).")

    return errors


def check_scripts_readme(scripts_dir: Path) -> list[str]:
    errors = []
    readme_path = scripts_dir / "README.md"
    if not readme_path.exists():
        return ["scripts/README.md not found."]

    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()

    for script_file in scripts_dir.iterdir():
        if script_file.is_file() and script_file.name != "README.md":
            if script_file.suffix in [".py", ".sh"]:
                if script_file.name not in readme_content:
                    errors.append(f"Script '{script_file.name}' is missing from scripts/README.md.")

    return errors


def check_naming_conventions(src_dir: Path) -> list[str]:
    errors = []
    if not src_dir.exists():
        return errors

    # Whitelist for words starting with 'I' + uppercase + lowercase
    whitelist = {"Issue", "Item", "Image", "Index", "Info", "Input", "Invalid", "Init", "Id", "Integration", "Identity"}
    i_prefix_pattern = re.compile(r"^I[A-Z][a-z]")

    domain_dir = src_dir / "domain"
    if domain_dir.exists():
        for filepath in domain_dir.rglob("*.py"):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            if i_prefix_pattern.match(class_name):
                                # Check if it's in whitelist
                                is_whitelisted = any(class_name.startswith(w) for w in whitelist)
                                if not is_whitelisted:
                                    errors.append(
                                        f"Naming Violation: Interface '{class_name}' in {filepath.name} uses 'I' prefix."
                                    )
                except SyntaxError:
                    pass

    infrastructure_dir = src_dir / "infrastructure"
    if infrastructure_dir.exists():
        for filepath in infrastructure_dir.rglob("*.py"):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            for base in node.bases:
                                base_name = ""
                                if isinstance(base, ast.Name):
                                    base_name = base.id
                                elif isinstance(base, ast.Attribute):
                                    base_name = base.attr
                                if base_name and base_name == class_name:
                                    errors.append(
                                        f"Naming Violation: Implementation '{class_name}' in {filepath.name} has the exact same name as its Interface (Alias required). Please add a technical prefix like 'Sql{class_name}'."
                                    )
                except SyntaxError:
                    pass

    return errors


def main():
    workspace_root = Path(__file__).parent.parent
    tests_dir = workspace_root / "tests"
    app_dir = workspace_root / "src" / "application"
    scripts_dir = workspace_root / "scripts"

    all_errors = []

    # 1. Feature-Driven Packaging Validation
    all_errors.extend(check_feature_packaging(app_dir))

    # 2. Scripts README Index Validation
    all_errors.extend(check_scripts_readme(scripts_dir))

    # 3. Naming Conventions Validation
    src_dir = workspace_root / "src"
    all_errors.extend(check_naming_conventions(src_dir))

    # 4. Test Traceability Validation (双方向)

    master_scenarios = extract_scenarios_from_spec(app_dir)

    unit_scenarios, unit_errs = extract_scenarios_from_tests(tests_dir / "unit", is_integration=False)
    integration_scenarios, int_errs = extract_scenarios_from_tests(tests_dir / "integration", is_integration=True)

    all_errors.extend(unit_errs)
    all_errors.extend(int_errs)

    # 3-1. Fake ID Check (捏造の禁止)
    fake_unit = unit_scenarios - master_scenarios
    if fake_unit:
        all_errors.append(f"Fake ID Loophole Detected: Unit tests contain unknown scenarios: {fake_unit}")

    fake_integration = integration_scenarios - master_scenarios
    if fake_integration:
        all_errors.append(f"Fake ID Loophole Detected: Integration tests contain unknown scenarios: {fake_integration}")

    # 3-2. Test Deletion Check (網羅性の強制)
    missing_unit = master_scenarios - unit_scenarios
    if missing_unit:
        all_errors.append(f"Test Deletion Loophole Detected: Missing unit tests for scenarios: {missing_unit}")

    missing_integration = master_scenarios - integration_scenarios
    if missing_integration:
        all_errors.append(f"Test Deletion Loophole Detected: Missing integration tests: {missing_integration}")

    if all_errors:
        print("❌ Architecture Validation Failed!\n")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)

    print("✅ All architecture constraints and SDD traceability requirements are mathematically proven.")
    sys.exit(0)


if __name__ == "__main__":
    main()
