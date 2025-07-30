#!/usr/bin/env python3
"""
StockFetch CLI - Command line interface for stock information display
"""

import sys
import argparse
from .Pyfinance import ticker, make_ascii


def format_display(ascii_art, info_text):
    """
    Format ASCII art and stock info side by side for display
    """
    if not ascii_art or ascii_art.strip() == "":
        # Create fallback display if no ASCII art
        ticker_name = sys.argv[1].upper() if len(sys.argv) > 1 else "STOCK"
        ascii_art = f"""
┌────────────────────────────┐
│                            │
│         {ticker_name:<8}           │
│       [ NO LOGO ]          │
│                            │
└────────────────────────────┘""".strip()

    ascii_lines = ascii_art.split('\n')
    info_lines = info_text.split('\n')
    
    # Ensure both have the same number of lines
    max_lines = max(len(ascii_lines), len(info_lines))
    while len(ascii_lines) < max_lines:
        ascii_lines.append(' ' * 28)
    while len(info_lines) < max_lines:
        info_lines.append('')
    
    # Combine side by side
    result = []
    for ascii_line, info_line in zip(ascii_lines, info_lines):
        # Strip ANSI codes for width calculation
        import re
        ascii_clean = re.sub(r'\033\[[0-9;]*m', '', ascii_line)
        padded_ascii = ascii_line + ' ' * (28 - len(ascii_clean))
        result.append(f"{padded_ascii}  {info_line}")
    
    return '\n'.join(result)


def main():
    """
    Main CLI entry point
    """
    parser = argparse.ArgumentParser(
        description="StockFetch - Display stock information with ASCII art logos",
        epilog="Example: stockfetch AAPL"
    )
    parser.add_argument('ticker', help='Stock ticker symbol (e.g., AAPL, TSLA)')
    parser.add_argument('--no-logo', action='store_true', help='Skip ASCII logo display')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    ticker_symbol = args.ticker.upper()
    
    try:
        # Capture stock info
        import io
        from contextlib import redirect_stdout
        
        # Get stock info by redirecting stdout
        f = io.StringIO()
        with redirect_stdout(f):
            ticker(ticker_symbol)
        stock_info = f.getvalue()
        
        if not args.no_logo:
            # Get ASCII art
            logo_url = f"https://github.com/nvstly/icons/blob/main/ticker_icons/{ticker_symbol}.png?raw=true"
            f_logo = io.StringIO()
            with redirect_stdout(f_logo):
                ascii_result = make_ascii(logo_url, ticker_symbol, 28, 28, 1)
            
            # If make_ascii printed anything, use that, otherwise use the return value
            logo_output = f_logo.getvalue()
            if logo_output.strip():
                ascii_art = logo_output
            else:
                ascii_art = ascii_result if ascii_result else ""
            
            # Display combined output
            combined_output = format_display(ascii_art, stock_info)
            print(combined_output)
        else:
            # Just display stock info
            print(stock_info)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 