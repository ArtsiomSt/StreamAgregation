from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def choices(cls) -> list:
        choices_list = []
        for member in cls._member_names_:
            current_choice = getattr(cls, member)
            choices_list.append((member, current_choice.value))
        return choices_list

    @classmethod
    def names(cls) -> list:
        member_names = []
        for member in cls._member_names_:
            current_choice = getattr(cls, member)
            member_names.append(current_choice.name)
        return member_names


class ObjectStatus(BaseEnum):
    PROCESSED = "processed"
    PENDING = "pending"
    CREATED = "created"
