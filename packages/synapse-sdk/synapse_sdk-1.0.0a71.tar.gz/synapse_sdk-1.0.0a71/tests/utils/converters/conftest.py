"""
Pytest configuration file for converters tests.
This file makes fixtures available to all tests in the converters module.
"""

# Import fixtures from dm_schema.py
from .fixtures.dm_schema import (
    categorized_dataset_path,
    dm_converter_class,
    fixtures_root,
    jpg_file_path_1,
    jpg_file_path_2,
    jpg_file_path_3,
    jpg_file_paths,
    jpg_file_paths_dict,
    jpg_files_dir,
    not_categorized_dataset_path,
    sample_coco_expected,
    sample_dm_json,
    temp_output_dir,
    test_dataset_path,
    train_dataset_path,
    valid_dataset_path,
)

# Re-export all fixtures so they're available to tests
__all__ = [
    'fixtures_root',
    'categorized_dataset_path',
    'not_categorized_dataset_path',
    'train_dataset_path',
    'test_dataset_path',
    'valid_dataset_path',
    'sample_dm_json',
    'sample_coco_expected',
    'temp_output_dir',
    'dm_converter_class',
    'jpg_files_dir',
    'jpg_file_paths',
    'jpg_file_path_1',
    'jpg_file_path_2',
    'jpg_file_path_3',
    'jpg_file_paths_dict',
]
