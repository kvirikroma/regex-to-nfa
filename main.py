from nfa import NFA


def green(inp: str) -> str:
    """Returns string in green color to print"""
    return "\033[92m" + inp + "\033[0m"


def red(inp: str) -> str:
    """Returns string in red color to print"""
    return "\033[91m" + inp + "\033[0m"


if __name__ == "__main__":
    #try:
        nfa = NFA(input("Enter the regexp: "))
        nfa.delete_regulars("$start")
        file = open(input("Enter the file name for NFA config: "), "w")
        alphabet_file = open(input("Enter the file name for alphabet: "), "w")
        nfa.to_file(file, alphabet_file)
        print(green("Success!"))
    #except Exception as ex:
    #    for arg in ex.args:
    #        print(red(str(arg)))
