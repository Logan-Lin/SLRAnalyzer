from grammar import Grammar
from SLRAn import SLRAn, str2masks
from LexAn import split_input_string


class Main(SLRAn):
    """
    Main class inherited from SLRAn, used for a simple interactive user interface.
    """
    def __init__(self, grammar):
        SLRAn.__init__(self, grammar)

    def control(self):
        """
        Display main control(menu).
        """
        choice = -1
        while not choice == 0:
            print("loganlin@SLR1:# ", end='')
            choice = input()
            choice = choice.split(' ')

            if choice[0] == 'grammar':
                self.grammar.print_grammar(flat=True)
                print()
                self.grammar.print_follow()
                print()
            elif choice[0] == 'map':
                self.print_map()
                print()
            elif choice[0] == 'ps':
                self.print_ps_list()
                print()
                self.print_read_dict()
                print()
            elif choice[0] == 'an':
                if len(choice) < 2:
                    print('Please input the string to analysis after order an.')
                    continue
                input_string = ' '.join(choice[1:])
                try:
                    self.analysis(str2masks(split_input_string(input_string)))
                    print("Valid input string.")
                except (ValueError, KeyError) as e:
                    print("Invalid input string.\n", e)
                print()
            elif choice[0] == 'csv':
                file_name = 'map.csv'
                if len(choice) > 1:
                    file_name = choice[1]
                self.export_to_csv(file_name)
                print("Exported to {}".format(file_name), '\n')
            elif choice[0] == 'help':
                format_string = '\t{:15}{}'
                print(format_string.format('grammar', 'Print out grammar details'))
                print(format_string.format('ps', 'Print out project sets'))
                print(format_string.format('map', 'Print out analysis map'))
                print(format_string.format('csv <filename>', 'Export analysis map to csv file'))
                print(format_string.format('an <series>', 'Analysis series'))
                print(format_string.format('exit', 'Quit this program'))
            elif choice[0] == 'exit':
                exit(0)
            else:
                print('Invalid order, input help to see all orders')


if __name__ == '__main__':
    main = Main(Grammar('grammar.txt', 'txt_file'))
    main.control()
