#!/usr/bin/env python3
"""Test script for yfinance market data fetching."""

import yfinance as yf

print(f"yfinance version: {yf.__version__}\n")

# Test different symbols for Indian indices
symbols_to_test = [
    ('^NSEI', 'NIFTY 50'),
    ('^BSESN', 'BSE SENSEX'),
    ('^NSEBANK', 'BANK NIFTY'),
]

for symbol, name in symbols_to_test:
    print(f"\n{'='*60}")
    print(f"Testing: {name} ({symbol})")
    print('='*60)
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        
        if not hist.empty:
            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) >= 2 else latest
            
            price = latest['Close']
            prev_close = prev['Close']
            change = price - prev_close
            change_pct = (change / prev_close) * 100
            
            print(f"✓ SUCCESS!")
            print(f"  Current: {price:.2f}")
            print(f"  Previous: {prev_close:.2f}")
            print(f"  Change: {change:+.2f} ({change_pct:+.2f}%)")
            print(f"  Data points: {len(hist)}")
            print(f"  Latest date: {hist.index[-1]}")
        else:
            print(f"✗ No data returned")
            
    except Exception as e:
        print(f"✗ ERROR: {e}")

print(f"\n{'='*60}")
print("Test complete!")
print('='*60)
