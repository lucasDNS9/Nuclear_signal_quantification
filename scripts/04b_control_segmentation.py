
# -*- coding: utf-8 -*-

# ============================================================
# IMPORTS
# ============================================================

from pathlib import Path

import tkinter as tk
from tkinter import filedialog

import numpy as np
import tifffile
import glasbey
from PIL import Image


# ============================================================
# PARAMÈTRES
# ============================================================

# Nombre de couleurs générées dans la palette.
N_COLORS = 512


# ============================================================
# SÉLECTION DU DOSSIER
# ============================================================

root = tk.Tk()

root.withdraw()


selected_folder = filedialog.askdirectory(
    title="Sélectionner le dossier contenant les masques"
)


if not selected_folder:

    root.destroy()

    raise SystemExit(
        "Aucun dossier sélectionné."
    )


input_folder = Path(
    selected_folder
)


# ============================================================
# DOSSIER DE SORTIE
# ============================================================

output_folder_seg = (
    input_folder.parent
    / "Control_Segmentation"
)


output_folder_seg.mkdir(
    parents=True,
    exist_ok=True
)


print()
print("=" * 60)
print("COLORATION DES MASQUES CELLPOSE")
print("=" * 60)

print()

print(
    f"Dossier d'entrée :\n{input_folder}"
)

print()

print(
    f"Dossier de sortie :\n{output_folder_seg}"
)


# ============================================================
# RECHERCHE DES IMAGES
# ============================================================

files = sorted(
    input_folder.glob("*.tif")
)


print()

print(
    f"{len(files)} image(s) trouvée(s)."
)


if len(files) == 0:

    root.destroy()

    raise SystemExit(
        "Aucune image .tif trouvée dans le dossier."
    )


# ============================================================
# CRÉATION DE LA PALETTE GLASBEY
# ============================================================

print()
print("=" * 60)
print("CRÉATION DE LA PALETTE GLASBEY")
print("=" * 60)

print()

print(
    f"Génération de {N_COLORS} couleurs..."
)


palette_hex = glasbey.create_palette(
    palette_size=N_COLORS
)


# Conversion des couleurs hexadécimales
# vers des valeurs RGB uint8.

def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(
            hex_color[i:i + 2],
            16
        )
        for i in (0, 2, 4)
    )


palette = np.array(
    [
        hex_to_rgb(color)
        for color in palette_hex
    ],
    dtype=np.uint8
)


# ============================================================
# AJOUT DU NOIR POUR LE FOND
# ============================================================

# Le label Cellpose 0 correspond au fond.
palette[0] = (
    0,
    0,
    0
)


print(
    "Palette Glasbey créée."
)


# ============================================================
# FONCTION DE COLORATION
# ============================================================

def colorize_mask(
    mask,
    palette
):

    # --------------------------------------------------------
    # Vérification de la dimension
    # --------------------------------------------------------

    if mask.ndim != 2:

        raise ValueError(
            "Le masque doit être une image 2D."
        )


    # --------------------------------------------------------
    # Conversion en entier
    # --------------------------------------------------------

    labels = mask.astype(
        np.int64
    )


    # --------------------------------------------------------
    # Application cyclique de la palette
    # --------------------------------------------------------

    color_indices = (
        labels % len(palette)
    )


    colored = palette[
        color_indices
    ]


    # --------------------------------------------------------
    # Fond noir
    # --------------------------------------------------------

    colored[
        labels == 0
    ] = (
        0,
        0,
        0
    )


    return colored.astype(
        np.uint8
    )


# ============================================================
# TRAITEMENT DES IMAGES
# ============================================================

processed = 0

failed = []


print()
print("=" * 60)
print("TRAITEMENT")
print("=" * 60)


for index, file in enumerate(
    files,
    start=1
):

    print()

    print(
        f"[{index}/{len(files)}] "
        f"{file.name}"
    )


    try:

        # ----------------------------------------------------
        # LECTURE DU MASQUE
        # ----------------------------------------------------

        mask = tifffile.imread(
            file
        )


        # ----------------------------------------------------
        # INFORMATIONS
        # ----------------------------------------------------

        max_label = int(
            mask.max()
        )

        n_cells = len(
            np.unique(mask)
        ) - 1


        print(
            f"    Dimensions : {mask.shape}"
        )

        print(
            f"    Type : {mask.dtype}"
        )

        print(
            f"    Nombre de cellules : {n_cells}"
        )


        # ----------------------------------------------------
        # COLORATION
        # ----------------------------------------------------

        colored = colorize_mask(
            mask,
            palette
        )


        # ----------------------------------------------------
        # NOM DU FICHIER
        # ----------------------------------------------------

        output_file = (
            output_folder_seg
            / f"{file.stem}_colored.jpg"
        )


        # ----------------------------------------------------
        # CONVERSION EN IMAGE PIL
        # ----------------------------------------------------

        image = Image.fromarray(
            colored,
            mode="RGB"
        )


        # ----------------------------------------------------
        # ENREGISTREMENT
        # ----------------------------------------------------

        image.save(
            output_file,
            quality=95
        )


        print(
            f"    -> {output_file.name}"
        )


        processed += 1


    except Exception as error:

        print()

        print(
            f"    [ERREUR] {error}"
        )


        failed.append(
            (
                file.name,
                str(error)
            )
        )


# ============================================================
# RÉSUMÉ
# ============================================================

print()
print()
print("=" * 60)
print("TRAITEMENT TERMINÉ")
print("=" * 60)

print()

print(
    f"Images traitées : "
    f"{processed}/{len(files)}"
)


if failed:

    print()

    print(
        f"Images en erreur : {len(failed)}"
    )


    for filename, error in failed:

        print()

        print(
            f"  {filename}"
        )

        print(
            f"    {error}"
        )


print()

print(
    "Images colorées enregistrées dans :"
)

print(
    output_folder_seg
)


# ============================================================
# FERMETURE TKINTER
# ============================================================

root.destroy()

