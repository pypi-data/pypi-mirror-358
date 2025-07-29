# DevGhost

Smart CLI tool to generate GitHub commit messages from code diffs using Gemini AI.

## Features
- Generates commit messages from your git diff using Gemini (Google AI) for free
- Works in any git project
- Easy setup for GitHub and Gemini API keys
- **Streamlined workflow:** Just press Enter to commit with the AI-generated message

## Installation

1. Clone/download this repo and navigate to the folder.
2. (Recommended) Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install as a CLI tool:
   ```sh
   pip install -e .
   ```

## Setup

1. Run the setup command to store your API keys:
   ```sh
   devghost setup
   ```
   - **GitHub Token:** Generate a Personal Access Token (classic) with `repo` scope at https://github.com/settings/tokens (set expiration up to 1 year).
   - **Gemini API Key:** Get your free API key from https://aistudio.google.com/app/apikey

## Usage

1. Make some changes in your git project.
2. Run:
   ```sh
   devghost suggest
   ```
   - The tool will show the AI-generated commit message.
   - **Press Enter to commit with this message, or Ctrl+C to cancel.**
   - All changes will be staged and committed automatically.

## Uninstall

To uninstall, simply remove the package:
```sh
pip uninstall devghost
```

## License
MIT 