from enum import Enum


def enum_to_choices(enum: Enum) -> list[tuple[str, str]]:
    return [(member.value, member.value) for member in enum]
