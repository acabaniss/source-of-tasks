from sotasks import AsanaTaskClient, Task
import pytest
import asana
from unittest.mock import MagicMock
from dotenv import load_dotenv
import os
import datetime


@pytest.fixture
def asana_client_integration(monkeypatch):
    load_dotenv("tests/integration.env")
    client = AsanaTaskClient(
        os.environ.get("ASANA_PERSONAL_ACCESS_TOKEN"),
        os.environ.get("ASANA_PROJECT_ID"),
    )
    yield client


@pytest.fixture
def asana_task_list(basic_task, complex_task, completed_task, explicit_date_task):
    task_list = [basic_task, complex_task, completed_task, explicit_date_task]
    yield task_list


@pytest.mark.integration
def test_confirm_failure():
    with pytest.raises(ValueError):
        _ = AsanaTaskClient("badtoken", os.environ.get("ASANA_PROJECT_ID"))


@pytest.mark.integration
def test_confirm_setup(asana_client_integration):
    assert asana_client_integration._check_token()
    assert asana_client_integration.project_id == os.environ.get("ASANA_PROJECT_ID")


@pytest.mark.integration
def test_import_tasks(asana_client_integration):
    task_list = asana_client_integration.import_tasks()
    assert all([isinstance(task, Task) for task in task_list])
    assert all(
        [
            task.get_identifier(asana_client_integration) is not None
            for task in task_list
        ]
    )


@pytest.mark.integration
def test_create_tasks(asana_client_integration, asana_task_list):
    asana_client_integration.create(asana_task_list)
    assert [
        task.get_identifier(asana_client_integration) is not None
        for task in asana_task_list
    ]


@pytest.mark.integration
def test_update_tasks(asana_client_integration):
    task_list_original = asana_client_integration.import_tasks()
    today = datetime.date.today()
    tasks_to_update = []
    for task in task_list_original:
        task.end_date = today
        tasks_to_update.append(task)
    asana_client_integration.update(tasks_to_update)
    task_list_new = asana_client_integration.import_tasks()
    assert all([task.end_date == today for task in task_list_new])
