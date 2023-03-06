from hourglass import *
from randomwalk import *
from turing_machine import *
import random

def main():
    desc = open("computation.tm", 'r').read()
    tm = TuringMachine(Rules(desc), {}, 'a', 0)

    model = Hourglass(random_bits = 2, computation = tm)
    print(model.describe_stationary_distribution())
    walk = RandomWalk(model, random.choice(model.core_layer))
    for _ in range(10):
        for _ in range(10000):
            walk.step()
        print("Walk is at node", walk.current_node)

if __name__ == '__main__':
    main()