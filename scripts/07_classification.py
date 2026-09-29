# -*- coding: utf-8 -*-
"""
Created on Aug 26 2026

@author: Lucas Denis
"""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import pandas as pd
from itertools import combinations

# ============================================================
# 1. Chargement de la table 
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

# Fichier de sortie
output_file = csv_file.parent / "quantification.csv"

# ============================================================
# 2. Récupération automatique des marqueurs
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
# 3. Saisie des seuils
# ============================================================

thresholds = {}
MIN_THRESHOLD = 0


def validate_thresholds():

    try:

        for marker, entry in entries.items():

            value = float(entry.get())

            if value < 0:
                raise ValueError

            thresholds[marker] = value

        window.destroy()

    except ValueError:

        messagebox.showerror(
            "Erreur",
            "Veuillez entrer une valeur numérique positive pour chaque marqueur."
        )


window = tk.Tk()

window.title("Seuils de positivité")

window.resizable(
    False,
    False
)


# ------------------------------------------------------------
# Titre
# ------------------------------------------------------------

tk.Label(
    window,
    text="Définir le seuil minimal de positivité",
    font=("Arial", 12, "bold")
).grid(
    row=0,
    column=0,
    columnspan=2,
    padx=20,
    pady=(15, 5)
)


tk.Label(
    window,
    text="Les valeurs ≥ au seuil seront considérées positives.",
    font=("Arial", 9)
).grid(
    row=1,
    column=0,
    columnspan=2,
    padx=20,
    pady=(0, 15)
)


# ------------------------------------------------------------
# Champs
# ------------------------------------------------------------

entries = {}

for i, marker in enumerate(markers, start=2):

    tk.Label(
        window,
        text=f"{marker} :"
    ).grid(
        row=i,
        column=0,
        sticky="e",
        padx=10,
        pady=5
    )

    entry = tk.Entry(
        window,
        width=15
    )

    entry.insert(
        0,
        str(MIN_THRESHOLD)
    )

    entry.grid(
        row=i,
        column=1,
        padx=10,
        pady=5
    )

    entries[marker] = entry


# ------------------------------------------------------------
# Bouton
# ------------------------------------------------------------

tk.Button(
    window,
    text="Valider",
    command=validate_thresholds,
    width=15
).grid(
    row=len(markers) + 2,
    column=0,
    columnspan=2,
    pady=15
)


window.mainloop()


# ------------------------------------------------------------
# Vérification
# ------------------------------------------------------------

if not thresholds:

    raise SystemExit(
        "Aucun seuil n'a été défini."
    )


print("\n" + "=" * 60)
print("SEUILS DE POSITIVITÉ")
print("=" * 60)

for marker, threshold in thresholds.items():

    print(
        f"{marker} : {threshold}"
    )


# ============================================================
# 4. Ajout des seuils et classification positive/négative
# ============================================================

for marker, threshold in thresholds.items():

    # --------------------------------------------------------
    # Seuil utilisé pour ce marqueur
    # --------------------------------------------------------

    df[f"threshold_{marker}"] = threshold

    # --------------------------------------------------------
    # Classification positive / négative
    # --------------------------------------------------------

    df[f"positive_{marker}"] = (
        df[f"mean_{marker}"] >= threshold
    )


# ============================================================
# 5. Ordres des colonnes
# ============================================================

# Colonnes générales
first_columns = [
    "Image",
    "Differentiation",
    "Jour",
    "Clone",
    "Condition",
    "label"
]

# Colonnes de chaque marqueur
marker_columns = []

for marker in markers:

    marker_columns.extend([
        f"mean_{marker}",
        f"threshold_{marker}",
        f"positive_{marker}"
    ])


# Nouveaux ordre des colonnes
column_order = first_columns + marker_columns


# Vérification des colonnes disponibles
column_order = [
    col for col in column_order
    if col in df.columns
]


# Réorganisation
df = df[column_order]

# ============================================================
# 6. Sauvegarde du dataframe
# ============================================================

df.to_csv(
    output_file,
    index=False
)


print("\n" + "=" * 60)
print("MESURES TERMINÉES")
print("=" * 60)

print(
    f"Nombre total de noyaux : "
    f"{len(df)}"
)

print(
    f"CSV : {output_file}"
)


# ============================================================
# 7. Classification des cellules
# ============================================================

def classify_cell(row):

    positive_markers = [
        marker
        for marker in markers
        if row[f"positive_{marker}"]
    ]


    # --------------------------------------------------------
    # Aucun marqueur positif
    # --------------------------------------------------------

    if len(positive_markers) == 0:

        return "Negative"


    # --------------------------------------------------------
    # Tous les marqueurs positifs
    # --------------------------------------------------------

    elif len(positive_markers) == len(markers):

        return "_".join(
            positive_markers
        )


    # --------------------------------------------------------
    # Un seul marqueur positif
    # --------------------------------------------------------

    elif len(positive_markers) == 1:

        return (
            f"{positive_markers[0]}_only"
        )


    # --------------------------------------------------------
    # Plusieurs marqueurs positifs
    # --------------------------------------------------------

    else:

        return "_".join(
            positive_markers
        )


df["population"] = (
    df.apply(
        classify_cell,
        axis=1
    )
)


# ============================================================
# 9. Liste de toutes les populations possibles
# ============================================================

all_populations = ["Negative"]


# Combinaisons de 1 marqueur
for marker in markers:

    all_populations.append(
        f"{marker}_only"
    )


# Combinaisons de 2 marqueurs ou plus
for n in range(2, len(markers) + 1):

    for combination in combinations(markers, n):

        all_populations.append(
            "_".join(combination)
        )


# ============================================================
# 10. Création du tableau récap
# ============================================================

summary = []


for image, group in df.groupby(
    "Image"
):

    total = len(group)


    # --------------------------------------------------------
    # Récupération des informations de l'image
    # --------------------------------------------------------

    image = group["Image"].iloc[0]
    differentiation = group["Differentiation"].iloc[0]
    jour = group["Jour"].iloc[0]
    clone = group["Clone"].iloc[0]
    condition = group["Condition"].iloc[0]



    result = {
        "Image": image,
        "Differentiation": differentiation,
        "Jour": jour,
        "Clone": clone,
        "Condition": condition,
        "total_cells": total
    }

    # --------------------------------------------------------
    # Nombre total de cellules positives pour chaque marqueur
    # --------------------------------------------------------

    for marker in markers:

        result[f"{marker}+"] = (
            group[f"positive_{marker}"]
            .sum()
        )


    # --------------------------------------------------------
    # Populations mutuellement exclusives
    # --------------------------------------------------------

    counts = (
        group["population"]
        .value_counts()
        .reindex(
            all_populations,
            fill_value=0
        )
    )

    for population, count in counts.items():

        result[population] = count


    # --------------------------------------------------------
    # Ajout des résultats
    # --------------------------------------------------------

    summary.append(
        result
    )


summary_df = pd.DataFrame(
    summary
)

# ============================================================
# 11. Remplacer les NaN par 0
# ============================================================

summary_df = summary_df.fillna(
    0
)

# ============================================================
# 12. Vérification des populations
# ============================================================

population_columns = [
    col
    for col in summary_df.columns
    if col not in [
        "Image",
        "Differentiation",
        "Jour",
        "Clone",
        "Condition",
        "total_cells"
    ]
    and not col.endswith("+")
]


summary_df["check"] = (
    summary_df[population_columns]
    .sum(axis=1)
    ==
    summary_df["total_cells"]
)


# ============================================================
# 13. Vérifications
# ============================================================

if summary_df["check"].all():

    print(
        "\n✓ Vérification OK : toutes les cellules "
        "appartiennent à une population unique."
    )

else:

    print(
        "\n⚠ ERREUR : les populations ne correspondent "
        "pas au nombre total de cellules."
    )


# ============================================================
# 14. Suppression colonne de vérification
# ============================================================

summary_df = summary_df.drop(
    columns=["check"]
)


# ============================================================
# 15. Sauvegarde du résumé
# ============================================================

output_summary = (
    output_file.parent /
    "quantification_summary.csv"
)


summary_df.to_csv(
    output_summary,
    index=False
)


print("\n" + "=" * 60)
print("Résumé sauvegardé :")
print(output_summary)
print("=" * 60)

