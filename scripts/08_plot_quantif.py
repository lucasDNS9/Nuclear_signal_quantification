# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 22:16:33 2026

@author: lucasdenis
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tkinter as tk

from tkinter import filedialog, messagebox
from pathlib import Path


# ============================================================
# PARAMÈTRES
# ============================================================

# Nom du marqueur à analyser
MARKER = "PAX3"


# Ordre souhaité des clones
CLONE_ORDER = [
    "WTC11",
    "ISO1",
    "ISO2"
]


# ============================================================
# 1. Sélection du fichier CSV
# ============================================================

root = tk.Tk()
root.withdraw()  # Cache la fenêtre principale tkinter

file_path = filedialog.askopenfilename(
    title="Select the quantification_summary.csv file",
    filetypes=[
        ("Fichiers CSV", "*.csv"),
        ("Tous les fichiers", "*.*")
    ]
)

# Si l'utilisateur annule
if not file_path:
    print("Aucun fichier sélectionné.")
    exit()


# ============================================================
# 2. Charger le fichier
# ============================================================

print(f"Fichier sélectionné : {file_path}")

try:
    df = pd.read_csv(file_path)
except Exception as e:
    messagebox.showerror(
        "Erreur",
        f"Impossible de lire le fichier CSV :\n\n{e}"
    )
    exit()


# ============================================================
# 3. Définir automatiquement les noms de colonnes
# ============================================================

MARKER_POSITIVE = f"{MARKER}+"
PERCENT_COLUMN = f"{MARKER}_percent"


# ============================================================
# 4. Vérifier que les colonnes nécessaires existent
# ============================================================

required_columns = [
    "Image",
    "Clone",
    MARKER_POSITIVE,
    "total_cells"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:

    messagebox.showerror(
        "Colonnes manquantes",
        "Les colonnes suivantes sont absentes du fichier CSV :\n\n"
        + "\n".join(missing_columns)
    )

    exit()


# ============================================================
# 5. Nettoyage des données
# ============================================================

df[MARKER_POSITIVE] = pd.to_numeric(
    df[MARKER_POSITIVE],
    errors="coerce"
)

df["total_cells"] = pd.to_numeric(
    df["total_cells"],
    errors="coerce"
)

# Supprimer les lignes invalides
df = df.dropna(
    subset=[
        "Clone",
        MARKER_POSITIVE,
        "total_cells"
    ]
)

# Éviter les divisions par zéro
df = df[
    df["total_cells"] > 0
]


# ============================================================
# 6. Calcul de la proportion de cellules positives
# ============================================================

df[PERCENT_COLUMN] = (
    df[MARKER_POSITIVE]
    / df["total_cells"]
) * 100


# ============================================================
# 7. Créer le graphique
# ============================================================

sns.set_theme(
    style="ticks",
    font_scale=1.4
)

fig, ax = plt.subplots(
    figsize=(6, 5)
)


# ------------------------------------------------------------
# Points individuels
# Chaque point = une image
# ------------------------------------------------------------

sns.stripplot(
    data=df,
    x="Clone",
    y=PERCENT_COLUMN,
    order=CLONE_ORDER,
    hue="Clone",
    jitter=0.18,
    size=9,
    alpha=0.8,
    palette="Set2",
    legend=False,
    ax=ax
)


# ------------------------------------------------------------
# Moyenne ± SD
# ------------------------------------------------------------

summary = (
    df.groupby("Clone")[PERCENT_COLUMN]
    .agg(["mean", "std"])
    .reset_index()
)


for i, clone in enumerate(CLONE_ORDER):

    row = summary[
        summary["Clone"] == clone
    ]

    # Si le clone n'existe pas dans le fichier
    if len(row) == 0:
        continue

    mean = row["mean"].iloc[0]
    std = row["std"].iloc[0]

    ax.errorbar(
        i,
        mean,
        yerr=std,
        fmt="_",
        color="black",
        markersize=20,
        capsize=6,
        capthick=2.5,
        linewidth=2.5
    )


# ============================================================
# 8. Mise en forme
# ============================================================

ax.set_xlabel(
    "Clone",
    fontsize=16,
    fontweight="bold"
)

ax.set_ylabel(
    f"{MARKER}+ cells (%)",
    fontsize=16,
    fontweight="bold"
)

ax.set_title(
    f"Proportion de cellules {MARKER}+",
    fontsize=18,
    fontweight="bold",
    pad=12
)

# Taille des labels des clones
ax.tick_params(
    axis="both",
    labelsize=14
)

# Axe Y de 0 à 100 %
ax.set_ylim(0, 100)

# Épaissir les axes
ax.spines["left"].set_linewidth(1.5)
ax.spines["bottom"].set_linewidth(1.5)

sns.despine()

plt.tight_layout()


# ============================================================
# 9. Sauvegarder automatiquement
# ============================================================

input_path = Path(file_path)

output_path = (
    input_path.parent
    / f"{input_path.stem}_{MARKER}_par_clone.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print(
    f"\nGraphique sauvegardé ici :\n{output_path}"
)


# ============================================================
# 10. Afficher le graphique
# ============================================================

plt.show()


# ============================================================
# 11. Message de fin
# ============================================================

messagebox.showinfo(
    "Terminé",
    f"Le graphique {MARKER}+ a été créé avec succès !\n\n"
    f"Fichier :\n{output_path}"
)
