#Set up your environment
from polars_bloomberg import BQuery
from datetime import date
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
#print(df_wide)

#create new column for price ratio
#IRL probably want a price spread instead of price ratio
#test price spread of ~(6/17) --> normally probably want rolling price spread
df_price = df_wide.with_columns(
    (pl.col('KO US EQUITY') / pl.col('PEP US EQUITY')).alias('KO / PEP Price Ratio'),
)
#print(df_price)

#create new column to determine 'normal' price ratio
#test with 30day rolling average
df_ratio = df_price.with_columns(
    (pl.col('KO / PEP Price Ratio').rolling_mean(window_size=30).alias('Moving 30 Day Price Ratio Avg'),
    pl.col('date').cast(pl.Date))
)
#print(df_ratio)

#create new column with deviation from avg
df_error = df_ratio.with_columns(
    ((pl.col('Moving 30 Day Price Ratio Avg') - pl.col('KO / PEP Price Ratio')).alias('Deviation'))
)
#print(df_error)

#create new column with absolute value 30 day rolling avg deviation
#using this column to create boundaries for the DAILY price ratio
df_noise = df_error.with_columns(
    (pl.col('Deviation').rolling_mean(window_size=30).abs().alias('Moving 30 Day Deviation Avg'),
    pl.col('date').cast(pl.Date))
)
#print(df_noise)

#create 2 new columns: upper band and lower band
#this is to measure whether price movements are actually substantial or not
df_boundary = df_noise.with_columns(
    ((pl.col('Moving 30 Day Price Ratio Avg') + (pl.col('Moving 30 Day Deviation Avg') * 1.5)).alias('Upper Bound')),
    (((pl.col("Moving 30 Day Price Ratio Avg")) - (pl.col('Moving 30 Day Deviation Avg') * 1.5)).alias('Lower Bound')),
     pl.col('date').cast(pl.Date)
)
print(df_boundary)


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




'''
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
