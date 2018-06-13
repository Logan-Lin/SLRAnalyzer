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
            print('====SLR(1)文法分析与四元式生成====')
            print('0-退出')
            print('1-查看文法')
            print('2-查看分析矩阵')
            print('3-查看有效项目集族')
            print('4-分析输入串，生成四元式')
            try:
                choice = int(input('选择功能：'))
            except ValueError:
                continue

            if choice == 1:
                self.grammar.print_grammar(flat=True)
                print()
                self.grammar.print_follow()
                print()
            elif choice == 2:
                self.print_map()
                print()
            elif choice == 3:
                self.print_ps_list()
                print()
                self.print_read_dict()
                print()
            elif choice == 4:
                input_string = input("键入输入串：")
                try:
                    self.analysis(str2masks(split_input_string(input_string)))
                    print("有效的输入串。")
                except (ValueError, KeyError) as e:
                    print("无效的输入串，具体原因：\n", e)
                print()


if __name__ == '__main__':
    main = Main(Grammar('grammar.txt', 'txt_file'))
    main.control()
