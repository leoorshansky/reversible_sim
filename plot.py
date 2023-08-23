from las_vegas import *
from montecarlo import *
from randomwalk import *
from turing_machine import *
from plotnine import *
import pandas as pd
import numpy as np

def lv_create_plot_output_ready_prob(walk: RandomWalk, sampling_period: int):
    max_trials = 20

    output_probs = np.zeros(max_trials)
    TRIALS = 500
    
    for i in range(TRIALS):
        found = False
        for j in range (max_trials):
            if found:
                output_probs[j] += 1.
            else:
                walk.run_for_time(sampling_period)
                ready, _ = walk.observe()
                if ready:
                    found = True
                    output_probs[j] += 1.

    for i in range(max_trials):
        output_probs[i]/=float(TRIALS)

    df = pd.DataFrame({
        "sample_sizes": np.arange(1,21),
        "output_probs": output_probs
    })

    plt = ggplot(df, aes(x = "sample_sizes", y = "output_probs")) + \
        geom_point() + \
        geom_line(aes(group = 1), color = "red") + \
        labs(title = f"Las Vegas Model - Simulated Probability of Observing a Valid Output\n by the Nth Measurement",
             x = f"Number of Measurements T Time Apart", y = f"Probability of Seeing Valid Output ({TRIALS} trials)")
    plt.save("plot.png")

def mc_create_plot_output_ready_prob(walk: RandomWalk, sampling_period: int):
    max_time = sampling_period * 2

    TIME_INCREMENT = 50
    num_increments = int(max_time / TIME_INCREMENT)
    print(num_increments, "increments")

    output_probs = np.zeros(num_increments)
    TRIALS = 500

    for i in range(TRIALS):
        found = False
        for j in range(num_increments):
            if found:
                output_probs[j] += 1.
            else:
                walk.run_for_time(TIME_INCREMENT)
                ready, _ = walk.observe()
                if ready:
                    found = True
                    output_probs[j] += 1.

    for i in range(num_increments):
        output_probs[i] /= float(TRIALS)

    df = pd.DataFrame({
        "sampling_periods": np.arange(0, max_time, TIME_INCREMENT),
        "output_probs": output_probs
    })

    plt = ggplot(df, aes(x = "sampling_periods", y = "output_probs")) + \
        geom_point() + \
        geom_line(aes(group = 1), color = "red") + \
        labs(title = f"Monte Carlo Model - Simulated Probability of Observing an\nIndependent Sample By the Nth Timestep",
                x = f"Number of Timesteps Waited", y = f"Probability of Independent Sample ({TRIALS} trials)")
    plt.save("plot.png")