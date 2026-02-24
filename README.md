# Pairs Trade
This is my first attempt at a 'pairs trading' regime that uses a simple mean reversion strategy generate gains on two stocks.  
For this project, I used Coke (KO) and Pepsi (PEP) stocks compare the traditional mean reversion strategy which uses Bollinger bands v. my approach which uses the standard deviation of the standard deviation (the volatility of the volatility) to compare PnL over 2024 and 2025.  
In essence, I want to see if my strategy meets or exceeds the typical approach used for mean reversion (when the relationship exceeds the standard devation * k-value).

**(pairstrade.py)**: The project itself is contained within this file. At now includes some deprecated code once I saved the data down locally so I didn't need to request access to the API each time I ran the program.  
**(oos_pairstrade_202X)**: These files are the out of sample tests which include both 2024 and 2025 datasets.  
**(.csv)**: These files contain the datasets marked by year.  
**(SAVE)**: The SAVE files are the scripts I ran to save the data locally. (I like saving these for clarity in documentation).

Setting up the BBG API was no easy feat given the BBG's notorious lack of documentation on their product. It requires a lot of initial investment before seeing dividends (no pun intended).  
BBG likes to use the 'polars' dataframe package which fortunately is highly compatible with basically every Python package. It does carry some nuance, which involved me needing to convert the dataset from 'vertical' to 'horizontal' formatting and learning the functions for mutating the dataframe.  
All in all, polars is pretty straight forward and easy to follow. Most mutate functions are named clearly (IE rolling_mean is the rolling mean function) which was very helpful.  

Most of the grunt work is done in the **pairtrading.py** file which reformats and mutates the data to run the mean reversion. 
I create 2 functions:  
**run_strategy_deviation** which uses the deviation of the deviation to signal when a trade should be made and  
**run_strategy_bollinger** which uses the more typical Bollinger band approach to calculate when a trade should be made.  

Final output can be seen for both 2024 and 2025.  
2024 PnL was very low. The relationship blew up in June of 2024 and both strategies were barely able to claw back a ~2-3% total PnL.  
2025 PnL was very different. The deviation strategy paid dividends which ended the year at ~12% total return, where the traditional Bollinger approach failed to capture the relationship and returned approximately -2% PnL.  

My main constraints in this work include my approach of using fixed start + end points for each test.  

In theory, I think it would be better to use a joined/combined dataset or better rolling window approaches. In both 2024 and 2025, my trading strategies don't start until ~June of each year, which effectively limits my opportunity to create gains by 50%.  
Even though my deviation strategy performed **BETTER** despite starting **LATER** than the Bollinger strategy, (this is because it uses the deviation of the deviation which is calculated after the initial devation) it still limits my PnL potential to the second half of the year.  

The other constraint includes cointegration testing. In theory, I believe I should only be making these trades when the stocks are moving together. Testing for cointegration before trading would likely have saved both strategies from the large drawdowns that occured in June 2024.  

Moving forward for pairstradev2.0, my goal is to incorporate some of these critiques to extend the gains that I would have made in both years.  

File/Folder,Description
pairstrade.py,"Core logic, data mutation, and strategy execution."
oos_pairstrade_202X,Out-of-sample testing scripts for 2024 and 2025.
data/*.csv,Historical datasets partitioned by year.
SAVE_scripts/,Utility scripts used to fetch and local-cache Bloomberg API data.

