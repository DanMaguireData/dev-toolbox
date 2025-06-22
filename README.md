# dev-toolbox
A personal collection of small, useful developer tools for code generation, analysis, and automation.


**Set up Pre-Commit Hooks:**
    This project uses `pre-commit` to automatically run linters and formatters (like Black, Flake8, isort) before each commit, ensuring code quality and consistency.

    *   **Install `pre-commit` (if not already installed via `requirements-dev.txt`):**
        If you haven't installed it via `requirements-dev.txt` or don't have it globally, you can install it:
        ```bash
        pip install pre-commit
        # Alternatively, on macOS with Homebrew:
        # brew install pre-commit
        ```
     *   **Install the Git hook scripts:**
        This command reads the `.pre-commit-config.yaml` file (which we will create) and sets up the hooks for this repository. You only need to run this once per clone/setup.
        ```bash
        pre-commit install
        ```
        Now, `pre-commit` will automatically run its configured checks whenever you run `git commit`. If any checks fail, the commit will be aborted, allowing you to fix the issues.

    *   **Useful Pre-Commit Commands:**
        *   **Update hook versions:** To update the hooks to their latest versions as defined in your `.pre-commit-config.yaml` (or their repositories):
            ```bash
            pre-commit autoupdate
            ```
        *   **Run manually on all files:** If you want to run all pre-commit hooks across all files at any time:
            ```bash
            pre-commit run --all-files
            ```
        *   **Skip pre-commit hooks (use with caution):** If you need to make a commit without running the hooks (e.g., for a work-in-progress commit you don't intend to push yet):
            ```bash
            git commit --no-verify
            ```
