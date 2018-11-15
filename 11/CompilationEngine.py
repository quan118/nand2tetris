from JackTokenizer import JackTokenizer, Token
from FSM import Node, DEFINITION, FINAL_STATE, FSM
from VMWriter import VMWriter, Segment, Arithmetic
from SymbolTable import Kind, SymbolTable

class CompilationEngine:
  def __init__(self, vmWriter, rootNode):
    self.vmWriter = vmWriter
    self.rootNode = rootNode
    self.compile(self.rootNode)
  
  # Done
  def compile(self, node):
    if node.tag == 'class':
      self.compileClass(node)
    elif node.tag == 'classVarDec':
      self.compileClassVarDec(node)
    elif node.tag == 'subroutineDec':
      self.compileSubroutineDec(node)
    elif node.tag == 'parameterList':
      self.compileParameterList(node)
    elif node.tag == 'subroutineBody':
      self.compileSubroutineBody(node)
    elif node.tag == 'varDec':
      self.compileVarDec(node)
    elif node.tag == 'statements':
      self.compileStatements(node)
    elif node.tag == 'letStatement':
      self.compileLet(node)
    elif node.tag == 'ifStatement':
      self.compileIf(node)
    elif node.tag == 'whileStatement':
      self.compileWhile(node)
    elif node.tag == 'doStatement':
      self.compileDo(node)
    elif node.tag == 'returnStatement':
      self.compileReturn()
    elif node.tag == 'expression':
      self.compileExpression(node)
    elif node.tag == 'term':
      self.compileTerm(node)
    elif node.tag == 'expressionList':
      self.compileExpressionList(node)
    pass

  # Done
  def compileClass(self, node):
    self.classSymbolTable = SymbolTable()
    self.className = node.children[1].data

    classVarDecs = [child for child in node.children if child.tag == 'classVarDec']
    for classVarDec in classVarDecs:
      self.compileClassVarDec(classVarDec)

    for child in node.children:
      if child.tag != 'classVarDec':
        self.compile(child)

  # Done
  def compileClassVarDec(self, node):
    # Kind
    if node.children[0].data == 'static':
      kind = Kind.STATIC
    elif node.children[0].data == 'field':
      kind = Kind.FIELD
    
    # Type
    type = node.children[1].data

    # identifiers
    identifiers = [child for child in node.children if child.tag == 'identifier']

    for identifier in identifiers:
      self.classSymbolTable.define(identifier.data, type, kind)

  # Done
  def compileSubroutineDec(self, node):
    self.subroutineSymbolTable = SymbolTable()
    self.subroutineLabelCounter = 0
    if node.children[0].tag == 'keyword':
      self.subroutineType = node.children[0].data
      if self.subroutineType == 'constructor':
        self.subroutineName = node.children[2].data
      elif self.subroutineType in ['method', 'function']:
        self.returnType = node.children[1]
        self.subroutineName = node.children[2]
      else:
        return
      parameterList = next(child for child in node.children if child.tag == 'parameterList')
      self.compileParameterList(parameterList)
      subroutineBody = next(child for child in node.children if child.tag == 'subroutineBody')
      self.compileSubroutineBody(subroutineBody)

  # Done
  def compileParameterList(self, node):
    if self.subroutineType in ['method', 'function']:
      self.subroutineSymbolTable.define('this', self.className, Kind.ARG)
    for child in node.children:
      if child.tag == 'keyword':
        type = node.data
      elif child.tag == 'identifier':
        self.subroutineSymbolTable.define(child.data, type, Kind.ARG)

  # Done
  def compileSubroutineBody(self, node):
    varDecs = [child for child in node.children if child.tag == 'varDec']
    for varDec in varDecs:
      self.compileVarDec(varDec)
    
    nLocals = self.subroutineSymbolTable.numberOfKind(Kind.VAR)
    self.vmWriter.writeFunction('%s.new' % self.className, nLocals)

    if self.subroutineType == 'constructor':
      objSize = self.classSymbolTable.numberOfKind(Kind.FIELD)
      self.vmWriter.writePush(Segment.CONST, objSize)
      self.vmWriter.writeCall('Memory.alloc', 1)
      self.vmWriter.writePop(Segment.POINTER, 0)
    elif self.subroutineType == 'method':
      self.vmWriter.writePush(Segment.ARG, 0)
      self.vmWriter.writePop(Segment.POINTER, 0)

    for child in node.children:
      self.compile(child)

  # Done
  def compileVarDec(self, node):
    # Kind
    kind = Kind.VAR

    # Type
    type = node.children[1].data
    
    # identifiers
    identifiers = [child for child in node.children if child.tag == 'identifier']

    for identifier in identifiers:
      self.subroutineSymbolTable.define(identifier.data, type, kind)

  def compileStatements(self, node):
    for child in node.children:
      self.compile(child)

  def writePop(self, identifier):
    idx = self.subroutineSymbolTable.indexOf(identifier)
    if idx >= 0:
      kind = self.subroutineSymbolTable.kindOf(identifier)
      if kind == Kind.ARG:
        self.vmWriter.writePop(Segment.ARG, idx)
      elif kind == Kind.VAR:
        self.vmWriter.writePop(Segment.LOCAL, idx)
    else:
      idx = self.classSymbolTable.indexOf(identifier)
      kind = self.classSymbolTable.kindOf(identifier)
      if kind == Kind.STATIC:
        self.vmWriter.writePop(Segment.STATIC, idx)
      elif kind == Kind.FIELD:
        self.vmWriter.writePop(Segment.THIS, idx)

  def writePush(self, identifier):
    idx = self.subroutineSymbolTable.indexOf(identifier)
    if idx >= 0:
      kind = self.subroutineSymbolTable.kindOf(identifier)
      if kind == Kind.ARG:
        self.vmWriter.writePush(Segment.ARG, idx)
      elif kind == Kind.VAR:
        self.vmWriter.writePush(Segment.LOCAL, idx)
    else:
      idx = self.classSymbolTable.indexOf(identifier)
      kind = self.classSymbolTable.kindOf(identifier)
      if kind == Kind.STATIC:
        self.vmWriter.writePush(Segment.STATIC, idx)
      elif kind == Kind.FIELD:
        self.vmWriter.writePush(Segment.THIS, idx)

  # Done
  def compileLet(self, node):
    if node.children[1].tag == 'identifier':
      identifier = node.children[1].data
    if node.children[2].tag == 'symbol' and node.children[2].data == '[' and node.children[4].tag == 'symbol' and node.children[4].data == ']':
      # handle array
      if node.children[3].tag == 'expression':
        expression1 = node.children[3]
      if node.children[6].tag == 'expression':
        expression2 = node.children[6]
      if expression1 and expression2:
        self.writePush(identifier)
        self.compileExpression(expression1)
        self.vmWriter.writeArithmetic(Arithmetic.ADD)
        self.compileExpression(expression2)
        self.vmWriter.writePop(Segment.TEMP, 0)
        self.vmWriter.writePop(Segment.POINTER, 1)
        self.vmWriter.writePush(Segment.TEMP, 0)
        self.vmWriter.writePop(Segment.THAT, 0)
    else:
      if node.children[3].tag == 'expression':
        expression = node.children[3]
        self.compileExpression(expression)
        self.writePop(identifier)

  def compileIf(self, node):
    label1 = '%s_%s_%d' % (self.className, self.subroutineName, self.subroutineLabelCounter)
    label2 = '%s_%s_%d' % (self.className, self.subroutineName, self.subroutineLabelCounter + 1)
    self.subroutineLabelCounter += 2
    statements = [child for child in node.children if child.tag == 'statements']
    self.compileExpression(node.children[2])
    self.vmWriter.writeArithmetic(Arithmetic.NOT)
    self.vmWriter.writeIf(label1)
    self.compileExpressionList(statements[0])
    self.vmWriter.writeGoto(label2)
    self.vmWriter.writeLabel(label1)
    if len(statements) == 2:
      self.compileExpressionList(statements[1])
    self.vmWriter.writeLabel(label2)

  def compileWhile(self, node):
    label1 = '%s_%s_%d' % (self.className, self.subroutineName, self.subroutineLabelCounter)
    label2 = '%s_%s_%d' % (self.className, self.subroutineName, self.subroutineLabelCounter + 1)
    self.subroutineLabelCounter += 2
    self.vmWriter.writeLabel(label1)
    self.compileExpression(node.children[2])
    self.vmWriter.writeArithmetic(Arithmetic.NOT)
    self.vmWriter.writeIf(label2)
    self.compileExpression(node.children[5])
    self.vmWriter.writeGoto(label1)
    self.vmWriter.writeLabel(label2)

  def compileDo(self, node):
    if node.children[2].data == '(' and node.children[4].data == ')':
      # subroutineName(expressionList)
      expressionList = node.children[3]
      self.compileExpressionList(expressionList)
      expressions = [child for child in expressionList.children if child.tag == 'expression']
      self.vmWriter.writeCall(node.children[1], len(expressions))
    elif node.children[2].data == '.':
      # (className|varName).subroutineName(expressionList)
      expressionList = node.children[5]
      self.compileExpressionList(expressionList)
      expressions = [child for child in expressionList.children if child.tag == 'expression']
      self.vmWriter.writeCall('%s.%s' % (node.children[1], node.children[3]), len(expressions))

  # Done
  def compileReturn(self):
    if self.subroutineType == 'constructor':
      self.vmWriter.writePush(Segment.POINTER, 0)
    elif self.subroutineType in ['method', 'function'] and self.returnType == 'void':
      self.vmWriter.writePush(Segment.CONST, 0)
    self.vmWriter.writeReturn()

  def handleOperator(self, operator):
    if operator == '+':
      self.vmWriter.writeArithmetic(Arithmetic.ADD)
    elif operator == '-':
      self.vmWriter.writeArithmetic(Arithmetic.SUB)
    elif operator == '*':
      self.vmWriter.writeCall('Math.multiply', 2)
    elif operator == '/':
      self.vmWriter.writeCall('Math.divide', 2)
    elif operator == '>':
      self.vmWriter.writeArithmetic(Arithmetic.GT)
    elif operator == '<':
      self.vmWriter.writeArithmetic(Arithmetic.LT)
    elif operator == '=':
      self.vmWriter.writeArithmetic(Arithmetic.EQ)
    elif operator == '&':
      self.vmWriter.writeArithmetic(Arithmetic.AND)
    elif operator == '|':
      self.vmWriter.writeArithmetic(Arithmetic.OR)
    elif operator == '~':
      self.vmWriter.writeArithmetic(Arithmetic.NOT)

  # Done
  def compileExpression(self, node):
    if len(node.children) == 1 and node.children[0].tag == 'term':
      self.compileTerm(node.children[0])
    elif len(node.children) == 2 and node.children[0].tag == 'symbol' and node.children[1].tag == 'term':
      self.compileTerm(node.children[1])
      if node.children[0].data == '-':
        self.vmWriter.writeArithmetic(Arithmetic.NEG)
    elif len(node.children) >= 3 and node.children[0].tag == 'term' and node.children[1].tag == 'symbol' and node.children[2].tag == 'term':
      self.compileTerm(node.children[0])
      self.compileTerm(node.children[2])
      self.handleOperator(node.children[1].data)
      for idx in range(3,len(node.children),2):
        if node.children[idx].tag == 'symbol' and node.children[idx+1].tag == 'term':
          self.compileTerm(node.children[idx+1])
          self.handleOperator(node.children[idx].data)

  def compileTerm(self, node):
    if node.children[0].tag == 'integerConstant':
      self.vmWriter.writePush(Segment.CONST, int(node.children[0].data))
    elif node.children[0].tag == 'stringConstant':
      self.vmWriter.writePush(Segment.CONST, len(node.children[0].data))
      self.vmWriter.writeCall('String.new', 1)
      for c in node.children[0].data:
        self.vmWriter.writePush(Segment.CONST, ord(c))
        self.vmWriter.writeCall('appendChar', 2)
    elif node.children[0].tag == 'keyword':
      if node.children[0].data == 'false':
        self.vmWriter.writePush(Segment.CONST, 0)
      elif node.children[0].data == 'true':
        self.vmWriter.writePush(Segment.CONST, -1)
      elif node.children[0].data == 'null':
        self.vmWriter.writePush(Segment.CONST, 0)
      elif node.children[0].data == 'this':
        self.vmWriter.writePush(Segment.ARG, 0)
    elif node.children[0].tag == 'identifier':
      if len(node.children) == 1:
        self.writePush(node.children[0].data) # varName
      elif len(node.children) == 4: 
        if node.children[1].data == '[' and node.children[3].data == ']':
          # varName[expression]
          self.compileTerm(node.children[2])
        elif node.children[1].data == '(' and node.children[3].data == ')':
          # subroutineName(expressionList)
          expressionList = node.children[2]
          self.compileExpressionList(expressionList)
          expressions = [child for child in expressionList.children if child.tag == 'expression']
          self.vmWriter.writeCall(node.children[0], len(expressions))  
      elif len(node.children) == 6:
        if node.children[1].data == '.' and node.children[3].data == '(' and node.children[5].data == ')':
          # object.subroutineName(expressionList)
          expressionList = node.children[2]
          self.compileExpressionList(expressionList)
          expressions = [child for child in expressionList.children if child.tag == 'expression']
          self.vmWriter.writeCall('%s.%s' % (node.children[0], node.children[2]), len(expressions))
    elif node.children[0].tag == 'symbol':
      if len(node.children) == 2 and node.children[1].tag == 'term':
        self.compileTerm(node.children[1])
        if node.children[0].data == '-':
          self.vmWriter.writeArithmetic(Arithmetic.NEG)
        elif node.children[1].data == '~':
          self.vmWriter.writeArithmetic(Arithmetic.NOT)

  def compileExpressionList(self, node):
    expressions = [child for child in node.children if child.tag == 'expression']
    for expression in expressions:
      self.compileExpression(expression)