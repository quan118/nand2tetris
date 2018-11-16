#!/usr/bin/python
import sys
import os
from JackTokenizer import JackTokenizer
from FSM import DEFINITION, FINAL_STATE, FSM
from VMWriter import VMWriter
from CompilationEngine import CompilationEngine

if __name__=='__main__':
  input = sys.argv[1]
  srcFiles = []
  if os.path.isfile(input):
    srcFiles = [input]
  elif os.path.isdir(input):
    srcFiles = [os.path.join(input, file) for file in os.listdir(input) if os.path.splitext(file)[-1] == '.jack']
  
  for src in srcFiles:
    tokenizer = JackTokenizer(src)
    fsm = FSM('class', DEFINITION['class'], FINAL_STATE['class'], tokenizer)
    rootNode = fsm.execute()
    output = os.path.splitext(src)[0] + '.vm'
    vmWriter = VMWriter(output)
    compilationEngine = CompilationEngine(vmWriter, rootNode)
    vmWriter.close()
