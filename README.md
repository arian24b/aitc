# aitc

**AITC** — AI Token Counter. A CLI tool for counting tokens in text/files and estimating API costs across popular LLM models. Supports a diff mode comparing two files.

## Features

- Count tokens in inline text, files, or piped stdin
- Estimate API costs for GPT-4o, GPT-4o mini, Claude Sonnet 4.5, Claude Haiku 4.5, Gemini 1.5 Pro, and Gemini 1.5 Flash
- Live pricing via OpenRouter API (`--live-prices`)
- Diff mode to compare token counts between two files (`--diff`)

## Installation

### Via pip

```bash
pip install aitc
```

### Via uv

```bash
uv tool install aitc
```

### From source

```bash
# Clone the repository
git clone https://github.com/arian24b/aitc.git
cd aitc

# Sync dependencies with uv
uv sync

# Run directly
uv run aitc --text "Hello, world!"

# Or install in development mode
uv tool install -e .
```

## Usage

### Count tokens from inline text

```bash
aitc --text "Your text here"
```

### Count tokens from a file

```bash
aitc --file README.md
```

### Pipe text via stdin

```bash
echo "Your text here" | aitc
cat somefile.txt | aitc
```

### Compare two files (diff mode)

```bash
aitc --diff file1.txt file2.txt
```

### Fetch live pricing

```bash
aitc --text "Hello" --live-prices
```

## Development

```bash
# Clone
git clone https://github.com/arian24b/aitc.git
cd aitc

# Set up environment with uv
uv sync

# Run linting
uv run ruff check .

# Build
uv build
```

## License

MIT

## Common commands

Built with [cfui](https://github.com/arian24b/cfui), so every command shares the same look and flags:

```bash
aitc help [command]     # help
aitc version            # version and git repo (also: aitc -v)
aitc update [--check]   # self update
aitc -q ...             # quiet: no banners/notes (or AITC_QUIET=1)
```

Missing required options are asked for interactively on a TTY; in pipes/CI they fail with `--flag is required`.
