#!/usr/bin/python

class Token:
  KEYWORD = 1
  SYMBOL = 2
  IDENTIFIER = 3
  INT_CONST = 4
  STRING_CONST = 5

class JackTokenizer:
  def __init__(self, filename):
    self.initTransitionTable()

    f = open(filename, 'r')
    self.data = f.read()
    f.close()

    self.tokens = []
    self.currentTokenId = -1
    self.parsing()

  def initTransitionTable(self):
    self.transitionTable = [
      {'digit': 1, 'letter': 3, '_': 3, '"': 5, '/': 7, 'symbol': 14, 'other': 0},    # state 0
      {'digit': 1, 'other': 2},       # state 1
      {},     # state 2
      {'digit': 3, 'letter': 3, 'other': 4},      # state 3
      {},     # state 4
      {'"': 6, 'newline': 6, 'other': 5}, # state 5
      {}, # state 6
      {'/': 8, '*': 10, 'other': 13}, # state 7
      {'newline': 9, 'other': 8}, # state 8
      {}, # state 9
      {'*': 11, 'other': 10}, # state 10
      {'/': 12, 'other': 10}, # state 11
      {}, # state 12
      {}, # state 13
      {} # state 14
    ]

  def parsing(self):
    state = start = end = 0
    nextState = None
    while end < len(self.data):
      c = self.data[end]
      nextState = None
      if self.isDigit(c) and 'digit' in self.transitionTable[state]:
        nextState = self.transitionTable[state]['digit']
      elif self.isLetter(c) and 'letter' in self.transitionTable[state]:
        nextState = self.transitionTable[state]['letter']
      elif self.isNewline(c) and 'newline' in self.transitionTable[state]:
        nextState = self.transitionTable[state]['newline']
      elif c in self.transitionTable[state]:
        nextState = self.transitionTable[state][c]
      if nextState == None and self.isSymbol(c) and 'symbol' in self.transitionTable[state]:
        nextState = self.transitionTable[state]['symbol']
      if nextState == None and 'other' in self.transitionTable[state]:
        nextState = self.transitionTable[state]['other']
      if nextState == None:
        print("Error occured")
        print('c:' + c)
        print('end: %d' % end)
        print('state: %d' % state)
        break
      state = nextState
      end += 1
      
      if state in [0, 9, 12]: # comment tokens
        if state == 9:
          end -= 1
        start = end
        state = 0
      elif state in [2, 4, 13]: # retract final states
        end -= 1
        value = self.data[start:end]
        tokenType = self.tokenType(state, value)
        self.tokens.append((tokenType, value))
        start = end
        state = 0
      elif state in [6, 14]: # final states
        if state == 6:
          value = self.data[start+1:end-1]
        else:
          value = self.data[start:end]
        tokenType = self.tokenType(state, value)
        self.tokens.append((tokenType, value))
        start = end
        state = 0

  def hasMoreTokens(self):
    return self.currentTokenId < len(self.tokens) - 1

  def advance(self):
    if self.currentTokenId < len(self.tokens):
      self.currentTokenId += 1

  def retract(self):
    if self.currentTokenId > 0:
      self.currentTokenId -= 1

  def getToken(self):
    return self.tokens[self.currentTokenId]

  def setTokenId(self, tokenId):
    self.currentTokenId = tokenId

  def tokenType(self, state, token):
    if state == 2:
      return Token.INT_CONST
    elif state == 4:
      if self.isKeyword(token):
        return Token.KEYWORD
      else:
        return Token.IDENTIFIER
    elif state == 6:
      return Token.STRING_CONST
    elif state == 13 or state == 14:
      return Token.SYMBOL

  def isDigit(self, ch):
    return ch.isdigit()

  def isLetter(self, ch):
    return ch.isalpha()

  def isSymbol(self, ch):
    return ch in ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']

  def isNewline(self, ch):
    return ch == '\n'

  def isKeyword(self, token):
    return token in ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']