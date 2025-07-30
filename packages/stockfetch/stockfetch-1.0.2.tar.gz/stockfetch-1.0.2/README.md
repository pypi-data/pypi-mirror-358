<div align="center">

# Stockfetch
</div>

**Neofetch for stocks**
![Screenshot](./image.png)

This is one of my first ventures into creating pip packages, and much of it came into fruition because of my love of (neo/fast)fetch

I've spent lots of time on r/UnixPorn and I hope they have something new to play around with now :)

## Installation
>pip install stockfetch 


### Note:

Older versions of windows CMD might not support ANSI colors by default. Consider using powershell.


Help:
```
avni@fedora:~/source/repos/StockFetch$ stockfetch -h
usage: stockfetch [-h] [--no-logo] ticker

StockFetch - Display stock information with ASCII art logos

positional arguments:
  ticker      Stock ticker symbol (e.g., AAPL, TSLA)

options:
  -h, --help  show this help message and exit
  --no-logo   Skip ASCII logo display

Example: stockfetch TSLA
```
