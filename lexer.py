import ply.lex as lex

reserved = {
    'dispositivo': 'DISPOSITIVO',
    'set': 'SET',
    'se': 'SE',
    'entao': 'ENTAO',
    'senao': 'SENAO',
    'enviar': 'ENVIAR',
    'alerta': 'ALERTA',
    'para': 'PARA',
    'todos': 'TODOS',
    'ligar': 'LIGAR',
    'desligar': 'DESLIGAR',
    'True': 'TRUE',
    'False': 'FALSE',
}

tokens = [
    'IDENT', 'NUMBER', 'STRING',
    'COLON', 'COMMA', 'DOT', 'ASSIGN',
    'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN',
    'AND', 'OPLOGIC',
] + list(reserved.values())

t_COLON   = r':'
t_COMMA   = r','
t_DOT     = r'\.'
t_ASSIGN  = r'='
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_AND     = r'&&'

def t_OPLOGIC(t):
    r'>=|<=|==|!=|>|<'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

def t_IDENT(t):
    r'[A-Za-z][A-Za-z0-9]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t

t_ignore = ' \t\r\n'

def t_error(t):
    print(f"ERRO LEXICO: caractere inesperado {t.value[0]!r} linha {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
