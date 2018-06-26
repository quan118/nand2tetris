#!/usr/bin/python
import sys
import os

class TokenType:
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
                print('end2:' + str(end))
                print('state2:' + str(state))
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
            return TokenType.INT_CONST
        elif state == 4:
            if self.isKeyword(token):
                return TokenType.KEYWORD
            else:
                return TokenType.IDENTIFIER
        elif state == 6:
            return TokenType.STRING_CONST
        elif state == 13 or state == 14:
            return TokenType.SYMBOL

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

    pass

class Node:
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data
        self.childrens = []

    def append(self, node):
        self.childrens.append(node)

    def tokensCount(self):
        total = 1
        for node in self.childrens:
            total += node.tokensCount()
        return total

class FSMEventType:
    KEYWORD = 1
    SYMBOL = 2
    IDENTIFIER = 3
    INT_CONST = 4
    STRING_CONST = 5
    DEFINITION = 6

DEFINITION = {
    'class': [{(FSMEventType.KEYWORD, 'class'): 1},
             {(FSMEventType.IDENTIFIER, None): 2},
             {(FSMEventType.SYMBOL, '{'): 3},
             {(FSMEventType.DEFINITION, 'classVarDec'): 3, (FSMEventType.DEFINITION, 'subroutineDec'): 4, (FSMEventType.SYMBOL, '}'): 5},
             {(FSMEventType.DEFINITION, 'subroutineDec'): 4, (FSMEventType.SYMBOL, '}'): 5}],
    'classVarDec': [{(FSMEventType.KEYWORD, 'static'): 1, (FSMEventType.KEYWORD, 'field'): 1},
                     {(FSMEventType.DEFINITION, 'type'): 2},
                     {(FSMEventType.IDENTIFIER, None): 3},
                     {(FSMEventType.SYMBOL, ','): 4, (FSMEventType.SYMBOL, ';'): 5},
                     {(FSMEventType.IDENTIFIER, None): 3}],
    'subroutineDec': [{(FSMEventType.KEYWORD, 'constructor'): 1, (FSMEventType.KEYWORD, 'function'): 1, (FSMEventType.KEYWORD, 'method'): 1},
                      {(FSMEventType.KEYWORD, 'void'): 2, (FSMEventType.DEFINITION, 'type'): 2},
                      {(FSMEventType.IDENTIFIER, None): 3},
                      {(FSMEventType.SYMBOL, '('): 4},
                      {(FSMEventType.DEFINITION, 'parameterList'): 5, (FSMEventType.SYMBOL, ')'): 6},
                      {(FSMEventType.SYMBOL, ')'): 6},
                      {(FSMEventType.DEFINITION, 'subroutineBody'): 7}],
    'type': [{(FSMEventType.KEYWORD, 'int'): 1, (FSMEventType.KEYWORD, 'char'): 1, (FSMEventType.KEYWORD, 'boolean'): 1, (FSMEventType.IDENTIFIER, None): 1}],
    'parameterList': [{(FSMEventType.DEFINITION,'type'): 1, 'other': 4},
                      {(FSMEventType.IDENTIFIER, None): 2},
                      {(FSMEventType.SYMBOL, ','): 3, 'other': 4},
                      {(FSMEventType.DEFINITION, 'type'): 1}],
    'subroutineBody': [{(FSMEventType.SYMBOL, '{'): 1},
                       {(FSMEventType.DEFINITION, 'varDec'): 1, (FSMEventType.DEFINITION, 'statements'): 2},
                       {(FSMEventType.SYMBOL, '}'): 3}],
    'varDec': [{(FSMEventType.KEYWORD, 'var'): 1},
               {(FSMEventType.DEFINITION, 'type'): 2},
               {(FSMEventType.IDENTIFIER, None): 3},
               {(FSMEventType.SYMBOL, ','): 4, (FSMEventType.SYMBOL, ';'): 5},
               {(FSMEventType.IDENTIFIER, None): 3}],
    'statements': [{(FSMEventType.DEFINITION, 'statement'): 0, 'other': 1}],
    'statement': [{(FSMEventType.DEFINITION, 'letStatement'): 1, (FSMEventType.DEFINITION, 'ifStatement'): 1, (FSMEventType.DEFINITION, 'whileStatement'): 1, (FSMEventType.DEFINITION, 'doStatement'): 1, (FSMEventType.DEFINITION, 'returnStatement'): 1}],
    'letStatement': [{(FSMEventType.KEYWORD, 'let'): 1},
                     {(FSMEventType.IDENTIFIER, None): 2},
                     {(FSMEventType.SYMBOL, '['): 3, (FSMEventType.SYMBOL, '='): 6}, 
                     {(FSMEventType.DEFINITION, 'expression'): 4},
                     {(FSMEventType.SYMBOL, ']'): 5},
                     {(FSMEventType.SYMBOL, '='): 6},
                     {(FSMEventType.DEFINITION, 'expression'): 7},
                     {(FSMEventType.SYMBOL, ';'): 8}],
    'ifStatement': [{(FSMEventType.KEYWORD, 'if'): 1},
                    {(FSMEventType.SYMBOL, '('): 2},
                    {(FSMEventType.DEFINITION, 'expression'): 3},
                    {(FSMEventType.SYMBOL, ')'): 4},
                    {(FSMEventType.SYMBOL, '{'): 5},
                    {(FSMEventType.DEFINITION, 'statements'): 6},
                    {(FSMEventType.SYMBOL, '}'): 7},
                    {(FSMEventType.KEYWORD, 'else'): 8, 'other': 12},
                    {(FSMEventType.SYMBOL, '{'): 9},
                    {(FSMEventType.DEFINITION, 'statements'): 10},
                    {(FSMEventType.SYMBOL, '}'): 11}],
    'whileStatement': [{(FSMEventType.KEYWORD, 'while'): 1},
                       {(FSMEventType.SYMBOL, '('): 2},
                       {(FSMEventType.DEFINITION, 'expression'): 3},
                       {(FSMEventType.SYMBOL, ')'): 4},
                       {(FSMEventType.SYMBOL, '{'): 5},
                       {(FSMEventType.DEFINITION, 'statements'): 6},
                       {(FSMEventType.SYMBOL, '}'): 7}],
    'doStatement': [{(FSMEventType.KEYWORD, 'do'): 1},
                    {(FSMEventType.DEFINITION, 'subroutineCall'): 2},
                    {(FSMEventType.SYMBOL, ';'): 3}],
    'returnStatement': [{(FSMEventType.KEYWORD, 'return'): 1},
                        {(FSMEventType.DEFINITION, 'expression'): 2, (FSMEventType.SYMBOL, ';'): 3},
                        {(FSMEventType.SYMBOL, ';'): 3}],
    'expression': [{(FSMEventType.DEFINITION, 'term'): 1},
                  {(FSMEventType.DEFINITION, 'op'): 2, 'other': 3},
                  {(FSMEventType.DEFINITION, 'term'): 1}],
    'term': [{(FSMEventType.IDENTIFIER, None): 1, (FSMEventType.SYMBOL, '('): 4, (FSMEventType.DEFINITION,'unaryOp'): 6, (FSMEventType.INT_CONST, None): 7, (FSMEventType.STRING_CONST, None): 7, (FSMEventType.DEFINITION, 'keywordConstant'): 7, (FSMEventType.DEFINITION, 'subroutineCall'): 7},
            {(FSMEventType.SYMBOL, '['): 2, 'other': 8},
            {(FSMEventType.DEFINITION, 'expression'): 3},
            {(FSMEventType.SYMBOL, ']'): 7},
            {(FSMEventType.DEFINITION, 'expression'): 5},
            {(FSMEventType.SYMBOL, ')'): 7},
            {(FSMEventType.DEFINITION, 'term'): 7}],
    'subroutineCall': [{(FSMEventType.IDENTIFIER, None): 1},
                       {(FSMEventType.SYMBOL, '('): 2, (FSMEventType.SYMBOL, '.'): 4},
                       {(FSMEventType.DEFINITION, 'expressionList'): 3},
                       {(FSMEventType.SYMBOL, ')'): 6},
                       {(FSMEventType.IDENTIFIER, None): 5},
                       {(FSMEventType.SYMBOL, '('): 2}],
    'expressionList': [{(FSMEventType.DEFINITION, 'expression'): 1, 'other': 3},
                       {(FSMEventType.SYMBOL, ','): 2, 'other': 3},
                       {(FSMEventType.DEFINITION, 'expression'): 1}],
    'op': [{(FSMEventType.SYMBOL, '+'): 1,(FSMEventType.SYMBOL, '-'): 1,(FSMEventType.SYMBOL, '*'): 1,
           (FSMEventType.SYMBOL, '/'): 1,(FSMEventType.SYMBOL, '&'): 1,(FSMEventType.SYMBOL, '|'): 1,
           (FSMEventType.SYMBOL, '<'): 1,(FSMEventType.SYMBOL, '>'): 1,(FSMEventType.SYMBOL, '='): 1}],
    'unaryOp': [{(FSMEventType.SYMBOL, '-'): 1, (FSMEventType.SYMBOL, '~'): 1}],
    'keywordConstant': [{(FSMEventType.KEYWORD, 'true'): 1, (FSMEventType.KEYWORD, 'false'): 1,
                         (FSMEventType.KEYWORD, 'null'): 1, (FSMEventType.KEYWORD, 'this'): 1}]
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

            for defEvent in [evt for evt in self.transitionTable[self.state] if type(evt) is tuple and evt[0] == FSMEventType.DEFINITION]:
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
        rootNode.childrens = nodes

        return rootNode

    def buildEvent(self, tokenType, token):
        if tokenType == TokenType.KEYWORD:
            return (FSMEventType.KEYWORD, token)
        elif tokenType == TokenType.IDENTIFIER:
            return (FSMEventType.IDENTIFIER, None)
        elif tokenType == TokenType.SYMBOL:
            return (FSMEventType.SYMBOL, token)
        elif tokenType == TokenType.STRING_CONST:
            return (FSMEventType.STRING_CONST, None)
        elif tokenType == TokenType.INT_CONST:
            return (FSMEventType.INT_CONST, None)
        return None
 
    def buildNode(self, event, token):
        tags = {FSMEventType.KEYWORD: 'keyword',
            FSMEventType.IDENTIFIER: 'identifier',
            FSMEventType.SYMBOL: 'symbol',
            FSMEventType.STRING_CONST: 'stringConstant',
            FSMEventType.INT_CONST: 'integerConstant'}
 
        if event[0] not in tags:
            return None
 
        return Node(tags[event[0]], token)
        
def nodeToString(node):
    result = ''
    data = node.data
    if data == '<':
        data = '&lt;'
    elif data == '>':
        data = '&gt;'
    elif data == '&':
        data = '&amp;'
    if len(node.childrens) <= 0:
        result += '<' + node.tag + '> '
        if data != None:
            result += data
        result += ' </' + node.tag + '>\n'
    else:
        if node.tag not in ['type', 'statement', 'subroutineCall', 'op', 'keywordConstant', 'unaryOp']:
            result += '<' + node.tag + '>\n'
        for child in node.childrens:
            result += nodeToString(child)
        if node.tag not in ['type', 'statement', 'subroutineCall', 'op', 'keywordConstant', 'unaryOp']:
            result += '</' + node.tag + '>\n'
    return result

if __name__=='__main__':
    inputfile = sys.argv[1]

    if os.path.isfile(inputfile):
        srcFiles = [inputfile]
    elif os.path.isdir(inputfile):
        srcFiles = [os.path.join(inputfile,file) for file in os.listdir(inputfile) if os.path.splitext(file)[-1] == '.jack']

    for srcFile in srcFiles:
        output = os.path.splitext(srcFile)[0] + '.xml'
        
        tokenizer = JackTokenizer(srcFile)
        fsm = FSM('class', DEFINITION['class'], FINAL_STATE['class'], tokenizer)
        node = fsm.execute()

        nodeByString = nodeToString(node)

        outputFile = open(output, 'w')
        outputFile.write(nodeByString)
        outputFile.close()