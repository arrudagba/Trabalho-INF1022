#!/usr/bin/env python3
"""Gera (transpila) todos os arquivos .obsact da pasta testes/ para .py.

Uso:
    python gerar_testes.py            # transpila tudo
    python gerar_testes.py --run      # transpila e executa cada .py gerado
    python gerar_testes.py --dir pasta  # usa outra pasta (padrao: testes)

Codigo de saida: 0 se nada inesperado, 1 se algum .obsact que deveria
compilar falhou. Arquivos cujo nome contem 'invalido', 'negativo', 'vazia',
'sem_lista' ou 'ponto' sao tratados como testes negativos (devem falhar).
"""
import argparse
import subprocess
import sys
from pathlib import Path

# Trechos de nome que indicam um teste que DEVE falhar (rejeicao esperada).
NEGATIVOS = ('invalido', 'negativo', 'vazia', 'vazio', 'sem_lista', 'entao_ponto')
# Testes negativos cujo nome nao casa o heuristico acima (lista explicita).
NEGATIVOS_EXPLICITOS = {'exemplo12_umidade'}


def eh_negativo(nome):
    return nome in NEGATIVOS_EXPLICITOS or any(t in nome for t in NEGATIVOS)


def main():
    ap = argparse.ArgumentParser(description="Transpila todos os .obsact de testes/")
    ap.add_argument('--dir', default='testes', help='pasta com os .obsact (padrao: testes)')
    ap.add_argument('--run', action='store_true', help='executa cada .py gerado')
    args = ap.parse_args()

    raiz = Path(__file__).resolve().parent
    pasta = (raiz / args.dir).resolve()
    if not pasta.is_dir():
        print(f"Pasta nao encontrada: {pasta}")
        return 2

    arquivos = sorted(pasta.glob('*.obsact'))
    if not arquivos:
        print(f"Nenhum .obsact em {pasta}")
        return 2

    ok = falhou = rejeitado = 0
    inesperados = []

    for obsact in arquivos:
        destino = obsact.with_suffix('.py')
        negativo = eh_negativo(obsact.stem)
        proc = subprocess.run(
            [sys.executable, str(raiz / 'obsact.py'), str(obsact), str(destino)],
            capture_output=True, text=True,
        )
        gerou = proc.returncode == 0

        if gerou:
            status = 'OK   ' if not negativo else 'OK?  '
            ok += 1
            if negativo:
                # Esperava rejeicao mas compilou.
                inesperados.append(f"{obsact.name}: esperava rejeicao, mas compilou")
        else:
            if negativo:
                status = 'REJEI'  # rejeicao esperada
                rejeitado += 1
            else:
                status = 'FALHA'
                falhou += 1
                inesperados.append(f"{obsact.name}: deveria compilar, mas falhou")

        print(f"[{status}] {obsact.name}")
        saida = (proc.stdout + proc.stderr).strip()
        if saida and not gerou:
            for linha in saida.splitlines():
                print(f"        {linha}")

        if args.run and gerou:
            run = subprocess.run(
                [sys.executable, str(destino)],
                capture_output=True, text=True, timeout=10,
            )
            corpo = (run.stdout + run.stderr).strip()
            for linha in corpo.splitlines():
                print(f"        > {linha}")
            if run.returncode != 0:
                print(f"        > [erro de execucao, exit {run.returncode}]")

    print("\n" + "-" * 40)
    print(f"compilaram: {ok}   rejeitados(esperado): {rejeitado}   falhas: {falhou}")
    if inesperados:
        print("INESPERADOS:")
        for m in inesperados:
            print(f"  - {m}")
        return 1
    print("Tudo conforme esperado.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
