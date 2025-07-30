#!/usr/bin/python
from __future__ import print_function

#from utillc.__init__ import *


__version__ = "0.11.2"

utillc_version = __version__
__all__ = ( 'EKOX', 'EKON', 'STACK', 'EKO', 'TYPE', 'EKOI', 'EKOT', 'EKOH', 'EKOF', 'test', 'Bool', 'ntimes', 'LINE', 'resizeImage', 'count_parameters', 'parse_args', 'Counter', 'ENV', 'print_nothing', 'print_everything', 'noeko', 'NS', 'WARNING', 'INFO', 'ERROR', 'LOG', 'EKOIT', 'yeseko', 'ekostream', 'to_file', 'TIME',	'get_notebook_dir', 'default_opt')
#__all__ = ('listp', 'dump', 'parse')

#import pymf
from datetime import datetime
import platform
python3Running = platform.python_version() == 3
#print (platform.python_version()[0])
try :
	import matplotlib
	import matplotlib.pyplot as plt
except Exception as e :
	pass
	#print('Warning : matplotlib not available ' + str(e))

import os
import argparse
from collections import namedtuple
import threading

import sys, os, os.path
#from time import *
import time as _time
from time import gmtime, strftime
from datetime import timedelta


import numpy as np
import re
import PIL
from PIL import Image
try :
	import tempfile
	import atexit
except :
	pass

class NoException(Exception):
	"""Exception never raised
	"""
	def __init__(self, expression, message):
		self.expression = expression
		self.message = message

import inspect

default_opt = {}
noeko_modules = {}

eko_config = {
	'add_time' : False
}

if "NOEKOFN" in os.environ :
	disc = os.environ["NOEKOFN"]
	disc = disc.split(",")
	disc = dict(zip(disc, range(len(disc))))
	noeko_modules.update(disc)
#print(noeko_modules)

def noeko() :
	ff = get_source_filename()
	fn = str(ff[1])
	EKOX(fn)
	noeko_modules[fn] = 1

def yeseko() :
	ff = get_source_filename()
	EKOX(ff)
	fn = str(ff[1])
	noeko_modules.pop(fn, None)


class Counter :
	i = 0
	def __init__(self, v : int=0) : self.i = v
	def __int__(self): return self.i
	def __str__(self): return str(self.i)
	def inc(self) : self.i += 1


def info(self, x) : 
	return EKOT(x, llevel=1)


# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables -- all in one file.
# -----------------------------------------------------------------------------

tokens = (

	'FLOAT', 'NAME','NUMBER', 'EKON', 'EKOX',  'EKOT', 'LBRACE', 'RBRACE',
	'PLUS','MINUS','TIMES','DIVIDE','EQUALS', 'ASSIGN',
	'LPAREN','RPAREN', 'COMMA', 'STRING', 'RBRACKET', 'LBRACKET', 'DOT', 'DIVIDE2', "COLON"
	)


# Tokens
t_COMMA	   = r'\,'
t_EKON	  = r'EKON'
t_EKOX	  = r'EKOX'
t_EKOT	  = r'EKOT'
t_PLUS	  = r'\+'
t_MINUS	  = r'-'
t_COLON	  = r':'
t_TIMES	  = r'\*'
t_DIVIDE  = r'/'
t_DIVIDE2  = r'//'
t_ASSIGN  = r'='
t_EQUALS  = r'=='
t_LPAREN  = r'\('
t_DOT  = r'.'
t_RPAREN  = r'\)'

t_LBRACKET	= r'\['
t_RBRACKET	= r'\]'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_NAME	  = r'[a-zA-Z_][a-zA-Z0-9_]*'

t_STRING  = r'\"([^\\\"]|\\.)*\"' + '|' +  r"\'([^\\\']|\\.)*\'" 

def t_FLOAT(t):
	#r'\d+\.\d+'
	# a better regex taking exponents into account:
	r'[-+]?[0-9]+(\.([0-9]+)?([eE][-+]?[0-9]+)?|[eE][-+]?[0-9]+)'		 
	t.value = float(t.value)
	return t

def t_NUMBER(t):
	r'\d+'
	try:
		t.value = int(t.value)
	except ValueError:
		print("Integer value too large %d", t.value)
		t.value = 0
	return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
	r'\n+'
	t.lexer.lineno += t.value.count("\n")
	
def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)
	
# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# Parsing rules

precedence = (
	('left','PLUS','MINUS', 'COLON'),
	('left','TIMES','DIVIDE'),
	('right','UMINUS'),
	)

# dictionary of names
names = { }

def p_top(t) :
	'top : expressions'
	t[0] = t[1]

def p_top_1(t) :
	'top : EKON expressions'
	t[0] = t[2]
def p_top_2(t) :
	'top : EKOX expressions'
	t[0] = t[2]
	
def p_top_3(t) :
	'top : EKOT expressions'
	t[0] = t[2]

def p_expressions_1(t) :
	'expressions : expression'
	t[0] = t[1]

def p_expressions_2(t) :
	'expressions : expressions COMMA expression'
	t[0] =	( ',', t[1], t[3])


def p_expression_binop(t):
	'''expression : expression PLUS expression
				  | expression MINUS expression
				  | expression TIMES expression
				  | expression EQUALS expression
				  | NAME ASSIGN expression
				  | expression DIVIDE2 expression
				  | expression DIVIDE expression'''
	t[0] = (t[2], t[1], t[3])

def p_expression_dot(t) :
	''' name : expression DOT dot_names'''
	t[0] = ('.', t[1], t[3])
	
def p_expression_uminus(t):

	'expression : MINUS expression %prec UMINUS'
	t[0] = ('-', "", t[2])
	
def p_expression_dict(t):
	'expression : LBRACE expressionsCC RBRACE'
	t[0] = ('', "{", t[2])
	
def p_expression_group(t):	  
	'''expression : LPAREN expressions RPAREN
				  | expression LBRACKET expressionsBE RBRACKET
				  | name LPAREN expressionsV RPAREN
	'''
	if t[1] == '(' :
		t[0] = ("", '(', t[2])
	elif t[2] == '[' :
		t[0] = (t[1], '[', t[3])
	else:
		t[0] = (t[1], '(', t[3])

def p_expression_number(t):
	'expression : NUMBER'
	t[0] = str(t[1])

def p_expression_float(t):
	'expression : FLOAT'
	t[0] = str(t[1])

def p_expression_name(t):
	'expression : name'
	t[0] = t[1]

def p_expression_string(t):
	'expression : STRING'
	t[0] = t[1]

def p_dot_names_1(t) :
	'dot_names : NAME'
	t[0] = t[1]
"""
def p_dot_names_2(t) :
	'dot_names : dot_names DOT NAME'
	t[0] = t[1] + '.' + t[2]
"""
	
def p_expressionsBE_1(t):
	'expressionsBE : '
	t[0] = ""

def p_expressionsBE_2(t):
	'expressionsBE : expressionsBEE COMMA expressionsBE'
	t[0] =	( ',', t[1], t[3])

def p_expressionsCC_1(t):
	'expressionsCC : expressionsCC1'
	t[0] = t[1]

def p_expressionsCC_2(t):
	'expressionsCC : expressionsCC COMMA expressionsCC1'
	t[0] =	( ',', t[1], t[3])

def p_expressionsCC1_1(t):
	'expressionsCC1 : expression COLON expression'
	t[0] =	( ':', t[1], t[3])


	
def p_expressionsBE_3(t):
	'expressionsBE : expressionsBEE'
	t[0] = t[1]

def p_expressionsBEE_0(t):
	'expressionsBEE : '
	t[0] = ""
def p_expressionsBEE_1(t):
	'expressionsBEE : expression'
	t[0] = t[1]
def p_expressionsBEE_2(t):
	'expressionsBEE : COLON'
	t[0] = t[1]

def p_expressionsBEEXX_3(t):
	'expressionsBEE : expression COLON expressionsBEE'
	t[0] =	( ':', t[1], t[3])
	

def p_expressionsV_1(t):
	'expressionsV : '
	t[0] = ""

def p_expressionsV_2(t):
	'expressionsV : expressions'
	t[0] = t[1]

def Xp_name_2(t) :
	''' name : name DOT NAME'''
	t[0] = t[1] + '.' + t[3]
	
def p_name_1(t) :
	''' name : NAME'''
	t[0] = t[1]
	
def p_error(t):
	#print("Syntax error at '%s', did you modify the file during execution?" % t.value)
	pass

def tostr(x) :
	if isinstance(x, str) :
		return x
	else :
		return x[0] + ','.join(map(tostr, x[1]))


inv = {
	'{' : '}',
	'(' : ')',
	'[' : ']'}



def listp(e) :
	if isinstance(e, tuple) and e[0] == ',' :
		return listp(e[1]) + [e[2]]
	else :
		return [e]


def dump(e) :

	if isinstance(e, str) :
		r = e
	elif e[0] in ['.', ',', "+", "-", "*", "/", ":", "==", "//", "=" ] :
		sep = "" if e[0] in [".", ":"] else " "
		r = dump(e[1]) + sep + e[0] + sep + dump(e[2])
	else :
		r = dump(e[0]) + e[1] + dump(e[2]) + inv[e[1]]
	return r


try :
	import ply.yacc as yacc
except :
	print("pip install lex ply")
	
yacc_parser = yacc.yacc()

def parseE(s) :
	e = yacc_parser.parse(s)
	return e


#print( strftime("Starting up %I:%M:%S %p", _time.localtime()))

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

start = _time.time()
KK=100
INFO = 100
WARNING = INFO+KK
ERROR = WARNING+KK
LOG = ERROR+KK
levels = [ ("INFO", INFO),
		   ("WARNING", WARNING),
		   ("ERROR" , ERROR),
		   ("LOG", LOG)]

def I2T(n) :
	return levels[n//KK - 1][0]
	
def T2I(s) :
	d = dict( zip([ e[0] for e in levels],
				  [ e[1] for e in levels]))
	return d[s]

defe = LOG

try :
	oeeko = os.environ["MINEKOLEVEL"]
	try :
		oeeko = T2I(oeeko)
	except Exception as e:
		pass
	defe = int(oeeko)
except Exception as e:
	defe = ERROR

_readEL = True
_el = 1000

try :
	_noReadEnv = os.environ["EKONOREADENV"] != ""
except KeyError:
	_noReadEnv = False

if _noReadEnv:
	_readEL = False
else :
	_readEL = True
	import argparse

_readEL = True


donothing = lambda : 1
donothing1 = lambda x : 1


def EKO_init_end(cause, r) :
	return 1
	if r <= 0:
		#EKOX(cause)
		print('www')
		return 1
	else :
		#print('xxxx\n')
		EKO_init_end(cause, r-1)
		print('yyy')
		os._exit(0)
	return 1



def el():
	global _el, _readEL
	#print("read el ", _readEL)
	if _readEL:
		__parser = None #argparse.ArgumentParser(add_help=False)
		InitArgs(__parser)
		SetOptions(__parser)
		ainit_ = EKO_init_end(cause='start', r=0)

		try:
			pass
			atexit.register(EKO_init_end, cause='end', r=2)
		except :
			pass
	return _el

Bool = lambda x : { '': True, 'yes' : True, 'no' : False, 'True' : True, 'False' : False , False : False, True : True}[x]

def InitArgs(parser):
	global _el, _readEL, options_
	try:
		parser.add_argument('--minekolevel', dest='el', default=defe, type=int, help='log level')
		parser.add_argument('--verbose', default=False, type=bool, help='enable verbose mode')
		options_, rem = parser.parse_known_args()
	except Exception as e:
		#print("exception : " , str(e))
		pass

def print_nothing() :
	global _el, _readEL
	_readEL = False
	_el = 1000000

def print_everything() :
	global defe, _el, _readEL
	_readEL = False
	_el = 0
	defe = 0


def get_source_filename(llevel = 0) :
	llevel = llevel+1
	frame = inspect.currentframe()
	ofrl =	len(inspect.getouterframes(frame))
	#ff = inspect.getouterframes(frame)[(1 + llevel) % ofrl]
	ff = inspect.getouterframes(frame)[(1 + llevel) % ofrl]
	relpath = os.path.relpath(ff[1])
	nbb = relpath.count("..")
	if nbb > 2 and os.path.isabs(ff[1]) :
		tff = ff
	else :
		tff = (ff[0], relpath, ff[2], ff[3], ff[4])
	return tff
	
def in_notebook() :
	ff = get_source_filename(0)
	fn = str(ff[1])
	return "ipython" in fn

if in_notebook() :
	print_everything()

def SetOptions(parser):
	global _el, _readEL, options_
	try :
		_el = int(os.environ["MINEKOLEVEL"])
	except :
		_el = -1
	try :
		try:
			_el = options_.el
			#print ("_el ", _el)
		except AttributeError:
			pass
		if options_.verbose:
			_el = -1
		#_readEL = False
	except :
		pass
	#print("xxx _el ", _el)

ekodict = {}
ekodict2 = {}
ekostream = sys.stderr

try :
	eko_stream = os.environ["EKOSTREAM"]
	try :
		ekostream = open(eko_stream, "w")
	except Exception as e:
		pass
except Exception as e:
	ekostream = sys.stdout
	pass



doeko = True

class ET :
	etab = ""
	def __init__(self) :
		ET.etab = "" + ET.etab
	def __enter__(self):
		return self
	def __exit__(self, _, __, ___):
		ET.etab = ET.etab[1:]

def to_file(fn) :
	ekostream = open(fn, "w")

def print1(x, color=False, noeko=False,n=INFO, opt={}) :
	ff = get_source_filename(1)
	fn = str(ff[1])
	
	#print("doeko", (doeko, noeko, defe, n))


	if doeko  and not noeko and fn not in noeko_modules and	 n >= defe:
		if color : ekostream.write(bcolors.WARNING)
		ekostream.write(ET.etab + x + "\n")
		if color : ekostream.write(bcolors.ENDC)
		ekostream.flush()
	return x

threadIDS = {}

def lab(n) :
	return "[" + I2T(n) + "] " if n > INFO else ""


def tt(_loc, n=INFO, opt={}):
	global start, ekodict
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)
	ll = _loc + '_' + str(len(ff))
	x = _time.time()
	elapsed = (x - start)
	start = x
	now = int(elapsed *1000)

	#print1('dict=' + str(ekodict))
	#print1('x=' + str(x))
	#print1('ll=' + str(ll))

	if ll in ekodict :
		then = ekodict[ll]
		ppp = '/' + str(int((x - then)*1000)).zfill(4)
	else:
		ppp = ''
	ekodict[ll] = x


	thid = threading.get_ident()
	if thid not in threadIDS :
		threadIDS[thid] = len(threadIDS)
	# display thread id if number of active thread > 2
	dthid = '(' + str(threadIDS[thid]).zfill(2) + ')' if len(threadIDS) > 2 else ""
	timestamp =	 datetime.now().strftime("%H:%M:%S:%f") if NS(**eko_config).add_time else ""
	ttt = str(now).zfill(4) + ppp + 'ms' + timestamp
	z = default_opt.copy()
	z.update(opt)
	if "with_date" in z :
		ttt = ttt + "-" + datetime.now().strftime("%d/%m %H:%M:%S") 
	return '[' + ttt +	']' + dthid + ' '

def TIME(f, n=10) :
	"""
	calls f with current time (sec), filename, line in source file
	"""
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	xx = _time.time()
	for i in range(n):
		r = f((xx, ff[1], ff[2]))
	yy = _time.time()
	return ((yy-xx)/n, r)

def LINE() :
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	return str(ff[1]) +	 ':' + str(ff[2])

def stringify(x) :
	pattern = 'stringify\((\w)\)'
	regex = re.compile(pattern)
	r = ""
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	match = regex.search(ff[4][0])
	g = match.groups()[0]
	rr = ff[4][0].replace(' ','').replace('SS','').replace('(','').replace(')','').replace('\n','')
	return g


def ntimes(closure = lambda x : sys.exit(0), max=-1) :
	global ekodict2
	if max >= 0 :
		closure = lambda x : 0
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)
	ll = str(len(ff))
	if ll in ekodict2 :
		ekodict2[ll] = ekodict2[ll] + 1
		closure(ekodict2[ll])
		if ekodict2[ll] >= max :
			sys.exit(0)
	else:
		ekodict2[ll] = 0
	

def dictify(x) :
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)
	pattern = 'dictify\( *\((\w)(, *\w)* *\) *\)'
	pattern = 'dictify\(\((\w)(, \w)\)\)'
	regex = re.compile(pattern)
	r = ""
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	EKOX(ff)
	EKOX(ff[4][0])
	match = regex.search(ff[4][0])
	return dict(zip([_x.replace(' ','').replace(',', '') for _x in match.groups()], list(x)))


every_dict = {}

def everySeconds(closure, intervalInSeconds, tag="a") :
	if tag not in every_dict :
		every_dict[tag]	 = datetime.now()
	else :
		now = datetime.now()
		duration = now - every_dict[tag]
		duration_in_s = duration.total_seconds() 
		if duration_in_s > intervalInSeconds :
			closure()
			every_dict[tag]	 = datetime.now()


def FE(x) :
	return EKOX(x, INFO, withprint=False, llevel=1, pattern="print")

def ROWCOLNUMBER(x) :
	h = x.shape[0]
	w = x.shape[1]
	xx = np.hstack((np.asarray([range(h)]).T, x))
	xx = np.vstack((np.asarray([range(w+1)]) + -1, xx))
	return xx

def STACK(llevel=0) :
	"""
	print the call stack from this point
	"""
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1:]
	pp = '\n'.join([ str(e[1]) + ":" + str(e[2]) + ": fct=" + str(e[3]) + ", line=" + str(e[4][0].strip()) for e in ff])
	print1("Stack_________________________:\n" + pp + "\n___________________________\n")

def info(x) : return EKOX(x, llevel=1, n=INFO)


def EKOQ(*args, n=INFO,pref="", color=False, check=False, withprint=True, llevel=0, pattern="EKOX"):
	EKON(*(args[1:]), n=n, pref=pref, color=color, check=check, withprint=withprint, llevel=llevel+1, pattern="EKOQ")
	


def EKON(*args,n=INFO,pref="", color=False, check=False, withprint=True, llevel=0, pattern="EKOX", opt={}):
	"""
	output x variable name followed by its value (in an emacs error format)
	"""
	#print("xxx", len(args))
	if len(args) == 1 :
		EKOX(args[0], n=n, llevel=llevel+1, pattern="EKON", istuple=len(args)>1, opt=opt, pref=pref)	
	else :
		EKOX(args, n=n, llevel=llevel+1, pattern="EKON", istuple=len(args)>1, opt=opt, pref=pref)			 
		
		
def EKOX(x, n=INFO, pref="", color=False, check=False, withprint=True, llevel=0, pattern="EKOX",
		 istuple=False, opt={}):
	"""
	output x variable name followed by its value (in an emacs error format)
	"""
	r = ""
	ff = get_source_filename(llevel)
	inl = ""
	try :
			inl = "\n" if isinstance(x, np.ndarray) else ""
	except :
		pass
	prt = (check and not x) or n >= el()
	#print ("n=", n, ', el()=', el(), prt)

	ppat = pattern + "("
	#print("coucou x =", x)
	#print((prt, n, el()))


	if prt :

		loc = str(ff[1]) +	':' + str(ff[2]) 
		strng = str(x)
		preamb = loc + ": " if withprint else ""
		if (ff[4] != None) :
			ids =  str(ff[4][0])
			doublecommainid1 = ('EKOX((' in ids and ('))' in ids))
			#t2 = lambda :	ids.index('))') ==	(len(ids) - 2)
			doublecommainid = doublecommainid1
			if (isinstance(x, tuple) and doublecommainid) or istuple:
				tkin = str(ff[4][0])
				#print("=================AA ", tkin)	
				#tk11 = tkin.replace(ppat, '').replace(')\n', '').strip('\n ')
				tk11 = tkin
				tk1 = tk11.split(',')
				#print("=================BBB ", tk11)
				#print("=================", "\n".join(tk1))
				try :
					#print("a2")					
					ppp = parseE(tk11)
					#print("jjjjjjjjjjjjj", dump(ppp))
					#print("jjjjjjjjjjjjj", ppp)					
					#print(pattern)
					#print("ppp", ppp, tk11)
					ppp = ppp[2]
					if pattern in ["EKOX", "EKON"] and ppp[0] == "" and ppp[1] == "(" :
						ppp = ppp[2]
					#print("a3")
					listppp = listp(ppp)
					listppp = [ e for e in listppp if e[0] != t_ASSIGN]
					tk = list(map(dump, listppp))
					
					#print("listp kkkkkkkkkkkkkkk", listppp, len(listppp), len(list(x)))
					#print("tk", tk, list(x))
					
					if len(tk) == len(list(x)) :
						tkkkk = str(ff[4][0]).replace(ppat, '').replace(')\n', '').strip('\n ')[1:-1].split(',')
						#print("xxxxxxxxxxxxxxxxxxxxxxxxxx")
						def ses(sx, sv) :
							ll, ll1 = [ "''", '""' ], ''.join([ sx[0], sx[-1]])
							hasquote = ll1 in ll
							strng = str(sv)
							ppref = "\n" if '\n' in strng else ""					
							return sx if hasquote else sx + '=' + ppref + strng 
						
						tkk = ', '.join([ses(sx, sv) for sx, sv in zip(tk, list(x))])
					else :
						tkk = str(ff[4][0]).replace(ppat, '').replace(')\n', '').strip('\n ') + '=' + inl + pref + strng
				except Exception as ee:
					print("exception", ee)
					#raise ee
					tkk=inl + pref + strng
					try :
						ppref = "\n" if '\n' in strng else ""					
						tkk = str(ff[4][0]).replace(ppat, '').replace(')\n', '').strip('\n ') + '=' + inl + ppref + pref + strng
					except :
						pass						
			else :
				# simple
				#print("zaza", ff[4][0], ppat)
				tk11 = ff[4][0]
				ppp = parseE(tk11)
				#print("llllllllllll", ppp)
				#print("jjjjjjjjjjjjj", dump(ppp))
				#print("ggggggggggggggg", dump(ppp[2]))
				
				tkk=inl + pref + strng
				try :
					tkk = str(ff[4][0]).replace(ppat, '').replace(')\n', '').strip('\n ') + '=' + inl + pref + strng
					tkk = dump(ppp[2]) + '=' + inl + pref + strng
					listppp = listp(ppp[2])
					listppp = [ e for e in listppp if e[0] != t_ASSIGN]
					tkk = list(map(dump, listppp))
					ppref = "\n" if '\n' in strng else ""					
					tkk = tkk[0] + "=" + ppref + strng
					#print("hhhhhhhhhhhhhhhh", tkk)					   
				except :
					pass
			if '\n' in strng :
				strng = '\n' + strng
	
			#print('ssssssssssssssssssssssss', n, lab(n))
			r = print1(preamb + tt(loc, n=n, opt=opt) + lab(n) + tkk + '.', color=color, noeko=not withprint, n=n)
		else:
			r = print1(preamb + tt(loc, n=n, opt=opt) + lab(n) + str(ff[3]) + '=' + inl + pref + strng + '.', color=color, noeko= not withprint, n=n)

	if check and not x :
		assert(c)
	return r

cwd = os.getcwd()		 
pcwd = lambda : EKOX(cwd)
#print_cwd = pcwd() 

def EKOX_old(x,n=INFO,pref=""):
	r = ""
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	inl = ""
	try :
		inl = "\n" if isinstance(x, ndarray) else ""
	except :
		pass
	#print "el=", n, ', ', el()
	if (n >= el()):

		loc = str(ff[1]) +	':' + str(ff[2])
		strng = str(x)
		if '\n' in strng :
			strng = '\n' + strng
		if (ff[4] != None) :
			r = print1(loc +  ': ' + tt(loc) + str(ff[4][0]).replace('EKOX(', '').replace(')\n', '').strip('\n ') + '=' + inl + pref + strng + '.')
		else:
			r = print1(loc +  ': ' + tt(loc) + str(ff[3]) + '=' + inl + pref + strng + '.')
	return r

numImages = 0
tempDir = "/kaggle/working/images"
tempDir = "/tmp/images"

#print(tempDir)
def EKOP(x,n=INFO, dir=tempDir, sz=500, label="", width=1000, height = 500, labels=None):
	"""
	create an bar plot image from an array
	"""
	r = ""
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	fn = tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=dir, prefix=label)
	#EKOX(fn)
	#EKOX(TYPE(x))
	if (n < el()): return ""
	if not isinstance(x, np.ndarray) :
		x = np.asarray(x)
	dpi = 100
	try :
		fig = plt.figure(figsize=(float(width)/dpi, float(height)/dpi), dpi=dpi)
		if len(x.shape) == 1 :
			plt.plot(x)
		else :
			if labels is None : labels= [""] * x.shape[0]
			t = range(x.shape[0])
			for i in range(x.shape[1]) : plt.plot(t, x[:,i], label=labels[i])
			plt.legend()
		fig.savefig(fn)
		plt.close()
	except :
		print('matplotlib not available')		 
		pass
	loc = (ff[1]) +	 ':' + str(ff[2])
	inl = "\n" if isinstance(x, np.ndarray) else ""
	if (n >= el()):
		if (ff[4] != None) :
			r = print1(loc +  ': ' + tt(loc, opt=opt) + str(ff[4][0]).replace('EKOP(', '').replace(')\n', '').strip('\n ') + '=' + inl + '[[file:' + str(fn.name) + ']].')
		else:
			r = print1(loc +  ': ' + tt(loc, opt=opt) + str(ff[3]) + '=' + inl +  '[[file:' + str(fn.name) + ']].')
	return r

	
def EKOF(fx,n=INFO, dir=tempDir, sz=500, label="", suffix=".png", width=1000, height = 500, llevel=0, opt={}):	  
	"""
	matplotlib genraic interface
	"""
	r = ""
	frame = inspect.currentframe()
	#ff = inspect.getouterframes(frame)[1]
	ofrl =	len(inspect.getouterframes(frame))
	ff = inspect.getouterframes(frame)[(1 + llevel) % ofrl]	   
	fn = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, dir=dir, prefix=label)
	if (n < el()): return ""
	dpi = 100
	try :
		fig = plt.figure(figsize=(float(width)/dpi, float(height)/dpi), dpi=dpi)
		fx(fig)
		fig.savefig(fn, dpi=dpi)
		plt.close(fig)
	except :
		print('matplotlib not available')
		pass
	loc = (ff[1]) +	 ':' + str(ff[2])
	inl = "\n"
	if (n >= el()):
		if (ff[4] != None) :
			r = print1(loc +  ': ' + tt(loc, opt=opt) + str(ff[4][0]).replace('EKOP(', '').replace(')\n', '').strip('\n ') + '=' + inl + '[[file:' + str(fn.name) + ']].')
		else:
			r = print1(loc +  ': ' + tt(loc, opt=opt) + str(ff[3]) + '=' + inl +  '[[file:' + str(fn.name) + ']].')
	return r



def EKOH(x,n=INFO, dir=tempDir, sz=500., label="", width=1000, height = 500, bins=50):
	"""
	"""
	def histo(fig) :
		matplotlib.pyplot.hist(x, bins=bins)
	return EKOF(histo, n, dir, sz, label, ".png", width, height, llevel=1)



def EKOB(x,n=INFO, dir=tempDir, sz=500, label="", ):

	import cv2
	"""
	create an bar plot image from an array
	"""
	r = ""
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	fn = tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=dir, prefix=label)
	#EKOX(fn)
	EKOX(TYPE(x))
	if (n < el()): return ""
	if not isinstance(x, np.ndarray) :
		x = np.asarray(x)
	n = x.shape[0]
	max = x.max()
	x = x / max * sz
	thick = 2
	pas = thick*2
	img = np.ones((n*pas, sz, 3))
	red = (0, 0, 255)
	try :
		[ cv2.line(img, (i*pas, sz), (i*pas, sz - int(e*sz)), red, 2) for i,e in enumerate(x) ]
		cv2.imwrite(fn.name, img)
	except :
		pass
	loc = (ff[1]) +	 ':' + str(ff[2])
	inl = "\n" if isinstance(x, np.ndarray) else ""
	if (n >= el()):
		if (ff[4] != None) :
			r = print1(loc +  ': ' + tt(loc, opt=opt) + str(ff[4][0]).replace('EKOB(', '').replace(')\n', '').strip('\n ') + '=' + inl + '[[file:' + str(fn.name) + ']].')
		else:
			r = print1(loc +  ': ' + tt(loc, opt=opt) + str(ff[3]) + '=' + inl +  '[[file:' + str(fn.name) + ']].')
	return r

def EKOIT(x,n=INFO, small=True,dir=tempDir, sz=350, label="", llevel=0):
	EKOI(x[:,:,::-1],n=INFO, small=True,dir=tempDir, sz=350, label="",	llevel=llevel+1)

def EKOICHW(x,n=INFO, small=True,dir=tempDir, sz=350, label="", llevel=0):
	EKOI(x.transpose(1,2,0),n=INFO, small=True,dir=tempDir, sz=350, label="",  llevel=llevel+1)	   


def EKOI(x,n=INFO, small=True,dir=tempDir, sz=350, label="", llevel=0, opt={}):
	"""
	output x variable name, create an image based on x value and output a string which cause emacs to display the image
	"""
	r = ""
	ff = get_source_filename(llevel)
	os.makedirs(dir, exist_ok = True) 
	fn = tempfile.NamedTemporaryFile(suffix='.png', delete=False, dir=dir, prefix=label)
	#EKOX(fn)

	if (n < el()): return ""
	if x is None : return ""
	if not isinstance(x, np.ndarray) :
		x = np.asarray(x)
	if len(x.shape) == 2 :
		x = np.stack([x]*3, axis=2) 


	ltp = [ float, np.float16, np.float32, np.float64, np.floating]
	try :
		ltp.append(np.float128)
	except :
		pass
	#EKOX(x.dtype)
	dtt = x.dtype
	if dtt in ltp :
		mean, std, min_, max_  = np.mean(x.astype(float)), np.std(x.astype(float)), np.min(x), np.max(x)
		if mean > 1. or max_ > 1. :
			x = x.astype(int)
		else :
			x = (x * 255).astype(int)
	#EKO()
	if small :
		fx = sz / x.shape[0]
		fy = fx
		#print(fx)
		pimg = Image.fromarray(x.astype(np.uint8))

		wpercent = (sz/float(pimg.size[0]))
		hsize = int((float(pimg.size[1])*float(wpercent)))
		pimg = pimg.resize((sz,hsize), Image.Resampling.LANCZOS)
		x = np.array(pimg)

	#EKO()
	#EKOX(TYPE(x))
	#cv2.imwrite(fn.name, x[:,:,::-1])
	pilim(x).save(fn.name)
	loc = (ff[1]) +	 ':' + str(ff[2])
	inl = "\n" if isinstance(x, np.ndarray) else ""
	if (n >= el()):
		if (ff[4] != None) :
			r = print1(loc +  ': ' + tt(loc, opt=opt) + str(ff[4][0]).replace('EKOX(', '').replace(')\n', '').strip('\n ') + '=' + inl + '[[file:' + str(fn.name) + ']].')
		else:
			r = print1(loc +  ': ' + tt(loc, opt=opt) + str(ff[3]) + '=' + inl +  '[[file:' + str(fn.name) + ']].')
	return r

def EKOZ(x):
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	inl = "\n" if isinstance(x, ndarray) else ""
	if (ff[4] != None) :
		return str(ff[4][0]).replace('EKOX(', '').replace(')\n', '').strip('\n ')
	else:
		return str(ff[3])

def testeko(x):
	EKOX(x)

a='eko'
#testeko(a)

def SEKO(x) :
	r = ""
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	if (ff[4] != None) :
		loc = str(ff[1]) +	':' + str(ff[2])
		r += loc +	': ' + tt(loc) + '=' + str( x)
	return r


def EKOT(*x,n=INFO,pref="", color=False, llevel=0, opt={} ):
	"""
	output x value
	"""
	r = ""
	ff = get_source_filename(llevel)
	#print("=======================", ff)
	if (ff[4] != None and n >= el()) :
		loc = str(ff[1]) +	':' + str(ff[2])
		r += print1( loc +	': ' + tt(loc, opt=opt) + lab(n) + '=' + pref + ', '.join(map(str,x)) + '.', color=color, opt=opt)
	return r

def LINE():
	"""
	yields the line file/numer whithout printing
	"""
	r = ""
	frame = inspect.currentframe()
	ff = inspect.getouterframes(frame)[1]
	if (ff[4] != None) :
		loc = str(ff[1]) +	':' + str(ff[2])
		r += loc +	' line ' + tt(loc, opt=opt) + '.'
	return r




def EKO(n=INFO, llevel=0, opt={}):
	"""
	output file:line
	put llevel=1 for line number corresponding to call of the fct where EKO is
	"""
	if not (isinstance(n, int) and isinstance(llevel, int)) :
		n, llevel = INFO, 0
	r = ""
	ff = get_source_filename(llevel)
	if (ff[4] != None and n >= el()) :
		loc = str(ff[1]) +	':' + str(ff[2])
		r += print1(loc +  ': ' + tt(loc, opt=opt) + '.', opt=opt)
		pass
	return r

class EK__ :
	def __init__(self) :
		EKO()

def TYPE(x,tab="", bins=10, range=None) :
	"""
	returns a string describing the type of x
	"""
	return '\n' + TYPE1(x, tab, 0, bins=bins, range=range)


def TYPE1(x,tab, depth, comp_mean=True, bins=10, range=None) :
	try :
		import torch
		if isinstance(x, torch.Tensor) :
			x = x.cpu().detach().numpy()
	except Exception as e:
		pass

	if isinstance(x, list) :
		w = ""
		if len(x) > 0:
			t = TYPE1(x[0], tab, depth+1, comp_mean=False)
			for i,e in enumerate(x):
				typ1 = TYPE1(e, tab, depth+1, comp_mean=False)
				if typ1 != t:
					w = "-not uniform-" + typ1 + " at " + str(i) + '-'
					break
		return 'list' + w + '#' + str(len(x)) + '(' + (TYPE1(x[0], tab+' ', depth+1) if len(x) > 0 else '') + ')'
	elif isinstance(x, tuple) :
		return 'tuple#' + str(len(x)) + '(' + ''.join(['\n' + tab + ' ' + str(i) + ' : ' + TYPE1(e, tab + ' ', depth+1) for i,e in enumerate(x)]) + '\n' + tab + ')'
	elif isinstance(x, np.ndarray) : #, np.generic) ) :
		imin_, imax_, mean, std, min_, max_ = 0,0,0,0,0,0
		hst=""
		if comp_mean :
			try :
				mean, std, imin_, imax_	 = np.mean(x.astype(float)), np.std(x.astype(float)), np.argmin(x), np.argmax(x)
				imax_ = np.unravel_index(np.argmax(x, axis=None), x.shape)
				max_ = x[imax_]
				imin_ = np.unravel_index(np.argmin(x, axis=None), x.shape)
				min_ = x[imin_]
				hst = np.histogram(x.flatten(), bins=bins, range=range)
				lhstv = [str(e)	 for e in hst[0]]
				lhstb = [str(e) for e in hst[1]]
				smx = np.max( [ len(s) for s in lhstv + lhstb])
				lhstv = [e.rjust(smx + 1, ' ')	for e in lhstv]
				lhstb = [e.rjust(smx + 1, ' ') for e in lhstb]

				hstv = ' '.join(lhstv)
				hstb = ' '.join(lhstb)
				hst = "\nhist=" + hstv
				hst +="\nbins=" + hstb
			except Exception as e:
				EKOX(e)
				pass
		return str(type(x).__name__) + '#' + str(x.shape) + '(' + str(x.dtype) + ', m=' + str(mean) + ' s=' + str(std) + ',min=' + str(min_) + '[' + str(imin_) + '],max=' + str(max_) + '[' + str(imax_) + ']' + hst + ')'
	elif isinstance(x, dict) :
		return 'dict#' + str(len(x)) + '(' + ((TYPE1(list(x.keys())[0], tab + ' ', depth+1) + ':' + TYPE1(list(x.values())[0], tab+' ', depth+1)) if len(x) > 0 else '') + ')'
	else :

		try :
			import torch
			if isinstance(x, torch.Tensor) :
				return	str(type(x).__name__) + '#' + str(x.size()) + '(' + str(x.type()) + ', m=' + str(x.float().mean()) + ' s=' + str(x.float().var()) + ')'
		except Exception as e:
			print(e)
			pass

		return type(x).__name__




def array2txt_(a) :
	def f1(l1,s) :
		return s[0].join([f1(x, s[1:]) for x in l1]) if isinstance(l1, list) else str(l1).zfill(2)
	l = a.tolist()
	r = f1(l, '\n  ')
	return '\n' + r

def array2txt(a) :
	return array2txt_(a.astype(int))

last = -1
totdur = 0
lastloc = ""
progressn = 0
def PROGRESS(cur, total, v = "", WW=50, force=False) :
	global last, lastloc, totdur, progressn
	progressn += 1
	v = str(v)

	if force or sys.stdout.isatty():
		frame = inspect.currentframe()
		ff = inspect.getouterframes(frame)[1]
		loc = ""
		if (ff[4] != None) :
			loc = str(ff[1]) +	':' + str(ff[2])

		now = _time.time()
		if cur == 0 or lastloc != loc:
			totdur = 0
			last=-1
		if last > 0 and lastloc == loc and loc != "":
			elapsed = (now - last)
			totdur += elapsed
			eta = float(total - cur) * totdur / cur
			p = float(cur) / total
			print( '\r', end='')

			sss = ['='] * int(p * WW) + ['-'] * int((1.-p)* WW)
			sss[progressn % len(sss)] = '.'
			print( ''.join(sss), end='')
			etaf = str(timedelta(seconds=int(eta)))
			if cur >= total :
				print( os.path.basename(loc) + ' TOT:' + str(timedelta(seconds=int(totdur))) + ', ' + v)
			else:
				print( os.path.basename(loc) + ' ETA:' + etaf + ', ' + str(cur) + '/' + str(total) + ' ' + v, end='')
			sys.stdout.flush()
		lastloc =  loc
		last = now

def ENV(var, defval=None) :
	isin = var in os.environ
	val =  os.environ[var] if isin else defval
	return val


#EKOX(sys.path)

noimage=0

# n emacs, use org-mode as your buffer's major mode.
# You then have access to all the power of org-mode formatting,
# which includes linking to image files and displaying them:
# then you can call org-toggle-inline-images (C-c C-x C-v) to display images in the buffer (without a prefix argument,
# it will display only images without description; if you give a prefix argument, it will display all images)


"""
Bytes-to-human / human-to-bytes converter.
Based on: http://goo.gl/kTQMs
Working with Python 2.x and 3.x.
Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
License: MIT
"""
SYMBOLS = {
	'customary'		: ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
	'customary_ext' : ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
					   'zetta', 'iotta'),
	'iec'			: ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
	'iec_ext'		: ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
					   'zebi', 'yobi'),
}

def bytes2human(n, format='%(value).1f %(symbol)s', symbols='customary'):
	"""
	Convert n bytes into a human readable string based on format.
	"""
	n = int(n)
	if n < 0:
		raise ValueError("n < 0")
	symbols = SYMBOLS[symbols]
	prefix = {}
	for i, s in enumerate(symbols[1:]):
		prefix[s] = 1 << (i+1)*10
	for symbol in reversed(symbols[1:]):
		if n >= prefix[symbol]:
			value = float(n) / prefix[symbol]
			return format % locals()
	return format % dict(symbol=symbols[0], value=n)


def checkGradient(optimizer=None, loss=None) :
	import torch
	if isinstance(optimizer, torch.nn.Module) :	 
		named_parameters = optimizer.named_parameters()
		def itt() :
			for i, (n, p) in enumerate(named_parameters) :
				if(p.requires_grad) and ("bias" not in n) and p.grad is not None:
					#p.grad.detach_()
					yield p
	if isinstance(optimizer, torch.optim.Optimizer) :
		def itt() :
			for group in optimizer.param_groups : 
				for p in group['params'] : 
					if p.requires_grad and p.grad is not None :
						yield p
	if isinstance(optimizer, list) and isinstance(optimizer[0], torch.Tensor) :
		def itt() :
			for t in optimizer :
				#t.grad.detach_()
				#t.grad.zero_()
				yield t
	#for i, p in enumerate(itt()): p.grad.zero_()
	#loss.backward() # retain_graph=True)
	lgs, ave_grads, max_grads, grads = [], [], [], {}
	for i, p in enumerate(itt()):
		grads[i]= p.grad
		ave_grads.append((grads[i]).abs().mean().item())
		max_grads.append((grads[i]).abs().max().item())
		lgs.append(grads[i].flatten())
	#EKOX(len(ave_grads))
	tgrads = torch.cat(lgs)
	return tgrads.cpu().detach().numpy(), ave_grads, max_grads

def crappyhist(a, bins=20, width=80):
	h, b = np.histogram(a, bins)
	s = '\n'.join([ '{:5.3f}  | {:{width}s} {}'.format(
		b[i], 
		'#'*int(width*h[i]/np.amax(h)), 
		h[i], 
		width=width) for i in range (0, bins)])
	return ' \n' + s

def pilim(x) :
	pimg = Image.fromarray(x.astype(np.uint8))
	return pimg

def resize(x, w, h) :
	y = pilim(x).resize((w,h))
	return np.array(y)

def resizeImage(x, ht, wt, keepAspectRatio = True, pad=True) :
	assert(len(x.shape) == 3)
	if keepAspectRatio :
		h,w,_ = x.shape
		art = ht/wt
		ari = h/w
		if ari > art or	 np.isclose(art, ari) :
			if pad :
				k = ht/h
				nww = int(w*k)
				ii = int((wt-nww)/2)				
				#imr = cv2.resize(x, dsize = (nww, ht), interpolation=cv2.INTER_CUBIC)
				imr = resize(x, nww, ht)
				black = np.zeros((ht, wt, 3),dtype=np.uint8)				
				black[:, ii : ii + nww , :] = imr
				res = black
			else :
				k = wt/w
				nhh = int(h*k)
				#imr = cv2.resize(x, dsize = (wt, nhh), interpolation=cv2.INTER_CUBIC)
				imr = resize(x, wt, nhh)
				hhh, www, _ = imr.shape
				ii = int((nhh - ht)/2)
				res = imr[ii : ii+ht, :, :]
			hhh, www, _ = res.shape
			assert(hhh == ht and www == wt)
			return res
		else :
			y = resizeImage(np.transpose(x, (1, 0, 2)), wt, ht, pad=pad)
			res = np.transpose(y, (1, 0, 2))
			hhh, www, _ = res.shape
			assert(hhh == ht and www == wt)
			return res
	else :
		#imr = cv2.resize(x, dsize = (wt, ht), interpolation=cv2.INTER_CUBIC)
		imr = resize(x, wt, ht)
		return imr

class NS(argparse.Namespace) :
	"""
	usage : 
		r = NS(b=1, c=[3,4], a="a")
		dct={"b":1, "c" : [3,4], "a":"a"}
		r = NS(**dct)

	..
	r.b # 1, par nom
	..
	b,c,a = r.A # par ordre, comme dans la declaration

	"""
	def __init__(self, **v) :
		super().__init__(**v)
	@property
	def A(self) :
		return vars(self).values()
	def __getitem__(self, key):
		#assert "subscriptable" in vars(self).keys()
		ll = list(vars(self).values())
		return ll[key]	  


def test() :

	nsns = NS(b=1, c=[3,4], x=34, a="a")
	EKOX(np.ones((3,3)))
	EKON(np.ones((3,3)), np.zeros((4,3)))

	assert(nsns.x==34)
	bb, cc, xx, aa = nsns.A
	assert(cc[0] == 3)
	EKON(xx, bb, cc, aa, pref="\t")
	EKON(xx, bb, cc, aa, pref="\n")
	EKON(xx, bb, cc, aa, n=WARNING)
	EKON(xx, bb, cc, aa)
	EKOX([ i for i in range(4)])
	EKON(xx, bb, cc, aa)
	EKOT("")
	EKOT("coucou")
	EKOT("coucou", n=WARNING)
	EKOX(xx)
	EKOX(xx, n=ERROR)
	
	EKOX(t_ASSIGN)
	assert(aa=="a")

	EKON(xx, cc, n=WARNING)
	EKOX(nsns.c)
	EKON(bb,cc,xx,aa)
	
	EKO()
	class X :
		class Y :
			y=33
		y = Y()
	xx = X()
	EKON(xx.y.y) 
	
	def parseEE(x) :
		p = parseE(x)

		y = list(map(dump, listp(p)))
		return y
	EKOX(parseEE("t2n(torch.topk(vv[0,:,0], 3).values)"))
	EKOX(parseEE("t2n(index[0]), t2n(torch.topk(bcn[0,:,0], 3).values), t2n(torch.topk(vv[0,:,0], 3).values)"))

	

	class X :
		def topk(self,x,y) :
			return namedtuple("T", "values indices")
	torch = X()
	t2n = lambda x : x
	vv	= bcn = np.ones([4,4,4])
	
	EKON(t2n(torch.topk(bcn[0,:,0], 3).values), t2n(torch.topk(vv[0,:,0], 3).values))
	EKON(t2n(torch.topk(bcn[0,:,0], 3).indices), t2n(torch.topk(vv[0,:,0], 3).indices))


	EKOX(parseEE("t2n(torch.topk(bcn[0,:,0], 3).values), t2n(torch.topk(vv[0,:,0], 3).values)"))
	EKOX(parseEE("t2n(torch.topk(bcn[0,:,0], 3).indices), t2n(torch.topk(vv[0,:,0], 3).indices)"))

	
	EKOX(parseEE("p"))
	EKOX(parseEE("p()"))
	EKOX(parseEE("a+b"))
	EKOX(parseEE("a+b+c"))
	EKOX(parseEE("t[a:b]"))
	EKOX(parseEE("t[:]"))
	EKOX(parseEE("t[0:]"))
	EKOX(parseEE("t[a:b:c]"))
	EKOX(parseEE("aaa + f(t[a:b])"))

	EKOX(parseEE("t2n(zzz.indices)"))
	EKOX(parseEE("a.b"))	
	EKOX(parseEE("a.b.c"))	  
	EKOX(parseEE("a(1).b"))	   
	EKOX(parseEE("a.X(1).b"))	 
	EKOX(parseEE("(a(1),c).b"))	   
	EKOX(parseEE("F((a(1),c).b)"))	  
	EKOX(parseEE("t2n(torch.topk(xx, 3).indices)"))
	EKOX(parseEE("t2n(torch.topk(bcn[0,:,0], 3).indices)"))
	EKOX(parseEE("t2n(torch.topk(bcn[0,:,0], 3).indices), t2n(torch.topk(vv[0,:,0], 3).indices)"))


	EKOX(parseEE("EKON(a)"))
	EKOX(parseEE("EKON(a,b)"))
	EKOX(parseEE("EKON(a, opt=1)"))

	EKO()
	EKOX(parseEE("EKON(opt={'a':22})"))
	EKO()
	EKOX(parseEE("EKON({'a':22})"))

	
	face = np.random.randint(0,255,size=(100,100,3))
	EKOX(face.shape)
	EKOI(face)
	EKOX(face.shape)
	hh, ww, _ = face.shape
	EKOI(resizeImage(face, ht=hh*2, wt=ww*3)) 
	EKOI(resizeImage(face, ht=hh*3, wt=ww*2)) 
	EKOI(resizeImage(face, ht=hh*2, wt=ww*3, pad=False)) 
	EKOI(resizeImage(face, ht=hh*3, wt=ww*2, pad=False)) 
	
	
	EKO()
	x,y=1, 'y'
	EKOX(x)


	EKOH(np.random.rand(100))

	im = np.fromfunction(lambda i, j: i*i/600/600 * 255 + j/600*255, (600, 600), dtype=float)
	EKOX(im.shape)
	EKOI(im)


	
	im = np.fromfunction(lambda i, j: np.asarray([(np.sin(i/np.pi/10) + np.cos(j/np.pi/10))/2.*255]*3), (600, 600), dtype=float).transpose(1,2,0)
	EKOX(TYPE(im))
	EKOI(im)
	EKOI(im, sz=500)
	EKO()
	EKOX(x,n=INFO)
	EKOX(x,n=WARNING)
	EKOX(x,n=ERROR)
	#EKON((1,2))

	f = lambda x : '<' + str(x) + '>'
	EKOX(f(("a", "b")))


	class X :
		x = 0
		def f(self) :
			return 0

	x =X()
	faces = np.ones((5, 3))
	kk, f = 4, 2
	EKOX((kk, f, faces[f]))
	EKOX((x,y))
	xy = (2,3)
	EKOX(xy)
	#print(FE(x))
	EKOX((x,y))
	#print(FE((x,y)))

	tt = "abcd"
	g = lambda x,y : x+y
	g1 = lambda y : y+y

	

	EKON(kk)
	EKON(kk,f)
	EKON(kk,g1(12))
	EKON(kk,g(12,13))
	EKON((kk,3),"a")
	EKON(tt[1+2], g(1,2), xy)
	EKOX((tt[1+2], g(1,2), xy))
	EKON(1,2,3,4,5)
	EKON(1,2,3,4,5)

	EKON(x.x)
	EKON(X())
	EKON(x . f ())
	
	EKON(1 +2, 1+ 2, x.x, x.f())
	vv = np.ones((4,4,4))
	EKOX(vv[0,:,0])


	EKOX(re.__version__)
	EKOX(argparse.__version__)

	ep = parseE("bcn[0,:,0]")

	EKO()
	ep = parseE("t2n(torch.topk(bcn[0,:,0], 3).indices), t2n(torch.topk(vv[0,:,0], 3).indices)")

	zzz = namedtuple("XXX", "indices y")
	t2n = lambda x : x
	torchtopk = lambda x,y : zzz
	
	bcn = np.zeros((2,2,2))
	
	EKON(t2n(torchtopk(bcn[0,:,0], 3).indices))
	EKON(t2n(torchtopk(bcn[0,:,0], 3).indices), t2n(torchtopk(vv[0,:,0], 3).indices))						 

	EKOT(1,2,"33")
	EKOX(1.2e3)
	

	import time
	
	a=1
	b=[2,3,4]
	EKON(a, b)
	EKOT(a, b)
	EKO()
	for i in range(5) :
		time.sleep(1)
		EKOX(i)
	ilm, ecart = 1,2
	EKON(ilm, ecart)
	
	EKON(ilm, ecart)   
	EKON(a, ecart)	
	EKON(ecart, a)	
	EKON(ilm, b)  
	EKOX(ecart)
	EKON(ecart)

	tt = [ "aaaa" , "bbbb"]
	EKON(tt[0][0])
	"""
	print_everything()
	EKO()
	print_everything()
	EKO()
	print_nothing()
	print_nothing()
	EKO()
	print_nothing()
	EKO()
	print_everything()
	EKO()
	"""

	EKO()
	noeko()
	EKO()
	yeseko()
	EKO()
	a, b, z = "aa", "bb", "zz"
	EKON("a", a, "b", b, 'z', z)
	
	EKOT("success", n=LOG, color=True)
	EKOT("success", n=LOG)
	
	EKOX(TIME(lambda x : x[0]+1))
	EKOX(in_notebook())

	EKON(a, b)
	EKON(a, b, opt={"with_date" : 1})	 
	default_opt["with_date"] = 1
	EKON(a, b)	  
	
def count_parameters(model):
	return sum(p.numel() for p in model.parameters() if p.requires_grad)

def parse_args(configin = {}) :
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("--dataroot", default="/mnt/hd2/data")
	args = parser.parse_known_args()[0]
	dataroot = args.dataroot
	now = datetime.now()
	dt = now.strftime("%x_%X").replace("/", "_")
	config = {
		'tag' : dt
	}

	config.update(configin)

	parser = argparse.ArgumentParser(add_help=False)
	for k,v in config.items() :		   
		t = type(v)
		if isinstance(v, bool) : t = Bool
		parser.add_argument("--" + k, default=v,type=t)
	args = parser.parse_known_args()[0]


	return args
	
def get_notebook_dir(root = "/content/gdrive/My Drive/") :
	"""
	pour google colab 
	permet de cd dans le folder ou se trouve le notebook
	%cd "{utillc.get_notebook_dir()}
	"""
	import os, subprocess
	import utillc
	import requests
	from requests import get
	from socket import gethostname, gethostbyname
	ip = gethostbyname(gethostname()) # 172.28.0.12
	filename = get(f"http://{ip}:9000/api/sessions").json()[0]["name"]
	filename = filename.replace("%20", " ")
	EKOX(filename)
	results = subprocess.check_output(['find', root, "-name", filename , "-print"]).decode('utf-8').strip()
	dd = os.path.dirname(results)
	return dd
	
if __name__ == "__main__":

	import inctest
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("--test", type=Bool)
	args = parser.parse_known_args()[0]
	if args.test :
		try :
			test()
			EKOX("aa")
			inctest.f()
		except Exception as e:
			print(e)
	print(__version__)

