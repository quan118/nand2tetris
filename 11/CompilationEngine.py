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
    elif node.tag == 'statement':
      self.compileStatement(node)
    elif node.tag == 'letStatement':
      self.compileLet(node)
    elif node.tag == 'ifStatement':
      self.compileIf(node)
    elif node.tag == 'whileStatement':
      self.compileWhile(node)
    elif node.tag == 'doStatement':
      self.compileDo(node)
    elif node.tag == 'returnStatement':
      self.compileReturn(node)
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
    type = self.compileType(node.children[1])

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
        self.returnType = node.children[1].data
        self.subroutineName = node.children[2].data
      else:
        return
      parameterList = next(child for child in node.children if child.tag == 'parameterList')
      self.compileParameterList(parameterList)
      subroutineBody = next(child for child in node.children if child.tag == 'subroutineBody')
      self.compileSubroutineBody(subroutineBody)

  # Done
  def compileParameterList(self, node):
    if self.subroutineType in ['method']:
      self.subroutineSymbolTable.define('this', self.className, Kind.ARG)
    for child in node.children:
      # if child.tag == 'keyword':
      #   type = node.data
      # elif child.tag == 'identifier':
      #   self.subroutineSymbolTable.define(child.data, type, Kind.ARG)
      if child.tag == 'type':
        type = self.compileType(child)
      elif child.tag == 'identifier':
        self.subroutineSymbolTable.define(child.data, type, Kind.ARG)

  def compileSubroutineCall(self, node):
    if node.children[1].data == '(' and node.children[3].data == ')':
      # subroutineName(expressionList)
      self.vmWriter.writePush(Segment.POINTER, 0)
      expressionList = node.children[2]
      self.compileExpressionList(expressionList)
      expressions = [child for child in expressionList.children if child.tag == 'expression']
      self.vmWriter.writeCall('%s.%s' % (self.className, node.children[0].data), len(expressions) + 1)
    elif node.children[1].data == '.':
      # (className|varName).subroutineName(expressionList)
      identifier = node.children[0].data
      expressionList = node.children[4]
      expressions = [child for child in expressionList.children if child.tag == 'expression']
      if self.subroutineSymbolTable.typeOf(identifier) != None:
        # localVarName.subroutineName(expressionList)
        type = self.subroutineSymbolTable.typeOf(identifier)
        index = self.subroutineSymbolTable.indexOf(identifier)
        kind = self.subroutineSymbolTable.kindOf(identifier)
        if kind == Kind.ARG:
          self.vmWriter.writePush(Segment.ARG, index)
        elif kind == Kind.VAR:
          self.vmWriter.writePush(Segment.LOCAL, index)
        self.compileExpressionList(expressionList)
        self.vmWriter.writeCall('%s.%s' % (type, node.children[2].data), len(expressions) + 1)
      elif self.classSymbolTable.typeOf(identifier):
        # fieldName.subroutineName(expressionList)
        type = self.classSymbolTable.typeOf(identifier)
        index = self.classSymbolTable.indexOf(identifier)
        kind = self.classSymbolTable.kindOf(identifier)
        if kind == Kind.FIELD:
          self.vmWriter.writePush(Segment.THIS, index)
        elif kind == Kind.STATIC:
          self.vmWriter.writePush(Segment.STATIC, index)
        self.compileExpressionList(expressionList)
        self.vmWriter.writeCall('%s.%s' % (type, node.children[2].data), len(expressions) + 1)
      else:
        self.compileExpressionList(expressionList)
        self.vmWriter.writeCall('%s.%s' % (node.children[0].data, node.children[2].data), len(expressions))

  # Done
  def compileSubroutineBody(self, node):
    varDecs = [child for child in node.children if child.tag == 'varDec']
    for varDec in varDecs:
      self.compileVarDec(varDec)
    
    nLocals = self.subroutineSymbolTable.numberOfKind(Kind.VAR)

    if self.subroutineType == 'constructor':
      self.vmWriter.writeFunction('%s.new' % self.className, nLocals)
      objSize = self.classSymbolTable.numberOfKind(Kind.FIELD)
      self.vmWriter.writePush(Segment.CONST, objSize)
      self.vmWriter.writeCall('Memory.alloc', 1)
      self.vmWriter.writePop(Segment.POINTER, 0)
    elif self.subroutineType == 'method':
      self.vmWriter.writeFunction('%s.%s' % (self.className, self.subroutineName), nLocals)
      self.vmWriter.writePush(Segment.ARG, 0)
      self.vmWriter.writePop(Segment.POINTER, 0)
    elif self.subroutineType == 'function':
      self.vmWriter.writeFunction('%s.%s' % (self.className, self.subroutineName), nLocals)

    for child in node.children:
      if child.tag != 'varDec':
        self.compile(child)

  # Done
  def compileVarDec(self, node):
    # Kind
    kind = Kind.VAR

    # Type
    type = self.compileType(node.children[1])
    
    # identifiers
    identifiers = [child for child in node.children if child.tag == 'identifier']

    for identifier in identifiers:
      self.subroutineSymbolTable.define(identifier.data, type, kind)

  def compileStatement(self, node):
    for child in node.children:
      self.compile(child)

  def compileType(self, node):
    return node.children[0].data

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
    self.compileStatements(statements[0])
    self.vmWriter.writeGoto(label2)
    self.vmWriter.writeLabel(label1)
    if len(statements) == 2:
      self.compileStatements(statements[1])
    self.vmWriter.writeLabel(label2)

  def compileWhile(self, node):
    label1 = '%s_%s_%d' % (self.className, self.subroutineName, self.subroutineLabelCounter)
    label2 = '%s_%s_%d' % (self.className, self.subroutineName, self.subroutineLabelCounter + 1)
    self.subroutineLabelCounter += 2
    self.vmWriter.writeLabel(label1)
    self.compileExpression(node.children[2])
    self.vmWriter.writeArithmetic(Arithmetic.NOT)
    self.vmWriter.writeIf(label2)
    self.compileStatements(node.children[5])
    self.vmWriter.writeGoto(label1)
    self.vmWriter.writeLabel(label2)

  def compileDo(self, node):
    self.compileSubroutineCall(node.children[1])
    self.vmWriter.writePop(Segment.TEMP, 0)

  # Done
  def compileReturn(self, node):
    if self.subroutineType == 'constructor':
      self.vmWriter.writePush(Segment.POINTER, 0)
    elif self.subroutineType in ['method', 'function']:
      if self.returnType == 'void':
        self.vmWriter.writePush(Segment.CONST, 0)
      else:
        if len(node.children) > 1 and node.children[1].tag == 'expression':
          self.compileExpression(node.children[1])
    self.vmWriter.writeReturn()

  def compileOp(self, node):
    self.handleOperator(node.children[0].data)

  def compileUnaryOp(self, node):
    if node.children[0].data == '-':
      self.vmWriter.writeArithmetic(Arithmetic.NEG)
    elif node.children[0].data == '~':
      self.vmWriter.writeArithmetic(Arithmetic.NOT)

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
    elif len(node.children) == 2 and node.children[0].tag == 'op' and node.children[1].tag == 'term':
      self.compileTerm(node.children[1])
      self.compileOp(node.children[0])
      # if node.children[0].data == '-':
      #   self.vmWriter.writeArithmetic(Arithmetic.NEG)
    elif len(node.children) >= 3 and node.children[0].tag == 'term' and node.children[1].tag == 'op' and node.children[2].tag == 'term':
      self.compileTerm(node.children[0])
      self.compileTerm(node.children[2])
      self.compileOp(node.children[1])
      # self.handleOperator(node.children[1].data)
      for idx in range(3,len(node.children),2):
        if node.children[idx].tag == 'op' and node.children[idx+1].tag == 'term':
          self.compileTerm(node.children[idx+1])
          # self.handleOperator(node.children[idx].data)
          self.compileOp(node.children[idx])

  def compileKeywordConstant(self, node):
    if node.children[0].data == 'false':
      self.vmWriter.writePush(Segment.CONST, 0)
    elif node.children[0].data == 'true':
      self.vmWriter.writePush(Segment.CONST, 1)
      self.vmWriter.writeArithmetic(Arithmetic.NEG)
    elif node.children[0].data == 'null':
      self.vmWriter.writePush(Segment.CONST, 0)
    elif node.children[0].data == 'this':
      self.vmWriter.writePush(Segment.POINTER, 0)

  def compileTerm(self, node):
    if node.children[0].tag == 'integerConstant':
      self.vmWriter.writePush(Segment.CONST, int(node.children[0].data))
    elif node.children[0].tag == 'stringConstant':
      self.vmWriter.writePush(Segment.CONST, len(node.children[0].data))
      self.vmWriter.writeCall('String.new', 1)
      for c in node.children[0].data:
        self.vmWriter.writePush(Segment.CONST, ord(c))
        self.vmWriter.writeCall('String.appendChar', 2)
    elif node.children[0].tag == 'keywordConstant':
      self.compileKeywordConstant(node.children[0])
    elif node.children[0].tag == 'identifier':
      if len(node.children) == 1:
        self.writePush(node.children[0].data) # varName
      elif len(node.children) == 4: 
        if node.children[1].data == '[' and node.children[3].data == ']':
          # varName[expression]
          self.compileExpression(node.children[2])
          self.writePush(node.children[0].data)
          self.vmWriter.writeArithmetic(Arithmetic.ADD)
          self.vmWriter.writePop(Segment.POINTER, 1)
          self.vmWriter.writePush(Segment.THAT, 0)
        elif node.children[1].data == '(' and node.children[3].data == ')':
          # subroutineName(expressionList)
          expressionList = node.children[2]
          self.compileExpressionList(expressionList)
          expressions = [child for child in expressionList.children if child.tag == 'expression']
          self.vmWriter.writeCall('%s.%s' % (self.className, node.children[0].data), len(expressions))
    elif node.children[0].tag == 'symbol':
      if len(node.children) == 2 and node.children[1].tag == 'term':
        self.compileTerm(node.children[1])
        if node.children[0].data == '-':
          self.vmWriter.writeArithmetic(Arithmetic.NEG)
        elif node.children[1].data == '~':
          self.vmWriter.writeArithmetic(Arithmetic.NOT)
      elif len(node.children) == 3 and node.children[1].tag == 'expression':
        self.compileExpression(node.children[1])
    elif node.children[0].tag == 'unaryOp':
      self.compileTerm(node.children[1])
      self.compileUnaryOp(node.children[0])
    elif node.children[0].tag == 'subroutineCall':
      self.compileSubroutineCall(node.children[0])

  def compileExpressionList(self, node):
    expressions = [child for child in node.children if child.tag == 'expression']
    for expression in expressions:
      self.compileExpression(expression)