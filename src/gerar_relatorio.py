import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from relatorio_exec import construir
import previsao_vendas as P

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "imagens")
def img(n): return os.path.join(IMG, n)
r = P.resumo()

config = {
 "eyebrow": "RELATÓRIO DE PREVISÃO DE DEMANDA",
 "titulo": "Previsão de Vendas",
 "subtitulo": "Modelo de séries temporais (SARIMAX) para projeção de receita e planejamento",
 "meta": "Ana Paula Galdino · Data Analytics (POSTECH/FIAP) · Junho de 2026",
 "fonte": "Série mensal de vendas  ·  Modelagem: Ana Paula Galdino",
 "sumario": [
   f"A partir de 5 anos de histórico mensal, construí um modelo de séries temporais que projeta a "
   f"receita dos próximos 12 meses. Na validação fora da amostra, o erro médio foi de apenas "
   f"<b>{r['mape']:.1f}%</b> (MAPE) — precisão suficiente para apoiar decisões de planejamento.",
   f"A previsão aponta cerca de <b>R$ {r['prox12']/1e6:.1f} milhões</b> nos próximos 12 meses, um "
   f"crescimento de <b>{r['cresc_prev']:.0f}%</b> sobre o último ano, com pico concentrado em "
   f"<b>{r['pico_mes']}</b>. Isso permite dimensionar estoque, equipe e caixa com antecedência.",
 ],
 "kpis": [
   (f"{r['mape']:.1f}%", "erro de previsão (MAPE)"),
   (f"R$ {r['prox12']/1e6:.1f} mi", "receita prevista (12m)"),
   (f"+{r['cresc_prev']:.0f}%", "crescimento projetado"),
   ("12 meses", "horizonte de projeção"),
 ],
 "secoes": [
   {"titulo": "1. Entendendo a série",
    "texto": [
      "Antes de prever, é preciso entender o comportamento. A série combina uma <b>tendência de alta</b> "
      "consistente com uma <b>sazonalidade forte</b>: o segundo semestre, e especialmente o fim do ano, "
      "concentra os maiores volumes.",
      "A decomposição separa esses três componentes (tendência, sazonalidade e resíduo), confirmando que "
      "o padrão sazonal é estável e, portanto, modelável com confiança.",
    ],
    "imagens": [(img("01_serie_historica.png"), "Histórico mensal de vendas"),
                (img("02_decomposicao.png"), "Tendência, sazonalidade e resíduo isolados")]},
   {"titulo": "2. O padrão sazonal",
    "texto": [
      "A venda média por mês do ano deixa o ciclo explícito: a virada para novembro e dezembro puxa o "
      "faturamento muito acima da média, enquanto o início do ano é o vale.",
      "Esse conhecimento, por si só, já orienta compras, campanhas e escala de equipe — independentemente "
      "do modelo preditivo.",
    ],
    "imagens": [(img("03_sazonalidade_mensal.png"), "Venda média por mês do ano"),
                (img("06_crescimento_anual.png"), "Faturamento anual e crescimento ano a ano")]},
   {"titulo": "3. Modelo e projeção",
    "texto": [
      f"O modelo SARIMAX foi validado num holdout dos últimos meses, atingindo MAPE de <b>{r['mape']:.1f}%</b> "
      "— ou seja, erra em média menos de 5% ao prever um mês que ele nunca viu.",
      "Com o modelo validado, a projeção de 12 meses vem acompanhada de um intervalo de confiança, que "
      "comunica o grau de incerteza e ajuda a planejar cenários otimista e conservador.",
    ],
    "imagens": [(img("04_validacao.png"), "Real vs. previsto no período de validação"),
                (img("05_previsao_12m.png"), "Projeção dos próximos 12 meses com intervalo de confiança")]},
 ],
 "conclusao_titulo": "Como usar na prática",
 "conclusoes": [
   "<b>Planejamento de estoque e compras:</b> antecipar o pico de fim de ano evita ruptura e excesso.",
   "<b>Dimensionamento de equipe e caixa:</b> a projeção mensal orienta contratações e fluxo de caixa.",
   "<b>Metas realistas:</b> a previsão com intervalo dá base para metas alcançáveis, não chutadas.",
   "<b>Próximo passo:</b> incorporar variáveis externas (campanhas, feriados, preço) para refinar o modelo.",
 ],
}

if __name__ == "__main__":
    construir(config, os.path.join(BASE, "Analise_Executiva_Previsao_Vendas.pdf"))
