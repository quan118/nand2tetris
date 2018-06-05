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
		# self.prefixLabel = os.path.splitext(inputfile)[0]
		self.returnTrueLabelIdx = 0
		self.endLabelIdx = 0
		self.returnLabelCounter = {}

	# Informs the codeWriter that the translation of a new VM file has started
	def setFileName(self, filename):
		self.srcFile = filename
		self.prefixLabel = os.path.splitext(os.path.split(filename)[1])[0]
		#print(self.prefixLabel)
		pass

	# Writes the assembly instructions that effect the boostrap code that initializes the VM
	def writeInit(self):
		self.outputfile.write("// Boostrap code\n")
		# SP=256
		self.outputfile.write("@256\n")
		self.outputfile.write("D=A\n")
		self.outputfile.write("@SP\n")
		self.outputfile.write("M=D\n")

		self.writeCall("Sys.init", 0)
		pass

	def writeLabel(self, label):
		self.outputfile.write("// label " + label + "\n")

		self.outputfile.write("(" + label + ")\n")

	def writeGoto(self, label):
		self.outputfile.write("// goto " + label + "\n")

		self.outputfile.write("@" + label + "\n")
		self.outputfile.write("0;JMP")

	def writeIf(self, label):
		self.outputfile.write("// if-goto " + label + "\n")

		self.outputfile.write("@SP\n")
		self.outputfile.write("M=M-1\n")
		self.outputfile.write("A=M\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@" + label + "\n")
		self.outputfile.write("D;JNE\n")

	def writeFunction(self, functionName, numVars):
		self.outputfile.write("// function " + functionName + " " + str(numVars) + "\n")
		label = functionName + "." + str(numVars)

		self.outputfile.write("(" + functionName + ")\n")
		if numVars > 0:
			# D = numVars
			self.outputfile.write("@" + str(numVars) + "\n")
			self.outputfile.write("D=A\n")

			self.outputfile.write("(" + label + ")\n")
			self.outputfile.write("@SP\n")
			self.outputfile.write("A=M\n")
			self.outputfile.write("M=0\n")

			self.outputfile.write("@SP\n")
			self.outputfile.write("M=M+1\n")
			self.outputfile.write("@" + label + "\n") 
			self.outputfile.write("D=D-1;JGT\n")

		pass

	def writeCall(self, functionName, numArgs):
		self.outputfile.write("// call " + functionName + " " + str(numArgs) + "\n")
		returnLabelIdx = 0
		if functionName in self.returnLabelCounter:
			returnLabelIdx = self.returnLabelCounter[functionName] + 1
		else:
			returnLabelIdx = 0
		self.returnLabelCounter[functionName] = returnLabelIdx
		
		returnLabel = functionName + "$ret." + str(returnLabelIdx)

		# save return label
		self.outputfile.write("@" + returnLabel + "\n")
		self.outputfile.write("D=A\n")
		self.outputfile.write("@SP\n")
		self.outputfile.write("A=M\n")
		self.outputfile.write("M=D\n")
		self.outputfile.write("@SP\n")
		self.outputfile.write("M=M+1\n")
		
		# save stack pointers
		stackPointers = ["LCL", "ARG", "THIS", "THAT"]

		for pointer in stackPointers:
			self.outputfile.write("@" + pointer + "\n")
			self.outputfile.write("D=M\n")
			self.outputfile.write("@SP\n")
			self.outputfile.write("A=M\n")
			self.outputfile.write("M=D\n")
			self.outputfile.write("@SP\n")
			self.outputfile.write("M=M+1\n")

		# ARG = SP - 5 - nArgs
		self.outputfile.write("@5\n")
		self.outputfile.write("D=A\n")
		self.outputfile.write("@" + str(numArgs) + "\n")
		self.outputfile.write("D=D+A\n")
		self.outputfile.write("@SP\n")
		self.outputfile.write("D=M-D\n")
		self.outputfile.write("@ARG\n")
		self.outputfile.write("M=D\n")

		# LCL = SP
		self.outputfile.write("@SP\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@LCL\n")
		self.outputfile.write("M=D\n")

		# goto function
		self.outputfile.write("@" + functionName + "\n")
		self.outputfile.write("0;JMP\n")

		# return address
		self.outputfile.write("(" + returnLabel + ")\n")
		pass

	def writeReturn(self):
		self.outputfile.write("// return\n")
		# tmp = return address
		self.outputfile.write("@5\n")
		self.outputfile.write("D=A\n")
		self.outputfile.write("@LCL\n")
		self.outputfile.write("A=M-D\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@tmp\n")
		self.outputfile.write("M=D\n")
		# *ARG[0] = return value
		self.outputfile.write("@SP\n")
		self.outputfile.write("A=M-1\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@ARG\n")
		self.outputfile.write("A=M\n")
		self.outputfile.write("M=D\n")
		# SP = ARG[0] + 1
		self.outputfile.write("@ARG\n")
		self.outputfile.write("D=M+1\n")
		self.outputfile.write("@SP\n")
		self.outputfile.write("M=D\n")
		# Restore THAT
		self.outputfile.write("@LCL\n")
		self.outputfile.write("A=M-1\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@THAT\n")
		self.outputfile.write("M=D\n")
		# Restore THIS
		self.outputfile.write("@LCL\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@2\n")
		self.outputfile.write("A=D-A\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@THIS\n")
		self.outputfile.write("M=D\n")
		# Restore ARG
		self.outputfile.write("@LCL\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@3\n")
		self.outputfile.write("A=D-A\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@ARG\n")
		self.outputfile.write("M=D\n")
		# Restore LCL
		self.outputfile.write("@LCL\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@4\n")
		self.outputfile.write("A=D-A\n")
		self.outputfile.write("D=M\n")
		self.outputfile.write("@LCL\n")
		self.outputfile.write("M=D\n")
		# Jump to return address
		self.outputfile.write("@tmp\n")
		self.outputfile.write("A=M;JMP\n")

		pass

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
			elif segment in ["local", "argument", "this", "that"]:
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
				self.outputfile.write("A=D+M\n")
				self.outputfile.write("D=M\n")
			elif segment == "temp":
				# D = temp index
				self.outputfile.write("@" + str(5+index) + "\n")
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

			if segment in ["local", "argument", "this", "that"]:
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
			elif segment == "temp":
				# D = tmp
				self.outputfile.write("@tmp\n")
				self.outputfile.write("D=M\n")
				# M[temp + index] = D
				self.outputfile.write("@" + str(5+index) + "\n")
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

	isSingleFile = True

	if os.path.isfile(inputfile):
		outputfile = os.path.splitext(inputfile)[0] + '.asm'
		srcFiles = [inputfile]
		isSingleFile = True
	elif os.path.isdir(inputfile):
		outputfile = inputfile + '.asm'
		srcFiles = [os.path.join(inputfile,file) for file in os.listdir(inputfile) if os.path.splitext(file)[-1] == '.vm']
		isSingleFile = False

	codeWriter = CodeWriter(outputfile)
	if not isSingleFile:
		codeWriter.writeInit()

	for srcFile in srcFiles:
		parser = Parser(srcFile)
		codeWriter.setFileName(srcFile)

		while parser.hasMoreCommands():
			parser.parse()
			commandType = parser.commandType()
			arg1 = parser.arg1()
			arg2 = parser.arg2()

			if commandType == CommandType.ARITHMETIC:
				codeWriter.writeArithmetic(arg1)
			elif commandType in [CommandType.PUSH, CommandType.POP]:
				codeWriter.writePushPop(commandType, arg1, arg2)
			elif commandType == CommandType.LABEL:
				codeWriter.writeLabel(arg1)
			elif commandType == CommandType.GOTO:
				codeWriter.writeGoto(arg1)
			elif commandType == CommandType.IF:
				codeWriter.writeIf(arg1)
			elif commandType == CommandType.FUNCTION:
				codeWriter.writeFunction(arg1, arg2)
			elif commandType == CommandType.RETURN:
				codeWriter.writeReturn()
			elif commandType == CommandType.CALL:
				codeWriter.writeCall(arg1, arg2)
			parser.advance()
	codeWriter.close()