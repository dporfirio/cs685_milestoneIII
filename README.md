# Install

Python 3.10 or above is required.

```
pip install unified-planning up-fast-downward
```

# Run

This code accepts many command line arguments. The only required arguments are the dimensions of the environment that the robot exists within. You can use 100 x 80 by default, but you can increase/decrease these to your liking.

```
python3 run.py --dim 100 80
```

The code accepts many other arguments:
```
1. --runs: default 10. This is the number of random planning problems to generate, run, and visualize in succession
2. --growth-factor: default 5. The size of obstacles in the environment.
3. --step: default 10. This is the size of each "leap" in RRT/RRT*.
4. --rrt_n: default 5000. This is the number of iterations to run in RRT/RRT*.
5. --rrt_star: default False. This is whether to run RRT* (versus RRT by default).
```

An example run with several additional arguments is below:

```
python3 run.py --dim 100 80 --runs 1 --growth-factor 3 --step 5 --rrt_n 10000 --rrt_star
```