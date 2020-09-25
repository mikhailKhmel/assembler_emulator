import sys

class Processor:
    cmd_memory = [0 for i in range(20)]
    data_memory = [0 for i in range(20)]
    reg_memory = [0 for i in range(4)]
    label_memory = [0 for i in range(20)]

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
                self.data_memory[ind+number] = self.from_any_to_int(massiv[number])
            self.label_memory[ind] = name
                
    def command_converter(self, curr_cmd):
        print(f'{curr_cmd}')
        cmd_type = curr_cmd[0]
        op1 = curr_cmd[1]
        op2 = curr_cmd[2]
        cmd_code = ''
        op1_code = ''
        op2_code = ''
        op1_value = ''
        op2_value = ''
        machine_code = ''

        # определение типа команды
        if cmd_type == 'mov':
            cmd_code ='0100'
        elif cmd_type == 'add':
            cmd_code ='0101'
            #etc
        
        # определение ПРИЕМНИКА
        if op1 in ['ax,','bx,', 'cx,', 'dx,']:
            # регистра
            op1_code ='00'
        elif '[' in op1:
            # адрес данных
            op1_code ='01'
        elif op1[:-1] in self.label_memory:
            # метка
            op1_code ='10'
        
        # определение ИСТОЧНИКА
        if op2 in ['ax','bx', 'cx', 'dx']:
            # регистр
            op2_code ='00'
        elif '[' in op2:
            # адрес данных
            op2_code ='01'
        else:
            # непосредственное значение
            op2_code ='10'

        # преобразование значение ПРЕМНИКА в бинарное значение
        if op1_code == '00':
            if op1 == 'ax,':
                op1_value = '00000001'
            elif op1 == 'bx,':
                op1_value = '00000010'
            elif op1 == 'cx,':
                op1_value = '00000011'
            elif op1 == 'dx,':
                op1_value = '00000100'
        elif op1_code == '01':
            data_address = format(self.from_any_to_int(op1[1:-2]), 'b')
            if len(data_address) < 8:
                tmp_str = ''.join(['0' for i in range(8 - len(data_address))])
                data_address = tmp_str + data_address
            op1_value = data_address
        elif op1_code == '10':
            data_value = format(self.from_any_to_int(op1), 'b')

            if len(data_value) < 8:
                tmp_str = ''.join(['0' for i in range(8 - len(data_value))])
                data_value = tmp_str + data_value
            op1_value = data_value

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
            if len(data_address) < 8:
                tmp_str = ''.join(['0' for i in range(8 - len(data_address))])
                data_address = tmp_str + data_address
            op2_value = data_address
        elif op2_code == '10':
            data_value = format(self.from_any_to_int(op2), 'b')

            if len(data_value) < 8:
                tmp_str = ''.join(['0' for i in range(8 - len(data_value))])
                data_value = tmp_str + data_value
            op2_value = data_value
        
        machine_code = int(cmd_code + op1_code + op2_code + op1_value + op2_value)
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
            self.cmd_memory[self.cmd_memory.index(0)] = int('001100000000000000000000',2)
            return
# TODO: выяснить почему такие длинные получаютсяк команды

        if self.cmd_mode == 'data':
            self.data_converter(curr_cmd)
            ind = self.cmd_memory.index(0)
            self.cmd_memory[ind] = int('000100000000000000000000', 2)
        elif self.cmd_mode == 'code':
            self.command_converter(curr_cmd)
            self.cmd_memory[self.cmd_memory.index(0)] = int('001000000000000000000000', 2)
                
    def output_info(self):
        print('ADDRESS\tCOMMAND MEMORY\tDATA MEMORY\tLABEL MEMORY')
        for i in range(len(self.cmd_memory)):
            print(f'{i}: {hex(self.cmd_memory[i])}\t{hex(self.data_memory[i])}\t{self.label_memory[i]}')
        
        print('REGISTER MEMORY:')
        for i in range(len(self.reg_memory)):
            print(f'{i}: {hex(self.reg_memory[i])}')

def main(programm):
    processor = Processor()
    for cmd in programm:
        processor.new_command_analyze(cmd)
        processor.output_info()

if __name__ == '__main__':
    file_name = sys.argv[1]
    with open(file_name, 'r') as f:
        programm = [line.strip() for line in f.readlines()]
        main(programm)

