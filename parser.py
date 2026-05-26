import ply.yacc as yacc
from lexer import tokens

# AST nodes: tuples (tag, ...children)

def p_programa(p):
    'programa : devices cmds'
    p[0] = ('program', p[1], p[2])

def p_devices_list(p):
    'devices : device devices'
    p[0] = [p[1]] + p[2]

def p_devices_one(p):
    'devices : device'
    p[0] = [p[1]]

def p_device_simple(p):
    'device : DISPOSITIVO COLON LBRACE IDENT RBRACE'
    p[0] = ('device', p[4], None)

def p_device_obs(p):
    'device : DISPOSITIVO COLON LBRACE IDENT COMMA IDENT RBRACE'
    p[0] = ('device', p[4], p[6])

def p_cmds_list(p):
    'cmds : cmd DOT cmds'
    p[0] = [p[1]] + p[3]

def p_cmds_one(p):
    'cmds : cmd DOT'
    p[0] = [p[1]]

def p_cmd(p):
    '''cmd : attrib
           | obsact
           | act'''
    p[0] = p[1]

def p_attrib(p):
    'attrib : SET IDENT ASSIGN var'
    p[0] = ('attrib', p[2], p[4])

def p_var_num(p):
    'var : NUMBER'
    p[0] = ('num', p[1])

def p_var_true(p):
    'var : TRUE'
    p[0] = ('bool', True)

def p_var_false(p):
    'var : FALSE'
    p[0] = ('bool', False)

def p_obsact_if(p):
    'obsact : SE obs ENTAO act'
    p[0] = ('if', p[2], p[4], None)

def p_obsact_ifelse(p):
    'obsact : SE obs ENTAO act SENAO act'
    p[0] = ('if', p[2], p[4], p[6])

def p_obs_single(p):
    'obs : IDENT OPLOGIC var'
    p[0] = [('cond', p[1], p[2], p[3])]

def p_obs_and(p):
    'obs : IDENT OPLOGIC var AND obs'
    p[0] = [('cond', p[1], p[2], p[3])] + p[5]

def p_act_action(p):
    '''act : LIGAR IDENT
           | DESLIGAR IDENT'''
    p[0] = ('action', p[1], p[2])

def p_act_alert_msg(p):
    'act : ENVIAR ALERTA LPAREN STRING RPAREN IDENT'
    p[0] = ('alert', p[4], None, [p[6]])

def p_act_alert_var(p):
    'act : ENVIAR ALERTA LPAREN STRING COMMA IDENT RPAREN IDENT'
    p[0] = ('alert', p[4], p[6], [p[8]])

def p_act_broadcast_msg(p):
    'act : ENVIAR ALERTA LPAREN STRING RPAREN PARA TODOS COLON namelist'
    p[0] = ('alert', p[4], None, p[9])

def p_act_broadcast_var(p):
    'act : ENVIAR ALERTA LPAREN STRING COMMA IDENT RPAREN PARA TODOS COLON namelist'
    p[0] = ('alert', p[4], p[6], p[11])

def p_namelist_one(p):
    'namelist : IDENT'
    p[0] = [p[1]]

def p_namelist_more(p):
    'namelist : IDENT COMMA namelist'
    p[0] = [p[1]] + p[3]

def p_error(p):
    if p:
        print(f"ERRO SINTATICO: token {p.type}({p.value!r}) linha {p.lineno}")
    else:
        print("ERRO SINTATICO: fim de arquivo inesperado")

parser = yacc.yacc(debug=False, write_tables=False)
