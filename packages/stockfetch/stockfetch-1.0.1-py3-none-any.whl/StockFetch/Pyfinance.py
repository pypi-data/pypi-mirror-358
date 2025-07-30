#!/usr/bin/env python3
import sys
import yfinance as yf
from PIL import Image, ImageEnhance
import requests
from io import BytesIO
import PIL.ImageOps as ImageOps
import numpy as np


def validate_ticker(ticker):
    """
    Validate if a ticker symbol exists and has data available.
    Returns True if valid, False otherwise.
    """
    try:
        dat = yf.Ticker(ticker)
        info = dat.info
        # Check if we have basic required info
        return info and len(info) > 1 and 'symbol' in info
    except:
        return False


def rgb_to_ansi(r, g, b):
    """
    Convert RGB values to ANSI 256-color code.
    """
    # Ensure values are within valid range
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    
    # Convert RGB to 6x6x6 color cube (216 colors)
    # ANSI 256-color: 16-231 are 6x6x6 RGB cube
    r_index = r * 5 // 255
    g_index = g * 5 // 255
    b_index = b * 5 // 255
    
    color_code = 16 + (36 * r_index) + (6 * g_index) + b_index
    return color_code
def validateUrl(url, ticker):
    resp = requests.head(url)
    if(resp.status_code > 400):
        print(resp.status_code)
        return False
    else: return True


def make_ascii(url, ticker, max_width=28, max_height=28, pixel_width=1):
    """
    Generate color-accurate ASCII art from PNG logos with proper transparency handling.
    
    Args:
        url (str): URL to the PNG image
        ticker (str): Stock ticker symbol for validation
        max_width (int): Maximum width of ASCII output
        max_height (int): Maximum height of ASCII output
        pixel_width (int): Pixel sampling width (1 for highest detail)
    
    Returns:
        str: ASCII art string with ANSI colors or empty string if failed
    """
    
    # First validate that this is a real stock ticker
    if not validate_ticker(ticker):
        print(f"Invalid ticker. Try again.")
        return "Invalid ticker. Try again"
    # Second, validate that the URL exists in the github repo rq.
    if not validateUrl(url, ticker):
        print(f"No image found, sorry!")
        return "No image found, sorry!"
    
    # ASCII characters from transparent/light to solid/dark in that order
    chars = " .':\"^,;Il!><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    
    try:
        # Fetch the image with proper headers
        headers = {
            'User-Agent': 'StockFetch/1.0',
            'Accept': 'image/png,image/*;q=0.9,*/*;q=0.8'
        }
        response = requests.get(url)
        # Open the PNG image
        img = Image.open(BytesIO(response.content))
        
        # Ensure we're working with RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            print("converting to RGBA")
        
        # Calculate new dimensions while preserving aspect ratio
        aspect_ratio = img.height / img.width
        new_width = max_width
        new_height = int(max_width * aspect_ratio)

        if new_height > max_height:
            new_height = max_height
            new_width = int(max_height / aspect_ratio)

        # Use high-quality resampling
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to numpy array for processing
        img_array = np.array(img)
        
        # Generate color-accurate ASCII art
        ascii_lines = []
        for y in range(0, img.height, pixel_width):
            row_chars = []
            for x in range(0, img.width, pixel_width):
                r, g, b, a = img_array[y, x]
                
                # a = alpha = 
                if a < 10:
                    row_chars.append(' ')
                    continue
                
                # Calculate luminance for character selection
                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                
                # Use alpha to determine character intensity
                alpha_factor = a / 255.0
                luminance_factor = 1.0 - (luminance / 255.0)  # Invert so dark = high value
                
                # Combine factors for character selection
                intensity = alpha_factor * (0.3 + 0.7 * luminance_factor)
                
                # Map to character index
                char_index = int(intensity * (len(chars) - 1))
                char_index = max(0, min(len(chars) - 1, char_index))
                
                # Get the character
                char = chars[char_index]
                
                # If the pixel has sufficient opacity, apply color
                if a > 50:  # Only color visible pixels
                    # Convert RGB to ANSI color code
                    color_code = rgb_to_ansi(r, g, b)
                    # Create colored character with ANSI escape sequence
                    colored_char = f"\033[38;5;{color_code}m{char}\033[0m"
                    row_chars.append(colored_char)
                else:
                    # Low opacity pixels remain uncolored
                    row_chars.append(char)
            
            ascii_lines.append("".join(row_chars))
        
        # Print the ASCII art
        result = "\n".join(ascii_lines)
        print(result)
        return result
        
    except requests.exceptions.Timeout:
        print(f"# Logo fetch timeout for {ticker}")
        return ""
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"# No logo found for {ticker}")
        else:
            print(f"# Logo unavailable for {ticker}")
        return ""
    except requests.exceptions.RequestException:
        print(f"# Network error fetching logo for {ticker}")
        return ""
    except Exception as e:
        print(f"# Could not process logo for {ticker}: {str(e)}")
        return ""


def main():
    pass


def ticker(ticker: str):
    try:
        dat = yf.Ticker(ticker)
        info = dat.info
        
        validate_ticker(ticker)        
        # Calculate daily change safely
        current_price = info.get('currentPrice', 0)
        open_price = info.get('open', current_price)
        daily_change = current_price - open_price
        daily_percent_change = (daily_change / open_price * 100) if open_price != 0 else 0
        
        # Display information with safe fallbacks
        print('\n', info.get('shortName', ticker.upper()), '\n',
          "Headquarters:", info.get('city', 'N/A'), info.get('state', ''), '\n',
          "Industry:", info.get('industry', 'N/A'), '\n',
          "Daily Change: $", f"{daily_change:.3f}","/",f"{daily_percent_change:.3f}%", '\n',
          "Current Price: $", f"{current_price:.3f}", '\n',
          "Revenue Growth:", f"{info.get('revenueGrowth', 0) * 100:.3f}%", '\n',
          "Current Ratio:", f"{info.get('currentRatio', 0):.3f}", '\n',
          "Total Debt: $", f"{info.get('totalDebt', 0):.3f}", '\n',
          "Gross Margins:", f"{info.get('grossMargins', 0) * 100:.3f}%", '\n',
          "Operating Margins:", f"{info.get('operatingMargins', 0) * 100:.3f}%", '\n',
          "Forward PE:", f"{info.get('forwardPE', 0):.3f}", '\n',
          "52-Week Change:", f"{info.get('52WeekChange', 0) * 100:.3f}%", '\n',
          "Market Capitalization: $", f"{info.get('marketCap', 0):.3f}", '\n',
          "Enterprise Value: $", f"{info.get('enterpriseValue', 0):.3f}", '\n',
          "Free Cash Flow: $", f"{info.get('freeCashflow', 0):.3f}", '\n',
          "Return on Assets (ROA):", f"{info.get('returnOnAssets', 0) * 100:.3f}%", '\n',
          "Trailing EPS:", f"{info.get('trailingEps', 0):.3f}", '\n',
          "Revenue Per Share: $", info.get('revenuePerShare', 0), '\n',
          "Operating Cash Flow: $", info.get('operatingCashflow', 0), '\n',
          "Shares Outstanding:", info.get('sharesOutstanding', 0), '\n'
        )
        
    except Exception as e:
        print(f"\n Error: Could not fetch data for ticker '{ticker}' \n Please verify the ticker symbol and try again.")


if __name__ == "__main__":
    main()
    
    
    
