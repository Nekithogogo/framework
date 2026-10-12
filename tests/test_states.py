from models import State
from models.states import find_state_by_code, find_state_by_id


def make_states() -> list[State]:
    return [
        State(1, "working", "Исправно", True),
        State(4, "decommissioned", "Списано", False),
    ]


def test_state_creation():
    state = State(1, "working", "Исправно", True)
    assert state.id == 1
    assert state.is_working
    assert not state.is_decommissioned
    assert str(state) == "Исправно"


def test_state_from_data():
    data = {"id": 4, "code": "decommissioned", "name": "Списано",
            "is_working": False}
    state = State.from_data(data)
    assert state.is_decommissioned
    assert state.to_dict() == data


def test_find_state():
    states = make_states()
    assert find_state_by_id(states, 4) is states[1]
    assert find_state_by_code(states, "working") is states[0]
    assert find_state_by_id(states, 9) is None
