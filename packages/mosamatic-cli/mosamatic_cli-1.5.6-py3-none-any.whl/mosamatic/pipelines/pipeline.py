class Pipeline:
    def __init__(self, input, output, params=None, overwrite=False):
        self._input = input
        self._output = output
        self._params = params
        self._overwrite = overwrite
        self._tasks = []

    def add_task(self, task):
        self._tasks.append(task)

    def run(self):
        for task in self._tasks:
            task.run()