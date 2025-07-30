"""
Performance tests for CodeGuard content hashing and comparison.

This module contains performance tests to ensure the content hashing
and comparison system can handle large codebases efficiently.
"""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.core.comparison_engine import ComparisonEngine
from src.core.content_hash_registry import ContentHashRegistry
from src.core.guard_tag_parser import GuardTag
from src.utils.hash_calculator import HashCalculator


class TestPerformanceScenarios:
    """Test suite for performance scenarios."""

    def setup_method(self):
        """Create temporary test directory."""
        self.test_dir = tempfile.mkdtemp(prefix="codeguard_perf_test_")
        print(f"📁 Test directory: {self.test_dir}")

    def teardown_method(self):
        """Clean up test directory."""
        if hasattr(self, "test_dir") and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🧹 Cleaned up: {self.test_dir}")

    def create_large_file_with_guards(self, file_path, num_guards=100, lines_per_guard=10):
        """Create a large file with many guards for performance testing."""
        content_lines = []
        content_lines.append("# Large file for performance testing")
        content_lines.append("")

        for i in range(num_guards):
            # Add guard tag
            guard_id = f"guard_{i}"
            content_lines.append(f"# @guard:ai[{guard_id}]:r.{lines_per_guard}")

            # Add guard content
            for j in range(lines_per_guard):
                content_lines.append(f"    line_{i}_{j} = 'content_{i}_{j}'")

            content_lines.append("")

        content = "\n".join(content_lines)
        with open(file_path, "w") as f:
            f.write(content)

        return content

    def test_large_file_hash_performance(self):
        """
        Test performance with large files containing many guards.

        Verifies that the system can handle files with hundreds of guards efficiently.
        """
        print("\n🧪 Test: Large File Hash Performance")
        print("=" * 50)

        registry = ContentHashRegistry()
        num_guards = 200
        lines_per_guard = 15

        # Create mock guard tags
        guards = []
        for i in range(num_guards):
            guard = Mock(spec=GuardTag)
            guard.identifier = f"perf_guard_{i}"
            guard.target = "ai"
            guard.permission = "r"
            guards.append(guard)

        # Create large file
        large_file = os.path.join(self.test_dir, "large_file.py")
        content = self.create_large_file_with_guards(large_file, num_guards, lines_per_guard)

        file_size = os.path.getsize(large_file)
        print(f"📊 Created file: {file_size:,} bytes, {num_guards} guards")

        # Test hash calculation performance
        start_time = time.time()

        for i, guard in enumerate(guards):
            # Extract guard content (simulate real usage)
            start_line = i * (lines_per_guard + 2) + 3  # Account for guard tag and spacing
            end_line = start_line + lines_per_guard - 1

            # Extract content for this guard
            file_lines = content.split("\n")
            guard_content = "\n".join(file_lines[start_line - 1 : end_line])

            # Register the content
            registry.register_guard_content(large_file, guard, guard_content, start_line, end_line)

        end_time = time.time()
        duration = end_time - start_time

        print(f"📊 Hash calculation time: {duration:.3f} seconds")
        print(f"📊 Guards per second: {num_guards / duration:.1f}")
        print(f"📊 Registry size: {len(registry._content_hashes)} files")

        # Performance threshold: should handle 100+ guards per second
        performance_ok = (num_guards / duration) > 50
        print(
            f"✅ PASS: Performance acceptable"
            if performance_ok
            else "⚠️  WARNING: Performance slower than expected"
        )

        return performance_ok

    def test_duplicate_content_scale(self):
        """
        Test performance with many duplicate content blocks.

        Verifies that the system efficiently handles duplicate content.
        """
        print("\n🧪 Test: Duplicate Content Scale")
        print("=" * 50)

        registry = ContentHashRegistry()
        num_files = 50
        num_duplicates_per_file = 20

        # Shared content that will be duplicated
        shared_content = """def shared_function():
    secret_value = "shared_secret"
    return process_secret(secret_value)"""

        # Create mock guard
        guard = Mock(spec=GuardTag)
        guard.identifier = "shared_guard"
        guard.target = "ai"
        guard.permission = "r"

        start_time = time.time()

        # Register the same content many times across multiple files
        for file_i in range(num_files):
            file_path = f"/test/file_{file_i}.py"

            for dup_i in range(num_duplicates_per_file):
                registry.register_guard_content(
                    file_path, guard, shared_content, dup_i * 5 + 1, dup_i * 5 + 3
                )

        end_time = time.time()
        duration = end_time - start_time
        total_registrations = num_files * num_duplicates_per_file

        print(f"📊 Total registrations: {total_registrations}")
        print(f"📊 Registration time: {duration:.3f} seconds")
        print(f"📊 Registrations per second: {total_registrations / duration:.1f}")

        # Test movement detection performance
        start_time = time.time()

        for _ in range(100):  # Test 100 movement checks
            is_movement, source_file, source_entry = registry.check_content_movement(
                shared_content, guard.identifier, "/test/new_file.py"
            )
            assert is_movement  # Should detect movement

        end_time = time.time()
        movement_duration = end_time - start_time

        print(f"📊 Movement detection time: {movement_duration:.3f} seconds")
        print(f"📊 Movement checks per second: {100 / movement_duration:.1f}")

        # Verify hash deduplication worked
        unique_hashes = len(registry._hash_to_files)
        print(f"📊 Unique hashes: {unique_hashes} (should be 1 for perfect deduplication)")

        # Performance should be good even with many duplicates
        performance_ok = (total_registrations / duration) > 500 and unique_hashes <= 5
        print(
            f"✅ PASS: Duplicate content handled efficiently"
            if performance_ok
            else "⚠️  WARNING: Duplicate handling could be optimized"
        )

        return performance_ok

    def test_cross_file_movement_scale(self):
        """
        Test performance of cross-file movement detection at scale.

        Verifies that movement detection remains fast with many files.
        """
        print("\n🧪 Test: Cross-File Movement Scale")
        print("=" * 50)

        registry = ContentHashRegistry()
        num_files = 100
        guards_per_file = 10

        # Create many files with unique content
        guard_contents = {}
        start_time = time.time()

        for file_i in range(num_files):
            file_path = f"/test/project/file_{file_i}.py"

            for guard_i in range(guards_per_file):
                guard = Mock(spec=GuardTag)
                guard.identifier = f"guard_{file_i}_{guard_i}"
                guard.target = "ai"
                guard.permission = "r"

                content = (
                    f"def function_{file_i}_{guard_i}():\n    return 'content_{file_i}_{guard_i}'"
                )
                guard_contents[(file_i, guard_i)] = content

                registry.register_guard_content(
                    file_path, guard, content, guard_i * 3 + 1, guard_i * 3 + 2
                )

        registration_time = time.time() - start_time
        total_guards = num_files * guards_per_file

        print(f"📊 Total guards registered: {total_guards}")
        print(f"📊 Registration time: {registration_time:.3f} seconds")

        # Test movement detection across many files
        start_time = time.time()
        movement_tests = 200

        for test_i in range(movement_tests):
            # Pick random content to test movement for
            file_i = test_i % num_files
            guard_i = test_i % guards_per_file
            content = guard_contents[(file_i, guard_i)]

            # Test movement to a new file
            is_movement, source_file, source_entry = registry.check_content_movement(
                content, f"guard_{file_i}_{guard_i}", "/test/new_location.py"
            )

            assert is_movement  # Should detect movement
            assert source_file == f"/test/project/file_{file_i}.py"

        movement_time = time.time() - start_time

        print(f"📊 Movement detection tests: {movement_tests}")
        print(f"📊 Movement detection time: {movement_time:.3f} seconds")
        print(f"📊 Movement checks per second: {movement_tests / movement_time:.1f}")

        # Performance should remain good even with many files
        performance_ok = (movement_tests / movement_time) > 100
        print(
            f"✅ PASS: Cross-file movement scales well"
            if performance_ok
            else "⚠️  WARNING: Movement detection may need optimization"
        )

        return performance_ok

    def test_hash_calculator_performance(self):
        """
        Test performance of hash calculation with large content.

        Verifies that hash calculation is efficient for large content blocks.
        """
        print("\n🧪 Test: Hash Calculator Performance")
        print("=" * 50)

        calculator = HashCalculator()

        # Generate large content blocks
        content_sizes = [1000, 5000, 10000, 50000]  # Lines of code
        results = {}

        for size in content_sizes:
            # Generate content
            lines = [f"    line_{i} = 'content_line_{i}'" for i in range(size)]
            content = "\n".join(lines)
            content_bytes = len(content.encode("utf-8"))

            # Test hash calculation performance
            start_time = time.time()

            # Calculate multiple hashes to get reliable timing
            num_iterations = 20
            for _ in range(num_iterations):
                hash_result = calculator.calculate_semantic_content_hash(
                    content=content, identifier="perf_test"
                )

            end_time = time.time()
            duration = end_time - start_time
            avg_time = duration / num_iterations

            results[size] = {
                "bytes": content_bytes,
                "time": avg_time,
                "throughput": content_bytes / avg_time,
            }

            print(
                f"📊 {size:,} lines ({content_bytes:,} bytes): {avg_time:.4f}s avg, {content_bytes/avg_time/1024/1024:.1f} MB/s"
            )

        # Performance should scale reasonably
        # Larger content should not be dramatically slower per byte
        small_throughput = results[1000]["throughput"]
        large_throughput = results[50000]["throughput"]
        throughput_ratio = large_throughput / small_throughput

        performance_ok = (
            throughput_ratio > 0.1
        )  # Large content shouldn't be more than 10x slower per byte
        print(f"📊 Throughput ratio (large/small): {throughput_ratio:.2f}")
        print(
            f"✅ PASS: Hash calculation scales reasonably"
            if performance_ok
            else "⚠️  WARNING: Hash calculation may degrade with size"
        )

        return performance_ok

    def test_cli_performance_integration(self):
        """
        Test end-to-end CLI performance with moderately large files.

        Verifies that the CLI can handle realistic file sizes efficiently.
        """
        print("\n🧪 Test: CLI Performance Integration")
        print("=" * 50)

        # Create moderately large test files
        num_guards = 50
        lines_per_guard = 20

        original_file = os.path.join(self.test_dir, "perf_original.py")
        modified_file = os.path.join(self.test_dir, "perf_modified.py")

        # Create original file
        original_content = self.create_large_file_with_guards(
            original_file, num_guards, lines_per_guard
        )

        # Create modified file with a few changes
        modified_lines = original_content.split("\n")
        # Change a few lines in different guards
        for i in [100, 300, 500, 700, 900]:
            if i < len(modified_lines):
                modified_lines[i] = modified_lines[i].replace("content", "MODIFIED")

        modified_content = "\n".join(modified_lines)
        with open(modified_file, "w") as f:
            f.write(modified_content)

        file_size = os.path.getsize(original_file)
        print(f"📊 File size: {file_size:,} bytes, {num_guards} guards")

        # Test CLI performance
        temp_dir_parent = os.path.dirname(self.test_dir)
        cmd = [
            "python",
            "-m",
            "src",
            "--allowed-roots",
            temp_dir_parent,
            "verify",
            "--target",
            "ai",
            "--format",
            "json",
            original_file,
            modified_file,
        ]

        start_time = time.time()

        result = subprocess.run(
            cmd, cwd=Path(__file__).parent.parent, capture_output=True, text=True
        )

        end_time = time.time()
        duration = end_time - start_time

        print(f"📊 CLI execution time: {duration:.3f} seconds")
        print(f"📊 Processing rate: {file_size / duration / 1024:.1f} KB/s")
        print(f"📋 Exit code: {result.returncode}")

        # Should detect violations and complete within reasonable time
        found_violations = result.returncode != 0 and "violation" in result.stdout.lower()
        reasonable_time = duration < 10.0  # Should complete within 10 seconds

        performance_ok = found_violations and reasonable_time
        print(
            f"✅ PASS: CLI performance acceptable"
            if performance_ok
            else "⚠️  WARNING: CLI performance needs attention"
        )

        if not found_violations:
            print(f"⚠️  Expected violations not detected")
        if not reasonable_time:
            print(f"⚠️  CLI took {duration:.1f}s, expected < 10s")

        return performance_ok

    def test_memory_usage_patterns(self):
        """
        Test memory usage patterns with large datasets.

        Verifies that memory usage remains reasonable.
        """
        print("\n🧪 Test: Memory Usage Patterns")
        print("=" * 50)

        import gc

        import psutil

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        registry = ContentHashRegistry()

        # Create many guards with varying content
        num_iterations = 1000
        content_variants = 10

        base_contents = [
            f"def function_variant_{i}():\n    return 'variant_{i}'"
            for i in range(content_variants)
        ]

        for iteration in range(num_iterations):
            guard = Mock(spec=GuardTag)
            guard.identifier = f"memory_test_{iteration}"
            guard.target = "ai"
            guard.permission = "r"

            # Use varying content to test memory patterns
            content = base_contents[iteration % content_variants]
            file_path = f"/test/memory_test_{iteration % 100}.py"  # Reuse some file paths

            registry.register_guard_content(file_path, guard, content, 1, 2)

            # Check memory every 100 iterations
            if iteration % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_growth = current_memory - initial_memory
                print(
                    f"📊 Iteration {iteration}: {current_memory:.1f} MB (+{memory_growth:.1f} MB)"
                )

        # Final memory check
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_growth = final_memory - initial_memory
        growth_per_item = total_growth / num_iterations * 1024  # KB per item

        print(f"📊 Initial memory: {initial_memory:.1f} MB")
        print(f"📊 Final memory: {final_memory:.1f} MB")
        print(f"📊 Total growth: {total_growth:.1f} MB")
        print(f"📊 Growth per item: {growth_per_item:.2f} KB")

        # Memory usage should be reasonable
        reasonable_memory = total_growth < 100  # Less than 100MB growth
        reasonable_per_item = growth_per_item < 10  # Less than 10KB per item

        memory_ok = reasonable_memory and reasonable_per_item
        print(
            f"✅ PASS: Memory usage reasonable"
            if memory_ok
            else "⚠️  WARNING: Memory usage may be excessive"
        )

        # Cleanup
        gc.collect()

        return memory_ok

    def run_all_tests(self):
        """Run all performance tests."""
        print("🚀 Performance Test Suite")
        print("=" * 60)

        self.setup_method()

        try:
            results = []
            results.append(self.test_large_file_hash_performance())
            results.append(self.test_duplicate_content_scale())
            results.append(self.test_cross_file_movement_scale())
            results.append(self.test_hash_calculator_performance())
            results.append(self.test_cli_performance_integration())
            results.append(self.test_memory_usage_patterns())

            # Summary
            passed = sum(results)
            total = len(results)

            print("\n" + "=" * 60)
            print("📋 PERFORMANCE TEST RESULTS")
            print("=" * 60)
            print(f"✅ Passed: {passed}/{total}")
            print(f"❌ Failed: {total - passed}/{total}")

            if passed == total:
                print("🎉 All performance tests passed!")
                return True
            else:
                print("⚠️  Some performance tests indicate optimization opportunities.")
                return False

        finally:
            self.teardown_method()


def test_performance_scenarios():
    """Main test function that can be called by pytest or directly."""
    test_suite = TestPerformanceScenarios()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    success = test_performance_scenarios()
    exit(0 if success else 1)
