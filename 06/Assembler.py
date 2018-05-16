#!/usr/bin/python
import sys
import ast
import os

class SymbolTable:
	def __init__(self):
		self.table = {'R0':0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4,
		'R5': 5, 'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9, 'R10': 10,
		'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
		'SCREEN': 16384, 'KBD': 24576, 'SP': 0, 'LCL': 1,
		'ARG': 2, 'THIS': 3, 'THAT': 4}
		self.availableAddr = 16

	def add(self, key, value = None):
		self.table[key] = value

	def get(self, key):
		if not key in self.table:
			return None

		return self.table[key]

	def getAvailableAddr(self):
		return self.availableAddr

	def nextAvailableAddr(self):
		self.availableAddr += 1

class Parser:
	def __init__(self, filename):
		self.filename = filename
		self.currentLineNo = 0
		f = open(self.filename, 'r')
		self.lines = f.readlines()
		f.close()

	# Remove whitespace, comments and labels
	def firstPass(self, symbolTable):
		self.normalizedLines = []
		curLineNo = 0
		for line in self.lines:
			line = line[:line.find('//')]
			line = line.strip()
			if len(line) <= 0:
				continue
			if line.startswith('(') and line.endswith(')'):
				key = line[1:-1]
				symbolTable.add(key, curLineNo)
				continue
			self.normalizedLines.append(line)
			curLineNo += 1

	# Resolve addresses
	def secondPass(self, symbolTable):
		for i in range(0, len(self.normalizedLines)):
			line = self.normalizedLines[i]
			if not line.startswith('@'):
				continue
			label = line[1:]

			if self.isNumericString(label):
				continue

			addr = symbolTable.get(label)
			if addr != None:
				self.normalizedLines[i] = '@' + str(addr)
			else:
				addr = symbolTable.getAvailableAddr()
				symbolTable.add(label, addr)
				self.normalizedLines[i] = '@' + str(addr)
				symbolTable.nextAvailableAddr()

	def reset(self):
		self.currentLineNo = 0

	def isACommand(self):
		if len(self.normalizedLines) <= self.currentLineNo or self.currentLineNo < 0:
			return False
		line = self.normalizedLines[self.currentLineNo]
		return line.startswith('@')


	def isCCommand(self):
		if len(self.normalizedLines) <= self.currentLineNo or self.currentLineNo < 0:
			return False
		line = self.normalizedLines[self.currentLineNo]
		return not line.startswith('@')

	def hasMoreCommands(self):
		return self.currentLineNo < len(self.normalizedLines)

	def advance(self):
		self.currentLineNo += 1

	def parseCCommand(self):
		if not self.isCCommand():
			return None
		parts = self.normalizedLines[self.currentLineNo].split(';')
		dest = comp = jmp = None

		if len(parts) == 1:
			dest, comp = self.getDestAndComp(parts[0])
		elif len(parts) == 2:
			dest, comp = self.getDestAndComp(parts[0])
			jmp = parts[1]

		return (dest, comp, jmp)

	def parseACommand(self):
		return self.normalizedLines[self.currentLineNo][1:]

	def getDestAndComp(self, line):
		dest = comp = None

		tokens = line.split('=')
		
		if len(tokens) == 1:
			comp = tokens[0]
		elif len(tokens) == 2:
			dest = tokens[0]
			comp = tokens[1]

		return (dest, comp)

	def currentCommand(self):
		return self.normalizedLines[self.currentLineNo]

	@staticmethod
	def isNumericString(line):
		try:
			num = int(line)
			return True
		except:
			return False

class Code:
	def __init__(self):
		self.compTable = {'0': '0101010', '1': '0111111', '-1': '0111010', 'D': '0001100',
			'A': '0110000', 'M': '1110000', '!D': '0001101', '!A': '0110001', '!M': '1110001',
			'-D': '0001111', '-A': '0110011', '-M': '1110011', 'D+1': '0011111', 'A+1': '0110111',
			'M+1': '1110111', 'D-1': '0001110', 'A-1': '0110010', 'M-1': '1110010',
			'D+A': '0000010', 'D+M': '1000010', 'D-A': '0010011', 'D-M': '1010011',
			'A-D': '0000111', 'M-D': '1000111', 'D&A': '0000000', 'D&M': '1000000',
			'D|A': '0010101', 'D|M': '1010101'}

		self.destTable = {None: '000', 'M': '001', 'D': '010', 'MD': '011', 'A': '100',
			'AM': '101', 'AD': '110', 'AMD': '111'}

		self.jumpTable = {None: '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
			'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}

		pass

	def comp(self, line):
		return self.compTable[line]

	def dest(self, line):
		return self.destTable[line]

	def jump(self, line):
		return self.jumpTable[line]

	def cCommandToBinary(self, comp, dest, jmp):
		return '111' + self.comp(comp) + self.dest(dest) + self.jump(jmp)

	def aCommandToBinary(self, line):
		return bin(int(line))[2:].rjust(16, '0')

class Assembler:
	def __init__(self, filename):
		self.symbolTable = SymbolTable()
		self.parser = Parser(filename)
		self.code = Code()
		self.binaryCode = []

	def run(self):
		self.binaryCode = []
		self.parser.firstPass(self.symbolTable)
		self.parser.secondPass(self.symbolTable)

		while self.parser.hasMoreCommands():
			binary = None
			currentCommand = self.parser.currentCommand()

			if self.parser.isACommand():
				cmd = self.parser.parseACommand()
				binary = self.code.aCommandToBinary(cmd)
			elif self.parser.isCCommand():
				dest, comp, jmp = self.parser.parseCCommand()
				binary = self.code.cCommandToBinary(comp, dest, jmp)
			if binary != None:
				self.binaryCode.append(binary)

			self.parser.advance()

	def machineCode(self):
		return self.binaryCode

if __name__=='__main__':
	filename = sys.argv[1]
	output = os.path.splitext(filename)[0] + '.hack'
	assembler = Assembler(filename)
	assembler.run()
	f = open(output, 'w')
	for line in assembler.machineCode():
		f.write(line)
		f.write('\n')
	f.close()
