# -*- coding: utf-8 -*-
"""
Created on Aug 26 2026

@author: Lucas Denis
"""
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from tqdm import tqdm
import tifffile
from skimage.measure import regionprops_table
import pandas as pd
import numpy as np

# ============================================================
# Sélection dossier de segmentation et dossier images
# ============================================================

root = tk.Tk()
root.withdraw()

# Choix du dossier contenant les masques de segmentation
segmentation_folder = filedialog.askdirectory(
    title="Select folder containing segmentation masks"
)

if not segmentation_folder:
    root.destroy()
    raise SystemExit("Aucun dossier de segmentation sélectionné.")

# Conversion en Path
segmentation_folder = Path(segmentation_folder)

# Choix du dossier contenant les images
images_folder = filedialog.askdirectory(
    title="Select folder containing images"
)

if not images_folder:
    root.destroy()
    raise SystemExit("Aucun dossier d'images sélectionné.")

# Conversion en Path
images_folder = Path(images_folder)

root.destroy()

# Fichier de sortie
output_file = segmentation_folder.parent / "quantification.csv"


# ============================================================
# 1. RECHERCHE DES IMAGES À TRAITER
# ============================================================

mask_files = sorted(
    segmentation_folder.glob(
        "*_DAPI_segmented.tif"
    )
)


print("=" * 60)
print(
    f"{len(mask_files)} images à traiter"
)
print("=" * 60)


all_results = []


# ============================================================
# 2. DETECTION DES MARQUEURS
# ============================================================

# Première image pour déterminer les marqueurs
first_mask_file = mask_files[0]

image_name = first_mask_file.name.replace(
    "_DAPI_segmented.tif",
    ""
)

marker_files = sorted(
    file for file in images_folder.glob(
        f"{image_name}_*.tif"
    )
    if file.stem.rsplit("_", 1)[-1].upper() != "DAPI"
)

if not marker_files:

    raise RuntimeError(
        "Aucun marqueur trouvé dans la première image."
    )

markers = [
    file.stem.rsplit("_", 1)[-1]
    for file in marker_files
]

print("\nMarqueurs détectés :")
print(markers)


# ============================================================
# 3. MESURE DU SIGNAL DE CHAQUE MARQUEURS POUR CHAQUE IMAGES
# ============================================================

for mask_file in tqdm(
    mask_files,
    desc="Traitement des images",
    unit="image"
    ):

    # --------------------------------------------------------
    # Nom de l'image
    # --------------------------------------------------------

    image_name = mask_file.name.replace(
        "_DAPI_segmented.tif",
        ""
    )


    # --------------------------------------------------------
    # Extraction des informations
    # --------------------------------------------------------

    parts = image_name.split("_")


    if len(parts) < 3:

        print(
            f"⚠ Nom inattendu : "
            f"{mask_file.name}"
        )

        continue


    differentiation = parts[0]
    jour = parts[1]
    clone = parts[2]


    # --------------------------------------------------------
    # Chargement du masque
    # --------------------------------------------------------

    mask = tifffile.imread(
        mask_file
    )


    # --------------------------------------------------------
    # DataFrame contenant les résultats
    # --------------------------------------------------------

    df = None


    # ========================================================
    # TRAITEMENT DE CHAQUE MARQUEUR
    # ========================================================

    for marker_file in marker_files:

        marker = marker_file.stem.rsplit("_", 1)[-1]

        # ----------------------------------------------------
        # Chargement de l'image
        # ----------------------------------------------------

        img = tifffile.imread(
            marker_file
        )


        # ----------------------------------------------------
        # Vérification dimensions
        # ----------------------------------------------------

        if img.shape != mask.shape:

            print(
                f"⚠ Dimensions incompatibles : "
                f"{marker_file.name}"
            )

            continue


        # ====================================================
        # MESURE DES INTENSITÉS PAR NOYAU
        # ====================================================

        props = regionprops_table(
            mask,
            intensity_image=img,
            properties=(
                "label",
                "mean_intensity"
            )
        )


        d = pd.DataFrame(
            props
        )

        # ----------------------------------------------------
        # Récupération des intensités
        # ----------------------------------------------------

        values = (
            d["mean_intensity"]
            .dropna()
            .values
        )


        # ----------------------------------------------------
        # Vérification du nombre de noyaux
        # ----------------------------------------------------

        if len(values) < 2:

            print(
                f"⚠ Pas assez de noyaux "
                f"pour calculer Otsu pour {marker}"
            )

            continue


        # ----------------------------------------------------
        # Vérification intensités identiques
        # ----------------------------------------------------

        if np.all(values == values[0]):

            print(
                f"⚠ Intensités identiques pour {marker} "
                f"→ Otsu impossible"
            )

            continue


        # ====================================================
        # CREATION COLONNE INTENSITE
        # ====================================================

        d[f"mean_{marker}"] = (
            d["mean_intensity"]
        )


        # ----------------------------------------------------
        # Suppression de la colonne temporaire
        # ----------------------------------------------------

        d = d.drop(
            columns=["mean_intensity"]
        )


        # ====================================================
        # FUSION AVEC LES AUTRES MARQUEURS
        # ====================================================

        if df is None:

            df = d

        else:

            df = df.merge(
                d,
                on="label",
                how="outer"
            )


    # ========================================================
    # VÉRIFICATION
    # ========================================================

    if df is None:

        print(
            "⚠ Aucun résultat pour cette image."
        )

        continue

    # ========================================================
    # Ajout des infos de l'image
    # ========================================================

    df["Image"] = image_name

    df["Differentiation"] = differentiation

    df["Jour"] = jour

    df["Clone"] = clone

    # --------------------------------------------------------
    # Création de la condition
    # --------------------------------------------------------

    df["Condition"] = (
        df["Differentiation"].astype(str)
        + "_"
        + df["Jour"].astype(str)
        + "_"
        + df["Clone"].astype(str)
    )


    # ========================================================
    # AJOUT AU RÉSULTAT GLOBAL
    # ========================================================

    all_results.append(
        df
    )


# ============================================================
# 4. FUSION FINALE
# ============================================================

if not all_results:

    raise RuntimeError(
        "Aucun résultat n'a été généré."
    )


final_df = pd.concat(
    all_results,
    ignore_index=True
)


# ============================================================
# 5. ORDRE DES COLONNES
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
    ])


# Nouveaux ordre des colonnes
column_order = first_columns + marker_columns


# Vérification des colonnes disponibles
column_order = [
    col for col in column_order
    if col in final_df.columns
]


# Réorganisation
final_df = final_df[column_order]


# ============================================================
# 6. SAUVEGARDE DU DATAFRAME
# ============================================================

final_df.to_csv(
    output_file,
    index=False
)


print("\n" + "=" * 60)
print("MESURES TERMINÉES")
print("=" * 60)

print(
    f"Nombre total de noyaux : "
    f"{len(final_df)}"
)

print(
    f"CSV : {output_file}"
)