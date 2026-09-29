# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 2026

@author: Lucas Denis
"""

from pathlib import Path
from tkinter import Tk, filedialog

import tifffile
import pandas as pd
import numpy as np
from PIL import Image

import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# VISUALISATION DE LA CLASSIFICATION
# ============================================================


# ============================================================
# 1. INPUTS
# ============================================================

root = Tk()
root.withdraw()

# ------------------------------------------------------------
# Sélection des masques Cellpose à contrôler
# ------------------------------------------------------------

selected_files = filedialog.askopenfilenames(
    title="Sélectionner les images à contrôler (masques de segmentation)",
    filetypes=[
        (
            "Masques DAPI",
            "*_DAPI_segmented.tif"
        ),
        (
            "Fichiers TIFF",
            "*.tif"
        ),
        (
            "Tous les fichiers",
            "*.*"
        )
    ]
)


if not selected_files:

    root.destroy()

    raise SystemExit(
        "Aucune image sélectionnée."
    )


# Conversion en Path
mask_files = [
    Path(file)
    for file in selected_files
]


# Dossier contenant les masques
input_folder = mask_files[0].parent


root.destroy()


print(
    f"\n{len(mask_files)} image(s) sélectionnée(s)."
)

# ============================================================
# 2. FICHIERS ET DOSSIERS
# ============================================================

# Tableau global généré par la pipeline de quantification
csv_file = input_folder.parent / "quantification.csv"

# Dossier de sortie des images de contrôle
output_folder = input_folder.parent / "Control_Classification"
output_folder.mkdir(exist_ok=True)


# ============================================================
# 3. CHARGEMENT DU CSV
# ============================================================

df = pd.read_csv(csv_file)

print(f"\n{len(df)} noyaux trouvés dans le tableau.")

print("\n======================================")
print("CONTRÔLE VISUEL DE LA CLASSIFICATION...")
print("======================================")

# ============================================================
# 4. Identification automatique des marqueurs
# ============================================================

marker_columns = [
    col
    for col in df.columns
    if col.startswith("mean_")
]


markers = [
    col.replace("mean_", "")
    for col in marker_columns
]


print(
    f"Marqueurs trouvés : {', '.join(markers)}"
)


# ============================================================
# 5. Traitements de chaque image
# ============================================================

for mask_file in mask_files:

    # --------------------------------------------------------
    # Récupération du nom de l'image
    # --------------------------------------------------------

    image = mask_file.name.replace(
        "_DAPI_segmented.tif",
        ""
    )


    print("\n" + "=" * 60)
    print(
        f"Image : {image}"
    )
    print("=" * 60)


    # --------------------------------------------------------
    # Chargement du masque
    # --------------------------------------------------------

    mask = tifffile.imread(
        mask_file
    )


    # --------------------------------------------------------
    # Vérification que l'image existe dans le CSV
    # --------------------------------------------------------

    image_df = df[
        df["Image"] == image
    ].copy()


    if image_df.empty:

        print(
            f"⚠ Aucune donnée trouvée dans le CSV "
            f"pour {image}"
        )

        continue


    print(
        f"{len(image_df)} noyaux dans le tableau."
    )


    # --------------------------------------------------------
    # Vérification de la correspondance des labels
    # --------------------------------------------------------

    mask_labels = set(
        np.unique(mask)
    )

    mask_labels.discard(0)


    table_labels = set(
        image_df["label"]
        .astype(int)
    )


    missing_in_table = (
        mask_labels - table_labels
    )

    missing_in_mask = (
        table_labels - mask_labels
    )


    if missing_in_table:

        print(
            f"⚠ {len(missing_in_table)} "
            f"labels du masque absents du tableau."
        )


    if missing_in_mask:

        print(
            f"⚠ {len(missing_in_mask)} "
            f"labels du tableau absents du masque."
        )


    # ========================================================
    # CRÉATION DES IMAGES POUR CHAQUE MARQUEUR
    # ========================================================

    for marker in markers:

        intensity_column = (
            f"mean_{marker}"
        )

        threshold_column = (
            f"threshold_{marker}"
        )


        # ----------------------------------------------------
        # Vérification des colonnes
        # ----------------------------------------------------

        required_columns = [
            intensity_column,
            threshold_column,
        ]


        missing_columns = [
            col
            for col in required_columns
            if col not in image_df.columns
        ]


        if missing_columns:

            print(
                f"⚠ Colonnes manquantes pour {marker} : "
                f"{missing_columns}"
            )

            continue


        # ----------------------------------------------------
        # Récupération des seuils
        # ----------------------------------------------------

        thresholds = (
            image_df[threshold_column]
            .dropna()
            .unique()
        )


        if len(thresholds) == 0:

            print(
                f"⚠ Aucun seuil pour {marker}"
            )

            continue


        threshold = (
            thresholds[0]
        )


        print(
            f"\n  → {marker}"
        )

        print(
            f"     Threshold  : {threshold:.2f}"
        )

        # ========================================================
        # CRÉATION DE L'IMAGE DE CLASSIFICATION
        # ========================================================

        positive_column = (
            f"positive_{marker}"
        )


        # --------------------------------------------------------
        # Vérifier que la colonne existe
        # --------------------------------------------------------

        if positive_column not in image_df.columns:

            print(
                f"⚠ Colonne {positive_column} absente "
                f"du tableau."
            )

            continue


        print(
            f"     → Création image {marker}"
        )


        # --------------------------------------------------------
        # Création de l'image RGB
        # --------------------------------------------------------

        rgb = np.zeros(
            (*mask.shape, 3),
            dtype=np.uint8
        )


        # --------------------------------------------------------
        # Parcours des noyaux
        # --------------------------------------------------------

        for _, row in image_df.iterrows():

            label = int(
                row["label"]
            )


            positive = row[
            positive_column
            ]


            # ----------------------------------------------------
            # Gestion des valeurs manquantes
            # ----------------------------------------------------

            if pd.isna(positive):

                continue


            # ----------------------------------------------------
            # Pixels appartenant au noyau
            # ----------------------------------------------------

            nucleus = (
                mask == label
            )


            # ----------------------------------------------------
            # Classification
            # ----------------------------------------------------

            if bool(positive):

                # POSITIF → BLEU/VERT

                rgb[nucleus] = [
                    0,
                    170,
                    100
                ]

            else:

                # NEGATIF → ROUGE

                rgb[nucleus] = [
                    230,
                    80,
                    50
                ]


        # ========================================================
        # SAUVEGARDE
        # ========================================================

        output_file = (
            output_folder /
            f"{image}_{marker}_classification.jpg"
        )


        Image.fromarray(rgb).save(
            output_file,
            quality=95
        )


        print(
            f"        Sauvegardé : "
            f"{output_file.name}"
        )


# ============================================================
# FIN
# ============================================================

print("\n" + "=" * 60)
print("CONTRÔLE DE CLASSIFICATION TERMINÉ")
print("=" * 60)

print(
    f"Images sauvegardées dans : "
    f"{output_folder}"
)