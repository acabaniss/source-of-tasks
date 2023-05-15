import datetime
from typing import Optional, Union, Any
from dateutil import parser


class Task(object):
    def __init__(
        self,
        name: str,
        description: Optional[str] = "",
        start_date: Optional[Union[datetime.date, str]] = None,
        end_date: Optional[Union[datetime.date, str]] = None,
        completed: Optional[bool] = False,
        additional_properties: Optional[dict] = {},
        identifiers: Optional[dict] = {},
    ):
        self.name = name
        self.description = description
        if isinstance(start_date, str):
            self.start_date = parser.parse(start_date).date()
        else:
            self.start_date = start_date
        if isinstance(end_date, str):
            self.end_date = parser.parse(end_date).date()
        else:
            self.end_date = end_date
        self.completed = completed
        self.additional_properties = {}
        self.additional_properties.update(additional_properties)
        self.identifiers = {}
        self.identifiers.update(identifiers)

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=", ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    def complete(self):
        self.completed = True

    def add_identifier(self, system: Any, id: Any):
        if system in self.identifiers.keys():
            raise ValueError(f"An Identifier is already present for {system}")
        else:
            self.identifiers[system] = id

    def get_identifier(self, system: Any):
        if system in self.identifiers.keys():
            return self.identifiers[system]
        else:
            return None
