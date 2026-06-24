"""
Gera uma série mensal de vendas (48 meses) com tendência, sazonalidade e ruído,
para o estudo de previsão. Autora: Ana Paula Galdino
"""
import os
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(23)
meses = pd.date_range("2021-01-01", periods=60, freq="MS")
t = np.arange(len(meses))
tendencia = 100000 + 1900 * t
fator_mes = {1:0.85,2:0.82,3:0.95,4:1.00,5:1.05,6:0.98,7:1.00,8:1.03,9:1.06,10:1.12,11:1.27,12:1.38}
saz = np.array([fator_mes[m.month] for m in meses])
ruido = 1 + rng.normal(0, 0.035, len(meses))
vendas = (tendencia * saz * ruido).round(0)
df = pd.DataFrame({"mes": meses.strftime("%Y-%m-01"), "vendas": vendas.astype(int)})
out = os.path.join(BASE, "dados", "vendas_mensais.csv")
df.to_csv(out, index=False)
print(f"Série gerada: {len(df)} meses -> {out}")
print(f"Vendas médias: R$ {df['vendas'].mean():,.0f}")
