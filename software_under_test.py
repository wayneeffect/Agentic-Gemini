def compute_heavy_logic(n: int) -> int:
    """
    TARGET BENCHMARK: A naive, unoptimized Fibonacci function.
    Gemini needs to rewrite this to use memoization, iteration, or Binet's formula 
    without changing the output results or breaking the evaluator.
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return compute_heavy_logic(n - 1) + compute_heavy_logic(n - 2)
