# Simulator for the DNA29 Conference Paper Submission: "Harvesting Brownian Motion: Zero Energy Computational Sampling"

## Usage
```
usage: simulate [-h] -i TM_INITIAL_STATE -b TM_RANDOM_BITS [-t T] {lv,mc} tm_filename

Runs a simulated model on a specified Turing machine

positional arguments:
  {lv,mc}               lv for Las Vegas, mc for Monte Carlo
  tm_filename

options:
  -h, --help            show this help message and exit
  -i TM_INITIAL_STATE, --tm_initial_state TM_INITIAL_STATE
  -b TM_RANDOM_BITS, --tm_random_bits TM_RANDOM_BITS
                        number of random bits to feed into the Turing machine as input
  -t T, --time_between_observations T
                        units of time in between consecutive observations, defaults to 500 * bits^2
```
