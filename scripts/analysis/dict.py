#!/usr/bin/env python3

# Command-line arguments:
#    analysis name (taint or datarace)
#    chord_output folder containing context-insensitive bddbddb/*.map files
#    chord_output folder containing context-sensitive bddbddb/*.map files
#    file whose tuples are the context-insensitive (ci) tuples 
#    file whose tuples are context-sensitive (cs) and correspond to the above ci tuples 
#    
# Output:
#    file containing the atom dictionary
#    file containing the tuple dictionary
#    file containing the annotated ci clauses 
#
# To be invoked from chord-fork folder.
# Example invocation:
# ./dict.py taint android_bench/stamp_output/YIgnoranceWriting/chord_output_mln-taint-problem 
#                 android_bench/stamp_output/YIgnoranceWriting/chord_output_mln-taint-oracle 
#                 android_bench/..../chord_output_mln-taint-problem/bnet/noaugment/named_cons_all.txt.pruned
#                 android_bench/..../chord_output_mln-taint-oracle/named_cons_all.txt

import logging
import re
import sys
from trie import TrieTest
from trie import Trie

# Uncomment the line below to do a simple test on Trie
# tst = TrieTest()

analysis = sys.argv[1]
probDir = sys.argv[2]
oracleDir = sys.argv[3]
tupleFileProb = sys.argv[4]
tupleFileOracle = sys.argv[5]

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

true = 1
false = 0

########################################################################################################################
# 1. Setup

if (analysis == 'taint'):
   matchingDoms = ['Z.map', 'M.map', 'V.map', 'U.map', 'F.map', 'I.map', 'L.map']
   mismatchingDoms = ['C.map', 'CL.map']
   relSign = {   'AssignPrim': ['U','U'],\
                 'CCL': ['C','CL'],\
                 'CICM': ['C','I','C','M'],\
                 'DUDU': ['C','U','C','U'],\
                 'LCL': ['L','CL'],\
                 'LoadPrim': ['U','V','F'],\
                 'LoadStatPrim': ['U','F'],\
                 'MU': ['M','U'],\
                 'MV': ['M','V'],\
                 'StorePrim': ['V','F','U'],\
                 'StoreStatPrim': ['F','U'],\
                 'flow': ['CL','CL'],\
                 'flowRefRef': ['V','V'],\
                 'flowRefPrim': ['V','U'],\
                 'flowPrimRef': ['U','V'],\
                 'flowPrimPrim': ['U','U'],\
                 'fpt': ['C','F','C'],\
                 'label': ['C','CL'],\
                 'labelIn': ['C','CL'],\
                 'labelPrim': ['C','U','CL'],\
                 'labelPrimFld': ['C','F','CL'],\
                 'labelPrimFldStat': ['F','CL'],\
                 'labelRef': ['C','V','CL'],\
                 'labelXferOut': ['C','CL'],\
                 'lflow': ['L','L'],\
                 'paramPrim': ['U','U','I'],\
                 'pt': ['C','V','C'],\
                 'reachableCM': ['C','M'],\
                 'returnPrim': ['U','U','I'],\
                 'sink': ['C','CL'],\
                 'sinkPrim': ['C','U','CL'],\
                 'sinkCtxtLabel': ['CL'],\
                 'srcCtxtLabel': ['CL'],\
                 'transferObjPrim': ['C','C','U'],\
                 'transferObjRef': ['C','C','V'],\
                 'transferPrimPrim': ['U','U'],\
                 'transferRefPrim': ['V','U'],\
                 'transferPrimRef': ['U','V'],\
                 'transferRefRef': ['V','V'],\
                 'varInLabel': ['V','L'],\
                 'varOutLabel': ['V','L'],\
                 'varInLabelPrim': ['U','L'],\
                 'varOutLabelPrim': ['U','L'] } 
elif (analysis == 'datarace'):
   matchingDoms = ['AS.map', 'P.map', 'V.map', 'Z.map', 'E.map', 'I.map', 'F.map', 'M.map', 'K.map']
   mismatchingDoms = ['C.map']
   relSign = {   'threadPH_cs': ['C','P','C','P'],\
                 'FC': ['F','C'],\
                 'parallelRaceHext': ['AS','C','E','AS','C','E'],\
                 'excludeSameThread': ['K'],\
                 'threadCICM': ['C','I','C','M'],\
                 'MPtail': ['M','P'],\
                 'CFC': ['C','F','C'],\
                 'PathEdge_cs': ['C','P','AS','AS','AS'],\
                 'threadStartI': ['I'],\
                 'datarace': ['AS','C','E','AS','C','E'],\
                 'statF': ['F'],\
                 'statE': ['E'],\
                 'simplePM_cs': ['C','P','C','M'],\
                 'EV': ['E','V'],\
                 'racePairs_cs': ['E','E'],\
                 'threadPM_cs': ['C','P','C'],\
                 'threadACH': ['AS','C','P'],\
                 'simplePH_cs': ['C','P','C','P'],\
                 'threadAC': ['AS','C'],\
                 'mhp_cs': ['C','P','AS','AS'],\
                 'escO': ['C'],\
                 'CEC': ['C','E','C'],\
                 'simplePT_cs': ['C','P','C','P'],\
                 'EF': ['E','F'],\
                 'PE': ['P','E'],\
                 'MPhead': ['M','P'],\
                 'CICM': ['C','I','C','M'],\
                 'MmethArg': ['M','Z','V'],\
                 'PP': ['P','P'],\
                 'PI': ['P','I'],\
                 'threadACM': ['AS','C','M'],\
                 'escapingRaceHext': ['AS','C','E','AS','C','E'],\
                 'SummEdge_cs': ['C','P','AS','AS','AS'],\
                 'unlockedRaceHext': ['AS','C','E','AS','C','E'],\
                 'CVC': ['C','V','C'],\
                 'mhe_cs': ['C','E','AS','AS'],\
                 'escE': ['E'] } 
else:
   print ("Unknown analysis!")
   sys.exit()

atomDictFileName = "atom_dict.txt"
tupleDictFileName = "tuple_dict.txt"
annotDictFileName = "annot_cons_all.txt"
atomDict = {}
tupleDict = {}
annotDict = {}

def readlines(filename):
   return [ line.strip() for line in open(filename) ]

def probfile(filename): 
   return '{0}/bddbddb/{1}'.format(probDir, filename) 

def oraclefile(filename): 
   return '{0}/bddbddb/{1}'.format(oracleDir, filename) 

def domName(relName, argNdx):
   argNameList = relSign[relName]
   return argNameList[argNdx]

def lit2Tuple(literal):
   return literal if not literal.startswith('NOT ') else literal[len('NOT '):]

def clause2Tuples(clause):
   return [ lit2Tuple(literal) for literal in clause ]

def clause2Antecedents(clause):
   return [ lit2Tuple(literal) for literal in clause[:-1] ]

def clause2Consequent(clause):
   consequent = clause[-1]
   assert not consequent.startswith('NOT ')
   return consequent

allCiTuples = set()
allCiClauses = set()
for line in readlines(tupleFileProb):
   clause = [ literal.strip() for literal in re.split(':|, ', line) ]
   clause = clause[1:]
   allCiClauses.add(tuple(clause))
   allCiTuples |= set(clause2Tuples(clause)) 

csTuplesTrie = Trie()
for line in readlines(tupleFileOracle):
   clause = [ literal.strip() for literal in re.split(':|, ', line) ]
   clause = clause[1:]
   for tup in clause2Tuples(clause):
      tupleParts = [ arg.strip() for arg in re.split('\(|\)|,', tup) ]
      relName, tupleArgsStr = tupleParts[0], tupleParts[1:-1] 
      tupleArgs = [int(s) for s in tupleArgsStr]
      csTuplesTrie.insert(tuple([relName] + tupleArgs), tup)

########################################################################################################################
# 2. Create atom dictionary 
#    atom dictionary maps an atom that could participate in the ci analysis to 
#                one or more corresponding atoms of the cs analysis
#    For matchingDoms, this mapping is one-to-one
#    For mismatchingDoms, this mapping could potentially be one-to-many
# 
#    Syntax for each atom: <dom_name>:<ndx_in_dom>
#    The first entry in each row is the ci atom. All other entries are the corresponding cs atoms
#
#    Typical entries in the atom dictionary:
#          CL:3 CL:3 CL:54 CL:55 CL:56 CL:57 CL:58
#          CL:4 CL:59 CL:4
#          C:2205 C:2205 
#          M:11 M:11

def getMap(lines, keyNdx, sepRE, zeroMapsToStar):
   key2line = {}
   lineNdx = 0
   for line in lines:
      parts = [ part.strip() for part in re.split(sepRE, line) ]
      key = parts[keyNdx]
      if (key not in key2line):
         key2line[key] = set()
      if (zeroMapsToStar == true and lineNdx == 0):
         key2line[key].add(-1)
      else:
         key2line[key].add(lineNdx)
      lineNdx += 1
   return key2line

with open(atomDictFileName, 'w') as atomDictFile:
   for d in matchingDoms:
      numLines = sum(1 for line in open(probfile(d)))
      dName = d[:-4]
      for i in range(numLines):
         atom = (dName, i)
         atomDict[atom] = [atom]
         atomStr = '{0}:{1}'.format(dName, i)
         atomDictFile.write('{0} {1}\n'.format(atomStr, atomStr))

   for d in mismatchingDoms:
      dName = d[:-4]   # remove extension ".map" from dom filename
      if (dName == 'C' and analysis == 'taint'):
         # The 0th element of the contexized object corresponds to the un-contextized objects used in ci analysis
         kIndex = 0
         # Syntax of an entry in domC
         # Context is an array of elements. 
         #     Each element has format stmt@<class_name: method_name(arg1,arg2....)>
         #     A context has the format [elem1,elem2,....]
         sepRegex = '>,|>]' 
         zeroMapsToStar = true
      elif (dName == 'C' and analysis == 'datarace'):
         # The 0th element of the contexized object corresponds to the un-contextized objects used in ci analysis
         kIndex = 0
         # Syntax of an entry in domC
         # Context is an array of elements. 
         #     Each element has format byte_code_offset!method_name(arg1;arg2;...)@class_name 
         #     A context has the format [elem1,elem2,....]
         sepRegex = ',' 
         zeroMapsToStar = true
      elif (dName == 'CL'):
         # Each element of domCL is a contextized label. It is represented as a pair <label,context>
         kIndex = 0
         sepRegex = ','
         zeroMapsToStar = false

      probDom = readlines(probfile(d))
      oracleDom = readlines(oraclefile(d))
      oracleDomMap = getMap(oracleDom, kIndex, sepRegex, zeroMapsToStar)
      probNdx = 0
      for line in probDom:
         p = [ part.strip() for part in re.split(sepRegex, line) ]
         csAtomList = [(dName,v) for v in oracleDomMap[p[kIndex]]]
         atomDict[(dName, probNdx)] = csAtomList
         ciAtomStr = '{0}:{1}'.format(dName, probNdx)
         csAtomStrList = ['{0}:{1}'.format(tup[0], tup[1]) for tup in csAtomList]
         csAtomStr = ' '.join(csAtomStrList) 
         atomDictFile.write('{0} {1}\n'.format(ciAtomStr, csAtomStr))
         probNdx += 1

atomDictFile.close()

########################################################################################################################
# 3. Create tuple dictionary 
#    tuple dictionary maps a tuple that could participate in the ci analysis to 
#                    one or more corresponding tuples of the cs analysis

def getAllCombos(ndx, arglst, relName):
   if (ndx == len(arglst)-1):
      domNameOfNdx = domName(relName, ndx)
      ciAtom = (domNameOfNdx, arglst[ndx])
      csAtomList = atomDict[ciAtom]
      newArgCombos = []
      for csAtom in csAtomList:
         newCombo = []
         newCombo.append(csAtom)
         newArgCombos.append(newCombo)
      return newArgCombos
   else:
      argCombos = getAllCombos(ndx+1, arglst, relName)
      newArgCombos = []
      domNameOfNdx = domName(relName, ndx)
      ciAtom = (domNameOfNdx, arglst[ndx])
      csAtomList = atomDict[ciAtom]
      for elem in argCombos:
         for csAtom in csAtomList:
            newCombo = []
            newCombo.append(csAtom)
            newCombo.extend(elem)
            newArgCombos.append(newCombo)
      return newArgCombos


with open(tupleDictFileName, 'w') as tupleDictFile:
   for ciTuple in allCiTuples:
      tupleParts = [ arg.strip() for arg in re.split('\(|\)|,', ciTuple) ]
      relName, tupleArgsStr = tupleParts[0], tupleParts[1:-1] 
      tupleArgs = [int(s) for s in tupleArgsStr]
      assert(len(tupleArgs) > 0)
      allArgCombos = getAllCombos(0, tupleArgs, relName)
      csTupleList = [] 
      for argCombo in allArgCombos:
         # remove the <dom_name>: that is prefixed to each dom index
         plainArgCombo = [arg[1] for arg in argCombo]
         csTuple = tuple([relName] + plainArgCombo)
         for tup in csTuplesTrie.retrieve(csTuple): csTupleList.append(tup)
      tupleDict[ciTuple] = csTupleList
      csTuplesStr = ' '.join(csTupleList)
      tupleDictFile.write('{0} {1}\n'.format(ciTuple, csTuplesStr))

tupleDictFile.close()

########################################################################################################################
# 3. Annotate the clauses in the ci derivation 


with open(annotDictFileName, 'w') as annotDictFile:
   for ciClause in allCiClauses:
      antecedents = clause2Antecedents(ciClause) 
      consequent = clause2Consequent(ciClause)
      hypothesis = true
      conclusion = true
      for antecedent in antecedents:
         csTupleList = tupleDict[antecedent] 
         if len(csTupleList) == 0: hypothesis = false
      csTupleList = tupleDict[consequent]
      if len(csTupleList) == 0: conclusion = false
      implication = false if hypothesis == true and conclusion == false else true
      ciClauseStr = ', '.join(ciClause)
      annotDictFile.write('{0}: {1}\n'.format('TRUE' if implication == true else 'FALSE', ciClauseStr))

annotDictFile.close()

