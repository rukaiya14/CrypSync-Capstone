"""
Visualization Service
Transforms historical data into chart-ready format
"""
from decimal import Decimal

class VisualizationService:
    def prepare_chart_data(self, price_snapshots):
        """Transform price snapshots into chart data structure"""
        try:
            if not price_snapshots:
                return {
                    'labels': [],
                    'datasets': []
                }
            
            # Extract labels (timestamps) and data (prices)
            labels = []
            prices = []
            
            for snapshot in price_snapshots:
                # Format timestamp for display
                timestamp = snapshot['timestamp']
                label = timestamp.strftime('%Y-%m-%d %H:%M')
                labels.append(label)
                
                # Convert Decimal to float for JSON serialization
                price = float(snapshot['price_usd'])
                prices.append(price)
            
            # Get crypto name from first snapshot
            crypto_name = price_snapshots[0]['crypto_id'].capitalize()
            
            chart_data = {
                'labels': labels,
                'datasets': [{
                    'label': f'{crypto_name} Price (USD)',
                    'data': prices,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'tension': 0.1
                }]
            }
            
            return chart_data
        
        except Exception as e:
            print(f"Error preparing chart data: {e}")
            return {'labels': [], 'datasets': []}
    
    def calculate_axis_scaling(self, prices):
        """Calculate appropriate Y-axis min, max, and step values"""
        if not prices:
            return {'min': 0, 'max': 100, 'step': 10}
        
        min_price = min(prices)
        max_price = max(prices)
        
        # Add 10% padding
        padding = (max_price - min_price) * 0.1
        
        return {
            'min': max(0, min_price - padding),
            'max': max_price + padding,
            'step': (max_price - min_price) / 10
        }
