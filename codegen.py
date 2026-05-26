RUNTIME = '''def ligar(namedevice):
    print(namedevice + " ligado!")

def desligar(namedevice):
    print(namedevice + " desligado!")

def alerta(namedevice, msg, var=None):
    print(namedevice + " recebeu o alerta:")
    if var is None:
        print(msg)
    else:
        print(msg + " " + str(var))
'''

def py_var(v):
    tag, val = v
    if tag == 'bool':
        return 'True' if val else 'False'
    return str(val)

def py_observation(name, symbols):
    return symbols.get('py_names', {}).get(name, name)

def gen_obs(obs, symbols):
    parts = []
    for _, name, op, var in obs:
        parts.append(f"{py_observation(name, symbols)} {op} {py_var(var)}")
    return ' and '.join(parts)

def gen_act(act, indent, symbols):
    pad = '    ' * indent
    if act[0] == 'action':
        return f"{pad}{act[1]}({act[2]!r})\n"
    # alert
    _, msg, var, devices = act
    out = ''
    for d in devices:
        if var is None:
            out += f"{pad}alerta({d!r}, {msg!r})\n"
        else:
            out += f"{pad}alerta({d!r}, {msg!r}, {py_observation(var, symbols)})\n"
    return out

def gen_cmd(cmd, indent, symbols):
    pad = '    ' * indent
    tag = cmd[0]
    if tag == 'attrib':
        return f"{pad}{py_observation(cmd[1], symbols)} = {py_var(cmd[2])}\n"
    if tag == 'if':
        _, obs, then_act, else_act = cmd
        out = f"{pad}if {gen_obs(obs, symbols)}:\n"
        out += gen_act(then_act, indent + 1, symbols)
        if else_act is not None:
            out += f"{pad}else:\n"
            out += gen_act(else_act, indent + 1, symbols)
        return out
    # bare act
    return gen_act(cmd, indent, symbols)

def generate(ast, symbols=None):
    _, devices, cmds = ast
    if symbols is None:
        observations = []
        for _, _name, obs in devices:
            if obs and obs not in observations:
                observations.append(obs)
        symbols = {
            'observations': observations,
            'py_names': {obs: obs for obs in observations},
        }

    out = RUNTIME + '\n'
    out += 'def main():\n'

    body = ''
    for obs in symbols.get('observations', []):
        body += f"    {py_observation(obs, symbols)} = 0\n"

    for c in cmds:
        body += gen_cmd(c, 1, symbols)

    if body:
        out += body
    else:
        out += '    pass\n'

    out += '\nif __name__ == "__main__":\n    main()\n'
    return out
