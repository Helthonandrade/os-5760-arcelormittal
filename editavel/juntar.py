"""Gera um HTML único (com pranchas e PDFs embutidos) a partir de editavel/index.html.
Uso: python3 juntar.py  ->  cria ../visualizador-OS5760-completo.html"""
import base64, os, re
aqui = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(aqui, 'index.html'), encoding='utf-8').read()
def embutir(m):
    caminho, tipo = m.group(1), ('image/jpeg' if m.group(1).endswith('.jpg') else 'application/pdf')
    dados = base64.b64encode(open(os.path.join(aqui, caminho), 'rb').read()).decode()
    return f'"data:{tipo};base64,{dados}"'
html = re.sub(r'"((?:pranchas|pdf)/[\w-]+\.(?:jpg|pdf))"', embutir, html)
saida = os.path.join(aqui, '..', 'visualizador-OS5760-completo.html')
open(saida, 'w', encoding='utf-8').write(html)
print('OK:', os.path.abspath(saida))
