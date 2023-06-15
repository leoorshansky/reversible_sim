from las_vegas import *
from randomwalk import *
from turing_machine import *
import random
import pandas as pd
import numpy as np
from plotnine import *
import argparse

# def make_plot_lv_output_prob():
#     desc = open("computation.tm", 'r').read()
#     tm = TuringMachine(Rules(desc), {}, 'a', 0)

#     BITS = 8
#     model = Hourglass(random_bits = BITS, computation = tm)
#     max_trials = 20

#     output_probs = np.zeros(20)
#     C = 500
#     RUN_LENGTH = C * (BITS ** 2)
#     TRIALS = 500

#     walk = RandomWalk(model, random.choice([node for node in model.adj_list if "half" in node.data]))
#     half = walk.current_node.data["half"]
    
#     for i in range(TRIALS):
#         found = False
#         for j in range (max_trials):
#             if found:
#                 output_probs[j]=output_probs[j]+1
#             else:
#                 node = walk.run_for_time(RUN_LENGTH)
#                 if node.type == "hold_output" and node.data["half"] != half:
#                     half = node.data["half"]
#                     found = True
#                     output_probs[j]=output_probs[j]+1

#     for i in range(max_trials):
#         output_probs[i]/=float(TRIALS)


#     print(output_probs)
#     df = pd.DataFrame({
#         "sample_sizes": np.arange(1,21),
#         "output_probs": output_probs
#     })

#     plt = ggplot(df, aes(x = "sample_sizes", y = "output_probs")) + \
#         geom_point() + \
#         geom_line(aes(group = 1), color = "red") + \
#         labs(title = f"Las Vegas Model - Simulated Probability of Observing a Valid Output\n by the Nth Measurement",
#              x = f"Number of Measurements T Time Apart", y = f"Probability of Seeing Valid Output ({TRIALS} trials)")
#     plt.save("plot.png")

def main():
    parser = argparse.ArgumentParser(prog="simulate", 
        description="Runs a simulated model on a specified Turing machine")
    parser.add_argument('model_kind', choices=['lv', 'mc'], help = 'lv for Las Vegas, mc for Monte Carlo')
    parser.add_argument('tm_filename')
    parser.add_argument('-i', '--tm_initial_state', required=True, help = 'the head state to start the Turing machine in')
    parser.add_argument('-b', '--tm_random_bits', required=True, type=int, help = 'number of random bits to feed into the Turing machine as input')
    parser.add_argument('-t', '--time_between_observations', dest='T', required=False, help = 'units of time in between consecutive observations, defaults to 500 * bits^2')

    args = parser.parse_args()
    
    print("Parsing Turing machine configuration... ", end = '', flush=True)
    desc = open(args.tm_filename, 'r').read()
    tm = TuringMachine(Rules(desc), {}, args.tm_initial_state, 0)
    print("Done")

    print("Constructing computation graph...", end = '', flush=True)
    if args.model_kind == 'lv':
        model = Hourglass(args.tm_random_bits, tm)
    else:
        raise "Model type not supported (yet)"
    print("Done")

    print("Beginning simulation.")
    walk = RandomWalk(model, random.choice([node for node in model.adj_list if "half" in node.data]))
    half = walk.current_node.data["half"]

    run_time = args.T or 500 * (args.tm_random_bits ** 2)

    while True:
        node = walk.run_for_time(run_time)
        if node.type == "hold_output" and node.data["half"] != half:
            half = node.data["half"]
            print('Observation: input =', node.data['randomness'], '-> output =', node.data['output'])
        else:
            print('Observation not ready')


if __name__ == '__main__':
    main()

