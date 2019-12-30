import csv

values = [-2, -1, 1, 2]
# intervals = ["klines_15m","klines_1h","klines_6h"]
# interval_counts = [50,25,10]
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
    with open("../data/"+interval+".csv","r") as file:
        reader = csv.reader(file)
        data[interval] = list(reader)
    length[interval] = len(data[interval])
    last[interval] = 0
    intervals_map[interval] = interval_counts[i]

with open("../data/evaluation_data.csv","r") as file:
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
            #fitness += 0.99 * ((float(evaluation_data[index][1]) - buy_price) / buy_price) * 100
            fitness += ((((float(evaluation_data[index][1]) - buy_price) / buy_price) * 100) - (0.01*abs( ((float(evaluation_data[index][1]) - buy_price) / buy_price) * 100)))
            status = "sold"
        index += 1
    return fitness

# this section creates all permutatins
initial_permutations = []
node_count = 0
for a in values:
    for i, b in enumerate(intervals):
        for c in range(0, interval_counts[i]):
            initial_permutations += [[a, b, c]]

max_val = 0
def add_node(root,parent,direction,permutations):
    global max_val
    global node_count
    max_tree = None
    max_perm = None
    for perm in permutations:
        for l in ["buy","sell"]:
            for r in ["buy","sell"]:
                tree = Tree(perm[0], perm[1], perm[2], Tree(l, 0, 0), Tree(r, 0, 0))
                if direction == "left":
                    prev_val = parent.left
                    parent.left = tree
                else:
                    prev_val = parent.right
                    parent.right = tree
                val = evaluate(root)
                if val>max_val:
                    max_val = val
                    max_tree = tree
                    max_perm = perm
                if direction == "left":
                    parent.left = prev_val
                else:
                    parent.right = prev_val
    if max_tree is not None:
        node_count += 1
        del(permutations[permutations.index(max_perm)])
        if direction == "left":
            parent.left = max_tree
        else:
            parent.right = max_tree
        print("node count:",node_count,"max value:",max_val,"max tree:",print_tree(root))
    return [max_tree,permutations]


def find_best_root(permutations):
    global max_val
    global node_count
    max_tree = None
    max_perm = None
    for perm in permutations:
        for l in ["buy","sell"]:
            for r in ["buy","sell"]:
                tree = Tree(perm[0], perm[1], perm[2], Tree(l, 0, 0), Tree(r, 0, 0))
                val = evaluate(tree)
                if val>max_val:
                    max_val = val
                    max_tree = tree
                    max_perm = perm
    if max_tree is not None:
        node_count += 1
        del(permutations[permutations.index(max_perm)])
        print("node count:", node_count, "max value:", max_val, "max tree:", print_tree(max_tree))
        return [max_tree,permutations]
    else:
        print("ERROR: TG1")


[root,permutations_root] = find_best_root(initial_permutations)
queue = [[root,permutations_root]]
while queue is not []:
    [poped_node,permutations_root] = queue.pop(0)
    [next_node1, permutations_1] = add_node(root,poped_node,"left",permutations_root.copy())
    [next_node2, permutations_2] = add_node(root, poped_node, "right", permutations_root) # TODO: maybe dont copy for one of them to make it faster
    if next_node1 is not None:
        queue.append([next_node1,permutations_1])
    if next_node2 is not None:
        queue.append([next_node2,permutations_2])
