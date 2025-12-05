# Polymarket Trader Analyzer - Two-Phase System

**Complete setup guide for automated trader discovery**

---

## 📋 Quick Reference

**File:** This is your `README.md` - copy this entire content when creating the file in GitHub

## 🎯 System Overview

### Phase 1: Quick Scan (Every 6 hours)
- Collects **150 traders per run** with basic stats
- **Parallel processing** (5 workers)
- Stats: PnL, volume, trades, win rate, avg bet
- **4 runs/day × 3 days = 1,800+ traders**

### Phase 2: Deep Analysis (Daily)
- Analyzes **top 100 promising traders** in detail
- Adds: Categories, badges, specialization, timing
- Filters: PnL > $200, Win Rate > 50%, 20+ trades

---

## 📁 Repository Structure

```
polymarket-trader-analyzer/
├── .github/
│   └── workflows/
│       ├── quick-scan.yml         # Runs every 6 hours
│       └── deep-analysis.yml      # Runs daily at 2 AM
├── quick_scan.py                  # Phase 1: Fast collection
├── deep_analysis.py               # Phase 2: Detailed analysis
├── requirements.txt
├── README.md
├── traders_quick.json             # Generated: Basic stats
├── traders_detailed.json          # Generated: Full analysis
├── promising_traders.json         # Generated: List for phase 2
└── *.csv                          # Generated: Exports
```

---

## 🚀 Setup Instructions

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Name: `polymarket-trader-analyzer`
3. Public or Private (your choice)
4. ✅ Add README
5. **Create repository**

### Step 2: Add Workflow Files

#### 2.1: Create `.github/workflows/quick-scan.yml`

1. Click **Add file** → **Create new file**
2. Name: `.github/workflows/quick-scan.yml`
3. Paste:

```yaml
name: Quick Scan (Every 6 Hours)

on:
  schedule:
    # Runs at 00:00, 06:00, 12:00, 18:00 UTC
    - cron: '0 */6 * * *'
  
  # Manual trigger
  workflow_dispatch:

jobs:
  quick-scan:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install requests
    
    - name: Run quick scan
      run: |
        python quick_scan.py
    
    - name: Commit results
      run: |
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        git add traders_quick.json
        git add promising_traders.json
        git diff --quiet && git diff --staged --quiet || (git commit -m "⚡ Quick scan - $(date -u +'%Y-%m-%d %H:%M UTC')" && git push)
```

4. **Commit changes**

#### 2.2: Create `.github/workflows/deep-analysis.yml`

1. Click **Add file** → **Create new file**
2. Name: `.github/workflows/deep-analysis.yml`
3. Paste:

```yaml
name: Deep Analysis (Daily)

on:
  schedule:
    # Runs daily at 2:00 AM UTC
    - cron: '0 2 * * *'
  
  # Manual trigger
  workflow_dispatch:

jobs:
  deep-analysis:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install requests pandas
    
    - name: Run deep analysis
      run: |
        python deep_analysis.py
    
    - name: Commit results
      run: |
        git config --local user.email "github-actions[bot]@users.noreply.github.com"
        git config --local user.name "github-actions[bot]"
        git add traders_detailed.json
        git add traders_quick.json
        git add *.csv || true
        git diff --quiet && git diff --staged --quiet || (git commit -m "🔍 Deep analysis - $(date -u +'%Y-%m-%d %H:%M UTC')" && git push)
```

4. **Commit changes**

### Step 3: Add Python Scripts

#### 3.1: Add `quick_scan.py`

1. Click **Add file** → **Create new file**
2. Name: `quick_scan.py`
3. **Copy the entire script from the "quick_scan.py" artifact above**
4. **Commit changes**

#### 3.2: Add `deep_analysis.py`

1. Click **Add file** → **Create new file**
2. Name: `deep_analysis.py`
3. **Copy the entire script from the "deep_analysis.py" artifact above**
4. **Commit changes**

#### 3.3: Add `requirements.txt`

1. Click **Add file** → **Create new file**
2. Name: `requirements.txt`
3. Paste:

```
requests>=2.31.0
pandas>=2.0.0
```

4. **Commit changes**

### Step 4: Enable GitHub Actions

1. Go to **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**
3. **Save**

### Step 5: Test Manual Run

#### Test Quick Scan:
1. Go to **Actions** tab
2. Click **Quick Scan (Every 6 Hours)**
3. Click **Run workflow** → **Run workflow**
4. Wait 2-3 minutes
5. ✅ Check if `traders_quick.json` appears!

#### Test Deep Analysis (after quick scan completes):
1. Go to **Actions** tab
2. Click **Deep Analysis (Daily)**
3. Click **Run workflow** → **Run workflow**
4. Wait 5-10 minutes
5. ✅ Check for CSV files!

---

## ✅ You're Done! System is Automated

### What Happens Now:

**Every 6 hours** (00:00, 06:00, 12:00, 18:00 UTC):
- ⚡ Quick scan runs
- Collects ~150 new traders
- Updates `traders_quick.json`
- Exports `promising_traders.json`

**Daily at 2:00 AM UTC:**
- 🔍 Deep analysis runs
- Analyzes top 100 promising traders
- Updates `traders_detailed.json`
- Exports CSV files by category

---

## 📊 Expected Timeline

| Day | Quick Scans | New Traders | Detailed | Total Database |
|-----|-------------|-------------|----------|----------------|
| 1   | 4           | ~600        | 100      | 600 quick      |
| 2   | 4           | ~600        | 100      | 1,200 quick    |
| 3   | 4           | ~600        | 100      | 1,800+ quick   |

**After 3 days:**
- 📦 **1,800+ traders** with basic stats
- 🎯 **300+ traders** with detailed analysis
- 📈 **CSV exports** by category

---

## 📥 How to Download & Use Data

### Option 1: Download from GitHub
1. Go to your repository
2. Download these files:
   - `traders_quick.json` - All traders (basic)
   - `traders_detailed.json` - Detailed analysis
   - `traders_sports.csv` - Top sports traders
   - `traders_politics.csv` - Top politics traders
   - etc.

### Option 2: Use in Google Colab

```python
# Download files from your GitHub repo
!wget https://raw.githubusercontent.com/YOUR_USERNAME/polymarket-trader-analyzer/main/traders_detailed.json

# Load and filter
import json
import pandas as pd

with open('traders_detailed.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data.values())

# Filter for sports specialists
sports = df[
    (df['main_category'] == 'Sports') &
    (df['pnl'] > 500) &
    (df['win_rate'] > 0.60) &
    (df['avg_bet'] > 100) &
    (df['avg_bet'] < 3000)
].sort_values('pnl', ascending=False)

print(sports[['username', 'pnl', 'win_rate', 'avg_bet', 'badges']])
```

### Option 3: Clone Repo and Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/polymarket-trader-analyzer.git
cd polymarket-trader-analyzer

# Run quick scan
python quick_scan.py

# Run deep analysis
python deep_analysis.py
```

---

## ⚙️ Configuration

### Change Collection Frequency

Edit `.github/workflows/quick-scan.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'   # Every 6 hours (current)
  # OR
  - cron: '0 */4 * * *'   # Every 4 hours (more frequent)
  - cron: '0 */8 * * *'   # Every 8 hours (less frequent)
```

### Change Number of Traders per Scan

Edit `quick_scan.py`, line ~200:

```python
results = scanner.run_quick_scan(
    target_new=150,    # Change this number
    max_workers=5      # Or adjust parallel workers
)
```

### Change "Promising" Filter Criteria

Edit `deep_analysis.py`, line ~80:

```python
if (data['pnl'] >= 200 and        # Change PnL threshold
    data['win_rate'] >= 0.50 and  # Change win rate
    data['trades'] >= 20 and       # Change min trades
```

---

## 🔍 Monitoring

### View Workflow Status
1. Go to **Actions** tab
2. See runs with ✅ (success) or ❌ (failed)
3. Click any run to see detailed logs

### Check Data Growth
```python
# In Colab or locally
import json

with open('traders_quick.json', 'r') as f:
    quick = json.load(f)

with open('traders_detailed.json', 'r') as f:
    detailed = json.load(f)

print(f"Quick scan: {len(quick)} traders")
print(f"Detailed: {len(detailed)} traders")
```

---

## 🐛 Troubleshooting

### "No traders in database after running"
- Check **Actions** tab for errors
- Ensure permissions are enabled in Settings
- Try manual run to see logs

### "API rate limit errors"
- Reduce `max_workers` from 5 to 3 in `quick_scan.py`
- Increase `time.sleep()` values

### "Deep analysis finds no promising traders"
- Run quick scan first (needs traders in database)
- Lower filter thresholds in `deep_analysis.py`

### "Workflow not running on schedule"
- GitHub Actions can be delayed ~15-30 minutes
- Check if workflows are enabled in Actions tab

---

## 📈 Advanced: Custom Filtering

After collecting data, create custom filters:

```python
import json
import pandas as pd

# Load detailed data
with open('traders_detailed.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data.values())

# Example: Contrarian crypto traders
contrarians = df[
    (df['main_category'] == 'Crypto') &
    (df['badges'].str.contains('Contrarian', na=False)) &
    (df['win_rate'] > 0.55) &
    (df['avg_bet'].between(200, 2000))
]

# Example: High-volume politics traders
politics = df[
    (df['main_category'] == 'Politics') &
    (df['volume'] > 50000) &
    (df['win_rate'] > 0.60) &
    (~df['badges'].str.contains('Whale', na=False))
]

# Export
contrarians.to_csv('crypto_contrarians.csv', index=False)
politics.to_csv('politics_highvolume.csv', index=False)
```

---

## 🎯 Next Steps

1. ✅ **Set up repository** (follow steps above)
2. ⏰ **Wait 3 days** for data collection
3. 📥 **Download data** and explore
4. 🎨 **Create custom filters** for your strategy
5. 📊 **Track favorite traders** over time

---

## 💡 Pro Tips

- **First week:** Let it run and collect data
- **After 1 week:** Start filtering for specialists
- **After 2 weeks:** Track historical performance
- **Weekly backup:** Download JSON files as backup
- **Adjust filters:** Refine "promising" criteria based on results

---

## 📧 Support

Open an issue in your repository if you encounter problems!

Happy hunting! 🚀
