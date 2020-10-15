import os
import sys

from typing import Tuple

from prettytable import PrettyTable


class Processor:
    SIZE = 50
    cmd_memory = [0 for _ in range(SIZE)]
    data_memory = [0 for _ in range(SIZE)]
    reg_memory = [0 for _ in range(4)]  # max = 1111 1111 1111 1111 = 65535
    label_memory = ['0' for _ in range(SIZE)]
    variables_memory = [0 for _ in range(SIZE)]
    program_memory = ['' for _ in range(SIZE)]
    CF = 0
    regs = {'ax': '0000000000000000', 'ah': '0000000000000001', 'al': '0000000000000010',
            'bx': '0000000000000011', 'bh': '0000000000000100', 'bl': '0000000000000101',
            'cx': '0000000000000110', 'ch': '0000000000000111', 'cl': '0000000000001000',
            'dx': '0000000000001001', 'dh': '0000000000001010', 'dl': '0000000000001011'}

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

    def check_max(self, n: int) -> bool:
        return True if n < 65536 else False

    def original_or_overflow(self, n: int) -> int:
        if self.check_max(n):
            self.CF = 0
            return n
        else:
            self.CF = 1
            return abs(n-65536)

    def append_zeros(self, s: str, m: int) -> str:
        if len(s) < m:
            t = ''.join('0' for _ in range(m - len(s)))
            return t + s
        else:
            return s

    def data_converter(self, curr_cmd):
        name = curr_cmd[0]
        if not ',' in curr_cmd[1]:  # если обычная переменная
            ind = self.variables_memory.index(0)
            if ind == -1:
                ind = 0
            data = self.from_any_to_int(curr_cmd[1])
            self.data_memory[ind] = data
            self.variables_memory[ind] = name
        else:  # если массив
            massiv = curr_cmd[1].split(',')
            ind = self.data_memory.index(0)
            if ind == -1:
                ind = 0
            for number in range(len(massiv)):
                self.data_memory[ind +
                                 number] = self.from_any_to_int(massiv[number])
                self.variables_memory[ind + number] = name

    # получить тип операнда
    def get_operand_type(self, op: str) -> str:
        if '[' and ']' in op:   # ячейка памяти
            return '00'
        elif op in self.regs.keys():  # регистр
            return '01'
        elif op in self.variables_memory:  # адрес переменной
            return '10'
        else:
            return '11'  # непосредственное значение или метка

    # получить значение из конкретного регистра
    def get_register_value(self, op: str) -> int:
        if op == 'ax':
            return self.reg_memory[0]
        elif op == 'ah':
            return int(self.append_zeros(format(self.reg_memory[0], 'b'), 16)[:8], 2)
        elif op == 'al':
            return int(self.append_zeros(format(self.reg_memory[0], 'b'), 16)[8:], 2)
        elif op == 'bx':
            return self.reg_memory[1]
        elif op == 'bh':
            return int(self.append_zeros(format(self.reg_memory[1], 'b'), 16)[:8], 2)
        elif op == 'bl':
            return int(self.append_zeros(format(self.reg_memory[1], 'b'), 16)[8:], 2)
        elif op == 'cx':
            return self.reg_memory[2]
        elif op == 'ch':
            return int(self.append_zeros(format(self.reg_memory[2], 'b'), 16)[:8], 2)
        elif op == 'cl':
            return int(self.append_zeros(format(self.reg_memory[2], 'b'), 16)[8:], 2)
        elif op == 'dx':
            return self.reg_memory[3]
        elif op == 'dh':
            return int(self.append_zeros(format(self.reg_memory[3], 'b'), 16)[:8], 2)
        elif op == 'dl':
            return int(self.append_zeros(format(self.reg_memory[3], 'b'), 16)[8:], 2)

    # ставим новое значение в определенный регистр
    def set_register_value(self, reg_name: str, val: int):
        if reg_name == 'ax':
            self.reg_memory[0] = val
        elif reg_name == 'ah':
            h = self.append_zeros(format(val, 'b'), 8)
            l = self.append_zeros(format(self.reg_memory[0], 'b'), 16)[8:]
            self.reg_memory[0] = int(h + l, 2)
        elif reg_name == 'al':
            h = self.append_zeros(format(self.reg_memory[0], 'b'), 16)[:8]
            l = self.append_zeros(format(val, 'b'), 8)
            self.reg_memory[0] = int(h + l, 2)
        elif reg_name == 'bx':
            self.reg_memory[1] = val
        elif reg_name == 'bh':
            h = self.append_zeros(format(val, 'b'), 8)
            l = self.append_zeros(format(self.reg_memory[1], 'b'), 16)[8:]
            self.reg_memory[1] = int(h + l, 2)
        elif reg_name == 'bl':
            h = self.append_zeros(format(self.reg_memory[1], 'b'), 16)[:8]
            l = self.append_zeros(format(val, 'b'), 8)
            self.reg_memory[1] = int(h + l, 2)
        elif reg_name == 'cx':
            self.reg_memory[2] = val
        elif reg_name == 'ch':
            h = self.append_zeros(format(val, 'b'), 8)
            l = self.append_zeros(format(self.reg_memory[2], 'b'), 16)[8:]
            self.reg_memory[2] = int(h + l, 2)
        elif reg_name == 'cl':
            h = self.append_zeros(format(self.reg_memory[2], 'b'), 16)[:8]
            l = self.append_zeros(format(val, 'b'), 8)
            self.reg_memory[2] = int(h + l, 2)
        elif reg_name == 'dx':
            self.reg_memory[3] = val
        elif reg_name == 'dh':
            h = self.append_zeros(format(val, 'b'), 8)
            l = self.append_zeros(format(self.reg_memory[3], 'b'), 16)[8:]
            self.reg_memory[3] = int(h + l, 2)
        elif reg_name == 'dl':
            h = self.append_zeros(format(self.reg_memory[3], 'b'), 16)[:8]
            l = self.append_zeros(format(val, 'b'), 8)
            self.reg_memory[3] = int(h + l, 2)

    # анализ операнда
    def operand_analyze(self, op: str) -> list:
        op_type = self.get_operand_type(op)  # получение типа операнда
        if op_type == '00':  # если операнд - ячейка в памяти
            clear_op = op[1:-1]  # без [ и ]
            clear_op_type = self.get_operand_type(clear_op)
            if clear_op_type == '01':
                op_value = self.append_zeros(
                    format(self.get_register_value(clear_op), 'b'), 16)
            elif clear_op_type == '10':
                op_value = self.append_zeros(
                    format(self.variables_memory.index(clear_op), 'b'), 16)
            elif clear_op_type == '11':
                op_value = self.append_zeros(
                    format(self.from_any_to_int(clear_op), 'b'), 16)
        elif op_type == '01':  # регистр
            op_value = self.regs[op]
        elif op_type == '10':   # переменная
            op_value = self.append_zeros(
                format(self.variables_memory.index(op), 'b'), 16)
        else:
            if op in self.label_memory:
                op_value = self.append_zeros(
                    format(self.label_memory.index(op), 'b'), 16)   # вернуть индекс метки
            else:
                op_value = self.append_zeros(
                    format(self.from_any_to_int(op), 'b'), 16)  # непосредственное значение

        return [op_type, op_value]

    # преобразование строки ассемблера в машинный код
    def command_converter(self, curr_cmd):
        curr_cmd_list = curr_cmd  # [команда, операнд1, (операнд2)]
        if len(curr_cmd_list) == 3:  # если команда имеет два операнда
            # убираем запятую у первого операнда
            curr_cmd_list[1] = curr_cmd_list[1][:-1]
            operands = curr_cmd_list[1:]
        else:
            operands = [curr_cmd_list[1]]   # если команда имеет один операнд

        cmd_code = '0000'
        op_codes = [['00', '0000000000000000'],  # op1_type and op1_value
                    ['00', '0000000000000000']]  # op2_type and op2_value

        # определение кода команды
        if curr_cmd_list[0] == 'mov':
            cmd_code = '0001'
        elif curr_cmd_list[0] == 'add':
            cmd_code = '0010'
        elif curr_cmd_list[0] == 'adc':
            cmd_code = '0011'
        elif curr_cmd_list[0] == 'loop':
            cmd_code = '0100'
        elif curr_cmd_list[0] == 'mul':
            cmd_code = '0101'

        # анализ каждого операнда
        for op in range(len(operands)):
            op_codes[op] = self.operand_analyze(operands[op])

        op1 = op_codes[0]
        op2 = op_codes[1]

        # собираем всё в одну бинарную строку и кладем в память команд
        machine_code = cmd_code + op1[0] + op2[0] + op1[1] + op2[1]
        self.cmd_memory[self.pc] = int(machine_code, 2)

    # создаем новую метку с индексом текущей команды
    def create_label(self, curr_cmd):
        label_name = curr_cmd[:-1]
        self.label_memory[self.pc] = label_name

    # анализ новой команды
    def new_command_analyze(self, new_cmd: str):
        curr_cmd = new_cmd.split(' ')
        if curr_cmd[0] == '.data':  # ставим режим анализа данных
            self.cmd_mode = 'data'
            self.pc += 1
            return
        elif curr_cmd[0] == '.code':    # ставим режим анализа кода
            self.cmd_mode = 'code'
            self.pc += 1
            return
        elif ':' in curr_cmd[0]:    # или создаем метку
            self.create_label(curr_cmd[0])
            self.pc += 1
            return

        if self.cmd_mode == 'data':
            self.data_converter(curr_cmd)   # анализируем данные в секции .data
            self.pc += 1
        elif self.cmd_mode == 'code':   # анализируем код в секции .code
            self.command_converter(curr_cmd)
            self.program_memory[self.pc] = new_cmd
            # и сразу же выполняем команду
            self.execute_command(self.cmd_memory[self.pc])
            self.pc += 1

    # функция отображения данных
    def output_info(self):
        table = PrettyTable()
        table.field_names = ['ADDRESS', 'COMMAND MEMORY', 'LITERALLY COMMAND', 'DATA MEMORY', 'VARIABLES MEMORY',
                             'LABEL MEMORY']
        for i in range(len(self.program_memory)):
            table.add_row(
                [i, int(self.cmd_memory[i]), self.program_memory[i], int(self.data_memory[i]), self.variables_memory[i],
                 self.label_memory[i]])
        print(table)

        table1 = PrettyTable()
        table1.field_names = ['ADDRESS', 'REGISTER MEMORY']
        regs = ['ax', 'bx', 'cx', 'dx']
        for i in range(len(self.reg_memory)):
            table1.add_row([regs[i], bin(self.reg_memory[i])])
        print(table1)

        table2 = PrettyTable()
        table2.field_names = ['CF']
        table2.add_row([self.CF])
        print(table2)

    # возвращаем значение ИСТОЧНИКА
    def source_value_definition(self, op_type, op_value) -> int:
        if op_type == '00':
            source_value = self.data_memory[int(op_value, 2)]
        elif op_type == '01':
            regs_reverse = {v: k for k, v in self.regs.items()}
            source_value = self.get_register_value(regs_reverse[op_value])
        elif op_type == '10':
            source_value = int(op_value, 2)
        elif op_type == '11':
            source_value = int(op_value, 2)
        return source_value

    # команда MOV
    def mov(self, op1_type, op1_value, op2_type, op2_value):
        source_value = self.source_value_definition(op2_type, op2_value)

        if op1_type == '00':
            self.data_memory[int(op1_value, 2)] = source_value
        elif op1_type == '01':
            regs_reverse = {v: k for k, v in self.regs.items()}
            self.set_register_value(regs_reverse[op1_value], source_value)

    # команда ADD
    def add(self, op1_type, op1_value, op2_type, op2_value):
        source_value = self.source_value_definition(op2_type, op2_value)

        if op1_type == '00':
            self.data_memory[int(op1_value, 2)] += source_value
        elif op1_type == '01':
            regs_reverse = {v: k for k, v in self.regs.items()}
            s1 = self.original_or_overflow(self.get_register_value(
                regs_reverse[op1_value]) + source_value)
            self.set_register_value(regs_reverse[op1_value], s1)

    # команда ADC
    def adc(self, op1_type, op1_value, op2_type, op2_value):
        source_value = self.source_value_definition(op2_type, op2_value)

        if op1_type == '00':
            self.data_memory[int(op1_value, 2)] += source_value
        elif op1_type == '01':
            regs_reverse = {v: k for k, v in self.regs.items()}
            s1 = self.get_register_value(
                regs_reverse[op1_value]) + source_value + self.CF
            self.set_register_value(regs_reverse[op1_value], s1)

    # команда LOOP
    def loop(self, op1_value):
        self.reg_memory[2] -= 1
        if self.label_memory[int(op1_value, 2)] != '0' and self.reg_memory[2] != 0:
            self.pc = int(op1_value, 2)
        else:
            return

    # команда MUL
    def mul(self, op1_type, op1_value):
        regs_reverse = {v: k for k, v in self.regs.items()}
        reg = regs_reverse[op1_value]
        if reg[-1] == 'h' or reg[-1] == 'l':
            v1 = self.get_register_value('al')
            v2 = self.get_register_value(reg)
            self.reg_memory[0] = v1 * v2
            self.CF = 0 if self.get_register_value('ah') == 0 else 1
        elif reg[-1] == 'x':
            v1 = self.get_register_value('ax')
            v2 = self.get_register_value(reg)
            result = self.append_zeros(format(v1 * v2, 'b'), 32)
            result_dx = result[:16]
            result_ax = result[16:]
            self.reg_memory[0] = int(result_ax, 2)
            self.reg_memory[3] = int(result_dx, 2)
            self.CF = 0 if self.get_register_value('dx') == 0 else 1

    # выполненить определенную команду
    def execute_command(self, curr_cmd: int):
        curr_cmd_bin = self.append_zeros(format(curr_cmd, 'b'), 40)

        # разбиваем на части
        cmd_type = curr_cmd_bin[:4]
        op1_type = curr_cmd_bin[4:6]
        op2_type = curr_cmd_bin[6:8]
        op1_value = curr_cmd_bin[8:24]
        op2_value = curr_cmd_bin[24:40]

        # и выполняем
        if cmd_type == '0001':
            self.mov(op1_type, op1_value, op2_type, op2_value)
        elif cmd_type == '0010':
            self.add(op1_type, op1_value, op2_type, op2_value)
        elif cmd_type == '0011':
            self.adc(op1_type, op1_value, op2_type, op2_value)
        elif cmd_type == '0100':
            self.loop(op1_value)
        elif cmd_type == '0101':
            self.mul(op1_type, op1_value)


def main(program):
    processor = Processor()
    processor.program_memory = program.copy()
    while len(processor.program_memory) < processor.SIZE:
        processor.program_memory.append('')
    while processor.pc < len(processor.program_memory):
        if processor.program_memory[processor.pc] == '':
            break
        processor.new_command_analyze(processor.program_memory[processor.pc])

    processor.output_info()


if __name__ == '__main__':
    file_name = 'cmd.txt'
    full_path = os.path.dirname(os.path.abspath(__file__)) + '\\' + file_name
    with open(full_path, 'r') as f:
        program = [line.strip() for line in f.readlines()]
        main(program)
