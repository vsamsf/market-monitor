"""Demo/mock data provider for development and when API fails."""

from datetime import datetime
from typing import Dict, List
import random


def get_demo_indices() -> List[Dict]:
    """Get demo market index data."""
    return [
        {
            'symbol': '^NSEI',
            'name': 'NIFTY 50',
            'current_price': 23450.75,
            'previous_close': 23398.50,
            'change': 52.25,
            'change_percent': 0.22,
            'timestamp': datetime.now()
        },
        {
            'symbol': '^BSESN',
            'name': 'BSE SENSEX',
            'current_price': 78120.30,
            'previous_close': 77980.25,
            'change': 140.05,
            'change_percent': 0.18,
            'timestamp': datetime.now()
        },
        {
            'symbol': '^NSEMDCP50',
            'name': 'NIFTY MIDCAP 50',
            'current_price': 15234.80,
            'previous_close': 15180.50,
            'change': 54.30,
            'change_percent': 0.36,
            'timestamp': datetime.now()
        },
        {
            'symbol': '^CNXSMALLCAP',
            'name': 'NIFTY SMALLCAP 100',
            'current_price': 18956.40,
            'previous_close': 18890.75,
            'change': 65.65,
            'change_percent': 0.35,
            'timestamp': datetime.now()
        }
    ]


def get_demo_summary() -> str:
    """Get demo market summary."""
    return """
📊 MARKET SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 NIFTY 50: 23,450.75 (+52.25, +0.22%)
   Previous Close: 23,398.50
   Market Sentiment: Bullish

📈 BSE SENSEX: 78,120.30 (+140.05, +0.18%)
   Previous Close: 77,980.25
   Market Sentiment: Bullish

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 MARKET INSIGHTS:
• Markets showing positive momentum
• IT and Banking sectors leading gains
• Midcap and Smallcap indices outperforming

🏭 SECTOR PERFORMANCE:
• IT: +0.8% (Strong buying)
• Banking: +0.5% (Positive)
• Auto: +0.3% (Moderate)
• Pharma: -0.1% (Flat to negative)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Note: This is demo data for development/testing purposes.
When the market is open (9:15 AM - 3:30 PM IST) and the API
is available, live data will be displayed.
"""
