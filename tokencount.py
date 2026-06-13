#!/usr/bin/env python3
"""Token counting and cost estimation CLI tool.

Counts tokens in text/files and estimates API cost across popular LLM models.
Supports a diff mode comparing two files.
"""

import argparse
import os
import sys
from typing import Any

import requests
import tiktoken

# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------

MODELS: list[dict[str, Any]] = [
    {
        "display_name": "GPT-4o",
        "openrouter_id": "openai/gpt-4o",
        "hardcoded_price_per_1m": 2.50,
    },
    {
        "display_name": "GPT-4o mini",
        "openrouter_id": "openai/gpt-4o-mini",
        "hardcoded_price_per_1m": 0.15,
    },
    {
        "display_name": "Claude Sonnet 4.5",
        "openrouter_id": "anthropic/claude-sonnet-4-5",
        "hardcoded_price_per_1m": 3.00,
    },
    {
        "display_name": "Claude Haiku 4.5",
        "openrouter_id": "anthropic/claude-haiku-4-5",
        "hardcoded_price_per_1m": 0.80,
    },
    {
        "display_name": "Gemini 1.5 Pro",
        "openrouter_id": "google/gemini-pro-1.5",
        "hardcoded_price_per_1m": 1.25,
    },
    {
        "display_name": "Gemini 1.5 Flash",
        "openrouter_id": "google/gemini-flash-1.5",
        "hardcoded_price_per_1m": 0.075,
    },
]


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

_ENCODING = "cl100k_base"


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string using cl100k_base encoding.

    Args:
        text: The input text to tokenize.

    Returns:
        The number of tokens in the text.
    """
    encoder = tiktoken.get_encoding(_ENCODING)
    return len(encoder.encode(text))


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------

_OPENROUTER_URL = "https://openrouter.ai/api/v1/models"
_LIVE_TIMEOUT_SECONDS = 3


def fetch_live_prices() -> dict[str, float] | None:
    """Fetch live model pricing from the OpenRouter API.

    Returns:
        A dict mapping openrouter_id -> price_per_1m_tokens, or None if the
        fetch fails for any reason (timeout, network error, bad JSON, etc.).
    """
    try:
        response = requests.get(_OPENROUTER_URL, timeout=_LIVE_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    if not isinstance(data, dict):
        return None
    models_list = data.get("data")
    if not isinstance(models_list, list):
        return None

    prices: dict[str, float] = {}
    for entry in models_list:
        model_id = entry.get("id")
        pricing = entry.get("pricing")
        if not isinstance(model_id, str) or not isinstance(pricing, dict):
            continue
        prompt_price = pricing.get("prompt")
        # OpenRouter pricing.prompt is price-per-token; convert to per-1M.
        if isinstance(prompt_price, (int, float)):
            prices[model_id] = prompt_price * 1_000_000
    return prices


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def format_number(n: int) -> str:
    """Format an integer with comma separators.

    Args:
        n: The integer to format.

    Returns:
        A string like "1,234".
    """
    return f"{n:,}"


def format_cost(cost: float) -> str:
    """Format a cost value to 6 decimal places.

    Args:
        cost: The cost value to format.

    Returns:
        A string like "0.003085".
    """
    return f"{cost:.6f}"


# ---------------------------------------------------------------------------
# Input reading
# ---------------------------------------------------------------------------


def read_file(path: str) -> str:
    """Read text content from a file.

    Args:
        path: Path to the file.

    Returns:
        The file contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path) as fh:
        return fh.read()


def read_stdin() -> str | None:
    """Read all text from standard input (non-interactive / pipe).

    Returns:
        The piped text, or None if stdin is a terminal (tty).
    """
    if sys.stdin.isatty():
        return None
    return sys.stdin.read()


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def _price_label(prices_live: bool, live_prices: dict | None) -> str | None:
    """Build the bracketed price-source annotation line.

    Args:
        prices_live: Whether --live-prices was requested.
        live_prices: The result of the live fetch (None means failed).

    Returns:
        A label string when --live-prices was used, None otherwise.
    """
    if not prices_live:
        return None
    if live_prices is None:
        return "[prices: fallback (live fetch failed)]"
    return "[prices: live via OpenRouter]"


def _get_prices(
    prices_live: bool,
) -> tuple[dict[str, float], dict[str, float] | None]:
    """Resolve per-model prices.

    Args:
        prices_live: Whether to attempt a live fetch.

    Returns:
        Tuple of (price_per_1m_by_openrouter_id, raw_prices_dict_or_None).
    """
    live_prices: dict[str, float] | None = None
    if prices_live:
        live_prices = fetch_live_prices()
    price_map: dict[str, float] = {}
    for m in MODELS:
        oid = str(m["openrouter_id"])
        if live_prices is not None and oid in live_prices:
            price_map[oid] = live_prices[oid]
        else:
            price_map[oid] = float(m["hardcoded_price_per_1m"])
    return price_map, live_prices


def output_basic(
    token_count: int,
    prices_live: bool,
) -> None:
    """Print basic mode output (tokens + cost estimates)."""
    price_map, live_prices = _get_prices(prices_live)

    print(f"Tokens: {format_number(token_count)}")
    label = _price_label(prices_live, live_prices)
    if label is not None:
        print(label)
    print()
    print("Cost estimates (input tokens):")

    for m in MODELS:
        oid = str(m["openrouter_id"])
        ppm = price_map[oid]
        cost = (token_count / 1_000_000) * ppm
        print(f"  {m['display_name']:<20} ${format_cost(cost)}")


def output_diff(
    path1: str,
    path2: str,
    prices_live: bool,
) -> None:
    """Print diff mode output (two-file comparison)."""
    try:
        text1 = read_file(path1)
        text2 = read_file(path2)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    count1 = count_tokens(text1)
    count2 = count_tokens(text2)
    delta = count2 - count1
    delta_pct = (delta / count1 * 100) if count1 > 0 else 0.0
    delta_sign = "+" if delta >= 0 else ""

    price_map, live_prices = _get_prices(prices_live)

    print(f"File 1: {path1:30s} → {format_number(count1):>8} tokens")
    print(f"File 2: {path2:30s} → {format_number(count2):>8} tokens")
    print()
    print(f"Delta: {delta_sign}{format_number(delta)} tokens  ({delta_sign}{delta_pct:.1f}%)")
    print()
    label = _price_label(prices_live, live_prices)
    if label is not None:
        print(label)
        print()
    print("Cost delta per model:")

    for m in MODELS:
        oid = str(m["openrouter_id"])
        ppm = price_map[oid]
        cost1 = (count1 / 1_000_000) * ppm
        cost2 = (count2 / 1_000_000) * ppm
        cost_delta = cost2 - cost1
        delta_sign_cost = "+" if cost_delta >= 0 else ""
        print(f"  {m['display_name']:<20} {delta_sign_cost}${format_cost(cost_delta)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Returns:
        The configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Count tokens and estimate LLM API costs.",
    )
    parser.add_argument(
        "--text",
        "-t",
        type=str,
        default=None,
        help="Inline text to count tokens for.",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        default=None,
        help="Path to a file whose content should be tokenized.",
    )
    parser.add_argument(
        "--diff",
        "-d",
        type=str,
        nargs=2,
        metavar=("FILE1", "FILE2"),
        default=None,
        help="Diff mode: compare token counts of two files.",
    )
    parser.add_argument(
        "--live-prices",
        action="store_true",
        default=False,
        help="Fetch real-time pricing from OpenRouter API.",
    )
    return parser


def get_input_text(args: argparse.Namespace) -> str:
    """Resolve the input text from the provided arguments or stdin.

    Priority: --text > --file > stdin pipe.

    Args:
        args: Parsed command-line arguments.

    Returns:
        The input text string.

    Raises:
        SystemExit: If no input source is available.
    """
    if args.text is not None:
        return args.text

    if args.file is not None:
        try:
            return read_file(args.file)
        except FileNotFoundError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    stdin_text = read_stdin()
    if stdin_text is not None:
        return stdin_text

    print(
        "Error: no input provided. Use --text, --file, or pipe data via stdin.",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.diff is not None:
        output_diff(args.diff[0], args.diff[1], args.live_prices)
    else:
        text = get_input_text(args)
        token_count = count_tokens(text)
        output_basic(token_count, args.live_prices)


if __name__ == "__main__":
    main()
