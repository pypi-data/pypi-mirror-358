"""Enhanced CLI interface for PDF section binding."""

import argparse
import os
import sys
import traceback
from pathlib import Path
from typing import Optional

from .core import SectionBindingProcessor, print_binding_instructions
from .version import __version__, __description__


# ANSI color codes for better CLI experience
class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Colorize text if terminal supports it."""
        if os.getenv("NO_COLOR") or not sys.stdout.isatty():
            return text
        return f"{color}{text}{cls.RESET}"

    @classmethod
    def success(cls, text: str) -> str:
        """Green success text."""
        return cls.colorize(text, cls.GREEN)

    @classmethod
    def error(cls, text: str) -> str:
        """Red error text."""
        return cls.colorize(text, cls.RED)

    @classmethod
    def warning(cls, text: str) -> str:
        """Yellow warning text."""
        return cls.colorize(text, cls.YELLOW)

    @classmethod
    def info(cls, text: str) -> str:
        """Blue info text."""
        return cls.colorize(text, cls.BLUE)

    @classmethod
    def highlight(cls, text: str) -> str:
        """Cyan highlighted text."""
        return cls.colorize(text, cls.CYAN)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def suggest_signature_sizes(current: int) -> str:
    """Suggest alternative signature sizes."""
    if current % 4 != 0:
        suggested_lower = (current // 4) * 4
        suggested_higher = ((current // 4) + 1) * 4
        return f"Try: {suggested_lower} or {suggested_higher}"

    common_sizes = [4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 56, 64]
    nearby = [s for s in common_sizes if abs(s - current) <= 8 and s != current]
    if nearby:
        return f"Common alternatives: {', '.join(map(str, nearby[:3]))}"
    return "Common sizes: 4, 8, 16, 32, 40"


def validate_pdf_file(filepath: str) -> Optional[str]:
    """Validate PDF file and return error message if invalid."""
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    if not os.path.isfile(filepath):
        return f"Path is not a file: {filepath}"

    if not os.access(filepath, os.R_OK):
        return f"File is not readable: {filepath}"

    # Check file size
    size = os.path.getsize(filepath)
    if size == 0:
        return f"File is empty: {filepath}"

    if size > 500 * 1024 * 1024:  # 500MB
        return f"File is very large ({format_file_size(size)}). Processing may be slow."

    # Basic PDF validation
    try:
        with open(filepath, "rb") as f:
            header = f.read(4)
            if header != b"%PDF":
                return f"File does not appear to be a valid PDF: {filepath}"
    except (OSError, IOError) as e:
        return f"Error reading file: {e}"

    return None


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pdf-section-binding",
        description=__description__,
        epilog="""
Examples:
  %(prog)s book.pdf                    # Basic usage (8-page signatures)
  %(prog)s book.pdf -s 40              # 10 papers per signature
  %(prog)s book.pdf -o output.pdf      # Specify output file
  %(prog)s book.pdf --dry-run          # Preview without creating file
  %(prog)s book.pdf -v                 # Verbose output
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Positional arguments
    parser.add_argument("input", help="Input PDF file path")

    # Optional arguments
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF file path (default: input_name_section_bound.pdf)",
    )

    parser.add_argument(
        "-s",
        "--signature-size",
        type=int,
        default=8,
        metavar="PAGES",
        help="Pages per signature (must be multiple of 4, default: 8). "
        "Common: 4, 8, 16, 32, 40. Formula: papers = pages ÷ 4",
    )

    # Behavior flags
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without creating output file",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress all output except errors"
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # Advanced options
    parser.add_argument(
        "--force", action="store_true", help="Overwrite output file if it exists"
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate command line arguments.

    Args:
        args: Parsed command line arguments

    Raises:
        SystemExit: If validation fails
    """
    # Enhanced PDF file validation
    pdf_error = validate_pdf_file(args.input)
    if pdf_error:
        if "very large" in pdf_error:
            print(Colors.warning(f"Warning: {pdf_error}"), file=sys.stderr)
        else:
            print(Colors.error(f"Error: {pdf_error}"), file=sys.stderr)
            sys.exit(1)

    # Enhanced signature size validation
    if args.signature_size % 4 != 0:
        suggestions = suggest_signature_sizes(args.signature_size)
        print(
            Colors.error(
                "Error: Signature size must be a multiple of 4 (each paper = 4 pages)."
            ),
            file=sys.stderr,
        )
        print(
            Colors.info(f"You specified {args.signature_size}. {suggestions}"),
            file=sys.stderr,
        )
        sys.exit(1)

    if args.signature_size < 4:
        print(
            Colors.error("Error: Signature size must be at least 4 pages (1 paper)."),
            file=sys.stderr,
        )
        sys.exit(1)

    if args.signature_size > 128:
        print(
            Colors.error(
                f"Error: Signature size too large ({args.signature_size}). "
                "Maximum recommended: 128 pages (32 papers)."
            ),
            file=sys.stderr,
        )
        print(
            Colors.info(
                "Large signature sizes make folding difficult and may not bind well."
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    # Generate output filename if not provided
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.with_stem(f"{input_path.stem}_section_bound"))

    # Validate output path
    if not args.dry_run:
        output_path = Path(args.output)

        # Check if output file exists and --force not specified
        if output_path.exists() and not args.force:
            print(
                f"Error: Output file '{args.output}' already exists. "
                "Use --force to overwrite.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Check if output directory is writable
        output_dir = output_path.parent
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True)
            except PermissionError:
                print(
                    f"Error: Cannot create output directory '{output_dir}'.",
                    file=sys.stderr,
                )
                sys.exit(1)

        if not os.access(output_dir, os.W_OK):
            print(
                f"Error: No write permission for output directory '{output_dir}'.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Validate conflicting options
    if args.quiet and args.verbose:
        print("Error: Cannot use both --quiet and --verbose options.", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Parse arguments
        parser = create_parser()
        args = parser.parse_args()

        # Validate arguments
        validate_arguments(args)

        # Configure output verbosity
        verbose = args.verbose and not args.quiet
        quiet = args.quiet

        if not quiet:
            print(Colors.highlight(f"PDF Section Binding Tool v{__version__}"))
            print("=" * 50)

        # Create processor
        processor = SectionBindingProcessor(verbose=verbose)

        # Process the PDF
        result = processor.process_pdf(
            input_path=args.input,
            output_path=args.output,
            signature_size=args.signature_size,
            dry_run=args.dry_run,
        )

        # Print results and instructions
        if not quiet:
            if args.dry_run:
                print(f"\n{Colors.info('🔍 DRY RUN ANALYSIS:')}")
                print(
                    f"Would process "
                    f"{Colors.highlight(str(result['total_pages']))} pages"
                )
                print(
                    f"Would create "
                    f"{Colors.highlight(str(result['total_signatures']))} "
                    "signatures"
                )
                print(
                    f"Would need "
                    f"{Colors.highlight(str(result['total_papers']))} "
                    "papers total"
                )
                print(f"Would save to: {Colors.highlight(result['output_path'])}")
            else:
                print(
                    f"\n{Colors.success('✅ Successfully created:')} "
                    f"{Colors.highlight(result['output_path'])}"
                )
                print(
                    f"{Colors.info('📊 Processed')} "
                    f"{Colors.highlight(str(result['total_pages']))} pages into "
                    f"{Colors.highlight(str(result['output_pages']))} "
                    "reordered pages"
                )

        # Print binding instructions
        print_binding_instructions(result, quiet=quiet)

        return 0

    except KeyboardInterrupt:
        if not (locals().get("args") and args.quiet):
            print(
                f"\n{Colors.error('❌ Operation cancelled by user.')}", file=sys.stderr
            )
        return 130  # Standard exit code for SIGINT

    except FileNotFoundError as e:
        print(Colors.error(f"❌ File error: {e}"), file=sys.stderr)
        return 2

    except PermissionError as e:
        print(Colors.error(f"❌ Permission error: {e}"), file=sys.stderr)
        return 13

    except ValueError as e:
        print(Colors.error(f"❌ Invalid input: {e}"), file=sys.stderr)
        return 22

    except RuntimeError as e:
        print(Colors.error(f"❌ Runtime error: {e}"), file=sys.stderr)
        if locals().get("args") and args.verbose:
            traceback.print_exc()
        return 1

    except (OSError, IOError) as e:
        print(Colors.error(f"❌ System error: {e}"), file=sys.stderr)
        if locals().get("args") and args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
