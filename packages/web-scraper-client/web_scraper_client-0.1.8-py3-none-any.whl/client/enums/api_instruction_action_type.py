from enum import Enum


class ApiInstructionActionType(Enum):
    WAIT_FOR = 'wait_for'
    WAIT = 'wait'
    SCROLL = 'scroll'
    CLICK = 'click'
    FIND = 'find'
    INPUT = 'input'
