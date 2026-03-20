import multiprocessing

class Franchise:
    """
    Sub-Corporations.
    """
    def spawn_branch(self, task):
        p = multiprocessing.Process(target=self._branch_logic, args=(task,))
        p.start()
        return f"Spinning off new Franchise Node (PID: {p.pid}) for: {task}"

    def _branch_logic(self, task):
        # In a real app, this runs a separate loop
        print(f"[Franchise] Branch executing: {task}")

franchise = Franchise()
