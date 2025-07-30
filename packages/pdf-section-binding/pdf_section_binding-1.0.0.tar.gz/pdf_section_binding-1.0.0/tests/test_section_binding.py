#!/usr/bin/env python3
"""
Test suite for PDF Section Binding functionality.
"""

import unittest
import tempfile
import os
import sys
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


from pdf_section_binding.core import (
    calculate_signature_order,
    SectionBindingProcessor,
)


class TestCalculateSignatureOrder(unittest.TestCase):
    """Test the signature order calculation algorithm."""

    def test_4_page_signature_exact_fit(self):
        """Test 4-page signature with exact number of pages."""
        result = calculate_signature_order(4, 4)
        expected = [4, 1, 3, 2]
        self.assertEqual(result, expected)

    def test_8_page_signature_exact_fit(self):
        """Test 8-page signature with exact number of pages."""
        result = calculate_signature_order(8, 8)
        expected = [8, 1, 7, 2, 6, 3, 5, 4]
        self.assertEqual(result, expected)

    def test_4_page_signature_with_padding(self):
        """Test 4-page signature requiring padding."""
        # 6 pages should be padded to 8 pages (2 signatures of 4)
        result = calculate_signature_order(6, 4)
        expected = [4, 1, 3, 2, 5, 6]  # Second signature only has pages 5,6
        self.assertEqual(result, expected)

    def test_8_page_signature_with_padding(self):
        """Test 8-page signature requiring padding."""
        # 12 pages should be padded to 16 pages (2 signatures of 8)
        result = calculate_signature_order(12, 8)
        expected = [
            8,
            1,
            7,
            2,
            6,
            3,
            5,
            4,
            9,
            10,
            11,
            12,
        ]  # Second signature only has pages 9-12
        self.assertEqual(result, expected)

    def test_16_page_signature(self):
        """Test 16-page signature."""
        result = calculate_signature_order(16, 16)
        expected = [16, 1, 15, 2, 14, 3, 13, 4, 12, 5, 11, 6, 10, 7, 9, 8]
        self.assertEqual(result, expected)

    def test_40_page_signature(self):
        """Test 40-page signature (10 papers)."""
        result = calculate_signature_order(40, 40)
        expected_length = 40
        self.assertEqual(len(result), expected_length)

        # Verify all pages are present
        self.assertEqual(set(result), set(range(1, 41)))

        # Check that first and last pages are in expected positions
        self.assertEqual(result[0], 40)  # Last page first
        self.assertEqual(result[1], 1)  # First page second
        self.assertEqual(result[-2], 21)  # Middle pages at end
        self.assertEqual(result[-1], 20)

    def test_custom_signature_sizes(self):
        """Test various custom signature sizes."""
        test_cases = [
            (12, 12),  # 3 papers
            (20, 20),  # 5 papers
            (24, 24),  # 6 papers
            (28, 28),  # 7 papers
        ]

        for total_pages, sig_size in test_cases:
            with self.subTest(signature_size=sig_size):
                result = calculate_signature_order(total_pages, sig_size)

                # Should have all pages
                self.assertEqual(len(result), total_pages)
                self.assertEqual(set(result), set(range(1, total_pages + 1)))

                # Should follow the pattern
                self.assertEqual(result[0], total_pages)  # Last page first
                self.assertEqual(result[1], 1)  # First page second

    def test_empty_pdf(self):
        """Test with 0 pages."""
        result = calculate_signature_order(0, 4)
        expected = []
        self.assertEqual(result, expected)

    def test_single_page(self):
        """Test with 1 page."""
        result = calculate_signature_order(1, 4)
        expected = [1]
        self.assertEqual(result, expected)

    def test_multiple_signatures(self):
        """Test with multiple 4-page signatures."""
        # 10 pages = 2 full signatures (8 pages) + 1 partial signature
        # (2 pages padded to 4)
        result = calculate_signature_order(10, 4)
        expected = [4, 1, 3, 2, 8, 5, 7, 6, 9, 10]
        self.assertEqual(result, expected)

    def test_signature_size_validation(self):
        """Test that the algorithm works with different valid signature sizes."""
        for sig_size in [4, 8, 16, 32]:
            result = calculate_signature_order(sig_size, sig_size)
            self.assertEqual(len(result), sig_size)
            self.assertTrue(all(1 <= page <= sig_size for page in result))

    def test_order_preserves_reading_sequence(self):
        """Test that when folded, pages appear in reading order."""
        # For a 4-page signature [4,1,3,2], when folded:
        # Sheet 1: [4,1] -> when folded becomes pages 1,2 (reading order)
        # Sheet 2: [3,2] -> when folded becomes pages 3,4 (reading order)
        result = calculate_signature_order(4, 4)
        self.assertEqual(result, [4, 1, 3, 2])

    def test_large_document(self):
        """Test with a larger document to ensure scalability."""
        total_pages = 100
        signature_size = 8
        result = calculate_signature_order(total_pages, signature_size)

        # Should have exactly 100 pages (no padding needed since 100 % 8 = 4,
        # padded to 104)
        expected_length = 100  # Only real pages, not padded ones
        self.assertEqual(len(result), expected_length)

        # All pages should be within valid range
        self.assertTrue(all(1 <= page <= total_pages for page in result))

        # Each page should appear exactly once
        self.assertEqual(len(set(result)), len(result))


class TestSectionBindingProcessor(unittest.TestCase):
    """Test the PDF processing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_pdf = os.path.join(self.temp_dir, "input.pdf")
        self.output_pdf = os.path.join(self.temp_dir, "output.pdf")
        self.processor = SectionBindingProcessor(verbose=False)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("pdf_section_binding.core.PdfReader")
    @patch("pdf_section_binding.core.PdfWriter")
    @patch("builtins.open")
    def test_process_pdf_basic(self, mock_open, mock_pdf_writer, mock_pdf_reader):
        """Test basic PDF processing functionality."""
        # Mock PDF reader
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [MagicMock() for _ in range(4)]  # 4 pages
        mock_pdf_reader.return_value = mock_reader_instance

        # Mock PDF writer
        mock_writer_instance = MagicMock()
        mock_writer_instance.pages = []
        mock_pdf_writer.return_value = mock_writer_instance

        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Test the function
        result = self.processor.process_pdf(self.input_pdf, self.output_pdf, 4)

        # Verify PDF reader was called
        mock_pdf_reader.assert_called_once_with(self.input_pdf)

        # Verify PDF writer was created
        mock_pdf_writer.assert_called_once()

        # Verify result structure
        self.assertEqual(result["input_path"], self.input_pdf)
        self.assertEqual(result["output_path"], self.output_pdf)
        self.assertEqual(result["total_pages"], 4)
        self.assertEqual(result["signature_size"], 4)

    @patch("pdf_section_binding.core.PdfReader")
    def test_file_not_found_error(self, mock_pdf_reader):
        """Test handling of file not found error."""
        mock_pdf_reader.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            self.processor.process_pdf(self.input_pdf, self.output_pdf, 4)

    @patch("pdf_section_binding.core.PdfReader")
    def test_permission_error(self, mock_pdf_reader):
        """Test handling of permission error."""
        mock_pdf_reader.side_effect = PermissionError("Permission denied")

        with self.assertRaises(PermissionError):
            self.processor.process_pdf(self.input_pdf, self.output_pdf, 4)

    @patch("pdf_section_binding.core.PdfReader")
    def test_unexpected_error(self, mock_pdf_reader):
        """Test handling of unexpected errors."""
        mock_pdf_reader.side_effect = Exception("Unexpected error")

        with self.assertRaises(RuntimeError):
            self.processor.process_pdf(self.input_pdf, self.output_pdf, 4)

    def test_dry_run_mode(self):
        """Test dry run mode."""
        with patch("pdf_section_binding.core.PdfReader") as mock_pdf_reader:
            # Mock PDF reader
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [MagicMock() for _ in range(8)]
            mock_pdf_reader.return_value = mock_reader_instance

            result = self.processor.process_pdf(
                self.input_pdf, self.output_pdf, 8, dry_run=True
            )

            # Should not create output file in dry run
            self.assertTrue(result["dry_run"])
            self.assertNotIn("output_pages", result)
            self.assertFalse(os.path.exists(self.output_pdf))


class TestSignatureOrderLogic(unittest.TestCase):
    """Test the mathematical logic of signature ordering."""

    def test_signature_folding_logic(self):
        """Test that the signature order follows proper folding logic."""
        # For an 8-page signature, the order should be:
        # [8,1,7,2,6,3,5,4]
        # When printed on 4 sheets and folded:
        # Sheet 1: 8(back), 1(front) -> becomes pages 1,2 when folded
        # Sheet 2: 7(back), 2(front) -> becomes pages 3,4 when folded
        # Sheet 3: 6(back), 3(front) -> becomes pages 5,6 when folded
        # Sheet 4: 5(back), 4(front) -> becomes pages 7,8 when folded

        result = calculate_signature_order(8, 8)
        expected = [8, 1, 7, 2, 6, 3, 5, 4]
        self.assertEqual(result, expected)

    def test_signature_pairing(self):
        """Test that pages are properly paired for double-sided printing."""
        result = calculate_signature_order(4, 4)
        # Result should be [4,1,3,2]
        # This creates two sheets: [4,1] and [3,2]
        # When folded: sheet 1 becomes pages 1,2 and sheet 2 becomes pages 3,4

        self.assertEqual(result[0], 4)  # First page printed
        self.assertEqual(result[1], 1)  # Second page printed (same sheet, other side)
        self.assertEqual(result[2], 3)  # Third page printed
        self.assertEqual(result[3], 2)  # Fourth page printed (same sheet, other side)

    def test_multiple_signature_independence(self):
        """Test that multiple signatures are processed independently."""
        # 8 pages with 4-page signatures should create 2 independent signatures
        result = calculate_signature_order(8, 4)

        # First signature: pages 1-4 -> [4,1,3,2]
        first_sig = result[:4]
        self.assertEqual(first_sig, [4, 1, 3, 2])

        # Second signature: pages 5-8 -> [8,5,7,6]
        second_sig = result[4:]
        self.assertEqual(second_sig, [8, 5, 7, 6])


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
