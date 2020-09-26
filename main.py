import sys


class Processor:
    cmd_memory = [0 for _ in range(20)]
    data_memory = [0 for _ in range(20)]
    reg_memory = [0 for _ in range(4)]
    label_memory = [0 for _ in range(20)]
    program_memory = ['' for _ in range(20)]

    def __init__(self):
        self.pc = 0
        self.cmd_mode = ''

    def from_any_to_int(self, number: str) -> int:
        if number[-1] == 'h':
            return int(number[:-1], 16)
        elif number[-1] == 'b':
            return int(number[:-1], 2)
        elif number[-1] == 'o':
            return int(number[:-1], 8)
        else:
            return int(number)

    def data_converter(self, curr_cmd):
        print(f'{curr_cmd}')
        name = curr_cmd[0]
        if not ',' in curr_cmd[1]:
            ind = self.data_memory.index(0)
            if ind == -1:
                ind = 0
            data = self.from_any_to_int(curr_cmd[1])
            self.data_memory[ind] = data
            self.label_memory[ind] = name
        else:
            massiv = curr_cmd[1].split(',')
            ind = self.data_memory.index(0)
            if ind == -1:
                ind = 0
            for number in range(len(massiv)):
                self.data_memory[ind + number] = self.from_any_to_int(massiv[number])
            self.label_memory[ind] = name

    def append_zeros(self, s: str, m: int) -> str:
        if len(s) < m:
            t = ''.join('0' for _ in range(m - len(s)))
            return t + s
        else:
            return s

    def command_converter(self, curr_cmd):
        print(f'{curr_cmd}')
        cmd_type = curr_cmd[0]
        op1 = curr_cmd[1][:-1]
        op2 = curr_cmd[2]
        cmd_code = ''
        op1_code = ''
        op2_code = ''
        op1_value = ''
        op2_value = ''
        machine_code = ''

        # определение типа команды
        if cmd_type == 'mov':
            cmd_code = '0100'
        elif cmd_type == 'add':
            cmd_code = '0101'
            # etc

        # определение ПРИЕМНИКА
        if op1 in ['ax', 'bx', 'cx', 'dx']:
            # регистра
            op1_code = '00'
        elif op1[0] == '[':
            # адрес данных
            op1_code = '01'
        if op1_code == '':
            try:
                ind = op1.index('[')
                if op1 in self.label_memory or op1[:ind] in self.label_memory:
                    op1_code = '10'  # переменная
            except:
                op1_code = '10'

        # определение ИСТОЧНИКА
        if op2 in ['ax', 'bx', 'cx', 'dx']:
            # регистр
            op2_code = '00'
        elif op2[0] == '[':
            # адрес данных
            op2_code = '01'

        if op2_code == '':
            try:
                ind = op2.index('[')
                if op2 in self.label_memory or op2[:ind] in self.label_memory:
                    op2_code = '10'  # переменная
            except:
                # непосредственное значение
                op2_code = '11'

        # преобразование значение ПРЕМНИКА в бинарное значение
        if op1_code == '00':
            if op1 == 'ax':
                op1_value = '00000001'
            elif op1 == 'bx':
                op1_value = '00000010'
            elif op1 == 'cx':
                op1_value = '00000011'
            elif op1 == 'dx':
                op1_value = '00000100'
        elif op1_code == '01':
            data_address = format(self.from_any_to_int(op1[1:-1]), 'b')
            op1_value = self.append_zeros(data_address, 8)
        elif op1_code == '10':
            if '[' in op1:
                varname = op1[:ind]
                shift = op1[ind + 1:-1]
                if shift == 'ax':
                    shift = self.reg_memory[0]
                elif shift == 'bx':
                    shift = self.reg_memory[1]
                elif shift == 'cx':
                    shift = self.reg_memory[2]
                elif shift == 'dx':
                    shift = self.reg_memory[3]
                else:
                    shift = int(shift)
                address = self.label_memory.index(varname) + shift
                op1_value = self.append_zeros(format(self.data_memory[address], 'b'), 8)
            else:
                op1_value = self.append_zeros(format(self.data_memory[self.label_memory.index(op1)], 'b'), 8)

        # преобразование значение ИСТОЧНИКА в бинарное значение
        if op2_code == '00':
            if op2 == 'ax':
                op2_value = '00000001'
            elif op2 == 'bx':
                op2_value = '00000010'
            elif op2 == 'cx':
                op2_value = '00000011'
            elif op2 == 'dx':
                op2_value = '00000100'
        elif op2_code == '01':
            data_address = format(self.from_any_to_int(op2[1:-1]), 'b')
            op2_value = self.append_zeros(data_address, 8)
        elif op2_code == '10':
            if '[' in op2:
                varname = op2[:ind]
                shift = op2[ind + 1:-1]
                if shift == 'ax':
                    shift = self.reg_memory[0]
                elif shift == 'bx':
                    shift = self.reg_memory[1]
                elif shift == 'cx':
                    shift = self.reg_memory[2]
                elif shift == 'dx':
                    shift = self.reg_memory[3]
                else:
                    shift = int(shift)
                address = self.label_memory.index(varname) + shift
                op2_value = self.append_zeros(format(self.data_memory[address], 'b'), 8)
            else:
                op2_value = self.append_zeros(format(self.data_memory[self.label_memory.index(op2)], 'b'), 8)
        elif op2_code == '11':
            op2_value = self.append_zeros(format(self.from_any_to_int(op2), 'b'), 8)

        s = cmd_code + op1_code + op2_code + op1_value + op2_value
        machine_code = int(s, 2)
        self.cmd_memory[self.cmd_memory.index(0)] = machine_code

    def create_label(self, curr_cmd):
        label_name = curr_cmd[0][:-1]
        self.label_memory[self.label_memory.index(0)] = label_name

    def new_command_analyze(self, new_cmd: str):

        curr_cmd = new_cmd.split(' ')
        if curr_cmd[0] == '.data':
            self.cmd_mode = 'data'
            return
        elif curr_cmd[0] == '.code':
            self.cmd_mode = 'code'
            return
        elif ':' in curr_cmd[0]:
            self.create_label(curr_cmd)
            # self.cmd_memory[self.cmd_memory.index(0)] = int('001100000000000000000000', 2)
            return

        if self.cmd_mode == 'data':
            self.data_converter(curr_cmd)
            # ind = self.cmd_memory.index(0)
            # self.cmd_memory[ind] = int('000100000000000000000000', 2)
        elif self.cmd_mode == 'code':
            self.command_converter(curr_cmd)
            self.program_memory[self.program_memory.index('')] = new_cmd
            # self.cmd_memory[self.cmd_memory.index(0)] = int('001000000000000000000000', 2)

    def output_info(self):
        print('ADDRESS\tCOMMAND MEMORY\tLITERALLY COMMAND\tDATA MEMORY\tLABEL MEMORY')
        for i in range(len(self.cmd_memory)):
            print(
                f'{i}: {bin(self.cmd_memory[i])}\t{self.program_memory[i]}\t{bin(self.data_memory[i])}\t{self.label_memory[i]}')

        print('REGISTER MEMORY:')
        for i in range(len(self.reg_memory)):
            print(f'{i}: {bin(self.reg_memory[i])}')

    def execute_command(self, curr_cmd: int):
        curr_cmd_str = format(curr_cmd, 'b')
        if len(curr_cmd_str) < 24:
            tmp_str = ''.join(['0' for _ in range(24 - len(curr_cmd_str))])
            curr_cmd_str = tmp_str + curr_cmd_str

        cmd_type = curr_cmd_str[0:3]
        op1_type = curr_cmd_str[4:5]
        op2_type = curr_cmd_str[6:7]
        op1_value = curr_cmd_str[8:15]
        op2_value = curr_cmd_str[16:23]

        if cmd_type == '0100':  # mov
            if op1_type == '00':  # reg
                if op2_type == '00':  # reg
                    self.reg_memory[int(op1_value, 2)] = self.reg_memory[int(op2_value, 2)]
                elif op2_type == '01':  # data
                    self.reg_memory[int(op1_value, 2)] = self.data_memory[int(op2_value, 2)]
                elif op2_type == '10':  # literal
                    self.reg_memory[int(op1_value, 2)] = int(op2_value, 2)
            elif op1_type == '10':  #data
                if op2_type == '00':  # reg
                    self.data_memory[int(op1_value, 2)] = self.reg_memory[int(op2_value, 2)]
                elif op2_type == '01':  # data
                    self.data_memory[int(op1_value, 2)] = self.data_memory[int(op2_value, 2)]
                elif op2_type == '10':  # literal
                    self.data_memory[int(op1_value, 2)] = int(op2_value, 2)


def main(program):
    processor = Processor()
    for cmd in program:
        processor.new_command_analyze(cmd)
    processor.output_info()


if __name__ == '__main__':
    file_name = sys.argv[1]
    with open(file_name, 'r') as f:
        program = [line.strip() for line in f.readlines()]
        main(program)
