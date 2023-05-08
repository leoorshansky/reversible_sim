from hourglass import *
from randomwalk import *
from turing_machine import *
import random
import pandas as pd
import numpy as np
from plotnine import *

def main():
    desc = open("computation.tm", 'r').read()
    tm = TuringMachine(Rules(desc), {}, 'a', 0)

    BITS = 8
    model = Hourglass(random_bits = BITS, computation = tm)
    max_trials = 20

    output_probs = np.zeros(20)
    C = 50
    RUN_LENGTH = C * (BITS ** 2)
    TRIALS = 500

    walk = RandomWalk(model, random.choice([node for node in model.adj_list if "half" in node.data]))
    half = walk.current_node.data["half"]
    
    for i in range(TRIALS):
        found = False
        for j in range (max_trials):
            if found:
                output_probs[j]=output_probs[j]+1
            else:
                node = walk.run_for_time(RUN_LENGTH)
                if node.type == "hold_output" and node.data["half"] != half:
                    half = node.data["half"]
                    found = True
                    output_probs[j]=output_probs[j]+1

    for i in range(max_trials):
        output_probs[i]/=float(TRIALS)


    print(output_probs)
    df = pd.DataFrame({
        "sample_sizes": np.arange(1,21),
        "output_probs": output_probs
    })

    plt = ggplot(df, aes(x = "sample_sizes", y = "output_probs")) + \
        geom_point() + \
        geom_line(aes(group = 1), color = "red") + \
        labs(title = f"Las Vegas Model - Simulated Probability of Observing a Valid Output\n by the Nth Measurement on {BITS}-bit Bitstring-Inversion TM",
             x = f"Number of Measurements T Time Apart (T={C}*r^2={RUN_LENGTH})", y = f"Probability of Seeing Valid Output ({TRIALS} trials)")
    plt.save("plot.png")


if __name__ == '__main__':
    main()

