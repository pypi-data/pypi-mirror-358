class AnnotationToTask:
    def __init__(self, run, *args, **kwargs):
        """Initialize the plugin task pre annotation action class.

        Args:
            run: Plugin run object.
        """
        self.run = run
