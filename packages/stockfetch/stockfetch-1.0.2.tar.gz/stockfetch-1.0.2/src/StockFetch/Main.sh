#!/bin/bash

# Validate input
if [ $# -eq 0 ]; then
    echo "Usage: $0 <TICKER>"
    echo "Example: $0 AAPL"
    exit 1
fi

# Fetch ASCII art with improved error handling
asciiArt=$(python3 -c "import Pyfinance; Pyfinance.make_ascii('https://github.com/nvstly/icons/blob/main/ticker_icons/' + '$@' + '.png?raw=true', '$@', 28, 28, 1)" 2>/dev/null)

# If ASCII art failed, create a fallback ticker display
if [[ "$asciiArt" == *"Invalid ticker"* ]] then
    # Create a simple ASCII ticker display as fallback
    ticker_upper=$(echo "$@ "| tr '[:lower:]' '[:upper:]')
    asciiArt="
┌────────────────────────────┐
│                            │
│         $ticker_upper      │
│       [ NO LOGO ]          │
│                            │
└────────────────────────────┘"
fi

# Fetch stock information
info=$(python3 -c "import Pyfinance; Pyfinance.ticker('$@')")

# Calculate terminal width for proper formatting
termWidth=$(tput cols)
tWidth=$(expr $termWidth - 7)

# Output the combined ASCII art and info
while IFS= read -r art && IFS= read -r inf <&3; do
    printf '%-28s  %s\n' "$art" "$inf"
done  < <(printf '%s\n' "$asciiArt") \
      3< <(printf '%s\n' "$info")