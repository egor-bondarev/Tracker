""" Helper strucutres for unit tests. """

from dataclasses import dataclass

@dataclass
class CreateUserResult:
    id: int
    username: str
