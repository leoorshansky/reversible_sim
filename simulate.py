from hourglass import *
from randomwalk import *
import random

def main():
    model = Hourglass(random_bits = 2, comp_length = 3)
    walk = RandomWalk(model, random.choice(model.core_layer))
    for _ in range(10):
        for _ in range(1000):
            walk.step()
        print("Walk is at node", walk.current_node)

if __name__ == '__main__':
    main()