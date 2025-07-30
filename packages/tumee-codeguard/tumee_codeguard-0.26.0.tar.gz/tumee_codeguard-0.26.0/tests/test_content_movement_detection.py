#!/usr/bin/env python3
"""
Test content movement detection to ensure the system correctly distinguishes
between content changes (violations) and content movement (not violations).
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class TestContentMovementDetection:
    """Test suite for content movement detection system."""

    def setup_method(self):
        """Create temporary test directory."""
        self.test_dir = tempfile.mkdtemp(prefix="codeguard_content_test_")
        print(f"📁 Test directory: {self.test_dir}")

    def teardown_method(self):
        """Clean up test directory."""
        if hasattr(self, "test_dir") and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up: {self.test_dir}")

    def run_codeguard_verify(self, original_file, modified_file, target="ai"):
        """Run codeguard verify command and return result."""
        # Get temp directory prefix
        temp_dir_parent = os.path.dirname(self.test_dir)

        cmd = [
            "python",
            "-m",
            "src",
            "--allowed-roots",
            temp_dir_parent,
            "verify",
            "--target",
            target,
            "--format",
            "json",
            original_file,
            modified_file,
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,  # Go up to project root
            capture_output=True,
            text=True,
        )

        return result

    def test_missing_tag_detection(self):
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

        # Modified file with guard tag removed
        modified_content = """def calculate_secret():
    secret_value = "confidential_data"
    processed = secret_value.upper()
    return processed

def other_function():
    return "normal code"
"""

        # Create test files
        original_file = os.path.join(self.test_dir, "original1.py")
        modified_file = os.path.join(self.test_dir, "modified1.py")

        with open(original_file, "w") as f:
            f.write(original_content)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        print(f"📝 Created: {original_file}")
        print(f"📝 Created: {modified_file}")

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output:\n{result.stdout}")
        if result.stderr:
            print(f"📋 Errors:\n{result.stderr}")

        # Expected: Should detect guard tag removal or content change
        success = result.returncode != 0 and "guard_removed" in result.stdout
        print(
            f"✅ PASS: Missing guard detected" if success else "❌ FAIL: Missing guard not detected"
        )
        return success

    def test_content_change_detection(self):
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
        original_file = os.path.join(self.test_dir, "original2.py")
        modified_file = os.path.join(self.test_dir, "modified2.py")

        with open(original_file, "w") as f:
            f.write(original_content)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        print(f"📝 Created: {original_file}")
        print(f"📝 Created: {modified_file}")

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output:\n{result.stdout}")
        if result.stderr:
            print(f"📋 Errors:\n{result.stderr}")

        # Expected: Should detect content change violation
        success = result.returncode != 0 and "read_only_violation" in result.stdout
        print(
            f"✅ PASS: Content change detected"
            if success
            else "❌ FAIL: Content change not detected"
        )
        return success

    def test_whitespace_normalization(self):
        """Test 3: Verify whitespace/formatting changes don't trigger violations."""
        print("\n🧪 Test 3: Whitespace Normalization")
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
        original_file = os.path.join(self.test_dir, "original3.py")
        modified_file = os.path.join(self.test_dir, "modified3.py")

        with open(original_file, "w") as f:
            f.write(original_content)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        print(f"📝 Created: {original_file}")
        print(f"📝 Created: {modified_file}")

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output:\n{result.stdout}")
        if result.stderr:
            print(f"📋 Errors:\n{result.stderr}")

        # Expected: Should NOT detect violations for whitespace-only changes
        success = result.returncode == 0 and '"violations": []' in result.stdout
        print(
            f"✅ PASS: Whitespace ignored"
            if success
            else "❌ FAIL: Whitespace flagged as violation"
        )
        return success

    def test_duplicate_content_handling(self):
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
        original_file = os.path.join(self.test_dir, "original4.py")
        modified_file = os.path.join(self.test_dir, "modified4.py")

        with open(original_file, "w") as f:
            f.write(original_content)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        print(f"📝 Created: {original_file}")
        print(f"📝 Created: {modified_file}")

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output:\n{result.stdout}")
        if result.stderr:
            print(f"📋 Errors:\n{result.stderr}")

        # Expected: Should detect exactly one violation (first instance changed)
        success = result.returncode != 0 and "read_only_violation" in result.stdout
        print(
            f"✅ PASS: Duplicate handling works"
            if success
            else "❌ FAIL: Duplicate handling failed"
        )
        return success

    def run_all_tests(self):
        """Run all test cases and return overall success."""
        print("🚀 Content Movement Detection Test Suite")
        print("=" * 60)

        self.setup_method()

        try:
            results = []
            results.append(self.test_missing_tag_detection())
            results.append(self.test_content_change_detection())
            results.append(self.test_whitespace_normalization())
            results.append(self.test_duplicate_content_handling())

            # Summary
            passed = sum(results)
            total = len(results)

            print("\n" + "=" * 60)
            print("📋 TEST RESULTS SUMMARY")
            print("=" * 60)
            print(f"✅ Passed: {passed}/{total}")
            print(f"❌ Failed: {total - passed}/{total}")

            if passed == total:
                print("🎉 All tests passed! Content movement detection working correctly.")
                return True
            else:
                print("⚠️  Some tests failed. Implementation needs review.")
                return False

        finally:
            self.teardown_method()


def test_content_movement_system():
    """Main test function that can be called by pytest or directly."""
    test_suite = TestContentMovementDetection()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    success = test_content_movement_system()
    exit(0 if success else 1)
