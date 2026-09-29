# -*- coding: utf-8 -*-
"""
Created on Aug 26 2026

@author: Lucas Denis
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# 1. Chargement de la table et génération dossier de sortie
# ============================================================

root = tk.Tk()
root.withdraw()  # Cache la fenêtre principale de Tkinter

csv_path = filedialog.askopenfilename(
    title="Select quantification file",
    filetypes=[
        ("Fichiers CSV", "*.csv"),
        ("Tous les fichiers", "*.*")
    ]
)

root.destroy()

# Vérifier qu'un fichier a bien été sélectionné
if not csv_path:
    raise SystemExit("Aucun fichier CSV sélectionné.")

csv_file = Path(csv_path)

print(f"Fichier sélectionné : {csv_file}")

df = pd.read_csv(csv_file)

print(
    f"\n{len(df)} noyaux trouvés dans le tableau."
)

# ============================================================
# 2. Création du dossier de sortie
# ============================================================

if "background" in csv_file.name.lower():

    plot_distri_folder = (
        csv_file.parent
        / "Plot_Distribution_background"
    )

else:

    plot_distri_folder = (
        csv_file.parent
        / "Plot_Distribution"
    )


plot_distri_folder.mkdir(
    exist_ok=True
)


# ============================================================
# 3. Récupérer automatiquement les marqueurs
# ============================================================

marker_columns = [
    col
    for col in df.columns
    if col.startswith("mean_")
]

markers = [
    col.replace("mean_", "", 1)
    for col in marker_columns
]


# ============================================================
# 4. Tracer la distribution
# ============================================================

for intensity_column in marker_columns:

    marker = intensity_column.replace(
        "mean_",
        ""
    )

    # --------------------------------------------------------
    # Toutes les intensités du marqueur
    # --------------------------------------------------------

    values = (
        df[intensity_column]
        .dropna()
        .values
    )


    if len(values) < 2:
        continue

    # ========================================================
    # FIGURE
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )


    # --------------------------------------------------------
    # Courbe de densité
    # --------------------------------------------------------

    sns.kdeplot(
        x=values,
        fill=True,
        linewidth=1,
        ax=ax
    )

    # ========================================================
    # MISE EN FORME
    # ========================================================

    # --------------------------------------------------------
    # Labels des axes
    # --------------------------------------------------------

    ax.set_xlabel(
        f"Mean Nuclear Intensity",
        fontsize=16,
        fontweight="bold",
        labelpad=8
    )

    ax.set_ylabel(
        "Density",
        fontsize=16,
        fontweight="bold",
        labelpad=8
    )


    # --------------------------------------------------------
    # Taille des graduations
    # --------------------------------------------------------

    ax.tick_params(
        axis="both",
        which="major",
        labelsize=13,
        width=1.5,
        length=6
    )


    # --------------------------------------------------------
    # Épaisseur des axes
    # --------------------------------------------------------

    for spine in ax.spines.values():

        spine.set_linewidth(1.5)


    # --------------------------------------------------------
    # Suppression du cadre supérieur et droit
    # --------------------------------------------------------

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


    # --------------------------------------------------------
    # Grille légère
    # --------------------------------------------------------

    ax.grid(
        axis="y",
        linestyle="--",
        linewidth=0.7,
        alpha=0.3
    )


    # --------------------------------------------------------
    # Titre
    # --------------------------------------------------------

    ax.set_title(
        f"{marker}",
        fontsize=18,
        fontweight="bold",
        pad=12
    )


    # --------------------------------------------------------
    # Marges
    # --------------------------------------------------------

    ax.margins(
        x=0.02
    )


    plt.tight_layout()


    # ========================================================
    # SAUVEGARDE
    # ========================================================

    if "background" in csv_file.name.lower():

        output_plot = (
            plot_distri_folder /
            f"Intensity_distribution_background_{marker}.png"
        )

    else:

        output_plot = (
            plot_distri_folder /
            f"Intensity_distribution_{marker}.png"
        )

    plt.savefig(
        output_plot,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

print(
    f"\nGraphiques sauvegardés dans : "
    f"{plot_distri_folder}"
)

