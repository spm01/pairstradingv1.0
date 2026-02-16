#set up my environment
from polars_bloomberg import BQuery
from datetime import date
import numpy as np
import polars as pl
import altair as alt
alt.renderers.enable('browser')

#start by grabbing the needed data
bq = BQuery()
with BQuery() as bq:
    df = bq.bdh(
        securities=['KO US EQUITY', 'PEP US EQUITY'],
        fields=['PX_LAST'], 
        start_date=date(2023, 1, 1), 
        end_date=date(2023, 12, 31),
    )

#reorganize the data frame from 'vertical' to 'horizontal'
df_wide = (
    df.pivot(
        values='PX_LAST',
        index = 'date',
        on = 'security',
        aggregate_function='first'
    )
    .sort('date')
)
print(df_wide)

def run_strategy(df_wide, window, k_mult):

    #create new column for price ratio
    #IRL probably want a price spread instead of price ratio
    #test price spread of ~(6/17) --> normally probably want rolling price spread
    #fractional changes make huge difference in performance (desmos graphic calc had ~0.01 difference with giant misses)
    df_price = df_wide.with_columns(
    (pl.col('KO US EQUITY') / pl.col('PEP US EQUITY')).alias('KO / PEP Price Ratio'))
    #print(df_price)

    #create new column to determine 'normal' price ratio
    #test with 30day rolling average
    df_ratio = df_price.with_columns(
        (pl.col('KO / PEP Price Ratio').rolling_mean(window_size=window).alias('Moving 30 Day Price Ratio Avg'),
        pl.col('date').cast(pl.Date)))
    #print(df_ratio)

    #create new column with deviation from avg
    df_error = df_ratio.with_columns(
        ((pl.col('Moving 30 Day Price Ratio Avg') - pl.col('KO / PEP Price Ratio')).alias('Deviation')))
    #print(df_error)

    #create new column with absolute value 30 day rolling std deviation
    #using this column to create boundaries for the DAILY price ratio
    df_noise = df_error.with_columns(
        (pl.col('Deviation').rolling_std(window_size=window).abs().alias('Moving 30 Day Std Deviation'),
        pl.col('date').cast(pl.Date)))
    #print(df_noise)

    #create 2 new columns: upper band and lower band
    #this is to measure whether price movements are actually substantial or not

    df_boundary = df_noise.with_columns(
        ((pl.col('Moving 30 Day Price Ratio Avg') + (pl.col('Moving 30 Day Std Deviation') * k_mult)).alias('Upper Bound')),
        (((pl.col("Moving 30 Day Price Ratio Avg")) - (pl.col('Moving 30 Day Std Deviation') * k_mult)).alias('Lower Bound')),
        pl.col('date').cast(pl.Date))
    #print(df_boundary)
    #typically it would be good to tune the K parameter based on our given target metrics (Sharpe's ratio/drawdowns etc) 

    #define our positions for the trades
    #-1 we short the relationship with the expectation that it will fall back to normal
    #1 we buy the relationship with the hope it will rise back to normal
    df_conditional = df_boundary.with_columns(
        pl.when(pl.col("KO / PEP Price Ratio") > pl.col('Upper Bound')).then(pl.lit(-1))
        .when(pl.col("KO / PEP Price Ratio") < pl.col('Lower Bound')).then(pl.lit(1))
        .otherwise(pl.lit(0))
        .alias("Target Position"))
    #print(df_conditional)

    #computing simulate PnL for 2023
    df_pnl = df_conditional.with_columns(
        (pl.col('KO US EQUITY').pct_change().alias('Ret_KO')),
        (pl.col('PEP US EQUITY').pct_change().alias('Ret_PEP')),
        (pl.col('Target Position').shift(1).alias('Position Held'))
        ).with_columns(
        ((pl.col("Ret_KO") - pl.col('Ret_PEP')) * pl.col('Position Held')).alias('Strategy_Daily_Return')
        ).with_columns(
        pl.col('Strategy_Daily_Return').fill_null(0).cum_sum().alias('Cumulative_PnL')
        ).drop_nulls()

    #df_count = df_pnl.select(pl.col('Position Held').value_counts())
    #print(df_count)
    #with K = 1.5, 1 values = 27, 0 values = 138, -1 values = 27

    #print(df_pnl)
    #print(df_pnl.select(['date', 'KO / PEP Price Ratio', 'Position Held', 'Strategy_Daily_Return', 'Cumulative_PnL']))
    #cumulative PnL is ~4.7% for FY2023
    #total_pnl = df_pnl.select(pl.last('Cumulative_PnL'))
    #print(total_pnl)

    #assume Risk Free Rate is ~4%
    daily_returns = df_pnl['Strategy_Daily_Return']
    rf_annual = 0.04
    rf_daily = (1 + rf_annual) ** (1/252) - 1
    excess_returns = daily_returns - rf_daily

    std = excess_returns.std()
    if std == 0:
        sharpe = 0.0
    else:
        sharpe = excess_returns.mean() / std * (252 ** 0.5)
    #print(sharpe)

    return df_pnl, sharpe

#excluding these lines so they don't fire everytime I run the file   
#result = run_strategy(df_wide, window=30, k_mult=1.5)
#print(result)


from concurrent.futures import ThreadPoolExecutor
import itertools

def evaluate_params(args):
    window, k = args
    try:
        df_result, sharpe_result = run_strategy(df_wide, window = int(window), k_mult=float(k))
        return {
            'window': window,
            'k': k,
            'sharpe': sharpe_result,
            'total_return': df_result['Cumulative_PnL'][-1]
        }
    except Exception as e:
        print(f"Failed for window={window}, k={k}: {e}")
        return {'window': window, 'k':k, 'sharpe': 0.0, 'total_return': 0.0}

potential_windows = np.arange(20, 91, 1)
k_multipliers = np.arange(1.0, 3.1, 0.001)
param_combinations = list(itertools.product(potential_windows, k_multipliers))

if __name__ == '__main__':
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(evaluate_params, param_combinations))
    results_df = pl.DataFrame(results)
    #print(results_df.sort('sharpe', descending=True).head(10))
    #find the best values that deliver the highest sharpes ratio
    best = results_df.sort('sharpe', descending=True).head(1)

    #dont really need to print this everytime, the important part is that I have the numbers
    print(best)

    #extract the values
    best_window = int(best['window'][0])
    best_k = float(best['k'][0])


'''
import numpy as np
potential_windows = np.arange(20, 91, 1)
k_multipliers = np.arange(1.0, 3.1, 0.001)
results = []

for test_window in potential_windows:
    for test_k in k_multipliers:
        df_result, sharpe_result = run_strategy(df_wide, window=int(test_window), k_mult=float(test_k))
        
        results.append({
            'window': test_window,
            'k': test_k,
            'sharpe': sharpe_result,
            'total_return': df_result['Cumulative_PnL'][-1],
        })
results_df = pl.DataFrame(results)
print(results_df.sort('sharpe', descending=True).head(10))
'''


#this is a 'gross sharpe' calculation b/c it doesn't compare rate of return to risk-free rate (~4% of US Treasury Bond)
#sharpe_gross = (daily_returns.mean() / daily_returns.std()) * (252 ** 0.5)
#print(sharpe_gross)

'''
#melt polars to long format for charting
df_long = df_error.unpivot(
    index='date',
    on=[
        'KO / PEP Price Ratio',
        'Moving 30 Day Price Ratio Avg',
        'Deviation'
    ],
    variable_name='Series',
    value_name='Value'
)
#print(df_long)

#chart dataframe for comparison
chart = (
    alt.Chart(df_long.to_pandas())
    .mark_line(strokeWidth=2)
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y('Value:Q', title='Price Ratio'),
        color=alt.Color('Series:N', title="")
    )
    .properties(
        width=800,
        height=400,
        title="KO / PEP Ratio v. 30 Rolling Avg"
    )
)
#chart.show()

#test visual inspection of data
chart = (df_ratio.plot.line(
            x='date', 
            y='Moving 30 Day Price Ratio Avg'
            )
        )
chart.encoding.x.title = 'Date'
chart.encoding.y.title = '30Day Rolling Price Ratio'
chart.show()
'''
