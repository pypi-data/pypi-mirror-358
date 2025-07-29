import os


class FromDMConverter:
    """Base class for converting data from DM format to a specific format.

    Attrs:
        root_dir (str): Root directory containing data.
        is_categorized_dataset (bool): Whether to handle train, test, valid splits.
        version (str): Version of the converter.
        converted_data: Holds the converted data after calling `convert()`.

    Usage:
        1. Subclass this base class and implement the `convert()` and `save_to_folder()` methods.
        2. Instantiate the converter with the required arguments.
        3. Call `convert()` to perform the in-memory conversion and obtain the result as a dict or list of dicts.
        4. Call `save_to_folder(output_dir)` to save the converted data and optionally copy original files.

    Args:
        root_dir (str): Path to the root directory containing data.
            - If `is_categorized_dataset=True`, the directory should contain subdirectories for
            `train`, `valid`, and optionally `test`.
            - Each subdirectory should contain `json` and `original_file` folders.
            - `train` and `valid` are required, while `test` is optional.
        is_categorized_dataset (bool): Whether to handle train, test, valid splits.

    Returns:
        - convert(): Returns the converted data as a Python dict or a dictionary with keys for each split.
        - save_to_folder(): Saves the converted data and optionally copies original files
        to the specified output directory.

    Example usage:
        # Dataset with splits
        converter = MyCustomConverter(root_dir='/path/to/data', is_categorized_dataset=True)
        converted = converter.convert()  # Returns a dict with keys for `train`, `valid`, and optionally `test`
        converter.save_to_folder('/my/target/output')  # Writes files/folders to output location

        # Dataset without splits
        converter = MyCustomConverter(root_dir='/path/to/data', is_categorized_dataset=False)
        converted = converter.convert()  # Returns a dict or a list, depending on the implementation
        converter.save_to_folder('/my/target/output')  # Writes files/folders to output location
    """

    def __init__(self, root_dir: str, is_categorized_dataset: bool = False) -> None:
        self.root_dir: str = root_dir
        self.is_categorized_dataset: bool = is_categorized_dataset
        self.version: str = '1.0'
        self.converted_data = None

    def convert(self):
        """Convert DM format to a specific format.

        This method should be implemented by subclasses to perform the actual conversion.
        """
        raise NotImplementedError

    def save_to_folder(self, output_dir: str) -> None:
        """Save converted data to the specified folder."""
        self.ensure_dir(output_dir)
        if self.converted_data is None:
            # Automatically call convert() if converted_data is not set
            self.converted_data = self.convert()

    @staticmethod
    def ensure_dir(path: str) -> None:
        """Ensure that the directory exists, creating it if necessary."""
        if not os.path.exists(path):
            os.makedirs(path)

    def _validate_required_dirs(self, dirs):
        """Validate that all required directories exist.

        Args:
            dirs (dict): A dictionary where keys are directory names and values are their paths.

        Raises:
            FileNotFoundError: If any required directory does not exist.
        """
        for name, path in dirs.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f'[ERROR] Required directory "{name}" does not exist at {path}')

    def _validate_optional_dirs(self, dirs):
        """Validate optional directories and return those that exist.

        Args:
            dirs (dict): A dictionary where keys are directory names and values are their paths.

        Returns:
            dict: A dictionary of existing optional directories.
        """
        existing_dirs = {}
        for name, path in dirs.items():
            if os.path.exists(path):
                existing_dirs[name] = path
            else:
                print(f'[WARNING] Optional directory "{name}" does not exist. Skipping.')
        return existing_dirs

    def _validate_splits(self, required_splits, optional_splits=[]):
        """Validate required and optional splits in the dataset.

        Args:
            required_splits (list): List of required split names (e.g., ['train', 'valid']).
            optional_splits (list): List of optional split names (e.g., ['test']).

        Returns:
            dict: A dictionary with split names as keys and their corresponding directories as values.
        """
        splits = {}

        if self.is_categorized_dataset:
            # Validate required splits
            required_dirs = {split: os.path.join(self.root_dir, split) for split in required_splits}
            self._validate_required_dirs(required_dirs)
            splits.update(required_dirs)

            # Validate optional splits
            optional_dirs = {split: os.path.join(self.root_dir, split) for split in optional_splits}
            splits.update(self._validate_optional_dirs(optional_dirs))
        else:
            # Validate `json` and `original_file` folders for non-split datasets
            required_dirs = {
                'json': os.path.join(self.root_dir, 'json'),
                'original_file': os.path.join(self.root_dir, 'original_file'),
            }
            self._validate_required_dirs(required_dirs)
            splits['root'] = self.root_dir

        return splits

    def _set_directories(self, split=None):
        """Set `self.json_dir` and `self.original_file_dir` based on the dataset split.

        Args:
            split (str, optional): The name of the split (e.g., 'train', 'valid', 'test').
                                   If None, assumes no dataset split.
        """
        if split:
            split_dir = os.path.join(self.root_dir, split)
            self.json_dir = os.path.join(split_dir, 'json')
            self.original_file_dir = os.path.join(split_dir, 'original_file')
        else:
            self.json_dir = os.path.join(self.root_dir, 'json')
            self.original_file_dir = os.path.join(self.root_dir, 'original_file')
