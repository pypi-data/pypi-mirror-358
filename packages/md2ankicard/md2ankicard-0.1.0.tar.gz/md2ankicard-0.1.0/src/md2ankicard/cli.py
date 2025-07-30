"""Command line interface for md2anki."""

import argparse
import sys
from pathlib import Path
from typing import List

from .converter import MarkdownToAnkiConverter


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Convert markdown files to Anki cards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  md2anki /path/to/markdown/folder output.apkg "My Deck"
  md2anki ./docs my_notes.apkg "Documentation" --verbose
  md2anki ./notes study.apkg "Study Notes" --grep "python"
        """
    )
    
    parser.add_argument(
        "folder_path",
        type=str,
        help="Path to the folder containing markdown files"
    )
    
    parser.add_argument(
        "output_file",
        type=str,
        help="Name of the output Anki file (.apkg)"
    )
    
    parser.add_argument(
        "deck_name",
        type=str,
        help="Name of the Anki deck"
    )
    
    parser.add_argument(
        "--grep",
        type=str,
        help="Only include files that contain this string in filename or content"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    folder_path = Path(args.folder_path)
    if not folder_path.exists():
        print(f"Error: Folder '{args.folder_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not folder_path.is_dir():
        print(f"Error: '{args.folder_path}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    
    output_path = Path(args.output_file)
    if output_path.suffix.lower() != '.apkg':
        print(f"Error: Output file must have .apkg extension. Got: {output_path.suffix}", file=sys.stderr)
        sys.exit(1)
    
    try:
        converter = MarkdownToAnkiConverter(
            deck_name=args.deck_name,
            verbose=args.verbose
        )
        
        converter.convert_folder(
            folder_path=folder_path,
            output_file=output_path,
            grep_pattern=args.grep
        )
        
        print(f"Successfully created Anki deck: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 