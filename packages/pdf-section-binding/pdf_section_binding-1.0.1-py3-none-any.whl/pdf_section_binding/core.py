"""Core functionality for PDF section binding."""

from typing import List
from PyPDF2 import PdfReader, PdfWriter


def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """Create a simple progress bar string."""
    if total == 0:
        return "[" + "=" * width + "]"

    progress = current / total
    filled = int(width * progress)
    progress_bar = "=" * filled + "-" * (width - filled)
    percentage = int(progress * 100)
    return f"[{progress_bar}] {percentage:3d}% ({current}/{total})"


def show_progress(current: int, total: int, prefix: str = "Progress") -> None:
    """Show progress bar for terminal output."""
    if total < 50:  # Don't show progress for small files
        return

    if current % max(1, total // 20) == 0 or current == total:  # Update every 5%
        progress_bar = create_progress_bar(current, total)
        print(f"\r{prefix}: {progress_bar}", end="", flush=True)
        if current == total:
            print()  # New line when complete


def calculate_signature_order(total_pages: int, signature_size: int) -> List[int]:
    """
    Calculate the page order for section binding.

    For section binding, pages are arranged so that when printed double-sided
    and folded, they appear in correct reading order.

    Args:
        total_pages: Total number of pages in the PDF
        signature_size: Number of pages per signature (must be multiple of 4)

    Returns:
        Ordered list of page numbers for section binding

    Raises:
        ValueError: If signature_size is not a multiple of 4 or is invalid
    """
    if signature_size % 4 != 0:
        raise ValueError(
            f"Signature size must be a multiple of 4, got {signature_size}"
        )

    if signature_size < 4:
        raise ValueError(f"Signature size must be at least 4, got {signature_size}")

    # Pad pages to make them divisible by signature size
    padded_pages = (
        (total_pages + signature_size - 1) // signature_size
    ) * signature_size

    # Create list of pages (1-indexed)
    pages = list(range(1, total_pages + 1))

    # Add blank pages if needed
    while len(pages) < padded_pages:
        pages.append(None)  # None represents blank pages

    # Calculate signature order
    reordered_pages = []

    # Process each signature
    for signature_start in range(0, padded_pages, signature_size):
        # Calculate the correct order for this signature
        signature_order = []

        for i in range(signature_size // 2):
            left_page = signature_start + i
            right_page = signature_start + signature_size - 1 - i

            # Add the pages for this sheet
            if right_page < len(pages):
                signature_order.append(pages[right_page])
            if left_page < len(pages):
                signature_order.append(pages[left_page])

        reordered_pages.extend(signature_order)

    return [p for p in reordered_pages if p is not None]


class SectionBindingProcessor:
    """Main processor for PDF section binding operations."""

    def __init__(self, verbose: bool = False):
        """Initialize processor.

        Args:
            verbose: Whether to output verbose information
        """
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")

    def process_pdf(
        self,
        input_path: str,
        output_path: str,
        signature_size: int = 8,
        dry_run: bool = False,
    ) -> dict:
        """
        Process a PDF for section binding.

        Args:
            input_path: Path to input PDF
            output_path: Path to output PDF
            signature_size: Pages per signature (default: 8)
            dry_run: If True, don't create output file, just analyze

        Returns:
            Dictionary with processing information

        Raises:
            FileNotFoundError: If input file doesn't exist
            PermissionError: If unable to read input or write output
            ValueError: If signature size is invalid
        """
        try:
            # Read the input PDF
            self.log(f"Reading PDF: {input_path}")
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)

            self.log(f"Total pages: {total_pages}")
            self.log(f"Signature size: {signature_size}")

            # Calculate page order
            page_order = calculate_signature_order(total_pages, signature_size)

            # Calculate statistics
            papers_per_signature = signature_size // 4
            total_signatures = (total_pages + signature_size - 1) // signature_size
            total_papers = total_signatures * papers_per_signature

            result = {
                "input_path": input_path,
                "output_path": output_path,
                "total_pages": total_pages,
                "signature_size": signature_size,
                "papers_per_signature": papers_per_signature,
                "total_signatures": total_signatures,
                "total_papers": total_papers,
                "page_order": page_order,
                "dry_run": dry_run,
            }

            if dry_run:
                self.log("Dry run mode - not creating output file")
                return result

            # Create output PDF
            self.log("Creating reordered PDF...")
            writer = PdfWriter()

            # Add pages in the calculated order
            for i, page_num in enumerate(page_order):
                # Show progress for large documents
                if not dry_run and self.verbose and total_pages > 50:
                    show_progress(i + 1, len(page_order), "Creating PDF")
                elif not dry_run and i % 100 == 0 and total_pages > 200:
                    # Show minimal progress for very large files even without verbose
                    self.log(f"Processing page {i+1}/{len(page_order)}...")

                if page_num and page_num <= total_pages:
                    writer.add_page(reader.pages[page_num - 1])  # Convert to 0-indexed

            # Write the output PDF
            self.log(f"Writing output: {output_path}")
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            result["output_pages"] = len(writer.pages)
            self.log(
                f"Successfully created {output_path} with {len(writer.pages)} pages"
            )

            return result

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Input file not found: {input_path}") from e
        except PermissionError as e:
            raise PermissionError(f"Permission error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error processing PDF: {e}") from e


def print_binding_instructions(result: dict, quiet: bool = False) -> None:
    """Print binding instructions based on processing result."""
    if quiet:
        return

    # Import Colors here to avoid circular imports
    try:
        from .cli import Colors
    except ImportError:
        # Fallback if Colors not available
        class Colors:
            """Fallback color class when CLI colors are not available."""

            @staticmethod
            def highlight(text):
                """Return text without highlighting."""
                return text

            @staticmethod
            def info(text):
                """Return text without info formatting."""
                return text

            @staticmethod
            def success(text):
                """Return text without success formatting."""
                return text

    print("\n" + "=" * 60)
    print(Colors.highlight("SECTION BINDING INSTRUCTIONS"))
    print("=" * 60)
    print(f"📄 Input: {Colors.info(result['input_path'])}")
    print(f"📋 Total pages: {Colors.highlight(str(result['total_pages']))}")
    print(
        f"📐 Signature size: {Colors.highlight(str(result['signature_size']))}" " pages"
    )
    print(
        f"📎 Papers per signature: "
        f"{Colors.highlight(str(result['papers_per_signature']))}"
    )
    print(f"📚 Total signatures: {Colors.highlight(str(result['total_signatures']))}")
    print(f"🗞️  Total papers needed: {Colors.highlight(str(result['total_papers']))}")

    if not result["dry_run"]:
        print(f"💾 Output: {Colors.success(result['output_path'])}")

    print(f"\n{Colors.info('📋 PRINTING & BINDING STEPS:')}")
    print("1. Print the output PDF double-sided (flip on long edge)")
    print(f"2. Each {result['papers_per_signature']} papers forms one signature")
    print("3. Fold each signature in half along the center")
    print("4. Stack all signatures in order")
    print("5. Bind along the folded edge (staple, glue, or spiral bind)")
    print("=" * 60)
