import timeit

class RnDLab:
    """
    Research & Development.
    """
    def ab_test(self, snippet_a, snippet_b):
        """
        Benchmarks two snippets safely.
        """
        try:
            t_a = timeit.timeit(stmt=snippet_a, number=1000)
            t_b = timeit.timeit(stmt=snippet_b, number=1000)
            
            winner = "A" if t_a < t_b else "B"
            return f"A/B Test Complete.\nA: {t_a:.5f}s\nB: {t_b:.5f}s\nWinner: {winner}"
        except Exception as e:
            return f"Test Failed: {e}"

rnd = RnDLab()
