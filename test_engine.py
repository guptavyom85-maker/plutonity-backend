# test_engine.py
from app.engine.backtest import run_full_backtest

# A simple moving average crossover strategy
# This is what a user would submit
TEST_STRATEGY = """
def generate_signals(df):
    # Calculate 20-day and 50-day moving averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    # Default: hold
    df['signal'] = 0
    
    # Buy when short MA crosses above long MA
    df.loc[df['MA20'] > df['MA50'], 'signal'] = 1
    
    # Sell when short MA crosses below long MA
    df.loc[df['MA20'] < df['MA50'], 'signal'] = -1
    
    return df
"""

result = run_full_backtest(
    code=TEST_STRATEGY,
    ticker="RELIANCE",
    start_date="2015-01-01",
    end_date="2024-01-01",
    initial_capital=100000
)

if result["status"] == "completed":
    print("\n✅ Backtest completed successfully!")
    print("\n📊 METRICS:")
    for key, value in result["metrics"].items():
        print(f"  {key}: {value}")
    print(f"\n📈 Total trades executed: {len(result['trades'])}")
    print("\nFirst 3 trades:")
    for trade in result["trades"][:3]:
        print(f"  {trade}")
else:
    print(f"\n❌ Backtest failed: {result['error']}")