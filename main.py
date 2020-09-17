import sys


class Processor:
    pc: int
    command_memory: list
    data_memory: list
    registers: list

    def __init__(self):
        self.pc = 0
        self.command_memory = []
        self.data_memory = []
        self.registers = [0 for i in range(4)]

    # 0000_0000 0000 0000 0000_0000_0000 HEX
    def append_command_and_data(self, new_command: str) -> bool:
        if len(new_command) == 7:
            self.command_memory.append(int(new_command[0], 16))
            self.data_memory.append(int(new_command[1:], 16))
            return True
        else:
            return False

    def load_commands(self, file_name):
        try:
            with open(file_name, 'r') as f:
                commands = f.readlines()
                for command in commands:
                    try:
                        command = command[:7]
                        self.append_command_and_data(new_command=''.join([i for i in command if i]))
                    except:
                        pass
        except FileNotFoundError:
            print(FileNotFoundError.strerror)

    def execute_command(self, command_address: int, register_address1: int, register_address2=None, literal_data=None):
        if self.command_memory[command_address] == 0:
            self.registers[register_address1] = literal_data if literal_data else self.registers[register_address2]
        elif self.command_memory[command_address] == 1:
            self.registers[register_address1] = self.registers[register_address1] + literal_data if literal_data else \
                self.registers[register_address1] + \
                self.registers[register_address2]
        elif self.command_memory[command_address] == 2:
            self.registers[register_address1] = self.registers[register_address1] - literal_data if literal_data else \
                self.registers[register_address1] - \
                self.registers[register_address2]

    def run(self):
        self.pc = 0

        while self.pc < len(self.command_memory):
            command_address = self.pc
            literal_data = (self.data_memory[self.pc] >> 8) & 65535
            register_address1 = (self.data_memory[self.pc] >> 4) & 15
            register_address2 = self.data_memory[self.pc] & 15
            self.execute_command(command_address=command_address, register_address1=register_address1,
                                 register_address2=register_address2, literal_data=literal_data)
            self.output_info()
            self.pc += 1

    def wipe_data(self):
        self.pc = 0
        self.command_memory = []
        self.data_memory = []
        self.registers = [0 for i in range(4)]

    def output_info(self):
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('COMMAND_MEMORY')
        for i in range(len(self.command_memory)):
            print(f'{i}: {hex(self.command_memory[i])}')
        print('DATA_MEMORY')
        for i in range(len(self.data_memory)):
            print(f'{i}: {hex(self.data_memory[i])}')
        print('REGISTERS')
        for i in range(len(self.registers)):
            print(f'{i}: {hex(self.registers[i])}')


def main():
    processor = Processor()
    print(sys.argv)
    if sys.argv[1]:
        processor.load_commands(str(sys.argv[1]))
    processor.output_info()
    while True:
        new_command = input('> ')
        if new_command == 'run':
            processor.run()
        elif new_command[:4] == 'load':
            processor.load_commands(new_command[5:])
            processor.output_info()
        elif new_command == 'wipe':
            processor.wipe_data()
            processor.output_info()
        else:
            processor.append_command_and_data(new_command=new_command)


if __name__ == '__main__':
    main()
