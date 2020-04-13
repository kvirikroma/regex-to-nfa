from typing import Dict, List, TextIO
from translator import parse_regexp
from random import choice


def generate_random_string(length: int) -> str:
    letters = 'abcdefghijklmnopqrstuvwxyz'
    letters += letters.upper()
    result = str()
    for i in range(length):
        result += choice(letters)
    return result


class State:
    def __init__(self, name: str, transitions: Dict[str, str] = None, lambdas: List[str] = None):
        self.name = name
        self.transitions = transitions if transitions else dict()
        self.lambdas = lambdas if lambdas else list()

    def __getitem__(self, item: str):
        return self.transitions[item]

    def __setitem__(self, key: str, value: str):
        self.transitions[key] = value

    def __delitem__(self, key: str):
        del self.transitions[key]

    def contains_regex(self) -> str or None:
        for i in self.transitions:
            if len(i) != 1:
                return i


class NFA:
    def __init__(self, regex: str):
        regex = regex.replace("|", "+")
        self.alphabet = list(set(regex.replace("(", "").replace(")", "").replace("+", "").replace("*", "").replace("&", "")))
        self.alphabet.sort()
        regex_items = regex.replace("(", ".").replace(")", ".").replace("+", ".").replace("*", ".").replace("&", ".").split('.')
        for item in regex_items:
            if len(item) >= 1:
                regex = regex.replace('*'+item, "*&"+item)
            if len(item) >= 2:
                regex = regex.replace(item, "&".join(item))
        regex = regex.replace("*(", "*&(").replace(")(", ")&(")
        for letter in self.alphabet:
            regex = regex.replace(letter+'(', letter+"&(").replace(')'+letter, ")&"+letter)
        self.map = dict()
        self.map["end"] = State("end")
        self.map["$start"] = State("$start", {regex: "end"})

    def __getitem__(self, item: str):
        return self.map[item]

    def __setitem__(self, key: str, value: 'State'):
        self.map[key] = value

    def __delitem__(self, key):
        del self.map[key]

    def delete_regulars(self, state: str = "$start"):
        while self[state].contains_regex():
            transition = self[state].contains_regex()
            action = parse_regexp(transition)
            if action.operator.name == 'union':
                self[state][action.left] = self[state][transition]
                self[state][action.right] = self[state][transition]
                del self[state][transition]
                if len(action.left) != 1:
                    self.delete_regulars(state)
                if len(action.right) != 1:
                    self.delete_regulars(state)
            if action.operator.name == 'concat':
                while True:
                    new_name = generate_random_string(5)
                    if not self.map.get(new_name):
                        break
                self[new_name] = State(new_name)
                self[new_name][action.right] = self[state][transition]
                self[state][action.left] = new_name
                del self[state][transition]
                if len(action.left) != 1:
                    self.delete_regulars(state)
                if len(action.right) != 1:
                    self.delete_regulars(new_name)
            if action.operator.name == 'star':
                while True:
                    new_name_left = generate_random_string(5)
                    if not self.map.get(new_name_left):
                        break
                while True:
                    new_name_right = generate_random_string(5)
                    if not self.map.get(new_name_right):
                        break
                self[new_name_left] = State(new_name_left, {action.left: new_name_right})
                self[new_name_right] = State(new_name_right, dict(), [self[state][transition], new_name_left])
                self[state].lambdas.append(self[state][transition])
                self[state].lambdas.append(new_name_right)
                del self[state][transition]
                if len(action.left) != 1:
                    self.delete_regulars(new_name_left)

    def to_file(self, file: TextIO, alphabet_file: TextIO):
        file.write("TRANSITIONS\n\n")
        for state in self.map:
            file.write(state + '\t' + ('1' if state == 'end' else '0') + '\t')
            for letter in self.alphabet:
                file.write((self[state][letter] if self[state].transitions.get(letter) else "null") + ' ')
            file.write('\n')
        file.write("\nLAMBDAS\n\n")
        for state in self.map:
            if not self[state].lambdas:
                continue
            file.write(state + "\t")
            for lambda_transition in self[state].lambdas:
                file.write(lambda_transition + ' ')
            file.write('\n')
        alphabet_file.write(' '.join(self.alphabet))
