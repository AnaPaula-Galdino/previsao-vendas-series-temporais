"""
Previsão de Vendas — Séries Temporais (SARIMAX)
Decompõe a série, valida o modelo num holdout e projeta 12 meses à frente.
Autora: Ana Paula Galdino
"""
import os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(BASE, "imagens"); os.makedirs(IMG, exist_ok=True)
C = {"escuro":"#1f4e79","medio":"#2e6da4","claro":"#5b9bd5","suave":"#a6c8e0",
     "destaque":"#4fc3f7","cinza":"#d9d9d9","alerta":"#c0392b"}
FONTE = "Série mensal de vendas  ·  Modelagem: Ana Paula Galdino"
plt.rcParams.update({"font.size":11,"font.family":"DejaVu Sans","axes.edgecolor":"#9aa7b8",
    "axes.grid":True,"grid.color":"#eef2f7","axes.axisbelow":True,"figure.dpi":120,"savefig.bbox":"tight"})
def rodape(fig): fig.text(0.01,0.005,FONTE,fontsize=7.5,color="#7a8aa0")
def brl(x): return f"R$ {x/1000:.0f}k"

df = pd.read_csv(os.path.join(BASE,"dados","vendas_mensais.csv"), parse_dates=["mes"])
s = df.set_index("mes")["vendas"].asfreq("MS")

# Validação: treina nos primeiros 42, prevê os últimos 6
treino, teste = s.iloc[:-6], s.iloc[-6:]
mod = SARIMAX(treino, order=(1,1,1), seasonal_order=(1,1,1,12)).fit(disp=False)
pred = mod.get_forecast(6); pmean = pred.predicted_mean
mape = float((np.abs((teste.values - pmean.values)/teste.values)).mean()*100)

# Modelo final em toda a série e previsão 12 meses
final = SARIMAX(s, order=(1,1,1), seasonal_order=(1,1,1,12)).fit(disp=False)
fc = final.get_forecast(12); fmean = fc.predicted_mean; ci = fc.conf_int()

# 1) Série histórica
def g1():
    fig,ax=plt.subplots(figsize=(11,4.8))
    ax.plot(s.index, s.values, color=C["escuro"], lw=2, marker="o", ms=3)
    ax.fill_between(s.index, s.values, color=C["claro"], alpha=0.25)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:brl(x)))
    ax.set_title("Vendas mensais — histórico (2021–2025)",fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_ylabel("Vendas")
    rodape(fig); fig.savefig(os.path.join(IMG,"01_serie_historica.png")); plt.close(fig)

# 2) Decomposição
def g2():
    dec = seasonal_decompose(s, model="multiplicative", period=12)
    fig,axes=plt.subplots(4,1,figsize=(11,8),sharex=True)
    for ax,(serie,nome,cor) in zip(axes,[(dec.observed,"Observado",C["escuro"]),
            (dec.trend,"Tendência",C["medio"]),(dec.seasonal,"Sazonalidade",C["claro"]),
            (dec.resid,"Resíduo",C["cinza"])]):
        ax.plot(serie.index, serie.values, color=cor, lw=1.8); ax.set_ylabel(nome, fontsize=9)
        ax.grid(True)
    axes[0].set_title("Decomposição da série (tendência × sazonalidade × resíduo)",
                      fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    rodape(fig); fig.savefig(os.path.join(IMG,"02_decomposicao.png")); plt.close(fig)

# 3) Sazonalidade média por mês
def g3():
    saz = df.assign(m=df["mes"].dt.month).groupby("m")["vendas"].mean()
    nomes=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    fig,ax=plt.subplots(figsize=(10,4.8))
    cores=[C["alerta"] if v==saz.max() else C["medio"] for v in saz.values]
    ax.bar(nomes, saz.values, color=cores)
    ax.axhline(saz.mean(), color=C["escuro"], ls="--", lw=1, label="média anual")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:brl(x)))
    ax.set_title("Sazonalidade: venda média por mês do ano",fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_ylabel("Venda média"); ax.legend(frameon=True)
    rodape(fig); fig.savefig(os.path.join(IMG,"03_sazonalidade_mensal.png")); plt.close(fig)

# 4) Validação (holdout)
def g4():
    fig,ax=plt.subplots(figsize=(11,4.8))
    ax.plot(treino.index, treino.values, color=C["cinza"], lw=1.5, label="Treino")
    ax.plot(teste.index, teste.values, color=C["escuro"], lw=2.2, marker="o", ms=5, label="Real")
    ax.plot(pmean.index, pmean.values, color=C["alerta"], lw=2.2, ls="--", marker="s", ms=5, label="Previsto")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:brl(x)))
    ax.set_title(f"Validação do modelo — MAPE de {mape:.1f}% no holdout",
                 fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_ylabel("Vendas"); ax.legend(frameon=True)
    rodape(fig); fig.savefig(os.path.join(IMG,"04_validacao.png")); plt.close(fig)

# 5) Previsão 12 meses com intervalo
def g5():
    fig,ax=plt.subplots(figsize=(11,4.8))
    ax.plot(s.index, s.values, color=C["escuro"], lw=2, label="Histórico")
    ax.plot(fmean.index, fmean.values, color=C["alerta"], lw=2.2, ls="--", marker="o", ms=4, label="Previsão 12m")
    ax.fill_between(ci.index, ci.iloc[:,0], ci.iloc[:,1], color=C["destaque"], alpha=0.25, label="Intervalo de confiança")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:brl(x)))
    ax.set_title("Previsão de vendas para os próximos 12 meses",fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_ylabel("Vendas"); ax.legend(frameon=True, loc="upper left")
    rodape(fig); fig.savefig(os.path.join(IMG,"05_previsao_12m.png")); plt.close(fig)

# 6) Crescimento anual
def g6():
    anual = df.assign(ano=df["mes"].dt.year).groupby("ano")["vendas"].sum()
    fig,ax=plt.subplots(figsize=(9,4.8))
    ax.bar(anual.index.astype(str), anual.values, color=C["escuro"])
    for i,(a,v) in enumerate(anual.items()):
        if i>0:
            yoy=(v/anual.iloc[i-1]-1)*100
            ax.text(i, v, f"+{yoy:.0f}%", ha="center", va="bottom", fontsize=10, color=C["alerta"], fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:f"R$ {x/1e6:.1f}M"))
    ax.set_title("Faturamento anual e crescimento ano a ano",fontweight="bold",color=C["escuro"],fontsize=13,pad=10)
    ax.set_ylabel("Vendas no ano")
    rodape(fig); fig.savefig(os.path.join(IMG,"06_crescimento_anual.png")); plt.close(fig)

def resumo():
    anual = df.assign(ano=df["mes"].dt.year).groupby("ano")["vendas"].sum()
    prox12 = float(fmean.sum())
    cresc_prev = (prox12/anual.iloc[-1]-1)*100
    return {"mape":mape,"prox12":prox12,"cresc_prev":cresc_prev,
            "pico_mes":"novembro/dezembro","ultimo_ano":float(anual.iloc[-1])}

def main():
    for g in (g1,g2,g3,g4,g5,g6): g()
    print({k:(round(v,1) if isinstance(v,float) else v) for k,v in resumo().items()})
    print("Gráficos:", sorted(x for x in os.listdir(IMG) if x.startswith("0")))

if __name__=="__main__":
    main()
