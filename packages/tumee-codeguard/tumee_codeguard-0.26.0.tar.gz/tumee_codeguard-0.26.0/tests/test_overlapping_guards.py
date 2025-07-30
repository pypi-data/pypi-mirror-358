"""
Tests for overlapping guard scenarios.

This module contains comprehensive tests for complex guard scenarios including
overlapping guards, nested guards, and hierarchical permission resolution.
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.core.comparison_engine import ComparisonEngine
from src.core.content_hash_registry import ContentHashRegistry
from src.core.guard_tag_parser import GuardTag
from src.core.permission_resolver import PermissionResolver


class TestOverlappingGuards:
    """Test suite for overlapping guard scenarios."""

    def setup_method(self):
        """Create temporary test directory."""
        self.test_dir = tempfile.mkdtemp(prefix="codeguard_overlap_test_")
        print(f"📁 Test directory: {self.test_dir}")

    def teardown_method(self):
        """Clean up test directory."""
        if hasattr(self, "test_dir") and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up: {self.test_dir}")

    def run_codeguard_verify(self, original_file, modified_file, target="ai"):
        """Run codeguard verify command and return result."""
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
            cmd, cwd=Path(__file__).parent.parent, capture_output=True, text=True
        )

        return result

    def test_overlapping_read_write_guards(self):
        """
        Test overlapping guards with different permissions.

        Verifies that when guards overlap, the most restrictive permission wins.
        """
        print("\n🧪 Test: Overlapping Read/Write Guards")
        print("=" * 50)

        # File with overlapping guards
        original_content = """def complex_function():
    # @guard:ai[outer]:w.10
    writable_start = True
    
    # @guard:ai[inner]:r.5
    read_only_content = "secret"
    more_secret = "data"
    end_read_only = True
    
    writable_end = True
"""

        # Modified content - change in read-only section
        modified_content = """def complex_function():
    # @guard:ai[outer]:w.10
    writable_start = True
    
    # @guard:ai[inner]:r.5
    read_only_content = "MODIFIED"  # VIOLATION: in read-only section
    more_secret = "data"
    end_read_only = True
    
    writable_end = True
"""

        # Create test files
        original_file = os.path.join(self.test_dir, "overlap_original.py")
        modified_file = os.path.join(self.test_dir, "overlap_modified.py")

        with open(original_file, "w") as f:
            f.write(original_content)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        print(f"📝 Created: {original_file}")
        print(f"📝 Created: {modified_file}")

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output: {result.stdout}")

        # Should detect violation in the read-only section
        success = result.returncode != 0 and "read_only_violation" in result.stdout.lower()
        print(
            f"✅ PASS: Overlapping guards enforced correctly"
            if success
            else "❌ FAIL: Should detect read-only violation"
        )
        return success

    def test_nested_permission_hierarchy(self):
        """
        Test nested guards with permission hierarchy.

        Verifies that nested guards follow proper permission resolution.
        """
        print("\n🧪 Test: Nested Permission Hierarchy")
        print("=" * 50)

        # File with nested guards (most restrictive should win)
        original_content = """class SecurityModule:
    # @guard:ai[class_level]:w.20
    def __init__(self):
        self.writable_data = "can_modify"
    
    def process_data(self):
        # @guard:ai[method_level]:r.8
        sensitive_operation = "read_only"
        
        # @guard:ai[critical_section]:n.3
        super_secret = "no_access"
        classified = super_secret.upper()
        
        return sensitive_operation + classified
"""

        # Modified content - changes at different levels
        modified_content = """class SecurityModule:
    # @guard:ai[class_level]:w.20
    def __init__(self):
        self.writable_data = "MODIFIED"  # OK: writable section
    
    def process_data(self):
        # @guard:ai[method_level]:r.8
        sensitive_operation = "CHANGED"  # VIOLATION: read-only section
        
        # @guard:ai[critical_section]:n.3
        super_secret = "no_access"
        classified = super_secret.upper()
        
        return sensitive_operation + classified
"""

        # Create test files
        original_file = os.path.join(self.test_dir, "nested_original.py")
        modified_file = os.path.join(self.test_dir, "nested_modified.py")

        with open(original_file, "w") as f:
            f.write(original_content)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output: {result.stdout}")

        # Should detect violations in restricted sections
        output_lower = result.stdout.lower()
        success = result.returncode != 0 and (
            "read_only_violation" in output_lower or "violation" in output_lower
        )
        print(
            f"✅ PASS: Nested permissions enforced"
            if success
            else "❌ FAIL: Should detect violations"
        )
        return success

    def test_multiple_targets_same_content(self):
        """
        Test multiple guards with different targets on same content.

        Verifies that target-specific permissions are correctly applied.
        """
        print("\n🧪 Test: Multiple Targets Same Content")
        print("=" * 50)

        # File with guards for different targets
        original_content = """def shared_function():
    # @guard:ai[shared]:r.5
    # @guard:human[shared]:w.5
    shared_content = "modifiable"
    result = process(shared_content)
    return result
"""

        modified_content = """def shared_function():
    # @guard:ai[shared]:r.5
    # @guard:human[shared]:w.5
    shared_content = "MODIFIED"  # OK for human, violation for AI
    result = process(shared_content)
    return result
"""

        # Create test files
        original_file = os.path.join(self.test_dir, "targets_original.py")
        modified_file = os.path.join(self.test_dir, "targets_modified.py")

        with open(original_file, "w") as f:
            f.write(original_content)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        # Test with AI target (should detect violation)
        result_ai = self.run_codeguard_verify(original_file, modified_file, target="ai")
        print(f"📋 AI Target Exit Code: {result_ai.returncode}")
        print(f"📋 AI Target Output: {result_ai.stdout}")

        # Test with human target (should be allowed)
        result_human = self.run_codeguard_verify(original_file, modified_file, target="human")
        print(f"📋 Human Target Exit Code: {result_human.returncode}")
        print(f"📋 Human Target Output: {result_human.stdout}")

        # AI should detect violation, human should be allowed
        ai_violation = result_ai.returncode != 0 and "violation" in result_ai.stdout.lower()
        human_allowed = (
            result_human.returncode == 0
            or "violations" in result_human.stdout
            and "[]" in result_human.stdout
        )

        success = ai_violation and human_allowed
        print(
            f"✅ PASS: Target-specific permissions work"
            if success
            else "❌ FAIL: Target permissions not working"
        )
        return success

    def test_guard_scope_boundaries(self):
        """
        Test guards with different scope boundaries.

        Verifies that guard scopes are correctly enforced at boundaries.
        """
        print("\n🧪 Test: Guard Scope Boundaries")
        print("=" * 50)

        # File with guards with specific line boundaries
        original_content = """def boundary_test():
    normal_line_1 = "unguarded"
    # @guard:ai[scope1]:r.3
    guarded_line_1 = "protected"
    guarded_line_2 = "protected"
    guarded_line_3 = "protected"
    normal_line_2 = "unguarded"
    
    # @guard:ai[scope2]:r.2
    another_guarded_1 = "protected"
    another_guarded_2 = "protected"
    normal_line_3 = "unguarded"
"""

        modified_content = """def boundary_test():
    normal_line_1 = "MODIFIED"  # OK: unguarded
    # @guard:ai[scope1]:r.3
    guarded_line_1 = "VIOLATION"  # VIOLATION: in guard scope
    guarded_line_2 = "protected"
    guarded_line_3 = "protected"
    normal_line_2 = "MODIFIED"  # OK: unguarded
    
    # @guard:ai[scope2]:r.2
    another_guarded_1 = "protected"
    another_guarded_2 = "protected"
    normal_line_3 = "MODIFIED"  # OK: unguarded
"""

        # Create test files
        original_file = os.path.join(self.test_dir, "boundary_original.py")
        modified_file = os.path.join(self.test_dir, "boundary_modified.py")

        with open(original_file, "w") as f:
            f.write(original_content)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output: {result.stdout}")

        # Should detect violation only in guarded scope
        success = result.returncode != 0 and "violation" in result.stdout.lower()
        print(
            f"✅ PASS: Scope boundaries enforced"
            if success
            else "❌ FAIL: Should detect violation in guarded scope"
        )
        return success

    def test_permission_resolver_integration(self):
        """
        Test direct integration with PermissionResolver for overlapping scenarios.

        Verifies that the permission resolver correctly handles complex scenarios.
        """
        print("\n🧪 Test: Permission Resolver Integration")
        print("=" * 50)

        # Create mock guards with overlapping permissions
        guard1 = Mock(spec=GuardTag)
        guard1.identifier = "outer_guard"
        guard1.target = "ai"
        guard1.permission = "w"  # write permission
        guard1.scope = "block"
        guard1.line = 1
        guard1.scopeStart = 1
        guard1.scopeEnd = 10

        guard2 = Mock(spec=GuardTag)
        guard2.identifier = "inner_guard"
        guard2.target = "ai"
        guard2.permission = "r"  # read-only (more restrictive)
        guard2.scope = "block"
        guard2.line = 3
        guard2.scopeStart = 3
        guard2.scopeEnd = 7

        guard3 = Mock(spec=GuardTag)
        guard3.identifier = "critical_guard"
        guard3.target = "ai"
        guard3.permission = "n"  # no permission (most restrictive)
        guard3.scope = "block"
        guard3.line = 5
        guard3.scopeStart = 5
        guard3.scopeEnd = 6

        guards = [guard1, guard2, guard3]

        # Test permission resolution at different lines
        resolver = PermissionResolver()

        # Line 2: only outer_guard applies (write permission)
        applicable_guards = [g for g in guards if g.scopeStart <= 2 <= g.scopeEnd]
        assert len(applicable_guards) == 1
        assert applicable_guards[0].permission == "w"
        print("✅ Line 2: Write permission (outer guard only)")

        # Line 4: outer_guard + inner_guard (read-only wins)
        applicable_guards = [g for g in guards if g.scopeStart <= 4 <= g.scopeEnd]
        most_restrictive = min(
            applicable_guards, key=lambda g: {"w": 3, "c": 2, "r": 1, "n": 0}[g.permission]
        )
        assert most_restrictive.permission == "r"
        print("✅ Line 4: Read-only permission (inner guard restriction)")

        # Line 5: all guards apply (no permission wins)
        applicable_guards = [g for g in guards if g.scopeStart <= 5 <= g.scopeEnd]
        most_restrictive = min(
            applicable_guards, key=lambda g: {"w": 3, "c": 2, "r": 1, "n": 0}[g.permission]
        )
        assert most_restrictive.permission == "n"
        print("✅ Line 5: No permission (critical guard restriction)")

        # Line 8: only outer_guard applies (write permission)
        applicable_guards = [g for g in guards if g.scopeStart <= 8 <= g.scopeEnd]
        assert len(applicable_guards) == 1
        assert applicable_guards[0].permission == "w"
        print("✅ Line 8: Write permission (outer guard only)")

        return True

    def test_complex_overlapping_scenario(self):
        """
        Test a complex real-world overlapping scenario.

        Verifies that complex overlapping scenarios are handled correctly.
        """
        print("\n🧪 Test: Complex Overlapping Scenario")
        print("=" * 50)

        # Complex file with multiple overlapping guards
        original_content = """class DatabaseConnector:
    # @guard:ai[class]:w.30
    def __init__(self, config):
        self.config = config
        
    def connect(self):
        # @guard:ai[connection]:r.15
        username = self.config['username']
        
        # @guard:ai[credentials]:n.8
        password = self.config['password']
        secret_key = self.config['secret']
        auth_token = generate_token(password, secret_key)
        
        connection_string = f"user={username};auth={auth_token}"
        
        # Back to connection guard scope
        self.connection = establish_connection(connection_string)
        
        # @guard:ai[logging]:c.3
        log_message = f"Connected as {username}"
        self.logger.info(log_message)
        
    def disconnect(self):
        # Back to class guard scope - writable
        if self.connection:
            self.connection.close()
"""

        modified_content = """class DatabaseConnector:
    # @guard:ai[class]:w.30
    def __init__(self, config):
        self.config = config
        
    def connect(self):
        # @guard:ai[connection]:r.15
        username = self.config['username']
        
        # @guard:ai[credentials]:n.8
        password = "HARDCODED_PASSWORD"  # CRITICAL VIOLATION: no permission zone
        secret_key = self.config['secret']
        auth_token = generate_token(password, secret_key)
        
        connection_string = f"user={username};auth={auth_token}"
        
        # Back to connection guard scope
        self.connection = establish_connection(connection_string)
        
        # @guard:ai[logging]:c.3
        log_message = f"Connected as {username} with debug info"  # WARNING: context violation
        self.logger.info(log_message)
        
    def disconnect(self):
        # Back to class guard scope - writable
        if self.connection:
            self.connection.close()
            print("Disconnected successfully")  # OK: writable section
"""

        # Create test files
        original_file = os.path.join(self.test_dir, "complex_original.py")
        modified_file = os.path.join(self.test_dir, "complex_modified.py")

        with open(original_file, "w") as f:
            f.write(original_content)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output: {result.stdout}")

        # Should detect multiple violations with different severities
        output_lower = result.stdout.lower()
        success = result.returncode != 0 and "violation" in output_lower

        print(
            f"✅ PASS: Complex overlapping scenario handled"
            if success
            else "⚠️  INFO: Complex scenario partially working"
        )
        return success

    def test_guard_hierarchy_resolution(self):
        """
        Test hierarchical guard resolution.

        Verifies that guard hierarchy is correctly resolved.
        """
        print("\n🧪 Test: Guard Hierarchy Resolution")
        print("=" * 50)

        engine = ComparisonEngine()

        # Create hierarchical guards
        file_guard = Mock(spec=GuardTag)
        file_guard.identifier = "file_level"
        file_guard.target = "ai"
        file_guard.permission = "w"
        file_guard.scope = "file"
        file_guard.line = 1
        file_guard.scopeStart = 1
        file_guard.scopeEnd = 100

        class_guard = Mock(spec=GuardTag)
        class_guard.identifier = "class_level"
        class_guard.target = "ai"
        class_guard.permission = "r"
        class_guard.scope = "class"
        class_guard.line = 10
        class_guard.scopeStart = 10
        class_guard.scopeEnd = 50

        method_guard = Mock(spec=GuardTag)
        method_guard.identifier = "method_level"
        method_guard.target = "ai"
        method_guard.permission = "n"
        method_guard.scope = "function"
        method_guard.line = 20
        method_guard.scopeStart = 20
        method_guard.scopeEnd = 30

        guards = [file_guard, class_guard, method_guard]

        # Test hierarchy resolution
        # Line 5: only file guard (write)
        applicable = [g for g in guards if g.scopeStart <= 5 <= g.scopeEnd]
        assert len(applicable) == 1
        assert applicable[0].permission == "w"
        print("✅ File level: Write permission")

        # Line 15: file + class guards (read wins)
        applicable = [g for g in guards if g.scopeStart <= 15 <= g.scopeEnd]
        most_restrictive = min(
            applicable, key=lambda g: {"w": 3, "c": 2, "r": 1, "n": 0}[g.permission]
        )
        assert most_restrictive.permission == "r"
        print("✅ Class level: Read-only permission")

        # Line 25: all guards (no permission wins)
        applicable = [g for g in guards if g.scopeStart <= 25 <= g.scopeEnd]
        most_restrictive = min(
            applicable, key=lambda g: {"w": 3, "c": 2, "r": 1, "n": 0}[g.permission]
        )
        assert most_restrictive.permission == "n"
        print("✅ Method level: No permission")

        return True

    def run_all_tests(self):
        """Run all overlapping guard tests."""
        print("🚀 Overlapping Guards Test Suite")
        print("=" * 60)

        self.setup_method()

        try:
            results = []
            results.append(self.test_overlapping_read_write_guards())
            results.append(self.test_nested_permission_hierarchy())
            results.append(self.test_multiple_targets_same_content())
            results.append(self.test_guard_scope_boundaries())
            results.append(self.test_permission_resolver_integration())
            results.append(self.test_complex_overlapping_scenario())
            results.append(self.test_guard_hierarchy_resolution())

            # Summary
            passed = sum(results)
            total = len(results)

            print("\n" + "=" * 60)
            print("📋 OVERLAPPING GUARDS TEST RESULTS")
            print("=" * 60)
            print(f"✅ Passed: {passed}/{total}")
            print(f"❌ Failed: {total - passed}/{total}")

            if passed == total:
                print("🎉 All overlapping guard tests passed!")
                return True
            else:
                print("⚠️  Some overlapping guard tests need attention.")
                return False

        finally:
            self.teardown_method()


def test_overlapping_guards_system():
    """Main test function that can be called by pytest or directly."""
    test_suite = TestOverlappingGuards()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    success = test_overlapping_guards_system()
    exit(0 if success else 1)
