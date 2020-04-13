from nfa import NFA


def green(inp: str) -> str:
    """Returns string in green color to print"""
    return "\033[92m" + inp + "\033[0m"


def red(inp: str) -> str:
    """Returns string in red color to print"""
    return "\033[91m" + inp + "\033[0m"


if __name__ == "__main__":
    try:
        nfa = file = None
        try:
            nfa = NFA(input("Enter the regexp: "))
            nfa.delete_regulars()
            file = open("nfa-input.txt", "w")
        except (KeyboardInterrupt, EOFError) as ex:
            print()
            exit()
        alphabet_file = open("nfa-alphabet.txt", "w")
        nfa.to_file(file, alphabet_file)
        print(green("Success"))
    except Exception as ex:
        for arg in ex.args:
            print(red(str(arg)))
