"""Класс Characteristic — характеристика оборудования."""


class Characteristic:
    """Параметр оборудования: название, значение и единица измерения.

    Характеристика не имеет собственного идентификатора: она существует
    только в составе оборудования и хранится вместе с ним.
    """

    def __init__(self, name: str, value: str, unit: str = "") -> None:
        """Создать характеристику."""
        self.name = name
        self.value = value
        self.unit = unit

    @classmethod
    def from_data(cls, data: dict) -> "Characteristic":
        """Создать характеристику из словаря данных JSON."""
        return cls(data["name"], data["value"], data.get("unit", ""))

    def to_dict(self) -> dict:
        """Вернуть данные характеристики для сохранения в JSON."""
        return {"name": self.name, "value": self.value, "unit": self.unit}

    def __str__(self) -> str:
        """Вернуть характеристику в виде «Объем: 32 ГБ»."""
        return f"{self.name}: {self.value} {self.unit}".rstrip()
