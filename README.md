# Pairs Trade
This is my first attempt at a 'pairs trading' regime that uses a simple mean reversion strategy generate gains on two stocks.
For this project, I used Coke (KO) and Pepsi (PEP) stocks to test this strategy. 

The project itself is contained within the **(pairstrade.py)** file. At now includes some deprecated code once I saved the data down locally so I didn't need to request access to the API each time I ran the program.
The **(oos_pairstrade_202X)** are the out of sample tests which include both 2024 and 2025 datasets.
The **(.csv)** datasets are marked by year.
The **(SAVE)** files are the scripts I ran to save the data locally. (I like saving these for clarity in documentation.

At the outset of this project, I was using my API each time I ran the program. 
Setting up the BBG API was no easy feat given the BBG's notorious lack of documentation on their product. It requires a lot of initial investment before seeing dividends (no pun intended).

BBG likes to use the 'polars' dataframe package which fortunately is highly compatible with basically every Python package. It does carry some nuance, which involved me needing to convert the dataset from 'vertical' to 'horizontal' formatting and learning the functions for mutating the dataframe. 
All in all, polars is pretty straight forward and easy to follow. Most mutate functions are named clearly (IE rolling_mean is the rolling mean function) which was very helpful.



