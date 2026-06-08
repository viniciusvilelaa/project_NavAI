# project_NavAI
Agente de AI para jogar contra jogadores na batalha naval


Definição dos Navios e Regras:

A frota padrão do Batalha Naval geralmente consiste em:
1 Porta-aviões (tamanho 5)
1 Encouraçado (tamanho 4)
1 Cruzador (tamanho 3)
1 Submarino (tamanho 3)
1 Destróier (tamanho 2)

O grid NumPy usará números inteiros para representar os estados:
0: Água/Vazio
1 a 5: Identificadores dos navios (para diferenciar cada navio posicionado)
-1: Tiro na água (Miss)
-2: Navio atingido (Hit)