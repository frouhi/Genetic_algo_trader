# import cbpro
#
# client = cbpro.PublicClient()
# one_min = client.get_product_historic_rates("BTC-USD",start=,granularity=60)
# five_min = client.get_product_historic_rates("BTC-USD",granularity=300)
# print(len(one_min))
# print(len(five_min))
################################--------####################################
# import csv
# from binance.client import Client
# client = Client("", "")
# klines_15m = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE,"1 month ago UTC")
# klines_1h = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 month ago UTC")
# klines_6h = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_6HOUR, "1 month ago UTC")
# klines_ls = [klines_15m,klines_1h,klines_6h]
# names = ["klines_15m","klines_1h","klines_6h"]
# for n,kline in enumerate(klines_ls):
#     for i,k in enumerate(kline):
#         if i==0:
#             continue
#         pre_delta = float(kline[i - 1][4]) - float(kline[i - 1][1])
#         delta = float(k[4])-float(k[1])
#         if delta>0 and pre_delta<=0:
#             category = 2
#         elif delta>0 and pre_delta>0:
#             category = 1
#         elif delta<=0 and pre_delta<=0:
#             category = -1
#         elif delta<=0 and pre_delta>0:
#             category = -2
#         with open(names[n]+"_test.csv","a")as file:
#             writer = csv.writer(file)
#             writer.writerow([k[6],category])
#
#         if i<3:
#             continue
#         if float(k[5]) > float(kline[i-1][5]) and float(k[5]) > float(kline[i-2][5]) and float(k[5]) > float(kline[i-3][5]):
#             category = 2
#         elif float(k[5]) > float(kline[i-1][5]) and float(k[5]) > float(kline[i-2][5]):
#             category = 1
#         elif float(k[5]) > float(kline[i-1][5]):
#             category = -1
#         else:
#             category = -2
#         with open(names[n]+"_volume_test.csv","a")as file:
#             writer = csv.writer(file)
#             writer.writerow([k[6],category])
#
# for i,k in enumerate(klines_ls[0]):
#     if i>0:
#         with open("evaluation_data_test.csv","a")as file:
#             writer = csv.writer(file)
#             writer.writerow([k[0], k[1]])
################################--------####################################

import csv

values = [-2, -1, 1, 2]
# intervals = ["klines_15m","klines_1h","klines_6h"]
# interval_counts = [90,50,10]
intervals = ["klines_15m","klines_1h","klines_15m_volume","klines_1h_volume"]
interval_counts = [25,10,25,10]

# this is a binary decision tree
class Tree:
    def __init__(self, value, time_interval, index, left=None, right=None):
        self.value = value
        self.time_interval = time_interval
        self.index = index
        self.left = left
        self.right = right
    def __copy__(self):
        if self.value in ["buy","sell"]:
            return Tree(self.value,self.time_interval,self.index)
        return Tree(self.value,self.time_interval,self.index,left=self.left.__copy__(),right=self.right.__copy__())

def print_tree(tree):
    if tree.value in ["buy", "sell"]:
        return str(tree.value)
    else:
        return ("["+str(tree.value)+","+str(tree.time_interval)+","+str(tree.index)+","+print_tree(tree.left)+","+print_tree(tree.right)+"]")
def decision(tree,data):
    if tree.value in ["buy", "sell"]:
        return tree.value
    #TODO: experiment with == and != instead of > and <
    #print(tree.time_interval,tree.index)
    if int(data[tree.time_interval][tree.index]) == tree.value: # >=
        return decision(tree.right,data)
    else:
        return decision(tree.left,data)
#######################################################
# this section reads in the data used in evaluate function.
data = {}
last = {}
length = {}
intervals_map = {}
for i,interval in enumerate(intervals):
    with open(interval+"_test.csv","r") as file:
        reader = csv.reader(file)
        data[interval] = list(reader)
    length[interval] = len(data[interval])
    last[interval] = 0
    intervals_map[interval] = interval_counts[i]

with open("evaluation_data_test.csv","r") as file:
    reader = csv.reader(file)
    evaluation_data = list(reader)
max_fitness = 0
best_tree = None
iteration_num = 0
def evaluate(tree):
    training_lists = {}
    for key in data.keys():
        training_lists[key] = []
        last[key] = 0
    fitness = 0
    # index = 25*12
    index = 0
    status = "sold"
    buy_price = 0
    evaluation_data_length = len(evaluation_data)
    while index < evaluation_data_length:
        for key in data.keys():
            while data[key][last[key]][0] <= evaluation_data[index][0] and last[key] < length[key]:
                training_lists[key] += [data[key][last[key]][1]]
                if len(training_lists[key]) > intervals_map[key]:
                    del (training_lists[key][0])
                last[key] += 1
        ############
        too_small = False
        for key in data.keys():
            if last[key] < intervals_map[key]:
                too_small = True
        if too_small:
            index += 1
            continue
        ############
        action = decision(tree, training_lists)
        # print(status,">>>",action)
        if status == "sold" and action == "buy":
            buy_price = float(evaluation_data[index][1])
            status = "bought"
        elif status == "bought" and action == "sell":
            # TODO: adjust the fees through changing the ratio below
            # fitness[tree] += 0.99*((float(evaluation_data[index][1])-buy_price)/buy_price)
            fitness += ((((float(evaluation_data[index][1]) - buy_price) / buy_price) * 100) - 0.005)
            status = "sold"
        index += 1
    return fitness


def list2tree(ls):
    if ls in ["buy","sell"]:
        return Tree(ls,0,0)
    return Tree(ls[0],ls[1],ls[2],list2tree(ls[3]),list2tree(ls[4]))

buy = "buy"
sell = "sell"
klines_15m = "klines_15m"
klines_1h = "klines_1h"
klines_6h = "klines_6h"
klines_15m_volume = "klines_15m_volume"
klines_1h_volume = "klines_1h_volume"
tree = list2tree([2,klines_1h,9,[1,klines_15m_volume,4,[-2,klines_15m,18,[-2,klines_1h,2,[2,klines_1h_volume,1,[-1,klines_15m,2,[2,klines_15m_volume,15,[1,klines_15m,19,[-1,klines_15m,3,[1,klines_15m,12,[-2,klines_15m_volume,21,buy,sell],[-1,klines_1h_volume,8,[-1,klines_15m,9,[-2,klines_15m_volume,18,[-2,klines_15m_volume,6,buy,[1,klines_15m_volume,2,[-2,klines_15m,22,[2,klines_15m,2,sell,sell],[-1,klines_15m,8,sell,buy]],[-2,klines_15m_volume,1,[1,klines_1h_volume,9,sell,sell],[-1,klines_1h_volume,5,sell,buy]]]],[1,klines_15m_volume,21,[-1,klines_15m,23,[2,klines_15m,23,[-1,klines_15m,9,buy,sell],[1,klines_15m_volume,7,sell,buy]],[-1,klines_15m_volume,17,[-2,klines_1h_volume,4,sell,buy],[-1,klines_15m,13,sell,buy]]],[1,klines_15m,4,[2,klines_15m_volume,19,[-2,klines_15m,5,sell,buy],[-1,klines_15m_volume,7,buy,buy]],[2,klines_15m_volume,11,[1,klines_15m,20,buy,buy],[-1,klines_1h_volume,5,buy,sell]]]]],sell],sell]],[2,klines_15m_volume,7,[2,klines_1h,3,sell,buy],[-1,klines_15m_volume,4,buy,buy]]],[-1,klines_15m,1,sell,buy]],[2,klines_1h_volume,7,[2,klines_1h,5,[-2,klines_15m_volume,1,[2,klines_15m,21,[-2,klines_1h_volume,2,sell,sell],[-2,klines_15m_volume,18,sell,buy]],[1,klines_15m,6,[-1,klines_1h,9,sell,[-2,klines_1h_volume,7,sell,buy]],[-1,klines_15m,0,buy,buy]]],[2,klines_15m_volume,16,[1,klines_15m_volume,5,[-2,klines_15m_volume,17,[1,klines_1h,6,[-2,klines_15m_volume,3,buy,sell],[-2,klines_15m_volume,21,[2,klines_1h,8,[1,klines_15m_volume,2,buy,sell],[2,klines_15m_volume,7,buy,buy]],[-2,klines_15m,12,[-2,klines_15m_volume,4,buy,sell],[2,klines_15m,9,sell,sell]]]],[2,klines_15m,8,[-1,klines_1h,0,sell,[1,klines_15m,15,[1,klines_15m_volume,7,buy,sell],[2,klines_15m,15,buy,sell]]],[2,klines_15m,21,[-2,klines_15m,4,sell,[1,klines_15m,0,buy,sell]],[1,klines_15m_volume,15,[-1,klines_15m_volume,5,[-1,klines_15m_volume,1,[2,klines_15m,0,buy,[-1,klines_1h,7,sell,[-2,klines_1h_volume,7,sell,buy]]],[-2,klines_1h,1,[-2,klines_15m_volume,16,buy,[1,klines_15m_volume,15,[-2,klines_1h,0,sell,buy],[-2,klines_15m,20,sell,sell]]],[-1,klines_15m_volume,9,buy,buy]]],buy],[2,klines_15m_volume,3,sell,sell]]]]],[1,klines_15m,24,sell,sell]],[1,klines_1h_volume,9,[1,klines_1h_volume,1,sell,buy],[2,klines_1h_volume,4,sell,sell]]]],[-2,klines_1h,3,sell,[-1,klines_1h,3,[-2,klines_15m,1,[-1,klines_15m_volume,6,[-1,klines_1h_volume,0,[-1,klines_15m,18,[1,klines_1h,2,buy,[2,klines_15m_volume,6,buy,buy]],sell],[-2,klines_15m_volume,0,[2,klines_15m_volume,14,sell,buy],[1,klines_15m_volume,19,buy,sell]]],[-1,klines_1h,1,[1,klines_15m_volume,22,[1,klines_15m_volume,0,sell,sell],[-1,klines_15m_volume,17,buy,buy]],[2,klines_15m_volume,0,[-1,klines_1h_volume,1,sell,sell],[2,klines_1h,4,buy,buy]]]],[1,klines_15m_volume,11,[1,klines_15m,14,[-2,klines_1h_volume,5,[1,klines_1h_volume,2,sell,sell],[2,klines_15m,10,buy,sell]],[-2,klines_15m,17,[2,klines_15m_volume,8,buy,sell],[-2,klines_15m_volume,0,sell,sell]]],[-1,klines_15m,3,[1,klines_15m,12,[2,klines_15m,0,buy,sell],[-1,klines_1h_volume,8,sell,sell]],[2,klines_15m_volume,7,[2,klines_15m_volume,6,buy,buy],[-1,klines_15m_volume,4,buy,sell]]]]],[-2,klines_15m_volume,18,[-2,klines_15m_volume,6,buy,[1,klines_15m_volume,2,[-2,klines_15m,22,[2,klines_15m,2,sell,sell],[-1,klines_15m,8,sell,buy]],[-2,klines_15m_volume,1,[1,klines_1h_volume,9,sell,sell],[-1,klines_1h_volume,5,sell,buy]]]],[1,klines_15m_volume,21,[-1,klines_15m,23,[2,klines_15m,23,[-1,klines_15m,9,buy,sell],[1,klines_15m_volume,7,sell,buy]],[-1,klines_15m_volume,17,[-2,klines_1h_volume,4,sell,buy],[-1,klines_15m,13,sell,buy]]],[1,klines_15m,4,[2,klines_15m_volume,19,[-2,klines_15m,5,sell,buy],[-1,klines_15m_volume,7,buy,buy]],[2,klines_15m_volume,11,[1,klines_15m,20,buy,buy],[-1,klines_1h_volume,5,buy,sell]]]]]]]]],[1,klines_1h_volume,4,[-1,klines_15m,9,buy,[1,klines_15m,4,[-2,klines_15m_volume,8,[1,klines_15m,15,[2,klines_15m,17,sell,buy],[-1,klines_15m_volume,14,[-2,klines_15m,11,[1,klines_15m,23,sell,sell],[2,klines_15m,7,buy,sell]],sell]],[-2,klines_1h,8,sell,[-1,klines_15m,5,[2,klines_15m_volume,21,sell,buy],buy]]],[1,klines_15m,9,[2,klines_15m_volume,2,[-1,klines_15m_volume,13,buy,sell],[-2,klines_15m_volume,19,buy,sell]],[-2,klines_15m,11,[1,klines_15m,23,sell,sell],[2,klines_15m,7,buy,sell]]]]],[2,klines_15m_volume,20,[2,klines_1h_volume,9,sell,sell],[-1,klines_15m,17,buy,buy]]]],[1,klines_1h_volume,5,[-1,klines_15m,16,[-2,klines_1h,4,[2,klines_15m_volume,2,[-1,klines_15m_volume,13,buy,[-1,klines_15m_volume,4,sell,buy]],[-2,klines_15m_volume,19,buy,sell]],[-1,klines_1h,7,[-1,klines_15m_volume,20,sell,buy],buy]],[-1,klines_15m,20,[2,klines_1h,3,buy,sell],[-1,klines_15m_volume,20,buy,sell]]],[-1,klines_1h,9,[-2,klines_15m_volume,23,[-2,klines_15m_volume,24,buy,sell],[-1,klines_15m_volume,3,[2,klines_15m_volume,6,[-2,klines_15m_volume,7,buy,buy],[2,klines_15m,23,[-1,klines_15m_volume,12,[1,klines_1h_volume,6,sell,buy],[1,klines_15m_volume,16,[-1,klines_15m,22,buy,buy],sell]],[-1,klines_15m,10,[-2,klines_15m,3,sell,buy],[1,klines_1h_volume,0,buy,sell]]]],sell]],[2,klines_1h_volume,5,[-1,klines_15m_volume,16,buy,[-2,klines_15m,22,buy,sell]],sell]]]],[-1,klines_15m_volume,17,[-1,klines_15m_volume,12,[-1,klines_15m_volume,19,[2,klines_15m,15,[2,klines_15m_volume,10,[-2,klines_15m,15,[-2,klines_15m_volume,22,sell,buy],[-1,klines_15m,1,[2,klines_15m,24,[-1,klines_15m,17,[-2,klines_15m_volume,17,[1,klines_1h,6,[2,klines_1h,2,[2,klines_15m,24,buy,[1,klines_15m_volume,12,sell,buy]],[1,klines_1h,7,[2,klines_15m_volume,14,sell,buy],[1,klines_15m,21,[-2,klines_1h_volume,5,[1,klines_1h,6,[-1,klines_15m_volume,19,[-2,klines_15m_volume,0,[1,klines_15m,3,[-1,klines_15m_volume,12,sell,sell],[1,klines_1h_volume,5,buy,buy]],[2,klines_15m,13,[2,klines_15m_volume,12,sell,sell],[-1,klines_15m_volume,18,buy,sell]]],[-2,klines_15m,13,[1,klines_15m,2,[-1,klines_15m_volume,4,buy,sell],[-2,klines_15m_volume,21,buy,sell]],[-1,klines_15m,14,[-1,klines_1h_volume,5,sell,sell],[2,klines_1h_volume,2,sell,sell]]]],[1,klines_15m,4,[-2,klines_15m_volume,8,[1,klines_15m,15,[2,klines_15m,17,sell,buy],[-1,klines_15m_volume,14,sell,sell]],[-2,klines_1h,8,[2,klines_15m_volume,0,buy,sell],[-1,klines_15m,5,buy,buy]]],[1,klines_15m,9,[2,klines_15m_volume,2,[-1,klines_15m_volume,13,buy,sell],[-2,klines_15m_volume,19,buy,sell]],[-2,klines_15m,11,[1,klines_15m,23,sell,sell],[2,klines_15m,7,buy,sell]]]]],[2,klines_1h,2,[1,klines_15m_volume,15,[-1,klines_15m_volume,4,[1,klines_1h,1,[-2,klines_15m_volume,22,buy,sell],[-2,klines_1h,4,buy,sell]],[-1,klines_1h,9,[1,klines_15m_volume,12,sell,[2,klines_15m_volume,10,[-2,klines_15m,15,[-2,klines_15m_volume,22,[-1,klines_15m,22,buy,[-2,klines_15m,21,buy,buy]],buy],[-1,klines_15m,1,buy,sell]],[-1,klines_15m,8,[-2,klines_1h_volume,3,sell,buy],[2,klines_15m_volume,2,sell,buy]]]],[-2,klines_15m_volume,24,buy,sell]]],[-1,klines_15m,3,[-2,klines_15m_volume,13,[1,klines_15m_volume,14,sell,buy],[2,klines_15m,6,sell,sell]],[-1,klines_15m,9,[1,klines_15m,1,buy,buy],[-1,klines_1h_volume,1,sell,buy]]]],[-2,klines_1h_volume,1,[1,klines_1h_volume,2,[-1,klines_1h,9,[1,klines_15m_volume,7,buy,sell],[-1,klines_15m,0,buy,sell]],[-1,klines_15m,3,[2,klines_1h_volume,9,buy,buy],[-2,klines_1h_volume,7,sell,buy]]],[1,klines_15m,5,[-2,klines_1h_volume,9,[-2,klines_15m_volume,10,sell,sell],[-2,klines_15m_volume,3,sell,buy]],[1,klines_15m_volume,0,[2,klines_15m_volume,2,buy,sell],[-2,klines_15m_volume,23,buy,buy]]]]]],sell]]],[-2,klines_15m_volume,21,[2,klines_1h,8,[1,klines_15m_volume,2,sell,buy],[2,klines_15m_volume,7,buy,buy]],[-2,klines_15m,12,[-2,klines_15m_volume,4,sell,sell],[2,klines_15m,9,buy,sell]]]],[2,klines_15m,8,[-1,klines_1h,0,sell,[1,klines_15m,15,[1,klines_15m_volume,7,buy,sell],[2,klines_15m,15,buy,sell]]],[2,klines_15m,21,[-2,klines_15m_volume,0,[1,klines_15m,3,[-1,klines_15m_volume,12,sell,buy],[1,klines_1h_volume,5,sell,buy]],[2,klines_15m,13,[2,klines_15m_volume,12,sell,sell],[-1,klines_15m_volume,18,buy,sell]]],[1,klines_15m_volume,15,[-1,klines_15m_volume,5,[-1,klines_15m_volume,1,[2,klines_15m,0,buy,[-1,klines_1h,7,sell,[-2,klines_1h_volume,7,sell,buy]]],[-2,klines_1h,1,[-2,klines_15m_volume,16,buy,[1,klines_15m_volume,15,[-2,klines_1h,0,sell,buy],[-2,klines_15m,20,sell,[-1,klines_15m,13,[-1,klines_1h,8,[-2,klines_1h_volume,8,[2,klines_1h,6,[-1,klines_15m_volume,12,sell,buy],[1,klines_15m,24,sell,buy]],[-2,klines_15m_volume,5,sell,[2,klines_1h,3,buy,sell]]],[-1,klines_15m_volume,14,[1,klines_15m,18,sell,sell],[1,klines_15m,2,[-1,klines_1h,6,sell,[2,klines_15m_volume,12,[-1,klines_1h,7,buy,sell],[1,klines_15m,21,buy,sell]]],[-2,klines_1h,0,buy,buy]]]],[1,klines_15m_volume,6,[1,klines_15m,6,[2,klines_15m,9,[-1,klines_1h,6,sell,sell],[-2,klines_1h,7,buy,sell]],[-1,klines_15m_volume,20,sell,[1,klines_1h_volume,2,sell,sell]]],[-2,klines_1h_volume,5,[-1,klines_15m_volume,13,buy,sell],[-2,klines_15m_volume,4,[-2,klines_1h,1,sell,buy],[2,klines_15m_volume,21,sell,buy]]]]]]]],[-1,klines_15m_volume,9,buy,buy]]],buy],[2,klines_15m_volume,3,sell,sell]]]]],buy],[1,klines_15m_volume,12,sell,buy]],sell]],[-1,klines_15m,8,[-2,klines_1h_volume,3,sell,buy],[2,klines_15m_volume,2,sell,buy]]],[2,klines_15m_volume,21,[1,klines_15m_volume,19,sell,buy],sell]],[-2,klines_15m,13,[-1,klines_1h,7,buy,sell],[-2,klines_15m_volume,1,sell,buy]]],[-2,klines_1h_volume,9,[-2,klines_1h,5,[2,klines_15m,18,sell,sell],[-2,klines_15m_volume,12,sell,sell]],[-2,klines_15m,3,[1,klines_15m_volume,5,[-1,klines_15m,15,[-1,klines_15m_volume,0,buy,sell],[-1,klines_15m_volume,22,buy,buy]],buy],[2,klines_15m_volume,22,sell,sell]]]],[-1,klines_1h,0,[-1,klines_15m_volume,5,[1,klines_15m,20,[-1,klines_15m,22,buy,sell],[1,klines_1h_volume,8,sell,buy]],[1,klines_15m,10,[-1,klines_15m,20,buy,sell],[1,klines_15m,9,buy,[2,klines_15m_volume,7,[-1,klines_15m_volume,1,[-2,klines_15m,19,sell,sell],[1,klines_1h,2,buy,buy]],[1,klines_15m_volume,5,[-2,klines_15m,22,buy,buy],[2,klines_15m,10,sell,sell]]]]]],[-2,klines_15m_volume,16,[-2,klines_15m_volume,13,[2,klines_1h_volume,9,buy,sell],[-1,klines_15m_volume,9,buy,buy]],[-1,klines_1h_volume,7,[-2,klines_15m_volume,7,buy,buy],[2,klines_15m,20,sell,buy]]]]]],[2,klines_15m,11,[2,klines_15m,12,[1,klines_15m,4,[-2,klines_15m_volume,8,[1,klines_15m,15,[2,klines_15m,17,buy,sell],[-1,klines_15m_volume,14,sell,sell]],[-2,klines_1h,8,[-1,klines_15m,5,[-2,klines_15m_volume,2,[-1,klines_1h,3,[-2,klines_15m,1,[-1,klines_15m_volume,6,[-1,klines_1h_volume,0,[-1,klines_15m,18,[1,klines_1h,2,buy,[2,klines_15m_volume,6,buy,buy]],sell],[-2,klines_15m_volume,0,[2,klines_15m_volume,14,sell,sell],[1,klines_15m_volume,19,buy,sell]]],[-1,klines_1h,1,[1,klines_15m_volume,22,[1,klines_15m_volume,0,sell,sell],[-1,klines_15m_volume,17,buy,buy]],[2,klines_15m_volume,0,[-1,klines_1h_volume,1,sell,sell],[2,klines_1h,4,buy,buy]]]],[1,klines_15m_volume,11,[1,klines_15m,14,[-2,klines_1h_volume,5,[1,klines_1h_volume,2,sell,sell],[2,klines_15m,10,buy,sell]],[-2,klines_15m,17,[2,klines_15m_volume,8,buy,sell],[-2,klines_15m_volume,0,sell,sell]]],[-1,klines_15m,3,[1,klines_15m,12,[2,klines_15m,0,buy,sell],[-1,klines_1h_volume,8,sell,sell]],[2,klines_15m_volume,7,[2,klines_15m_volume,6,buy,buy],[-1,klines_15m_volume,4,buy,sell]]]]],[-2,klines_15m_volume,18,[-2,klines_15m_volume,6,buy,[1,klines_15m_volume,2,[-2,klines_15m,22,[2,klines_15m,2,sell,sell],[-1,klines_15m,8,sell,buy]],[-2,klines_15m_volume,1,[1,klines_1h_volume,9,sell,sell],[-1,klines_1h_volume,5,sell,buy]]]],[1,klines_15m_volume,21,[-1,klines_15m,23,[2,klines_15m,23,[-1,klines_15m,9,buy,sell],[1,klines_15m_volume,7,sell,buy]],[-1,klines_15m_volume,17,[-2,klines_1h_volume,4,sell,buy],[-1,klines_15m,13,sell,buy]]],[1,klines_15m,4,[2,klines_15m_volume,19,[-2,klines_15m,5,sell,buy],[-1,klines_15m_volume,7,buy,buy]],[2,klines_15m_volume,11,[1,klines_15m,20,buy,buy],[-1,klines_1h_volume,5,buy,sell]]]]]],[-2,klines_1h_volume,5,[1,klines_1h,6,[-1,klines_15m_volume,19,[-2,klines_15m_volume,0,[1,klines_15m,3,[-1,klines_15m_volume,12,sell,buy],[1,klines_1h_volume,5,buy,buy]],[2,klines_15m,13,[2,klines_15m_volume,12,sell,sell],[-1,klines_15m_volume,18,sell,buy]]],[-2,klines_15m,13,[1,klines_15m,2,[-1,klines_15m_volume,4,buy,sell],[-2,klines_15m_volume,21,sell,sell]],[-1,klines_15m,14,[-1,klines_1h_volume,5,buy,sell],[2,klines_1h_volume,2,sell,sell]]]],[1,klines_15m,4,[-2,klines_15m_volume,8,[1,klines_15m,15,[2,klines_15m,17,buy,sell],[-1,klines_15m_volume,14,sell,sell]],[-2,klines_1h,8,[-1,klines_15m,5,buy,buy],[2,klines_15m_volume,0,buy,sell]]],[1,klines_15m,9,[2,klines_15m_volume,2,[-1,klines_15m_volume,13,buy,sell],[-2,klines_15m_volume,19,buy,sell]],[-2,klines_15m,11,[1,klines_15m,23,sell,sell],[2,klines_15m,7,sell,buy]]]]],[2,klines_1h,2,[1,klines_15m_volume,15,[-1,klines_15m_volume,4,[1,klines_1h,1,[-2,klines_15m_volume,22,buy,sell],[-2,klines_1h,4,buy,sell]],[-1,klines_1h,9,[1,klines_15m_volume,12,sell,buy],[-2,klines_15m_volume,24,buy,sell]]],[-1,klines_15m,3,[-2,klines_15m_volume,13,[1,klines_15m_volume,14,sell,buy],[2,klines_15m,6,sell,sell]],[-1,klines_15m,9,[1,klines_15m,1,buy,buy],[-1,klines_1h_volume,1,sell,buy]]]],[-2,klines_1h_volume,1,[1,klines_1h_volume,2,buy,[-1,klines_15m,3,[2,klines_1h_volume,9,buy,buy],[-2,klines_1h_volume,7,sell,buy]]],[1,klines_15m,5,buy,[1,klines_15m_volume,0,[2,klines_15m_volume,2,buy,sell],[-2,klines_15m_volume,23,buy,buy]]]]]]],buy],[2,klines_15m_volume,0,buy,buy]]],[1,klines_15m,9,[2,klines_15m_volume,2,[-1,klines_15m_volume,13,buy,sell],[-2,klines_15m_volume,19,buy,[-2,klines_15m,13,[-1,klines_1h,7,buy,sell],[-2,klines_15m_volume,1,sell,buy]]]],[-2,klines_15m,11,[1,klines_15m,23,sell,sell],[2,klines_15m,7,sell,buy]]]],[1,klines_1h_volume,0,[2,klines_15m_volume,10,[-1,klines_15m,15,[-1,klines_15m_volume,0,sell,buy],[-1,klines_15m_volume,22,buy,buy]],[2,klines_1h,8,[-2,klines_15m_volume,14,buy,buy],[-2,klines_15m,20,sell,sell]]],[1,klines_15m_volume,5,[-2,klines_1h_volume,5,[2,klines_15m_volume,14,[-1,klines_1h,4,buy,sell],[-2,klines_15m,17,buy,sell]],[-2,klines_15m_volume,4,[-2,klines_1h,1,sell,buy],[2,klines_15m_volume,21,sell,buy]]],[1,klines_15m_volume,22,[2,klines_1h,0,sell,[1,klines_15m_volume,7,sell,sell]],buy]]]],[1,klines_15m,12,sell,[-1,klines_1h,1,[-1,klines_1h_volume,3,[-2,klines_1h_volume,4,[1,klines_15m,18,sell,sell],[2,klines_15m_volume,11,buy,buy]],[-1,klines_15m_volume,17,[-1,klines_15m,5,[2,klines_15m_volume,14,sell,sell],sell],[-2,klines_15m_volume,14,buy,buy]]],[2,klines_1h,4,[-2,klines_15m,5,[2,klines_1h,7,buy,[-2,klines_15m,22,[2,klines_15m,2,sell,sell],[-1,klines_15m,8,[1,klines_15m,23,sell,sell],buy]]],[-2,klines_15m_volume,3,buy,buy]],[-2,klines_15m_volume,18,[-2,klines_15m_volume,10,sell,sell],[1,klines_1h_volume,3,buy,[1,klines_15m,24,sell,sell]]]]]]]],[-2,klines_15m_volume,2,[-1,klines_1h,3,[-2,klines_15m,1,[-1,klines_15m_volume,6,[-1,klines_1h_volume,0,[-1,klines_15m,18,[1,klines_1h,2,buy,sell],[2,klines_15m_volume,6,buy,buy]],[-2,klines_15m_volume,0,[2,klines_15m_volume,14,sell,sell],[1,klines_15m_volume,19,sell,buy]]],[-1,klines_1h,1,[1,klines_15m_volume,22,[1,klines_15m_volume,0,sell,sell],[-1,klines_15m_volume,17,buy,buy]],[2,klines_15m_volume,0,[-1,klines_1h_volume,1,sell,sell],[2,klines_1h,4,buy,buy]]]],[1,klines_15m_volume,11,[1,klines_15m,14,[-2,klines_1h_volume,5,[1,klines_1h_volume,2,sell,sell],[2,klines_15m,10,sell,buy]],[-2,klines_15m,17,[2,klines_15m_volume,8,sell,sell],[-2,klines_15m_volume,0,sell,sell]]],[-1,klines_15m,3,[1,klines_15m,12,[2,klines_15m,0,buy,sell],[-1,klines_1h_volume,8,sell,sell]],[2,klines_15m_volume,7,[2,klines_15m_volume,6,buy,buy],[-1,klines_15m_volume,4,buy,sell]]]]],[-2,klines_15m_volume,18,[-2,klines_15m_volume,6,buy,[1,klines_15m_volume,2,[-2,klines_15m,22,[2,klines_15m,2,sell,sell],[-1,klines_15m,8,sell,buy]],[-2,klines_15m_volume,1,[1,klines_1h_volume,9,sell,sell],[-1,klines_1h_volume,5,sell,buy]]]],[1,klines_15m_volume,21,[-1,klines_15m,23,[2,klines_15m,23,[-1,klines_15m,9,buy,sell],[1,klines_15m_volume,7,buy,sell]],[-1,klines_15m_volume,17,[-2,klines_1h_volume,4,sell,sell],[-1,klines_15m,13,buy,buy]]],[1,klines_15m,4,[2,klines_15m_volume,19,[-2,klines_15m,5,sell,buy],[-1,klines_15m_volume,7,buy,buy]],[2,klines_15m_volume,11,[1,klines_15m,20,buy,buy],[-1,klines_1h_volume,5,buy,sell]]]]]],[-2,klines_1h_volume,5,[1,klines_1h,6,[-1,klines_15m_volume,19,[-2,klines_15m_volume,0,[1,klines_15m,3,[-1,klines_15m_volume,12,sell,buy],[1,klines_1h_volume,5,sell,buy]],[2,klines_15m,13,[2,klines_15m_volume,12,sell,sell],[-1,klines_15m_volume,18,buy,sell]]],[-2,klines_15m,13,[1,klines_15m,2,[-1,klines_15m_volume,4,buy,sell],[-2,klines_15m_volume,21,sell,sell]],[-1,klines_15m,14,[-1,klines_1h_volume,5,buy,sell],[2,klines_1h_volume,2,sell,sell]]]],[1,klines_15m,4,[-2,klines_15m_volume,8,[1,klines_15m,15,[2,klines_15m,17,buy,sell],[-1,klines_15m_volume,14,sell,sell]],[-2,klines_1h,8,[-1,klines_15m,5,buy,buy],[2,klines_15m_volume,0,buy,sell]]],[1,klines_15m,9,[2,klines_15m_volume,2,[-1,klines_15m_volume,13,buy,sell],[-2,klines_15m_volume,19,buy,sell]],[-2,klines_15m,11,[1,klines_15m,23,sell,sell],[2,klines_15m,7,sell,[2,klines_15m_volume,7,[-1,klines_15m_volume,1,[-2,klines_15m,19,sell,sell],[1,klines_1h,2,buy,buy]],[1,klines_15m_volume,5,[-2,klines_15m,22,buy,buy],[2,klines_15m,10,sell,sell]]]]]]]],[2,klines_1h,2,[1,klines_15m_volume,15,[-1,klines_15m_volume,4,[1,klines_1h,1,[-2,klines_15m_volume,22,buy,sell],[-2,klines_1h,4,buy,sell]],[-1,klines_1h,9,[1,klines_15m_volume,12,sell,buy],[-2,klines_15m_volume,24,buy,sell]]],[-1,klines_15m,3,[-2,klines_15m_volume,13,[1,klines_15m_volume,14,sell,buy],[2,klines_15m,6,sell,sell]],[-1,klines_15m,9,[1,klines_15m,1,buy,buy],[-1,klines_1h_volume,1,sell,buy]]]],[-2,klines_1h_volume,1,[1,klines_1h_volume,2,[-1,klines_1h,9,[1,klines_1h_volume,8,[-2,klines_15m,17,[2,klines_15m_volume,18,[-2,klines_15m_volume,13,[2,klines_15m_volume,1,[-1,klines_15m_volume,0,[2,klines_15m_volume,2,buy,buy],buy],[-1,klines_15m_volume,12,[2,klines_15m_volume,6,buy,sell],[2,klines_15m_volume,5,sell,buy]]],[2,klines_15m_volume,7,[-1,klines_15m_volume,1,[-2,klines_15m,19,sell,sell],[1,klines_1h,2,buy,buy]],[1,klines_15m_volume,5,[-2,klines_15m,22,buy,buy],[2,klines_15m,10,sell,sell]]]],[-1,klines_15m_volume,3,[-1,klines_1h,8,[1,klines_1h_volume,7,[-1,klines_15m_volume,11,buy,sell],[1,klines_15m,18,buy,sell]],[2,klines_15m_volume,24,[-2,klines_15m,19,buy,buy],[-2,klines_15m,20,buy,sell]]],[2,klines_15m,23,[2,klines_15m_volume,22,[1,klines_1h,4,buy,buy],[-1,klines_15m,3,sell,sell]],[2,klines_15m,0,[2,klines_15m_volume,2,buy,buy],[-2,klines_15m,4,buy,buy]]]]],[-2,klines_15m_volume,17,[1,klines_1h,6,[-2,klines_15m_volume,3,buy,sell],[-2,klines_15m_volume,21,buy,[-2,klines_15m,12,[-2,klines_15m_volume,4,buy,sell],[2,klines_15m,9,sell,sell]]]],[2,klines_15m,8,[-1,klines_1h,0,sell,[1,klines_15m,15,[1,klines_15m_volume,7,buy,sell],[2,klines_15m,15,buy,sell]]],[2,klines_15m,21,[-2,klines_15m,4,sell,[1,klines_15m,0,buy,sell]],[1,klines_15m_volume,15,[-1,klines_15m_volume,5,[-1,klines_15m_volume,1,[2,klines_15m,0,buy,[-1,klines_1h,7,sell,[-2,klines_1h_volume,7,sell,buy]]],[-2,klines_1h,1,[-2,klines_15m_volume,16,buy,[1,klines_15m_volume,15,[-2,klines_1h,0,sell,buy],[-2,klines_15m,20,sell,sell]]],[-1,klines_15m_volume,9,buy,buy]]],buy],[2,klines_15m_volume,3,sell,sell]]]]]],sell],[-1,klines_15m,0,buy,sell]],[-1,klines_15m,3,[2,klines_1h_volume,9,buy,buy],[-2,klines_1h_volume,7,sell,buy]]],[1,klines_15m,5,buy,[1,klines_15m_volume,0,[2,klines_15m_volume,2,buy,sell],[-2,klines_15m_volume,23,buy,buy]]]]]]]],[-2,klines_15m,6,[-1,klines_15m_volume,19,[-1,klines_15m_volume,7,[2,klines_15m,20,[1,klines_15m_volume,23,[-1,klines_15m_volume,0,buy,sell],[-1,klines_15m_volume,3,[-1,klines_1h_volume,7,buy,[1,klines_1h_volume,0,buy,sell]],[-1,klines_15m,5,buy,[-2,klines_15m,3,sell,[1,klines_1h_volume,5,sell,sell]]]]],[2,klines_15m,5,[1,klines_15m_volume,8,[-1,klines_1h,2,buy,[-2,klines_15m_volume,19,buy,sell]],[-2,klines_15m,2,sell,[1,klines_15m_volume,11,sell,buy]]],[-1,klines_15m,20,[-1,klines_15m_volume,10,sell,[1,klines_1h_volume,5,sell,sell]],[-1,klines_1h,0,[-2,klines_1h_volume,0,buy,buy],[2,klines_15m,23,buy,buy]]]]],[-1,klines_15m_volume,16,[2,klines_15m_volume,22,[2,klines_1h,3,[2,klines_15m_volume,12,[-1,klines_1h,7,buy,[1,klines_15m,21,buy,sell]],sell],[-1,klines_15m,14,sell,[-1,klines_15m_volume,4,buy,sell]]],[2,klines_15m,3,[-1,klines_15m,22,[-1,klines_15m_volume,24,sell,sell],[-2,klines_15m,21,buy,buy]],[2,klines_15m,7,[-2,klines_15m_volume,21,buy,sell],[1,klines_15m_volume,21,sell,buy]]]],[2,klines_15m_volume,6,[-2,klines_15m_volume,7,buy,buy],[2,klines_15m,23,[-1,klines_15m_volume,12,[1,klines_1h_volume,6,sell,buy],[1,klines_15m_volume,16,[-1,klines_15m,22,buy,buy],sell]],[-1,klines_15m,10,[-2,klines_15m,3,sell,buy],[1,klines_1h_volume,0,buy,sell]]]]]],[2,klines_15m_volume,6,[2,klines_15m,11,[2,klines_1h,5,[2,klines_15m,9,[-1,klines_1h,6,sell,sell],[-2,klines_1h,7,buy,sell]],[2,klines_15m_volume,16,[1,klines_15m_volume,5,[2,klines_15m_volume,11,[1,klines_1h_volume,1,[1,klines_1h_volume,4,[1,klines_1h_volume,8,buy,[-1,klines_15m,7,[1,klines_15m,1,buy,buy],[-2,klines_1h,3,sell,buy]]],[2,klines_1h,2,sell,sell]],[1,klines_1h,4,[2,klines_15m_volume,12,buy,sell],[-1,klines_1h,6,buy,sell]]],[-2,klines_15m_volume,5,[-1,klines_15m,5,[-2,klines_1h_volume,7,buy,buy],[-1,klines_15m_volume,4,sell,buy]],[2,klines_1h,7,[1,klines_1h,8,sell,buy],[1,klines_15m_volume,8,sell,sell]]]],[1,klines_15m,24,sell,sell]],[1,klines_1h_volume,9,[1,klines_1h_volume,1,buy,sell],[2,klines_1h_volume,4,sell,sell]]]],[-1,klines_1h_volume,4,[-1,klines_1h,0,buy,[1,klines_15m,16,[-2,klines_15m,10,[2,klines_15m_volume,19,[-2,klines_1h,8,sell,buy],[-2,klines_1h,9,buy,buy]],buy],[1,klines_15m_volume,1,buy,sell]]],[-1,klines_15m,15,buy,[-2,klines_15m_volume,12,[2,klines_15m,12,buy,buy],[2,klines_15m,3,buy,buy]]]]],[-1,klines_15m,13,[-1,klines_1h,8,[-2,klines_1h_volume,8,[2,klines_1h,6,sell,[1,klines_15m,24,sell,buy]],[-2,klines_15m_volume,5,sell,[2,klines_1h,3,buy,sell]]],[-1,klines_15m_volume,14,[1,klines_15m,18,sell,[-2,klines_15m_volume,17,[1,klines_1h,6,[-2,klines_15m_volume,3,buy,sell],[-2,klines_15m_volume,21,[2,klines_1h,8,[1,klines_15m_volume,2,buy,sell],[2,klines_15m_volume,7,buy,buy]],[-2,klines_15m,12,[-2,klines_15m_volume,4,buy,sell],[2,klines_15m,9,sell,sell]]]],[2,klines_15m,8,[-1,klines_1h,0,sell,[1,klines_15m,15,[1,klines_15m_volume,7,buy,sell],[2,klines_15m,15,buy,sell]]],[2,klines_15m,21,[-2,klines_15m,4,sell,[1,klines_15m,0,buy,sell]],[1,klines_15m_volume,15,[-1,klines_15m_volume,5,[-1,klines_15m_volume,1,[2,klines_15m,0,buy,[-1,klines_1h,7,sell,[-2,klines_1h_volume,7,sell,buy]]],[-2,klines_1h,1,[-2,klines_15m_volume,16,buy,[1,klines_15m_volume,15,[-2,klines_1h,0,sell,buy],[-2,klines_15m,20,sell,sell]]],[-1,klines_15m_volume,9,buy,buy]]],buy],[2,klines_15m_volume,3,sell,sell]]]]]],[1,klines_15m,2,[-1,klines_1h,6,sell,[2,klines_15m_volume,12,[-1,klines_1h,7,buy,sell],[1,klines_15m,21,buy,sell]]],[-2,klines_1h,0,buy,buy]]]],[1,klines_15m_volume,6,[1,klines_15m,6,[2,klines_15m,9,[-1,klines_1h,6,sell,sell],[-2,klines_1h,7,buy,sell]],[-1,klines_15m_volume,20,sell,[1,klines_1h_volume,2,sell,sell]]],[-2,klines_1h_volume,5,[-1,klines_15m_volume,13,buy,sell],[-2,klines_15m_volume,4,[-2,klines_1h,1,sell,buy],[2,klines_15m_volume,21,sell,buy]]]]]]],[-1,klines_15m_volume,13,[-2,klines_15m,17,[2,klines_15m_volume,18,[-2,klines_15m_volume,13,[2,klines_15m_volume,1,[-1,klines_15m_volume,0,[1,klines_15m_volume,22,[2,klines_1h,0,sell,buy],[1,klines_15m_volume,7,sell,sell]],buy],[-1,klines_15m_volume,12,[2,klines_15m_volume,6,buy,sell],[2,klines_15m_volume,5,buy,sell]]],[2,klines_15m_volume,7,[-1,klines_15m_volume,1,[-2,klines_15m,19,sell,sell],[1,klines_1h,2,buy,buy]],[1,klines_15m_volume,5,[-2,klines_15m,22,[1,klines_15m_volume,7,sell,sell],buy],[2,klines_15m,10,sell,sell]]]],[-1,klines_15m_volume,3,[-1,klines_1h,8,[1,klines_1h_volume,7,[-1,klines_15m_volume,11,buy,sell],[1,klines_15m,18,sell,buy]],[2,klines_15m_volume,24,[-2,klines_15m,19,buy,buy],[-2,klines_15m,20,buy,sell]]],[2,klines_15m,23,[2,klines_15m_volume,22,[1,klines_1h,4,buy,sell],[-1,klines_15m,3,sell,sell]],[2,klines_15m,0,[2,klines_15m_volume,2,[1,klines_1h,7,[2,klines_15m_volume,14,sell,buy],[1,klines_15m,21,[-2,klines_1h_volume,5,[1,klines_1h,6,[-1,klines_15m_volume,19,[-2,klines_15m_volume,0,[1,klines_15m,3,[-1,klines_15m_volume,12,sell,sell],[1,klines_1h_volume,5,buy,buy]],[2,klines_15m,13,[2,klines_15m_volume,12,sell,sell],[-1,klines_15m_volume,18,buy,sell]]],[-2,klines_15m,13,[1,klines_15m,2,[-1,klines_15m_volume,4,buy,sell],[-2,klines_15m_volume,21,buy,sell]],[-1,klines_15m,14,[-1,klines_1h_volume,5,sell,sell],[2,klines_1h_volume,2,sell,sell]]]],[1,klines_15m,4,[-2,klines_15m_volume,8,[1,klines_15m,15,[2,klines_15m,17,sell,buy],[-1,klines_15m_volume,14,sell,sell]],[-2,klines_1h,8,[2,klines_15m_volume,0,buy,sell],[-1,klines_15m,5,buy,buy]]],[1,klines_15m,9,[2,klines_15m_volume,2,[-1,klines_15m_volume,13,buy,sell],[-2,klines_15m_volume,19,buy,sell]],[-2,klines_15m,11,[1,klines_15m,23,sell,sell],[2,klines_15m,7,buy,sell]]]]],[2,klines_1h,2,[1,klines_15m_volume,15,[-1,klines_15m_volume,4,[1,klines_1h,1,[-2,klines_15m_volume,22,buy,sell],[-2,klines_1h,4,buy,sell]],[-1,klines_1h,9,[1,klines_15m_volume,12,sell,[2,klines_15m_volume,10,[-2,klines_15m,15,[-2,klines_15m_volume,22,[-1,klines_15m,22,buy,[-2,klines_15m,21,buy,buy]],buy],[-1,klines_15m,1,buy,sell]],[-1,klines_15m,8,buy,[2,klines_15m_volume,2,sell,[-2,klines_1h_volume,3,sell,buy]]]]],[-2,klines_15m_volume,24,buy,sell]]],[-1,klines_15m,3,[-2,klines_15m_volume,13,[1,klines_15m_volume,14,sell,buy],[2,klines_15m,6,sell,sell]],[-1,klines_15m,9,[1,klines_15m,1,buy,buy],[-1,klines_1h_volume,1,sell,buy]]]],[-2,klines_1h_volume,1,[1,klines_1h_volume,2,[-1,klines_1h,9,[1,klines_15m_volume,7,buy,sell],[-1,klines_15m,0,buy,sell]],[-1,klines_15m,3,[2,klines_1h_volume,9,buy,buy],[-2,klines_1h_volume,7,sell,buy]]],[1,klines_15m,5,[-2,klines_1h_volume,9,[-2,klines_15m_volume,10,sell,sell],[-2,klines_15m_volume,3,sell,buy]],[1,klines_15m_volume,0,buy,[-2,klines_15m_volume,23,buy,buy]]]]]],sell]],buy],[-2,klines_15m,4,buy,buy]]]]],[-2,klines_15m_volume,17,[1,klines_1h,6,[-2,klines_15m_volume,3,buy,sell],[-2,klines_15m_volume,21,[2,klines_1h,8,[1,klines_15m_volume,2,sell,buy],[2,klines_15m_volume,7,buy,buy]],[-2,klines_15m,12,[-2,klines_15m_volume,4,buy,sell],[2,klines_15m,9,sell,sell]]]],[2,klines_15m,8,[-1,klines_1h,0,sell,[1,klines_15m,15,[1,klines_15m_volume,7,buy,sell],[2,klines_15m,15,buy,sell]]],[2,klines_15m,21,[-2,klines_15m,4,sell,[1,klines_15m,0,buy,sell]],[1,klines_15m_volume,15,[-1,klines_15m_volume,5,[-1,klines_15m_volume,1,[2,klines_15m,0,buy,[-1,klines_1h,7,sell,[-2,klines_1h_volume,7,buy,buy]]],[-2,klines_1h,1,[-2,klines_15m_volume,16,buy,[1,klines_15m_volume,15,[-2,klines_1h,0,sell,sell],[-2,klines_15m,20,sell,sell]]],[-1,klines_15m_volume,9,buy,buy]]],buy],[2,klines_15m_volume,3,sell,sell]]]]]],[-2,klines_15m,16,[-1,klines_15m_volume,16,[1,klines_15m_volume,24,[-2,klines_15m,2,[-2,klines_1h_volume,3,sell,buy],[-2,klines_15m_volume,21,[-2,klines_1h_volume,0,sell,sell],[1,klines_15m_volume,8,buy,buy]]],[1,klines_15m,1,[-1,klines_15m_volume,6,[-1,klines_1h_volume,0,[-1,klines_15m,18,[1,klines_1h,2,buy,[2,klines_15m_volume,6,buy,buy]],sell],[-2,klines_15m_volume,0,[2,klines_15m_volume,14,sell,sell],[1,klines_15m_volume,19,buy,sell]]],[-1,klines_1h,1,[1,klines_15m_volume,22,[1,klines_15m_volume,0,sell,sell],[-1,klines_15m_volume,17,buy,buy]],[2,klines_15m_volume,0,[-1,klines_1h_volume,1,sell,sell],[2,klines_1h,4,buy,buy]]]],[-1,klines_15m_volume,11,[-2,klines_15m_volume,20,sell,buy],[1,klines_1h_volume,6,buy,sell]]]],[2,klines_15m_volume,11,[1,klines_1h_volume,1,[1,klines_1h_volume,4,[1,klines_1h_volume,8,buy,[-1,klines_15m,7,[1,klines_15m,1,buy,[-2,klines_1h,3,sell,buy]],buy]],[2,klines_1h,2,sell,sell]],[1,klines_1h,4,[2,klines_15m_volume,12,sell,sell],[-1,klines_1h,6,buy,sell]]],[-2,klines_15m_volume,5,[-1,klines_15m,5,[-2,klines_1h_volume,7,buy,buy],[-1,klines_15m_volume,4,sell,buy]],[2,klines_1h,7,[1,klines_1h,8,sell,buy],[1,klines_15m_volume,8,sell,buy]]]]],[1,klines_15m,12,buy,[-2,klines_1h_volume,4,[1,klines_15m_volume,1,[-1,klines_1h_volume,4,[-2,klines_1h,5,sell,buy],[1,klines_15m,11,buy,sell]],[-1,klines_15m,18,[-1,klines_15m,9,buy,sell],[-1,klines_1h,2,buy,sell]]],[-1,klines_15m,9,[-2,klines_15m_volume,19,[-1,klines_1h,0,buy,sell],[-1,klines_15m,12,[1,klines_15m_volume,14,sell,buy],sell]],[2,klines_15m,0,[-1,klines_15m,19,sell,sell],[1,klines_1h,4,sell,sell]]]]]]]]])
print(print_tree(tree))
print(evaluate(tree))