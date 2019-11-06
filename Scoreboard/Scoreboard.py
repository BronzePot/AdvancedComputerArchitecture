# 根据课件，构造三个类：InstructionStatus，FunctionalUnitStatus，RegisterResultStatus
import re
class Scoreboard(object):
    def __init__(self, instructionsFilename):
        self.clock = 0
        self.functionalUnitStatus = FunctionalUnitStatus()
        self.registerResultStatus = RegisterResultStatus()
        self.instructionStatus = InstructionStatus(instructionsFilename, self.functionalUnitStatus, self.registerResultStatus, self.clock)
        return

    def start(self):
        while True:
            self.instructionStatus.tiktok()



class InstructionStatus(object):
    def __init__(self, instructionsFilename, functionalUnitStatus, registerResultStatus, clock):
        # 用于存放指令及其指令状态的列表
        self.functionalUnitStatus = functionalUnitStatus
        self.registerResultStatus = registerResultStatus
        self.clock = clock
        self.instructions = list()
        try:
            f = open(instructionsFilename, 'r')
            while True:
                s = f.readline()
                if not s:
                    f.close()
                    break
                operation, destination, sourceJ, sourceK = re.split(' ', s.rstrip())
                self.instructions.append({
                    'operation' :  operation,
                    'destination' : destination,
                    'sourceJ' : sourceJ,
                    'sourceK' : sourceK,
                    'unit' : '',
                    'flag' : False,
                    'statusIssue' : '',
                    'statusReadOperands' : '',
                    'statusExecutionComplete' : '',
                    'statusWriteResult' : ''
                })
        except  IOError:
            print('Read file error!')
            exit(0)
        # print(self.instructions)
        return

    def tiktok(self):
        programEnd = True
        for instruction in self.instructions:
            if instruction['statusWriteResult'] == '':
                programEnd = False
                break
        if programEnd:
            exit('运行结束！')
        self.clock += 1
        for instruction in self.instructions:
            instruction['flag'] = False
        for instruction in self.instructions:
            if instruction['statusIssue'] == '':
                if (self.functionalUnitStatus.getUnitStatus(self.getUnitName(instruction)) and 
                self.registerResultStatus.getRegisterStatus(instruction['destination']) == ''):
                    self.issue(instruction)
                    instruction['flag'] = True
                break
        for instruction in self.instructions:
            if instruction['statusIssue'] != '' and instruction['statusReadOperands'] == '' and not instruction['flag']:
                for unit in self.functionalUnitStatus.functionalUnits:
                    if unit['functionalUnitName'] == instruction['unit']:
                        if unit['statusRj'] == 'Yes' and unit['statusRk'] == 'Yes':
                            self.readOperands(instruction, 'Rj')
                            self.readOperands(instruction, 'Rk')
                            instruction['flag'] = True
        for instruction in self.instructions:
            if instruction['statusReadOperands'] != '' and instruction['statusExecutionComplete'] == '' and not instruction['flag']:
                instruction['flag'] = True
                self.executeInstructions(instruction)
        for instruction in self.instructions:
            if instruction['statusExecutionComplete'] != '' and instruction['statusWriteResult'] == '' and not instruction['flag']:
                RAWHazard = False
                for instruction2 in self.instructions:
                    if instruction2['statusIssue'] != '' and instruction2['statusExecutionComplete'] == '':
                        if (int(instruction2['statusIssue']) < int(instruction['statusIssue']) and
                        instruction['destination'] in [instruction2['sourceJ'], instruction2['sourceK']]):
                            if instruction2['statusReadOperands'] == '':
                                RAWHazard = True
                                break
                            elif int(instruction2['statusReadOperands']) == self.clock:
                                RAWHazard = True
                                break                            
                if not RAWHazard:
                    instruction['flag'] = True
                    self.writeResult(instruction)
        self.printStatus()

    
    def issue(self, instruction):
        instruction['statusIssue'] = self.clock
        unitName = self.functionalUnitStatus.getUnitStatus(self.getUnitName(instruction))
        instruction['unit'] = unitName
        for unit in self.functionalUnitStatus.functionalUnits:
            if unit['functionalUnitName'] == unitName:
                if instruction['operation'] == 'LD' or instruction['operation'] == 'SD':
                    unit['usedTime'] = 1
                elif instruction['operation'] == 'ADDD' or instruction['operation'] == 'SUBD':
                    unit['usedTime'] = 2
                elif instruction['operation'] == 'MULT':
                    unit['usedTime'] = 10
                elif instruction['operation'] == 'DIVD':
                    unit['usedTime'] = 40
                else:
                    unit['usedTime'] = -1
                unit['statusBusy'] = True
                unit['statusOp'] = unitName
                unit['statusFi'] = instruction['destination']
                unit['statusFj'] = instruction['sourceJ']
                unit['statusFk'] = instruction['sourceK']
                unit['statusQj'] = self.registerResultStatus.getRegisterStatus(instruction['sourceJ'])
                unit['statusQk'] = self.registerResultStatus.getRegisterStatus(instruction['sourceK'])
                unit['statusRj'] = 'Yes' if unit['statusQj'] == '' else 'No'
                unit['statusRk'] = 'Yes' if unit['statusQk'] == '' else 'No'
                self.registerResultStatus.registers[instruction['destination']] = unitName
    
    def readOperands(self, instruction, reg):
        instruction['statusReadOperands'] = self.clock
        instruction[reg] = 'No'
        return

    def executeInstructions(self, instruction):
        for unit in self.functionalUnitStatus.functionalUnits:
            if unit['functionalUnitName'] == instruction['unit']:
                unit['usedTime'] -= 1
                unit['statusRj'] = 'No'
                unit['statusRk'] = 'No'
                if unit['usedTime'] == 0:
                    instruction['statusExecutionComplete'] = self.clock

    def writeResult(self, instruction):
        instruction['statusWriteResult'] = self.clock
        for unit in self.functionalUnitStatus.functionalUnits:
            if unit['functionalUnitName'] == instruction['unit']:
                self.registerResultStatus.registers[unit['statusFi']] = ''
                unit['statusBusy'] = False
                for unit2 in self.functionalUnitStatus.functionalUnits:
                    if unit2['statusQj'] == unit['functionalUnitName']:
                        unit2['statusRj'] = 'Yes'
                    if unit2['statusQk'] == unit['functionalUnitName']:
                        unit2['statusRk'] = 'Yes'
                self.functionalUnitStatus.resetUnit(unit)

    # 获取指令需要使用的运算单元名称
    def getUnitName(self, instruction):
        unitName = ''
        if instruction['operation'] == 'LD' or instruction['operation'] == 'SD':
            unitName = 'Integer'
        elif instruction['operation'] == 'MULT':
            unitName = 'Mult'
        elif instruction['operation'] == 'ADDD' or instruction['operation'] == 'SUBD':
            unitName = 'Add'
        elif instruction['operation'] == 'DIVD':
            unitName = 'Divide'
        return unitName

    def printStatus(self):
        print('Clock ' + str(self.clock)+':')
        print('Instruction Status')
        print('Instruction\tDestination\tsourceJ\tsourceK\tIssue\tRead Operands\tExecution complete\tWrite Result')
        for instruction in self.instructions:
            print(instruction['operation'] + '\t\t' +
            instruction['destination'] + '\t\t' +
            instruction['sourceJ'] + '\t' +
            instruction['sourceK'] + '\t' +
            str(instruction['statusIssue']) + '\t' +
            str(instruction['statusReadOperands']) + '\t\t' +
            str(instruction['statusExecutionComplete']) + '\t\t\t' +
            str(instruction['statusWriteResult']))
        print('Functional Units Status')
        print('UnitName\tBusy\tOperation\tFi\tFj\tFk\tQj\tQk\tRj\tRk')
        for functionalUnit in self.functionalUnitStatus.functionalUnits:
            print(functionalUnit['functionalUnitName'] + '\t\t' +
            str(functionalUnit['statusBusy']) + '\t' +
            functionalUnit['statusOp'] + '\t\t' +
            functionalUnit['statusFi'] + '\t' +
            functionalUnit['statusFj'] + '\t' +
            functionalUnit['statusFk'] + '\t' +
            functionalUnit['statusQj'] + '\t' +
            functionalUnit['statusQk'] + '\t' +
            functionalUnit['statusRj'] + '\t' +
            functionalUnit['statusRk'])
        print('Registers Status')
        print('F0\tF2\tF4\tF6\tF8\tF10\tF12\tF14\tF16\tF18\tF20\tF22\tF24\tF26\tF28\tF30')
        registers = ''
        for register in self.registerResultStatus.registers:
            registers += self.registerResultStatus.registers[register] + '\t'
        print(registers)
            

class FunctionalUnitStatus(object):
    def __init__(self):
        self.functionalUnits = list()
        functionalUnitsName = ['Integer', 'Mult1', 'Mult2', 'Add', 'Divide']
        for functionalUnitName in functionalUnitsName:
            self.functionalUnits.append({
                'functionalUnitName' : functionalUnitName,
                'usedTime' : -1,
                'statusBusy' : False,
                'statusOp' : '',
                'statusFi' : '',
                'statusFj' : '',
                'statusFk' : '',
                'statusQj' : '',
                'statusQk' : '',
                'statusRj' : '',
                'statusRk' : ''
            })
        # print(self.functionalUnits)
        return

    # 获取运算单元被占用情况
    def getUnitStatus(self, unitName):
        if unitName != 'Mult':
            for unit in self.functionalUnits:
                if unit['functionalUnitName'] == unitName:
                    if unit['statusBusy'] == False:
                        return unit['functionalUnitName']
        else:
            for unit in self.functionalUnits:
                if unit['functionalUnitName'] in ["Mult1", "Mult2"]:
                    if unit['statusBusy'] == False:
                        return unit['functionalUnitName']
        return False

    def resetUnit(self, unit):
        unit['usedTime'] = -1
        unit['statusBusy'] = False
        unit['statusOp'] = ''
        unit['statusFi'] = ''
        unit['statusFj'] = ''
        unit['statusFk'] = ''
        unit['statusQj'] = ''
        unit['statusQk'] = ''
        unit['statusRj'] = ''
        unit['statusRk'] = ''
        return

class RegisterResultStatus(object):
    def __init__(self):
        self.registers = dict()
        # 32个单精度浮点寄存器（16个双精度浮点寄存器）
        for i in range(0, 16):
            self.registers['F'+str(2*i)] = ''
        # print(self.registers)
        return

    def getRegisterStatus(self, oprandName):
        if oprandName[0] != 'F':
            return ''
        else:
            return self.registers[oprandName]

SB = Scoreboard('Scoreboard/code.txt')
SB.start()