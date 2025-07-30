"""
Gitignore pattern database for RPC autocomplete functionality.
Provides comprehensive patterns for various development environments.
"""

from typing import Dict, List, TypedDict


class GitignoreSuggestion(TypedDict):
    """Type definition for gitignore suggestion objects."""

    label: str
    detail: str
    documentation: str
    insertText: str


class GitignorePatternsDatabase:
    """Database of gitignore patterns organized by category."""

    def __init__(self):
        self._patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, List[GitignoreSuggestion]]:
        """Initialize the pattern database organized by category."""
        return {
            "dependencies": [
                {
                    "label": "node_modules/",
                    "detail": "Node.js dependencies",
                    "documentation": "Ignores all Node.js package dependencies installed by npm/yarn",
                    "insertText": "node_modules/",
                },
                {
                    "label": "vendor/",
                    "detail": "Vendor dependencies",
                    "documentation": "Ignores vendor directory containing third-party dependencies",
                    "insertText": "vendor/",
                },
                {
                    "label": "bower_components/",
                    "detail": "Bower dependencies",
                    "documentation": "Ignores Bower package dependencies",
                    "insertText": "bower_components/",
                },
            ],
            "build_outputs": [
                {
                    "label": "dist/",
                    "detail": "Distribution folder",
                    "documentation": "Ignores compiled/built distribution files",
                    "insertText": "dist/",
                },
                {
                    "label": "build/",
                    "detail": "Build folder",
                    "documentation": "Ignores build output directory",
                    "insertText": "build/",
                },
                {
                    "label": "out/",
                    "detail": "Output folder",
                    "documentation": "Ignores compilation output directory",
                    "insertText": "out/",
                },
                {
                    "label": "target/",
                    "detail": "Rust/Java build output",
                    "documentation": "Ignores Rust Cargo or Java Maven/Gradle build output",
                    "insertText": "target/",
                },
                {
                    "label": "bin/",
                    "detail": "Binary output",
                    "documentation": "Ignores compiled binary files",
                    "insertText": "bin/",
                },
            ],
            "logs": [
                {
                    "label": "*.log",
                    "detail": "Log files",
                    "documentation": "Ignores all files with .log extension",
                    "insertText": "*.log",
                },
                {
                    "label": "npm-debug.log*",
                    "detail": "NPM debug logs",
                    "documentation": "Ignores NPM debug log files",
                    "insertText": "npm-debug.log*",
                },
                {
                    "label": "yarn-debug.log*",
                    "detail": "Yarn debug logs",
                    "documentation": "Ignores Yarn debug log files",
                    "insertText": "yarn-debug.log*",
                },
                {
                    "label": "yarn-error.log*",
                    "detail": "Yarn error logs",
                    "documentation": "Ignores Yarn error log files",
                    "insertText": "yarn-error.log*",
                },
                {
                    "label": "logs/",
                    "detail": "Log directory",
                    "documentation": "Ignores entire logs directory",
                    "insertText": "logs/",
                },
            ],
            "environment": [
                {
                    "label": ".env",
                    "detail": "Environment variables",
                    "documentation": "Ignores environment configuration file containing secrets",
                    "insertText": ".env",
                },
                {
                    "label": ".env.local",
                    "detail": "Local environment variables",
                    "documentation": "Ignores local environment overrides",
                    "insertText": ".env.local",
                },
                {
                    "label": ".env.*.local",
                    "detail": "Environment overrides",
                    "documentation": "Ignores all local environment override files",
                    "insertText": ".env.*.local",
                },
                {
                    "label": ".env.development.local",
                    "detail": "Development environment",
                    "documentation": "Ignores local development environment variables",
                    "insertText": ".env.development.local",
                },
                {
                    "label": ".env.production.local",
                    "detail": "Production environment",
                    "documentation": "Ignores local production environment variables",
                    "insertText": ".env.production.local",
                },
            ],
            "ide_files": [
                {
                    "label": ".vscode/",
                    "detail": "VS Code settings",
                    "documentation": "Ignores VS Code workspace settings (consider project-specific exceptions)",
                    "insertText": ".vscode/",
                },
                {
                    "label": ".idea/",
                    "detail": "IntelliJ IDEA settings",
                    "documentation": "Ignores IntelliJ IDEA project files",
                    "insertText": ".idea/",
                },
                {
                    "label": "*.sublime-workspace",
                    "detail": "Sublime Text workspace",
                    "documentation": "Ignores Sublime Text workspace files",
                    "insertText": "*.sublime-workspace",
                },
                {
                    "label": "*.sublime-project",
                    "detail": "Sublime Text project",
                    "documentation": "Ignores Sublime Text project files",
                    "insertText": "*.sublime-project",
                },
            ],
            "os_files": [
                {
                    "label": ".DS_Store",
                    "detail": "macOS system file",
                    "documentation": "Ignores macOS Finder metadata files",
                    "insertText": ".DS_Store",
                },
                {
                    "label": "Thumbs.db",
                    "detail": "Windows system file",
                    "documentation": "Ignores Windows thumbnail cache files",
                    "insertText": "Thumbs.db",
                },
                {
                    "label": "Desktop.ini",
                    "detail": "Windows folder config",
                    "documentation": "Ignores Windows folder configuration files",
                    "insertText": "Desktop.ini",
                },
                {
                    "label": "*.tmp",
                    "detail": "Temporary files",
                    "documentation": "Ignores all temporary files",
                    "insertText": "*.tmp",
                },
                {
                    "label": "*.temp",
                    "detail": "Temporary files",
                    "documentation": "Ignores all temp files",
                    "insertText": "*.temp",
                },
            ],
            "editor_files": [
                {
                    "label": "*.swp",
                    "detail": "Vim swap files",
                    "documentation": "Ignores Vim editor swap files",
                    "insertText": "*.swp",
                },
                {
                    "label": "*.swo",
                    "detail": "Vim swap files",
                    "documentation": "Ignores additional Vim swap files",
                    "insertText": "*.swo",
                },
                {
                    "label": "*~",
                    "detail": "Backup files",
                    "documentation": "Ignores editor backup files",
                    "insertText": "*~",
                },
            ],
            "coverage": [
                {
                    "label": "coverage/",
                    "detail": "Test coverage",
                    "documentation": "Ignores test coverage reports",
                    "insertText": "coverage/",
                },
                {
                    "label": ".nyc_output/",
                    "detail": "NYC coverage",
                    "documentation": "Ignores NYC (Node.js) coverage output",
                    "insertText": ".nyc_output/",
                },
                {
                    "label": "lcov.info",
                    "detail": "LCOV coverage report",
                    "documentation": "Ignores LCOV coverage report file",
                    "insertText": "lcov.info",
                },
            ],
            "caches": [
                {
                    "label": ".cache/",
                    "detail": "Cache directory",
                    "documentation": "Ignores general cache directory",
                    "insertText": ".cache/",
                },
                {
                    "label": ".parcel-cache/",
                    "detail": "Parcel cache",
                    "documentation": "Ignores Parcel bundler cache",
                    "insertText": ".parcel-cache/",
                },
                {
                    "label": ".next/",
                    "detail": "Next.js cache",
                    "documentation": "Ignores Next.js build cache",
                    "insertText": ".next/",
                },
                {
                    "label": ".nuxt/",
                    "detail": "Nuxt.js cache",
                    "documentation": "Ignores Nuxt.js build cache",
                    "insertText": ".nuxt/",
                },
            ],
            "python": [
                {
                    "label": "__pycache__/",
                    "detail": "Python cache",
                    "documentation": "Ignores Python bytecode cache",
                    "insertText": "__pycache__/",
                },
                {
                    "label": "*.pyc",
                    "detail": "Python compiled",
                    "documentation": "Ignores Python compiled bytecode files",
                    "insertText": "*.pyc",
                },
                {
                    "label": "*.pyo",
                    "detail": "Python optimized",
                    "documentation": "Ignores Python optimized bytecode files",
                    "insertText": "*.pyo",
                },
                {
                    "label": "venv/",
                    "detail": "Python virtual environment",
                    "documentation": "Ignores Python virtual environment directory",
                    "insertText": "venv/",
                },
                {
                    "label": ".venv/",
                    "detail": "Python virtual environment",
                    "documentation": "Ignores hidden Python virtual environment directory",
                    "insertText": ".venv/",
                },
            ],
            "security": [
                {
                    "label": "*.key",
                    "detail": "Private keys",
                    "documentation": "Ignores private key files",
                    "insertText": "*.key",
                },
                {
                    "label": "*.pem",
                    "detail": "Certificate files",
                    "documentation": "Ignores PEM certificate files",
                    "insertText": "*.pem",
                },
                {
                    "label": "*.p12",
                    "detail": "Certificate bundles",
                    "documentation": "Ignores PKCS#12 certificate bundles",
                    "insertText": "*.p12",
                },
            ],
        }

    def get_all_patterns(self) -> List[GitignoreSuggestion]:
        """Get all patterns flattened into a single list."""
        all_patterns = []
        for category_patterns in self._patterns.values():
            all_patterns.extend(category_patterns)
        return all_patterns

    def get_patterns_by_category(self, category: str) -> List[GitignoreSuggestion]:
        """Get patterns for a specific category."""
        return self._patterns.get(category, [])

    def get_categories(self) -> List[str]:
        """Get list of available categories."""
        return list(self._patterns.keys())

    def search_patterns(self, prefix: str, context: str = "file") -> List[GitignoreSuggestion]:
        """
        Search patterns by prefix with contextual filtering.

        Args:
            prefix: Text prefix to match against
            context: Context hint ("file", "folder", "template")

        Returns:
            List of matching suggestions
        """
        if not prefix:
            return self.get_all_patterns()

        prefix_lower = prefix.lower()
        matches = []

        for pattern in self.get_all_patterns():
            # Check if prefix matches label or detail
            if (
                prefix_lower in pattern["label"].lower()
                or prefix_lower in pattern["detail"].lower()
            ):
                matches.append(pattern)

        # Apply contextual filtering
        if context == "folder":
            # Prioritize directory patterns (ending with /)
            directory_matches = [p for p in matches if p["insertText"].endswith("/")]
            file_matches = [p for p in matches if not p["insertText"].endswith("/")]
            matches = directory_matches + file_matches

        return matches


# Global instance
gitignore_patterns_db = GitignorePatternsDatabase()
