from project import get_init_ps, ProjectSet


class SLRMap:
    """
    SLR(1) grammar analysis map constructor.
    """

    def __init__(self, grammar):
        """
        :param grammar: Grammar object.
        """
        self.grammar = grammar

        # The total state count in this SLR map. Will increase in the process of SLR map construction.
        self.state_count = 0

        # List of valid project sets.
        self.ps_list = []

        # A dict containing symbol reading and project set transfer information.
        # The dict's format is (Original_ps, read_symbol) -> (Transfer_ps).
        self.read_dict = dict()

        self.construct_ps_list()
        self.map = self.construct_map()

    def construct_ps_list(self):
        """
        Construct all project set list.
        """
        # Init the first project set C0.
        init_ps = get_init_ps(self.grammar)
        self.ps_list.append(init_ps)
        self.state_count += 1

        # Use stack to process until there is no project set in move state.
        ps_stack = [init_ps]
        while len(ps_stack) > 0:
            stack_top = ps_stack[0]
            del ps_stack[0]
            state = stack_top.get_state()
            if state == ProjectSet.ProjectSetState.STATUTE:
                continue
            elif state == ProjectSet.ProjectSetState.MOVE or state == ProjectSet.ProjectSetState.BOTH:
                for read_symbol in stack_top.get_all_readable():
                    new_ps = stack_top.read(read_symbol, self.state_count)
                    if new_ps not in self.ps_list:
                        # new project set is not in ps list.
                        self.ps_list.append(new_ps)
                        self.state_count += 1
                        ps_stack.append(new_ps)
                    else:
                        # new project is already in ps list.
                        new_ps = self.ps_list[self.ps_list.index(new_ps)]
                    # Assign transfer information to read dict.
                    self.read_dict[(stack_top, read_symbol)] = new_ps

    def construct_map(self):
        """
        Construct SLR(1) analysis map.
        """
        map_matrix = []
        for i in range(len(self.ps_list)):
            map_matrix_row = [''] * len(self.grammar.symbols)
            ps = self.ps_list[i]
            state = ps.get_state()
            if state == ProjectSet.ProjectSetState.MOVE or state == ProjectSet.ProjectSetState.BOTH:
                for symbol in ps.get_all_readable():
                    transfer_ps = self.read_dict[(ps, symbol)]
                    map_matrix_row[self.grammar.get_symbol_index(symbol)] = 'S{}'.format(transfer_ps.index)
            if state == ProjectSet.ProjectSetState.BOTH or state == ProjectSet.ProjectSetState.STATUTE:
                statute_dict = ps.process_double()
                for project, input_symbol in statute_dict.items():
                    formula_index = self.grammar.get_formula_index(project.non_t, ' '.join(project.symbols))
                    for follow_symbol in input_symbol:
                        map_matrix_row[self.grammar.get_symbol_index(follow_symbol)] = 'R{}'.format(formula_index)
                        # if follow_symbol == '#' and formula_index == 0:
                        #     map_matrix_row[self.grammar.get_symbol_index(follow_symbol)] = 'Acc'
            map_matrix.append(map_matrix_row)
        map_matrix[0][self.grammar.get_symbol_index('#')] = 'Acc'
        return map_matrix

    def get_action(self, current_state, input_symbol):
        """
        Get next action based on current state and input symbol.

        :param current_state: int, current stack top state number.
        :param input_symbol: str, input symbol.
        :return: str, next action to take like 'S10' or 'R5'.
        """
        return self.map[current_state][self.grammar.get_symbol_index(input_symbol)]

    def print_ps_list(self):
        for ps in self.ps_list:
            print(ps)

    def print_read_dict(self, full=False):
        """
        Print out read dict information.

        :param full: bool, print all project sets' content or not.
        """
        for (original_ps, read_symbol), transfer_ps in self.read_dict.items():
            if full:
                print('{} {} -> {}'.format(str(original_ps), read_symbol, str(transfer_ps)))
            else:
                print('{:4}{:2} -> C{}'.format('C' + str(original_ps.index), read_symbol, transfer_ps.index))

    def print_map(self):
        """
        Print out SLR(1) analysis map.
        """
        format_string = '{:5}' * (len(self.grammar.symbols) + 1)
        print(format_string.format(*([''] + self.grammar.symbols)))
        for i in range(len(self.ps_list)):
            print(format_string.format(*(['S{}'.format(i)] + self.map[i])))
