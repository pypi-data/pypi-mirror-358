"""
Workspace analyzer for intelligent gitignore suggestions.
Detects languages, frameworks, build tools, and project characteristics.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..core.interfaces import IFileSystemAccess
from ..core.language.config import (
    FILE_TYPE_PATTERNS,
    LANGUAGE_FILES,
    has_docs_in_directory,
    has_tests_in_directory,
)


@dataclass
class WorkspaceInfo:
    """Information about a workspace detected through analysis."""

    languages: Set[str]
    frameworks: Set[str]
    build_tools: Set[str]
    ides: Set[str]
    package_managers: Set[str]
    has_tests: bool
    has_docs: bool
    project_type: str  # "web", "mobile", "library", "cli", "monorepo", "unknown"


class WorkspaceAnalyzer:
    """Analyzes workspace structure to detect project characteristics."""

    def __init__(self, filesystem_access=None):
        """
        Initialize workspace analyzer.

        Args:
            filesystem_access: IFileSystemAccess instance for secure operations
        """
        self.filesystem_access = filesystem_access

        # Language detection patterns - use centralized configuration
        self.language_files = LANGUAGE_FILES

        # Framework detection patterns
        self.framework_patterns = {
            "react": ["react", "@types/react"],
            "vue": ["vue", "@vue/cli"],
            "angular": ["@angular/core", "angular.json"],
            "svelte": ["svelte", "svelte.config.js"],
            "nextjs": ["next", "next.config.js"],
            "nuxtjs": ["nuxt", "nuxt.config.js"],
            "gatsby": ["gatsby", "gatsby-config.js"],
            "express": ["express"],
            "fastapi": ["fastapi"],
            "django": ["django", "manage.py"],
            "flask": ["flask"],
            "rails": ["rails", "Gemfile"],
            "laravel": ["laravel", "artisan"],
            "spring": ["spring-boot"],
            "dotnet": ["Microsoft.AspNetCore"],
            "electron": ["electron"],
            "ionic": ["@ionic/angular", "@ionic/react", "@ionic/vue"],
            "cordova": ["cordova"],
            "flutter": ["flutter"],
            "reactnative": ["react-native"],
        }

        # Build tool detection
        self.build_tools = {
            "webpack": ["webpack.config.js", "webpack.config.ts"],
            "vite": ["vite.config.js", "vite.config.ts"],
            "rollup": ["rollup.config.js", "rollup.config.ts"],
            "parcel": [".parcelrc", "parcel.json"],
            "esbuild": ["esbuild.config.js"],
            "grunt": ["Gruntfile.js", "Gruntfile.coffee"],
            "gulp": ["gulpfile.js", "gulpfile.ts"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle", "build.gradle.kts"],
            "cmake": ["CMakeLists.txt"],
            "make": ["Makefile", "makefile"],
            "cargo": ["Cargo.toml"],
            "pip": ["requirements.txt", "setup.py"],
            "poetry": ["pyproject.toml"],
            "composer": ["composer.json"],
            "yarn": ["yarn.lock"],
            "npm": ["package-lock.json"],
            "pnpm": ["pnpm-lock.yaml"],
        }

        # IDE detection
        self.ide_patterns = {
            "vscode": [".vscode/"],
            "intellij": [".idea/"],
            "sublime": ["*.sublime-project", "*.sublime-workspace"],
            "vim": [".vimrc", ".vim/"],
            "emacs": [".emacs", ".emacs.d/"],
            "atom": [".atom/"],
        }

    async def analyze_workspace(self, workspace_path: Path) -> WorkspaceInfo:
        """
        Analyze workspace to detect project characteristics.

        Args:
            workspace_path: Path to workspace root

        Returns:
            WorkspaceInfo with detected characteristics
        """
        if not workspace_path.exists() or not workspace_path.is_dir():
            return WorkspaceInfo(
                languages=set(),
                frameworks=set(),
                build_tools=set(),
                ides=set(),
                package_managers=set(),
                has_tests=False,
                has_docs=False,
                project_type="unknown",
            )

        # Gather all files in workspace (shallow scan for performance)
        all_files = []
        all_dirs = []

        try:
            # Scan root directory
            for item in workspace_path.iterdir():
                if item.is_file():
                    all_files.append(item.name)
                elif item.is_dir() and not item.name.startswith("."):
                    all_dirs.append(item.name)

            # Scan one level deep for common directories
            common_dirs = ["src", "lib", "app", "components", "pages", "public", "static"]
            for dir_name in common_dirs:
                dir_path = workspace_path / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    try:
                        for item in dir_path.iterdir():
                            if item.is_file():
                                all_files.append(f"{dir_name}/{item.name}")
                    except (PermissionError, OSError):
                        continue

        except (PermissionError, OSError):
            # If we can't read the directory, return minimal info
            return WorkspaceInfo(
                languages=set(),
                frameworks=set(),
                build_tools=set(),
                ides=set(),
                package_managers=set(),
                has_tests=False,
                has_docs=False,
                project_type="unknown",
            )

        # Detect characteristics
        languages = self._detect_languages(workspace_path, all_files)
        frameworks = await self._detect_frameworks(workspace_path, all_files)
        build_tools = self._detect_build_tools(all_files)
        ides = self._detect_ides(workspace_path, all_dirs)
        package_managers = self._detect_package_managers(all_files)
        has_tests = has_tests_in_directory(workspace_path)
        has_docs = has_docs_in_directory(workspace_path)
        project_type = self._determine_project_type(languages, frameworks, all_files)

        return WorkspaceInfo(
            languages=languages,
            frameworks=frameworks,
            build_tools=build_tools,
            ides=ides,
            package_managers=package_managers,
            has_tests=has_tests,
            has_docs=has_docs,
            project_type=project_type,
        )

    def _detect_languages(self, workspace_path: Path, files: List[str]) -> Set[str]:
        """Detect programming languages used in workspace."""
        detected = set()

        for language, patterns in self.language_files.items():
            for pattern in patterns:
                if pattern.startswith("*."):
                    # Extension pattern
                    ext = pattern[1:]  # Remove *
                    if any(f.endswith(ext) for f in files):
                        detected.add(language)
                        break
                else:
                    # Exact filename
                    if pattern in files:
                        detected.add(language)
                        break

        return detected

    async def _detect_frameworks(self, workspace_path: Path, files: List[str]) -> Set[str]:
        """Detect frameworks by analyzing package.json dependencies."""
        detected = set()

        # Check package.json for JavaScript/TypeScript frameworks
        package_json_path = workspace_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, "r", encoding="utf-8") as f:
                    package_data = json.load(f)

                # Check dependencies and devDependencies
                all_deps = {}
                all_deps.update(package_data.get("dependencies", {}))
                all_deps.update(package_data.get("devDependencies", {}))

                for framework, deps in self.framework_patterns.items():
                    if any(dep in all_deps for dep in deps):
                        detected.add(framework)

            except (json.JSONDecodeError, FileNotFoundError, PermissionError):
                pass

        # Check for framework-specific files
        framework_files = {
            "django": ["manage.py", "settings.py"],
            "rails": ["Gemfile", "config.ru"],
            "laravel": ["artisan", "composer.json"],
            "spring": ["pom.xml"],
            "flutter": ["pubspec.yaml"],
        }

        for framework, framework_file_patterns in framework_files.items():
            if any(pattern in files for pattern in framework_file_patterns):
                detected.add(framework)

        return detected

    def _detect_build_tools(self, files: List[str]) -> Set[str]:
        """Detect build tools used in workspace."""
        detected = set()

        for tool, patterns in self.build_tools.items():
            if any(pattern in files for pattern in patterns):
                detected.add(tool)

        return detected

    def _detect_ides(self, workspace_path: Path, dirs: List[str]) -> Set[str]:
        """Detect IDEs used in workspace."""
        detected = set()

        # Check for IDE directories
        for ide, patterns in self.ide_patterns.items():
            for pattern in patterns:
                if pattern.endswith("/"):
                    # Directory pattern
                    dir_name = pattern[:-1]
                    if dir_name in dirs or (workspace_path / dir_name).exists():
                        detected.add(ide)
                        break

        return detected

    def _detect_package_managers(self, files: List[str]) -> Set[str]:
        """Detect package managers used in workspace."""
        detected = set()

        manager_files = {
            "npm": ["package-lock.json"],
            "yarn": ["yarn.lock"],
            "pnpm": ["pnpm-lock.yaml"],
            "pip": ["requirements.txt"],
            "poetry": ["poetry.lock"],
            "composer": ["composer.lock"],
            "cargo": ["Cargo.lock"],
            "maven": ["pom.xml"],
            "gradle": ["build.gradle"],
        }

        for manager, manager_file_patterns in manager_files.items():
            if any(pattern in files for pattern in manager_file_patterns):
                detected.add(manager)

        return detected

    def _determine_project_type(
        self, languages: Set[str], frameworks: Set[str], files: List[str]
    ) -> str:
        """Determine the type of project based on detected characteristics."""

        # Web frameworks
        web_frameworks = {"react", "vue", "angular", "svelte", "nextjs", "nuxtjs", "gatsby"}
        if frameworks & web_frameworks:
            return "web"

        # Mobile frameworks
        mobile_frameworks = {"flutter", "reactnative", "ionic", "cordova"}
        if frameworks & mobile_frameworks:
            return "mobile"

        # Library indicators
        library_files = ["setup.py", "pyproject.toml", "Cargo.toml", "package.json"]
        if any(f in files for f in library_files):
            # Check if it's a library vs application
            if "src/lib" in " ".join(files) or "lib/" in " ".join(files):
                return "library"

        # CLI tools
        cli_indicators = ["bin/", "cmd/", "cli.py", "main.go"]
        if any(indicator in " ".join(files) for indicator in cli_indicators):
            return "cli"

        # Monorepo indicators
        monorepo_indicators = ["lerna.json", "nx.json", "rush.json", "packages/"]
        if any(
            indicator in files or indicator in " ".join(files) for indicator in monorepo_indicators
        ):
            return "monorepo"

        # Default to web if has common web languages
        if languages & {"javascript", "typescript", "html", "css"}:
            return "web"

        return "unknown"
