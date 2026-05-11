# ⚽ Mundial 2026 · Simulador de Probabilidades

Simulador Monte Carlo del Mundial 2026 para Streamlit Community Cloud.

## Estructura

```
wc2026/
├── app.py                      ← App principal Streamlit
├── requirements.txt            ← Dependencias para Streamlit Cloud
├── data/
│   ├── teams_elo.json          ← Equipos con ratings Elo
│   ├── groups.json             ← Grupos del torneo
│   ├── results.json            ← Resultados (se actualiza manualmente)
│   └── historico_campeon.csv   ← Histórico diario de % campeón
└── assets/
```

## Flujo diario durante el torneo

```bash
# 1. Introduce los resultados del día
python update_results.py

# 2. Recalcula simulaciones y añade al histórico
python simulator.py

# 3. Sube a GitHub → Streamlit Cloud se actualiza automáticamente
git add data/
git commit -m "Resultados jornada $(date +%Y-%m-%d)"
git push
```

## Deploy en Streamlit Community Cloud

1. Sube este repositorio a GitHub
2. Ve a https://share.streamlit.io
3. Conecta el repositorio
4. Entry point: `wc2026/app.py`
5. ¡Deploy!
