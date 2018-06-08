from SLRMap import SLRMap


class SLRAn(SLRMap):
    """
    SLR analyzer.
    """
    def __init__(self, grammar):
        SLRMap.__init__(self, grammar)

        self.step = 0

    def analysis(self, input_series):
        """
        Use SLR to analysis input series.

        :param input_series: list, containing symbols of input series.
        :raise: ValueError when current state and input symbol don't match any action in analysis map.
        """
        global step_str, symbol_stack_str, state_stack_str, input_series_str, action_str
        step_str, symbol_stack_str, state_stack_str, input_series_str, action_str = [], [], [], [], []

        self.step = 0
        symbol_stack = ['#']
        state_stack = [0]
        input_series.append('#')

        while True:
            # Get the top of state stack and its corresponding project set.
            top_state_num = state_stack[-1]

            # Pop in the first symbol of input series.
            input_symbol = input_series[0]

            action = self.get_action(top_state_num, input_symbol)
            if action == 'Acc':
                action = 'R0'
            if len(action) == 0:
                self.print_stack(symbol_stack, state_stack, input_series, action, True)
                raise ValueError("Current state {} and input symbol {} don't match any action in analysis map."
                                 .format(top_state_num, input_symbol))
            self.print_stack(symbol_stack, state_stack, input_series, action)
            if action[0] == 'S':
                symbol_stack.append(input_symbol)
                del input_series[0]
                state_stack.append(int(action[1:]))
            if action[0] == 'R':
                formula = self.grammar.formula_list[int(action[1:])]
                formula_length = len(formula[1].split(' '))
                del state_stack[-formula_length:]
                del symbol_stack[-formula_length:]

                if int(action[1:]) == 0 and input_symbol == '#':
                    self.print_stack(symbol_stack, state_stack, input_series, 'Acc', True)
                    return

                non_t = formula[0]
                goto = int(self.get_action(state_stack[-1], non_t)[1:])
                state_stack.append(goto)
                symbol_stack.append(non_t)

    def print_stack(self, symbol_stack, state_stack, input_series, action, print_out=False):
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
        step_str.append(str(self.step))
        symbol_stack_str.append(''.join(symbol_stack))
        state_stack_str.append(' '.join(str(x) for x in state_stack))
        input_series_str.append(''.join(input_series))
        action_str.append(action)

        if print_out:
            # Use the max length of all strings to format.
            format_string = '{{:{}}}{{:{}}}{{:{}}}{{:{}}}{{}}'.\
                format(6, len(max(state_stack_str, key=len)) + 2,
                       len(max(symbol_stack_str, key=len)) + 2,
                       len(max(input_series_str, key=len)) + 2)
            for i in range(self.step + 1):
                print(format_string.format(step_str[i], state_stack_str[i], symbol_stack_str[i],
                                           input_series_str[i], action_str[i]))
