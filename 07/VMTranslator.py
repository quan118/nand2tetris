#!/usr/bin/python
import sys
import ast
import os

class CommandType:
	ARITHMETIC = 0
	PUSH = 1
	POP = 2
	LABEL = 3
	GOTO = 4
	IF = 5
	FUNCTION = 6
	RETURN = 7
	CALL = 8

class Parser:
	def __init__(self, filename):
		self.filename = filename
		self.currentLineNo = 0
		f = open(self.filename, 'r')
		self.lines = f.readlines()
		f.close()
		self.initCommandTypeTable()
		self.normalize()
		pass

	def initCommandTypeTable(self):
		self.cmdTypeTable = {
			'add': CommandType.ARITHMETIC, 'sub': CommandType.ARITHMETIC, 'neg': CommandType.ARITHMETIC,
			'eq': CommandType.ARITHMETIC, 'gt': CommandType.ARITHMETIC, 'lt': CommandType.ARITHMETIC,
			'and': CommandType.ARITHMETIC, 'or': CommandType.ARITHMETIC, 'not': CommandType.ARITHMETIC,
			'pop': CommandType.POP, 'push': CommandType.PUSH,
			'label': CommandType.LABEL, 'goto': CommandType.GOTO, 'if-goto': CommandType.IF,
			'function': CommandType.FUNCTION, 'call': CommandType.CALL, 'return': CommandType.RETURN}

	# Remove whitespace and comments
	def normalize(self):
		self.normalizedLines = []
		for line in self.lines:
			line = line[:line.find('//')].strip()
			if len(line) <= 0:
				continue
			self.normalizedLines.append(line)

	def hasMoreCommands(self):
		return self.currentLineNo < len(self.normalizedLines)

	def advance(self):
		self.currentLineNo += 1

	# return 1 of these types: ARITHMETIC, PUSH, POP, LABEL, GOTO, IF, FUNCTION, RETURN, CALL
	def commandType(self):
		return self.cmdType

	# return the first argument of the current command. In the case of ARTHMETIC, the command
	# itself (add, sub, etc.) is returned.
	# Should not be called if the current command is C_RETURN
	def arg1(self):
		return self.argument1

	# returns the second argument of the current command.
	# Should be called only if the current command is PUSH, POP, FUNCTION or CALL
	def arg2(self):
		return self.argument2

	def parse(self):
		tokens = self.normalizedLines[self.currentLineNo].split(' ')
		self.cmdType = self.cmdTypeTable[tokens[0]]

		if self.cmdType == CommandType.ARITHMETIC:
			self.argument1 = tokens[0]
			self.argument2 = None
		elif self.cmdType in [CommandType.PUSH, CommandType.POP, CommandType.FUNCTION, CommandType.CALL]:
			self.argument1 = tokens[1]
			self.argument2 = int(tokens[2])
		elif self.cmdType in [CommandType.LABEL, CommandType.GOTO, CommandType.IF]:
			self.argument1 = tokens[1]
			self.argument2 = None
		else:
			self.argument1 = None
			self.argument2 = None


class CodeWriter:
	def __init__(self, filename):
		self.outputfile = open(filename, 'w')
		self.prefixLabel = os.path.splitext(inputfile)[0]
		self.returnTrueLabelIdx = 0
		self.endLabelIdx = 0

	# writes to the output file the assembly code that implements the given arithmetic command
	def writeArithmetic(self, command):
		self.outputfile.write("// " + command + "\n")

		if command in ["neg", "not"]:
			# D = POP
			self.outputfile.write("@SP\n")
			self.outputfile.write("M=M-1\n")
			self.outputfile.write("A=M\n")
			self.outputfile.write("D=M\n")

			# Calculate
			if command == "neg":
				self.outputfile.write("D=-D\n")
			elif command == "not":
				self.outputfile.write("D=!D\n")

		else:
			# tmp = POP
			self.outputfile.write("@SP\n")
			self.outputfile.write("M=M-1\n")
			self.outputfile.write("A=M\n")
			self.outputfile.write("D=M\n")
			self.outputfile.write("@tmp\n")
			self.outputfile.write("M=D\n")

			# D = POP
			self.outputfile.write("@SP\n")
			self.outputfile.write("M=M-1\n")
			self.outputfile.write("A=M\n")
			self.outputfile.write("D=M\n")

			# Calculate
			self.outputfile.write("@tmp\n")
			if command == "add":
				self.outputfile.write("D=D+M\n")
			elif command == "sub":
				self.outputfile.write("D=D-M\n")
			elif command in ["eq", "gt", "lt"]:
				self.outputfile.write("D=D-M\n")
				self.outputfile.write("@RETURN_TRUE" + str(self.returnTrueLabelIdx) + "\n")
				if command == "eq":
					self.outputfile.write("D;JEQ\n")
				elif command == "gt":
					self.outputfile.write("D;JGT\n")
				elif command == "lt":
					self.outputfile.write("D;JLT\n")
				#self.outputfile.write("(RETURN_FALSE)\n")
				self.outputfile.write("D=0\n")
				self.outputfile.write("@END" + str(self.endLabelIdx) + "\n")
				self.outputfile.write("0;JMP\n")
				self.outputfile.write("(RETURN_TRUE" + str(self.returnTrueLabelIdx) + ")\n")
				self.outputfile.write("D=-1\n")
				self.outputfile.write("(END" + str(self.endLabelIdx) + ")\n")

				self.returnTrueLabelIdx += 1
				self.endLabelIdx += 1
			elif command == "and":
				self.outputfile.write("D=D&M\n")
			elif command == "or":
				self.outputfile.write("D=D|M\n")

		# PUSH D
		self.outputfile.write("@SP\n")
		self.outputfile.write("A=M\n")
		self.outputfile.write("M=D\n")
		self.outputfile.write("@SP\n")
		self.outputfile.write("M=M+1\n")

	# Writes to the output file the assembly code that implements the given command, where command is either PUSH or POP
	# command: PUSH or POP
	# segment: string
	# index: int
	def writePushPop(self, command, segment, index):
		commandStr = "push" if command == CommandType.PUSH else "pop"
		self.outputfile.write("// " + commandStr + " " + segment + " " + str(index) + "\n")
		if command == CommandType.PUSH:
			if segment == "constant":
				# D = constant value
				self.outputfile.write("@" + str(index) + "\n")
				self.outputfile.write("D=A\n")
			elif segment in ["local", "argument", "this", "that", "temp"]:
				# D = *(@Segment + index)
				self.outputfile.write("@" + str(index) + "\n")
				self.outputfile.write("D=A\n")
				if segment == "local":
					self.outputfile.write("@LCL\n")
				elif segment == "argument":
					self.outputfile.write("@ARG\n")
				elif segment == "this":
					self.outputfile.write("@THIS\n")
				elif segment == "that":
					self.outputfile.write("@THAT\n")
				elif segment == "temp":
					self.outputfile.write("@5\n")
				self.outputfile.write("A=D+M\n")
				self.outputfile.write("D=M\n")
			elif segment == "static":
				# D = static variable
				self.outputfile.write("@" + self.prefixLabel + "." + str(index) + "\n")
				self.outputfile.write("D=M\n")
			elif segment == "pointer":
				# D = THIS/THAT
				if index == 0:
					self.outputfile.write("@THIS\n")
				elif index == 1:
					self.outputfile.write("@THAT\n")
				self.outputfile.write("D=M\n")
			# *SP = D
			self.outputfile.write("@SP\n")
			self.outputfile.write("A=M\n")
			self.outputfile.write("M=D\n")
			# SP++
			self.outputfile.write("@SP\n")
			self.outputfile.write("M=M+1\n")
		elif command == CommandType.POP:
			# SP--
			self.outputfile.write("@SP\n")
			self.outputfile.write("M=M-1\n")
			
			# tmp = *SP
			self.outputfile.write("A=M\n")
			self.outputfile.write("D=M\n")
			self.outputfile.write("@tmp\n")
			self.outputfile.write("M=D\n")

			if segment in ["local", "argument", "this", "that", "temp"]:
				# addr = @Segment + index
				self.outputfile.write("@" + str(index) + "\n")
				self.outputfile.write("D=A\n")
				if segment == "local":
					self.outputfile.write("@LCL\n")
				elif segment == "argument":
					self.outputfile.write("@ARG\n")
				elif segment == "this":
					self.outputfile.write("@THIS\n")
				elif segment == "that":
					self.outputfile.write("@THAT\n")
				elif segment == "temp":
					self.outputfile.write("@5\n")
				self.outputfile.write("D=D+M\n")
				self.outputfile.write("@addr\n")
				self.outputfile.write("M=D\n")

				# D = tmp
				self.outputfile.write("@tmp\n")
				self.outputfile.write("D=M\n")

				# *addr = D
				self.outputfile.write("@addr\n")
				self.outputfile.write("A=M\n")
				self.outputfile.write("M=D\n")

			elif segment == "static":
				# static variable = D
				self.outputfile.write("@" + self.prefixLabel + "." + str(index) + "\n")
				self.outputfile.write("M=D\n")

			elif segment == "pointer":
				# THIS/THAT = D
				if index == 0:
					self.outputfile.write("@THIS\n")
				elif index == 1:
					self.outputfile.write("@THAT\n")
				self.outputfile.write("M=D\n")
		
	# Closes the output file
	def close(self):
		self.outputfile.close()
		pass

if __name__=='__main__':
	inputfile = sys.argv[1]
	outputfile = os.path.splitext(inputfile)[0] + '.asm'

	parser = Parser(inputfile)
	codeWriter = CodeWriter(outputfile)

	while parser.hasMoreCommands():
		parser.parse()
		commandType = parser.commandType()
		arg1 = parser.arg1()
		arg2 = parser.arg2()

		if commandType == CommandType.ARITHMETIC:
			codeWriter.writeArithmetic(arg1)
		elif commandType in [CommandType.PUSH, CommandType.POP]:
			codeWriter.writePushPop(commandType, arg1, arg2)

		parser.advance()

	codeWriter.close()