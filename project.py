from copy import copy
from enum import Enum
from collections import Counter


class Project:
    """
    Class Project is a presentation of project in LR and SLR analysis.
    """
    def __init__(self, non_t, symbols, pos=0):
        """
        Initial this project with non-terminal symbol and formula symbols.
        Initial state will be A->.BCD.

        :param non_t: str, this project's non-terminal symbol.
        :param symbols: list, containing this project's formula symbols.
        """
        self.non_t = non_t
        self.symbols = symbols
        self.pos = pos
        self.length = len(symbols)

    def __eq__(self, other) -> bool:
        """
        Only when non-terminal symbol, formula symbols and current position are all same
        can we say that the two Project instance is same.
        """
        return self.non_t == other.non_t and self.symbols == other.symbols and self.pos == other.pos

    def __str__(self) -> str:
        symbols = copy(self.symbols)
        symbols.insert(self.pos, '.')
        return '{}->{}'.format(self.non_t, ''.join(symbols))

    def __hash__(self) -> int:
        return hash((self.non_t, tuple(self.symbols), self.pos))

    def get_state(self):
        """
        Get project's current state.

        :return: ProjectState, presenting project's current state.
        """
        if self.pos == self.length:
            if self.symbols[-1] == '#':
                return self.ProjectState['ACC']
            else:
                return self.ProjectState['STATUTE']
        elif self.length == 1 and self.pos == 0 and self.symbols[0] == 'e':
            return self.ProjectState['STATUTE']
        else:
            if self.symbols[self.pos].isupper():
                return self.ProjectState['WAIT']
            else:
                return self.ProjectState['MOVE']

    def get_next(self):
        """
        Get project current position's next symbol to move in.

        :return:
        """
        if self.can_move():
            return self.symbols[self.pos]
        else:
            raise ValueError('Project is already in statute or accept state, don not have next symbol')

    def advance(self):
        """
        Advance this project's dot position for one bit.
        """
        if self.can_move():
            self.pos += 1
            return self
        else:
            raise ValueError('Project is already in statute or accept state, cannot be advanced.')

    def can_move(self):
        """
        Check if the project can be move in.

        :return: bool, true if project can be move in.
        """
        return not (self.get_state() == self.ProjectState.ACC or self.get_state() == self.ProjectState.STATUTE)

    class ProjectState(Enum):
        """
        Project's different states.
        """
        STATUTE = 1,  # Statute project, like A->E+T.
        ACC = 2,  # Accept project, like S->A#.
        MOVE = 3,  # Move in project, like E->E.+T
        WAIT = 4  # Wait for statute project, like E->E+.T


class ProjectSet:
    """
    Valid project set.
    """
    def __init__(self, grammar, project_list, index, do_closure=True):
        """
        :param grammar: Grammar object, used for closure operation.
        :param project_list: list, initial project list containing Project objects.
        :param index: int, the index of this project set.
        :param do_closure: bool, do a closure operation in initialization or not.
        """
        self.grammar = grammar
        self.project_list = project_list
        self.index = index

        # Will do a closure operation in initialization in default, don't have to do it manually.
        if do_closure:
            self.closure()

    def __eq__(self, other) -> bool:
        """
        When comparing two ProjectSets, index is not counted.
        """
        return Counter(self.project_list) == Counter(other.project_list)

    def __str__(self) -> str:
        result = 'C{}: {{'.format(self.index)
        for p in self.project_list:
            result += str(p)
            if self.project_list.index(p) != len(self.project_list) - 1:
                result += ', '
        result += '}'
        return result

    def __hash__(self) -> int:
        return hash(tuple(self.project_list))

    def get_state(self):
        """
        Get current project set state.

        :return: ProjectSetState, presenting current project set's state.
        """
        move_count = 0
        statute_count = 0
        for p in self.project_list:
            state = p.get_state()
            if state == Project.ProjectState.STATUTE or state == Project.ProjectState.ACC:
                statute_count +=1
            else:
                move_count += 1
        if statute_count == 1 and move_count == 0:
            return self.ProjectSetState.STATUTE
        elif statute_count == 0 and move_count > 0:
            return self.ProjectSetState.MOVE
        else:
            return self.ProjectSetState.BOTH

    def closure(self):
        """
        Process closure operation.
        """
        changed = True  # Indicate whether there are new Projects added.
        while changed:
            changed = False
            for p in self.project_list:
                if p.get_state() == Project.ProjectState.WAIT:
                    non_t = p.get_next()
                    for formula in self.grammar.get_all_formulas(non_t):
                        new_project = Project(non_t, formula.split(' '))
                        if new_project not in self.project_list:
                            changed = True
                            self.project_list.append(new_project)
        return self

    def read(self, symbol, new_index=-1):
        """
        Process read operation.

        :param symbol: the symbol to read
        :param new_index: int, new project set's index
        :return: a new ProjectSet instance.
        :raise: ValueError when there are no Project who can read the given symbol
            or project set is in statute state.
        """
        new_project_list = []
        if self.get_state() != self.ProjectSetState.STATUTE:
            for p in self.project_list:
                if p.get_state() == Project.ProjectState.WAIT or p.get_state() == Project.ProjectState.MOVE:
                    if p.get_next() == symbol:
                        new_project_list.append(copy(p).advance())
        else:
            raise ValueError("Project set is in statute state, can't perform read operation.")
        if len(new_project_list) > 0:
            return ProjectSet(self.grammar, new_project_list, new_index)
        else:
            raise ValueError("There are no Project who can read the given symbol.")

    def get_all_readable(self):
        """
        Return a list containing all next symbol in project set.

        :return: list, containing all next symbol in project set that can use to perform read operation.
        """
        result = []
        if self.get_state() != self.ProjectSetState.STATUTE:
            for p in self.project_list:
                if p.get_state() == Project.ProjectState.WAIT or p.get_state() == Project.ProjectState.MOVE:
                    result.append(p.get_next())
        return result

    def process_double(self):
        """
        Function specially designed for project set which are in 'BOTH' or 'STATUTE' state.

        :return: dict, covering all projects in statute state,
            each item in 'Project -> input_symbol' format.
        :raise: ValueError when project set is not in BOTH state, which is not applicable to use this function.
        """
        result = dict()
        all_symbols = set(self.get_all_readable())
        for p in self.project_list:
            if p.get_state() == Project.ProjectState.STATUTE:
                follow_set = self.grammar.follow_dict[p.non_t]
                if not all_symbols.isdisjoint(follow_set):
                    raise ValueError("Find same next symbol between statute projects and move in projects.")
                all_symbols |= follow_set
                result[p] = follow_set
        return result

    class ProjectSetState(Enum):
        """
        Project set's different states.
        """
        STATUTE = 1,
        MOVE = 2,
        BOTH = 3  # There are both statute projects and move in projects or multiple statute projects in project set.


def get_init_ps(grammar):
    """
    Get a grammar's initial project set.

    :param grammar: Grammar object.
    :return: ProjectSet object, given grammar's initial project set.
    """
    project_list = []
    start_symbol = grammar.start_symbol
    for formula in grammar.get_all_formulas(start_symbol):
        project_list.append(Project(start_symbol, formula.split(' ')))
    return ProjectSet(grammar, project_list, 0)
