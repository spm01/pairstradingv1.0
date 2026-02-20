#set up my environment
from polars_bloomberg import BQuery
from datetime import date
import numpy as np
import polars as pl
import altair as alt


import os 
os.chdir("c:/Users/Sean/OneDrive/Desktop/Python/finance")
print(os.getcwd())


#start by grabbing the needed data
bq = BQuery()
with BQuery() as bq:
    df = bq.bdh(
        securities=['KO US EQUITY', 'PEP US EQUITY'],
        fields=['PX_LAST'], 
        start_date=date(2025, 1, 1), 
        end_date=date(2025, 12, 31),
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

#convert to pandas format
df_csv = df_wide.to_pandas()

#save data down into CSV format

#write the file path
file_path = 'KO_PEP_DATA_2025.csv'
df_csv.to_csv(file_path, index=False)

print("Data saved lol")
