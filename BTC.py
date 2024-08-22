import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

asset1 = 1000
def trade1(x):
    global asset1
    asset1 = (x["Close"] / x["Open"]) * asset1
    x['Asset1'] = asset1
    return x['Asset1']


asset2 = 1000
def trade2(x):
    global asset2
    asset2 = (x["High"] / x["Open"]) * asset2
    x['Asset2'] = asset2
    return x['Asset2']


df = pd.DataFrame()
try:
    df = pd.read_csv("BTC-USD.csv")
except:
    df = yf.download("BTC-USD", start="2019-01-01", end="2024-08-06")
    df.reset_index(inplace=True)
    if (len(df) == 0):
        print("\nplease check your internet connection!\n")

df["Day Of Week"] = pd.to_datetime(df["Date"]).dt.day_of_week

# saving last day's values
last_day = [df.loc[len(df) - 1, "Date"], df.loc[len(df)-1, "Close"], df.loc[len(df) - 1, "High"]]

# Day Of Week=5 is Saturday  and  Day Of Week=2 is Wednesday
df = df.where((df["Day Of Week"] == 2) | (df["Day Of Week"] == 5)).dropna()
df["Day Of Week"] = df["Day Of Week"].astype("int")
df.index = np.arange(len(df))

df.drop(["Low", "Adj Close", "Volume"], axis=1, inplace=True)

# if the first day of trade is converting Bitcoin to dollar(Wednesday), ignore that day
if df.loc[0, "Day Of Week"] == 2:
    df.drop(df.index[0], axis=0, inplace=True)

# making each sample or row represent a whole week
df["Close"] = df["Close"].shift(-1)
df["High"] = df["High"].shift(-1)
df.drop(df.index[(df["Day Of Week"] == 2)], axis=0, inplace=True)
df.index = np.arange(len(df))

# Adding 2 Asset columns
df["Asset1"] = 0
df["Asset2"] = 0

# if asset is in BTC not dollar on the last day(it's sat, sun, mon or tue)
if np.isnan(df.loc[len(df)-1, "Close"]):
    # Asset should be converted at the last day's Close price or High price
    df.loc[len(df)-1, "Close"] = last_day[1]
    df.loc[len(df)-1, "High"] = last_day[2]

# Trading
df["Asset1"] = df.apply(trade1, 1)
df["Asset2"] = df.apply(trade2, 1)

final_asset1 = df.loc[len(df)-1, "Asset1"].astype("int")
final_asset2 = df.loc[len(df)-1, "Asset2"].astype("int")
print(df[["Date", "Open", "Close", "High", "Asset1", "Asset2"]].round(2))
print("-" * 70, "\nAsset Value on", last_day[0], " :")
print("\t1: (if trade on wednesday was done in Close Price)\t=", final_asset1, "$")
print("\t2: (if trade on wednesday was done in High Price)\t=", final_asset2, "$")

fig = plt.figure(figsize=(9, 5))
plt.plot(pd.to_datetime(df["Date"]), df["Asset1"], color="blue", label="trading in Close Price")
plt.plot(pd.to_datetime(df["Date"]), df["Asset2"], color="purple", label="trading in High Price")
plt.legend()
plt.xlabel("Date")
plt.ylabel("Asset $")
plt.title("Asset changes over time")

# showing last asset values on plot
plt.annotate(final_asset1, xy=(1, final_asset1), xytext=(8, 0),
             xycoords=('axes fraction', 'data'), textcoords='offset points')
plt.annotate(final_asset2, xy=(1, final_asset2), xytext=(8, 0),
             xycoords=('axes fraction', 'data'), textcoords='offset points')
plt.show()
