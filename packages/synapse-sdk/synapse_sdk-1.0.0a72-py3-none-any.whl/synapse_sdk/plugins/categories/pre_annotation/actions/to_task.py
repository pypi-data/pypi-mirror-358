import json
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

import requests
from pydantic import AfterValidator, BaseModel, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.plugins.models import Run
from synapse_sdk.utils.pydantic.validators import non_blank


class AnnotationMethod(str, Enum):
    FILE = 'file'
    INFERENCE = 'inference'


class AnnotateTaskDataStatus(str, Enum):
    SUCCESS = 'success'
    FAILED = 'failed'


class ToTaskRun(Run):
    class AnnotateTaskDataLog(BaseModel):
        """Log model for annotate task data."""

        task_info: Optional[str] = None
        status: AnnotateTaskDataStatus
        created: str

    class MetricsRecord(BaseModel):
        """Metrics record model."""

        stand_by: int
        failed: int
        success: int

    def log_annotate_task_data(self, task_info: Dict[str, Any], status: AnnotateTaskDataStatus):
        """Log annotate task data."""
        now = datetime.now().isoformat()
        self.log(
            'annotate_task_data',
            self.AnnotateTaskDataLog(task_info=json.dumps(task_info), status=status, created=now).model_dump(),
        )

    def log_metrics(self, record: MetricsRecord, category: str):
        """Log FileToTask metrics.

        Args:
            record (MetricsRecord): The metrics record to log.
            category (str): The category of the metrics.
        """
        record = self.MetricsRecord.model_validate(record)
        self.set_metrics(value=record.model_dump(), category=category)


class ToTaskParams(BaseModel):
    """ToTask action parameters.

    Args:
        name (str): The name of the action.
        description (str | None): The description of the action.
        project (int): The project ID.
        agent (int): The agent ID.
        task_filters (dict): The filters of tasks.
        method (AnnotationMethod): The method of annotation.
        target_specification_name (str | None): The name of the target specification.
        model (int): The model ID.
        pre_processor (int | None): The pre processor ID.
        pre_processor_params (dict): The params of the pre processor.
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: Optional[str] = None
    project: int
    agent: int
    task_filters: Dict[str, Any]
    method: Optional[AnnotationMethod] = None
    target_specification_name: Optional[str] = None
    model: Optional[int] = None
    pre_processor: Optional[int] = None
    pre_processor_params: Dict[str, Any]

    @field_validator('project', mode='before')
    @classmethod
    def check_project_exists(cls, value: int, info) -> int:
        """Validate synapse-backend project exists."""
        if not value:
            return value

        action = info.context['action']
        client = action.client
        try:
            client.get_project(value)
        except ClientError:
            raise PydanticCustomError('client_error', 'Error occurred while checking project exists.')
        return value


@register_action
class ToTaskAction(Action):
    """ToTask action for pre-annotation data processing.

    This action handles the process of annotating data to tasks in a project. It supports
    two annotation methods: file-based annotation and inference-based annotation.

    File-based annotation fetches data from file URLs specified in task data units,
    downloads and processes JSON data, and updates task data with the processed information.
    It also validates target specification names against file specifications.

    Inference-based annotation is currently not supported but will support model inference
    for automatic data annotation in future implementations.

    Attrs:
        name (str): Action name, set to 'to_task'.
        category (PluginCategory): Plugin category, set to PRE_ANNOTATION.
        method (RunMethod): Execution method, set to JOB.
        run_class (Type[ToTaskRun]): Run class for this action.
        params_model (Type[ToTaskParams]): Parameter validation model.
        progress_categories (Dict): Progress tracking configuration.
        metrics_categories (Set[str]): Metrics categories for this action.

    Note:
        This action requires a valid project with an associated data collection.
        For file-based annotation, the target_specification_name must exist in the
        project's file specifications.

    Raises:
        ValueError: If run instance or parameters are not properly initialized.
        ClientError: If there are issues with backend API calls.
    """

    name = 'to_task'
    category = PluginCategory.PRE_ANNOTATION
    method = RunMethod.JOB
    run_class = ToTaskRun
    params_model = ToTaskParams
    progress_categories = {
        'annotate_task_data': {
            'proportion': 100,
        },
    }
    metrics_categories = {
        'annotate_task_data': {
            'stand_by': 0,
            'failed': 0,
            'success': 0,
        }
    }

    def start(self):
        """Start to_task action.

        * Generate tasks.
        * Annotate data to tasks.
        """
        if not self.run or not self.params:
            raise ValueError('Run instance or parameters not properly initialized')

        # Type assertion to help the linter
        assert isinstance(self.run, ToTaskRun)
        assert isinstance(self.run.client, BackendClient)

        client: BackendClient = self.run.client
        project_id = self.params['project']
        project_response = client.get_project(project_id)
        if isinstance(project_response, str):
            self.run.log_message('Invalid project response received.')
            self.run.end_log()
            return {}
        project: Dict[str, Any] = project_response

        data_collection_id = project.get('data_collection')
        if not data_collection_id:
            self.run.log_message('Project does not have a data collection.')
            self.run.end_log()
            return {}

        data_collection_response = client.get_data_collection(data_collection_id)
        if isinstance(data_collection_response, str):
            self.run.log_message('Invalid data collection response received.')
            self.run.end_log()
            return {}
        data_collection: Dict[str, Any] = data_collection_response

        # Generate tasks if provided project is empty.
        task_ids_query_params = {
            'project': self.params['project'],
            'fields': 'id',
        }
        if self.params['task_filters']:
            task_ids_query_params.update(self.params['task_filters'])
        task_ids_generator, task_ids_count = client.list_tasks(params=task_ids_query_params, list_all=True)
        task_ids = [int(item.get('id', 0)) for item in task_ids_generator if isinstance(item, dict) and item.get('id')]

        # If no tasks found, break the job.
        if not task_ids_count:
            self.run.log_message('Tasks to annotate not found.')
            self.run.end_log()
            return {}

        # Annotate data to tasks.
        method = self.params.get('method')
        if method == AnnotationMethod.FILE:
            # Check if target specification name exists in file specifications.
            target_specification_name = self.params.get('target_specification_name')
            if not target_specification_name:
                self.run.log_message('Target specification name is required for file annotation method.')
                self.run.end_log()
                return {}

            file_specifications = data_collection.get('file_specifications', [])
            target_spec_exists = any(spec.get('name') == target_specification_name for spec in file_specifications)
            if not target_spec_exists:
                self.run.log_message(
                    f'Target specification name "{target_specification_name}" not found in file specifications'
                )
                self.run.end_log()
                return {}
            self._handle_annotate_data_from_files(task_ids, target_specification_name)
        elif method == AnnotationMethod.INFERENCE:
            self._handle_annotate_data_with_inference(task_ids)
        else:
            self.run.log_message(f'Unsupported annotation method: {method}')
            self.run.end_log()
            return {}

        return {}

    def _handle_annotate_data_from_files(self, task_ids: List[int], target_specification_name: str):
        """Handle annotate data from files to tasks.

        Args:
            task_ids (List[int]): List of task IDs to annotate data to.
            target_specification_name (str): The name of the target specification.
        """
        if not self.run or not self.params:
            raise ValueError('Run instance or parameters not properly initialized')

        # Type assertion to help the linter
        assert isinstance(self.run, ToTaskRun)
        assert isinstance(self.run.client, BackendClient)

        client: BackendClient = self.run.client
        task_params = {
            'fields': 'id,data,data_unit',
            'expand': 'data_unit',
        }

        total_tasks = len(task_ids)
        success_count = 0
        failed_count = 0
        current_progress = 0

        # Initialize metrics and progress
        self._update_metrics(total_tasks, success_count, failed_count)
        self.run.set_progress(0, total_tasks, category='annotate_task_data')
        self.run.log_message('Annotating data to tasks...')

        # Process each task
        for task_id in task_ids:
            try:
                result = self._process_single_task(
                    client, task_id, task_params, target_specification_name, AnnotationMethod.FILE
                )
                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1

                current_progress += 1
                self._update_metrics(total_tasks, success_count, failed_count)
                self.run.set_progress(current_progress, total_tasks, category='annotate_task_data')

            except Exception as e:
                self.run.log_message(f'Failed to process task {task_id}: {str(e)}')
                self.run.log_annotate_task_data({'task_id': task_id, 'error': str(e)}, AnnotateTaskDataStatus.FAILED)
                failed_count += 1
                current_progress += 1
                self._update_metrics(total_tasks, success_count, failed_count)
                self.run.set_progress(current_progress, total_tasks, category='annotate_task_data')

        # Finalize progress
        self.run.set_progress(total_tasks, total_tasks, category='annotate_task_data')
        self.run.log_message(f'Annotation completed. Success: {success_count}, Failed: {failed_count}')

    def _process_single_task(
        self,
        client: BackendClient,
        task_id: int,
        task_params: Dict[str, Any],
        target_specification_name: Optional[str],
        method: AnnotationMethod,
    ) -> Dict[str, Any]:
        """Process a single task for annotation.

        Args:
            client (BackendClient): The backend client instance.
            task_id (int): The task ID to process.
            task_params (Dict[str, Any]): Parameters for getting task data.
            target_specification_name (Optional[str]): The name of the target specification.
            method (AnnotationMethod): The annotation method to use.

        Returns:
            Dict[str, Any]: Result dictionary with 'success' boolean and optional 'error' message.
        """
        if not self.run:
            raise ValueError('Run instance not properly initialized')

        # Type assertion to help the linter
        assert isinstance(self.run, ToTaskRun)

        # Get task data
        task_response = client.get_task(task_id, params=task_params)
        if isinstance(task_response, str):
            error_msg = 'Invalid task response'
            self.run.log_message(f'{error_msg} received for task {task_id}')
            self.run.log_annotate_task_data({'task_id': task_id, 'error': error_msg}, AnnotateTaskDataStatus.FAILED)
            return {'success': False, 'error': error_msg}

        task: Dict[str, Any] = task_response

        if method == AnnotationMethod.FILE:
            if not target_specification_name:
                error_msg = 'Target specification name is required for file annotation method'
                self.run.log_message(f'{error_msg} for task {task_id}')
                self.run.log_annotate_task_data({'task_id': task_id, 'error': error_msg}, AnnotateTaskDataStatus.FAILED)
                return {'success': False, 'error': error_msg}
            return self._process_single_task_with_file(client, task_id, task, target_specification_name)
        elif method == AnnotationMethod.INFERENCE:
            return self._process_single_task_with_inference(client, task_id, task)
        else:
            error_msg = f'Unsupported annotation method: {method}'
            self.run.log_message(f'{error_msg} for task {task_id}')
            self.run.log_annotate_task_data({'task_id': task_id, 'error': error_msg}, AnnotateTaskDataStatus.FAILED)
            return {'success': False, 'error': error_msg}

    def _process_single_task_with_file(
        self, client: BackendClient, task_id: int, task: Dict[str, Any], target_specification_name: str
    ) -> Dict[str, Any]:
        """Process a single task for file-based annotation.

        Args:
            client (BackendClient): The backend client instance.
            task_id (int): The task ID to process.
            task (Dict[str, Any]): The task data.
            target_specification_name (str): The name of the target specification.

        Returns:
            Dict[str, Any]: Result dictionary with 'success' boolean and optional 'error' message.
        """
        if not self.run:
            raise ValueError('Run instance not properly initialized')

        # Type assertion to help the linter
        assert isinstance(self.run, ToTaskRun)

        # Extract data file information
        data_unit = task.get('data_unit', {})
        files = data_unit.get('files', {})
        data_file = files.get(target_specification_name)

        if not data_file:
            error_msg = 'File specification not found'
            self.run.log_message(f'{error_msg} for task {task_id}')
            self.run.log_annotate_task_data({'task_id': task_id, 'error': error_msg}, AnnotateTaskDataStatus.FAILED)
            return {'success': False, 'error': error_msg}

        url = data_file.get('url')
        if not url:
            error_msg = 'URL not found'
            self.run.log_message(f'{error_msg} for task {task_id}')
            self.run.log_annotate_task_data({'task_id': task_id, 'error': error_msg}, AnnotateTaskDataStatus.FAILED)
            return {'success': False, 'error': error_msg}

        # Fetch and process the data
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = json.loads(response.content)

            # Convert data to task object
            annotation_to_task = self.entrypoint(self.run)
            converted_data = annotation_to_task.convert_data_from_file(data)

            # Submit annotation data
            client.annotate_task_data(task_id, data={'action': 'submit', 'data': converted_data})

            # Log success
            self.run.log_annotate_task_data({'task_id': task_id, 'url': url}, AnnotateTaskDataStatus.SUCCESS)
            return {'success': True}

        except requests.RequestException as e:
            error_msg = f'Failed to fetch data from URL: {str(e)}'
            self.run.log_message(f'{error_msg} for task {task_id}')
            self.run.log_annotate_task_data({'task_id': task_id, 'error': error_msg}, AnnotateTaskDataStatus.FAILED)
            return {'success': False, 'error': error_msg}
        except json.JSONDecodeError as e:
            error_msg = f'Failed to parse JSON data: {str(e)}'
            self.run.log_message(f'{error_msg} for task {task_id}')
            self.run.log_annotate_task_data({'task_id': task_id, 'error': error_msg}, AnnotateTaskDataStatus.FAILED)
            return {'success': False, 'error': error_msg}

    def _process_single_task_with_inference(
        self, client: BackendClient, task_id: int, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single task for inference-based annotation.

        Args:
            client (BackendClient): The backend client instance.
            task_id (int): The task ID to process.
            task (Dict[str, Any]): The task data.

        Returns:
            Dict[str, Any]: Result dictionary with 'success' boolean and optional 'error' message.
        """
        if not self.run or not self.params:
            raise ValueError('Run instance or parameters not properly initialized')

        # Type assertion to help the linter
        assert isinstance(self.run, ToTaskRun)

        try:
            # Get pre-processor information
            pre_processor_id = self.params.get('pre_processor')

            if not pre_processor_id:
                error_msg = 'Pre-processor ID is required for inference annotation method'
                self.run.log_message(f'{error_msg} for task {task_id}')
                self.run.log_annotate_task_data({'task_id': task_id, 'error': error_msg}, AnnotateTaskDataStatus.FAILED)
                return {'success': False, 'error': error_msg}

            # Call inference pre processor if specified.
            pre_processor = client.get_plugin_release(pre_processor_id)
            pre_processor_code = pre_processor['config']['code']
            pre_processor_version = pre_processor['version']

            # Extract task data for inference
            data_unit = task.get('data_unit', {})
            files = data_unit.get('files', {})

            # Find primary image URL from files
            primary_file_url = ''
            for file_info in files.values():
                if file_info.get('is_primary') and file_info.get('url'):
                    primary_file_url = file_info['url']
                    break

            pre_processor_params = self.params.get('pre_processor_params', {})
            pre_processor_params['image_path'] = primary_file_url
            inference_payload = {
                'agent': 1,
                'action': 'inference',
                'version': pre_processor_version,
                'params': {
                    'model': self.params.get('model'),
                    'method': 'post',
                    'json': pre_processor_params,
                },
            }
            inference_data = client.run_plugin(pre_processor_code, inference_payload)

            # Convert data to task object
            annotation_to_task = self.entrypoint(self.run)
            converted_result = annotation_to_task.convert_data_from_inference(inference_data)

            # Submit inference annotation data
            client.annotate_task_data(task_id, data={'action': 'submit', 'data': converted_result})

            # Log success
            self.run.log_annotate_task_data(
                {'task_id': task_id, 'pre_processor_id': pre_processor_id}, AnnotateTaskDataStatus.SUCCESS
            )
            return {'success': True}

        except Exception as e:
            error_msg = f'Failed to process inference for task {task_id}: {str(e)}'
            self.run.log_message(error_msg)
            self.run.log_annotate_task_data({'task_id': task_id, 'error': error_msg}, AnnotateTaskDataStatus.FAILED)
            return {'success': False, 'error': error_msg}

    def _update_metrics(self, total_tasks: int, success_count: int, failed_count: int):
        """Update metrics for task annotation progress.

        Args:
            total_tasks (int): Total number of tasks to process.
            success_count (int): Number of successfully processed tasks.
            failed_count (int): Number of failed tasks.
        """
        if not self.run:
            raise ValueError('Run instance not properly initialized')

        # Type assertion to help the linter
        assert isinstance(self.run, ToTaskRun)

        metrics = self.run.MetricsRecord(
            stand_by=total_tasks - success_count - failed_count, failed=failed_count, success=success_count
        )
        self.run.log_metrics(metrics, 'annotate_task_data')

    def _handle_annotate_data_with_inference(self, task_ids: List[int]):
        """Handle annotate data with inference to tasks.

        Args:
            task_ids (List[int]): List of task IDs to annotate data to.
        """
        if not self.run or not self.params:
            raise ValueError('Run instance or parameters not properly initialized')

        if not self.params.get('model'):
            raise ValueError('Model is required for inference annotation method')

        # Type assertion to help the linter
        assert isinstance(self.run, ToTaskRun)
        assert isinstance(self.run.client, BackendClient)

        client: BackendClient = self.run.client
        task_params = {
            'fields': 'id,data,data_unit',
            'expand': 'data_unit',
        }

        total_tasks = len(task_ids)
        success_count = 0
        failed_count = 0
        current_progress = 0

        # Initialize metrics and progress
        self._update_metrics(total_tasks, success_count, failed_count)
        self.run.set_progress(0, total_tasks, category='annotate_task_data')
        self.run.log_message('Annotating data to tasks using inference...')

        # Process each task
        for task_id in task_ids:
            try:
                result = self._process_single_task(client, task_id, task_params, None, AnnotationMethod.INFERENCE)
                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1

                current_progress += 1
                self._update_metrics(total_tasks, success_count, failed_count)
                self.run.set_progress(current_progress, total_tasks, category='annotate_task_data')

            except Exception as e:
                self.run.log_message(f'Failed to process task {task_id}: {str(e)}')
                self.run.log_annotate_task_data({'task_id': task_id, 'error': str(e)}, AnnotateTaskDataStatus.FAILED)
                failed_count += 1
                current_progress += 1
                self._update_metrics(total_tasks, success_count, failed_count)
                self.run.set_progress(current_progress, total_tasks, category='annotate_task_data')

        # Finalize progress
        self.run.set_progress(total_tasks, total_tasks, category='annotate_task_data')
        self.run.log_message(f'Inference annotation completed. Success: {success_count}, Failed: {failed_count}')
