from SLRMap import SLRMap
from grammar import get_formula_type, FormulaType


class Mask:
    """
    Class for representing variables with outer and inner representation.

    For example, any identifier or integer in this grammar will be present as 'i' to the SLR analyzer,
    but when generating quaternary, we still need to know the identifier's name or integer's value.
    After i is stated into non-terminal symbols, it will be present as non-terminal symbol itself to analyzer,
    but we need to remember the value it contains.
    """
    def __init__(self, inner, outer):
        """
        :param inner: Inner presentation, such as identifier 'a' or integer '10'.
        :param outer: Outer presentation, such as terminal symbol 'i' or non-terminal symbol 'E'.
        """
        self.inner = inner
        self.outer = outer

    def __str__(self):
        if len(self.outer) == 0:
            return '_'
        elif len(self.inner) == 0:
            return self.outer
        else:
            return '{}<{}>'.format(self.outer, self.inner)


def str2masks(input_series):
    """
    Turn raw input into mask list.

    :param input_series: list, containing symbols of raw inputs.
    :return: list, with Mask objects as items.
    """
    result = []
    for symbol in input_series:
        if symbol[0].isalpha() or symbol.isdigit():
            result.append(Mask(symbol, 'i'))
        elif len(symbol) == 1 and symbol in '+-/*()=':
            result.append(Mask('', symbol))
        else:
            raise ValueError('Input symbol {} not valid'.format(symbol))
    return result


def gen(symbol, s1, s2, s3):
    """
    Generate one quaternary formula.

    :param symbol: Mask object
    :param s1: Mask object
    :param s2: Mask object
    :param s3: Mask object
    """
    result = '(' + symbol.outer
    for s in [s1, s2, s3]:
        result += ','
        if len(s.outer) == 0:
            result += '_'
        else:
            result += s.inner
    result += ')'
    return result


class SLRAn(SLRMap):
    """
    SLR analyzer.
    """
    def __init__(self, grammar):
        SLRMap.__init__(self, grammar)

        self.step = 0
        self.temp_num = 0

    def analysis(self, input_series):
        """
        Use SLR to analysis input series.

        :param input_series: list, containing symbols of input series, which items are Mask objects.
        :raise: ValueError when current state and input symbol don't match any action in analysis map.
        """
        global step_str, symbol_stack_str, state_stack_str, input_series_str, action_str, quat_str
        step_str, symbol_stack_str, state_stack_str, input_series_str, action_str, quat_str = [], [], [], [], [], []

        self.step = 0
        self.temp_num = 0
        symbol_stack = [Mask('', '#')]
        state_stack = [0]
        input_series.append(Mask('', '#'))

        while True:
            # Get the top of state stack and its corresponding project set.
            top_state_num = state_stack[-1]

            # Pop in the first symbol of input series.
            input_symbol = input_series[0]

            action = self.get_action(top_state_num, input_symbol.outer)
            if action == 'Acc':
                action = 'R0'
            if len(action) == 0:
                self.print_stack(symbol_stack, state_stack, input_series, action, '', True)
                raise ValueError("Current state {} and input symbol {} don't match any action in analysis map."
                                 .format(top_state_num, input_symbol.outer))
            if action[0] == 'S':
                self.print_stack(symbol_stack, state_stack, input_series, action)

                symbol_stack.append(input_symbol)
                del input_series[0]
                state_stack.append(int(action[1:]))
            if action[0] == 'R':
                formula = self.grammar.formula_list[int(action[1:])]
                formula_length = len(formula[1].split(' '))

                non_t_inner = ''
                quat = ''
                formula_type = get_formula_type(formula[1])
                if formula_type == FormulaType.ENTRY or formula_type == FormulaType.SINGLE:
                    non_t_inner = symbol_stack[-1].inner
                elif formula_type == FormulaType.BRACKET:
                    non_t_inner = symbol_stack[-2].inner
                elif formula_type == FormulaType.BIN:
                    self.temp_num += 1
                    temp = Mask('T{}'.format(self.temp_num), 'i')
                    quat = gen(symbol_stack[-2], symbol_stack[-3], symbol_stack[-1], temp)
                    non_t_inner = temp.inner
                elif formula_type == FormulaType.EQUAL:
                    quat = gen(symbol_stack[-2], symbol_stack[-1], Mask('', ''), symbol_stack[-3])

                self.print_stack(symbol_stack, state_stack, input_series, action, quat)

                del state_stack[-formula_length:]
                del symbol_stack[-formula_length:]

                if int(action[1:]) == 0 and input_symbol.outer == '#':
                    self.print_stack(symbol_stack, state_stack, input_series, 'Acc', '', True)
                    return

                non_t = Mask(non_t_inner, formula[0])
                goto = int(self.get_action(state_stack[-1], non_t.outer)[1:])
                state_stack.append(goto)
                symbol_stack.append(non_t)

    def print_stack(self, symbol_stack, state_stack, input_series, action, quat='', print_out=False):
        """
        Print out current stack state.
        For format need, information will only print out to console when print_out is set to true.
        """
        self.step += 1
        if self.step == 1:
            step_str.append('Step')
            symbol_stack_str.append('Symbol stack')
            state_stack_str.append('State stack')
            input_series_str.append('Input series')
            action_str.append('Action')
            quat_str.append('Quat')
        step_str.append(str(self.step))
        symbol_stack_str.append(''.join(str(z) for z in symbol_stack))
        state_stack_str.append(' '.join(str(x) for x in state_stack))
        input_series_str.append(''.join(str(y) for y in input_series))
        action_str.append(action)
        quat_str.append(quat)

        if print_out:
            # Use the max length of all strings to format.
            format_string = '{{:{}}}{{:{}}}{{:{}}}{{:{}}}{{:{}}}{{}}'.\
                format(6, len(max(state_stack_str, key=len)) + 2,
                       len(max(symbol_stack_str, key=len)) + 2,
                       len(max(input_series_str, key=len)) + 2,
                       len(max(action_str, key=len)) + 2)
            for i in range(self.step + 1):
                print(format_string.format(step_str[i], state_stack_str[i], symbol_stack_str[i],
                                           input_series_str[i], action_str[i], quat_str[i]))