# md2ankicard

**Convert Markdown notes (with images) into Anki decks.**

`md2ankicard` is a command-line tool to batch-convert Markdown files into Anki `.apkg` file, preserving images and formatting.

## ✨ Features

- 📄 Converts each `.md` file into an Anki note (card).
- 🖼️ Automatically includes images referenced in Markdown.
- 🔍 Optional `--grep` to filter files by keyword (e.g. by a tag).
- 🧠 Uses the Markdown filename as the front (question) and content as the back (answer).
- 🗃️ Outputs a standard `.apkg` file ready to import into Anki.

## 📦 Installation

```bash
pip install md2ankicard
```

Or with Poetry (for development):

```bash
git clone https://github.com/andrewromanenco/md2ankicard.git
cd md2ankicard
poetry install
```
## 🚀 Usage

```bash
md2ankicard <markdown_folder> <output.apkg> "<deck name>" [--grep <pattern>] [--verbose]
```

or if run from sources

```bash
poetry run md2ankicard PathToFilder FileName.apkg DeckName -v --grep '#SomeTag'
```
### Examples

#### Convert all Markdown files in the 'notes' folder to an Anki deck
`md2ankicard ./notes study.apkg "Study Notes"`

#### Only include files that mention 'python'
`md2ankicard ./notes code.apkg "Code Review" --grep "python"`

#### Show detailed output during conversion
`md2ankicard ./docs docs.apkg "Documentation" --verbose`

## 🧠 How It Works

- Each .md file becomes one Anki card.
- The file name (without extension) becomes the front of the card.
- The rendered Markdown (including images) becomes the back.
- Images are automatically detected and embedded in the .apkg file.

## 📝 License

This project is licensed under the MIT License.
