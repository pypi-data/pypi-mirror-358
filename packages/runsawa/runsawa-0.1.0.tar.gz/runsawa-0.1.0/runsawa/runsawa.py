import concurrent.futures
import sys
from tqdm import tqdm


def runsawa(func, iterable, workers=5):
    """
    Runs a function concurrently on an iterable and shows progress.

    Args:
        func: The function to apply to each item in the iterable.
        iterable: The iterable to loop over.
        workers: The number of concurrent workers.

    Returns:
        A generator that yields the results.
    """
    iterable = list(iterable)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(func, item) for item in iterable}

        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(iterable),
            file=sys.stdout,
        ):
            try:
                yield future.result()
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
