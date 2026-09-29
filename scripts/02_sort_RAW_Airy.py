
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 2026

@author: Lucas Denis
"""

from pathlib import Path
import shutil
import tkinter as tk
from tkinter import filedialog


# ============================================================
# SÉLECTION DU DOSSIER
# ============================================================

root = tk.Tk()
root.withdraw()

source_folder = filedialog.askdirectory(
    title="Select the folder containing the images"
)

if not source_folder:
    print("Aucun dossier sélectionné.")
    exit()

source_folder = Path(source_folder)


# ============================================================
# CRÉATION DES DOSSIERS
# ============================================================

processed_folder = source_folder / "Airyscan_processed"
raw_folder = source_folder / "RAW"

processed_folder.mkdir(exist_ok=True)
raw_folder.mkdir(exist_ok=True)


# ============================================================
# TRI DES FICHIERS
# ============================================================

processed_count = 0
raw_count = 0

for file in source_folder.iterdir():

    # On ne traite que les fichiers
    if not file.is_file():
        continue

    # On ignore les éventuels fichiers déjà présents dans
    # les dossiers de destination
    if file.parent in [processed_folder, raw_folder]:
        continue

    # Airyscan processed
    if "Airyscan" in file.name:
        destination = processed_folder
        processed_count += 1

    # RAW
    else:
        destination = raw_folder
        raw_count += 1

    # Déplacement du fichier
    shutil.move(str(file), str(destination / file.name))


# ============================================================
# RÉSULTAT
# ============================================================

print()
print("=" * 50)
print("TRI DES IMAGES TERMINÉ")
print("=" * 50)
print(f"Dossier source : {source_folder}")
print()
print(f"Airyscan_processed : {processed_count} fichiers")
print(f"RAW                : {raw_count} fichiers")
print()
print(f"Total              : {processed_count + raw_count} fichiers")
print("=" * 50)