##Genetic Algorithm Based Trading System##

**Author**
* Farhang Rouhi

**Introduction**

This program uses genetic algorithms and binary decision trees to develop a Trading system. The resulting binary decision tree
is capable of detecting patterns in basic price and volume data and make an expert decision about the next optimal action.

**How does it work?**
1.  **Data Collection**
    
    First we collect candle stick data from Binance cryptocurrency exchange. Note that the data can come from any exchange, Binance is an arbitrary choice.
The data is collected for multiple time intervals to give the system a better intuition about the market behaviour. Each collected data point is a 
continues value which means that the state space is infinite and too large. In order to make the state space finite, 
each data point is converted to a discrete value. These values are ["very low","low","high","very high"] enumerated by [-2,-1,1,2].
For simplicity and smaller state space we could also use [-1,1].

2. **Initial Random Population**

    