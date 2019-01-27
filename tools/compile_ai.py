""" WIP AI compiler """

import ast

def parse(s):
  return ast.parse(s)

def compile(a, ops=[]):
  """ Convert an AST into a list of ops """
  ops = []

  for f in ast.iter_fields(a):
    #print(f)
    pass

  for n in ast.iter_child_nodes(a):
    if isinstance(n,ast.Call):
      #print(a._fields)
      ops += (n.func.id,n.args)
      
    ops += compile(n)
  
  return ops

def assemble(ops):
  """ Converts a list of ops to machine code interpretable by the Broodwar AI engine """

  for op in ops:
    pass

print(compile(parse("""
start_town()
build_start(1, command_center, 80)
build_start(4, scv, 80)
#if enemyowns(barracks) or enemyowns(gateway) or enemyowns(spawning_pool):
#  build_start(1, spawning_pool)
""")))