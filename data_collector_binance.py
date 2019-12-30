import csv
from binance.client import Client
'''
This scripts collects financial data that is used by other scripts.
'''
client = Client("", "")
klines_15m = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "10 years ago UTC","1 month ago UTC")
klines_1h = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "10 years ago UTC","1 month ago UTC")
klines_6h = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_6HOUR, "10 years ago UTC","1 month ago UTC")
klines_ls = [klines_15m,klines_1h,klines_6h]
names = ["klines_15m","klines_1h","klines_6h"]
for n,kline in enumerate(klines_ls):
    for i,k in enumerate(kline):
        if i==0:
            continue
        pre_delta = float(kline[i - 1][4]) - float(kline[i - 1][1])
        delta = float(k[4])-float(k[1])
        if delta>0 and pre_delta<=0:
            category = 2
        elif delta>0 and pre_delta>0:
            category = 1
        elif delta<=0 and pre_delta<=0:
            category = -1
        elif delta<=0 and pre_delta>0:
            category = -2
        with open(names[n]+".csv","a")as file:
            writer = csv.writer(file)
            writer.writerow([k[6],category])

        if i<3:
            continue
        if float(k[5]) > float(kline[i-1][5]) and float(k[5]) > float(kline[i-2][5]) and float(k[5]) > float(kline[i-3][5]):
            category = 2
        elif float(k[5]) > float(kline[i-1][5]) and float(k[5]) > float(kline[i-2][5]):
            category = 1
        elif float(k[5]) > float(kline[i-1][5]):
            category = -1
        else:
            category = -2
        with open(names[n]+"_volume.csv","a")as file:
            writer = csv.writer(file)
            writer.writerow([k[6],category])

for i,k in enumerate(klines_ls[0]):
    if i>0:
        with open("evaluation_data.csv","a")as file:
            writer = csv.writer(file)
            writer.writerow([k[0], k[1]])