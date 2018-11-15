from JackTokenizer import Token

class FSMEvent:
  KEYWORD = 1
  SYMBOL = 2
  IDENTIFIER = 3
  INT_CONST = 4
  STRING_CONST = 5
  DEFINITION = 6

DEFINITION = {
  'class': [
    {(FSMEvent.KEYWORD, 'class'): 1},
    {(FSMEvent.IDENTIFIER, None): 2},
    {(FSMEvent.SYMBOL, '{'): 3},
    {(FSMEvent.DEFINITION, 'classVarDec'): 3,(FSMEvent.DEFINITION, 'subroutineDec'): 4, (FSMEvent.SYMBOL,'}'): 5},
    {(FSMEvent.DEFINITION, 'subroutineDec'): 4, (FSMEvent.SYMBOL, '}'): 5}],
  'classVarDec': [
    {(FSMEvent.KEYWORD, 'static'): 1, (FSMEvent.KEYWORD,'field'): 1},
    {(FSMEvent.DEFINITION, 'type'): 2},
    {(FSMEvent.IDENTIFIER, None): 3},
    {(FSMEvent.SYMBOL, ','): 4, (FSMEvent.SYMBOL, ';'):5},
    {(FSMEvent.IDENTIFIER, None): 3}],
  'subroutineDec': [
    {(FSMEvent.KEYWORD, 'constructor'): 1,(FSMEvent.KEYWORD, 'function'): 1, (FSMEvent.KEYWORD, 'method'): 1},
    {(FSMEvent.KEYWORD, 'void'): 2,(FSMEvent.DEFINITION, 'type'): 2},
    {(FSMEvent.IDENTIFIER, None): 3},
    {(FSMEvent.SYMBOL, '('): 4},
    {(FSMEvent.DEFINITION, 'parameterList'): 5,(FSMEvent.SYMBOL, ')'): 6},
    {(FSMEvent.SYMBOL, ')'): 6},
    {(FSMEvent.DEFINITION, 'subroutineBody'): 7}],
  'type': [
    {(FSMEvent.KEYWORD, 'int'): 1, (FSMEvent.KEYWORD, 'char'): 1, (FSMEvent.KEYWORD, 'boolean'): 1, (FSMEvent.IDENTIFIER, None): 1}
  ],
  'parameterList': [
    {(FSMEvent.DEFINITION,'type'): 1, 'other': 4},
    {(FSMEvent.IDENTIFIER, None): 2},
    {(FSMEvent.SYMBOL, ','): 3, 'other': 4},
    {(FSMEvent.DEFINITION, 'type'): 1}],
  'subroutineBody': [
    {(FSMEvent.SYMBOL, '{'): 1},
    {(FSMEvent.DEFINITION, 'varDec'): 1,(FSMEvent.DEFINITION, 'statements'): 2},
    {(FSMEvent.SYMBOL, '}'): 3}],
  'varDec': [
    {(FSMEvent.KEYWORD, 'var'): 1},
    {(FSMEvent.DEFINITION, 'type'): 2},
    {(FSMEvent.IDENTIFIER, None): 3},
    {(FSMEvent.SYMBOL, ','): 4, (FSMEvent.SYMBOL, ';'): 5},
    {(FSMEvent.IDENTIFIER, None): 3}],
  'statements': [
    {(FSMEvent.DEFINITION, 'statement'): 0, 'other': 1}],
  'statement': [
    {(FSMEvent.DEFINITION, 'letStatement'): 1,(FSMEvent.DEFINITION, 'ifStatement'): 1, (FSMEvent.DEFINITION,'whileStatement'): 1, (FSMEvent.DEFINITION, 'doStatement'): 1,(FSMEvent.DEFINITION, 'returnStatement'): 1}
  ],
  'letStatement': [
    {(FSMEvent.KEYWORD, 'let'): 1},
    {(FSMEvent.IDENTIFIER, None): 2},
    {(FSMEvent.SYMBOL, '['): 3, (FSMEvent.SYMBOL, '='):6}, 
    {(FSMEvent.DEFINITION, 'expression'): 4},
    {(FSMEvent.SYMBOL, ']'): 5},
    {(FSMEvent.SYMBOL, '='): 6},
    {(FSMEvent.DEFINITION, 'expression'): 7},
    {(FSMEvent.SYMBOL, ';'): 8}],
  'ifStatement': [
    {(FSMEvent.KEYWORD, 'if'): 1},
    {(FSMEvent.SYMBOL, '('): 2},
    {(FSMEvent.DEFINITION, 'expression'): 3},
    {(FSMEvent.SYMBOL, ')'): 4},
    {(FSMEvent.SYMBOL, '{'): 5},
    {(FSMEvent.DEFINITION, 'statements'): 6},
    {(FSMEvent.SYMBOL, '}'): 7},
    {(FSMEvent.KEYWORD, 'else'): 8, 'other': 12},
    {(FSMEvent.SYMBOL, '{'): 9},
    {(FSMEvent.DEFINITION, 'statements'): 10},
    {(FSMEvent.SYMBOL, '}'): 11}],
  'whileStatement': [
    {(FSMEvent.KEYWORD, 'while'): 1},
    {(FSMEvent.SYMBOL, '('): 2},
    {(FSMEvent.DEFINITION, 'expression'): 3},
    {(FSMEvent.SYMBOL, ')'): 4},
    {(FSMEvent.SYMBOL, '{'): 5},
    {(FSMEvent.DEFINITION, 'statements'): 6},
    {(FSMEvent.SYMBOL, '}'): 7}],
  'doStatement': [
    {(FSMEvent.KEYWORD, 'do'): 1},
    {(FSMEvent.DEFINITION, 'subroutineCall'): 2},
    {(FSMEvent.SYMBOL, ';'): 3}],
  'returnStatement': [
    {(FSMEvent.KEYWORD, 'return'): 1},
    {(FSMEvent.DEFINITION, 'expression'): 2,(FSMEvent.SYMBOL, ';'): 3},
    {(FSMEvent.SYMBOL, ';'): 3}],
  'expression': [
    {(FSMEvent.DEFINITION, 'term'): 1},
    {(FSMEvent.DEFINITION, 'op'): 2, 'other': 3},
    {(FSMEvent.DEFINITION, 'term'): 1}],
  'term': [
    {(FSMEvent.IDENTIFIER, None): 1,(FSMEvent.SYMBOL, '('): 4,(FSMEvent.DEFINITION,'unaryOp'): 6,(FSMEvent.INT_CONST, None): 7,(FSMEvent.STRING_CONST, None): 7,(FSMEvent.DEFINITION,'keywordConstant'): 7,(FSMEvent.DEFINITION, 'subroutineCall'): 7},
    {(FSMEvent.SYMBOL, '['): 2, 'other': 8},
    {(FSMEvent.DEFINITION, 'expression'): 3},
    {(FSMEvent.SYMBOL, ']'): 7},
    {(FSMEvent.DEFINITION, 'expression'): 5},
    {(FSMEvent.SYMBOL, ')'): 7},
    {(FSMEvent.DEFINITION, 'term'): 7}],
  'subroutineCall': [
    {(FSMEvent.IDENTIFIER, None): 1},
    {(FSMEvent.SYMBOL, '('): 2, (FSMEvent.SYMBOL, '.'): 4},
    {(FSMEvent.DEFINITION, 'expressionList'): 3},
    {(FSMEvent.SYMBOL, ')'): 6},
    {(FSMEvent.IDENTIFIER, None): 5},
    {(FSMEvent.SYMBOL, '('): 2}],
  'expressionList': [
    {(FSMEvent.DEFINITION, 'expression'): 1, 'other': 3},
    {(FSMEvent.SYMBOL, ','): 2, 'other': 3},
    {(FSMEvent.DEFINITION, 'expression'): 1}],
  'op': [{(FSMEvent.SYMBOL, '+'): 1,(FSMEvent.SYMBOL, '-'): 1, (FSMEvent.SYMBOL, '*'): 1,
         (FSMEvent.SYMBOL, '/'): 1,(FSMEvent.SYMBOL, '&'): 1, (FSMEvent.SYMBOL, '|'): 1,
         (FSMEvent.SYMBOL, '<'): 1,(FSMEvent.SYMBOL, '>'): 1, (FSMEvent.SYMBOL, '='): 1}],
  'unaryOp': [{(FSMEvent.SYMBOL, '-'): 1, (FSMEvent.SYMBOL, '~'): 1}],
  'keywordConstant': [{(FSMEvent.KEYWORD, 'true'): 1, (FSMEvent.KEYWORD, 'false'): 1,
                       (FSMEvent.KEYWORD, 'null'): 1, (FSMEvent.KEYWORD, 'this'): 1}]
}

FINAL_STATE = {
  'class': {5: False},
  'classVarDec': {5: False},
  'type': {1: False},
  'subroutineDec': {7: False},
  'parameterList': {4: True},
  'subroutineBody': {3: False},
  'varDec': {5: False},
  'statements': {1: True},
  'statement': {1: False},
  'letStatement': {8: False},
  'ifStatement': {11: False, 12: True},
  'whileStatement': {7: False},
  'doStatement': {3: False},
  'returnStatement': {3: False},
  'expression': {3: True},
  'term': {7: False, 8: True},
  'subroutineCall': {6: False},
  'expressionList': {3: True},
  'op': {1: False},
  'unaryOp': {1: False},
  'keywordConstant': {1: False}
}

class Node:
  def __init__(self, tag, data):
    self.tag = tag
    self.data = data
    self.children = []
  
  def append(self, node):
    self.children.append(node)
  
  def tokensCount(self):
    total = 1
    for node in self.children:
        total += node.tokensCount()
    return total

class FSM:
  def __init__(self, definitionName, transitionTable, finalStates, tokenizer):
    self.definitionName = definitionName
    self.transitionTable = transitionTable
    self.tokenizer = tokenizer
    self.finalStates = finalStates
    self.state = 0

  def execute(self):
    rootNode = None
    nodes = []
    while self.tokenizer.hasMoreTokens() and self.state not in self.finalStates:
      self.tokenizer.advance()
      token = self.tokenizer.getToken()
      currentTokenId = self.tokenizer.currentTokenId
      tokenType = token[0]
      value = token[1]
      event = self.buildEvent(tokenType, value)
      # matching token with definitions
      self.tokenizer.retract()
      prevTokenId = self.tokenizer.currentTokenId
      selectedNode = None
      selectedTokenId = None
      selectedDefEvent = None
      for defEvent in [evt for evt in self.transitionTable[self.state] if type(evt) is tuple and evt[0] == FSMEvent.DEFINITION]:
          definitionName = defEvent[1]
          fsm = FSM(definitionName, DEFINITION[definitionName], FINAL_STATE[definitionName], self.tokenizer)
          node = fsm.execute()
          if node != None and (selectedNode == None or node.tokensCount() > selectedNode.tokensCount()):
              selectedNode = node
              selectedTokenId = self.tokenizer.currentTokenId
              selectedDefEvent = defEvent
          self.tokenizer.setTokenId(prevTokenId)
      if selectedNode != None and selectedTokenId != None:
          self.tokenizer.setTokenId(selectedTokenId)
          nodes.append(selectedNode)
          self.state = self.transitionTable[self.state][selectedDefEvent]
      elif event in self.transitionTable[self.state]:
          self.tokenizer.setTokenId(currentTokenId)
          node = self.buildNode(event, value)
          nodes.append(node)
          self.state = self.transitionTable[self.state][event]
      elif 'other' in self.transitionTable[self.state]:
          self.tokenizer.setTokenId(currentTokenId)
          self.state = self.transitionTable[self.state]['other']
      else:
          return None
    if self.state in self.finalStates and self.finalStates[self.state] == True:
        self.tokenizer.retract()
    rootNode = Node(self.definitionName, None)
    rootNode.children = nodes
    return rootNode

  def buildEvent(self, tokenType, token):
    if tokenType == Token.KEYWORD:
      return (FSMEvent.KEYWORD, token)
    elif tokenType == Token.IDENTIFIER:
      return (FSMEvent.IDENTIFIER, None)
    elif tokenType == Token.SYMBOL:
      return (FSMEvent.SYMBOL, token)
    elif tokenType == Token.STRING_CONST:
      return (FSMEvent.STRING_CONST, None)
    elif tokenType == Token.INT_CONST:
      return (FSMEvent.INT_CONST, None)
    return None

  def buildNode(self, event, token):
    tags = {FSMEvent.KEYWORD: 'keyword',
      FSMEvent.IDENTIFIER: 'identifier',
      FSMEvent.SYMBOL: 'symbol',
      FSMEvent.STRING_CONST: 'stringConstant',
      FSMEvent.INT_CONST: 'integerConstant'}

    if event[0] not in tags:
      return None

    return Node(tags[event[0]], token)