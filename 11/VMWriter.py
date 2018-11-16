#!/user/bin/python
import unittest
import StringIO
import os

class Segment:
  CONST = 'constant'
  ARG = 'argument'
  LOCAL = 'local'
  STATIC = 'static'
  THIS = 'this'
  THAT = 'that'
  POINTER = 'pointer'
  TEMP = 'temp'

class Arithmetic:
  ADD = 'add'
  SUB = 'sub'
  NEG = 'neg'
  EQ = 'eq'
  GT = 'gt'
  LT = 'lt'
  AND = 'and'
  OR = 'or'
  NOT = 'not'

class VMWriter:
  def __init__(self, output):
    self.outputFile = open(output, 'w')
  
  def writePush(self, segment, index):
    self.outputFile.write("push %s %d\n" % (segment, index))
  
  def writePop(self, segment, index):
    self.outputFile.write("pop %s %d\n" % (segment, index))

  def writeArithmetic(self, arithmetic):
    self.outputFile.write("%s\n" % arithmetic)
  
  def writeLabel(self, label):
    self.outputFile.write("label %s\n" % label)

  def writeGoto(self, label):
    self.outputFile.write("goto %s\n" % label)

  def writeIf(self, label):
    self.outputFile.write("if-goto %s\n" % label)

  def writeCall(self, name, nArgs):
    self.outputFile.write("call %s %d\n" % (name, nArgs))

  def writeFunction(self, name, nLocals):
    self.outputFile.write("function %s %d\n" % (name, nLocals))
  
  def writeReturn(self):
    self.outputFile.write("return\n")

  def close(self):
    self.outputFile.close()

class TestVMWriter(unittest.TestCase):
  def test_writePush(self):
    vmWriter = VMWriter('test_writePush')
    vmWriter.writePush(Segment.CONST, 0)
    vmWriter.writePush(Segment.ARG, 1)
    vmWriter.writePush(Segment.LOCAL, 2)
    vmWriter.writePush(Segment.STATIC, 3)
    vmWriter.writePush(Segment.THIS, 4)
    vmWriter.writePush(Segment.THAT, 5)
    vmWriter.writePush(Segment.POINTER, 6)
    vmWriter.writePush(Segment.TEMP, 7)
    vmWriter.close()

    f = open('test_writePush', 'r')
    lines = f.readlines()
    lines = [line.strip("\n") for line in lines]
    self.assertEqual(lines[0], 'push const 0')
    self.assertEqual(lines[1], 'push argument 1')
    self.assertEqual(lines[2], 'push local 2')
    self.assertEqual(lines[3], 'push static 3')
    self.assertEqual(lines[4], 'push this 4')
    self.assertEqual(lines[5], 'push that 5')
    self.assertEqual(lines[6], 'push pointer 6')
    self.assertEqual(lines[7], 'push temp 7')
    f.close()
    os.remove('test_writePush')
  
  def test_writePop(self):
    vmWriter = VMWriter('test_writePop')
    vmWriter.writePop(Segment.CONST, 0)
    vmWriter.writePop(Segment.ARG, 1)
    vmWriter.writePop(Segment.LOCAL, 2)
    vmWriter.writePop(Segment.STATIC, 3)
    vmWriter.writePop(Segment.THIS, 4)
    vmWriter.writePop(Segment.THAT, 5)
    vmWriter.writePop(Segment.POINTER, 6)
    vmWriter.writePop(Segment.TEMP, 7)
    vmWriter.close()

    f = open('test_writePop', 'r')
    lines = f.readlines()
    lines = [line.strip("\n") for line in lines]
    self.assertEqual(lines[0], 'pop const 0')
    self.assertEqual(lines[1], 'pop argument 1')
    self.assertEqual(lines[2], 'pop local 2')
    self.assertEqual(lines[3], 'pop static 3')
    self.assertEqual(lines[4], 'pop this 4')
    self.assertEqual(lines[5], 'pop that 5')
    self.assertEqual(lines[6], 'pop pointer 6')
    self.assertEqual(lines[7], 'pop temp 7')
    f.close()
    os.remove('test_writePop')

  def test_writeArithmetic(self):
    vmWriter = VMWriter('test_writeArithmetic')
    vmWriter.writeArithmetic(Arithmetic.ADD)
    vmWriter.writeArithmetic(Arithmetic.SUB)
    vmWriter.writeArithmetic(Arithmetic.NEG)
    vmWriter.writeArithmetic(Arithmetic.EQ)
    vmWriter.writeArithmetic(Arithmetic.GT)
    vmWriter.writeArithmetic(Arithmetic.LT)
    vmWriter.writeArithmetic(Arithmetic.AND)
    vmWriter.writeArithmetic(Arithmetic.OR)
    vmWriter.writeArithmetic(Arithmetic.NOT)
    vmWriter.close()

    f = open('test_writeArithmetic', 'r')
    lines = f.readlines()
    lines = [line.strip("\n") for line in lines]
    self.assertEqual(lines[0], 'add')
    self.assertEqual(lines[1], 'sub')
    self.assertEqual(lines[2], 'neg')
    self.assertEqual(lines[3], 'eq')
    self.assertEqual(lines[4], 'gt')
    self.assertEqual(lines[5], 'lt')
    self.assertEqual(lines[6], 'and')
    self.assertEqual(lines[7], 'or')
    self.assertEqual(lines[8], 'not')
    f.close()
    os.remove('test_writeArithmetic')

  def test_writeLabel(self):
    vmWriter = VMWriter('test_writeLabel')
    vmWriter.writeLabel('label_here')
    vmWriter.close()

    f = open('test_writeLabel', 'r')
    lines = f.readlines()
    lines = [line.strip("\n") for line in lines]
    self.assertEqual(lines[0], 'label label_here')
    f.close()
    os.remove('test_writeLabel')

  def test_writeGoto(self):
    vmWriter = VMWriter('test_writeGoto')
    vmWriter.writeGoto('label_here')
    vmWriter.close()

    f = open('test_writeGoto', 'r')
    lines = f.readlines()
    lines = [line.strip("\n") for line in lines]
    self.assertEqual(lines[0], 'goto label_here')
    f.close()
    os.remove('test_writeGoto')
  
  def test_writeIf(self):
    vmWriter = VMWriter('test_writeIf')
    vmWriter.writeIf('label_here')
    vmWriter.close()

    f = open('test_writeIf', 'r')
    lines = f.readlines()
    lines = [line.strip("\n") for line in lines]
    self.assertEqual(lines[0], 'if-goto label_here')
    f.close()
    os.remove('test_writeIf')

  def test_writeCall(self):
    vmWriter = VMWriter('test_writeCall')
    vmWriter.writeCall('func_name', 5)
    vmWriter.close()

    f = open('test_writeCall', 'r')
    lines = f.readlines()
    lines = [line.strip("\n") for line in lines]
    self.assertEqual(lines[0], 'call func_name 5')
    f.close()
    os.remove('test_writeCall')

  def test_writeFunction(self):
    vmWriter = VMWriter('test_writeFunction')
    vmWriter.writeFunction('func_name', 3)
    vmWriter.close()

    f = open('test_writeFunction', 'r')
    lines = f.readlines()
    lines = [line.strip("\n") for line in lines]
    self.assertEqual(lines[0], 'function func_name 3')
    f.close()
    os.remove('test_writeFunction')

  def test_writeReturn(self):
    vmWriter = VMWriter('test_writeReturn')
    vmWriter.writeReturn()
    vmWriter.close()

    f = open('test_writeReturn', 'r')
    lines = f.readlines()
    lines = [line.strip("\n") for line in lines]
    self.assertEqual(lines[0], 'return')
    f.close()
    os.remove('test_writeReturn')

if __name__=='__main__':
  unittest.main()
