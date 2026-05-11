
import streamlit as st
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import os
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mundial 2026 · Simulador",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PATHS ───────────────────────────────────────────────────────────────────
DATA_DIR   = Path(__file__).parent / "data"
TEAMS_FILE = DATA_DIR / "teams_elo.json"
GROUPS_FILE = DATA_DIR / "groups.json"
RESULTS_FILE = DATA_DIR / "results.json"
HISTORIC_FILE = DATA_DIR / "historico_campeon.csv"

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Fuentes */
  @import url('https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Satoshi', 'Inter', sans-serif;
  }

  /* Colores base */
  :root {
    --color-primary: #01696f;
    --color-bg: #f7f6f2;
    --color-surface: #f9f8f5;
    --color-text: #28251d;
    --color-text-muted: #7a7974;
    --color-border: #d4d1ca;
    --color-gold: #d19900;
    --color-success: #437a22;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #1c1b19 !important;
  }
  [data-testid="stSidebar"] * {
    color: #cdccca !important;
  }
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    color: #f9f8f5 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 1.2rem;
    margin-bottom: 0.3rem;
    opacity: 0.6;
  }

  /* KPI cards */
  .kpi-card {
    background: white;
    border: 1px solid #e8e6e0;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 1px 3px rgba(40,37,29,0.06);
    margin-bottom: 0.5rem;
  }
  .kpi-label {
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #7a7974;
    margin-bottom: 0.25rem;
  }
  .kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: #01696f;
    line-height: 1.1;
  }
  .kpi-sub {
    font-size: 0.78rem;
    color: #7a7974;
    margin-top: 0.2rem;
  }

  /* Tabla de grupos */
  .group-card {
    background: white;
    border: 1px solid #e8e6e0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(40,37,29,0.04);
  }
  .group-title {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #7a7974;
    margin-bottom: 0.6rem;
  }
  .team-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.35rem 0;
    border-bottom: 1px solid #f0ede8;
    font-size: 0.88rem;
  }
  .team-row:last-child { border-bottom: none; }
  .team-name { font-weight: 500; color: #28251d; }
  .team-elo  { font-size: 0.78rem; color: #7a7974; font-variant-numeric: tabular-nums; }
  .team-prob {
    font-size: 0.82rem;
    font-weight: 600;
    color: #01696f;
    min-width: 3.5rem;
    text-align: right;
  }

  /* Badges */
  .badge {
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
  }
  .badge-gold    { background: #fdf3d6; color: #8a5b00; }
  .badge-silver  { background: #f0efec; color: #5a5957; }
  .badge-bronze  { background: #fde8d5; color: #713417; }
  .badge-green   { background: #dff0d3; color: #2e5c10; }
  .badge-teal    { background: #d0e8ea; color: #01696f; }

  /* Tab styling */
  button[data-baseweb="tab"] {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
  }
  button[data-baseweb="tab"][aria-selected="true"] {
    color: #01696f !important;
    border-bottom-color: #01696f !important;
  }

  /* Metric override */
  [data-testid="stMetric"] label {
    font-size: 0.73rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #7a7974 !important;
  }
  [data-testid="stMetricValue"] {
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: #01696f !important;
  }

  /* Header banner */
  .app-header {
    background: linear-gradient(135deg, #01696f 0%, #0c4e54 60%, #0f3638 100%);
    border-radius: 14px;
    padding: 1.8rem 2rem 1.5rem;
    margin-bottom: 1.5rem;
    color: white;
    box-shadow: 0 4px 20px rgba(1,105,111,0.25);
  }
  .app-header h1 {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
    color: white !important;
  }
  .app-header p {
    font-size: 0.88rem;
    opacity: 0.75;
    margin: 0;
    color: white !important;
  }

  /* Progress bar */
  .prob-bar-bg {
    background: #e8f4f5;
    border-radius: 4px;
    height: 6px;
    margin-top: 4px;
    width: 100%;
  }
  .prob-bar-fill {
    background: #01696f;
    border-radius: 4px;
    height: 6px;
  }

  /* Simulación resultados */
  .sim-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    background: white;
    border: 1px solid #e8e6e0;
  }
  .sim-rank {
    font-size: 0.72rem;
    font-weight: 700;
    color: #bab9b4;
    width: 1.4rem;
    text-align: center;
  }
  .sim-flag { font-size: 1.3rem; }
  .sim-name { font-size: 0.88rem; font-weight: 500; flex: 1; }
  .sim-pct {
    font-size: 0.95rem;
    font-weight: 700;
    color: #01696f;
    min-width: 3.5rem;
    text-align: right;
    font-variant-numeric: tabular-nums;
  }

  /* Hide Streamlit branding */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─── CARGA DE DATOS ──────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_teams():
    with open(TEAMS_FILE) as f:
        return json.load(f)

@st.cache_data(ttl=60)
def load_groups():
    with open(GROUPS_FILE) as f:
        return json.load(f)

@st.cache_data(ttl=30)
def load_results():
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return {}

@st.cache_data(ttl=30)
def load_historic():
    if HISTORIC_FILE.exists():
        return pd.read_csv(HISTORIC_FILE, parse_dates=["fecha"])
    return pd.DataFrame(columns=["fecha", "equipo", "prob"])


teams  = load_teams()
groups = load_groups()


# ─── MOTOR DE SIMULACIÓN ─────────────────────────────────────────────────────
def elo_prob(elo_a, elo_b):
    """Probabilidad de victoria de A sobre B (sin empate)."""
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

def simulate_match(team_a, team_b, teams_data, results=None):
    """
    Devuelve (ganador, perdedor) o (None, None) si empate en KO.
    En fase de grupos: 3 resultados posibles (A gana, empate, B gana).
    En KO: solo A gana o B gana.
    """
    key = f"{team_a}_{team_b}"
    rev = f"{team_b}_{team_a}"

    if results and (key in results or rev in results):
        res = results.get(key) or results.get(rev)
        ga = res.get("goles_a", 0) if key in results else res.get("goles_b", 0)
        gb = res.get("goles_b", 0) if key in results else res.get("goles_a", 0)
        if ga > gb:   return team_a, team_b
        elif gb > ga: return team_b, team_a
        else:         return None, None  # empate en grupos
    else:
        ea = teams_data[team_a]["elo"]
        eb = teams_data[team_b]["elo"]
        pa = elo_prob(ea, eb)
        r  = np.random.random()
        if r < pa * 0.8:    return team_a, team_b
        elif r > 1 - pb*0.8 if (pb := 1 - pa) else False: return team_b, team_a
        else:
            tie_a = pa / (pa + (1 - pa))
            return (team_a, team_b) if np.random.random() < tie_a else (team_b, team_a) if np.random.random() > 0.5 else (None, None)

def simulate_match_v2(team_a, team_b, teams_data, results=None, knockout=False):
    """
    Simulación limpia:
      - Grupos: A gana (pA*0.75), empate (0.25), B gana (pB*0.75)  → suma = 1
      - KO:     A gana (pA), B gana (pB)
    """
    key = f"{team_a}_{team_b}"
    rev = f"{team_b}_{team_a}"

    if results and (key in results or rev in results):
        res = results.get(key) or results.get(rev)
        if key in results:
            ga, gb = res.get("goles_a", 0), res.get("goles_b", 0)
        else:
            ga, gb = res.get("goles_b", 0), res.get("goles_a", 0)
        if ga > gb:   return team_a, team_b
        elif gb > ga: return team_b, team_a
        else:         return "DRAW", "DRAW"

    ea = teams_data[team_a]["elo"]
    eb = teams_data[team_b]["elo"]
    pa = elo_prob(ea, eb)
    pb = 1 - pa

    if knockout:
        return (team_a, team_b) if np.random.random() < pa else (team_b, team_a)
    else:
        r = np.random.random()
        p_win_a = pa * 0.75
        p_draw  = 0.25
        if r < p_win_a:
            return team_a, team_b
        elif r < p_win_a + p_draw:
            return "DRAW", "DRAW"
        else:
            return team_b, team_a

def simulate_group(group_id, teams_data, groups_data, results=None):
    """Simula un grupo y devuelve los 2 clasificados."""
    group_teams   = groups_data[group_id]["teams"]
    group_matches = groups_data[group_id]["matches"]

    points = {t: 0 for t in group_teams}
    gf     = {t: 0 for t in group_teams}
    gc     = {t: 0 for t in group_teams}

    for match in group_matches:
        t_a, t_b = match[0], match[1]
        winner, loser = simulate_match_v2(t_a, t_b, teams_data, results, knockout=False)
        if winner == "DRAW":
            points[t_a] += 1
            points[t_b] += 1
            g = int(np.random.normal(1.2, 0.8))
            g = max(0, g)
            gf[t_a] += g; gc[t_a] += g
            gf[t_b] += g; gc[t_b] += g
        else:
            points[winner] += 3
            g_w = max(1, int(np.random.normal(2.0, 0.9)))
            g_l = max(0, int(np.random.normal(0.9, 0.7)))
            gf[winner] += g_w; gc[winner] += g_l
            gf[loser]  += g_l; gc[loser]  += g_w

    # Ordenar: puntos → diferencia de goles → goles a favor
    sorted_teams = sorted(group_teams,
        key=lambda t: (points[t], gf[t]-gc[t], gf[t]),
        reverse=True)
    return sorted_teams[:2]

def simulate_tournament(teams_data, groups_data, results=None, n_sims=50_000):
    """
    Simula el torneo n_sims veces.
    Devuelve dict: {code: {"winner": int, "final": int, ...}}
    """
    all_codes  = list(teams_data.keys())
    n_groups   = len(groups_data)

    counts = {c: {"winner": 0, "final": 0, "semi": 0, "quarter": 0, "r16": 0} for c in all_codes}

    for _ in range(n_sims):
        # Fase de grupos: clasificar 2 por grupo
        qualified = {}
        for gid in groups_data:
            top2 = simulate_group(gid, teams_data, groups_data, results)
            qualified[gid] = top2  # [1ro, 2do]

        # R16: bracket clásico (los 12 grupos del WC2026)
        # Simplificación: emparejar grupos secuencialmente 1ro vs 2do de otro
        group_ids  = list(groups_data.keys())  # A..L
        r16_teams  = []
        for i in range(0, len(group_ids), 2):
            g1, g2 = group_ids[i], group_ids[i+1]
            r16_teams.append((qualified[g1][0], qualified[g2][1]))  # 1ro G1 vs 2do G2
            r16_teams.append((qualified[g2][0], qualified[g1][1]))  # 1ro G2 vs 2do G1

        # KO rounds
        def play_ko_round(pairs, res=None):
            winners = []
            for t_a, t_b in pairs:
                w, _ = simulate_match_v2(t_a, t_b, teams_data, res, knockout=True)
                winners.append(w)
            return winners

        r16_winners = play_ko_round(r16_teams, results)
        for t in r16_winners: counts[t]["r16"] += 1

        qf_pairs = [(r16_winners[i], r16_winners[i+1]) for i in range(0, len(r16_winners), 2)]
        qf_winners = play_ko_round(qf_pairs, results)
        for t in qf_winners: counts[t]["quarter"] += 1

        sf_pairs = [(qf_winners[i], qf_winners[i+1]) for i in range(0, len(qf_winners), 2)]
        sf_winners = play_ko_round(sf_pairs, results)
        for t in sf_winners: counts[t]["semi"] += 1

        final_winner, _ = simulate_match_v2(sf_winners[0], sf_winners[1], teams_data, results, knockout=True)
        counts[final_winner]["winner"] += 1
        for t in sf_winners: counts[t]["final"] += 1

    # Normalizar
    probs = {}
    for c in all_codes:
        probs[c] = {k: counts[c][k] / n_sims * 100 for k in counts[c]}
    return probs


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚽ Mundial 2026")
    st.markdown("---")

    st.markdown("### 🎛️ Simulación")
    n_sims = st.select_slider(
        "Iteraciones",
        options=[10_000, 25_000, 50_000, 100_000],
        value=50_000,
        help="Más iteraciones = más precisión, más tiempo"
    )

    run_sim = st.button("▶ Simular ahora", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("### 📁 Datos")
    if RESULTS_FILE.exists():
        results = load_results()
        n_played = len(results)
        st.success(f"✓ {n_played} partidos jugados")
    else:
        results = {}
        st.info("Sin resultados aún")

    if HISTORIC_FILE.exists():
        hist_df = load_historic()
        st.info(f"📈 {len(hist_df)} entradas históricas")
    else:
        hist_df = pd.DataFrame(columns=["fecha","equipo","prob"])

    st.markdown("---")
    st.markdown("### ℹ️ Info")
    st.caption("Simulación Monte Carlo con ratings Elo.
Actualiza los resultados y recalcula desde tu PC.")
    st.caption(f"v1.0 · Mayo 2026")


# ─── SIMULACIÓN PRINCIPAL ─────────────────────────────────────────────────────
if run_sim or "sim_probs" not in st.session_state:
    with st.spinner(f"Simulando {n_sims:,} torneos..."):
        probs = simulate_tournament(teams, groups, results, n_sims)
        st.session_state["sim_probs"]  = probs
        st.session_state["sim_nsims"] = n_sims
        st.session_state["sim_time"]  = datetime.now().strftime("%H:%M:%S")

probs = st.session_state.get("sim_probs", {})
sim_nsims = st.session_state.get("sim_nsims", n_sims)
sim_time  = st.session_state.get("sim_time", "--:--:--")


# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <h1>⚽ Mundial 2026 · Simulador de Probabilidades</h1>
  <p>Simulación Monte Carlo · {sim_nsims:,} iteraciones · Última sim: {sim_time}</p>
</div>
""", unsafe_allow_html=True)


# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Probabilidades", 
    "📊 Por Grupos", 
    "📈 Evolución Histórica",
    "⚽ Partidos"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PROBABILIDADES GLOBALES
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # Top 3 KPI cards
    if probs:
        sorted_probs = sorted(probs.items(), key=lambda x: x[1]["winner"], reverse=True)
        top3 = sorted_probs[:3]

        k1, k2, k3 = st.columns(3)
        labels = [
            ("🥇 Favorito", "badge-gold"),
            ("🥈 2º Favorito", "badge-silver"),
            ("🥉 3er Favorito", "badge-bronze"),
        ]
        for col, (code, data), (label, badge) in zip([k1,k2,k3], top3, labels):
            team = teams[code]
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                  <div class="kpi-label">{label}</div>
                  <div class="kpi-value">{team['flag']} {team['name_es']}</div>
                  <div style="margin-top:0.4rem">
                    <span class="badge {badge}">{data['winner']:.1f}% campeón</span>
                  </div>
                  <div class="kpi-sub">Elo: {team['elo']:,} · Final: {data['final']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Tabla completa de probabilidades
    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        st.markdown("#### Top 20 — Probabilidad de ganar el Mundial")

        top20 = sorted_probs[:20]
        codes = [c for c,_ in top20]
        labels_chart = [f"{teams[c]['flag']} {teams[c]['name_es']}" for c in codes]
        values = [probs[c]["winner"] for c in codes]

        colors = ["#01696f" if i == 0 else "#4f98a3" if i < 3 else "#cedcd8" for i in range(20)]

        fig = go.Figure(go.Bar(
            x=values[::-1],
            y=labels_chart[::-1],
            orientation="h",
            marker_color=colors[::-1],
            text=[f"{v:.1f}%" for v in values[::-1]],
            textposition="outside",
            textfont=dict(size=11, color="#28251d"),
            cliponaxis=False,
        ))
        fig.update_layout(
            height=520,
            margin=dict(l=0, r=60, t=10, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=12, color="#28251d")),
            showlegend=False,
            font=dict(family="Satoshi, Inter, sans-serif"),
        )
        fig.update_xaxes(range=[0, max(values) * 1.25])
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.markdown("#### Tabla completa")
        rows = []
        for i, (code, data) in enumerate(sorted_probs, 1):
            team = teams[code]
            rows.append({
                "#":      i,
                "Equipo": f"{team['flag']} {team['name_es']}",
                "🏆 Camp.": f"{data['winner']:.1f}%",
                "🥈 Final": f"{data['final']:.1f}%",
                "4º SF":  f"{data['semi']:.1f}%",
                "8º QF":  f"{data['quarter']:.1f}%",
            })
        df_table = pd.DataFrame(rows)
        st.dataframe(
            df_table,
            hide_index=True,
            use_container_width=True,
            height=500,
            column_config={
                "#":       st.column_config.NumberColumn(width="small"),
                "Equipo":  st.column_config.TextColumn(width="medium"),
                "🏆 Camp.": st.column_config.TextColumn(width="small"),
                "🥈 Final": st.column_config.TextColumn(width="small"),
                "4º SF":   st.column_config.TextColumn(width="small"),
                "8º QF":   st.column_config.TextColumn(width="small"),
            }
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — POR GRUPOS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Probabilidades de clasificación por grupo")
    st.caption("% de veces que cada equipo clasifica 1º o 2º en su grupo en las simulaciones.")

    group_ids = list(groups.keys())
    n_cols = 3
    rows_of_groups = [group_ids[i:i+n_cols] for i in range(0, len(group_ids), n_cols)]

    for row in rows_of_groups:
        cols = st.columns(len(row))
        for col, gid in zip(cols, row):
            with col:
                group_teams = groups[gid]["teams"]
                # Ordenar por elo
                ordered = sorted(group_teams, key=lambda c: teams[c]["elo"], reverse=True)

                html_rows = ""
                for code in ordered:
                    team = teams[code]
                    win_p = probs.get(code, {}).get("winner", 0)
                    elo   = team["elo"]
                    bar_w = min(100, win_p * 10)
                    html_rows += f"""
                    <div class="team-row">
                      <span class="team-name">{team['flag']} {team['name_es']}</span>
                      <span class="team-elo">{elo}</span>
                      <span class="team-prob">{win_p:.1f}%</span>
                    </div>
                    """

                st.markdown(f"""
                <div class="group-card">
                  <div class="group-title">Grupo {gid}</div>
                  {html_rows}
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EVOLUCIÓN HISTÓRICA
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### Evolución de % campeón a lo largo del torneo")

    if hist_df.empty:
        st.info("""
        📭 **Sin datos históricos todavía.**

        El histórico se construye día a día:
        1. Introduces los resultados del día en tu PC local
        2. Ejecutas `python update_results.py`
        3. El script añade una fila a `data/historico_campeon.csv`
        4. Haces `git push` → la gráfica aparece aquí

        **Mientras tanto, la pestaña "🏆 Probabilidades" muestra las probabilidades actuales.**
        """)

        # Gráfica demo
        st.markdown("##### Vista previa (datos de ejemplo)")
        demo_teams = ["BRA", "ARG", "FRA", "ESP", "ENG"]
        demo_dates = pd.date_range("2026-06-11", periods=7, freq="D")
        demo_data = []
        rng = np.random.default_rng(42)
        for team in demo_teams:
            base = probs.get(team, {}).get("winner", 5)
            vals = [base]
            for _ in range(6):
                vals.append(max(0.5, vals[-1] + rng.normal(0, 2)))
            for i, (date, val) in enumerate(zip(demo_dates, vals)):
                demo_data.append({"fecha": date, "equipo": team, "prob": val})
        demo_df = pd.DataFrame(demo_data)

    else:
        demo_df = None
        st.success(f"✓ Datos históricos cargados: {hist_df['fecha'].nunique()} fechas, "
                   f"{hist_df['equipo'].nunique()} equipos")

    plot_df = demo_df if demo_df is not None else hist_df

    # Selector de equipos a mostrar
    all_team_codes = plot_df["equipo"].unique().tolist()
    default_show = all_team_codes[:8]

    selected = st.multiselect(
        "Equipos a mostrar",
        options=all_team_codes,
        default=default_show,
        format_func=lambda c: f"{teams.get(c, {}).get('flag', '')} {teams.get(c, {}).get('name_es', c)}"
    )

    if selected:
        filtered = plot_df[plot_df["equipo"].isin(selected)]

        PALETTE = [
            "#01696f","#d19900","#a12c7b","#006494",
            "#437a22","#da7101","#7a39bb","#a13544",
        ]

        fig2 = go.Figure()
        for i, code in enumerate(selected):
            d = filtered[filtered["equipo"] == code].sort_values("fecha")
            team_info = teams.get(code, {})
            fig2.add_trace(go.Scatter(
                x=d["fecha"],
                y=d["prob"],
                mode="lines+markers",
                name=f"{team_info.get('flag','')} {team_info.get('name_es', code)}",
                line=dict(color=PALETTE[i % len(PALETTE)], width=2.5),
                marker=dict(size=7, color=PALETTE[i % len(PALETTE)]),
                hovertemplate="%{y:.1f}%<extra></extra>",
            ))

        fig2.update_layout(
            height=420,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=0, r=10, t=10, b=10),
            xaxis=dict(
                title="Fecha",
                showgrid=True,
                gridcolor="#f0ede8",
                tickfont=dict(size=11),
            ),
            yaxis=dict(
                title="% Probabilidad campeón",
                showgrid=True,
                gridcolor="#f0ede8",
                ticksuffix="%",
                tickfont=dict(size=11),
            ),
            legend=dict(
                orientation="v",
                font=dict(size=11),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#e8e6e0",
                borderwidth=1,
            ),
            font=dict(family="Satoshi, Inter, sans-serif"),
            hovermode="x unified",
        )
        st.plotly_chart(fig2, use_container_width=True)

        if demo_df is not None:
            st.caption("⚠️ Esta gráfica usa datos de ejemplo. Los datos reales aparecerán aquí tras el primer `git push`.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PARTIDOS JUGADOS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### Partidos registrados")

    if not results:
        st.info("""
        📭 **Sin partidos registrados.**

        Los resultados se actualizan desde tu PC local con `python update_results.py`.
        Una vez hagas `git push`, aparecerán aquí.
        """)
    else:
        # Mostrar resultados registrados
        rows_res = []
        for key, res in results.items():
            codes = key.split("_")
            if len(codes) == 2:
                ca, cb = codes
                ta = teams.get(ca, {})
                tb = teams.get(cb, {})
                ga = res.get("goles_a", "?")
                gb = res.get("goles_b", "?")
                rows_res.append({
                    "Local":    f"{ta.get('flag','')} {ta.get('name_es', ca)}",
                    "Goles":    f"{ga} - {gb}",
                    "Visitante": f"{tb.get('flag','')} {tb.get('name_es', cb)}",
                    "Fase":     res.get("fase", "Grupos"),
                    "Fecha":    res.get("fecha", ""),
                })
        if rows_res:
            df_res = pd.DataFrame(rows_res)
            st.dataframe(df_res, hide_index=True, use_container_width=True, height=400)
            st.caption(f"Total: {len(rows_res)} partido(s) registrado(s)")

    st.markdown("---")
    st.markdown("##### Formato de `data/results.json`")
    st.code("""
{
  "BRA_ARG": {
    "goles_a": 2,
    "goles_b": 1,
    "fase": "Grupos",
    "fecha": "2026-06-14"
  },
  "FRA_ESP": {
    "goles_a": 0,
    "goles_b": 2,
    "fase": "Cuartos",
    "fecha": "2026-07-04"
  }
}
    """, language="json")
    st.caption("El código de equipo siempre es el local (A) primero. Ver `teams_elo.json` para todos los códigos.")
