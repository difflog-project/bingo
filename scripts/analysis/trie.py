#!/usr/bin/env python3

import sys

class Trie:
   def __init__(self):
      self.root = dict()


   def insert(self, entry, s):
      currDict = self.root
      for i in range(len(entry) - 1):
         currDict = currDict.setdefault(entry[i], {})
      currDict[entry[-1]] = s


   def retrieve(self, entry):     
      retVal = []
      currDicts = [self.root]
      for i in range(len(entry) - 1):
         newDicts = []
         if entry[i] == -1:
            for d in currDicts:
               newDicts.extend(d.values())
         else:
            for d in currDicts:
               if entry[i] in d: newDicts.append(d[entry[i]])
         currDicts = newDicts

      vals = []
      if entry[-1] == -1:
         for d in currDicts:
            vals.extend(d.values())
      else:
         for d in currDicts:
            if entry[-1] in d: vals.append(d[entry[-1]])
      return vals



class TrieTest:
   def __init__(self):
      print("Testing Trie")
      t = Trie()
      
      e1 = ('A', 1, 1, 1, 1)
      e2 = ('B', 1, 1, 1, 2)
      e3 = ('A', 1, 1, 1, 3)
      e4 = ('A', 1, 2, 1, 1)
      e5 = ('A', 1, 6, 1, 1)
      e6 = ('A', 1, 7, 1, 1)
      r1 = ('A', 1, -1, 1, -1)
      r2 = ('A', 1, -1, 1, 1)
      r3 = ('A', 1, 1, 1, -1)
      r4 = ('A', 1, 1, 1, 1)
      
      t.insert(e1, 'e1_str')
      t.insert(e2, 'e2_str')
      t.insert(e3, 'e3_str')
      t.insert(e4, 'e4_str')
      t.insert(e5, 'e5_str')
      t.insert(e6, 'e6_str')
      
      rvals = t.retrieve(r1)
      print ('{0}'.format(rvals))
      rvals = t.retrieve(r2)
      print ('{0}'.format(rvals))
      rvals = t.retrieve(r3)
      print ('{0}'.format(rvals))
      rvals = t.retrieve(r4)
      print ('{0}'.format(rvals))
      sys.exit()
