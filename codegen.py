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

def gen_obs(obs):
    parts = []
    for _, name, op, var in obs:
        parts.append(f"{name} {op} {py_var(var)}")
    return ' and '.join(parts)

def gen_act(act, indent):
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
            out += f"{pad}alerta({d!r}, {msg!r}, {var})\n"
    return out

def gen_cmd(cmd, indent):
    pad = '    ' * indent
    tag = cmd[0]
    if tag == 'attrib':
        return f"{pad}{cmd[1]} = {py_var(cmd[2])}\n"
    if tag == 'if':
        _, obs, then_act, else_act = cmd
        out = f"{pad}if {gen_obs(obs)}:\n"
        out += gen_act(then_act, indent + 1)
        if else_act is not None:
            out += f"{pad}else:\n"
            out += gen_act(else_act, indent + 1)
        return out
    # bare act
    return gen_act(cmd, indent)

def generate(ast):
    _, devices, cmds = ast
    out = RUNTIME + '\n'
    out += 'def main():\n'
    # observations default 0
    seen = set()
    for _, _name, obs in devices:
        if obs and obs not in seen:
            out += f"    {obs} = 0\n"
            seen.add(obs)
    if not seen:
        out += '    pass\n'
    out += '\n'
    for c in cmds:
        out += gen_cmd(c, 1)
    out += '\nif __name__ == "__main__":\n    main()\n'
    return out
