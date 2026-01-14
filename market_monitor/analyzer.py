"""Market trend analyzer."""

from typing import Dict, List
from utils.logger import get_logger
from utils.helpers import format_percentage

logger = get_logger(__name__)


class MarketAnalyzer:
    """Analyze market trends and generate insights."""
    
    def __init__(self):
        """Initialize market analyzer."""
        pass
    
    def determine_sentiment(self, indices_data: List[Dict]) -> str:
        """
        Determine overall market sentiment based on index performance.
        
        Args:
            indices_data: List of index data dictionaries
        
        Returns:
            Sentiment string: 'bullish', 'bearish', or 'neutral'
        """
        if not indices_data:
            return 'neutral'
        
        # Calculate average change percent
        total_change = sum(data.get('change_percent', 0) for data in indices_data)
        avg_change = total_change / len(indices_data)
        
        # Determine sentiment
        if avg_change > 0.5:
            return 'bullish'
        elif avg_change < -0.5:
            return 'bearish'
        else:
            return 'neutral'
    
    def analyze_trends(self, indices_data: List[Dict]) -> Dict:
        """
        Analyze market trends across different market caps.
        
        Args:
            indices_data: List of index data with 'type' field
        
        Returns:
            Dictionary with trend analysis
        """
        analysis = {
            'large_cap': {'count': 0, 'avg_change': 0, 'trend': 'neutral'},
            'mid_cap': {'count': 0, 'avg_change': 0, 'trend': 'neutral'},
            'small_cap': {'count': 0, 'avg_change': 0, 'trend': 'neutral'},
            'overall_sentiment': 'neutral'
        }
        
        # Group by type
        for data in indices_data:
            index_type = data.get('type', 'unknown')
            change = data.get('change_percent', 0)
            
            if index_type in analysis:
                analysis[index_type]['count'] += 1
                analysis[index_type]['avg_change'] += change
        
        # Calculate averages and trends
        for cap_type in ['large_cap', 'mid_cap', 'small_cap']:
            if analysis[cap_type]['count'] > 0:
                avg = analysis[cap_type]['avg_change'] / analysis[cap_type]['count']
                analysis[cap_type]['avg_change'] = round(avg, 2)
                
                # Determine trend
                if avg > 0.3:
                    analysis[cap_type]['trend'] = 'up'
                elif avg < -0.3:
                    analysis[cap_type]['trend'] = 'down'
                else:
                    analysis[cap_type]['trend'] = 'flat'
        
        # Overall sentiment
        analysis['overall_sentiment'] = self.determine_sentiment(indices_data)
        
        return analysis
    
    def detect_significant_moves(self, indices_data: List[Dict], threshold: float = 2.0) -> List[Dict]:
        """
        Detect indices with significant price movements.
        
        Args:
            indices_data: List of index data
            threshold: Change percentage threshold for significance
        
        Returns:
            List of indices with significant moves
        """
        significant_moves = []
        
        for data in indices_data:
            change_pct = abs(data.get('change_percent', 0))
            if change_pct >= threshold:
                significant_moves.append({
                    'name': data.get('name'),
                    'change_percent': data.get('change_percent'),
                    'current_price': data.get('current_price'),
                    'direction': 'up' if data.get('change_percent', 0) > 0 else 'down'
                })
        
        return significant_moves
    
    def generate_insights(self, indices_data: List[Dict], sector_data: List[Dict] = None) -> List[str]:
        """
        Generate human-readable market insights.
        
        Args:
            indices_data: List of index data
            sector_data: Optional sector performance data
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Overall sentiment
        sentiment = self.determine_sentiment(indices_data)
        sentiment_emoji = {'bullish': '📈', 'bearish': '📉', 'neutral': '➡️'}
        insights.append(f"{sentiment_emoji[sentiment]} Market Sentiment: {sentiment.upper()}")
        
        # Trend analysis
        trends = self.analyze_trends(indices_data)
        
        # Large cap trend
        large_cap = trends['large_cap']
        if large_cap['count'] > 0:
            trend_desc = large_cap['trend'].upper()
            insights.append(
                f"Large-cap indices trending {trend_desc} "
                f"(avg: {format_percentage(large_cap['avg_change'])})"
            )
        
        # Mid/Small cap trend
        mid_cap = trends['mid_cap']
        small_cap = trends['small_cap']
        
        if mid_cap['count'] > 0:
            insights.append(
                f"Mid-cap trend: {mid_cap['trend'].upper()} "
                f"({format_percentage(mid_cap['avg_change'])})"
            )
        
        if small_cap['count'] > 0:
            insights.append(
                f"Small-cap trend: {small_cap['trend'].upper()} "
                f"({format_percentage(small_cap['avg_change'])})"
            )
        
        # Significant moves
        sig_moves = self.detect_significant_moves(indices_data, threshold=1.5)
        if sig_moves:
            insights.append("⚠️ Significant moves detected:")
            for move in sig_moves:
                direction_symbol = "🔼" if move['direction'] == 'up' else "🔽"
                insights.append(
                    f"  {direction_symbol} {move['name']}: "
                    f"{format_percentage(move['change_percent'])}"
                )
        
        # Sector performance
        if sector_data:
            top_sector = sector_data[0] if sector_data else None
            bottom_sector = sector_data[-1] if sector_data else None
            
            if top_sector:
                insights.append(
                    f"🏆 Top sector: {top_sector['sector']} "
                    f"({format_percentage(top_sector['change_percent'])})"
                )
            if bottom_sector and len(sector_data) > 1:
                insights.append(
                    f"📊 Bottom sector: {bottom_sector['sector']} "
                    f"({format_percentage(bottom_sector['change_percent'])})"
                )
        
        return insights
