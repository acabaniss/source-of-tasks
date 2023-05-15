from sotasks import Task
import pytest
import datetime


@pytest.fixture
def basic_task():
    task = Task("Example Name", "Example Description\nMultiline")
    yield task


@pytest.fixture
def complex_task():
    task = Task(
        "Complex Name",
        "Complex Description\nMultiline",
        additional_properties={"key": "value"},
    )
    yield task


@pytest.fixture
def completed_task():
    task = Task("Completed Name", "Completed Description\nMultiline", completed=True)
    return task


@pytest.fixture
def explicit_date_task():
    task = Task(
        "Date Task",
        end_date=datetime.date(2015, 2, 3),
    )
    yield task


@pytest.fixture
def implicit_date_task():
    task = Task("Inferred Date Task", end_date="2015-02-03")
    yield task
