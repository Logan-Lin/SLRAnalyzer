import pandas as pd


def init_grammar(file, method="csv_file"):
    """
    Create grammar data frame using different inputs.

    :param file: file directory or string list, based on what method to use. If method is "csv_file",
        'file' should be file directory of grammar csv file; if method is "txt_file",
        'file' should be file directory of grammar plain text file; if method is "text",
        'file' should be string list with every line contains one grammar formula.
    :param method: str, used to distinguish three different grammar initialization methods.
        Can be 'csv_file', 'txt_file' or 'text'.
    :return: pandas data frame, containing grammar details.
    """
    if method == "csv_file":
        return pd.read_csv(file, delimiter='`', index_col=0)
    index = []
    grammar_matrix = []
    if method == "txt_file":
        with open(file, "r") as txt_file:
            for line in txt_file.read().splitlines():
                if len(line) == 2:
                    continue
                non_t, formulas = line.split("->")
                non_t = non_t.strip()
                for formula in formulas.split('|'):
                    formula = formula.strip()
                    index.append(non_t)
                    grammar_matrix.append(formula)
    elif method == "text":
        for line in file:
            non_t, formulas = line.split("->")
            for formula in formulas.split('|'):
                index.append(non_t)
                grammar_matrix.append(formula)
    return pd.DataFrame(grammar_matrix, index=index, columns=["formula"])


class Grammar:
    """
    Grammar class representing a grammar.
    """
    def __init__(self, file, method, start_symbol=None):
        """
        :param file: file directory or string list, based on what method to use. If method is "csv_file",
            'file' should be file directory of grammar csv file; if method is "txt_file",
            'file' should be file directory of grammar plain text file; if method is "text",
            'file' should be string list with every line contains one grammar formula.
        :param method: str, used to distinguish three different grammar initialization methods.
            Can be 'csv_file', 'txt_file' or 'text'.
        """
        grammar = init_grammar(file, method)
        self.grammar = grammar
        self.non_ts = grammar[~grammar.index.duplicated(keep='first')].index

        # first_dict is a python dict used to store FIRST(a) array corresponding to one non-terminal symbol and formula.
        # The dict's form is (non-terminal, formula) -> FIRST(a) list.
        self.first_dict = dict()

        # follow_dict is a python dict used to store FOLLOW(A) array.
        # The dict's form is non-terminal -> FOLLOW(a) set.
        self.follow_dict = dict()

        self.construct_first()

        if start_symbol is None:
            start_symbol = grammar.index[0]
        self.start_symbol = start_symbol
        self.construct_follow(start_symbol)

        self.formula_list, self.symbols = self.get_symbol_formula_list()

    def __str__(self):
        result = []
        for non_t in self.non_ts:
            formulas = self.get_all_formulas(non_t)
            result.append("{0:2}-> {1:}".format(non_t, "|".join(list(formulas))))
        return '\n'.join(result)

    def get_all_formulas(self, non_t):
        """
        Returns all formulas corresponding to the specified non-terminal symbol.

        :param non_t: string, the non-terminal symbol.
        :return: list or pandas Series, all formulas corresponding to the specified non-terminal symbol
        """
        formulas = self.grammar.loc[non_t]
        formulas = formulas["formula"]
        if type(formulas).__name__ == "str":
            # If there is only one formula corresponding to the non-terminal symbol,
            # the returned 'formulas' could be string object.
            # Considering we have to traverse 'formulas', we turn it to a list here.
            formulas = [formulas]
        return formulas

    def get_symbol_formula_list(self):
        """
        :return: list, containing grammar's all formula, each item in (non_t, formula) format.
        """
        formulas = []
        symbols = {'#'}
        for non_t in self.non_ts:
            symbols.add(non_t)
            for formula in self.get_all_formulas(non_t):
                formulas.append((non_t, formula))
                symbols |= set(formula.split(' '))
        return formulas, list(sorted(symbols))

    def get_formula_index(self, non_t, formula_str):
        """
        :param non_t: str, non-terminal symbol in the formula.
        :param formula_str: str, formula content.
        :return: int, formula non_t->formula_str's position in formula list.
        """
        return self.formula_list.index((non_t, formula_str))

    def get_symbol_index(self, symbol):
        """
        Returns the index of given symbol in this grammar's symbol list.

        :param symbol: str, the symbol to search index for.
        :return: int, the index of symbol.
        """
        return self.symbols.index(symbol)

    def construct_first(self):
        """
        Construct all non-terminal symbols and formulas' FIRST(a) array.
        """
        for non_t in self.non_ts:
            self.get_first(non_t)

        for non_t in self.non_ts:
            self.append_first(non_t)

    def print_first(self):
        """
        Print out all formulas' first(a) set.
        """
        print('{0:15}{1:}'.format("Formula", "First(a)"))
        for (non_t, formula), first in self.first_dict.items():
            print('{0:2}-> {1:10}{{{2:}}}'.format(non_t, formula, ", ".join(sorted(first))))
        print()

    def construct_follow(self, start_symbol='S'):
        """
        Construct all non-terminal symbols' FOLLOW(A) array.

        :param start_symbol: string, the start symbol of the grammar.
        """
        for non_t in self.non_ts:
            self.get_follow(non_t, start_symbol)

        for i in range(len(self.non_ts)):
            for non_t in self.non_ts:
                self.append_follow(non_t)

    def print_follow(self):
        """
        Print out all non-terminal symbols' follow(A) set.
        """
        print('{:3}{}'.format('', 'FOLLOW(A)'))
        for non_t, follow in self.follow_dict.items():
            print('{:3}{{{}}}'.format(non_t, ", ".join(sorted(follow))))
        print()

    def get_first(self, non_t, first_index=0):
        """
        Get a non-terminal symbols' all FIRST(a) array.
        Insert every formula's FIRST(a) into first_dict in the same time.

        :param non_t: str, non-terminal symbol.
        :param first_index: int, the index to fetch the first symbol.
            Used to skip non-terminal symbols that can be inferred to empty.
        :return: set, the non-terminal symbol's all FIRST(a) array.
        """
        # List 'first' is used to store the non-terminal symbol's all FIRST(a) array.
        first = set()
        for formula in self.get_all_formulas(non_t):
            # List 'formula_first' is used to store formula's FIRST(a) array.
            formula_first = set()
            formula_list = formula.split(" ")
            try:
                first_sym = formula_list[first_index]
            except IndexError:
                continue
            if first_sym.isupper():
                if 'e' in list(self.get_all_formulas(first_sym)):
                    # If the first symbol can be inferred to empty.
                    first |= self.get_first(non_t, first_index=first_index + 1)
                    formula_first |= self.get_first(non_t, first_index=first_index + 1)
                if not first_sym == non_t:
                    # The first symbol of formula is an upper character, which means it is an non-terminal symbol.
                    # In this case, we recursively search for corresponding FIRST(a) array.
                    first |= self.get_first(first_sym)
                    formula_first |= self.get_first(first_sym)
            else:
                # The first symbol is not an upper character, which means it is an terminal symbol.
                # In this case, we directory store the symbol into array.
                first.add(first_sym)
                formula_first.add(first_sym)
            # Insert formula's FIRST(a) into the dict.
            try:
                self.first_dict[(non_t, formula)] |= formula_first
            except KeyError:
                # The first_dict corresponding to this formula is not set before.
                self.first_dict[(non_t, formula)] = formula_first
        return first

    def append_first(self, non_t):
        """
        An add-on to get_first, focus in dealing with left-recursive grammar.

        :param non_t: str, non-terminal symbol.
        """
        for formula in self.get_all_formulas(non_t):
            first_sym = formula.split(" ")[0]
            if first_sym.isupper() and first_sym == non_t:
                self.first_dict[(non_t, formula)] |= self.get_first(first_sym)

    def get_follow(self, non_t, start_symbol='S'):
        """
        Get a non-terminal symbols' all FOLLOW(A) array.
        Insert every non-terminals' FOLLOW(A) array into follow_dict in the same time.
        Noted that this follow set only considers 'Ab' or 'AB' situation,
        in which b is add to follow(A) and first(B) is add to follow(A).

        :param non_t: str, non-terminal symbol.
        :param start_symbol: str, the start symbol of the grammar.
        :return: The non-terminal symbol's all FOLLOW(a) array.
        """
        follow = set()
        for non_terminal in self.non_ts:
            for formula in self.get_all_formulas(non_terminal):
                formula_list = formula.split(" ")
                if non_t in formula_list:
                    # The specified non-terminal symbol is in formula, then get the index of the symbol.
                    index = formula_list.index(non_t)
                    if not index == len(formula_list) - 1:
                        if formula_list[index + 1].isupper():
                            # If the follow of the symbol is an non-terminal-symbol,
                            # add the follow symbol's FIRST(A) to its follow set.
                            follow |= self.get_first(formula_list[index + 1])
                        else:
                            # If the follow of the symbol is an terminal-symbol,
                            # directory add that symbol to its FOLLOW set.
                            follow.add(formula_list[index + 1])
        follow -= {'e'}
        if non_t == start_symbol:
            follow.add('#')
        self.follow_dict[non_t] = follow
        return follow

    def append_follow(self, non_t):
        """
        An add-on to get_follow, focus on two situation: 'B->...A', and 'B->...AC, C->e',
        in which follow(B) is add to follow(A).

        :param non_t: str, non_terminal symbol.
        """
        for non_terminal in self.non_ts:
            for formula in self.get_all_formulas(non_terminal):
                formula_list = formula.split(" ")
                if non_t in formula_list:
                    index = formula_list.index(non_t)
                    if index == len(formula_list) - 1:
                        if not non_t == non_terminal:
                            # If the symbol is in the end of the formula,
                            # then add all FOLLOW(A) to the symbol's FOLLOW set.
                            try:
                                self.follow_dict[non_t] |= self.follow_dict[non_terminal]
                            except KeyError:
                                continue
                    elif formula_list[index + 1].isupper():
                        if 'e' in list(self.get_all_formulas(formula_list[index + 1])) \
                                and index == len(formula_list) - 2:
                            # If the follow of the symbol is the end of the formula and can be inferred to empty,
                            # add the formula's corresponding non-terminal symbol's FOLLOW()
                            # to the symbol's FOLLOW set.
                            try:
                                self.follow_dict[non_t] |= self.follow_dict[non_terminal]
                            except KeyError:
                                continue

    def print_grammar(self, flat=False):
        """
        Print out grammar formulas.

        :param flat: bool, set to true to display grammar in flat mode.
        """
        if flat:
            for i in range(len(self.formula_list)):
                print("R{}: {}->{}".format(i, self.formula_list[i][0], self.formula_list[i][1]))
        else:
            print(str(self) + '\n')
