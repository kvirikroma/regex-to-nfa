from typing import Dict, TextIO, Set
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
    def __init__(self, name: str, transitions: Dict[str, Set[str]] = None, lambdas: Set[str] = None):
        self.name = name
        self.transitions = transitions if transitions else dict()
        self.lambdas = lambdas if lambdas else set()

    def __getitem__(self, item: str) -> Set[str]:
        return self.transitions[item]

    def __setitem__(self, key: str, value: Set[str]):
        self.transitions[key] = value

    def __delitem__(self, key: str):
        del self.transitions[key]

    def contains_regex(self) -> str or None:
        for i in self.transitions:
            if len(i) != 1:
                return i


class NFA:
    def __init__(self, regex: str):
        regex = regex.replace("|", "+").replace(" ", "")
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
        self.map["$start"] = State("$start", {regex: {"end"}})

    def __getitem__(self, item: str) -> State:
        return self.map[item]

    def __setitem__(self, key: str, value: 'State'):
        self.map[key] = value

    def __delitem__(self, key):
        del self.map[key]

    def generate_new_name(self):
        while True:
            new_name = generate_random_string(5)
            if not self.map.get(new_name):
                break
        return new_name

    def delete_regulars(self, state: str = "$start"):
        while self[state].contains_regex():
            transition = self[state].contains_regex()
            action = parse_regexp(transition)
            if action.operator.name == 'union':
                if not self[state].transitions.get(action.left):
                    self[state][action.left] = set()
                self[state][action.left].update(self[state][transition])
                if not self[state].transitions.get(action.right):
                    self[state][action.right] = set()
                self[state][action.right].update(self[state][transition])
                del self[state][transition]
                if len(action.left) != 1:
                    self.delete_regulars(state)
                if len(action.right) != 1:
                    self.delete_regulars(state)
            if action.operator.name == 'concat':
                new_name = self.generate_new_name()
                self[new_name] = State(new_name)
                if not self[new_name].transitions.get(action.right):
                    self[new_name][action.right] = set()
                self[new_name][action.right].update(self[state][transition])
                if not self[state].transitions.get(action.left):
                    self[state][action.left] = set()
                self[state][action.left].add(new_name)
                del self[state][transition]
                if len(action.left) != 1:
                    self.delete_regulars(state)
                if len(action.right) != 1:
                    self.delete_regulars(new_name)
            if action.operator.name == 'star':
                new_name_left = self.generate_new_name()
                while True:
                    new_name_right = self.generate_new_name()
                    if new_name_right != new_name_left:
                        break
                self[new_name_left] = State(new_name_left, {action.left: {new_name_right}})
                self[new_name_right] = State(new_name_right, dict(), {new_name_left})
                self[new_name_right].lambdas.update(self[state][transition])
                self[state].lambdas.update(self[state][transition])
                self[state].lambdas.add(new_name_left)
                del self[state][transition]
                if len(action.left) != 1:
                    self.delete_regulars(new_name_left)

    def to_file(self, file: TextIO, alphabet_file: TextIO):
        file.write("TRANSITIONS\n\n")
        for state in self.map:
            file.write(state + '\t' + ('1' if state == 'end' else '0') + '\t')
            string_to_append = str()
            for letter in self.alphabet:
                if self[state].transitions.get(letter):
                    new_part = str(self[state][letter]).replace(',', '').replace("'", '')
                else:
                    new_part = "null"
                if new_part.find(' ') == -1 and new_part.find('\t') == -1:
                    new_part = new_part.rstrip('}').lstrip('{')
                string_to_append += new_part + ' '
            file.write(string_to_append.rstrip("null ") + '\n')
        file.write("\nLAMBDAS\n\n")
        for state in self.map:
            if not self[state].lambdas:
                continue
            file.write(state + "\t")
            for lambda_transition in self[state].lambdas:
                file.write(lambda_transition + ' ')
            file.write('\n')
        alphabet_file.write(' '.join(self.alphabet))
