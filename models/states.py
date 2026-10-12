"""Класс State и функции работы со справочником состояний."""
from typing import List, Optional

from .base import Entity

WORKING = "working"
DECOMMISSIONED = "decommissioned"


class State(Entity):
    """Состояние оборудования: исправно, неисправно, в ремонте, списано."""

    def __init__(
        self,
        state_id: int,
        code: str,
        name: str,
        is_working: bool,
    ) -> None:
        """Создать объект состояния."""
        super().__init__(state_id)
        self.code = code
        self.name = name
        self.is_working = is_working

    @property
    def is_decommissioned(self) -> bool:
        """Признак состояния «списано»."""
        return self.code == DECOMMISSIONED

    @classmethod
    def from_data(cls, data: dict) -> "State":
        """Создать состояние из словаря данных JSON."""
        return cls(data["id"], data["code"], data["name"], data["is_working"])

    def to_dict(self) -> dict:
        """Вернуть данные состояния для сохранения в JSON."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "is_working": self.is_working,
        }

    def __str__(self) -> str:
        """Вернуть название состояния."""
        return self.name


def find_state_by_id(states: List[State], state_id: int) -> Optional[State]:
    """Найти состояние по идентификатору."""
    for state in states:
        if state.id == state_id:
            return state
    return None


def find_state_by_code(states: List[State], code: str) -> Optional[State]:
    """Найти состояние по коду (например, working)."""
    for state in states:
        if state.code == code:
            return state
    return None


def show_states(states: List[State]) -> None:
    """Вывести справочник состояний."""
    for state in states:
        mark = "можно устанавливать" if state.is_working else "нельзя"
        print(f"{state.id}. {state} — {mark}")
