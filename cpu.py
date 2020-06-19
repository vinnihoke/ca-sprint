"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    '''
    TERMINOLOGY
    * `SP`: Stack pointer. Address 244 if stack is empty
    * `PC`: Program Counter, address of the currently executing instruction
    * `IR`: Instruction Register, contains a copy of the currently executing instruction
    * `MAR`: Memory Address Register, holds the memory address we're reading or writing
    * `MDR`: Memory Data Register, holds the value to write or the value just read
    * `FL`: Flags, see below
    '''

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # Bytes of memory
        self.reg = [0] * 8 # Registers
        self.pc = 0 # Program Counter
        self.sp = self.reg[7] # Stack pointer. Address 244 if stack is empty
        self.reg[7] = 0xF4
        self.greaterThan = 0
        self.lessThan = 0
        self.equals = 0
        self.running = False
        self.operand_a = 0
        self.operand_b = 0

        self.branch_table = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100000: self.ADD,
            0b10000100: self.ST,
            0b01010100: self.JMP,
            0b10100111: self.CMP,
            0b01010110: self.JNE,
            0b01010101: self.JEQ,
            0b01001000: self.PRA,
            0b01100101: self.INC,
            0b01100101: self.DEC,

        }

    def INC(self):
        '''
        *This is an instruction handled by the ALU.*

        `INC register`

        Increment (add 1 to) the value in the given register.
        '''
        self.alu("INC", self.operand_a, self.operand_b)
        self.pc += 2

    def DEC(self):
        '''
        *This is an instruction handled by the ALU.*

        `DEC register`

        Decrement (subtract 1 from) the value in the given register.
        '''
        self.alu("INC", self.operand_a, self.operand_b)
        self.pc += 2

    def PRA(self):
        '''
        Print alpha character value stored in the given register.

        Print to the console the ASCII character corresponding to the value in the
        register.
        '''
        print(ord(self.operand_a))

    def JMP(self):
        '''
        Jump to the address stored in the given register.

        Set the `PC` to the address stored in the given register.
        '''
        address = self.reg[self.operand_a]
        self.pc = address

    def JNE(self):
        '''
        If `E` flag is clear (false, 0), jump to the address stored in the given
        register.
        '''
        if not self.equals:
            address = self.reg[self.operand_a]
            self.pc = address
        else:
            self.pc += 2
    
    def JEQ(self):
        '''
        If `equal` flag is set (true), jump to the address stored in the given register.
        '''
        if self.equals:
            address = self.reg[self.operand_a]
            self.pc = address
        else:
            self.pc += 2

    def ST(self):
        '''
        Store value in registerB in the address stored in registerA.
        This opcode writes to memory.
        '''
        # Value of registerB
        value = self.reg[self.operand_b]

        # Address stored in registerA
        address = self.reg[self.operand_a]

        # Write to memory
        self.ram[address] = value

    def ADD(self):
        '''
        *This is an instruction handled by the ALU.*

        `ADD registerA registerB`

        Add the value in two registers and store the result in registerA.
        '''
        self.alu("ADD", self.operand_a, self.operand_b)
        self.pc += 3

    def RET(self):
        '''
        Pop the value from the top of the stack and store it in the `PC`.
        '''
        next_instruction = self.ram[self.sp]
        self.sp += 1
        self.pc = next_instruction

    def CALL(self):
        '''
        Calls a subroutine (function) at the address stored in the register.

        1. The address of the ***instruction*** _directly after_ `CALL` is
        pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.

        2. The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.
        '''

        # Get address to the instruction directy after CALL
        next_instruction = self.pc + 2

        # Push to stack
        self.sp -= 1
        self.ram[self.sp] = next_instruction
        
        # PC is set to the address stored in the given register
        self.pc = self.reg[self.operand_a]

    def POP(self):
        '''
        Pop the value at the top of the stack into the given register.

        1. Copy the value from the address pointed to by `SP` to the given register.
        2. Increment `SP`.
        '''
        # Store the current value
        value = self.ram[self.sp]

        self.reg[self.operand_a] = value
        self.sp += 1
        self.pc += 2

    def PUSH(self):
        '''
        Push the value in the given register on the stack.

        1. Decrement the `SP`.
        2. Copy the value in the given register to the address pointed to by
        `SP`.
        '''
        # Decrement SP
        self.sp -= 1

        # Push the value in the given register on the stack.
        value = self.reg[self.operand_a]
        self.ram[self.sp] = value
        self.pc += 2

    def HLT(self):
        self.running = False

    def LDI(self):
        '''
        Set the value of a register to an integer.
        '''
        self.reg[self.operand_a] = self.operand_b
        self.pc += 3

    def PRN(self):
        '''
        Print numeric value stored in the given register.

        Print to the console the decimal integer value that is stored in the given
        register.
        '''
        print(self.reg[self.operand_a])
        self.pc += 2

    def MUL(self):
        '''
        Multiply the values in two registers together and store the result in registerA.
        '''
        self.alu("MUL", self.operand_a, self.operand_b)
        self.pc += 3

    def CMP(self):
        '''
        Compare the values in two registers.

        * If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.

        * If registerA is less than registerB, set the Less-than `L` flag to 1,
        otherwise set it to 0.

        * If registerA is greater than registerB, set the Greater-than `G` flag
        to 1, otherwise set it to 0.
        '''
        self.alu("CMP", self.operand_a, self.operand_b)
        self.pc += 3


    def load(self, file):
        """Load a program into memory."""
        address = 0

        try:
            with open(file, 'r') as reader:
                # read and print the entire file line by line
                for line in reader:
                    line_arr = line.split()
                    # if a binary string, store in ram
                    for word in line_arr:
                        try:
                            instruction = int(word, 2)
                            self.ram[address] = instruction
                            address += 1
                        except ValueError:
                            continue
        except IOError:
            print('Please specify a valid file name')


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            # Reset counters
            self.equals = 0
            self.lessThan = 0
            self.greaterThan = 0

            if self.reg[reg_a] == self.reg[reg_b]:
                self.equals += 1
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.lessThan += 1
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.greaterThan += 1
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            ir = self.ram[self.pc]  # Instruction Register
            self.operand_a = self.ram_read(self.pc + 1)
            self.operand_b = self.ram_read(self.pc + 2)

            self.branch_table[ir]()

    def ram_read(self, mar):
        # MAR: Memory Address Register contains the address that is being read or written to
        return self.ram[mar]

    def ram_write(self, mdr, address):
        # MDR: Memory Data Register contains the data that was read or the data to write
        self.ram[address] = mdr
        
