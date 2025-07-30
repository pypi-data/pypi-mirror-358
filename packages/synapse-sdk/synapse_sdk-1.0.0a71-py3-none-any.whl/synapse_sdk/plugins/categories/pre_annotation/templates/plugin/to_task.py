class AnnotationToTask:
    def __init__(self, run, *args, **kwargs):
        """Initialize the plugin task pre annotation action class.

        Args:
            run: Plugin run object.
        """
        self.run = run

    def convert_data_from_file(self, data: dict):
        """Convert the data from a file to a task object.

        Args:
            data: Converted data.
        """
        return data

    def convert_data_from_inference(self, data: dict):
        """Convert the data from inference result to a task object.

        Args:
            data: Converted data.
        """
        return data
