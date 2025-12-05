"""
Quick Scan Mode - Fast parallel collection of basic trader stats
Collects: PnL, volume, trades, win rate, avg bet size
Goal: 1000+ traders in 3 days
"""

import requests
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class QuickScanner:
    """Fast parallel trader scanning with minimal stats"""
    
    def __init__(self, data_file='traders_quick.json'):
        self.data_api = "https://data-api.polymarket.com"
        self.headers = {"Accept": "application/json"}
        self.data_file = data_file
        self.database = self.load_database()
        
    def load_database(self):
        """Load existing quick scan database"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    print(f"✓ Loaded {len(data)} traders from quick scan")
                    return data
            except:
                print("⚠ Starting fresh database")
                return {}
        return {}
    
    def save_database(self):
        """Save database"""
        with open(self.data_file, 'w') as f:
            json.dump(self.database, f, indent=2)
        print(f"✓ Saved {len(self.database)} traders")
    
    def get_recent_traders(self, limit=500, offset=0):
        """Get recent active traders"""
        url = f"{self.data_api}/trades"
        params = {"limit": limit, "offset": offset}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            trades = response.json()
            addresses = list(set(t.get('proxyWallet') for t in trades if t.get('proxyWallet')))
            return addresses
        except Exception as e:
            print(f"Error fetching traders: {e}")
            return []
    
    def quick_analyze_trader(self, address):
        """
        Fast analysis - only essential stats
        Returns: dict with basic stats or None
        """
        try:
            # Get trades
            url = f"{self.data_api}/trades"
            params = {"user": address, "limit": 500}
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code != 200:
                return None
            
            trades = response.json()
            if not trades:
                return None
            
            # Get positions
            url = f"{self.data_api}/positions"
            params = {"user": address, "limit": 100}
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            positions = response.json() if response.status_code == 200 else []
            
            # Calculate basic stats
            total_trades = len(trades)
            
            # Volume and avg bet
            total_volume = 0
            for trade in trades:
                size = abs(float(trade.get('usdcSize', 0)))
                if size == 0:
                    size = abs(float(trade.get('size', 0)) * float(trade.get('price', 1)))
                total_volume += size
            
            avg_bet_size = total_volume / total_trades if total_trades > 0 else 0
            
            # PnL
            total_pnl = sum(float(p.get('cashPnl', 0)) for p in positions)
            
            # Win rate
            wins = sum(1 for p in positions if float(p.get('cashPnl', 0)) > 5)
            losses = sum(1 for p in positions if float(p.get('cashPnl', 0)) < -5)
            win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
            
            # Username
            username = trades[0].get('name', '') or trades[0].get('pseudonym', 'Anonymous')
            
            return {
                'address': address,
                'username': username,
                'pnl': round(total_pnl, 2),
                'volume': round(total_volume, 2),
                'trades': total_trades,
                'avg_bet': round(avg_bet_size, 2),
                'win_rate': round(win_rate, 3),
                'wins': wins,
                'losses': losses,
                'scanned_at': datetime.now().isoformat(),
                'detailed_analysis': False  # Flag for phase 2
            }
            
        except Exception as e:
            print(f"  Error analyzing {address[:10]}: {e}")
            return None
    
    def parallel_scan(self, addresses, max_workers=5):
        """
        Scan multiple traders in parallel
        
        Parameters:
        - addresses: List of trader addresses
        - max_workers: Number of parallel threads (default: 5)
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_address = {
                executor.submit(self.quick_analyze_trader, addr): addr 
                for addr in addresses
            }
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_address):
                completed += 1
                if completed % 10 == 0:
                    print(f"  Completed: {completed}/{len(addresses)}")
                
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"  Task failed: {e}")
        
        return results
    
    def run_quick_scan(self, target_new=150, max_workers=5):
        """
        Main quick scan execution
        
        Parameters:
        - target_new: Target number of new traders to find
        - max_workers: Parallel threads (5 recommended)
        """
        print("\n" + "="*80)
        print(f"QUICK SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        print(f"\nTarget: {target_new} new traders")
        print(f"Parallel workers: {max_workers}")
        
        # Get recent traders
        print("\n1. Fetching active traders...")
        all_recent = []
        for page in range(3):  # Check 3 pages = 1500 trades
            traders = self.get_recent_traders(limit=500, offset=page*500)
            all_recent.extend(traders)
            if len(traders) < 500:
                break
            time.sleep(0.5)
        
        all_recent = list(set(all_recent))  # Remove duplicates
        print(f"   Found {len(all_recent)} unique active traders")
        
        # Filter for new traders
        known = set(self.database.keys())
        new_traders = [t for t in all_recent if t not in known]
        existing_traders = [t for t in all_recent if t in known]
        
        print(f"   - New: {len(new_traders)}")
        print(f"   - Already scanned: {len(existing_traders)}")
        
        # Select traders to scan (prioritize new)
        to_scan = new_traders[:target_new]
        
        if len(to_scan) < target_new and existing_traders:
            # Add some existing for updates
            to_scan.extend(existing_traders[:target_new - len(to_scan)])
        
        print(f"\n2. Scanning {len(to_scan)} traders in parallel...")
        start_time = time.time()
        
        results = self.parallel_scan(to_scan, max_workers=max_workers)
        
        elapsed = time.time() - start_time
        print(f"\n3. Scan complete in {elapsed:.1f} seconds")
        print(f"   Successfully analyzed: {len(results)}")
        print(f"   Speed: {len(results)/elapsed:.1f} traders/second")
        
        # Update database
        new_count = 0
        updated_count = 0
        
        for result in results:
            address = result['address']
            if address not in self.database:
                new_count += 1
            else:
                updated_count += 1
            self.database[address] = result
        
        print(f"\n4. Database updated:")
        print(f"   - New traders added: {new_count}")
        print(f"   - Existing updated: {updated_count}")
        print(f"   - Total in database: {len(self.database)}")
        
        # Save
        self.save_database()
        
        # Export promising traders
        self.export_promising()
        
        return {
            'scanned': len(results),
            'new': new_count,
            'updated': updated_count,
            'total': len(self.database)
        }
    
    def export_promising(self):
        """Export list of promising traders for deep analysis"""
        promising = []
        
        for address, data in self.database.items():
            # Filter criteria for "promising"
            if (data['pnl'] >= 200 and 
                data['win_rate'] >= 0.50 and 
                data['trades'] >= 20 and
                not data.get('detailed_analysis', False)):
                
                promising.append(address)
        
        with open('promising_traders.json', 'w') as f:
            json.dump(promising, f, indent=2)
        
        print(f"\n✓ Exported {len(promising)} promising traders for deep analysis")
    
    def get_stats(self):
        """Get database statistics"""
        if not self.database:
            return "No traders scanned yet"
        
        total = len(self.database)
        avg_pnl = sum(t['pnl'] for t in self.database.values()) / total
        avg_wr = sum(t['win_rate'] for t in self.database.values()) / total
        
        detailed = sum(1 for t in self.database.values() if t.get('detailed_analysis', False))
        promising = sum(1 for t in self.database.values() 
                       if t['pnl'] >= 200 and t['win_rate'] >= 0.50 and t['trades'] >= 20)
        
        return f"""
Database Stats:
- Total traders: {total}
- Avg PnL: ${avg_pnl:.2f}
- Avg Win Rate: {avg_wr:.1%}
- Detailed analysis done: {detailed}
- Promising traders: {promising}
        """

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("POLYMARKET QUICK SCANNER - Phase 1")
    print("="*80)
    
    scanner = QuickScanner()
    
    # Show current stats
    print(scanner.get_stats())
    
    # Run scan
    results = scanner.run_quick_scan(
        target_new=150,    # Collect 150 traders per run
        max_workers=5      # 5 parallel workers (safe)
    )
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Scanned: {results['scanned']}")
    print(f"New: {results['new']}")
    print(f"Total database: {results['total']}")
    print(f"\nRun this 4x/day for 3 days = 1,800+ traders!")
    print("="*80)
