import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.lines import Line2D

# -----------------------------
# K-medians (L1 / Taxicab) clustering
# -----------------------------
def k_medians_l1(X: np.ndarray, k: int, max_iter: int = 100, tol: float = 1e-6, random_state: int = 42):
    """
    K-medians clustering under the taxicab (L1/Manhattan) metric.

    - Assignment: nearest centroid by L1 distance
    - Update: centroid is coordinate-wise median (not mean!)
    """
    rng = np.random.default_rng(random_state)

    # Initialize centroids by sampling k points
    centroids = X[rng.choice(X.shape[0], size=k, replace=False)]

    for _ in range(max_iter):
        # Assign each point to closest centroid (L1)
        dists = np.sum(np.abs(X[:, None, :] - centroids[None, :, :]), axis=2)  # (n, k)
        labels = np.argmin(dists, axis=1)

        # Update centroids with coordinate-wise medians
        new_centroids = centroids.copy()
        for j in range(k):
            members = X[labels == j]
            if members.shape[0] == 0:
                # Empty cluster: re-seed to a random point
                new_centroids[j] = X[rng.integers(0, X.shape[0])]
            else:
                new_centroids[j] = np.median(members, axis=0)

        # Convergence check (L1 shift)
        shift = np.sum(np.abs(new_centroids - centroids))
        centroids = new_centroids
        if shift < tol:
            break

    return labels, centroids


# -----------------------------
# 1. Load Excel file
# -----------------------------
# Hint : Change the name of the Excel Work book and Output File to get results in a different league - Solomon Mcharo, Constance Develle, Brittany Quan, Jiaqi Paige, Claudia Sinclair and Madeline Young.
file_path = "SerieABook.xlsx"
df = pd.read_excel(file_path)
OUTPUT_FILE = "SerieABook_with_clusters2.xlsx"

# -----------------------------
# 2. Select required columns
# -----------------------------
cols = ["age", "weight_kg", "mcharo_develle_ln_price", "short_name"]
df = df[cols].dropna().reset_index(drop=True)

df_sub = (
    df[cols]
    .dropna()
    .reset_index(drop=False)   # keep original index!
)

# -----------------------------
# 3. Run L1 clustering (clusters decide color)
# -----------------------------
k = 4  # change this if you want more/fewer clusters

X_raw = df[["age", "weight_kg", "mcharo_develle_ln_price"]].to_numpy(dtype=float)

# Normalize so age/weight/price are comparable
mu = X_raw.mean(axis=0)
sigma = X_raw.std(axis=0)
sigma[sigma == 0] = 1.0
X = (X_raw - mu) / sigma

clusters, centroids = k_medians_l1(X, k=k)

# -----------------------------
# 4. Attach clusters back to df + save
# -----------------------------
df_sub["cluster"] = clusters

df["cluster"] = np.nan
df.loc[df_sub["index"], "cluster"] = df_sub["cluster"].values
df.to_excel(OUTPUT_FILE, index=False)

# Cluster series used for plotting
df_cluster = df["cluster"].dropna().astype(int)
counts = df_cluster.value_counts().sort_index()

# -----------------------------
# 5. Build a shared cluster->color map (SAME for pie + scatter)
# -----------------------------
cmap = plt.cm.tab10
cluster_ids = sorted(df_cluster.unique())
cluster_color_map = {cid: cmap(cid) for cid in cluster_ids}

# -----------------------------
# 6. Pie chart (uses shared colors)
# -----------------------------
fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
pie_colors = [cluster_color_map[c] for c in counts.index]

ax_pie.pie(
    counts.values,
    labels=[f"Cluster {i}" for i in counts.index],
    autopct="%1.1f%%",
    startangle=90,
    colors=pie_colors,
    wedgeprops={"edgecolor": "black"},
)
ax_pie.set_title("Saudi Pro League Cluster Distribution (K-medians L1)")
ax_pie.axis("equal")

fig_pie.tight_layout()
fig_pie.savefig("SaudiProLeague_cluster_distribution_pie.png", dpi=200)

# Show pie without blocking, then close so it doesn't interfere
plt.show(block=False)
plt.close(fig_pie)

# -----------------------------
# 7. 3D scatter (uses same shared colors)
# -----------------------------
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection="3d")

# IMPORTANT: use per-point colors from the same mapping
point_colors = [cluster_color_map[c] for c in df_cluster.to_numpy()]

sc = ax.scatter(
    df.loc[df_cluster.index, "age"],
    df.loc[df_cluster.index, "weight_kg"],
    df.loc[df_cluster.index, "mcharo_develle_ln_price"],
    c=point_colors,
    alpha=0.65,
    s=35,
)

# Labels are short_name
for idx in df_cluster.index:
    row = df.loc[idx]
    ax.text(
        row["age"],
        row["weight_kg"],
        row["mcharo_develle_ln_price"],
        str(row["short_name"]),
        fontsize=7,
    )

ax.set_xlabel("Age")
ax.set_ylabel("Weight (kg)")
ax.set_zlabel("Mcharo-Develle ln(Price)")
ax.set_title(" Serie A (Calcio) K-medians (Taxicab/L1) Clusters: Age vs Weight vs Mcharo-Develle ln(Price)")

# Add a legend with the same cluster colors (more reliable than colorbar here)
legend_elements = [
    Line2D(
        [0], [0],
        marker="o",
        color="w",
        label=f"Cluster {cid}",
        markerfacecolor=cluster_color_map[cid],
        markersize=8,
    )
    for cid in cluster_ids
]
ax.legend(handles=legend_elements, title="Clusters", loc="upper left")

fig.tight_layout()
fig.savefig("primerarecard_develle.png", dpi=200)
plt.show()
