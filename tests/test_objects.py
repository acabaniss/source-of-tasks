import pytest
from sotasks import Task
import datetime
from zoneinfo import ZoneInfo


class GenericTaskClient(object):
    def __init__(self, id: int):
        self.id = id
        self.task_counter = 0

    def create(self, name: str) -> Task:
        """Create a new task"""
        task = Task(name, identifiers={self: self.task_counter})
        self.task_counter += 1
        return task


@pytest.fixture
def gtc1():
    gtc1 = GenericTaskClient(1)
    yield gtc1


@pytest.fixture
def gtc2():
    gtc2 = GenericTaskClient(2)
    yield gtc2


def test_basic_properties(basic_task):
    assert basic_task.name == "Example Name"
    assert basic_task.description == "Example Description\nMultiline"
    assert basic_task.completed is False


def test_complex_properties(complex_task):
    assert "key" in complex_task.additional_properties.keys()
    assert complex_task.additional_properties.get("key") == "value"


# status and compleness
def test_complete(completed_task):
    assert completed_task.completed


# dates
def test_dates_basic(explicit_date_task):
    assert explicit_date_task.end_date == datetime.date(2015, 2, 3)


def test_dates_inferred(implicit_date_task):
    assert implicit_date_task.end_date == datetime.date(2015, 2, 3)


# identifiers
def test_identifier_get(gtc1):
    task0 = gtc1.create("Task 0")
    assert task0.get_identifier(gtc1) == 0


def test_identifier_get_none(gtc1, gtc2):
    task0 = gtc1.create("Task 0")
    assert task0.get_identifier(gtc2) is None


def test_identifier_add(gtc1, gtc2):
    task0 = gtc1.create("Task 0")
    task0.add_identifier(gtc2, -1)
    assert task0.get_identifier(gtc2) == -1


def test_identifier_add_duplicate_error(gtc1):
    task0 = gtc1.create("Task 0")
    with pytest.raises(ValueError):
        task0.add_identifier(gtc1, -1)
