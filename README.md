# Simulator for the DNA29 Conference **Best Poster Award Winner**: "Harvesting Brownian Motion: Zero Energy Computational Sampling"

[Read the paper here.](https://arxiv.org/pdf/2309.06957.pdf)

## Usage
```
usage: python3 simulate.py [-h] -i TM_INITIAL_STATE -b TM_RANDOM_BITS [-t T] [-p] {lv,mc} tm_filename

Runs a simulated model on a specified Turing machine

positional arguments:
  {lv,mc}               lv for Las Vegas, mc for Monte Carlo
  tm_filename

options:
  -h, --help            show this help message and exit
  -i TM_INITIAL_STATE, --tm_initial_state TM_INITIAL_STATE
                        the head state to start the Turing machine in
  -b TM_RANDOM_BITS, --tm_random_bits TM_RANDOM_BITS
                        number of random bits to feed into the Turing machine as input
  -t T, --time_between_observations T
                        units of time in between consecutive observations, defaults to 500 * bits^2
  -p, --print-model     do not run simulation, only print the computation graph of the constructed model
```
