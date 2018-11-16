#!/user/bin/python
import unittest

class Kind:
  STATIC = 1
  FIELD = 2
  ARG = 3
  VAR = 4

class SymbolTable:
  def __init__(self):
    self.reset()
  
  def reset(self):
    self.table = {}
    self.kindCounter = {Kind.STATIC: 0, Kind.FIELD: 0, Kind.ARG: 0, Kind.VAR: 0}

  def define(self, name, type, kind):
    self.table[name] = (type, kind, self.kindCounter[kind])
    self.kindCounter[kind] += 1
  
  def kindOf(self, name):
    return self.table[name][1]
  
  def typeOf(self, name):
    if name not in self.table:
      return None
    return self.table[name][0]

  def indexOf(self, name):
    if name not in self.table:
      return -1
    return self.table[name][2]

  def numberOfKind(self, kind):
    return self.kindCounter[kind]

class TestSymbolTable(unittest.TestCase):
  def setUp(self):
    self.tbl = SymbolTable()
    self.tbl.define('x', 'int', Kind.FIELD)
    self.tbl.define('y', 'int', Kind.FIELD)
    self.tbl.define('c', 'int', Kind.STATIC)
    self.tbl.define('this', 'Point', Kind.ARG)
    self.tbl.define('dx', 'int', Kind.VAR)

  def tearDown(self):
    del self.tbl

  def test_kindOf(self):
    self.assertEqual(self.tbl.kindOf('x'), Kind.FIELD)
    self.assertEqual(self.tbl.kindOf('y'), Kind.FIELD)
    self.assertEqual(self.tbl.kindOf('c'), Kind.STATIC)
    self.assertEqual(self.tbl.kindOf('this'), Kind.ARG)
    self.assertEqual(self.tbl.kindOf('dx'), Kind.VAR)

  def test_typeOf(self):
    self.assertEqual(self.tbl.typeOf('x'), 'int')
    self.assertEqual(self.tbl.typeOf('y'), 'int')
    self.assertEqual(self.tbl.typeOf('c'), 'int')
    self.assertEqual(self.tbl.typeOf('this'), 'Point')
    self.assertEqual(self.tbl.typeOf('dx'), 'int')

  def test_indexOf(self):
    self.assertEqual(self.tbl.indexOf('x'), 0)
    self.assertEqual(self.tbl.indexOf('y'), 1)
    self.assertEqual(self.tbl.indexOf('c'), 0)
    self.assertEqual(self.tbl.indexOf('this'), 0)
    self.assertEqual(self.tbl.indexOf('dx'), 0)

if __name__=='__main__':
  unittest.main()


