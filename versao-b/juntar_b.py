"""Gera um arquivo único e offline da Versão B: versao-b/fluxograma-versao-b.html

Uso (na raiz do repositório):  python3 versao-b/juntar_b.py [--com-pdfs]
Embute dados.js, as 33 pranchas e o PDF da OS. Com --com-pdfs, embute também os executivos
(o arquivo passa de ~5 MB para ~31 MB).
"""
import base64, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, '..')
html = open(os.path.join(AQUI, 'index.html'), encoding='utf-8').read()
dados = open(os.path.join(AQUI, 'dados.js'), encoding='utf-8').read()
com_pdfs = '--com-pdfs' in sys.argv

def uri(rel):
    caminho = os.path.normpath(os.path.join(AQUI, rel))
    tipo = 'image/jpeg' if caminho.endswith('.jpg') else 'application/pdf'
    return f'"data:{tipo};base64,{base64.b64encode(open(caminho, "rb").read()).decode()}"'

dados = re.sub(r'"(\.\./editavel/pranchas/[\w-]+\.jpg)"', lambda m: uri(m.group(1)), dados)
def doc(m):
    nome, rel = m.group(1), m.group(2)
    return f'{nome}:' + (uri(rel) if (nome == 'os' or com_pdfs) else '""')
dados = re.sub(r'(os|stand|fest):"(\.\./editavel/pdf/\w+\.pdf)"', doc, dados)
html = html.replace('<script src="dados.js"></script>', '<script>\n' + dados.replace('</script', '<\\/script') + '\n</script>')
saida = os.path.join(AQUI, 'fluxograma-versao-b.html')
open(saida, 'w', encoding='utf-8').write(html)
print('OK:', os.path.abspath(saida), f'{os.path.getsize(saida) / 1e6:.1f} MB')
