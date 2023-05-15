import asana
from .objects import Task
from typing import Optional, List, Any
import datetime
import warnings


class AsanaTaskClient(object):
    __static_mapping = {
        "name": "name",
        "notes": "description",
        "start_on": "start_date",
        "due_on": "end_date",
        "completed": "completed",
    }

    __dynamic_mapping = {
        "start_at": "start_date",
        "due_at": "end_date",
    }

    def __init__(self, access_token: str, project_id: str):
        self.client = asana.Client.access_token(access_token)
        # to avoid a deprecation warning, this header is requried
        self.client.headers = {
            "Asana-Enable": "new_goal_memberships,new_user_task_lists"
        }
        self._check_token()
        # define fields for mapping, although logic is handled in import
        # ignores time
        self.project_id = project_id

    def _check_token(self):
        try:
            _ = self.client.users.get_user("me")
            return True
        except asana.error.NoAuthorizationError as e:
            raise ValueError("Access token is invalid, please try again.")

    def import_tasks(
        self,
    ) -> List[Task]:
        # generate field list
        fields = list(self.__static_mapping.keys()) + list(
            self.__dynamic_mapping.keys()
        )
        asana_task_list = self.client.tasks.get_tasks(
            {
                "project": self.project_id,
                "opt_fields": fields,
                "options": {"limit": 100},  # improves performance
            }
        )
        task_list = []
        for asana_task in asana_task_list:
            _task = {}
            # do all static property mappings
            for k, v in self.__static_mapping.items():
                if k in asana_task.keys():
                    _task[v] = asana_task[k]
            _task["identifiers"] = {self: asana_task["gid"]}
            # TODO: fix time based mappings
            # ## start time
            # if asana_task.get("start_at") is not None:
            #     _task["start_date"] = asana_task["start_at"]
            # elif asana_task.get("due_on") is not None:
            #     _task["start_date"] = asana_task["start_on"]
            # ## end time
            # if asana_task.get("due_at") is not None:
            #     _task["end_date"] = asana_task["due_at"]
            # elif asana_task.get("due_on") is not None:
            #     _task["end_date"] = asana_task["due_on"]
            task_list.append(Task(**_task))
        return task_list

    def _task_to_asana(self, task: Task) -> dict[str, Any]:
        _asana_task = {k: getattr(task, v) for k, v in self.__static_mapping.items()}
        # fix datetimes
        _asana_task = {
            k: (
                v.isoformat()
                if isinstance(v, datetime.date) or isinstance(v, datetime.datetime)
                else v
            )
            for k, v in _asana_task.items()
        }
        # Handle a common Asana error with a Warning
        if "start_on" in _asana_task.keys() and "end_on" not in _asana_task.keys():
            warnings.warn(
                f"Asana requires both a start and an end time. Dropping `start_on` to resolve."
            )
            _ = _asana_task.pop("start_on")
        return _asana_task

    def _create_one(self, task: Task):
        if task.get_identifier(self) is not None:
            raise ValueError(f"Task {task} is already in {self}")
        _asana_task = self._task_to_asana(task)
        params = {"projects": [self.project_id], **_asana_task}
        created_task = self.client.tasks.create(params)
        task.add_identifier(self, created_task["gid"])

    def create(self, task_list: List[Task]):
        for task in task_list:
            self._create_one(task)

    def _update_one(self, task: Task) -> dict[str, Any]:
        """Update one task in Asana from this project."""
        _asana_task = self._task_to_asana(task)
        _asana_task = {k: v for k, v in _asana_task.items() if v is not None}
        gid = task.get_identifier(self)
        if gid is None:
            raise ValueError(
                f"Task {task} does not have an identifier for Asana {self}"
            )
        updated_task = self.client.tasks.update(gid, _asana_task)

    def update(self, task_list: List[Task]):
        """Update a list of tasks in Asana."""
        for task in task_list:
            self._update_one(task)
