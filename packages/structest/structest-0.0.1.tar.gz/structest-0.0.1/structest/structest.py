import argparse
import os
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check test file structure.")
    parser.add_argument("directory", type=str, help="Project root directory")
    return parser.parse_args()


def get_dirs(base_path: str) -> list[str]:
    ignore = {"tests", "__pycache__", ".git", ".venv", "venv"}
    result = []
    for directory in os.listdir(base_path):
        full_path = os.path.join(base_path, directory)
        if os.path.isdir(full_path) and directory not in ignore:
            result.append(directory)
    return result


def find_modules(base_dirs: list[str]) -> set[str]:
    modules = set()
    for base_dir in base_dirs:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    modules.add(file)  # Keep full filename with .py
    return modules


def find_test_files(test_dir: str) -> set[str]:
    tests = set()
    for root, _, files in os.walk(test_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                module_name = file[len("test_") :]  # Keep .py extension
                tests.add(module_name)
    return tests


def main() -> None:
    args = parse_args()
    base_path = args.directory

    if not os.path.isdir(base_path):
        print(f"❌ Directory '{base_path}' does not exist.")
        sys.exit(1)

    source_dirs = get_dirs(base_path)
    modules = find_modules(source_dirs)
    tests = find_test_files("tests")

    missing_tests = modules - tests
    extra_tests = tests - modules

    if missing_tests:
        print("❌ Missing tests for:", ", ".join(sorted(missing_tests)))
    if extra_tests:
        print(
            "❌ Test files without matching modules:",
            ", ".join(sorted(extra_tests)),
        )
    if not missing_tests and not extra_tests:
        print("✅ All test files are correctly named and mapped.")

    if missing_tests or extra_tests:
        sys.exit(1)


if __name__ == "__main__":
    main()
