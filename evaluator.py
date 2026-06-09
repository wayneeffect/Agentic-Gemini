import time
import json
import sys
from software_under_test import compute_heavy_logic

def run_tests():
    # Test cases to guarantee semantic correctness
    test_cases = {0: 0, 1: 1, 5: 5, 10: 55, 20: 6765, 30: 832040}
    
    # 1. Functional Correctness Check
    try:
        for input_val, expected_output in test_cases.items():
            if compute_heavy_logic(input_val) != expected_output:
                return {"status": "FAIL", "reason": f"Incorrect output for n={input_val}"}
    except Exception as e:
        return {"status": "FAIL", "reason": f"Execution crashed: {str(e)}"}

    # 2. Performance Benchmarking Check
    # We measure how long it takes to compute a heavy value (n=35)
    start_time = time.perf_counter()
    _ = compute_heavy_logic(35) 
    end_time = time.perf_counter()
    
    execution_ms = int((end_time - start_time) * 1000)

    return {
        "status": "SUCCESS",
        "latency_ms": execution_ms,
        "reason": f"All tests passed in {execution_ms}ms"
    }

if __name__ == "__main__":
    result = run_tests()
    # Output raw JSON to standard out for our loop wrapper to capture
    print(json.dumps(result))
    # If the tests failed, exit with a non-zero code to trigger a Git rollback
    if result["status"] == "FAIL":
        sys.exit(1)
