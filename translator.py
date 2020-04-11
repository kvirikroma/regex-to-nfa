from enum import Enum
from typing import List


class Operator(Enum):
    star = "*"
    union = "+"
    concat = "&"


class ParsedRegexp:
    def __init__(self, left: str, operator: Operator, right: str = None):
        if operator.name == "star":
            if right:
                raise ValueError('Operator("*") cannot have right operand')
            elif not left:
                raise ValueError('Operator("*") must have left operand')
        elif not right or not left:
            raise ValueError('Operator("' + Operator.value + '") must have both operands')
        self.left = left
        self.operator = operator
        self.right = right


def regex_to_parts(regex: str) -> List[str]:
    regex_symbols = list(regex)
    depth = 0
    regexp_parts = list()
    part_beginning = 0
    for i in range(len(regex_symbols)):
        if regex_symbols[i] == '(':
            if depth == 0:
                part_beginning = i
            depth += 1
            continue
        if regex_symbols[i] == ')':
            depth -= 1
            if depth < 0:
                print(regex)
                raise ValueError("Invalid brackets detected")
            if depth == 0:
                regexp_parts.append(regex[part_beginning:(i+1)])
            continue
        if depth == 0:
            regexp_parts.append(regex[i])
    for i in regexp_parts:
        if i in ("()", ""):
            try:
                regexp_parts.remove(i)
            except ValueError:
                pass
    if len(regexp_parts) == 1:
        if regexp_parts[0][0] == '(' and regexp_parts[0][-1] == ')':
            regexp_parts[0] = regexp_parts[0][1:-1]
        if len(regexp_parts[0]) > 1:
            return regex_to_parts(regexp_parts[0])
    return regexp_parts


def parts_to_action(regex_parts: List[str]) -> ParsedRegexp:
    operation = -1
    for i in ("+", "&", "*"):
        if operation == -1:
            try:
                operation = regex_parts.index(i)
            except ValueError:
                pass
    if operation == -1:
        raise ValueError("Cannot find operators in " + str().join(regex_parts))
    return ParsedRegexp(
        str().join(regex_parts[:operation]),
        Operator(regex_parts[operation]),
        str().join(regex_parts[(operation+1):])
    )


def parse_regexp(regex: str) -> ParsedRegexp:
    return parts_to_action(regex_to_parts(regex))
