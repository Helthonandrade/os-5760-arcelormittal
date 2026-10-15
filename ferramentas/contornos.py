"""Gera os contornos (SVG) das peças a partir dos pixels das pranchas.

Uso (a partir da raiz do repositório):
    python3 ferramentas/contornos.py            -> grava os contornos em editavel/index.html
    python3 ferramentas/contornos.py --conferir -> também gera imagens de conferência em ferramentas/conferencia/

Cada alvo define uma região (polígono em % da prancha) e um modo de seleção:
  color : pixels dentro da região com uma das cores indicadas (HSV do OpenCV)
  ink   : traço/preenchimento não branco dentro da região (desenhos em linha)
  poly  : o próprio polígono, traçado à mão sobre a prancha (sem pixels a segmentar)
O contorno resultante segue o recorte real dos pixels; não é uma caixa.
Requer: opencv-python-headless, numpy.
"""
import json, os, re, sys
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITAVEL = os.path.join(AQUI, '..', 'editavel')
HTML = os.path.join(EDITAVEL, 'index.html')

# Cores em HSV do OpenCV (H 0-180). Cada cor é uma lista de faixas [hmin,hmax,smin,smax,vmin,vmax].
CORES = {
    'q25_laranja': [[5, 14, 120, 255, 120, 255]],
    'q25_amarelo': [[17, 33, 90, 255, 150, 255]],
    'q25_verde': [[42, 72, 70, 255, 90, 255]],
    'q25_ciano': [[80, 102, 110, 255, 120, 255]],
    'q25_rosa': [[150, 176, 50, 210, 150, 255]],
    'vermelho': [[0, 4, 150, 255, 190, 255], [176, 180, 150, 255, 190, 255]],
    'parica': [[8, 24, 25, 120, 130, 225]],
    'laranja': [[3, 22, 120, 255, 100, 255]],
    'laranja_vivo': [[3, 20, 180, 255, 150, 255]],
    'laranja_mapa': [[12, 16, 200, 255, 200, 255]],
    'roxo': [[118, 140, 70, 230, 110, 255]],
    'magenta': [[135, 175, 60, 255, 60, 255]],
    'lima': [[30, 52, 70, 230, 170, 255]],
    'petroleo': [[80, 105, 120, 255, 25, 170]],
    'escuro': [[0, 180, 0, 50, 0, 105]],
    'cinza': [[0, 180, 0, 45, 120, 215]],
    'cinza_claro': [[0, 180, 0, 40, 150, 236]],
    'branco': [[0, 180, 0, 45, 222, 255]],
    'roxo_escuro': [[112, 150, 80, 255, 25, 130]],
    'oliva': [[22, 48, 50, 220, 90, 215]],
    'carpete_palco': [[3, 10, 230, 255, 185, 240]],
    'branco_creme': [[15, 40, 15, 90, 225, 255]],
    'gradiente': [[150, 180, 60, 255, 90, 255], [0, 12, 60, 255, 120, 255]],
}


def R(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


# ---------------------------------------------------------------------------------------------
# ALVOS: sub = número do subitem na OS; page = prancha; conf = traçado | manual | provisorio
# ---------------------------------------------------------------------------------------------
Q25 = [[4, 11], [30.5, 11], [64.5, 38], [64.5, 74], [4, 74]]
Q25_LAT = R(67, 3, 91.5, 47)
ALVOS = [
    # ============================ ESTANDE ===============================
    # 1.1 Estrutura em box Q25 (prancha 05/09)
    dict(sub='1.1.1', page='stand-06', mode='color', cores=['q25_laranja'], regions=[Q25, Q25_LAT], minArea=25, close=1),
    dict(sub='1.1.2', page='stand-06', mode='color', cores=['q25_rosa'], regions=[Q25, Q25_LAT], minArea=25, close=1),
    dict(sub='1.1.3', page='stand-06', mode='color', cores=['q25_verde'], regions=[Q25, Q25_LAT], minArea=25, close=1),
    dict(sub='1.1.4', page='stand-06', mode='color', cores=['q25_ciano'], regions=[Q25, Q25_LAT], minArea=25, close=1),
    dict(sub='1.1.5', page='stand-06', mode='color', cores=['q25_amarelo'], regions=[Q25, Q25_LAT], minArea=25, close=1),
    dict(sub='1.1.6', page='stand-06', mode='color', cores=['vermelho'], regions=[Q25], minArea=12, close=1),
    dict(sub='1.1.7', page='stand-06', mode='color', cores=['parica'], regions=[R(69.5, 19, 80.5, 45)], minArea=40, close=2, fill=4000),
    dict(sub='1.1.8', page='stand-06', mode='color', cores=['q25_laranja', 'q25_rosa', 'q25_verde', 'q25_ciano', 'q25_amarelo', 'vermelho'],
         regions=[Q25, Q25_LAT], minArea=60, close=2, group='all'),
    dict(sub='1.1.8', page='stand-03', mode='color', cores=['laranja'], regions=[[[19, 25], [42, 7], [74, 33], [74, 64], [51, 79], [19, 53]]],
         minArea=400, close=2, fill=200000, seeds=[[21, 45]], group='all'),
    # 1.2 Grades, fechamento e mapa (prancha 06/09 e planta 03/09)
    dict(sub='1.2.1', page='stand-07', mode='color', cores=['laranja'], regions=[R(6.2, 14.5, 21.8, 60)], minArea=200, close=2, fill=900000),
    dict(sub='1.2.1', page='stand-04', mode='ink', regions=[R(35.6, 22.9, 44.5, 24.6), R(35.6, 68.4, 44.5, 70.1), R(72.1, 25.4, 73.4, 35.9)],
         minArea=8, close=2, fill=5000, conf='traçado'),
    dict(sub='1.2.1', page='stand-03', mode='ink', regions=[[[28.2, 42.3], [33.7, 45.3], [33.7, 62.8], [28.2, 59.7]], [[66.4, 44.4], [71.2, 41.1], [71.2, 58.6], [66.4, 62.2]]],
         minArea=30, close=2, fill=20000),
    dict(sub='1.2.2', page='stand-09', mode='color', cores=['parica'], regions=[R(6.4, 33.4, 9, 36.8), R(54.8, 33.4, 57.3, 36.8)], minArea=10, close=1, fill=2000),
    dict(sub='1.2.2', page='stand-04', mode='color', cores=['parica'], regions=[R(36.3, 22.4, 37.5, 25), R(44.4, 22.4, 45.5, 25), R(36.3, 68, 37.5, 70.6), R(44.4, 68, 45.5, 70.6), R(71.5, 24, 73.6, 26.5), R(71.5, 34.7, 73.6, 37)],
         minArea=3, close=1, fill=500, conf='provisorio', note='Na planta o enchimento aparece como pequenos blocos junto aos pilares; a forma exata depende do detalhe de vão 150 x 325 cm.'),
    dict(sub='1.2.3', page='stand-07', mode='color', cores=['laranja', 'gradiente'], regions=[R(44.2, 23.3, 85, 54.8)], minArea=500, close=2, fill=900000, group='all'),
    dict(sub='1.2.4', page='stand-07', mode='poly', polys=[[[48.9, 22.7], [51.6, 22.7], [51.6, 24.4], [48.9, 24.4]]], conf='provisorio',
         note='A prancha 06/09 aponta o forro em napa para o topo do fechamento, sem desenhar a faixa; a prancha 02/09 indica napa laranja na testeira.'),
    dict(sub='1.2.5', page='stand-07', mode='color', cores=['laranja_mapa', 'magenta'], regions=[R(46.5, 27.5, 61.8, 49.5)], minArea=150, open=1, close=3, fill=60000, group='all'),
    dict(sub='1.2.5', page='stand-09', mode='color', cores=['laranja_mapa', 'magenta'], regions=[R(9.5, 38.5, 28.2, 65.5)], minArea=150, open=1, close=3, fill=60000, group='all'),
    dict(sub='1.2.6', page='stand-07', mode='color', cores=['laranja_mapa', 'magenta'], regions=[R(46.5, 27.5, 61.8, 49.5)], minArea=150, open=1, close=3, fill=60000, group='all',
         conf='provisorio', note='A prancha não mostra a posição nem a quantidade de pregos e linhas: o destaque indica só a área do mapa.'),
    # 1.3 Testeira (prancha 07/09)
    dict(sub='1.3.1', page='stand-08', mode='color', cores=['laranja'], regions=[[[9, 47], [52, 14], [52.5, 26], [10, 59]], R(26.8, 60.2, 87.5, 73.6)], minArea=40, close=2, fill=3000),
    dict(sub='1.3.2', page='stand-08', mode='poly', polys=[[[11.2, 46.1], [48.6, 15.6], [49.6, 16.6], [12.2, 47.2]]], conf='provisorio',
         note='O apoio superior só aparece como chamada na vista isométrica; não há detalhe de seção ou fixação.'),
    dict(sub='1.3.3', page='stand-08', mode='color', cores=['cinza_claro'], regions=[R(54.4, 61.5, 84, 71.8)], minArea=6, close=3, fill=4000, group='all'),
    dict(sub='1.3.3', page='stand-08', mode='color', cores=['cinza_claro'], regions=[[[28.5, 39], [48.5, 21.3], [49.8, 23.8], [29.8, 41.5]], [[29, 35], [49, 17], [49.6, 18.6], [29.4, 36.6]]],
         minArea=6, close=3, fill=4000, group='all'),
    dict(sub='1.3.4', page='stand-08', mode='color', cores=['cinza_claro'], regions=[R(31, 61.5, 44, 72.6)], minArea=6, close=3, fill=4000, group='all'),
    dict(sub='1.3.4', page='stand-08', mode='color', cores=['cinza_claro'], regions=[[[12, 53], [21, 41.5], [21.8, 45], [12.6, 56]]], minArea=6, close=3, fill=4000, group='all'),
    # 1.4 Cobertura (prancha 08/09)
    dict(sub='1.4.1', page='stand-09', mode='ink', regions=[R(66.6, 50.6, 91.3, 75)], minArea=200, close=3, fill=900000, seeds=[[79, 62]]),
    dict(sub='1.4.2', page='stand-09', mode='color', cores=['branco_creme'], regions=[[[8.2, 23.2], [57.6, 29.6], [57.6, 30.6], [8.2, 24.6]]], minArea=40, close=2),
    dict(sub='1.4.2', page='stand-09', mode='ink', regions=[R(66.6, 50.6, 91.3, 75)], minArea=200, close=3, fill=900000, seeds=[[79, 62]]),
    dict(sub='1.4.3', page='stand-09', mode='color', cores=['laranja'], regions=[R(56.9, 23.2, 59, 33.8)], minArea=30, close=1, fill=3000),
    # 1.5 Balcões (prancha 09/09 e planta 03/09)
    dict(sub='1.5.1', page='stand-10', mode='ink', regions=[R(60.5, 23.5, 86, 70.5)], minArea=500, close=3, fill=900000, group='all'),
    dict(sub='1.5.1', page='stand-04', mode='poly', polys=[R(29.8, 26.5, 32.7, 34.4), R(29.8, 34.4, 32.7, 42.4), R(48.5, 51.1, 51.4, 59.1), R(48.5, 59.1, 51.4, 67.1), R(57.2, 27.3, 62.9, 31.3)], conf='traçado',
         note='Na planta os balcões são retângulos simples; o contorno segue as arestas desenhadas.'),
    dict(sub='1.5.2', page='stand-10', mode='color', cores=['gradiente', 'laranja'], regions=[[[61, 30], [77.6, 43], [77.6, 70.3], [61, 57]]], minArea=300, close=2, fill=90000, group='all'),
    dict(sub='1.5.3', page='stand-10', mode='ink', regions=[R(60.5, 23.5, 86, 70.5)], minArea=500, close=3, fill=900000, group='all', conf='provisorio',
         note='A posição do tambor com chave não está desenhada; o destaque mostra só o balcão.'),
    # 1.6 Totem de TV
    dict(sub='1.6.1', page='stand-10', mode='color', cores=['laranja', 'escuro', 'cinza'], regions=[R(16, 15, 34.5, 76.5)], minArea=500, close=3, fill=900000, group='all'),
    dict(sub='1.6.1', page='stand-04', mode='color', cores=['laranja'], regions=[R(51.3, 27.3, 55.5, 31.8)], minArea=10, close=2, fill=5000),
    dict(sub='1.6.2', page='stand-05', mode='color', cores=['laranja'], regions=[R(44.6, 24.3, 47.2, 29.3)], minArea=10, close=1, fill=2000),
    dict(sub='1.6.3', page='stand-10', mode='color', cores=['escuro', 'cinza'], regions=[R(20.6, 19.8, 28.6, 47)], minArea=200, close=2, fill=90000),
    # 1.7 Iluminação (prancha 04/09 e 06/09)
    dict(sub='1.7.1', page='stand-05', mode='color', cores=['laranja'], regions=[R(38.5, 21.5, 43.6, 22.7), R(38.5, 70.5, 43.6, 71.8), R(73.2, 27, 74, 34)], minArea=6, close=1),
    dict(sub='1.7.1', page='stand-07', mode='color', cores=['laranja_vivo'], regions=[R(10.6, 19.2, 17.2, 20.5), R(10.6, 27.9, 17.2, 29.3), R(10.6, 36.7, 17.2, 38.1), R(10.6, 45.3, 17.2, 46.7), R(10.6, 54, 17.2, 55.3)],
         minArea=4, close=1),
    dict(sub='1.7.2', page='stand-05', mode='color', cores=['laranja'], regions=[R(39.9, 25.2, 42.2, 28.2), R(39.9, 65.3, 42.2, 68.3), R(69.6, 29.2, 71.6, 31.6)], minArea=6, close=1, fill=500),
    dict(sub='1.7.3', page='stand-05', mode='color', cores=['laranja'], regions=[R(38.5, 21.5, 43.6, 28.4), R(38.5, 65.2, 43.6, 71.8), R(69.6, 27, 74, 34), R(44.6, 24.3, 47.2, 29.3)],
         minArea=6, close=1, fill=500, group='all'),
    # 1.8 Árvore cenográfica (somente imagens 3D)
    dict(sub='1.8.1', page='stand-02', mode='poly', conf='manual', note='Contorno traçado à mão sobre a imagem 3D; não há vista executiva da árvore.', polys=[
        [[15.6, 12.2], [17.2, 10.7], [20.5, 10.2], [25.5, 10.4], [28.4, 11.2], [28.9, 12.4], [27.2, 14.6], [24.6, 17.2], [23.6, 22], [23.4, 30], [23.9, 36], [24.2, 39.9], [22.3, 40.3], [20.4, 39.9], [20.9, 36], [21.6, 30], [21.5, 22], [20.4, 17.2], [17.6, 14.6]],
        [[55.1, 15.2], [57.2, 13.6], [61, 13.1], [65.2, 13.6], [67.6, 15.4], [66.2, 17.2], [63.6, 19.2], [62.7, 24], [62.6, 32], [63, 36], [63.4, 40], [61.6, 40.3], [60, 40], [60.5, 36], [61, 32], [61, 24], [59.6, 19.2], [57, 17.2]],
        [[8.6, 57.5], [10.2, 56.8], [13, 56.8], [15.8, 57.5], [14.5, 59], [13.2, 61], [12.9, 66], [13.3, 72.6], [11.2, 72.6], [11.8, 66], [11.9, 61], [10.2, 59]]]),
    dict(sub='1.8.2', page='stand-02', mode='poly', conf='manual', note='Fabricação bloqueada até haver desenho executivo; contorno da referência 3D.', polys=[
        [[15.6, 12.2], [17.2, 10.7], [20.5, 10.2], [25.5, 10.4], [28.4, 11.2], [28.9, 12.4], [27.2, 14.6], [24.6, 17.2], [23.6, 22], [23.4, 30], [23.9, 36], [24.2, 39.9], [22.3, 40.3], [20.4, 39.9], [20.9, 36], [21.6, 30], [21.5, 22], [20.4, 17.2], [17.6, 14.6]]]),
    # 1.9 Carpete (consta nas pranchas, não na OS)
    dict(sub='1.9.1', page='stand-04', mode='color', cores=['laranja'], regions=[R(23.5, 22.4, 73.6, 70.6)], minArea=2000, close=3, fill=900000, group='all'),

    # ============================ FESTIVAL LED ===============================
    # 2 Credenciamento (prancha 03/23)
    dict(sub='2.1', page='fest-04', mode='color', cores=['laranja', 'magenta', 'lima', 'roxo', 'petroleo', 'cinza_claro', 'cinza'], regions=[[[29.5, 52], [55.5, 30.8], [56, 39], [30.5, 60]]], minArea=500, close=3, fill=900000, group='all'),
    dict(sub='2.2', page='fest-04', mode='color', cores=['laranja', 'magenta', 'lima', 'roxo', 'petroleo'], regions=[[[32, 52.5], [55.6, 33], [55.6, 39.2], [32, 59.6]]], minArea=200, close=2, fill=90000, group='all'),
    dict(sub='2.3', page='fest-04', mode='color', cores=['cinza_claro'], regions=[[[29.6, 50.8], [53.5, 30.6], [56, 32.8], [32, 53]]], minArea=100, close=2, fill=30000, group='all'),
    dict(sub='2.4', page='fest-04', mode='color', cores=['laranja', 'magenta', 'lima', 'roxo', 'petroleo', 'cinza_claro', 'cinza'], regions=[[[29.5, 52], [55.5, 30.8], [56, 39], [30.5, 60]]], minArea=500, close=3, fill=900000, group='all', conf='provisorio',
         note='A cortina interna é citada em texto e não aparece desenhada; o destaque mostra o balcão.'),
    dict(sub='2.5', page='fest-04', mode='ink', regions=[[[22.6, 29], [46.3, 9.4], [48.6, 10.2], [48.6, 34], [24.6, 54]], R(73, 22.2, 93.3, 38.8)], minArea=800, close=3, fill=900000),
    dict(sub='2.6', page='fest-04', mode='color', cores=['cinza', 'cinza_claro', 'escuro'], regions=[R(40, 41.2, 76, 76.4)], minArea=150, close=4, group='all', exclude=[[[29.5, 52], [55.5, 30.8], [56, 39], [30.5, 60]], R(66.5, 65, 74.8, 72.6), R(40, 41, 48.5, 53)]),
    # 3 Totem acrílico (prancha 04/23)
    dict(sub='3.1', page='fest-05', mode='color', cores=['cinza', 'cinza_claro'], regions=[R(23.4, 17.2, 42.5, 66.7)], minArea=500, close=3, fill=900000),
    dict(sub='3.1', page='fest-05', mode='color', cores=['cinza', 'cinza_claro'], regions=[[[69.4, 28], [83.2, 17.2], [83.2, 56], [69.4, 66]]], minArea=500, close=3, fill=900000),
    dict(sub='3.2', page='fest-05', mode='color', cores=['branco'], regions=[R(26, 21, 40.5, 50)], minArea=15, close=3, fill=3000, group='all'),
    dict(sub='3.3', page='fest-05', mode='color', cores=['petroleo', 'escuro'], regions=[R(23.4, 66.4, 42.5, 75)], minArea=300, close=2, fill=90000),
    dict(sub='3.3', page='fest-05', mode='color', cores=['petroleo', 'escuro'], regions=[[[67.5, 66.5], [70, 64.5], [85.5, 56], [85.5, 65.5], [71.6, 76.6], [67.5, 73]]], minArea=300, close=2, fill=90000),
    # 4.1 Photo opp: estrutura, arcos e base
    dict(sub='4.1.1', page='fest-08', mode='color', cores=['laranja'], regions=[R(8, 19.5, 37.5, 57.5)], minArea=100, close=2, exclude=[[[38.85, 30.8], [38.43, 32.25], [37.4, 32.85], [36.37, 32.25], [35.95, 30.8], [36.37, 29.35], [37.4, 28.75], [38.43, 29.35]], [[34.25, 26.0], [33.83, 27.45], [32.8, 28.05], [31.77, 27.45], [31.35, 26.0], [31.77, 24.55], [32.8, 23.95], [33.83, 24.55]]]),
    dict(sub='4.1.1', page='fest-07', mode='color', cores=['laranja'], regions=[R(54.5, 37.5, 84, 75)], minArea=100, close=2),
    dict(sub='4.1.2', page='fest-08', mode='color', cores=['laranja', 'q25_ciano'], regions=[R(48, 29.5, 71, 60), R(51.5, 54.5, 74.5, 84)], minArea=100, close=2, exclude=[[[53.7, 86.3], [53.26, 87.8], [52.2, 88.42], [51.14, 87.8], [50.7, 86.3], [51.14, 84.8], [52.2, 84.18], [53.26, 84.8]], [[56.6, 86.0], [56.16, 87.5], [55.1, 88.12], [54.04, 87.5], [53.6, 86.0], [54.04, 84.5], [55.1, 83.88], [56.16, 84.5]], [[58.8, 83.3], [58.36, 84.8], [57.3, 85.42], [56.24, 84.8], [55.8, 83.3], [56.24, 81.8], [57.3, 81.18], [58.36, 81.8]], R(45, 52, 50.5, 62)]),
    dict(sub='4.1.3', page='fest-06', mode='color', cores=['petroleo'], regions=[[[21.2, 74.5], [62.8, 42], [65.3, 43.5], [65.3, 51], [25.5, 82.3], [21.2, 79]]], minArea=300, close=2, fill=90000, group='all'),
    dict(sub='4.1.3', page='fest-06', mode='color', cores=['petroleo'], regions=[R(66, 4, 88.6, 24.5)], minArea=200, close=2, fill=90000, group='all'),
    # 4.2 Letreiro e logo
    dict(sub='4.2.1', page='fest-06', mode='ink', regions=[R(72.8, 55.5, 87.6, 75)], minArea=300, close=3, fill=900000, group='all'),
    dict(sub='4.2.1', page='fest-06', mode='color', cores=['cinza', 'cinza_claro'], regions=[[[33.2, 56], [48.6, 44], [52.5, 40], [57, 42], [57, 52], [42, 63.5], [40, 69], [36, 73.5], [33.2, 72]]],
         minArea=150, close=3, fill=40000, group='all', conf='manual', note='Na isometria as letras se sobrepõem às chapas coloridas; a vista do luminoso (à direita) é a referência precisa.'),
    dict(sub='4.2.1', page='fest-06', mode='color', cores=['cinza', 'cinza_claro'], regions=[R(71.5, 3.2, 84.5, 18.7)], minArea=150, close=3, fill=40000, group='all'),
    dict(sub='4.2.2', page='fest-06', mode='ink', regions=[R(6, 16.3, 14.6, 28.4)], minArea=80, close=3, fill=90000, group='all'),
    dict(sub='4.2.2', page='fest-06', mode='ink', regions=[R(55.8, 30.7, 58.7, 35.2)], minArea=10, close=2, fill=9000, group='all', conf='provisorio',
         note='Na isometria o logo é pequeno; use o detalhe à esquerda como referência.'),
    dict(sub='4.2.3', page='fest-06', mode='ink', regions=[R(72.8, 55.5, 87.6, 75)], minArea=300, close=3, fill=900000, group='all', conf='provisorio',
         note='O ponto de alimentação do luminoso não está desenhado; o destaque mostra o luminoso.'),
    # 4.3 Triângulos (pranchas 08 a 10/23)
    dict(sub='4.3.1', page='fest-09', mode='color', cores=['laranja', 'roxo'], regions=[R(14, 44, 33, 72)], minArea=300, close=2, fill=90000),
    dict(sub='4.3.2', page='fest-09', mode='color', cores=['roxo', 'laranja'], regions=[[[55, 53], [61.5, 46], [71.4, 69], [70, 69.5]], [[71.2, 67.8], [80.6, 46.2], [86.7, 55], [72.4, 68.4]]], minArea=300, close=2, fill=90000),
    dict(sub='4.3.3', page='fest-10', mode='color', cores=['petroleo', 'lima'], regions=[[[12, 48.5], [19.5, 43], [23.8, 64.8]], [[23.6, 64.8], [27.8, 43], [35, 49]]], minArea=300, close=2, fill=90000),
    dict(sub='4.3.4', page='fest-10', mode='color', cores=['roxo'], regions=[[[57.6, 62.8], [61.8, 54], [71, 67.5]]], minArea=300, close=2, fill=90000),
    dict(sub='4.3.5', page='fest-10', mode='color', cores=['petroleo'], regions=[[[71, 67.5], [83.8, 50.6], [87.8, 61.5]]], minArea=300, close=2, fill=90000),
    dict(sub='4.3.6', page='fest-11', mode='color', cores=['laranja'], regions=[[[13.8, 68.6], [15.6, 59.2], [27.8, 68.6]]], minArea=200, close=2, fill=90000),
    dict(sub='4.3.7', page='fest-11', mode='color', cores=['oliva', 'lima'], regions=[[[20.4, 55.9], [21.4, 55.1], [26.4, 52.5], [27.9, 68.7], [26.7, 68.7]]], minArea=20, close=2, fill=90000, group='all'),
    dict(sub='4.3.8', page='fest-11', mode='color', cores=['roxo', 'lima', 'q25_amarelo', 'q25_verde'], regions=[[[63.6, 57.3], [65.5, 35.8], [73.2, 39.5]], [[63.6, 57.3], [77.4, 46.6], [79.2, 57.3]]], minArea=20, close=2, fill=90000),
    # 4.4 Montagem e base MDF
    dict(sub='4.4.1', page='fest-11', mode='color', cores=['lima'], regions=[R(72.5, 70.8, 82.5, 78.6)], minArea=200, close=2, fill=90000),
    dict(sub='4.4.1', page='fest-12', mode='color', cores=['lima'], regions=[R(58.6, 63.8, 64.6, 70.5)], minArea=60, close=2, fill=9000),
    dict(sub='4.4.2', page='fest-12', mode='color', cores=['laranja', 'roxo', 'lima', 'petroleo'], regions=[R(18.5, 16, 72, 76)], minArea=400, close=3, fill=20000, group='all'),
    # 5 Flâmulas
    dict(sub='5.1', page='fest-13', mode='color', cores=['laranja', 'roxo', 'roxo_escuro', 'magenta', 'lima', 'petroleo', 'escuro'], regions=[[[29.8, 39.8], [42.6, 29.6], [42.6, 68.7], [29.8, 78.8]]], minArea=500, close=3, fill=900000),
    dict(sub='5.2', page='fest-13', mode='color', cores=['laranja', 'roxo', 'roxo_escuro', 'magenta', 'lima', 'petroleo', 'escuro'], regions=[[[48.6, 24.3], [61.6, 14.1], [61.6, 53.3], [48.6, 63.4]]], minArea=500, close=3, fill=900000),
    dict(sub='5.3', page='fest-13', mode='ink', regions=[R(29.7, 9.5, 30.6, 39), R(35.8, 19.5, 36.6, 34), R(41.9, 14.5, 42.8, 30), R(48.7, 9.5, 49.6, 24.8), R(54.7, 4.5, 55.6, 19.5), R(60.8, 1, 61.8, 14.6)], minArea=4, close=2,
         conf='traçado', note='Cabos de suspensão como desenhados; pontos de fixação no local ainda não medidos.'),
    # 6 Cubos paperboard (prancha 13/23)
    dict(sub='6.1', page='fest-14', mode='color', cores=['gradiente', 'laranja', 'magenta', 'cinza_claro', 'cinza'], regions=[R(74.6, 43.5, 93, 68.5), R(54.8, 61, 70.8, 85)], minArea=300, open=2, close=3, fill=90000, exclude=[R(66, 82.5, 86, 88)]),
    dict(sub='6.1', page='fest-14', mode='color', cores=['gradiente', 'laranja', 'magenta'], regions=[R(7.2, 35.4, 17.2, 50.2), R(20.6, 24.8, 28.2, 39.2)], minArea=100, close=3, fill=90000, group='all',
         exclude=[R(14, 38.5, 22, 47)]),
    dict(sub='6.2', page='fest-14', mode='poly', conf='manual', note='Faces com arte dos 4 cubos (2 por conjunto), traçadas pelas arestas do desenho.', polys=[
        [[84.0, 48.6], [86.9, 46.3], [86.9, 51.4], [84.0, 53.3]], [[84.0, 57.9], [86.9, 55.9], [86.9, 60.6], [84.0, 62.6]],
        [[62.8, 65.9], [65.7, 63.7], [65.7, 68.5], [62.8, 70.6]], [[62.8, 75.6], [65.6, 73.5], [65.6, 78.1], [62.8, 80.1]]]),
    dict(sub='6.3', page='fest-14', mode='poly', conf='provisorio', polys=[[[23.2, 46.5], [24.6, 46.5], [24.6, 48.2], [23.2, 48.2]]],
         note='O carpete é citado na legenda "carpete + cubos" sem área desenhada; marcação apenas na legenda.'),
    # 7 Totem 2º pavimento (prancha 14/23)
    dict(sub='7.1', page='fest-15', mode='color', cores=['laranja', 'roxo', 'magenta', 'gradiente', 'cinza_claro'], regions=[R(25.2, 18.2, 43.6, 67.4)], minArea=500, close=3, fill=900000),
    dict(sub='7.1', page='fest-15', mode='color', cores=['laranja', 'roxo', 'magenta', 'gradiente', 'cinza_claro'], regions=[[[70.4, 25.8], [83.9, 15.4], [83.9, 55.6], [70.4, 65.4]]], minArea=500, close=3, fill=900000),
    dict(sub='7.2', page='fest-15', mode='color', cores=['gradiente', 'magenta', 'laranja'], regions=[R(25.2, 67.8, 43.6, 75.7)], minArea=300, close=2, fill=90000),
    dict(sub='7.2', page='fest-15', mode='color', cores=['gradiente', 'magenta', 'laranja'], regions=[[[68.5, 64], [70.6, 62.6], [71, 65.6], [84, 56], [85.8, 57.5], [85.8, 64], [72.4, 74], [68.5, 70.6]]], minArea=300, close=2, fill=90000, group='all'),
    # 8 Lounges
    dict(sub='8.1', page='fest-16', mode='color', cores=['laranja'], regions=[R(6, 46, 42, 76)], minArea=1000, close=2, fill=900000),
    dict(sub='8.2', page='fest-16', mode='color', cores=['laranja'], regions=[R(30.5, 12, 55, 45.5)], minArea=1000, close=2, fill=900000),
    # 9 Sala de imprensa
    dict(sub='9.1', page='fest-17', mode='color', cores=['laranja', 'escuro', 'lima'], regions=[[[18.2, 36.6], [42.2, 16.8], [45.6, 19.6], [45.6, 52.6], [21.4, 72], [18.2, 69.8]]], minArea=800, close=3, fill=900000),
    dict(sub='9.2', page='fest-17', mode='color', cores=['laranja', 'lima'], regions=[[[21.2, 38.6], [45.6, 19.6], [45.6, 52.6], [21.4, 72]]], minArea=800, close=3, fill=900000),
    # 10.1 Palco: LED e carpetes
    dict(sub='10.1.1', page='fest-18', mode='color', cores=['escuro'], regions=[[[30, 35], [51.4, 18], [54.6, 20.6], [54.6, 42.8], [38.4, 55.6], [34, 56.6], [30, 56.6]]], minArea=500, open=1, close=3, fill=90000, group='all'),
    dict(sub='10.1.1', page='fest-23', mode='color', cores=['escuro'], regions=[R(30.6, 15.2, 67.3, 43.5)], minArea=500, close=2, fill=900000, group='all'),
    dict(sub='10.1.4', page='fest-18', mode='color', cores=['escuro'], regions=[[[30, 35], [51.4, 18], [54.6, 20.6], [54.6, 42.8], [38.4, 55.6], [34, 56.6], [30, 56.6]]], minArea=500, open=1, close=3, fill=90000, group='all'),
    dict(sub='10.1.4', page='fest-23', mode='color', cores=['escuro'], regions=[R(30.6, 15.2, 67.3, 43.5)], minArea=500, close=2, fill=900000, group='all'),
    dict(sub='10.1.2', page='fest-19', mode='color', cores=['laranja_vivo'], regions=[R(22.6, 31.8, 76.6, 63.4)], minArea=2000, close=3, fill=200000, group='all'),
    dict(sub='10.1.2', page='fest-18', mode='color', cores=['carpete_palco'], regions=[R(17.5, 30, 75, 77.5)], minArea=1500, open=1, close=3, fill=40000, group='all'),
    dict(sub='10.1.3', page='fest-19', mode='color', cores=['roxo'], regions=[R(31.4, 42.4, 39, 53.4), R(26, 50.5, 33.4, 61), R(63.2, 48.8, 70.4, 59.4)], minArea=200, close=3, fill=20000),
    dict(sub='10.1.3', page='fest-18', mode='color', cores=['roxo'], regions=[R(32.2, 63.6, 41.6, 71.8), R(31.8, 71.6, 41.4, 80.4), R(66.2, 43.6, 75.8, 52)], minArea=200, close=3, fill=20000),
    # 10.2 Estruturas de fundo
    dict(sub='10.2.1', page='fest-20', mode='color', cores=['escuro'], regions=[R(10, 20.6, 31.8, 74)], minArea=300, close=1),
    dict(sub='10.2.2', page='fest-23', mode='poly', conf='manual', note='Divisão em três blocos sugerida pela vista frontal (420 + 650 + 420 cm); a divisão física ainda precisa ser definida.', polys=[
        R(6.9, 15.4, 30.7, 51.4), R(30.7, 43.3, 67.6, 51.4), R(67.3, 15.4, 91, 51.4)]),
]

# Vista frontal (prancha 22/23): colunas e linhas da grade de quadros, em %
LAT_E = [7.0, 10.95, 14.9, 18.85, 22.8, 26.75, 30.7]
LAT_D = [67.35, 71.3, 75.25, 79.2, 83.15, 87.1, 91.0]
LIN = [15.5, 22.45, 29.45, 36.4, 43.4, 51.35]
CEN = [30.7, 38.05, 45.4, 52.75, 60.1, 67.45]


def cel(cols, i0, i1, r0, r1, pad=0.25):
    return R(cols[i0] + pad, LIN[r0] + pad, cols[i1] - pad, LIN[r1] - pad)


QUADROS = {  # tipo: (cor, células nas duas laterais)
    '01': ('laranja_vivo', [(0, 2, 0, 1), (0, 2, 2, 3)]),
    '02': ('roxo', [(2, 4, 0, 1), (2, 4, 2, 3)]),
    '03': ('lima', [(4, 6, 0, 1), (4, 6, 2, 3)]),
    '04': ('roxo', [(0, 1, 1, 2), (5, 6, 1, 2), (0, 1, 3, 4), (5, 6, 3, 4)]),
    '05': ('lima', [(1, 3, 1, 2), (1, 3, 3, 4)]),
    '06': ('laranja', [(3, 5, 1, 2), (3, 5, 3, 4)]),
    '07': ('laranja_vivo', [(0, 2, 4, 5)]),
    '08': ('roxo', [(2, 4, 4, 5)]),
    '09': ('lima', [(4, 6, 4, 5)]),
}
for n, (tipo, (cor, cels)) in enumerate(QUADROS.items(), start=1):
    regs = [cel(cols, *c) for cols in (LAT_E, LAT_D) for c in cels]
    ALVOS.append(dict(sub=f'10.3.{n}', page='fest-23', mode='color', cores=[cor, 'cinza_claro'], regions=regs, minArea=80, close=2, fill=20000))
# Centro do palco: 07 (1), 08 (2), 09 (2)
ALVOS += [
    dict(sub='10.4.1', page='fest-23', mode='color', cores=['laranja_vivo'], regions=[R(CEN[0] + .25, 43.65, CEN[1] - .25, 51.1)], minArea=80, close=2, fill=20000),
    dict(sub='10.4.2', page='fest-23', mode='color', cores=['roxo'], regions=[R(CEN[1] + .25, 43.65, CEN[2] - .25, 51.1), R(CEN[3] + .25, 43.65, CEN[4] - .25, 51.1)], minArea=80, close=2, fill=20000),
    dict(sub='10.4.3', page='fest-23', mode='color', cores=['lima', 'q25_verde'], regions=[R(CEN[2] + .25, 43.65, CEN[3] - .25, 51.1), R(CEN[4] + .25, 43.65, CEN[5] - .25, 51.1)], minArea=80, close=2, fill=20000),
    dict(sub='10.4.1', page='fest-22', mode='color', cores=['laranja_vivo'], regions=[R(7, 63, 14, 72.4)], minArea=80, close=2, fill=20000),
    dict(sub='10.4.2', page='fest-22', mode='color', cores=['roxo'], regions=[R(12.4, 57.6, 19.2, 66.4), R(24.6, 47, 31.6, 56)], minArea=80, close=2, fill=20000),
    dict(sub='10.4.3', page='fest-22', mode='color', cores=['lima'], regions=[R(18.4, 52.4, 25.2, 61.2), R(31.6, 42.6, 39.6, 51.6)], minArea=80, close=2, fill=20000),
    # 10.5 Logos
    dict(sub='10.5.1', page='fest-24', mode='ink', regions=[R(6.4, 65.6, 26.3, 79.8)], minArea=100, close=3, fill=60000, group='all'),
    dict(sub='10.5.1', page='fest-24', mode='color', cores=['branco'], regions=[R(13, 27.2, 26.4, 37)], minArea=30, close=3, fill=20000, group='all'),
    dict(sub='10.5.2', page='fest-24', mode='ink', regions=[R(40.4, 69.2, 58.4, 77.4)], minArea=60, close=3, fill=60000, group='all'),
    dict(sub='10.5.2', page='fest-24', mode='color', cores=['branco'], regions=[R(72, 27.2, 84.3, 32.4)], minArea=30, close=3, fill=20000, group='all'),
    dict(sub='10.5.3', page='fest-24', mode='ink', regions=[R(69.3, 70.3, 85.4, 77.4)], minArea=60, close=3, fill=60000, group='all'),
    dict(sub='10.5.3', page='fest-24', mode='color', cores=['branco', 'cinza_claro'], regions=[R(72.4, 33.6, 83.4, 38.8)], minArea=30, close=3, fill=20000, group='all'),
]
# Quadros na isometria das laterais (prancha 20/23): mesma regra de cor, por posição
ISO_Q = {
    '10.3.1': ('laranja_vivo', [R(6.6, 31.6, 15.2, 40.6), R(6.6, 48.6, 15.2, 57.4)]),
    '10.3.2': ('roxo', [R(15.8, 25.4, 24.8, 34.6), R(16, 42.6, 24.8, 51.4)]),
    '10.3.3': ('lima', [R(25.2, 19.4, 33.8, 28.6), R(25.2, 36.4, 33.8, 45.4)]),
    '10.3.4': ('roxo', [R(10.2, 39.5, 11.4, 53), R(10.2, 56.6, 11.4, 70), R(29.8, 25.4, 38.4, 34.4), R(29.8, 42.6, 38.4, 51.4)]),
    '10.3.5': ('lima', [R(11.4, 37.4, 20.4, 46.4), R(11.4, 54.2, 20.4, 63.4)]),
    '10.3.6': ('laranja', [R(20.6, 31.4, 29.4, 40.4), R(20.6, 48.6, 29.4, 57.6)]),
    '10.3.7': ('laranja_vivo', [R(6.6, 65.6, 15.2, 75.8)]),
    '10.3.8': ('roxo', [R(15.8, 59.4, 24.8, 69.8)]),
    '10.3.9': ('lima', [R(25.2, 53.6, 34.6, 64.2)]),
}
for sub, (cor, regs) in ISO_Q.items():
    ALVOS.append(dict(sub=sub, page='fest-21', mode='color', cores=[cor], regions=regs, minArea=60, close=2, fill=20000))


# ---------------------------------------------------------------------------------------------
def poly_px(poly, W, H):
    return np.array([[p[0] * W / 100, p[1] * H / 100] for p in poly], np.int32)


def color_mask(hsv, cores):
    m = np.zeros(hsv.shape[:2], np.uint8)
    for c in cores:
        for h0, h1, s0, s1, v0, v1 in CORES[c]:
            m |= cv2.inRange(hsv, (h0, s0, v0), (h1, s1, v1))
    return m


def fill_small_holes(mask, maxArea):
    if not maxArea:
        return mask
    inv = cv2.bitwise_not(mask)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    H, W = mask.shape
    out = mask.copy()
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        touches = x == 0 or y == 0 or x + w >= W or y + h >= H
        if not touches and a <= maxArea:
            out[lab == i] = 255
    return out


def process(alvo, img, hsv):
    H, W = img.shape[:2]
    region = np.zeros((H, W), np.uint8)
    if alvo['mode'] == 'poly':
        groups = []
        for poly in alvo['polys']:
            pts = poly_px(poly, W, H)
            m = np.zeros((H, W), np.uint8)
            cv2.fillPoly(m, [pts], 255)
            groups.append(m)
        return groups
    for poly in alvo['regions']:
        cv2.fillPoly(region, [poly_px(poly, W, H)], 255)
    for poly in alvo.get('exclude', []):
        cv2.fillPoly(region, [poly_px(poly, W, H)], 0)
    if alvo['mode'] == 'color':
        sel = color_mask(hsv, alvo['cores'])
    elif alvo['mode'] == 'faces':  # áreas entre os traços pretos do desenho
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sel = ((g > 95) * 255).astype(np.uint8)
        m0 = cv2.bitwise_and(sel, region)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m0, connectivity=4)
        bx, by, bw, bh = cv2.boundingRect(region)
        sel = np.zeros_like(m0)
        for sx, sy in alvo['seeds']:
            v = lab[int(sy * H / 100), int(sx * W / 100)]
            x, y, w, h, _a = st[v] if v else (0, 0, 0, 0, 0)
            if v and x > bx and y > by and x + w < bx + bw and y + h < by + bh:  # face fechada pelos traços
                sel[lab == v] = 255
        if alvo.get('hull') and sel.any():
            pts = cv2.findNonZero(sel)
            sel = np.zeros_like(sel)
            cv2.fillPoly(sel, [cv2.convexHull(pts)], 255)
            return [sel]
    else:  # ink
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sel = (((g < 215) | ((hsv[..., 1] > 50) & (hsv[..., 2] < 250))) * 255).astype(np.uint8)
    m = cv2.bitwise_and(sel, region)
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    if alvo.get('open'):
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k(alvo['open']))
    if alvo.get('close'):
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k(alvo['close']))
        m = cv2.bitwise_and(m, cv2.dilate(region, k(1)))
    m = fill_small_holes(m, alvo.get('fill', 0))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    keep = np.zeros_like(m)
    seeds = [(int(s[0] * W / 100), int(s[1] * H / 100)) for s in alvo.get('seeds', [])]
    for i in range(1, n):
        if stats[i][4] < alvo.get('minArea', 30):
            continue
        if seeds and alvo['mode'] != 'faces' and not any(lab[y, x] == i for x, y in seeds):
            continue
        keep[lab == i] = 255
    if alvo.get('group', 'each') == 'all':
        return [keep] if keep.any() else []
    n, lab = cv2.connectedComponents(keep, connectivity=8)
    return [((lab == i) * 255).astype(np.uint8) for i in range(1, n)]


def mask_to_path(m):
    cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    parts = []
    for c in cs:
        if cv2.contourArea(c) < 6:
            continue
        a = cv2.approxPolyDP(c, 0.7, True).reshape(-1, 2)
        if len(a) < 3:
            continue
        parts.append('M' + 'L'.join(f'{x:g} {y:g}' for x, y in a) + 'Z')
    ys, xs = np.nonzero(m)
    box = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    return ''.join(parts), box


def main():
    conferir = '--conferir' in sys.argv
    pages = {}
    resultado = {}
    vazios = []
    for alvo in ALVOS:
        pg = alvo['page']
        if pg not in pages:
            img = cv2.imread(os.path.join(EDITAVEL, 'pranchas', pg + '.jpg'))
            pages[pg] = (img, cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
        img, hsv = pages[pg]
        groups = process(alvo, img, hsv)
        conf = alvo.get('conf', 'manual' if alvo['mode'] == 'poly' else 'traçado')
        sub = resultado.setdefault(alvo['sub'], {})
        ent = sub.setdefault(pg, {'conf': conf, 'note': alvo.get('note', ''), 'g': []})
        if conf == 'provisorio':
            ent['conf'] = 'provisorio'
        if alvo.get('note') and alvo['note'] not in ent['note']:
            ent['note'] = (ent['note'] + ' ' + alvo['note']).strip()
        for m in groups:
            d, box = mask_to_path(m)
            if d:
                ent['g'].append({'d': d, 'b': box})
        if not groups:
            vazios.append((alvo['sub'], pg))
        alvo['_masks'] = groups
    if vazios:
        print('ATENÇÃO, alvos sem pixels:', vazios)
    js = 'const SHAPES=' + json.dumps(resultado, ensure_ascii=False, separators=(',', ':')) + ';'
    html = open(HTML, encoding='utf-8').read()
    novo, n = re.subn(r'/\*CONTORNOS-INICIO\*/.*?/\*CONTORNOS-FIM\*/', lambda _: '/*CONTORNOS-INICIO*/' + js + '/*CONTORNOS-FIM*/', html, flags=re.S)
    if n != 1 and conferir:
        print('Aviso: marcadores não encontrados; nada gravado em index.html')
    elif n != 1:
        sys.exit('Marcadores /*CONTORNOS-INICIO*/ ... /*CONTORNOS-FIM*/ não encontrados em index.html')
    if n == 1:
        open(HTML, 'w', encoding='utf-8').write(novo)
    total = sum(len(e['g']) for s in resultado.values() for e in s.values())
    print(f'OK: {len(resultado)} subitens, {total} contornos gravados em index.html ({len(js) // 1024} KB)')
    if conferir:
        out = os.path.join(AQUI, 'conferencia')
        os.makedirs(out, exist_ok=True)
        por_pg = {}
        for alvo in ALVOS:
            por_pg.setdefault(alvo['page'], []).append(alvo)
        for pg, alvos in por_pg.items():
            base = pages[pg][0]
            tiles = []
            for alvo in alvos:
                ov = base.copy()
                tudo = np.zeros(base.shape[:2], np.uint8)
                for m in alvo['_masks']:
                    tudo |= m
                if not tudo.any():
                    continue
                cor = np.zeros_like(ov); cor[:] = (0, 90, 255)
                ov = np.where(tudo[..., None] > 0, (ov * .45 + cor * .55).astype(np.uint8), (ov * .55 + 255 * .45).astype(np.uint8))
                cs, _ = cv2.findContours(tudo, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
                cv2.drawContours(ov, cs, -1, (0, 0, 200), 1)
                ys, xs = np.nonzero(tudo)
                x0, y0, x1, y1 = max(0, xs.min() - 25), max(0, ys.min() - 25), min(base.shape[1], xs.max() + 25), min(base.shape[0], ys.max() + 25)
                crop = ov[y0:y1, x0:x1]
                s_ = 330 / max(crop.shape[:2])
                crop = cv2.resize(crop, None, fx=s_, fy=s_, interpolation=cv2.INTER_AREA if s_ < 1 else cv2.INTER_CUBIC)
                tile = np.full((360, 340, 3), 255, np.uint8)
                tile[22:22 + crop.shape[0], 5:5 + crop.shape[1]] = crop
                cv2.putText(tile, alvo['sub'] + ' ' + alvo.get('conf', ''), (5, 16), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 1, cv2.LINE_AA)
                tiles.append(tile)
            if not tiles:
                continue
            cols = 4
            while len(tiles) % cols:
                tiles.append(np.full((360, 340, 3), 255, np.uint8))
            rows = [np.hstack(tiles[k:k + cols]) for k in range(0, len(tiles), cols)]
            cv2.imwrite(os.path.join(out, pg + '.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 82])
        print('Conferência em', out)

if __name__ == '__main__':
    main()
