# combat script by v4c10xz
# (inspired by slu4 on youtube, i followed his tutorial!)
def look():								
	global pc								
	if source[pc] == ';':
		while source[pc] != '\n' and source[pc] != '\0': pc += 1		
	return source[pc]

def take():								
	global pc; c = look(); pc += 1; return c

def takestring(word):			
	global pc; copypc = pc
	for c in word:
		if take() != c: pc = copypc; return False
	return True

def next():								
	while look() == ' ' or look() == '\t' or look() == '\n' or look() == '\r': take()
	return look()

def takenext(c):					
	if next() == c: take(); return True
	else: return False

def isdigit(c): return (c >= '0' and c <= '9')									
def isalpha(c): return ((c >= 'a' and c <= 'z') or (c >= 'a' and c <= 'z'))
def isalnum(c): return (isdigit(c) or isalpha(c))
def isadd(c): return (c == '+' or c == '-')
def ismul(c): return (c == '*' or c == '/')

def takenextalnum():
	alnum = ""
	if isalpha(next()):
		while isalnum(look()): alnum += take()
	return alnum


def booleanfactor(act):
	inv = takenext('~'); e = expression(act); b = e[1]; next()
	if (e[0] == 'i'): 																			
		if takestring("=="): b = (b == mathexpression(act))
		elif takestring("~="): b = (b != mathexpression(act))
		elif takestring("<="): b = (b <= mathexpression(act))
		elif takestring("<"): b = (b < mathexpression(act))
		elif takestring(">="): b = (b >= mathexpression(act))
		elif takestring(">"): b = (b > mathexpression(act))
	else:
		if takestring("=="): b = (b == stringexpression(act))
		elif takestring("~="): b = (b != stringexpression(act))
		else: b = (b != "")
	return act[0] and (b != inv)											

def booleanterm(act):
	b = booleanfactor(act)
	while takenext('and'): b = b & booleanfactor(act)		
	return b

def booleanexpression(act):
	b = booleanterm(act)
	while takenext('or'): b = b | booleanterm(act)			
	return b

def mathfactor(act):
	m = 0
	if takenext('('):
		m = mathexpression(act)
		if not takenext(')'): error("missing ')'")
	elif isdigit(next()):
		while isdigit(look()): m = 10 * m + ord(take()) - ord('0')
	elif takestring("value("):
		s = string(act)
		if act[0] and s.isdigit(): m = int(s)
		if not takenext(')'): error("missing ')'")
	else:
		ident = takenextalnum()
		if ident not in variable or variable[ident][0] != 'i': error("unknown variable")
		elif act[0]: m = variable[ident][1]
	return m

def mathterm(act):
	m = mathfactor(act)
	while ismul(next()):
		c = take(); m2 = mathfactor(act)
		if c == '*': m = m * m2													
		else: m = m / m2															
	return m

def mathexpression(act):
	c = next()																				
	m = mathterm(act)
	if c == '-': m = -m
	while isadd(next()):
		c = take(); m2 = mathterm(act)
		if c == '+': m = m + m2												
		else: m = m - m2														
	return m

def string(act):
	s = ""
	if takenext('\"'):															
		while not takestring("\""):
			if look() == '\0': error("unexpected eof")
			if takestring("\\n"): s += '\n'
			else: s += take()
	elif takestring("string("):												
		s = str(mathexpression(act))
		if not takenext(')'): error("missing ')'")
	elif takestring("prompt()"):
		if act[0]: s = input()
	else: 
		ident = takenextalnum()
		if ident in variable and variable[ident][0] == 's':	s = variable[ident][1]
		else: error("not a string")
	return s

def stringexpression(act):
	s = string(act)
	while takenext('+'): s += string(act)							
	return s

def expression(act):
	global pc; copypc = pc; ident = takenextalnum(); pc = copypc			
	if next() == '\"' or ident == "string" or ident == "prompt" or (ident in variable and variable[ident][0] == 's'):
		return ('s', stringexpression(act))
	else: return ('i', mathexpression(act))

def dowhile(act):
	global pc; local = [act[0]]; pc_while = pc				
	while booleanexpression(local): block(local); pc = pc_while
	block([False])																		

def doifelse(act):
	b = booleanexpression(act)
	if act[0] and b: block(act)												
	else: block([False])
	next()
	if takestring("else"):														
		if act[0] and not b: block(act)
		else: block([False])

def dogosub(act):
	global pc
	ident = takenextalnum()
	if ident not in variable or variable[ident][0] != 'p': error("unknown subroutine")
	ret = pc; pc = variable[ident][1]; block(act); pc = ret		
def dosubdef():
	global pc
	ident = takenextalnum()
	if ident == "": error ("missing subroutine identifier")
	variable[ident] = ('p', pc); block([False])

def doassign(act):																				
	ident = takenextalnum()
	if not takenext('=') or ident == "": error("unknown statement")
	e = expression(act)
	if act[0] or ident not in variable: variable[ident] = e		

def dobreak(act):
	if act[0]: act[0] = False													

def doprint(act):
	while True:																							
		e = expression(act)
		if act[0]: print(e[1], end="")
		if not takenext(','): return
		
def statement(act):
	if takestring("print"): doprint(act)
	elif takestring("if"): doifelse(act)
	elif takestring("while"): dowhile(act)
	elif takestring("break"): dobreak(act) 
	elif takestring("fire"): dogosub(act)
	elif takestring("event"): dosubdef()
	else: doassign(act)							

def block(act):
	if takenext('{'):
		while not takenext('}'): block(act)
	else: statement(act)

def program():
	act = [True]
	while next() != '\0': block(act)

def error(text):
	s = source[:pc].rfind("\n") + 1; e = source.find("\n", pc)
	print("\nerror " + text + " in line " + str(source[:pc].count("\n") + 1) + ": '" + source[s:pc] + "_" + source[pc:e] + "'\n")
	exit(1)


pc = 0; variable = {}										

import sys                                          
if len(sys.argv) < 2: print('usage: combat.py <sourcefile>'); exit(1)
try: f = open(sys.argv[1], 'r')																				
except: print("error: can't find source file \'" + sys.argv[1] + "\'."); exit(1)
source = f.read() + '\0'; f.close()																			

program()

