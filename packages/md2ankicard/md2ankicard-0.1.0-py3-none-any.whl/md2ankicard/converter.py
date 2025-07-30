"""Core conversion logic for markdown to Anki."""

import genanki
import markdown
from pathlib import Path
from typing import List, Optional, Set
import hashlib
import re
import html
import warnings

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="Field contained the following invalid HTML tags.*",
    module='genanki.note'
)

class MarkdownToAnkiConverter:
    """Convert markdown files to Anki cards."""

    def __init__(
        self,
        deck_name: str = "Markdown Notes",
        verbose: bool = False
    ):
        """Initialize the converter.

        Args:
            deck_name: Name of the Anki deck
            verbose: Enable verbose output
        """
        self.deck_name = deck_name
        self.verbose = verbose
        self.deck_id = int(hashlib.md5(deck_name.encode()).hexdigest()[:8], 16)
        self.deck = genanki.Deck(self.deck_id, deck_name)
        self.model = self._create_basic_model()
        self.media_files = []

    def _create_basic_model(self) -> genanki.Model:
        """Create a basic Anki card model."""
        return genanki.Model(
            1607392319,  # Random model ID
            "Basic",
            fields=[
                {'name': 'Front'},
                {'name': 'Back'}
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
                    'afmt': '{{Front}}<hr id="answer">{{Back}}',
                }
            ]
        )

    def _find_markdown_files(self, folder_path: Path) -> List[Path]:
        """Find all markdown files recursively.

        Args:
            folder_path: Root folder to search in

        Returns:
            List of markdown file paths
        """
        markdown_files = []
        for file_path in folder_path.rglob("*.md"):
            if file_path.is_file():
                markdown_files.append(file_path)

        return sorted(markdown_files)

    def _check_for_duplicate_filenames(self, files: List[Path]) -> None:
        """Check for duplicate filenames and raise error if found.

        Args:
            files: List of file paths to check

        Raises:
            ValueError: If duplicate filenames are found
        """
        filename_counts = {}
        duplicate_files = []

        for file_path in files:
            filename = file_path.stem  # filename without extension
            if filename in filename_counts:
                filename_counts[filename].append(file_path)
                duplicate_files.append(filename)
            else:
                filename_counts[filename] = [file_path]

        if duplicate_files:
            error_msg = "Duplicate filenames found:\n"
            for filename in set(duplicate_files):
                error_msg += f"  '{filename}.md' found in:\n"
                for file_path in filename_counts[filename]:
                    error_msg += f"    - {file_path}\n"
            raise ValueError(error_msg)

    def _find_html_images(self, content: str, markdown_file_path: Path) -> List[str]:
        """Find HTML img tags in markdown content.

        Args:
            content: Markdown content to search
            markdown_file_path: Path to the markdown file (for relative path resolution)

        Returns:
            List of image file paths found
        """
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(img_pattern, content)

        image_paths = []
        for match in matches:
            image_path = match.strip()

            if image_path.startswith('/'):
                raise ValueError(f"Absolute image paths are not supported. Found: <img src=\"{image_path}\"> in {markdown_file_path}")

            if image_path.startswith(('data:', 'http://', 'https://')):
                if self.verbose:
                    print(f"Skipping external/data image: {image_path}")
                continue

            resolved_path = markdown_file_path.parent / image_path

            if not resolved_path.suffix:
                for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                    if (resolved_path.parent / f"{resolved_path.name}{ext}").exists():
                        resolved_path = resolved_path.parent / f"{resolved_path.name}{ext}"
                        break

            if resolved_path.exists() and resolved_path.is_file():
                image_paths.append(str(resolved_path))
                if self.verbose:
                    print(f"Found HTML image: {resolved_path}")
            else:
                if self.verbose:
                    print(f"HTML image not found: {resolved_path}")

        return image_paths

    def _process_html_images(self, content: str, markdown_file_path: Path) -> str:
        """Process HTML img tags and ensure they're included in the Anki deck.

        Args:
            content: Markdown content to process
            markdown_file_path: Path to the markdown file

        Returns:
            Processed content with HTML img tags preserved
        """
        def replace_html_image(match):
            full_tag = match.group(0)
            src_match = re.search(r'src=["\']([^"\']+)["\']', full_tag)

            if not src_match:
                return full_tag

            image_path = src_match.group(1).strip()

            if image_path.startswith('/'):
                raise ValueError(f"Absolute image paths are not supported. Found: <img src=\"{image_path}\"> in {markdown_file_path}")

            if image_path.startswith(('data:', 'http://', 'https://')):
                return full_tag

            resolved_path = markdown_file_path.parent / image_path

            if not resolved_path.suffix:
                for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                    if (resolved_path.parent / f"{resolved_path.name}{ext}").exists():
                        resolved_path = resolved_path.parent / f"{resolved_path.name}{ext}"
                        break
            if resolved_path.exists() and resolved_path.is_file():
                self.media_files.append(str(resolved_path))
                if self.verbose:
                    print(f"  Added HTML image to deck: {resolved_path.name}")
                return full_tag
            else:
                if self.verbose:
                    print(f"  HTML image not found: {resolved_path}")
                return full_tag

        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        processed_content = re.sub(img_pattern, replace_html_image, content)

        return processed_content

    def _find_obsidian_images(self, content: str, markdown_file_path: Path) -> List[str]:
        """Find Obsidian-style image references in markdown content.

        Args:
            content: Markdown content to search
            markdown_file_path: Path to the markdown file (for relative path resolution)

        Returns:
            List of image file paths found
        """
        obsidian_pattern = r'!\[\[([^\]]+)\]\]'
        matches = re.findall(obsidian_pattern, content)

        image_paths = []
        for match in matches:
            image_path = match.strip()

            if image_path.startswith('/'):
                raise ValueError(f"Absolute image paths are not supported. Found: ![[{image_path}]] in {markdown_file_path}")

            image_path = markdown_file_path.parent / image_path

            if not image_path.suffix:
                for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                    if (image_path.parent / f"{image_path.name}{ext}").exists():
                        image_path = image_path.parent / f"{image_path.name}{ext}"
                        break

            if image_path.exists() and image_path.is_file():
                image_paths.append(str(image_path))
                if self.verbose:
                    print(f"Found image: {image_path}")
            else:
                if self.verbose:
                    print(f"Image not found: {image_path}")

        return image_paths

    def _process_obsidian_images(self, content: str, markdown_file_path: Path) -> str:
        """Process Obsidian-style image embeds and convert them to standard markdown.

        Args:
            content: Markdown content to process
            markdown_file_path: Path to the markdown file

        Returns:
            Processed content with Obsidian embeds converted to standard markdown
        """
        def replace_obsidian_image(match):
            image_path = match.group(1).strip()

            if image_path.startswith('/'):
                raise ValueError(f"Absolute image paths are not supported. Found: ![[{image_path}]] in {markdown_file_path}")

            resolved_path = markdown_file_path.parent / image_path

            if not resolved_path.suffix:
                for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
                    if (resolved_path.parent / f"{resolved_path.name}{ext}").exists():
                        resolved_path = resolved_path.parent / f"{resolved_path.name}{ext}"
                        break

            if resolved_path.exists() and resolved_path.is_file():
                image_filename = resolved_path.name
                self.media_files.append(str(resolved_path))
                if self.verbose:
                    print(f"  Added image to deck: {resolved_path.name}")
                return f"![{resolved_path.stem}]({image_filename})"
            else:
                if self.verbose:
                    print(f"  Image not found: {resolved_path}")
                return match.group(0)
        obsidian_pattern = r'!\[\[([^\]]+)\]\]'
        processed_content = re.sub(obsidian_pattern, replace_obsidian_image, content)

        return processed_content

    def _filter_files_by_grep(self, files: List[Path], grep_pattern: str) -> List[Path]:
        """Filter files based on grep pattern in filename or content.

        Args:
            files: List of file paths to filter
            grep_pattern: String to search for in filename or content

        Returns:
            List of files that match the grep pattern
        """
        if not grep_pattern:
            return files

        matching_files = []
        grep_pattern_lower = grep_pattern.lower()

        for file_path in files:
            if grep_pattern_lower in file_path.name.lower():
                matching_files.append(file_path)
                if self.verbose:
                    print(f"File matches (filename): {file_path}")
                continue
            try:
                content = self._read_markdown_file(file_path)
                if grep_pattern_lower in content.lower():
                    matching_files.append(file_path)
                    if self.verbose:
                        print(f"File matches (content): {file_path}")
            except Exception as e:
                if self.verbose:
                    print(f"Error reading file {file_path}: {e}")

        return matching_files

    def _read_markdown_file(self, file_path: Path) -> str:
        """Read and return the content of a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    def _convert_markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown content to HTML.

        Args:
            markdown_content: Raw markdown content

        Returns:
            HTML content
        """
        extensions = [
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc'#,
            #'markdown.extensions.nl2br'
        ]

        md = markdown.Markdown(extensions=extensions)
        html_content = md.convert(markdown_content)

        return html_content

    def _clean_html(self, html_content: str) -> str:
        """Clean and format HTML content.

        Args:
            html_content: Raw HTML content

        Returns:
            Cleaned HTML content
        """
        html_content = re.sub(r'\n\s*\n', '\n\n', html_content)
        html_content = html_content.replace('\n', '<br>')
        html_content = re.sub(r'(<br>)+', '<br>', html_content)
        html_content = html.escape(html_content)
        html_content = html_content.replace('&lt;br&gt;', '<br>')
        html_content = html_content.replace('&lt;hr&gt;', '<hr>')
        html_content = html_content.replace('&lt;p&gt;', '<p>')
        html_content = html_content.replace('&lt;/p&gt;', '</p>')
        html_content = html_content.replace('&lt;h1&gt;', '<h1>')
        html_content = html_content.replace('&lt;/h1&gt;', '</h1>')
        html_content = html_content.replace('&lt;h2&gt;', '<h2>')
        html_content = html_content.replace('&lt;/h2&gt;', '</h2>')
        html_content = html_content.replace('&lt;h3&gt;', '<h3>')
        html_content = html_content.replace('&lt;/h3&gt;', '</h3>')
        html_content = html_content.replace('&lt;strong&gt;', '<strong>')
        html_content = html_content.replace('&lt;/strong&gt;', '</strong>')
        html_content = html_content.replace('&lt;em&gt;', '<em>')
        html_content = html_content.replace('&lt;/em&gt;', '</em>')
        html_content = html_content.replace('&lt;code&gt;', '<code>')
        html_content = html_content.replace('&lt;/code&gt;', '</code>')
        html_content = html_content.replace('&lt;pre&gt;', '<pre>')
        html_content = html_content.replace('&lt;/pre&gt;', '</pre>')
        html_content = html_content.replace('&lt;ul&gt;', '<ul>')
        html_content = html_content.replace('&lt;/ul&gt;', '</ul>')
        html_content = html_content.replace('&lt;ol&gt;', '<ol>')
        html_content = html_content.replace('&lt;/ol&gt;', '</ol>')
        html_content = html_content.replace('&lt;li&gt;', '<li>')
        html_content = html_content.replace('&lt;/li&gt;', '</li>')
        html_content = html_content.replace('&lt;img', '<img')
        html_content = html_content.replace('&lt;table&gt;', '<table>')
        html_content = html_content.replace('&lt;/table&gt;', '</table>')
        html_content = html_content.replace('&lt;tr&gt;', '<tr>')
        html_content = html_content.replace('&lt;/tr&gt;', '</tr>')
        html_content = html_content.replace('&lt;td&gt;', '<td>')
        html_content = html_content.replace('&lt;/td&gt;', '</td>')
        html_content = html_content.replace('&lt;th&gt;', '<th>')
        html_content = html_content.replace('&lt;/th&gt;', '</th>')

        return html_content.strip()

    def _create_card_name(self, file_path: Path) -> str:
        """Create a card name from the file path.

        Args:
            file_path: Path to the markdown file

        Returns:
            Card name (filename without extension)
        """
        name = file_path.stem

        return name

    def _add_file_as_card(self, file_path: Path) -> None:
        """Add a markdown file as an Anki card.

        Args:
            file_path: Path to the markdown file
        """
        try:
            markdown_content = self._read_markdown_file(file_path)

            if not markdown_content.strip():
                if self.verbose:
                    print(f"Skipping empty file: {file_path}")
                return

            processed_content = self._process_obsidian_images(markdown_content, file_path)
            processed_content = self._process_html_images(processed_content, file_path)
            card_name = self._create_card_name(file_path)
            html_content = self._convert_markdown_to_html(processed_content)

            filename = file_path.stem
            note_id = int(hashlib.md5(filename.encode()).hexdigest()[:8], 16)

            note = genanki.Note(
                model=self.model,
                fields=[card_name, html_content],
                #guid=genanki.guid_for(filename)
                guid=note_id
            )

            self.deck.add_note(note)

            if self.verbose:
                print(f"Added card: {card_name} from {file_path}")

        except Exception as e:
            if self.verbose:
                print(f"Error processing {file_path}: {e}")
            else:
                raise

    def convert_folder(
        self,
        folder_path: Path,
        output_file: Path,
        grep_pattern: Optional[str] = None
    ) -> None:
        """Convert all markdown files in a folder to Anki cards.

        Args:
            folder_path: Path to the folder containing markdown files
            output_file: Path for the output Anki file
            grep_pattern: Optional string to filter files by filename or content
        """
        if self.verbose:
            print(f"Searching for markdown files in: {folder_path}")
            if grep_pattern:
                print(f"Filtering files containing: '{grep_pattern}'")

        markdown_files = self._find_markdown_files(folder_path)

        if not markdown_files:
            raise ValueError(f"No markdown files found in {folder_path}")

        if grep_pattern:
            markdown_files = self._filter_files_by_grep(markdown_files, grep_pattern)
            if not markdown_files:
                raise ValueError(f"No markdown files found in {folder_path} containing '{grep_pattern}'")

        self._check_for_duplicate_filenames(markdown_files)

        if self.verbose:
            print(f"Found {len(markdown_files)} markdown files")

        for file_path in markdown_files:
            self._add_file_as_card(file_path)

        if self.verbose:
            print(f"Created {len(self.deck.notes)} cards")
            if self.media_files:
                print(f"Included {len(self.media_files)} images")

        package = genanki.Package(self.deck, media_files=self.media_files)
        package.write_to_file(str(output_file))

        if self.verbose:
            print(f"Anki package written to: {output_file}")