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
# ('if', cond_list, then_cmds, else_cmds|None)
# ('while', cond_list, body_cmds)
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

def p_cmds_more(p):
    'cmds : full_cmd cmds'
    p[0] = [p[1]] + p[2]

def p_cmds_one(p):
    'cmds : full_cmd'
    p[0] = [p[1]]

def p_full_cmd_obsact_dot(p):
    'full_cmd : obsact DOT'
    p[0] = p[1]

def p_full_cmd_obsact(p):
    'full_cmd : obsact'
    p[0] = p[1]

def p_full_cmd_loop_dot(p):
    'full_cmd : loop DOT'
    p[0] = p[1]

def p_full_cmd_loop(p):
    'full_cmd : loop'
    p[0] = p[1]

def p_full_cmd_simple(p):
    'full_cmd : simple_cmd DOT'
    p[0] = p[1]

def p_full_cmd_simple_without_dot(p):
    'full_cmd : simple_cmd'
    p[0] = p[1]

def p_full_cmd_error(p):
    'full_cmd : error DOT'
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

def p_var_error(p):
    'var : error'
    _syntax_error("VAR invalido; esperado numero inteiro nao negativo ou bool")
    p[0] = ('error_var', None)

# ── obsact (if / if-else) ─────────────────────────────────────────────────────
# Single-act if: "se obs entao act." — the DOT is consumed inside if_cmds.
#   obsact reduces without consuming extra DOT; full_cmd uses 'obsact' (no dot).
# Multi-cmd if:  "se obs entao cmd. cmd. ." — body cmds consume their dots,
#   inner obsacts consume their own dots (via if_cmds: obsact DOT).
#   The lone "." is the obsact block terminator consumed by "obsact DOT" rules.
# Note: a single-act inner if (no lone dot) followed by more outer cmds MUST
#   have an explicit lone "." after it so the parser knows the inner if ended.
#   Example: "se c entao se c2 entao ligar v. . set x=1. ."

def p_obsact_if(p):
    'obsact : SE obs ENTAO if_cmds'
    p[0] = ('if', p[2], p[4], None)

def p_obsact_ifelse(p):
    'obsact : SE obs ENTAO if_cmds SENAO if_cmds'
    p[0] = ('if', p[2], p[4], p[6])

def p_obsact_error(p):
    'obsact : SE error'
    _syntax_error("OBSACT invalido; esperado se OBS entao CMDS")
    p[0] = ('error',)

def p_loop(p):
    'loop : ENQUANTO obs FACA LBRACE block_cmds RBRACE'
    p[0] = ('while', p[2], p[5])

def p_loop_error(p):
    'loop : ENQUANTO error'
    _syntax_error("LOOP invalido; esperado enquanto OBS faca { CMDS }")
    p[0] = ('error',)

# if_cmds: one or more cmds inside an if body.
# Each simple_cmd may or may not have a trailing dot (to handle both single-line
# and multi-line bodies). PLY resolves shift/reduce by preferring shift (greedy).

def p_if_cmds_simple_dot_more(p):
    'if_cmds : simple_cmd DOT if_cmds'
    p[0] = [p[1]] + p[3]

def p_if_cmds_simple_dot(p):
    'if_cmds : simple_cmd DOT'
    p[0] = [p[1]]

def p_if_cmds_simple(p):
    'if_cmds : simple_cmd'
    p[0] = [p[1]]

def p_if_cmds_obsact_dot_more(p):
    'if_cmds : obsact DOT if_cmds'
    p[0] = [p[1]] + p[3]

def p_if_cmds_obsact_dot(p):
    'if_cmds : obsact DOT'
    p[0] = [p[1]]

def p_if_cmds_obsact_more(p):
    'if_cmds : obsact if_cmds'
    p[0] = [p[1]] + p[2]

def p_if_cmds_obsact(p):
    'if_cmds : obsact'
    p[0] = [p[1]]

# block_cmds is used by explicit braced blocks, currently loops.

def p_block_cmds_more(p):
    'block_cmds : block_cmd block_cmds'
    p[0] = [p[1]] + p[2]

def p_block_cmds_one(p):
    'block_cmds : block_cmd'
    p[0] = [p[1]]

def p_block_cmd_simple_dot(p):
    'block_cmd : simple_cmd DOT'
    p[0] = p[1]

def p_block_cmd_simple(p):
    'block_cmd : simple_cmd'
    p[0] = p[1]

def p_block_cmd_obsact_dot(p):
    'block_cmd : obsact DOT'
    p[0] = p[1]

def p_block_cmd_obsact(p):
    'block_cmd : obsact'
    p[0] = p[1]

def p_block_cmd_loop_dot(p):
    'block_cmd : loop DOT'
    p[0] = p[1]

def p_block_cmd_loop(p):
    'block_cmd : loop'
    p[0] = p[1]

def p_block_cmd_error(p):
    'block_cmd : error DOT'
    _syntax_error("comando invalido dentro de bloco")
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

def p_obs_error_rhs(p):
    'obs : IDENT OPLOGIC error'
    _syntax_error("OBS invalida; esperado VAR depois do operador logico")
    p[0] = [('cond', p[1], p[2], ('error_var', None))]

def p_obs_verificar_error(p):
    'obs : VERIFICAR error'
    _syntax_error("OBS invalida; esperado verificar(namedevice) oplogic VAR")
    p[0] = [('cond', ('actexecute', 'verificar', '<erro>'), '==', ('error_var', None))]

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

def p_actexecute_error(p):
    '''actexecute : LIGAR error
                  | DESLIGAR error
                  | VERIFICAR LPAREN error RPAREN'''
    _syntax_error("ACTEXECUTE invalido; esperado ACTION namedevice")
    p[0] = ('error',)

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
