"""Command-line interface for KMA."""

import argparse
import json
import sys
from typing import List, Tuple

import numpy as np

from optimizer.algorithm.komodo_mlipir_algorithm import KomodoMlipirAlgorithm
from optimizer.utils.benchmark import get_benchmark_function


def benchmark_cli():
    """Run benchmark tests from command line."""
    parser = argparse.ArgumentParser(
        description="Run benchmark tests for Komodo Mlipir Algorithm"
    )
    parser.add_argument(
        "--functions",
        nargs="+",
        default=["sphere", "rosenbrock"],
        help="Benchmark functions to test",
    )
    parser.add_argument(
        "--dimensions",
        nargs="+",
        type=int,
        default=[2, 5, 10],
        help="Dimensions to test",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=30,
        help="Number of runs per configuration",
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.json",
        help="Output file for results",
    )
    
    args = parser.parse_args()
    
    results = {}
    
    for func_name in args.functions:
        print(f"\nBenchmarking {func_name} function...")
        results[func_name] = {}
        
        for dim in args.dimensions:
            print(f"  Testing {dim}D...")
            func = get_benchmark_function(func_name, dim)
            bounds = get_function_bounds(func_name, dim)
            
            fitness_values = []
            
            for run in range(args.runs):
                kma = KomodoMlipirAlgorithm(
                    population_size=50,
                    fitness_function=func,
                    search_space=bounds,
                    max_iterations=200,
                    random_state=run
                )
                kma.fit(verbose=False)
                fitness_values.append(kma.best_fitness)
            
            results[func_name][f"{dim}D"] = {
                "mean": float(np.mean(fitness_values)),
                "std": float(np.std(fitness_values)),
                "min": float(np.min(fitness_values)),
                "max": float(np.max(fitness_values)),
            }
    
    # Save results
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {args.output}")


def optimize_cli():
    """Run optimization from command line."""
    parser = argparse.ArgumentParser(
        description="Optimize a function using Komodo Mlipir Algorithm"
    )
    parser.add_argument(
        "--function",
        required=True,
        help="Function to optimize (name or Python expression)",
    )
    parser.add_argument(
        "--bounds",
        nargs="+",
        type=float,
        required=True,
        help="Search space bounds (min1 max1 min2 max2 ...)",
    )
    parser.add_argument(
        "--population",
        type=int,
        default=50,
        help="Population size",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=200,
        help="Maximum iterations",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show optimization progress",
    )
    
    args = parser.parse_args()
    
    # Parse bounds
    if len(args.bounds) % 2 != 0:
        parser.error("Bounds must be pairs of min/max values")
    
    search_space = [
        (args.bounds[i], args.bounds[i + 1])
        for i in range(0, len(args.bounds), 2)
    ]
    
    # Get or create function
    if args.function in ["sphere", "rosenbrock", "rastrigin", "ackley"]:
        func = get_benchmark_function(args.function, len(search_space))
    else:
        # Try to evaluate as Python expression
        try:
            func = eval(f"lambda x: {args.function}")
        except:
            parser.error(f"Invalid function: {args.function}")
    
    # Run optimization
    kma = KomodoMlipirAlgorithm(
        population_size=args.population,
        fitness_function=func,
        search_space=search_space,
        max_iterations=args.iterations,
        random_state=args.seed
    )
    
    kma.fit(verbose=args.verbose)
    
    # Print results
    results = kma.get_results()
    print(f"\nOptimization completed!")
    print(f"Best solution: {results['best_solution']}")
    print(f"Best fitness: {results['best_fitness']}")
    print(f"Iterations: {results['n_iterations']}")


def get_function_bounds(func_name: str, dim: int) -> List[Tuple[float, float]]:
    """Get standard bounds for benchmark functions."""
    bounds_map = {
        "sphere": [(-5.12, 5.12)] * dim,
        "rosenbrock": [(-2.048, 2.048)] * dim,
        "rastrigin": [(-5.12, 5.12)] * dim,
        "ackley": [(-32.768, 32.768)] * dim,
    }
    return bounds_map.get(func_name, [(-10, 10)] * dim)


if __name__ == "__main__":
    if sys.argv[1] == "benchmark":
        benchmark_cli()
    elif sys.argv[1] == "optimize":
        optimize_cli()
    else:
        print("Usage: kma-benchmark or kma-optimize")