# *.* coding=utf-8 *.*

import ply.yacc as yacc
import lex
from collections import deque

tokens = lex.tokens

rules = deque()
rule = deque()

extends = deque()

Number = -1

class expr:
	def __init__(self,t):
		self.t = t
	def __str__(self):
		return "expr:%s" % (str(self.t))
	def __repr__(self):
		return "expr:%s" % (str(self.t))
	def __radd__(self, other):
		return self.t + other
	def process_plus(self):
		if self.t[0] == '(' and self.t[-2] == ')' and self.t[-1] == '+':
			new_label = inc_number()
			new_expr =  [ new_label , ':'] + self.t[1:-2 ] + \
						[ '|' , new_label ] + self.t[1:-2 ]
			extends.append( new_expr )
			self.t = [ new_label ]
		else:
			pass
		return self
	def process_mult(self):
		if self.t[0] == '(' and self.t[-2] == ')' and self.t[-1] == '*':
			new_label = inc_number()
			new_expr =  [ new_label , ':'] + self.t[1:-2 ] + \
						[ '|' , new_label ] + self.t[1:-2] + [ '|' ,'empty' ]
			extends.append( new_expr )
			self.t = [ new_label ]
	def process_ques(self):
		if self.t[0] == '(' and self.t[-2] == ')' and self.t[-1] == '?':
			new_label = inc_number()
			new_expr =  [ new_label , ':'] + self.t[1:-2 ] + \
						[ '|' , 'empty' ]
			extends.append( new_expr )
			self.t = [ new_label ]	
	
	def process(self):
		for x in self.t:
			if x == '?':
				return self.process_ques()
			elif x=='+':
				return self.process_plus()
			elif x == '*':
				return self. process_mult()
		return self.t
	def process_sub(self):
		if self.t[0] == '(':
			flag = False
			if self.t[-1] == ')':
				for x in self.t[1:-1]:
					if x == '|':
						flag = True
						break
			if self.t[-2] == ')' :
				for x in self.t[1:-2]:
					if x == '|':
						flag = True
						break
			if flag == True:
				new_label = inc_number()
				new_expr = [ new_label , ':' ] + self.t[1:-2]
				extends.append( new_expr )
				self.t = [ new_label ]
'''
class rule:
	def __init__(self,t):
		self.t = t
	def __str__(self):
		return "rule:%s" % (str(self.t))
	def __repr__(self):
		return "rule:%s" % (str(self.t))
'''

def p_program( p ):
	'''
		program : grammar_statment options_statment rule_statments 
	'''
	pass

def p_grammar_statment( p ):
	'''
		grammar_statment : GRAMMAR ID SEMI
	'''
	pass

def p_options_statment( p ):
	'''
		options_statment : OPTIONS BLPAREN option_statments BRPAREN
	'''
	pass

def p_option_statments( p ):
	'''
		option_statments : option_statment
						| option_statments option_statment
	'''
	pass

def p_option_statment( p ):
	'''
		option_statment : ID EQUALS ID SEMI
	'''
	pass

def p_rule_statments( p ):
	'''
		rule_statments : rule_statment
					| rule_statments rule_statment
	'''
	pass
def p_rule_statment( p ):
	'''
		rule_statment : ID COLON rules SEMI

	'''
	rule.appendleft(p[2])
	rule.appendleft(p[1])
	rules.append(deque(rule))
	rule.clear()
	pass


def p_rules( p ):
	'''
		rules : rule
			| rules rule
	'''
	if len(p) == 2:
		rule.append(p[1])
	if p[0] == None : p[0] = []
	p[0] = p[0] + p[1]

def p_rule( p ):
	'''
		rule : expr
			| rule expr
			| rule VERTICAL expr
			| empty
	'''
	if p[0] == None : p[0] = []
	if len(p) == 2:
		p[0] = p[0] + p[1]
	if len(p) == 3:
		p[0] =  p[1] + p[2]
	if len(p) == 4:
		p[0] = p[1] +  [ p[2] ] + p[3]
def p_expr( p ):
	'''
		expr : ptoken
			| s_expr
	'''
	if p[0] == None: p[0] = []
	p[0] = p[0] + p[1]

def p_sub_expr( p ):
	'''
		sub_expr :  LPAREN rule RPAREN
			| LPAREN rule RPAREN operator
	'''
	if len(p) == 4:
		if p[2] !=None:
			p[0] = expr( [ p[1] ] + p[2] +[ p[3] ]  )
			p[0].process_sub()
	if len(p) == 5:
		if p[2] != None:
			p[0] = expr( [ p[1] ] + p[2] + [ p[3] ] + p[4] )
			p[0].process_sub()
			p[0].process()

def p_s_expr( p ):
	'''
		s_expr :
				| expr operator
				| expr
				| LPAREN RPAREN
				| expr sub_expr
				| sub_expr
	'''
	if len(p) == 3:
		if p[1] != None and p[1] != '(':
			if p[0] == None : p[0] = []
			p[0] = expr(  p[0] + p[1] + p[2] )
			#p[0].process()
	if len(p) == 2:
		if p[1] != None:
			if p[0] == None: p[0] = []
			p[0] = p[0] + p[1]

def p_operator( p ):
	'''
		operator : PLUS
				| MULT
				| QUES
	'''
	p[0] = [ p[1] ]

def p_ptoken( p ):
	'''
		ptoken : ID
				| SPE_TOKEN
	'''
	p[0] = [ p[1] ]


#### Empty
   
def p_empty( p ):
    '''empty : '''

#### Catastrophic error handler

def p_error(p):
	if p:
		print "Syntax error at '%s' lineno = %i linepos=%i" %  ( p.value , p.lineno , p.lexpos )
	else:
		print "Syntax error at EOF"

def split_lower(p):
	import re
	if len(p) == 1 : return lex.tokenNameList[p]
	if len( re.findall('[A-Z_]' , p ) ) == len( p ):
		return p
	else:
		return ( "_".join(re.findall('[A-Z][a-z]+',p)) ).lower()

def inc_number():
	global Number
	Number = Number+1
	return 'A%d' % (Number)

def get_yacc(l):
	b = yacc.yacc()

	b.error = 0
	result = b.parse(lexer = l , debug=1)
	#"""
	sf = open("source.py","w")
	for x in  rules:
		sf.write( 'def p_%s(p):' % x[0] )
		sf.write( "\n\t'''\n")
		body = ""
		for y in x[2]:
			if y == "|":
				body = body + " " +  ( "\n\t" + y )
			else:
				body = body + " "+ y
		sf.write( "\t %s%s%s%s%s" % (x[0]," ",x[1] , " " , body) )
		sf.write( "\n\t\n'''")
		sf.write( "\tpass\n")
		sf.write( "\n")
	sf.close()


	ef = open("extends.py","w")

	for x in extends:
		ef.write( 'def p_%s(p):\n' % x[0] )
		ef.write( "\t'''\n" )
		body = ""
		for y in x[2:]:
			if y == "|":
				body = body + " " + ( "\n\t" + y )
			else:
				body = body + " "+ y
		ef.write( "\t %s%s%s%s%s"  % ( x[0]," ",x[1] , " " , body ) )
		ef.write( "\n\t" )
		ef.write( "\t'''\n" )
		ef.write( "\tpass\n" )
		ef.write( "\n" )
	ef.close()
	#"""
	if b.error : return None


