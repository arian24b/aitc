# aitc

[فارسی](README.fa.md)

AI Token Counter. Counts the tokens in text, a file, or piped input and estimates what that input costs on popular LLM APIs. It can also compare two files.

## Install

Python 3.12 to 3.15.

```bash
uv tool install aitc      # or: pipx install aitc, pip install aitc
```

From a clone: `uv sync && uv run aitc --text "Hello"`.

## Usage

`aitc` has one command, `count`, and it runs by default, so `aitc --text ...` and `aitc count --text ...` are the same.

```bash
aitc --text "Your text here"           # inline text
aitc --file README.md                  # a file
echo "Your text here" | aitc           # stdin
aitc --diff old.txt new.txt            # token and cost difference between two files
aitc --text "Hello" --live-prices      # current prices from OpenRouter
aitc                                   # in a terminal with no input: asks for the text
```

Options of `count`:

| Option | Meaning |
|---|---|
| `-t`, `--text TEXT` | text to count |
| `-f`, `--file FILE` | file to count |
| `-d`, `--diff FILE FILE` | compare two files |
| `--live-prices` | fetch prices from OpenRouter instead of the built-in table |

Input is taken in this order: `--text`, then `--file`, then stdin. Costs are for input tokens, in USD per model: GPT-4o, GPT-4o mini, Claude Sonnet 4.5, Claude Haiku 4.5, Gemini 1.5 Pro, Gemini 1.5 Flash. Tokens are counted with the `cl100k_base` encoding, so counts for other model families are estimates.

## Common commands

Built on [cfuicli](https://github.com/arian24b/cfui), so it looks and behaves like the other tools in this family.

```bash
aitc help [command]     # help; -h works on any command
aitc version            # version and git repository (also: -v)
aitc update [--check]   # update the tool itself; --check only compares versions
aitc -q ...             # quiet: no banner or notes (or AITC_QUIET=1)
```

- A missing required option is asked for when you run the tool in a terminal. In a pipe or in CI it stops with `--flag is required. Pass --flag <value> or run interactively.` (exit code 2).
- Errors appear in a red box on stderr with a non-zero exit code. Ctrl-C exits with 130.
- Color is used only on a terminal. `NO_COLOR=1` turns it off.

## Development

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv build
```

## License

MIT
