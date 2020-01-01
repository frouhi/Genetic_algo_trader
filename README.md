## Genetic Algorithm Based Trading System ##

**Author**
* Farhang Rouhi

**Introduction**

This program uses genetic algorithms and binary decision trees to develop a Trading system. The resulting binary decision tree
is capable of detecting patterns in basic price and volume data and make an expert decision about the next optimal action.

**How to Use?**

First run the genetic_algo_trader.py. This program runs the genetic algorithm in a loop and saves the best result in best_tree.txt. 
The training data used by this program excludes latest one month which is used for testing the system. 
To test the trading system over this one month of data, run the test.py. If you want to use the latest data, run the data_collector_binance.py.
Note that you can modify this script to use any other exchange or asset and the other scripts should work without any problem.

**How does it work?**
1.  **Data Collection**
    
    First we collect candle stick data from Binance cryptocurrency exchange. Note that the data can come from any exchange, Binance is an arbitrary choice.
The data is collected for multiple time intervals to give the system a better intuition about the market behaviour. Each collected data point is a 
continues value which means that the state space is infinite and too large. In order to make the state space finite, 
each data point is converted to a discrete value. These values are ["very low","low","high","very high"] enumerated by [-2,-1,1,2].
For simplicity and smaller state space we could also use [-1,1].

2. **Initial Random Population**

    In this step, we create a set of random binary decision trees. Each binary decision tree is a trading system. The non-terminal
    nodes of each tree have index, value and time interval. The leaf nodes are the decision which is "buy" or "sell".
    A very important point is that a node cannot repeat in its own subtree. The reason is that since the same condition is already checked, 
    the same subtree is always chosen. Therefore, repeating the same node can cost a lot of memory and time. However, the same node can repeat in different subtrees.
    
3. **Selection**

    In this step, the fitness of each tree is calculated and a fixed number of trees with highest fitness are selected.
    Another option would be to use roulette wheel selection instead of selecting the highest fitnesses. To find the fitness we 
    use the tree for trading on our training data. fitness is the profit made by that tree. To find the decision for each time, 
    we start from the root and we compare the value of each node and the training value that the node points to. If they are equal we go
     to the right subtree, otherwise we go left. The final node or the leaf node is the decision. However, if the decision is "buy" 
     and we have already bought the asset, no action is taken. Similarly, if the decision is "sell" and we have already sold the asset
     we take no action.

4. **Genetic Operations**

    In this step we apply our genetic operations on the selected population to create a larger population. Then we go to step 3.
    Genetic operations that are used here are crossover and mutation. In crossover, we swap two random subtrees from two trees
    to generate two new trees. In mutation, we choose a random node. Then, we swap two random subtrees from the left and right subtrees of the chosen node.
     Sometimes, some excess nodes are created as a result of genetic operations. We can remove them using a pruning algorithms.
     
 **Future Work**
 
 The main goal of this program is to practice and experiment with genetic algorithms. However, the results are very interesting and promising.
 The current program is mostly profitable. There are many areas to improve this project:
 1. Use tail recursive functions or iterative methods to make tree operations faster.
 2. Use financial indicators such as Moving Averages instead of raw and basic data.
 3. Use other parameters to configure the genetic algorithm.
 4. Add another layer of complexity by allowing the program to trade multiple assets instead of one.
 5. Couple this genetic algorithm with a neural network.
 
 **Disclaimer**
 
 This program is not intended to be used for real trading. The author of this project is in no way responsible for any trading loss.