import ply.yacc as yacc
from lexer import tokens

syntax_errors = []


def reset_syntax_errors():
    syntax_errors.clear()


def _syntax_error(message):
    text = f"ERRO SINTATICO: {message}"
    print(text)
    syntax_errors.append(text)


# AST nodes: tuples (tag, ...fields)
# ('program', devices, cmds)
# ('device', namedevice, observation|None)
# ('attrib', obs_name, value)         -- value: ('num',n)|('bool',b)|('actexecute',act,dev)
# ('attrib_device', dev, obs, value)  -- set {dev, obs} = val
# ('if', cond_list, then_cmds, else_cmds|None)   -- then/else are command LISTS
# ('while', cond_list, body_cmds)                -- body is a command LIST
# ('actexecute', 'ligar'|'desligar'|'verificar', device)
# ('alert', msg, obs|None, devices_list)
# cond item: ('cond', lhs, op, rhs)
#   lhs: obs_name str OR ('actexecute',act,dev)

def p_programa(p):
    'programa : devices cmds'
    p[0] = ('program', p[1], p[2])

# ── devices ──────────────────────────────────────────────────────────────────

def p_devices_list(p):
    'devices : device devices'
    p[0] = [p[1]] + p[2]

def p_devices_one(p):
    'devices : device'
    p[0] = [p[1]]

def p_device_simple(p):
    'device : DISPOSITIVO device_open IDENT RBRACE'
    p[0] = ('device', p[3], None)

def p_device_obs(p):
    'device : DISPOSITIVO device_open IDENT COMMA IDENT RBRACE'
    p[0] = ('device', p[3], p[5])

def p_device_error(p):
    'device : DISPOSITIVO device_open error RBRACE'
    _syntax_error("DEVICE invalido; esperado dispositivo {namedevice} ou {namedevice, observation}")
    p[0] = ('error',)

def p_device_open(p):
    '''device_open : COLON LBRACE
                   | LBRACE'''
    p[0] = None

# ── top-level cmds ───────────────────────────────────────────────────────────
# A program body is a sequence of commands. Every command is self-delimited:
#   * simple_cmd  -- optionally terminated by '.'  (per enunciado examples)
#   * if_stmt     -- delimited by its own structure (single cmd or { block })
#   * loop        -- delimited by 'faca { ... }'
# There is no ambiguity about where an if ends, so two consecutive top-level
# ifs no longer get wrongly nested.

def p_cmds_more(p):
    'cmds : cmd cmds'
    p[0] = [p[1]] + p[2]

def p_cmds_one(p):
    'cmds : cmd'
    p[0] = [p[1]]

def p_cmd_simple_dot(p):
    'cmd : simple_cmd DOT'
    p[0] = p[1]

def p_cmd_simple(p):
    'cmd : simple_cmd'
    p[0] = p[1]

def p_cmd_if(p):
    'cmd : if_stmt'
    p[0] = p[1]

def p_cmd_loop(p):
    'cmd : loop'
    p[0] = p[1]

def p_cmd_error(p):
    'cmd : error DOT'
    _syntax_error("CMD invalido ou incompleto antes de '.'")
    p[0] = ('error',)

def p_simple_cmd(p):
    '''simple_cmd : attrib
                  | act'''
    p[0] = p[1]

# ── attrib ────────────────────────────────────────────────────────────────────

def p_attrib_var(p):
    'attrib : SET IDENT ASSIGN var'
    p[0] = ('attrib', p[2], p[4])

def p_attrib_actexecute(p):
    'attrib : SET IDENT ASSIGN actexecute'
    p[0] = ('attrib', p[2], p[4])

def p_attrib_device_var(p):
    'attrib : SET LBRACE IDENT COMMA IDENT RBRACE ASSIGN var'
    p[0] = ('attrib_device', p[3], p[5], p[8])

def p_attrib_error(p):
    'attrib : SET error'
    _syntax_error("ATTRIB invalido; esperado set observation = VAR ou set observation = ACTEXECUTE")
    p[0] = ('error',)

def p_var_num(p):
    'var : NUMBER'
    p[0] = ('num', p[1])

def p_var_true(p):
    'var : TRUE'
    p[0] = ('bool', True)

def p_var_false(p):
    'var : FALSE'
    p[0] = ('bool', False)

# ── if / if-else ──────────────────────────────────────────────────────────────
# Body of an if/else (branch) is EITHER a single command, OR a braced block
# { cmds } for multiple commands and nested ifs. A branch always yields a LIST.

def p_if_stmt(p):
    'if_stmt : SE obs ENTAO branch'
    p[0] = ('if', p[2], p[4], None)

def p_if_stmt_else(p):
    'if_stmt : SE obs ENTAO branch SENAO branch'
    p[0] = ('if', p[2], p[4], p[6])

def p_if_stmt_error(p):
    'if_stmt : SE error'
    _syntax_error("OBSACT invalido; esperado se OBS entao CMD ou se OBS entao { CMDS }")
    p[0] = ('error',)

def p_branch_block(p):
    'branch : LBRACE cmds RBRACE'
    p[0] = p[2]

def p_branch_simple_dot(p):
    'branch : simple_cmd DOT'
    p[0] = [p[1]]

def p_branch_simple(p):
    'branch : simple_cmd'
    p[0] = [p[1]]

def p_branch_if(p):
    'branch : if_stmt'
    p[0] = [p[1]]

def p_branch_loop(p):
    'branch : loop'
    p[0] = [p[1]]

# ── loop ──────────────────────────────────────────────────────────────────────

def p_loop(p):
    'loop : ENQUANTO obs FACA LBRACE cmds RBRACE'
    p[0] = ('while', p[2], p[5])

def p_loop_error(p):
    'loop : ENQUANTO error'
    _syntax_error("LOOP invalido; esperado enquanto OBS faca { CMDS }")
    p[0] = ('error',)

# ── obs (conditions) ──────────────────────────────────────────────────────────

def p_obs_ident(p):
    'obs : IDENT OPLOGIC var'
    p[0] = [('cond', p[1], p[2], p[3])]

def p_obs_ident_and(p):
    'obs : IDENT OPLOGIC var AND obs'
    p[0] = [('cond', p[1], p[2], p[3])] + p[5]

def p_obs_verificar(p):
    'obs : VERIFICAR LPAREN IDENT RPAREN OPLOGIC var'
    p[0] = [('cond', ('actexecute', 'verificar', p[3]), p[5], p[6])]

def p_obs_verificar_and(p):
    'obs : VERIFICAR LPAREN IDENT RPAREN OPLOGIC var AND obs'
    p[0] = [('cond', ('actexecute', 'verificar', p[3]), p[5], p[6])] + p[8]

def p_obs_verificar_nospace(p):
    'obs : VERIFICAR IDENT OPLOGIC var'
    p[0] = [('cond', ('actexecute', 'verificar', p[2]), p[3], p[4])]

def p_obs_verificar_nospace_and(p):
    'obs : VERIFICAR IDENT OPLOGIC var AND obs'
    p[0] = [('cond', ('actexecute', 'verificar', p[2]), p[3], p[4])] + p[6]

# ── act ───────────────────────────────────────────────────────────────────────

def p_act_execute(p):
    'act : actexecute'
    p[0] = p[1]

def p_act_alert_direct(p):
    'act : ENVIAR ALERTA alert_args IDENT'
    msg, var = p[3]
    p[0] = ('alert', msg, var, [p[4]])

def p_act_alert_broadcast(p):
    'act : ENVIAR ALERTA alert_args PARA TODOS COLON namelist'
    msg, var = p[3]
    p[0] = ('alert', msg, var, p[7])

def p_act_alert_error(p):
    'act : ENVIAR ALERTA error'
    _syntax_error("ACTALERT invalido; esperado enviar alerta (msg) namedevice ou para todos: lista")
    p[0] = ('error',)

def p_actexecute_ligar(p):
    'actexecute : LIGAR IDENT'
    p[0] = ('actexecute', 'ligar', p[2])

def p_actexecute_desligar(p):
    'actexecute : DESLIGAR IDENT'
    p[0] = ('actexecute', 'desligar', p[2])

def p_actexecute_verificar_parens(p):
    'actexecute : VERIFICAR LPAREN IDENT RPAREN'
    p[0] = ('actexecute', 'verificar', p[3])

def p_actexecute_verificar_nospace(p):
    'actexecute : VERIFICAR IDENT'
    p[0] = ('actexecute', 'verificar', p[2])

def p_alert_args_msg(p):
    '''alert_args : LPAREN STRING RPAREN
                  | STRING'''
    p[0] = (p[2], None) if len(p) == 4 else (p[1], None)

def p_alert_args_var(p):
    '''alert_args : LPAREN STRING COMMA IDENT RPAREN
                  | STRING COMMA IDENT'''
    p[0] = (p[2], p[4]) if len(p) == 6 else (p[1], p[3])

def p_alert_args_error(p):
    'alert_args : LPAREN error RPAREN'
    _syntax_error("argumentos de alerta invalidos; esperado (msg) ou (msg, observation)")
    p[0] = ('', None)

def p_namelist_one(p):
    'namelist : IDENT'
    p[0] = [p[1]]

def p_namelist_more(p):
    'namelist : IDENT COMMA namelist'
    p[0] = [p[1]] + p[3]

def p_namelist_error(p):
    'namelist : error'
    _syntax_error("namelist invalida; esperado pelo menos um namedevice")
    p[0] = []

def p_error(p):
    if p:
        _syntax_error(f"token {p.type}({p.value!r}) linha {p.lineno}")
    else:
        _syntax_error("fim de arquivo inesperado")

parser = yacc.yacc(debug=False, write_tables=False)
