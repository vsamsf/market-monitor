"""Market summary generator."""

from typing import List, Dict, Optional
from datetime import datetime
from utils.logger import get_logger
from utils.helpers import get_ist_now, format_datetime, format_percentage
from market_monitor.data_fetcher import MarketDataFetcher
from market_monitor.analyzer import MarketAnalyzer

logger = get_logger(__name__)


class SummaryGenerator:
    """Generate market summaries and reports."""
    
    def __init__(self):
        """Initialize summary generator."""
        self.data_fetcher = MarketDataFetcher()
        self.analyzer = MarketAnalyzer()
    
    def generate_daily_summary(
        self,
        indices: List[Dict[str, str]],
        include_sectors: bool = True
    ) -> str:
        """
        Generate daily market summary.
        
        Args:
            indices: List of index configurations
            include_sectors: Whether to include sector performance
        
        Returns:
            Formatted summary string
        """
        try:
            current_time = get_ist_now()
            
            # Fetch market data
            logger.info("Fetching market data for daily summary")
            indices_data = self.data_fetcher.fetch_multiple_indices(indices)
            
            if not indices_data:
                return "⚠️ Unable to fetch market data at this time."
            
            # Fetch sector data if requested
            sector_data = []
            if include_sectors:
                sector_data = self.data_fetcher.get_sector_performance()
            
            # Generate insights
            insights = self.analyzer.generate_insights(indices_data, sector_data)
            
            # Build summary
            summary_lines = [
                "=" * 60,
                "📊 DAILY MARKET SUMMARY",
                "=" * 60,
                f"Generated: {format_datetime(current_time, '%A, %B %d, %Y at %I:%M %p IST')}",
                "",
                "📈 INDEX PERFORMANCE",
                "-" * 60
            ]
            
            # Add index data
            for data in indices_data:
                change_symbol = "+" if data['change'] >= 0 else ""
                arrow = "🟢" if data['change'] >= 0 else "🔴"
                
                summary_lines.append(
                    f"{arrow} {data['name']:<25} {data['current_price']:>10,.2f} "
                    f"({change_symbol}{format_percentage(data['change_percent'])})"
                )
            
            summary_lines.extend([
                "",
                "💡 MARKET INSIGHTS",
                "-" * 60
            ])
            
            # Add insights
            for insight in insights:
                summary_lines.append(insight)
            
            # Add sector performance if available
            if sector_data:
                summary_lines.extend([
                    "",
                    "🏭 SECTOR PERFORMANCE",
                    "-" * 60
                ])
                
                for sector in sector_data[:5]:  # Top 5 sectors
                    change_symbol = "+" if sector['change_percent'] >= 0 else ""
                    bar = "█" * int(abs(sector['change_percent']) * 2)
                    
                    summary_lines.append(
                        f"{sector['sector']:<20} {change_symbol}{format_percentage(sector['change_percent']):>7} {bar}"
                    )
            
            summary_lines.append("=" * 60)
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return f"⚠️ Error generating market summary: {str(e)}"
    
    def generate_live_update(self, indices: List[Dict[str, str]]) -> str:
        """
        Generate quick live market update.
        
        Args:
            indices: List of index configurations
        
        Returns:
            Formatted update string
        """
        try:
            current_time = get_ist_now()
            
            # Fetch current data
            indices_data = self.data_fetcher.fetch_multiple_indices(indices)
            
            if not indices_data:
                return "⚠️ Unable to fetch market data."
            
            # Build update
            update_lines = [
                f"⏰ Market Update - {format_datetime(current_time, '%I:%M %p IST')}",
                ""
            ]
            
            for data in indices_data:
                change_symbol = "+" if data['change'] >= 0 else ""
                arrow = "🟢" if data['change'] >= 0 else "🔴"
                
                update_lines.append(
                    f"{arrow} {data['name']}: {data['current_price']:,.2f} "
                    f"({change_symbol}{format_percentage(data['change_percent'])})"
                )
            
            # Add sentiment
            sentiment = self.analyzer.determine_sentiment(indices_data)
            sentiment_text = {"bullish": "📈 Bullish", "bearish": "📉 Bearish", "neutral": "➡️ Neutral"}
            update_lines.append(f"\nSentiment: {sentiment_text[sentiment]}")
            
            return "\n".join(update_lines)
            
        except Exception as e:
            logger.error(f"Error generating live update: {e}")
            return f"⚠️ Error: {str(e)}"
    
    def generate_alert_message(self, index_data: Dict, previous_data: Dict) -> Optional[str]:
        """
        Generate alert message if significant change detected.
        
        Args:
            index_data: Current index data
            previous_data: Previous index data
        
        Returns:
            Alert message or None
        """
        try:
            current_price = index_data.get('current_price', 0)
            previous_price = previous_data.get('current_price', 0)
            
            if previous_price == 0:
                return None
            
            change_pct = ((current_price - previous_price) / previous_price) * 100
            
            # Check if change is significant (>1.5%)
            if abs(change_pct) >= 1.5:
                direction = "surged" if change_pct > 0 else "dropped"
                emoji = "🚨" if abs(change_pct) >= 2.0 else "⚠️"
                
                return (
                    f"{emoji} ALERT: {index_data['name']} has {direction} "
                    f"{format_percentage(abs(change_pct))} to {current_price:,.2f} "
                    f"in the last 30 minutes!"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating alert: {e}")
            return None
