from las_vegas import *
from montecarlo import *
from randomwalk import *
from turing_machine import *
from plot import lv_create_plot_output_ready_prob, mc_create_plot_output_ready_prob
import argparse
import webbrowser, urllib.parse


def main():
    parser = argparse.ArgumentParser(prog="python3 simulate.py", 
        description="Runs a simulated model on a specified Turing machine")
    parser.add_argument('model_kind', choices=['lv', 'mc'], help = 'lv for Las Vegas, mc for Monte Carlo')
    parser.add_argument('tm_filename')
    parser.add_argument('-i', '--tm-initial-state', required=True, help = 'the head state to start the Turing machine in')
    parser.add_argument('-b', '--tm-random-bits', required=True, type=int, help = 'number of random bits to feed into the Turing machine as input')
    parser.add_argument('-t', '--time-between-observations', dest='T', required=False, type=int, help = 'units of time in between consecutive observations, defaults to 100 * comp_length^2 * bits^2')
    parser.add_argument('-c', '--create-plot', choices=['output_ready_prob'], required=False, help='instead of running the standard simulation, output the desired plot')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--print-model', action="store_true", help = 'do not run simulation, only print the computation graph of the constructed model (prints in GraphViz format)')
    group.add_argument('-g', '--interactive-graph', action="store_true", help = 'like --print-model, but opens a web browser with an interactive view of the computation graph of the model')

    args = parser.parse_args()
    
    print("Parsing Turing machine configuration... ", end = '', flush=True)
    desc = open(args.tm_filename, 'r').read()
    tm = TuringMachine(Rules(desc), {}, args.tm_initial_state)
    print("Done")

    print("Constructing computation graph...", end = '', flush=True)
    if args.model_kind == 'lv':
        model = LasVegasSampler(args.tm_random_bits, tm)
        walk = LasVegasRandomWalk(model)
    elif args.model_kind == 'mc':
        model = MonteCarloSampler(args.tm_random_bits, tm)
        walk = MonteCarloRandomWalk(model)
    else:
        raise "Model type not supported (yet)"
    print("Done")

    if args.print_model or args.interactive_graph:
        if args.model_kind == "lv":
            clusterings = [("top half", range(model.randomizer_layer_start_index)),
                           ("randomizer", range(model.randomizer_layer_start_index, model.bottom_layer_start_index)),
                           ("bottom half", range(model.bottom_layer_start_index, len(model.layers)))]
            graphviz_string = model.to_graphviz_layered(clusterings)
        elif args.model_kind == "mc":
            clusterings = [("m = 1", range(len(model.layers) // 2)),
                           ("m = -1", range(len(model.layers) // 2, len(model.layers)))]
            graphviz_string = model.to_graphviz_layered(clusterings)
        if args.print_model:
            print(graphviz_string)
        elif args.interactive_graph:
            quoted_string = urllib.parse.quote(graphviz_string, safe="")
            url = "https://dreampuf.github.io/GraphvizOnline/#" + quoted_string
            try:
                webbrowser.open(url)
            except OSError:
                with open("graph.txt", 'w') as file:
                    file.write(graphviz_string)
                print("Graph is too big to be passed in the command line. Go to http://magjac.com/graphviz-visual-editor/ and paste the contents of the generated graph.txt")
        return
    
    match args.create_plot:
        case 'output_ready_prob':
            print("Generating plot 'output ready probability' from samples...", end = '', flush=True)
            sampling_period = 15 * (args.tm_random_bits ** 2 + longest_computation_path(tm.rules, args.tm_initial_state, args.tm_random_bits))
            if args.model_kind == 'lv':
                lv_create_plot_output_ready_prob(walk, sampling_period)
            elif args.model_kind == 'mc':
                mc_create_plot_output_ready_prob(walk, sampling_period)
            print("Done")
            return
        case _:
            pass

    print("Beginning simulation.")
    if args.model_kind == 'lv':
        walk = LasVegasRandomWalk(model)
        run_time = args.T or 100 * (args.tm_random_bits ** 2 + longest_computation_path(tm.rules, args.tm_initial_state, args.tm_random_bits))
        while True:
            walk.run_for_time(run_time)
            ready, node = walk.observe()
            if ready:
                print('Observation: half =', node.data['half'], '-- input =', node.data['randomness'], '-> output =', node.data['tape'])
            else:
                print('Observation not ready')
    if args.model_kind == 'mc':
        walk = MonteCarloRandomWalk(model)
        run_time = args.T or 100 * (args.tm_random_bits ** 2 + longest_computation_path(tm.rules, args.tm_initial_state, args.tm_random_bits))
        while True:
            walk.run_for_time(run_time)
            ready, node = walk.observe()
            half, output_node = outputting_half_of_monte_carlo_node(node)
            print('Observation: half =', half, '-- input =', output_node.data['randomness'], '-> output =', output_node.data['tape'], '-- was_reset =', ready)

if __name__ == '__main__':
    main()

