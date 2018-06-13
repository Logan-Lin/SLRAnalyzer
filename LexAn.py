import re


def split_input_string(input_string):
    """
    Split input string into identifiers, symbols and numbers.

    :param input_string: str, input string representing an assignment statement,
        like 'A=B+C'.
    :return: list with each item containing split symbols, identifiers and numbers.
        All symbols will remain the same sequence with input string.
    """
    if not bool(re.compile('^[a-zA-Z0-9.*/+-=() ]+$').search(input_string)):
        raise ValueError("Input series contain symbols not in assignment statement.")
    return list(map(process_single, filter(len, re.findall(r"[\-+*/=()]|[\w]+", input_string))))


def process_single(word):
    """
    Process a single word, whether it's identifier, number or symbols.

    :param word: str, the word to process
    :return: str, the input
    """
    if word[0].isnumeric():
        try:
            int(word)
        except ValueError:
            raise ValueError("Expression {} not valid".format(word))
    return word
