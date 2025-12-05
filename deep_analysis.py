"""
Deep Analysis Mode - Phase 2
Adds detailed stats to promising traders from quick scan
Categories, badges, specialization, timing, etc.
"""

import requests
import json
import os
from datetime import datetime
from collections import defaultdict
import time
import statistics

class DeepAnalyzer:
    """Detailed analysis for promising traders"""
    
    def __init__(self, 
                 quick_file='traders_quick.json',
                 detailed_file='traders_detailed.json',
                 promising_file='promising_traders.json'):
        self.data_api = "https://data-api.polymarket.com"
        self.gamma_api = "https://gamma-api.polymarket.com"
        self.headers = {"Accept": "application/json"}
        
        self.quick_file = quick_file
        self.detailed_file = detailed_file
        self.promising_file = promising_file
        
        self.quick_db = self.load_json(quick_file)
        self.detailed_db = self.load_json(detailed_file)
        self.market_cache = {}
        
    def load_json(self, filename):
        """Load JSON file"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_detailed(self):
        """Save detailed database"""
        with open(self.detailed_file, 'w') as f:
            json.dump(self.detailed_db, f, indent=2)
        print(f"✓ Saved {len(self.detailed_db)} detailed profiles")
    
    def get_promising_traders(self, limit=100):
        """Get list of promising traders to analyze"""
        if os.path.exists(self.promising_file):
            with open(self.promising_file, 'r') as f:
                return json.load(f)[:limit]
        
        # Fallback: filter from quick scan
        promising = []
        for address, data in self.quick_db.items():
            if (data['pnl'] >= 200 and 
                data['win_rate'] >= 0.50 and 
                data['trades'] >= 20 and
                address not in self.detailed_db):
                promising.append(address)
        
        return promising[:limit]
    
    def categorize_market(self, tags):
        """Categorize market from tags"""
        if not tags:
            return 'Other'
        
        tags_lower = [str(t).lower() for t in tags]
        
        if any(k in tags_lower for k in ['politics', 'election', 'biden', 'trump', 'congress']):
            return 'Politics'
        elif any(k in tags_lower for k in ['sports', 'nba', 'nfl', 'mlb', 'soccer', 'football']):
            return 'Sports'
        elif any(k in tags_lower for k in ['crypto', 'bitcoin', 'ethereum', 'btc', 'eth']):
            return 'Crypto'
        elif any(k in tags_lower for k in ['business', 'tech', 'stocks', 'economy']):
            return 'Business'
        elif any(k in tags_lower for k in ['entertainment', 'celebrity', 'movies', 'music']):
            return 'Entertainment'
        elif any(k in tags_lower for k in ['science', 'ai', 'technology', 'space']):
            return 'Science'
        else:
            return 'Other'
    
    def calculate_badges(self, trades, positions):
        """Calculate trader badges"""
        badges = []
        
        if not trades:
            return badges
        
        # Entry prices
        entry_prices = [float(t.get('price', 0.5)) for t in trades if 0 < float(t.get('price', 0)) <= 1]
        
        if entry_prices:
            low_prob = sum(1 for p in entry_prices if p < 0.5)
            
            # CONTRARIAN
            if low_prob == len(entry_prices):
                badges.append('Contrarian')
            
            # LOTTERY TICKET
            lottery_count = sum(1 for p in positions if float(p.get('cashPnl', 0)) > 100)
            if lottery_count > 0 and low_prob > len(entry_prices) * 0.5:
                badges.append('Lottery Ticket')
        
        # Position count badges
        if len(positions) >= 500:
            badges.append('Veteran')
        elif len(positions) >= 100:
            badges.append('Novice')
        
        # Volume badges
        total_volume = sum(
            abs(float(t.get('usdcSize', 0)) or float(t.get('size', 0)) * float(t.get('price', 1)))
            for t in trades
        )
        
        if total_volume > 500000:
            badges.append('Whale')
        elif total_volume > 100000:
            badges.append('High Roller')
        
        return badges
    
    def deep_analyze_trader(self, address):
        """
        Comprehensive analysis with all details
        """
        print(f"  Analyzing {address[:10]}...")
        
        try:
            # Get basic data from quick scan
            basic = self.quick_db.get(address, {})
            
            # Fetch fresh trades and positions
            url = f"{self.data_api}/trades"
            params = {"user": address, "limit": 500}
            response = requests.get(url, headers=self.headers, params=params, timeout=20)
            trades = response.json() if response.status_code == 200 else []
            
            url = f"{self.data_api}/positions"
            params = {"user": address, "limit": 200}
            response = requests.get(url, headers=self.headers, params=params, timeout=20)
            positions = response.json() if response.status_code == 200 else []
            
            if not trades:
                return None
            
            # Category analysis
            category_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0})
            
            for trade in trades:
                # Simplified category detection from trade data
                # (Full market API calls would be too slow)
                condition_id = trade.get('conditionId', '')
                # Use basic heuristic or skip detailed categorization
                category = 'Other'  # Placeholder
                category_stats[category]['trades'] += 1
            
            for pos in positions:
                pnl = float(pos.get('cashPnl', 0))
                category = 'Other'  # Simplified
                category_stats[category]['pnl'] += pnl
                if pnl > 5:
                    category_stats[category]['wins'] += 1
                elif pnl < -5:
                    category_stats[category]['losses'] += 1
            
            # Main category
            if category_stats:
                main_category = max(category_stats.items(), key=lambda x: x[1]['trades'])[0]
                specialization_pct = category_stats[main_category]['trades'] / len(trades)
            else:
                main_category = 'Other'
                specialization_pct = 0
            
            # Badges
            badges = self.calculate_badges(trades, positions)
            
            # Both-sides betting
            market_sides = defaultdict(set)
            for trade in trades:
                market_id = trade.get('conditionId', '')
                side = trade.get('side', '')
                if market_id and side:
                    market_sides[market_id].add(side)
            
            both_sides_count = sum(1 for sides in market_sides.values() if len(sides) > 1)
            both_sides_ratio = both_sides_count / len(market_sides) if market_sides else 0
            
            # Entry price analysis
            entry_prices = [float(t.get('price', 0.5)) for t in trades if 0 < float(t.get('price', 0)) <= 1]
            avg_entry_price = statistics.mean(entry_prices) if entry_prices else 0.5
            
            # Max drawdown (simplified)
            pnl_values = sorted([float(p.get('cashPnl', 0)) for p in positions])
            max_drawdown = 0
            if pnl_values:
                cumulative = 0
                peak = 0
                for pnl in pnl_values:
                    cumulative += pnl
                    peak = max(peak, cumulative)
                    drawdown = peak - cumulative
                    max_drawdown = max(max_drawdown, drawdown)
            
            # Combine with basic stats
            detailed = {
                **basic,  # Include all quick scan data
                'badges': badges,
                'main_category': main_category,
                'specialization_pct': round(specialization_pct, 3),
                'both_sides_ratio': round(both_sides_ratio, 3),
                'avg_entry_price': round(avg_entry_price, 3),
                'max_drawdown': round(max_drawdown, 2),
                'unique_markets': len(set(t.get('conditionId', '') for t in trades)),
                'detailed_analysis': True,
                'analyzed_at': datetime.now().isoformat()
            }
            
            return detailed
            
        except Exception as e:
            print(f"    Error: {e}")
            return None
    
    def run_deep_analysis(self, max_analyze=100):
        """
        Main deep analysis execution
        
        Parameters:
        - max_analyze: Maximum number of traders to analyze
        """
        print("\n" + "="*80)
        print(f"DEEP ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Get promising traders
        print("\n1. Loading promising traders...")
        promising = self.get_promising_traders(limit=max_analyze)
        
        if not promising:
            print("   No promising traders found!")
            print("   Make sure quick_scan.py has run first")
            return
        
        print(f"   Found {len(promising)} promising traders to analyze")
        
        # Analyze each
        print(f"\n2. Running deep analysis...")
        analyzed_count = 0
        
        for i, address in enumerate(promising):
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(promising)}")
            
            result = self.deep_analyze_trader(address)
            
            if result:
                self.detailed_db[address] = result
                
                # Mark as analyzed in quick scan too
                if address in self.quick_db:
                    self.quick_db[address]['detailed_analysis'] = True
                
                analyzed_count += 1
            
            time.sleep(0.3)  # Rate limiting
        
        print(f"\n3. Analysis complete:")
        print(f"   Successfully analyzed: {analyzed_count}/{len(promising)}")
        
        # Save both databases
        self.save_detailed()
        
        with open(self.quick_file, 'w') as f:
            json.dump(self.quick_db, f, indent=2)
        print(f"✓ Updated quick scan database")
        
        # Export top traders by category
        self.export_by_category()
        
        return analyzed_count
    
    def export_by_category(self):
        """Export top traders by category to CSVs"""
        import pandas as pd
        
        if not self.detailed_db:
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(self.detailed_db.values())
        
        # Export all
        df.to_csv('traders_detailed_all.csv', index=False)
        print(f"✓ Exported traders_detailed_all.csv ({len(df)} traders)")
        
        # Export by category
        for category in df['main_category'].unique():
            cat_df = df[df['main_category'] == category].sort_values('pnl', ascending=False)
            filename = f'traders_{category.lower()}.csv'
            cat_df.head(50).to_csv(filename, index=False)
            print(f"✓ Exported {filename} (top 50 {category} traders)")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("POLYMARKET DEEP ANALYZER - Phase 2")
    print("="*80)
    
    analyzer = DeepAnalyzer()
    
    # Run deep analysis on promising traders
    analyzed = analyzer.run_deep_analysis(max_analyze=100)
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    print(f"Analyzed {analyzed} traders in detail")
    print("Check CSV files for results by category!")
    print("="*80)
