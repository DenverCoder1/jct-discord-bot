# Style Guide

Please follow the guidelines stated here when contributing to this repository.

## Spacing

- Leave two empty lines between functions outside of a class.
- Leave one empty line between functions inside of a class.
- Leave one empty line between logical blocks of code in the same function.

## Naming

- Use `snake_case` for files, folders, and variables.
- Use `PascalCase` for classes.
- Use `kebab-case` for branch names.

## Auto Formatting

If you want your IDE to help you format your code, search how to set up your IDE to use the `black` formatter.

The formatting and linting dependencies can be installed all at once with `pip install -r requirements-dev.txt`.

To run `black` and `isort` on all files, run `task lint`.
