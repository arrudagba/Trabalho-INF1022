import keyword
import re


DEVICE_RE = re.compile(r'^[A-Za-z]+$')
OBSERVATION_RE = re.compile(r'^[A-Za-z][A-Za-z0-9]*$')
RUNTIME_NAMES = {'ligar', 'desligar', 'alerta', 'main'}


class SemanticError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('\n'.join(errors))

    def __str__(self):
        return '\n'.join(f'ERRO SEMANTICO: {error}' for error in self.errors)


def validate(ast):
    _, devices, cmds = ast
    errors = []
    device_names = {}
    observations = {}

    for _, name, observation in devices:
        if not _valid_device_name(name):
            errors.append(
                f"namedevice '{name}' invalido na declaracao; use somente letras"
            )
        elif name in device_names:
            errors.append(f"dispositivo '{name}' declarado mais de uma vez")
        else:
            device_names[name] = observation

        if observation is not None:
            if not _valid_observation_name(observation):
                errors.append(
                    f"observation '{observation}' invalida; use letras e numeros, comecando por letra"
                )
            else:
                observations.setdefault(observation, []).append(name)

    for cmd in cmds:
        _validate_cmd(cmd, device_names, observations, errors)

    if errors:
        raise SemanticError(errors)

    observation_names = list(observations)
    return {
        'devices': set(device_names),
        'observations': observation_names,
        'observation_devices': observations,
        'py_names': _make_python_names(observation_names),
    }


def _validate_cmd(cmd, devices, observations, errors):
    tag = cmd[0]

    if tag == 'attrib':
        _, observation, _value = cmd
        _require_observation(observation, observations, 'atribuicao', errors)
        return

    if tag == 'if':
        _, obs, then_act, else_act = cmd
        for _, observation, _op, _value in obs:
            _require_observation(observation, observations, 'condicao', errors)
        _validate_act(then_act, devices, observations, errors)
        if else_act is not None:
            _validate_act(else_act, devices, observations, errors)
        return

    _validate_act(cmd, devices, observations, errors)


def _validate_act(act, devices, observations, errors):
    if act[0] == 'action':
        _, _action, device = act
        _require_device(device, devices, 'acao', errors)
        return

    _, _msg, observation, target_devices = act
    if observation is not None:
        _require_observation(observation, observations, 'alerta', errors)

    for device in target_devices:
        _require_device(device, devices, 'alerta', errors)


def _require_device(name, devices, context, errors):
    if not _valid_device_name(name):
        errors.append(
            f"namedevice '{name}' invalido em {context}; use somente letras"
        )
        return

    if name not in devices:
        errors.append(f"dispositivo '{name}' usado em {context} nao foi declarado")


def _require_observation(name, observations, context, errors):
    if not _valid_observation_name(name):
        errors.append(
            f"observation '{name}' invalida em {context}; use letras e numeros, comecando por letra"
        )
        return

    if name not in observations:
        errors.append(
            f"observation '{name}' usada em {context} nao foi declarada em nenhum dispositivo"
        )


def _valid_device_name(name):
    return DEVICE_RE.fullmatch(name) is not None


def _valid_observation_name(name):
    return OBSERVATION_RE.fullmatch(name) is not None


def _make_python_names(observations):
    names = {}
    used = set(RUNTIME_NAMES)

    for observation in observations:
        candidate = observation
        if (
            not candidate.isidentifier()
            or keyword.iskeyword(candidate)
            or candidate in used
        ):
            candidate = f'obs_{observation}'

        base = candidate
        suffix = 2
        while candidate in used:
            candidate = f'{base}_{suffix}'
            suffix += 1

        used.add(candidate)
        names[observation] = candidate

    return names
