"""
Build the interactive prod-prod weighted similarity heatmap (online appendix
counterpart to Figure 3 / fig:heatmap_product_similarities in the paper).

Reads:
  - Exports/03-2026/03 - Product similarities/03.02 - Prod-prod similarities/
    RiO prod-prod similarity matrix WEIGHTED.csv
  - Data/Varenr labels/product_codes_4digit_summary.csv

Writes (into the kristianskovisen.github.io repo):
  - online-appendix/product-similarity.html   (full standalone page)
  - online-appendix/data/prod_prod_similarity_weighted_matrix.csv (labeled square matrix)
  - online-appendix/data/prod_prod_similarity_weighted_pairs.csv  (tidy pairwise, i<j)
"""
import pandas as pd
import plotly.graph_objects as go
import json

PROJECT = "/Users/au563401/Library/CloudStorage/OneDrive-Aarhusuniversitet/Dokumenter/Projects/CH1 Relatedness in Occupations"
SITE = "/Users/au563401/Documents/GitHub/kristianskovisen"

MATRIX_CSV = f"{PROJECT}/Exports/03-2026/03 - Product similarities/03.02 - Prod-prod similarities/RiO prod-prod similarity matrix WEIGHTED.csv"
LABELS_CSV = f"{PROJECT}/Data/Varenr labels/product_codes_4digit_summary.csv"

OUT_HTML = f"{SITE}/online-appendix/product-similarity.html"
OUT_DATA_DIR = f"{SITE}/online-appendix/data"
OUT_MATRIX_CSV = f"{OUT_DATA_DIR}/prod_prod_similarity_weighted_matrix.csv"
OUT_PAIRS_CSV = f"{OUT_DATA_DIR}/prod_prod_similarity_weighted_pairs.csv"

# ---------------------------------------------------------------- load data
mat = pd.read_csv(MATRIX_CSV)
codes = [c.replace("hs_", "") for c in mat.columns]
mat.columns = codes
mat.index = codes

labels = pd.read_csv(LABELS_CSV, dtype={"code4": str})
labels["code4"] = labels["code4"].str.zfill(4)
name_lookup = dict(zip(labels["code4"], labels["summary"]))

names = [name_lookup.get(c, "No description available") for c in codes]
axis_labels = [f"{c}" for c in codes]

# ---------------------------------------------------------------- hover text
z = mat.values.round(4)
n = len(codes)
hover = [
    [
        f"{codes[i]}: {names[i]}<br>{codes[j]}: {names[j]}<br>"
        f"Weighted similarity Φ: {z[i, j]:.3f}"
        for j in range(n)
    ]
    for i in range(n)
]

# ---------------------------------------------------------------- figure
fig = go.Figure(
    data=go.Heatmap(
        z=z,
        x=axis_labels,
        y=axis_labels,
        text=hover,
        hoverinfo="text",
        colorscale="Viridis",
        zmin=0,
        zmax=1,
        colorbar=dict(
            title=dict(text="Weighted<br>similarity Φ", font=dict(family="IBM Plex Mono, monospace", size=11)),
            tickfont=dict(family="IBM Plex Mono, monospace", size=10),
            thickness=14,
        ),
        xgap=0.3,
        ygap=0.3,
    )
)

fig.update_layout(
    xaxis=dict(
        tickfont=dict(family="IBM Plex Mono, monospace", size=8),
        tickangle=90,
        showgrid=False,
        constrain="domain",
    ),
    yaxis=dict(
        tickfont=dict(family="IBM Plex Mono, monospace", size=8),
        showgrid=False,
        autorange="reversed",
        scaleanchor="x",
        scaleratio=1,
    ),
    margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="white",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Newsreader, Georgia, serif", color="#17222c"),
    height=780,
)

plot_html = fig.to_html(
    full_html=False,
    include_plotlyjs="cdn",
    config={"responsive": True, "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
    div_id="prodprod-heatmap",
)

# ---------------------------------------------------------------- data exports
import os
os.makedirs(OUT_DATA_DIR, exist_ok=True)

labeled_matrix = mat.copy()
labeled_matrix.index.name = "hs4"
labeled_matrix.to_csv(OUT_MATRIX_CSV)

pairs = []
for i in range(n):
    for j in range(i + 1, n):
        pairs.append((codes[i], names[i], codes[j], names[j], z[i, j]))
pairs_df = pd.DataFrame(pairs, columns=["product_i", "name_i", "product_j", "name_j", "weighted_similarity"])
pairs_df.sort_values("weighted_similarity", ascending=False, inplace=True)
pairs_df.to_csv(OUT_PAIRS_CSV, index=False)

print("n products:", n)
print("matrix csv ->", OUT_MATRIX_CSV)
print("pairs csv ->", OUT_PAIRS_CSV, "rows:", len(pairs_df))

# ---------------------------------------------------------------- page template
page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Online Appendix &middot; Product-Product Similarity &mdash; Kristian Skov Isen</title>
  <meta name="description" content="Interactive version of Figure 3: bilateral task-based similarity between products, weighted by occupational skill transferability." />
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230c3d63'/%3E%3Ctext x='16' y='22' font-family='Georgia,serif' font-size='16' fill='white' text-anchor='middle'%3EKI%3C/text%3E%3C/svg%3E" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400..600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet" />

  <link rel="stylesheet" href="../style.css" />
  <style>
    .wrap--wide {{ max-width: 1080px; }}
    .backlink {{
      font-family: var(--mono); font-size: 0.76rem; color: var(--muted);
      display: inline-block; margin-bottom: 1.6rem;
    }}
    .backlink:hover {{ color: var(--accent); }}
    .appendix-title {{
      font-family: var(--display); font-optical-sizing: auto; font-weight: 540;
      font-size: clamp(1.7rem, 4.5vw, 2.4rem); line-height: 1.1; letter-spacing: -0.015em;
      margin: 0 0 0.9rem;
    }}
    .appendix-note {{
      color: var(--ink-2); margin: 0 0 1.6rem;
    }}
    .plot-card {{
      background: var(--card); border: 1px solid var(--line); border-radius: 10px;
      padding: clamp(0.6rem, 2vw, 1.2rem); margin-bottom: 1.6rem; overflow-x: auto;
    }}
    .plot-card > div {{ min-width: 640px; }}
    .legend-note {{
      font-family: var(--mono); font-size: 0.72rem; color: var(--muted);
      margin: 0 0 2rem;
    }}
  </style>
</head>
<body>
  <main class="wrap wrap--wide">
    <a class="backlink" href="../index.html">&larr; Back to kristianskovisen.github.io</a>

    <p class="eyebrow">Online appendix &middot; Product Relatedness in Tasks</p>
    <h1 class="appendix-title">Product-product similarity in occupations</h1>
    <p class="appendix-note">
      Interactive counterpart to Figure 3 of the paper. Each cell is the weighted
      cosine similarity &Phi;(&omega;, &omega;&prime;) between two HS4 products'
      occupational task vectors, extended with a skill-transferability weighting
      matrix estimated from excess worker flows between occupations. Values closer
      to 1 (bright yellow) indicate products whose production draws on very similar
      occupations; values closer to 0 (dark blue/purple) indicate little occupational
      overlap. The diagonal equals 1 by construction. Only products satisfying GDPR
      thresholds (more than five single-product firms observed, 2010&ndash;2019) are
      included. Hover over any tile to see the two HS4 product codes, their names,
      and the weighted similarity value.
    </p>

    <div class="plot-card">
      {plot_html}
    </div>
    <p class="legend-note">{n} products &middot; {n * (n - 1) // 2:,} unique pairs &middot; colorscale: viridis</p>

    <section class="section" id="download" aria-labelledby="download-title">
      <h2 class="section-title" id="download-title">Download the data</h2>
      <p class="appendix-note">
        The full weighted similarity matrix and a tidy pairwise version (sorted by
        similarity, one row per unique product pair) are available below.
      </p>
      <div class="actions">
        <a class="btn btn--primary" href="data/prod_prod_similarity_weighted_pairs.csv" download>
          <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12m0 0-4-4m4 4 4-4"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>
          Pairwise similarities (CSV)
        </a>
        <a class="btn" href="data/prod_prod_similarity_weighted_matrix.csv" download>
          <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12m0 0-4-4m4 4 4-4"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/></svg>
          Full similarity matrix (CSV)
        </a>
      </div>
    </section>

    <footer class="foot">
      <span>&copy; 2026 Kristian Skov Isen</span>
      <span>Aarhus, Denmark</span>
    </footer>
  </main>
</body>
</html>
"""

with open(OUT_HTML, "w") as f:
    f.write(page)

print("page ->", OUT_HTML)
