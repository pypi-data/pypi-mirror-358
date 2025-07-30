import requests
import time
from runsawa import runsawa

# Using JSONPlaceholder - supports both POST (create) and GET (read) operations
BASE_URL = "https://jsonplaceholder.typicode.com"
POSTS_URL = f"{BASE_URL}/posts"
POST_URL = f"{BASE_URL}/posts/{{}}"


def create_post(post_id):
    """Creates a new post via POST request."""
    try:
        post_data = {
            "title": f"Test Post {post_id}",
            "body": f"This is the body content for post number {post_id}. Created via parallel processing!",
            "userId": (post_id % 10) + 1,  # Cycle through user IDs 1-10
        }
        response = requests.post(POSTS_URL, json=post_data, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "operation": "CREATE",
            "post_id": post_id,
            "created_id": data.get("id", "unknown"),
            "title": data.get("title", "unknown"),
            "user_id": data.get("userId", "unknown"),
        }
    except requests.exceptions.RequestException as e:
        print(f"Error creating post {post_id}: {e}")
        return None


def fetch_post(post_id):
    """Fetches an existing post via GET request."""
    try:
        response = requests.get(POST_URL.format(post_id), timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "operation": "FETCH",
            "post_id": post_id,
            "title": data.get("title", "unknown"),
            "user_id": data.get("userId", "unknown"),
            "body_length": len(data.get("body", "")),
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching post {post_id}: {e}")
        return None


if __name__ == "__main__":
    # Test with 50 posts for both create and fetch operations
    post_ids = range(1, 51)

    print("=" * 60)
    print("TESTING POST OPERATIONS (Creating Posts)")
    print("=" * 60)

    # Test creating posts with runsawa (parallel processing)
    print("Creating posts with runsawa (parallel processing)...")
    start_time = time.time()
    create_results_runsawa = []
    for response_data in runsawa(create_post, post_ids, workers=15):
        if response_data:
            create_results_runsawa.append(response_data)
    create_runsawa_time = time.time() - start_time
    print(f"runsawa create results: {len(create_results_runsawa)}")
    print(f"runsawa create time: {create_runsawa_time:.2f} seconds")

    # Test creating posts without runsawa (sequential processing)
    print("\nCreating posts without runsawa (sequential processing)...")
    start_time = time.time()
    create_results_sequential = []
    for post_id in list(post_ids)[:20]:  # Reduced for sequential to save time
        response_data = create_post(post_id)
        if response_data:
            create_results_sequential.append(response_data)
    create_sequential_time = time.time() - start_time
    print(f"Sequential create results: {len(create_results_sequential)}")
    print(f"Sequential create time: {create_sequential_time:.2f} seconds")

    print("\n" + "=" * 60)
    print("TESTING GET OPERATIONS (Fetching Posts)")
    print("=" * 60)

    # Test fetching posts with runsawa (parallel processing)
    print("Fetching posts with runsawa (parallel processing)...")
    start_time = time.time()
    fetch_results_runsawa = []
    for response_data in runsawa(fetch_post, post_ids, workers=15):
        if response_data:
            fetch_results_runsawa.append(response_data)
    fetch_runsawa_time = time.time() - start_time
    print(f"runsawa fetch results: {len(fetch_results_runsawa)}")
    print(f"runsawa fetch time: {fetch_runsawa_time:.2f} seconds")

    # Test fetching posts without runsawa (sequential processing)
    print("\nFetching posts without runsawa (sequential processing)...")
    start_time = time.time()
    fetch_results_sequential = []
    for post_id in list(post_ids)[:20]:  # Reduced for sequential to save time
        response_data = fetch_post(post_id)
        if response_data:
            fetch_results_sequential.append(response_data)
    fetch_sequential_time = time.time() - start_time
    print(f"Sequential fetch results: {len(fetch_results_sequential)}")
    print(f"Sequential fetch time: {fetch_sequential_time:.2f} seconds")

    # Show performance comparison
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)

    if create_runsawa_time > 0 and fetch_runsawa_time > 0:
        print("CREATE Operations:")
        create_speedup = (create_sequential_time / create_runsawa_time) * (
            len(create_results_runsawa) / len(create_results_sequential)
        )
        print(f"  Estimated speedup: {create_speedup:.2f}x faster with runsawa")

        print("\nFETCH Operations:")
        fetch_speedup = (fetch_sequential_time / fetch_runsawa_time) * (
            len(fetch_results_runsawa) / len(fetch_results_sequential)
        )
        print(f"  Estimated speedup: {fetch_speedup:.2f}x faster with runsawa")

    print(f"\nSample created posts:")
    for result in create_results_runsawa[:3]:
        if result:
            print(f"  - Created: '{result['title']}' (User {result['user_id']})")

    print(f"\nSample fetched posts:")
    for result in fetch_results_runsawa[:3]:
        if result:
            print(
                f"  - Fetched: '{result['title']}' (User {result['user_id']}, {result['body_length']} chars)"
            )
