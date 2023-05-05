from hourglass import *
from randomwalk import *
from turing_machine import *
import random
import pandas as pd
from plotnine import *

def main():
    desc = open("computation.tm", 'r').read()
    tm = TuringMachine(Rules(desc), {}, 'a', 0)

    BITS = 8
    model = Hourglass(random_bits = BITS, computation = tm)

    sample_sizes = [1, 2, 5, 10, 20, 50, 100]
    output_probs = []
    C = 500
    RUN_LENGTH = C * (BITS ** 2)
    TRIALS = 100

    walk = RandomWalk(model, random.choice([node for node in model.adj_list if "half" in node.data]))
    half = walk.current_node.data["half"]
    for sample_size in sample_sizes:
        print(sample_size)
        found_outputs = 0.
        for _ in range(TRIALS):
            for _ in range(sample_size):
                node = walk.run_for_time(RUN_LENGTH)
                if node.type == "hold_output" and node.data["half"] != half:
                    half = node.data["half"]
                    found_outputs += 1.
                    break
                
        output_probs.append(found_outputs / TRIALS)
            
    print(output_probs)
    print(sample_sizes)
    df = pd.DataFrame({
        "sample_sizes": sample_sizes,
        "output_probs": output_probs
    })

    plt = ggplot(df, aes(x = "sample_sizes", y = "output_probs")) + \
        geom_point() + \
        scale_x_log10() + \
        geom_line(aes(group = 1), color = "red") + \
        labs(title = f"Las Vegas Model - Simulated Probability of Observing a Valid Output\n by the Nth Measurement on {BITS}-bit Bitstring-Inversion TM",
             x = f"Number of Measurements T Time Apart (T={C}*r^2={RUN_LENGTH})", y = f"Probability of Seeing Valid Output (n={TRIALS})")
    plt.save("plot.png")


if __name__ == '__main__':
    main()