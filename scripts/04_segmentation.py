# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 2026

@author: Lucas Denis
"""

from cellpose import models, io
from pathlib import Path
import os
from tqdm import tqdm
from tkinter import Tk, filedialog
import logging
import warnings

warnings.filterwarnings("ignore")
logging.getLogger("tifffile").setLevel(logging.ERROR)

# -----------------------
# Chargement des paramètres
# -----------------------
from config import load_config
config = load_config()

model_name = config["cellpose"]["model"]
diameter = config["cellpose"]["diameter"]
flow_threshold = config["cellpose"]["flow_threshold"]
cellprob_threshold = config["cellpose"]["cellprob_threshold"]


# Masquer la fenêtre principale
root = Tk()
root.withdraw()

# Choix du dossier contenant les images
selected_folder = filedialog.askdirectory(
    title="Select folder containing images"
)

# Vérifier qu'un dossier a été sélectionné
if not selected_folder:
    raise SystemExit("Aucun dossier sélectionné.")

# Conversion en objet Path
input_folder = Path(selected_folder)

# Création automatique du dossier "Segmentation"
output_folder = input_folder.parent / "Segmentation"
output_folder.mkdir(exist_ok=True)

print(f"Dossier Images : {input_folder}")
print(f"Dossier Segmentation : {output_folder}")

# -----------------------
# Initialisation
# -----------------------

os.makedirs(output_folder, exist_ok=True)

model = models.CellposeModel(
    model_type=model_name
)


# -----------------------
# Segmentation batch
# -----------------------

files = list(Path(input_folder).glob("*_DAPI.tif"))

print(f"{len(files)} images à traiter.")

for file in tqdm(files, desc="Segmentation", unit="image"):

    img = io.imread(file)

    masks, flows, styles = model.eval(
        img,
        diameter=diameter,
        channels=[0, 0],
        flow_threshold=flow_threshold,
        cellprob_threshold=cellprob_threshold
    )

    output = Path(output_folder) / (
        file.stem + "_segmented.tif"
    )

    io.imsave(
        output,
        masks.astype("uint16")
    )


print(f"Segmentation sauvegardée : {output_folder}")