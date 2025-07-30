#!/usr/bin/env python3
"""
Comprehensive tests for content movement detection system.

This test suite verifies that the new semantic content hashing system correctly:
1. Detects missing guard tags
2. Detects actual content changes
3. Ignores content movement between files (no false violations)
4. Handles duplicate content with occurrence counting
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional

from src.core.filesystem_access import FileSystemAccess

# Import from src directory
from src.core.validator import CodeGuardValidator


class ContentMovementTestSuite:
    """Test suite for content movement detection."""

    def __init__(self):
        """Initialize test suite with temporary directory."""
        self.test_dir = None
        self.validator = None

    def setup(self):
        """Create temporary test directory and validator."""
        self.test_dir = tempfile.mkdtemp(prefix="codeguard_test_")
        print(f"📁 Created test directory: {self.test_dir}")

        # Create filesystem access with test directory as root
        filesystem_access = FileSystemAccess([self.test_dir])

        # Create validator with semantic comparison enabled
        self.validator = CodeGuardValidator(
            filesystem_access=filesystem_access,
            normalize_whitespace=True,
            normalize_line_endings=True,
            ignore_blank_lines=True,
            ignore_indentation=False,
        )

    def cleanup(self):
        """Remove temporary test directory."""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up test directory: {self.test_dir}")

    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file with given content."""
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    def test_1_missing_tag_detection(self):
        """Test 1: Verify missing guard tags are detected."""
        print("\n🧪 Test 1: Missing Tag Detection")
        print("=" * 50)

        # Original file with guard tag
        original_content = """def calculate_secret():
    # @guard:ai[secret]:r.3
    secret_value = "confidential_data"
    processed = secret_value.upper()
    return processed

def other_function():
    return "normal code"
"""

        # Modified file with guard tag removed but content moved
        modified_content = """def calculate_secret():
    secret_value = "confidential_data"
    processed = secret_value.upper()
    return processed

def other_function():
    return "normal code"
"""

        # Create test files
        original_file = self.create_test_file("original1.py", original_content)
        modified_file = self.create_test_file("modified1.py", modified_content)

        print(f"📝 Created original file: {original_file}")
        print(f"📝 Created modified file: {modified_file}")

        # Run validation
        result = self.validator.validate_files(original_file, modified_file, target="ai")

        print(f"\n📊 Validation Results:")
        print(f"   Status: {result.status}")
        print(f"   Violations found: {result.violation_count}")
        print(f"   Guard tags found: {result.guard_tags_found}")

        if result.violations:
            print(f"\n🚨 Violations detected:")
            for i, violation in enumerate(result.violations, 1):
                print(f"   {i}. {violation.violation_type}: {violation.message}")
                print(f"      Line {violation.line_start}-{violation.line_end}")

        # Expected: Should detect guard tag removal
        if result.violation_count > 0:
            print("✅ PASS: Missing guard tag correctly detected")
            return True
        else:
            print("❌ FAIL: Missing guard tag not detected")
            return False

    def test_2_content_change_detection(self):
        """Test 2: Verify actual content changes trigger violations."""
        print("\n🧪 Test 2: Content Change Detection")
        print("=" * 50)

        # Original file with guarded content
        original_content = """def process_data():
    # @guard:ai[data]:r.3
    sensitive_data = "original_secret"
    result = sensitive_data.encode()
    return result
"""

        # Modified file with actual content change
        modified_content = """def process_data():
    # @guard:ai[data]:r.3
    sensitive_data = "MODIFIED_SECRET"
    result = sensitive_data.encode()
    return result
"""

        # Create test files
        original_file = self.create_test_file("original2.py", original_content)
        modified_file = self.create_test_file("modified2.py", modified_content)

        print(f"📝 Created original file: {original_file}")
        print(f"📝 Created modified file: {modified_file}")

        # Run validation
        result = self.validator.validate_files(original_file, modified_file, target="ai")

        print(f"\n📊 Validation Results:")
        print(f"   Status: {result.status}")
        print(f"   Violations found: {result.violation_count}")
        print(f"   Guard tags found: {result.guard_tags_found}")

        if result.violations:
            print(f"\n🚨 Violations detected:")
            for i, violation in enumerate(result.violations, 1):
                print(f"   {i}. {violation.violation_type}: {violation.message}")
                print(f"      Line {violation.line_start}-{violation.line_end}")
                print(f"      Original: {violation.original_content[:50]}...")
                print(f"      Modified: {violation.modified_content[:50]}...")

        # Expected: Should detect content change violation
        if result.violation_count > 0:
            print("✅ PASS: Content change correctly detected as violation")
            return True
        else:
            print("❌ FAIL: Content change not detected")
            return False

    def test_3_content_movement_no_violation(self):
        """Test 3: Verify content movement between files doesn't trigger violations."""
        print("\n🧪 Test 3: Content Movement (No Violation)")
        print("=" * 50)

        # Simulate content being moved from file1 to file2

        # Original file1 with guarded content
        original_file1_content = """def original_function():
    # @guard:ai[movetest]:r.3
    moveable_content = "this will move"
    processed = moveable_content.upper()
    return processed
"""

        # Original file2 empty
        original_file2_content = """def empty_function():
    pass
"""

        # Modified file1 with content removed
        modified_file1_content = """def original_function():
    pass
"""

        # Modified file2 with content moved in
        modified_file2_content = """def empty_function():
    pass

def new_function():
    # @guard:ai[movetest]:r.3
    moveable_content = "this will move"
    processed = moveable_content.upper()
    return processed
"""

        # Create test files
        original_file1 = self.create_test_file("original_file1.py", original_file1_content)
        original_file2 = self.create_test_file("original_file2.py", original_file2_content)
        modified_file1 = self.create_test_file("modified_file1.py", modified_file1_content)
        modified_file2 = self.create_test_file("modified_file2.py", modified_file2_content)

        print(f"📝 Created original file1: {original_file1}")
        print(f"📝 Created original file2: {original_file2}")
        print(f"📝 Created modified file1: {modified_file1}")
        print(f"📝 Created modified file2: {modified_file2}")

        # Register original content in hash registry by validating both files first
        print("\n📋 Registering original content...")
        result1_orig = self.validator.validate_files(original_file1, original_file1, target="ai")
        result2_orig = self.validator.validate_files(original_file2, original_file2, target="ai")

        # Now validate the movement
        print("\n🔍 Validating content movement...")
        result1 = self.validator.validate_files(original_file1, modified_file1, target="ai")
        result2 = self.validator.validate_files(original_file2, modified_file2, target="ai")

        print(f"\n📊 File1 Validation Results:")
        print(f"   Status: {result1.status}")
        print(f"   Violations found: {result1.violation_count}")

        print(f"\n📊 File2 Validation Results:")
        print(f"   Status: {result2.status}")
        print(f"   Violations found: {result2.violation_count}")

        total_violations = result1.violation_count + result2.violation_count

        if result1.violations or result2.violations:
            print(f"\n🚨 Violations detected:")
            for i, violation in enumerate(result1.violations + result2.violations, 1):
                print(f"   {i}. {violation.violation_type}: {violation.message}")

        # Expected: Should NOT detect violations for content movement
        if total_violations == 0:
            print("✅ PASS: Content movement correctly ignored (no false violations)")
            return True
        else:
            print("❌ FAIL: Content movement incorrectly flagged as violation")
            return False

    def test_4_duplicate_content_handling(self):
        """Test 4: Verify duplicate content with occurrence counting."""
        print("\n🧪 Test 4: Duplicate Content Handling")
        print("=" * 50)

        # Original file with duplicate guarded content
        original_content = """def function1():
    # @guard:ai[dup]:r.2
    duplicate_content = "same content"
    return duplicate_content

def function2():
    # @guard:ai[dup]:r.2
    duplicate_content = "same content"
    return duplicate_content
"""

        # Modified file with one instance changed
        modified_content = """def function1():
    # @guard:ai[dup]:r.2
    duplicate_content = "CHANGED content"
    return duplicate_content

def function2():
    # @guard:ai[dup]:r.2
    duplicate_content = "same content"
    return duplicate_content
"""

        # Create test files
        original_file = self.create_test_file("original4.py", original_content)
        modified_file = self.create_test_file("modified4.py", modified_content)

        print(f"📝 Created original file: {original_file}")
        print(f"📝 Created modified file: {modified_file}")

        # Run validation
        result = self.validator.validate_files(original_file, modified_file, target="ai")

        print(f"\n📊 Validation Results:")
        print(f"   Status: {result.status}")
        print(f"   Violations found: {result.violation_count}")
        print(f"   Guard tags found: {result.guard_tags_found}")

        if result.violations:
            print(f"\n🚨 Violations detected:")
            for i, violation in enumerate(result.violations, 1):
                print(f"   {i}. {violation.violation_type}: {violation.message}")
                print(f"      Line {violation.line_start}-{violation.line_end}")

        # Expected: Should detect exactly one violation (first instance changed)
        if result.violation_count == 1:
            print("✅ PASS: Duplicate content correctly handled (one violation detected)")
            return True
        elif result.violation_count == 0:
            print("❌ FAIL: No violations detected for changed duplicate content")
            return False
        else:
            print(f"❌ FAIL: Expected 1 violation, got {result.violation_count}")
            return False

    def test_5_whitespace_normalization(self):
        """Test 5: Verify whitespace/formatting changes don't trigger violations."""
        print("\n🧪 Test 5: Whitespace Normalization")
        print("=" * 50)

        # Original file with specific formatting
        original_content = """def format_test():
    # @guard:ai[format]:r.3
    data = "test"
    result = data.strip()
    return result
"""

        # Modified file with different whitespace but same content
        modified_content = """def format_test():
    # @guard:ai[format]:r.3
    data    =    "test"
    result   =   data.strip()
    return result
"""

        # Create test files
        original_file = self.create_test_file("original5.py", original_content)
        modified_file = self.create_test_file("modified5.py", modified_content)

        print(f"📝 Created original file: {original_file}")
        print(f"📝 Created modified file: {modified_file}")

        # Run validation
        result = self.validator.validate_files(original_file, modified_file, target="ai")

        print(f"\n📊 Validation Results:")
        print(f"   Status: {result.status}")
        print(f"   Violations found: {result.violation_count}")

        if result.violations:
            print(f"\n🚨 Violations detected:")
            for i, violation in enumerate(result.violations, 1):
                print(f"   {i}. {violation.violation_type}: {violation.message}")

        # Expected: Should NOT detect violations for whitespace-only changes
        if result.violation_count == 0:
            print("✅ PASS: Whitespace changes correctly ignored")
            return True
        else:
            print("❌ FAIL: Whitespace changes incorrectly flagged as violations")
            return False

    def run_all_tests(self):
        """Run all test cases."""
        print("🚀 Starting Content Movement Detection Test Suite")
        print("=" * 60)

        self.setup()

        try:
            test_results = []

            # Run all tests
            test_results.append(("Missing Tag Detection", self.test_1_missing_tag_detection()))
            test_results.append(
                ("Content Change Detection", self.test_2_content_change_detection())
            )
            test_results.append(
                ("Content Movement (No Violation)", self.test_3_content_movement_no_violation())
            )
            test_results.append(
                ("Duplicate Content Handling", self.test_4_duplicate_content_handling())
            )
            test_results.append(
                ("Whitespace Normalization", self.test_5_whitespace_normalization())
            )

            # Summary
            print("\n" + "=" * 60)
            print("📋 TEST RESULTS SUMMARY")
            print("=" * 60)

            passed = 0
            failed = 0

            for test_name, result in test_results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
                if result:
                    passed += 1
                else:
                    failed += 1

            print(f"\n📊 Overall Results: {passed} passed, {failed} failed")

            if failed == 0:
                print(
                    "🎉 All tests passed! Content movement detection system is working correctly."
                )
                return True
            else:
                print("⚠️  Some tests failed. Review implementation.")
                return False

        finally:
            self.cleanup()


def main():
    """Main test runner."""
    test_suite = ContentMovementTestSuite()
    success = test_suite.run_all_tests()

    if success:
        print("\n✅ Content movement detection system verification complete!")
        exit(0)
    else:
        print("\n❌ Tests failed - system needs review")
        exit(1)


if __name__ == "__main__":
    main()
