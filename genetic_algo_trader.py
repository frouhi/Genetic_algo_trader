import csv
import random
import numpy
'''
tools used:
    1. genetic algorithms
    2. binary decision tree
    3. stochastic simulation
    4. random number generator
the goal is:
    1. detect patterns and predict via them
    2. use stochastic simulation to find optimal probabilities in relation to price changes

for this file:
tools used:
    1. genetic algorithms
    2. binary decision tree
the goal is:
    1. detect patterns and predict via them

ideas:
    1. use more than one time intervals
    2. categorise based on previous prices
'''
#stat = ["extreme_drop","drop","neutral","increase","extreme_increase"]
values = [-2, -1, 1, 2]
# intervals = ["klines_15m","klines_1h","klines_6h"]
# interval_counts = [50,20,10]# was 90,50,10
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

'''def length(tree):
    if tree.value in ["buy", "sell"]:
        return 1
    return 1 + length(tree.left) + length(tree.right)'''


def tree2list(tree):
    if tree is None:
        return []
    return [tree]+tree2list(tree.left)+tree2list(tree.right)


def tree2list_leafless(tree):
    if tree.value in ["buy", "sell"]:
        return []
    return [tree]+tree2list_leafless(tree.left)+tree2list_leafless(tree.right)


# swap two random subtrees
def crossover(tree1,tree2):
    ls1 = tree2list(tree1)
    ls2 = tree2list(tree2)
    rnd_indx1 = random.randrange(0,len(ls1))
    rnd_indx2 = random.randrange(0,len(ls2))
    temp = ls1[rnd_indx1]
    if rnd_indx1 == 0:
        tree1 = ls2[rnd_indx2]
    elif ls1[rnd_indx1-1].left == temp:
        ls1[rnd_indx1 - 1].left = ls2[rnd_indx2]
    else:
        ls1[rnd_indx1 - 2].right = ls2[rnd_indx2]
    if rnd_indx2 == 0:
        tree2 = temp
    elif ls2[rnd_indx2-1].left == ls2[rnd_indx2]:
        ls2[rnd_indx2 - 1].left = temp
    else:
        ls2[rnd_indx2 - 2].right = temp
    return [tree1,tree2]


def mutation(tree):
    ls = tree2list_leafless(tree)
    rnd_indx = random.randrange(0,len(ls))
    [new_left,new_right] = crossover(ls[rnd_indx].left,ls[rnd_indx].right)
    ls[rnd_indx].left = new_left
    ls[rnd_indx].right = new_right


#TODO: recursive and not very efficient !! => improve
def cleanup_helper(subtree,value,tree,parent,direction):
    if tree.value in ["buy","sell"]:
        return
    if value == tree.value:
        if direction == "left":
            parent.left = (tree.left if subtree=="left" else tree.right)
            cleanup_helper(subtree,value,parent.left,parent,"left")
        else:
            parent.right = (tree.left if subtree=="left" else tree.right)
            cleanup_helper(subtree,value,parent.right,parent,"right")
    else:
        cleanup_helper(subtree,value,tree.left,tree,"left")
        cleanup_helper(subtree,value,tree.right,tree,"right")


def cleanup(tree):
    if tree.value in ["buy","sell"]:
        return
    cleanup_helper("left", tree.value, tree.left, tree, "left")
    cleanup_helper("right", tree.value, tree.right, tree, "right")
    cleanup(tree.left)
    cleanup(tree.right)




# def generate_random_tree(depth,ls):
#     if depth == 0:
#         return Tree(["buy","sell"][random.randrange(0,2)],0,0)
#     value = values[random.randrange(0,len(values))]
#     interval_idx = random.randrange(0,len(intervals))
#     interval = intervals[interval_idx]
#     index = random.randrange(0,interval_counts[interval_idx])
#     while [value,interval,index] in ls:
#         #print([value,interval,index])
#         #print(str([value,interval,index])+">>"+str(ls))
#         interval_idx = random.randrange(0, len(intervals))
#         value = values[random.randrange(0, len(values))]
#         interval = intervals[interval_idx]
#         index = random.randrange(0, interval_counts[interval_idx])
#     ls += [[value,interval,index]]
#     return Tree(value,interval,index,generate_random_tree(depth-1,ls),generate_random_tree(depth-1,ls))
############## alternative generate_random_tree #####
def generate_random_tree(depth):
    permutations = []
    for a in values:
        for i, b in enumerate(intervals):
            for c in range(0, interval_counts[i]):
                permutations += [[a, b, c]]
    return generate_random_tree_helper(depth,permutations)
def generate_random_tree_helper(depth,permutations):
    if depth == 0:
        return Tree(["buy","sell"][random.randrange(0,2)],0,0)
    length = len(permutations)
    rnd = random.randrange(0,length)
    node = permutations[rnd]
    del(permutations[rnd])
    #TODO: experiment with the following two versions. Note that for the secons one we should make the state space smaller
    # return Tree(node[0],node[1],node[2],generate_random_tree_helper(depth-1,permutations),generate_random_tree_helper(depth-1,permutations))
    return Tree(node[0], node[1], node[2], generate_random_tree_helper(depth - 1, permutations),
                generate_random_tree_helper(depth - 1, permutations.copy()))


def generate_random_population(count,depth):
    population = []
    for i in range(0,count):
        population += [generate_random_tree(depth)]
    return population

# this function selects best fitting trees of the population with roulette wheel selection
# def selection(fitness):
#     for key in fitness.keys():
#         val = fitness[key]
#         #TODO: Experiment with removing negatives or just doing nothing to them
#         if val<=0:
#             val = val-100
#         val += 300
#         fitness[key] = val
#     sum_val = sum(fitness.values())
#     for key in fitness.keys():
#         fitness[key] = fitness[key]/sum_val
#     return list(numpy.random.choice(list(fitness.keys()), selected_population_size, False, list(fitness.values())))
def selection(fitness):
    ls = list(fitness.values())
    ls = sorted(ls)[-selected_population_size:]
    result = []
    for key in fitness.keys():
        if fitness[key] in ls:
            result += [key]
    return result

total_population_size = 100
selected_population_size = 10
population = generate_random_population(total_population_size, 9)
data = {}
last = {}
length = {}
intervals_map = {}
for i,interval in enumerate(intervals):
    with open(interval+".csv","r") as file:
        reader = csv.reader(file)
        data[interval] = list(reader)
    length[interval] = len(data[interval])
    last[interval] = 0
    intervals_map[interval] = interval_counts[i]

with open("evaluation_data.csv","r") as file:
    reader = csv.reader(file)
    evaluation_data = list(reader)
max_fitness = 0
best_tree = None
iteration_num = 0


while True:
    fitness = {}
    for tree in population:
        #print(print_tree(tree))
        training_lists = {}
        for key in data.keys():
            training_lists[key] = []
            last[key] = 0
        fitness[tree] = 0
        # index = 25*12
        index = 0
        status = "sold"
        buy_price = 0
        evaluation_data_length = len(evaluation_data)
        while index<evaluation_data_length:
            for key in data.keys():
                while data[key][last[key]][0] <= evaluation_data[index][0] and last[key]<length[key]:
                    training_lists[key] += [data[key][last[key]][1]]
                    if len(training_lists[key])>intervals_map[key]:
                        del(training_lists[key][0])
                    last[key] += 1
            ############
            too_small = False
            for key in data.keys():
                if last[key]<intervals_map[key]:
                    too_small = True
            if too_small:
                index+=1
                continue
            ############
            action = decision(tree, training_lists)
            #print(status,">>>",action)
            if status == "sold" and action == "buy":
                buy_price = float(evaluation_data[index][1])
                status = "bought"
            elif status == "bought" and action == "sell":
                #TODO: adjust the fees through changing the ratio below
                #fitness[tree] += 0.99*((float(evaluation_data[index][1])-buy_price)/buy_price)
                #fitness[tree] += 0.99 * ((float(evaluation_data[index][1]) - buy_price) / buy_price) * 100
                fitness[tree] += ((((float(evaluation_data[index][1]) - buy_price) / buy_price) * 100) - (
                            0.01 * abs(((float(evaluation_data[index][1]) - buy_price) / buy_price) * 100)))
                status = "sold"
            index += 1
    ############################
    val = max(fitness.values())
    idx = list(fitness.values()).index(val)
    print("iteration: "+str(iteration_num)+"   max_fitness: "+str(val))
    if val>max_fitness:
        max_fitness = val
        best_tree = list(fitness.keys())[idx]
    if best_tree != list(fitness.keys())[idx]:
        print("best tree of this round: ",print_tree(list(fitness.keys())[idx]))
    print("best_val: ",max_fitness,"best_tree: ",print_tree(best_tree))
    iteration_num += 1
    selected_population = selection(fitness)

    # ls = []
    # for l in selected_population:
    #     ls += [fitness[l]]
    # print(">> ",str(ls))

    population = selected_population.copy()
    while len(population)<total_population_size:
        genetic_operation = random.randrange(0,2)
        if genetic_operation == 0:
            i1 = random.randrange(0,selected_population_size)
            i2 = random.randrange(0,selected_population_size)
            while i1 == i2:
                i2 = random.randrange(0, selected_population_size)
            copy1 = selected_population[i1].__copy__()
            copy2 = selected_population[i2].__copy__()
            population += crossover(copy1,copy2) # to role back cleanup, uncomment this line and comment next ones-preloop
            # [copy1,copy2] = crossover(copy1,copy2)
            # cleanup(copy1)
            # cleanup(copy2)
            # population += [copy1,copy2]
        else:
            i = random.randrange(0, selected_population_size)
            copy = selected_population[i].__copy__()
            mutation(copy)
            # cleanup(copy) # cleanup step. Can ignore for testing stages
            population += [copy]
