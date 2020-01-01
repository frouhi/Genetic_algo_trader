import csv
import pickle
'''
This script tests the generated
'''
values = [-2, -1, 1, 2]
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
        return ([tree.value,str(tree.time_interval),tree.index,print_tree(tree.left),
                print_tree(tree.right)])

def decision(tree,data):
    if tree.value in ["buy", "sell"]:
        return tree.value
    #TODO: experiment with == and != instead of > and <
    #print(tree.time_interval,tree.index)
    if int(data[tree.time_interval][tree.index]) == tree.value: # >=
        return decision(tree.right,data)
    else:
        return decision(tree.left,data)


# this section reads in the data used in evaluate function.
data = {}
last = {}
length = {}
intervals_map = {}
for i,interval in enumerate(intervals):
    with open("../data/"+interval+"_test.csv","r") as file:
        reader = csv.reader(file)
        data[interval] = list(reader)
    length[interval] = len(data[interval])
    last[interval] = 0
    intervals_map[interval] = interval_counts[i]

with open("../data/evaluation_data_test.csv","r") as file:
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
        too_small = False
        for key in data.keys():
            if last[key] < intervals_map[key]:
                too_small = True
        if too_small:
            index += 1
            continue
        action = decision(tree, training_lists)
        if status == "sold" and action == "buy":
            buy_price = float(evaluation_data[index][1])
            status = "bought"
        elif status == "bought" and action == "sell":
            fitness += ((((float(evaluation_data[index][1]) - buy_price) / buy_price) * 100) - 0.002)
            status = "sold"
        index += 1
    return fitness


def list2tree(ls):
    if ls in ["buy","sell"]:
        return Tree(ls,0,0)
    return Tree(ls[0],ls[1],ls[2],list2tree(ls[3]),list2tree(ls[4]))

with open("../data/best_tree.txt", "rb") as f:   # Unpickling
    tree = list2tree(pickle.load(f))
print("Profit over last month =",evaluate(tree),"%")