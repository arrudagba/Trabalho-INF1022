# Trabalho Final INF1022 2026.1 — Analisador Sintático ObsAct

**Disciplina:** INF1022 — Analisadores Léxicos e Sintáticos 
**Professores:** Luís e Edward Hermann  
**Turma:** 3WB

| Aluno | Matrícula |
|---|---|
| Gabriel de Barros Arruda | 2311723 |
| Arthur Rodrigues Alves Barbosa | 2310394 |

---

## O que foi implementado

Foi implementado um analisador léxico e sintático para a linguagem **ObsAct**, que compila programas escritos em ObsAct para a linguagem **Python**. O analisador recebe como entrada um arquivo `.obsact` e produz como saída um arquivo `.py` equivalente.

A implementação utiliza a biblioteca **PLY** (Python Lex-Yacc), que é um gerador de analisadores LALR(1) — análogo ao Bison/Yacc, porém escrito em Python.

Foram implementadas as seguintes funcionalidades:

- Declaração de dispositivos nas duas formas: `dispositivo: {namedevice}` e `dispositivo: {namedevice, observation}`
- Atribuição de valores a sensores via `set observation = VAR` (suporte a inteiros e booleanos `True`/`False`)
- Comando condicional `se OBS entao ACT` (if simples)
- Comando condicional `se OBS entao ACT senao ACT` (if-else)
- Condições compostas com `&&` (AND lógico entre múltiplas observações)
- Operadores lógicos: `>`, `<`, `>=`, `<=`, `==`, `!=`
- Ações `ligar` e `desligar` para um dispositivo
- Envio de alerta com mensagem simples: `enviar alerta ("msg") namedevice`
- Envio de alerta com mensagem e variável concatenada: `enviar alerta ("msg", observation) namedevice`
- **Broadcast**: `enviar alerta ("msg") para todos: dev1, dev2, ...`
- **Broadcast com variável**: `enviar alerta ("msg", observation) para todos: dev1, dev2, ...`
- Geração das 4 funções de runtime no código Python de saída (`ligar`, `desligar`, `alerta` com e sem variável)
- Inicialização automática de toda `observation` para zero (conforme Suposições do enunciado)
- Validação semântica de dispositivos e observações declarados antes do uso
- Validação de formato: `namedevice` apenas com letras e `observation` com letras/números iniciando por letra
- Suporte a booleanos `True`/`False`, `TRUE`/`FALSE` e `true`/`false`
- Geração de nomes Python seguros para observações que colidam com palavras reservadas da linguagem alvo

---

## O que funciona

Todos os 5 exemplos de teste fornecidos compilam e executam corretamente:

- `exemplo1.obsact` — declaração de dispositivos, `set`, `se/entao/ligar` → ventilador ligado!
- `exemplo2.obsact` — broadcast de alerta com variável para múltiplos dispositivos
- `exemplo3.obsact` — múltiplos dispositivos, `se/entao/senao`, alerta simples e `ligar`/`desligar`
- `exemplo4.obsact` — `set` + `ligar` direto
- `exemplo5.obsact` — envio de alerta simples sem variável

A concatenação `msg + " " + str(observation)` na função `alerta` segue a especificação do enunciado: resultado é `msg + (espaço) + valor da variável`.

---

As validações semânticas foram separadas da análise sintática em `semantic.py`. Assim, o lexer continua usando `IDENT` para nomes em geral, enquanto a etapa semântica verifica o papel de cada identificador no contexto correto:

- `namedevice` deve conter somente letras.
- `observation` deve conter letras e números, começando por letra.
- Todo dispositivo usado por `ligar`, `desligar` ou `enviar alerta` precisa ter sido declarado.
- Toda observação usada em `set`, condições ou alerta com variável precisa ter sido declarada em algum dispositivo.
- Dispositivos duplicados são rejeitados.

---

## Quais os testes utilizados

5 arquivos de teste em `testes/`, baseados nos exemplos do enunciado (seção 1.2):

| Arquivo | Descrição |
|---|---|
| `exemplo1.obsact` | Termômetro + ventilador; atribuição e condicional simples |
| `exemplo2.obsact` | Broadcast de alerta com variável para monitor e celular |
| `exemplo3.obsact` | Múltiplos sensores; if-else; alerta simples |
| `exemplo4.obsact` | Atribuição + ligar direto |
| `exemplo5.obsact` | Alerta simples sem variável |

Saídas geradas (arquivos `.py`) estão na mesma pasta `testes/`.

Além dos exemplos positivos, foram verificados casos de erro semântico: uso de dispositivo não declarado, uso de observação não declarada, `namedevice` com número, arquivos UTF-8 com BOM e observação com nome que seria palavra reservada em Python.

---

## Como executar

**Pré-requisito:**
```bash
pip install ply
```

**Compilar um programa ObsAct:**
```bash
python obsact.py <entrada.obsact> <saida.py>
```

**Executar o Python gerado:**
```bash
python <saida.py>
```

**Exemplo completo:**
```bash
python obsact.py testes/exemplo1.obsact testes/exemplo1.py
python testes/exemplo1.py
# saída: ventilador ligado!
```

---

## Gramática final utilizada

A gramática final ficou próxima à proposta original, com as seguintes adições e ajustes:

```
programa  ->  devices cmds

devices   ->  device devices
           |  device

device    ->  dispositivo device_open IDENT }
           |  dispositivo device_open IDENT , IDENT }

device_open -> : {
            |  {

cmds      ->  cmd . cmds
           |  cmd .
           |  cmd cmds
           |  cmd

cmd       ->  attrib
           |  obsact
           |  act

attrib    ->  set IDENT = var

var       ->  NUMBER
           |  TRUE
           |  FALSE

obsact    ->  se obs entao act
           |  se obs entao act senao act

obs       ->  IDENT oplogic var
           |  IDENT oplogic var && obs

oplogic   ->  >  |  <  |  >=  |  <=  |  ==  |  !=

act       ->  ligar IDENT
           |  desligar IDENT
           |  enviar alerta alert_args IDENT
           |  enviar alerta alert_args para todos : namelist

alert_args -> ( STRING )
           |  ( STRING , IDENT )
           |  STRING
           |  STRING , IDENT

namelist  ->  IDENT
           |  IDENT , namelist
```

### Alterações em relação à gramática do enunciado

| Ponto | Alteração |
|---|---|
| `VAR -> num \| bool` | Fatorado como alternativas explícitas (`NUMBER`, `TRUE`, `FALSE`); o lexer aceita também `True`/`False` e `true`/`false` |
| `DEVICES -> DEVICE DEVICES \| DEVICES` | Recursão à esquerda solta no enunciado simplificada para `device devices \| device` (necessário para LALR(1)) |
| `ACT` broadcast | Adicionado nas duas formas: com e sem variável, conforme seção 1.1 do enunciado |
| `&&` em `obs` | Associativo à direita via recursão: `IDENT oplogic var && obs` |
| `cmd -> act` | Adicionado para permitir ações sem condição (`ligar`, `desligar` e `enviar alerta` diretamente) |
| Terminal `.` | O ponto continua aceito como finalizador de comando, mas também foi permitido omiti-lo para cobrir exemplos do enunciado que aparecem sem o ponto final |
| `device_open` | Permite `dispositivo: { ... }` e `dispositivo { ... }`, cobrindo a forma principal da gramática e variações dos exemplos |
| `alert_args` | Fatora as formas de alerta e aceita mensagem com ou sem parênteses, pois os exemplos do PDF alternam entre as duas formas |
| Validação semântica | Implementada fora da gramática em `semantic.py`: declarações, duplicidade, formato de nomes e existência de dispositivos/observações |

---

## Estrutura dos arquivos

```
Trabalho 2026.1/
├── obsact.py       # driver principal (lê .obsact, escreve .py)
├── lexer.py        # analisador léxico (PLY lex)
├── parser.py       # analisador sintático LALR(1) + construção de AST (PLY yacc)
├── semantic.py     # validação semântica e tabela de símbolos
├── codegen.py      # gerador de código Python a partir da AST
├── README.md       # este relatório
└── testes/
    ├── exemplo1.obsact ... exemplo5.obsact   # casos de teste
    └── exemplo1.py   ... exemplo5.py         # saídas geradas
```
