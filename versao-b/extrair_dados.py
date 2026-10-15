"""Gera versao-b/dados.js a partir de editavel/index.html (fonte única dos dados da OS).

Uso (na raiz do repositório):  python3 versao-b/extrair_dados.py
Copia, sem alterar, os blocos SHAPES (contornos), PAGES, PAGE_NAMES, R (funções) e PROJECTS (itens da OS).
Os caminhos das pranchas e PDFs passam a apontar para ../editavel/.
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(AQUI, '..', 'editavel', 'index.html')
SAIDA = os.path.join(AQUI, 'dados.js')

html = open(FONTE, encoding='utf-8').read()


def bloco(regex):
    m = re.search(regex, html, re.S | re.M)
    if not m:
        sys.exit('Bloco não encontrado: ' + regex)
    return m.group(1)


shapes = bloco(r'/\*CONTORNOS-INICIO\*/(const SHAPES=.*?;)/\*CONTORNOS-FIM\*/')
pages = bloco(r'^(const PAGES=\{[^\n]*?\};)$')
names = bloco(r'^(const PAGE_NAMES=\{.*?\};)$')
funcs = bloco(r'^(const R=\{[^\n]*?\};)$')
projects = bloco(r'^(const PROJECTS=\[.*?\n\];)\n')

pages = pages.replace('"pranchas/', '"../editavel/pranchas/')
docs = 'const DOCS={os:"../editavel/pdf/os.pdf",stand:"../editavel/pdf/stand.pdf",fest:"../editavel/pdf/fest.pdf"};'

out = '\n'.join([
    '/* Gerado por extrair_dados.py a partir de editavel/index.html. Não editar à mão. */',
    shapes, pages, names, docs, funcs, projects, ''])
open(SAIDA, 'w', encoding='utf-8').write(out)
print('OK:', os.path.abspath(SAIDA), f'{len(out) // 1024} KB')
