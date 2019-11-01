# 模拟内存
class Memory(object):
    # 初始化内存
    def __init__(self):
        print('初始化内存……')
        self.init_Memory()
    def init_Memory(self):
        self.mem = bytearray(2**32) # 32位地址对应长度为2**32的数组
        # 假设内存的前16个字节存放数据，此处数字为随机设定，演示运算为11+13=24，即0x0b+0x0d=0x18
        self.mem[0] = 0
        self.mem[1] = 0
        self.mem[2] = 0
        self.mem[3] = 11
        self.mem[4] = 0
        self.mem[5] = 0
        self.mem[6] = 0
        self.mem[7] = 13
        self.mem[8] = 23
        self.mem[9] = 12
        self.mem[10] = 67
        self.mem[11] = 34
        self.mem[12] = 98
        self.mem[13] = 54
        self.mem[14] = 98
        self.mem[15] = 67
        
    # 获取内存中某个地址的数据
    def getMemData(self, addr):
        return self.mem[addr:addr+4]
    # 向内存写入值
    def setMemData(self, addr, data):
        self.mem[addr] = data

# 模拟IO
class IO(object):
    # 初始化IO
    def __init__(self):
        print('初始化IO……')
        self.init_Input()
        self.init_Output()
    # 初始化输入
    def init_Input(self):
        self.input = []
    # 从文件中获取汇编代码
    def inputCode(self, filename):
        print('从'+filename+'中读取代码')
        self.input = [s.rstrip('\n') for s in open(filename, 'r').readlines()] # 逐行读取代码，删去换行个
        self.writeCodetoMem()
    # 把代码从input读入到内存中
    def writeCodetoMem(self):
        for i in range(self.PC, self.PC + len(self.input)):
            # 此处简化代码转化为指令的过程，每条指令占四个字节，分别对应opcode, oprand1, oprand2, oprand3
            # load指令opcode为1，add指令opcode为2，store指令opcode为3
            print(self.input[i - self.PC])
            if self.input[i - self.PC] == 'Load r1, #0':
                self.setMemData(i * 4, 1)
                self.setMemData(i * 4 + 1, 1)
                self.setMemData(i * 4 + 2, 0)
                self.setMemData(i * 4 + 3, 0)
            elif self.input[i - self.PC] == 'Load r2, #1':
                self.setMemData(i * 4, 1)
                self.setMemData(i * 4 + 1, 2)
                self.setMemData(i * 4 + 2, 1)
                self.setMemData(i * 4 + 3, 0)
            elif self.input[i - self.PC] == 'Add r3, r1, r2':
                self.setMemData(i * 4, 2)
                self.setMemData(i * 4 + 1, 3)
                self.setMemData(i * 4 + 2, 1)
                self.setMemData(i * 4 + 3, 2)
            else:
                self.setMemData(i * 4, 3)
                self.setMemData(i * 4 + 1, 3)
                self.setMemData(i * 4 + 2, 3)
                self.setMemData(i * 4 + 3, 0)


# 模拟CPU
class CPU(object):
    # 初始化模拟器CPU
    def __init__(self):
        print('初始化CPU……')
        self.init_CPU()
        print('初始化内存……')
        self.init_Memory()
        print('初始化IO……')
        self.init_Input()
    # 初始化CPU
    def init_CPU(self):
        self.PC = 100 # 指令指针，假设内存从第400个字节开始装载
        self.IR = 0 # 指令寄存器
        self.Regs = [bytearray(4)] * 32 # 初始化32个32位寄存器
    # 根据PC值读取指令
    def fetch(self):
        print('从Mem['+str(self.PC)+']读取指令')
        # 读取一条指令到指令寄存器中
        self.IR = self.getMemData(self.PC * 4)
        # 程序计数器+1
        self.PC += 1
    # 处理读取到的指令
    def process(self):
        print('*'*50)
        self.fetch()
        opcode  = self.IR[0] # 获取操作符
        if opcode == 1:
            print('此指令为Load指令')
            self.Regs[self.IR[1]] = self.getMemData(self.IR[2]*4)
            print('Mem['+str(self.IR[1])+']--->寄存器R'+str(self.IR[1])+'中,值为'+str(hex2int(self.getMemData(self.IR[2]*4))))
        elif opcode == 2:
            print('此指令为Add指令')
            self.Regs[self.IR[1]] = int2hex(hex2int(self.Regs[self.IR[2]]) + hex2int(self.Regs[self.IR[3]]))
            print('寄存器R['+str(self.IR[2])+']+'+'寄存器R['+str(self.IR[3])+']--->寄存器R['+str(self.IR[1])+']，（' +str(hex2int(self.Regs[self.IR[2]]))+'+'+str(hex2int(self.Regs[self.IR[3]]))+'='+str(hex2int(self.Regs[self.IR[1]]))+'）')
        elif opcode == 3:
            print('此指令为Store指令')
            self.setMemData(self.IR[2]*4, self.Regs[self.IR[1]][0])
            self.setMemData(self.IR[2]*4+1, self.Regs[self.IR[1]][1])
            self.setMemData(self.IR[2]*4+2, self.Regs[self.IR[1]][2])
            self.setMemData(self.IR[2]*4+3, self.Regs[self.IR[1]][3])
            print('寄存器R['+str(self.IR[1])+']--->Mem['+str(self.IR[2])+']，值为'+str(hex2int(self.Regs[self.IR[1]])))
        else:
            print('程序运行结束！')
            exit(0)
        self.printStatus()
    # CPU保持运行
    def run(self):
        while(True):
            self.process()
    # 输出当前的内存和寄存器状态
    def printStatus(self):
        print('内存和寄存器状态：\n'+'\n'.join('0x'+str(i*4).zfill(8)+'-0x'+str(i*4+3).zfill(8)+':0x'+str(hex(hex2int(self.getMemData(i*4))))[2:].zfill(8) for i in range(0, 4)))
        print('\n'.join('Regs['+str(i)+']:0x'+str(hex(hex2int(self.Regs[i])))[2:].zfill(8) for i in range(0, 4)))
        print('IR:0x'+str(hex(hex2int(self.IR)))[2:].zfill(8))
        print('PC:0x'+str(hex(self.PC))[2:].zfill(8))

# 模拟计算机类
class Computer(CPU, IO, Memory):
    pass

# 用于将十六进制数转化为整形
def hex2int(hexarray):
    return int.from_bytes(hexarray, byteorder='big')

# 用于将整形数转化为十六进制
def int2hex(num):
    return bytearray.fromhex(str(hex(num)).replace('0x','').zfill(8))


if __name__ == '__main__':
    computer = Computer()
    computer.inputCode('ComputerSimulator/code.txt')
    try:
        computer.run()
    except:
        raise
    