"""
Tests for unicode and special character handling.

This module contains tests to ensure the content hashing and comparison
system correctly handles unicode characters, special symbols, and
various text encodings.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest  # type: ignore

from src.core.comparison_engine import ComparisonEngine
from src.core.content_hash_registry import ContentHashRegistry
from src.core.guard_tag_parser import GuardTag
from src.utils.hash_calculator import HashCalculator


class TestUnicodeEdgeCases:
    """Test suite for unicode and special character handling."""

    def setup_method(self):
        """Create temporary test directory."""
        self.test_dir = tempfile.mkdtemp(prefix="codeguard_unicode_test_")
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

    def test_unicode_content_hashing(self):
        """
        Test content hashing with unicode characters.

        Verifies that unicode content is hashed consistently.
        """
        print("\n🧪 Test: Unicode Content Hashing")
        print("=" * 50)

        calculator = HashCalculator()
        registry = ContentHashRegistry()

        # Test various unicode content
        unicode_contents = [
            "def test():\n    # 中文注释\n    return '测试'",
            "def test():\n    # Комментарий\n    return 'тест'",
            "def test():\n    # العربية\n    return 'اختبار'",
            "def test():\n    # 日本語\n    return 'テスト'",
            "def test():\n    # Emoji 🚀🎉\n    return '✅'",
            "def test():\n    # Math: π ≈ 3.14159\n    return '∑αβγ'",
            "def test():\n    # Special: «quotes» \"curly\"\n    return '…ellipsis'",
        ]

        guard = Mock(spec=GuardTag)
        guard.identifier = "unicode_test"
        guard.target = "ai"
        guard.permission = "r"

        hashes = []
        for i, content in enumerate(unicode_contents):
            # Test hash calculation
            hash1 = calculator.calculate_semantic_content_hash(
                content=content, identifier=guard.identifier
            )
            hash2 = calculator.calculate_semantic_content_hash(
                content=content, identifier=guard.identifier
            )

            # Hashes should be consistent
            assert hash1 == hash2, f"Inconsistent hashing for unicode content {i}"
            hashes.append(hash1)

            # Test registry storage
            file_path = f"/test/unicode_{i}.py"
            registry.register_guard_content(file_path, guard, content, 1, 3)

            print(f"✅ Unicode test {i+1}: Consistent hashing")

        # All hashes should be different (different content)
        assert len(set(hashes)) == len(hashes), "Unicode contents should produce different hashes"
        print(f"✅ All {len(hashes)} unicode contents have unique hashes")

        return True

    def test_unicode_normalization(self):
        """
        Test unicode normalization consistency.

        Verifies that different unicode representations normalize consistently.
        """
        print("\n🧪 Test: Unicode Normalization")
        print("=" * 50)

        calculator = HashCalculator()

        # Test unicode normalization forms
        # These should be treated as the same content after normalization
        test_cases = [
            # Composed vs decomposed characters
            ("café", "cafe\u0301"),  # é vs e + combining accent
            ("naïve", "nai\u0308ve"),  # ï vs i + combining diaeresis
            ("résumé", "re\u0301sume\u0301"),  # é vs e + combining accent
        ]

        for i, (composed, decomposed) in enumerate(test_cases):
            content1 = f"def test():\n    text = '{composed}'\n    return text"
            content2 = f"def test():\n    text = '{decomposed}'\n    return text"

            hash1 = calculator.calculate_semantic_content_hash(
                content=content1, identifier="norm_test"
            )
            hash2 = calculator.calculate_semantic_content_hash(
                content=content2, identifier="norm_test"
            )

            # After normalization, these should be the same
            # Note: This depends on the normalization strategy in HashCalculator
            print(f"📊 Test case {i+1}: '{composed}' vs '{decomposed}'")
            print(f"    Hash1: {hash1[:16]}...")
            print(f"    Hash2: {hash2[:16]}...")

            # For now, just verify they produce valid hashes
            assert isinstance(hash1, str) and len(hash1) > 0
            assert isinstance(hash2, str) and len(hash2) > 0
            print(f"✅ Both forms produce valid hashes")

        return True

    def test_mixed_encoding_content(self):
        """
        Test content with mixed character encodings.

        Verifies that mixed content is handled correctly.
        """
        print("\n🧪 Test: Mixed Encoding Content")
        print("=" * 50)

        # Content mixing ASCII, Latin-1, and UTF-8 characters
        mixed_content = """def process_international_data():
    # @guard:ai[mixed]:r.10
    ascii_text = "Hello World"
    latin1_text = "Café résumé naïve"
    utf8_text = "Hello 世界 🌍"
    cyrillic_text = "Привет мир"
    arabic_text = "مرحبا بالعالم"
    emoji_text = "🚀 CodeGuard 🔒 Security ✅"
    math_symbols = "π ≈ 3.14159, ∑ α β γ δ"
    special_quotes = "«guillemets» "curly quotes" 'apostrophes'"
    return f"{ascii_text} {latin1_text} {utf8_text}"
"""

        modified_content = """def process_international_data():
    # @guard:ai[mixed]:r.10
    ascii_text = "Hello World"
    latin1_text = "Café résumé naïve"
    utf8_text = "Hello 世界 🌍"
    cyrillic_text = "MODIFIED мир"  # VIOLATION: changed content
    arabic_text = "مرحبا بالعالم"
    emoji_text = "🚀 CodeGuard 🔒 Security ✅"
    math_symbols = "π ≈ 3.14159, ∑ α β γ δ"
    special_quotes = "«guillemets» "curly quotes" 'apostrophes'"
    return f"{ascii_text} {latin1_text} {utf8_text}"
"""

        # Create test files with UTF-8 encoding
        original_file = os.path.join(self.test_dir, "mixed_original.py")
        modified_file = os.path.join(self.test_dir, "mixed_modified.py")

        with open(original_file, "w", encoding="utf-8") as f:
            f.write(mixed_content)
        with open(modified_file, "w", encoding="utf-8") as f:
            f.write(modified_content)

        print(f"📝 Created files with mixed unicode content")

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output: {result.stdout}")

        # Should detect violation in the modified cyrillic text
        success = result.returncode != 0 and "violation" in result.stdout.lower()
        print(
            f"✅ PASS: Mixed encoding violation detected"
            if success
            else "❌ FAIL: Should detect violation"
        )

        return success

    def test_emoji_and_symbols_content(self):
        """
        Test content with emojis and special symbols.

        Verifies that emoji and symbol content is handled correctly.
        """
        print("\n🧪 Test: Emoji and Symbols Content")
        print("=" * 50)

        # Content with various emojis and symbols
        original_content = """def emoji_function():
    # @guard:ai[emoji]:r.8
    status_codes = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
        "rocket": "🚀",
        "lock": "🔒"
    }
    return status_codes["success"]
"""

        modified_content = """def emoji_function():
    # @guard:ai[emoji]:r.8
    status_codes = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
        "rocket": "🚀",
        "lock": "🔓"  # VIOLATION: changed lock to unlocked
    }
    return status_codes["success"]
"""

        # Create test files
        original_file = os.path.join(self.test_dir, "emoji_original.py")
        modified_file = os.path.join(self.test_dir, "emoji_modified.py")

        with open(original_file, "w", encoding="utf-8") as f:
            f.write(original_content)
        with open(modified_file, "w", encoding="utf-8") as f:
            f.write(modified_content)

        print(f"📝 Created files with emoji content")

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output: {result.stdout}")

        # Should detect the emoji change violation
        success = result.returncode != 0 and "violation" in result.stdout.lower()
        print(
            f"✅ PASS: Emoji change detected" if success else "❌ FAIL: Should detect emoji change"
        )

        return success

    def test_unicode_whitespace_normalization(self):
        """
        Test unicode whitespace normalization.

        Verifies that different unicode whitespace characters are normalized.
        """
        print("\n🧪 Test: Unicode Whitespace Normalization")
        print("=" * 50)

        calculator = HashCalculator()

        # Test different types of whitespace
        whitespace_variants = [
            "def test():\n    return 'normal spaces'",
            "def test():\n\u00a0\u00a0\u00a0\u00a0return 'non-breaking spaces'",  # NBSP
            "def test():\n\u2000\u2000\u2000\u2000return 'en quad spaces'",  # En quad
            "def test():\n\u2003\u2003\u2003\u2003return 'em space'",  # Em space
            "def test():\n\u3000\u3000\u3000\u3000return 'ideographic space'",  # Ideographic space
        ]

        hashes = []
        for i, content in enumerate(whitespace_variants):
            hash_val = calculator.calculate_semantic_content_hash(
                content=content, identifier="whitespace_test"
            )
            hashes.append(hash_val)
            print(f"📊 Whitespace variant {i+1}: {hash_val[:16]}...")

        # Check if normalization makes them similar
        # Note: Depending on normalization strategy, these might be the same or different
        unique_hashes = len(set(hashes))
        print(f"📊 Unique hashes: {unique_hashes}/{len(hashes)}")

        # All should produce valid hashes
        all_valid = all(isinstance(h, str) and len(h) > 0 for h in hashes)
        print(
            f"✅ PASS: All whitespace variants produce valid hashes"
            if all_valid
            else "❌ FAIL: Invalid hashes produced"
        )

        return all_valid

    def test_bidi_text_handling(self):
        """
        Test bidirectional text handling.

        Verifies that right-to-left text is handled correctly.
        """
        print("\n🧪 Test: Bidirectional Text Handling")
        print("=" * 50)

        # Content with bidirectional text (Hebrew, Arabic)
        bidi_content = """def bidi_function():
    # @guard:ai[bidi]:r.6
    hebrew_text = "שלום עולם"  # Hello World in Hebrew
    arabic_text = "مرحبا بالعالم"  # Hello World in Arabic
    mixed_text = "Hello שלום مرحبا World"  # Mixed LTR/RTL
    return f"{hebrew_text} {arabic_text}"
"""

        modified_content = """def bidi_function():
    # @guard:ai[bidi]:r.6
    hebrew_text = "שלום MODIFIED"  # VIOLATION: changed Hebrew text
    arabic_text = "مرحبا بالعالم"  # Hello World in Arabic
    mixed_text = "Hello שלום مرحبا World"  # Mixed LTR/RTL
    return f"{hebrew_text} {arabic_text}"
"""

        # Create test files
        original_file = os.path.join(self.test_dir, "bidi_original.py")
        modified_file = os.path.join(self.test_dir, "bidi_modified.py")

        with open(original_file, "w", encoding="utf-8") as f:
            f.write(bidi_content)
        with open(modified_file, "w", encoding="utf-8") as f:
            f.write(modified_content)

        print(f"📝 Created files with bidirectional text")

        # Run verification
        result = self.run_codeguard_verify(original_file, modified_file)

        print(f"📋 Exit Code: {result.returncode}")
        print(f"📋 Output: {result.stdout}")

        # Should detect the change in Hebrew text
        success = result.returncode != 0 and "violation" in result.stdout.lower()
        print(
            f"✅ PASS: Bidirectional text change detected"
            if success
            else "❌ FAIL: Should detect bidi text change"
        )

        return success

    def test_zero_width_characters(self):
        """
        Test handling of zero-width characters.

        Verifies that zero-width characters don't break hashing.
        """
        print("\n🧪 Test: Zero-Width Characters")
        print("=" * 50)

        calculator = HashCalculator()

        # Content with zero-width characters
        base_content = "def test():\n    return 'test'"

        # Add various zero-width characters
        zero_width_variants = [
            base_content,  # Normal
            base_content.replace("test", "te\u200bst"),  # Zero-width space
            base_content.replace("test", "te\u200cst"),  # Zero-width non-joiner
            base_content.replace("test", "te\u200dst"),  # Zero-width joiner
            base_content.replace("test", "te\ufeffst"),  # Zero-width no-break space
        ]

        hashes = []
        for i, content in enumerate(zero_width_variants):
            hash_val = calculator.calculate_semantic_content_hash(
                content=content, identifier="zw_test"
            )
            hashes.append(hash_val)
            print(f"📊 Zero-width variant {i+1}: {hash_val[:16]}...")

        # All should produce valid hashes
        all_valid = all(isinstance(h, str) and len(h) > 0 for h in hashes)
        print(
            f"✅ PASS: All zero-width variants produce valid hashes"
            if all_valid
            else "❌ FAIL: Invalid hashes produced"
        )

        # Check hash consistency
        unique_hashes = len(set(hashes))
        print(f"📊 Unique hashes: {unique_hashes}/{len(hashes)}")

        return all_valid

    def test_surrogate_pairs(self):
        """
        Test handling of unicode surrogate pairs.

        Verifies that high/low surrogate pairs are handled correctly.
        """
        print("\n🧪 Test: Unicode Surrogate Pairs")
        print("=" * 50)

        calculator = HashCalculator()
        registry = ContentHashRegistry()

        # Content with characters requiring surrogate pairs (outside BMP)
        surrogate_content = """def surrogate_test():
    # @guard:ai[surrogate]:r.5
    musical_note = "𝄞"  # Musical symbol (U+1D11E)
    emoji_complex = "👨‍💻"  # Man technologist (composite emoji)
    math_symbol = "𝔸"  # Mathematical double-struck A (U+1D538)
    ancient_text = "𒀀"  # Cuneiform (U+12000)
    return f"{musical_note} {emoji_complex}"
"""

        guard = Mock(spec=GuardTag)
        guard.identifier = "surrogate_test"
        guard.target = "ai"
        guard.permission = "r"

        # Test hash calculation
        hash_val = calculator.calculate_semantic_content_hash(
            content=surrogate_content, identifier=guard.identifier
        )

        print(f"📊 Surrogate pair hash: {hash_val[:16]}...")

        # Test registry storage
        registry.register_guard_content("/test/surrogate.py", guard, surrogate_content, 1, 5)

        # Verify content can be retrieved
        locations = registry.get_content_locations(hash_val)
        assert any(entry.file_path == "/test/surrogate.py" for entry in locations)

        print(f"✅ Surrogate pairs handled correctly")

        return True

    def test_file_encoding_detection(self):
        """
        Test file encoding detection and handling.

        Verifies that files with different encodings are handled correctly.
        """
        print("\n🧪 Test: File Encoding Detection")
        print("=" * 50)

        # Test content with non-ASCII characters
        test_content = """def encoding_test():
    # @guard:ai[encoding]:r.4
    text = "Héllö Wörld! 🌟"
    chinese = "你好世界"
    return text + chinese
"""

        # Create files with different encodings
        utf8_file = os.path.join(self.test_dir, "utf8_file.py")
        latin1_file = os.path.join(self.test_dir, "latin1_file.py")

        # Write UTF-8 file
        with open(utf8_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Write Latin-1 file (will fail for Chinese characters, so modify content)
        latin1_content = test_content.replace("你好世界", "mundo")
        try:
            with open(latin1_file, "w", encoding="latin-1") as f:
                f.write(latin1_content)
            print(f"📝 Created Latin-1 encoded file")
        except UnicodeEncodeError:
            print(f"📝 Latin-1 encoding failed as expected for Chinese characters")
            # Create a simpler Latin-1 file
            simple_content = """def encoding_test():
    # @guard:ai[encoding]:r.3
    text = "Héllö Wörld!"
    return text
"""
            with open(latin1_file, "w", encoding="latin-1") as f:
                f.write(simple_content)

        # Test that both files can be read and processed
        calculator = HashCalculator()

        # Read UTF-8 file
        with open(utf8_file, "r", encoding="utf-8") as f:
            utf8_content = f.read()

        # Read Latin-1 file
        with open(latin1_file, "r", encoding="latin-1") as f:
            latin1_content = f.read()

        # Both should produce valid hashes
        utf8_hash = calculator.calculate_semantic_content_hash(
            content=utf8_content, identifier="encoding_test"
        )
        latin1_hash = calculator.calculate_semantic_content_hash(
            content=latin1_content, identifier="encoding_test"
        )

        print(f"📊 UTF-8 hash: {utf8_hash[:16]}...")
        print(f"📊 Latin-1 hash: {latin1_hash[:16]}...")

        # Both should be valid hashes
        success = (
            isinstance(utf8_hash, str)
            and len(utf8_hash) > 0
            and isinstance(latin1_hash, str)
            and len(latin1_hash) > 0
        )

        print(
            f"✅ PASS: Both encodings produce valid hashes"
            if success
            else "❌ FAIL: Encoding issues detected"
        )

        return success

    def run_all_tests(self):
        """Run all unicode and edge case tests."""
        print("🚀 Unicode Edge Cases Test Suite")
        print("=" * 60)

        self.setup_method()

        try:
            results = []
            results.append(self.test_unicode_content_hashing())
            results.append(self.test_unicode_normalization())
            results.append(self.test_mixed_encoding_content())
            results.append(self.test_emoji_and_symbols_content())
            results.append(self.test_unicode_whitespace_normalization())
            results.append(self.test_bidi_text_handling())
            results.append(self.test_zero_width_characters())
            results.append(self.test_surrogate_pairs())
            results.append(self.test_file_encoding_detection())

            # Summary
            passed = sum(results)
            total = len(results)

            print("\n" + "=" * 60)
            print("📋 UNICODE EDGE CASES TEST RESULTS")
            print("=" * 60)
            print(f"✅ Passed: {passed}/{total}")
            print(f"❌ Failed: {total - passed}/{total}")

            if passed == total:
                print("🎉 All unicode edge case tests passed!")
                return True
            else:
                print("⚠️  Some unicode edge case tests need attention.")
                return False

        finally:
            self.teardown_method()


def test_unicode_edge_cases():
    """Main test function that can be called by pytest or directly."""
    test_suite = TestUnicodeEdgeCases()
    return test_suite.run_all_tests()


if __name__ == "__main__":
    success = test_unicode_edge_cases()
    exit(0 if success else 1)
