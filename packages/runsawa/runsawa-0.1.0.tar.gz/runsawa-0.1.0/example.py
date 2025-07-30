import time
from runsawa import runsawa


def my_function(i):
    time.sleep(0.001)  # Reduced sleep time for 10k iterations
    return i * 2


if __name__ == "__main__":
    # Test with runsawa (parallel processing)
    print("Testing with runsawa (parallel processing)...")
    start_time = time.time()
    results_runsawa = []
    for result in runsawa(my_function, range(10000), workers=50):
        results_runsawa.append(result)
    runsawa_time = time.time() - start_time
    print(f"runsawa results count: {len(results_runsawa)}")
    print(f"runsawa execution time: {runsawa_time:.2f} seconds")

    # Test without runsawa (sequential processing)
    print("\nTesting without runsawa (sequential processing)...")
    start_time = time.time()
    results_sequential = []
    for i in range(10000):
        results_sequential.append(my_function(i))
    sequential_time = time.time() - start_time
    print(f"Sequential results count: {len(results_sequential)}")
    print(f"Sequential execution time: {sequential_time:.2f} seconds")

    # Show performance comparison
    print(f"\nPerformance comparison:")
    print(f"Speedup: {sequential_time / runsawa_time:.2f}x faster with runsawa")
    print(f"Time saved: {sequential_time - runsawa_time:.2f} seconds")

    # Verify results are the same
    print(f"Results match: {sorted(results_runsawa) == sorted(results_sequential)}")
