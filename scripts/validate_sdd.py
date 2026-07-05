#!/usr/import/env python3
"""
validate_sdd.py

以下の3つのアーキテクチャ制約を自動検証する統合Linterです。
1. テストの仕様ID（SDD）紐付け検証: テストコードのDocString内に仕様ID（[SCENARIO-XX]）があるか。
2. Application層検証: src/application/ 内に README.md, spec.md, *.py が揃っているか。
3. スクリプトのインデックス検証: scripts/ 内の全スクリプトが scripts/README.md に記載されているか。
"""

import ast
import re
import sys
from pathlib import Path

SCENARIO_PATTERN = re.compile(r"\[SCENARIO-\d+\]")


def check_test_file(filepath: Path) -> list[str]:
    errors = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return [f"SyntaxError in {filepath}: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            docstring = ast.get_docstring(node)
            if not docstring:
                errors.append(f"Function '{node.name}' in {filepath.name} lacks a docstring entirely.")
                continue

            if not SCENARIO_PATTERN.search(docstring):
                errors.append(f"Function '{node.name}' in {filepath.name} lacks spec ID in docstring.")

    return errors


def check_feature_packaging(app_dir: Path) -> list[str]:
    errors = []
    if not app_dir.exists():
        return [f"Application directory not found: {app_dir}"]

    # src/application 直下のディレクトリを走査
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

    # スクリプトファイルを走査（*.py, *.sh）
    for script_file in scripts_dir.iterdir():
        if script_file.is_file() and script_file.name != "README.md":
            if script_file.suffix in [".py", ".sh"]:
                if script_file.name not in readme_content:
                    errors.append(f"Script '{script_file.name}' is missing from scripts/README.md.")

    return errors


def main():
    workspace_root = Path(__file__).parent.parent
    tests_dir = workspace_root / "tests"
    app_dir = workspace_root / "src" / "application"
    scripts_dir = workspace_root / "scripts"

    all_errors = []

    # 1. Test Traceability Validation
    if tests_dir.exists():
        for test_file in tests_dir.rglob("test_*.py"):
            all_errors.extend(check_test_file(test_file))

    # 2. Feature-Driven Packaging Validation
    all_errors.extend(check_feature_packaging(app_dir))

    # 3. Scripts README Index Validation
    all_errors.extend(check_scripts_readme(scripts_dir))

    if all_errors:
        print("❌ Architecture Validation Failed!\n")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)

    print("✅ All architecture constraints and SDD traceability requirements are satisfied.")
    sys.exit(0)


if __name__ == "__main__":
    main()
