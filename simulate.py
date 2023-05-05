from hourglass import *
from randomwalk import *
from turing_machine import *
import random
import pandas as pd
from plotnine import *

def main():
    desc = open("computation.tm", 'r').read()
    tm = TuringMachine(Rules(desc), {}, 'a', 0)

    model = Hourglass(random_bits = 4, computation = tm)

    sample_sizes = [1, 2, 5, 10, 20, 50, 100]
    output_probs = []
    RUN_LENGTH = 10000
    TRIALS = 100

    walk = RandomWalk(model, random.choice(model.core_layer))
    half = None
    for sample_size in sample_sizes:
        print(sample_size)
        found_outputs = 0.
        for _ in range(TRIALS):
            for _ in range(sample_size):
                node = walk.run_for_time(RUN_LENGTH)
                if node.type == "hold_output" and node.data["half"] != half:
                    found_outputs += 1.
                    break
                half = node.data["half"]
        output_probs.append(found_outputs)
            
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
        labs(title = "Las Vegas Model - Simulated Probability of Observing a\nValid Output by the Nth Measurement",
             x = "Number of Measurements", y = "Probability of Seeing Valid Output (n=100)")
    plt.save("plot.png")


if __name__ == '__main__':
    main()