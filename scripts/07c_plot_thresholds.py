# -*- coding: utf-8 -*-
"""
Created on Aug 26 2026

@author: Lucas Denis
"""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import pandas as pd
import numpy as np
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

#Création dossier de sortie
plot_distri_folder = csv_file.parent / "Plot_Thresholds"
plot_distri_folder.mkdir(exist_ok=True)

# ============================================================
# 2. Récupérer automatiquement les marqueurs
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
# 3. Tracer la distribution
# ============================================================

for intensity_column in marker_columns:

    marker = intensity_column.replace(
        "mean_",
        ""
    )

    threshold_column = (
            f"threshold_{marker}"
        )
    
    
    # --------------------------------------------------------
    # Vérifier que les seuils existent
    # --------------------------------------------------------
    
    if (
        threshold_column not in df.columns
    ):
        continue

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

    # --------------------------------------------------------
    # Récupérer les seuils uniques
    # --------------------------------------------------------
    
    thresholds = (
        df[threshold_column]
        .dropna()
        .unique()
    )
    
    if len(thresholds) == 0:
        continue
    
    
    # --------------------------------------------------------
    # Vérifier qu'il n'y a qu'un seul seuil
    # --------------------------------------------------------
    
    if len(thresholds) > 1:
    
        print(
            f"⚠ Plusieurs seuils trouvés pour "
            f"{marker} : {thresholds}"
        )
    
    threshold = thresholds[0]

    # ========================================================
    # FIGURE
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )


    # --------------------------------------------------------
    # Courbe de densité
    # --------------------------------------------------------

    kde = sns.kdeplot(
        x=values,
        fill=False,
        linewidth=0,
        ax=ax
    )

    # Récupération des coordonnées
    x_kde = kde.lines[-1].get_xdata()
    y_kde = kde.lines[-1].get_ydata()

    # Supprimer la courbe temporaire
    kde.lines[-1].remove()


    # --------------------------------------------------------
    # Ajouter le seuil exactement dans les coordonnées
    # --------------------------------------------------------

    if x_kde.min() < threshold < x_kde.max():

        y_threshold = np.interp(
            threshold,
            x_kde,
            y_kde
        )

        # Partie gauche
        x_left = np.append(
            x_kde[x_kde < threshold],
            threshold
        )

        y_left = np.append(
            y_kde[x_kde < threshold],
            y_threshold
        )

        # Partie droite
        x_right = np.insert(
            x_kde[x_kde > threshold],
            0,
            threshold
        )

        y_right = np.insert(
            y_kde[x_kde > threshold],
            0,
            y_threshold
        )

    else:

        x_left = x_kde[x_kde <= threshold]
        y_left = y_kde[x_kde <= threshold]

        x_right = x_kde[x_kde >= threshold]
        y_right = y_kde[x_kde >= threshold]


    # --------------------------------------------------------
    # Remplissage rouge
    # --------------------------------------------------------

    ax.fill_between(
        x_left,
        y_left,
        color="red",
        alpha=0.3
    )


    # --------------------------------------------------------
    # Remplissage vert
    # --------------------------------------------------------

    ax.fill_between(
        x_right,
        y_right,
        color="green",
        alpha=0.3
    )


    # --------------------------------------------------------
    # Courbe rouge
    # --------------------------------------------------------

    ax.plot(
        x_left,
        y_left,
        color="red",
        linewidth=1
    )


    # --------------------------------------------------------
    # Courbe verte
    # --------------------------------------------------------

    ax.plot(
        x_right,
        y_right,
        color="green",
        linewidth=1
    )

    # --------------------------------------------------------
    # Seuil
    # --------------------------------------------------------
    
    plt.axvline(
        threshold,
        linestyle="-",
        linewidth=1.5,
        color="black",
        label=f"threshold = {threshold:.2f}"
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

    ax.set_ylim(bottom=0)

    plt.legend()

    plt.tight_layout()


    # ========================================================
    # SAUVEGARDE
    # ========================================================

    output_plot = (
        plot_distri_folder /
        f"Threshold_{marker}.png"
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

