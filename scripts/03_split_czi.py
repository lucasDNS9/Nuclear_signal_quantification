# -*- coding: utf-8 -*-

# ============================================================
# SPLIT CZI -> TIFF
# ============================================================

from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import tifffile

from aicspylibczi import CziFile


# ============================================================
# FENÊTRE PRINCIPALE TKINTER
# ============================================================

root = tk.Tk()
root.withdraw()


# ============================================================
# SÉLECTION DU DOSSIER
# ============================================================

input_dir = filedialog.askdirectory(
    title="Choisir le dossier contenant les fichiers CZI"
)


# L'utilisateur a annulé

if not input_dir:

    print("Aucun dossier sélectionné.")

    root.destroy()

    raise SystemExit


input_dir = Path(input_dir)


# ============================================================
# RECHERCHE DES CZI
# ============================================================

czi_files = sorted(
    input_dir.glob("*.czi")
)


total_files = len(czi_files)


if total_files == 0:

    messagebox.showerror(
        "Aucun fichier CZI",
        "Aucun fichier .czi n'a été trouvé dans le dossier."
    )

    root.destroy()

    raise SystemExit


print()
print("=" * 60)
print("FICHIERS CZI TROUVÉS")
print("=" * 60)

print()
print(
    f"{total_files} fichier(s) CZI trouvé(s)."
)

for file in czi_files:

    print(
        f"  - {file.name}"
    )

print()


# ============================================================
# DÉTECTION DU NOMBRE DE CANAUX
# ============================================================

# On utilise le premier CZI comme référence.

reference_czi = czi_files[0]


print("=" * 60)
print("DÉTECTION DU NOMBRE DE CANAUX")
print("=" * 60)

print()
print(
    f"Fichier de référence : {reference_czi.name}"
)

print()


try:

    czi = CziFile(
        str(reference_czi)
    )

    dims = czi.get_dims_shape()

    print(
        "Dimensions détectées :"
    )

    print(
        dims
    )

    # Première série du CZI
    first_series = dims[0]

    if "C" not in first_series:

        messagebox.showerror(
            "Erreur",
            "Impossible de détecter l'axe des canaux (C)."
        )

        root.destroy()

        raise SystemExit


    # Exemple :
    #
    # C : (0, 4)
    #
    # signifie 4 canaux.

    n_channels = first_series["C"][1]


    print()

    print(
        f"Nombre de canaux détecté : {n_channels}"
    )


except Exception as error:

    print()
    print("=" * 60)
    print("ERREUR LORS DE LA LECTURE DU CZI")
    print("=" * 60)

    print()
    print(error)

    messagebox.showerror(
        "Erreur de lecture CZI",
        str(error)
    )

    root.destroy()

    raise SystemExit


# ============================================================
# FENÊTRE DE CORRESPONDANCE DES CANAUX
# ============================================================

channel_window = tk.Toplevel()

channel_window.title(
    "Correspondance des canaux"
)

channel_window.resizable(
    False,
    False
)


# Message

tk.Label(
    channel_window,
    text=(
        f"{n_channels} canal(aux) détecté(s).\n"
        "Indiquez le nom de chaque canal."
    ),
    padx=20,
    pady=15
).pack()


# Frame contenant les champs

frame = tk.Frame(
    channel_window,
    padx=20,
    pady=10
)

frame.pack()


entries = []


# ============================================================
# VALEURS PAR DÉFAUT
# ============================================================

default_names = [
    "",
    "",
    "",
    ""
]


for i in range(n_channels):

    row = tk.Frame(
        frame
    )

    row.pack(
        fill="x",
        pady=4
    )


    tk.Label(
        row,
        text=f"Canal {i + 1} :",
        width=12,
        anchor="e"
    ).pack(
        side="left",
        padx=5
    )


    default_value = ""

    if i < len(default_names):

        default_value = default_names[i]


    entry = tk.Entry(
        row,
        width=25
    )

    entry.insert(
        0,
        default_value
    )

    entry.pack(
        side="left"
    )


    entries.append(
        entry
    )


# ============================================================
# VALIDATION
# ============================================================

dialog_validated = False

markers = []


def validate_channels():

    global dialog_validated

    markers.clear()

    for entry in entries:

        marker = entry.get().strip()

        if marker == "":

            messagebox.showerror(
                "Nom manquant",
                "Tous les canaux doivent avoir un nom.",
                parent=channel_window
            )

            return

        markers.append(
            marker
        )


    # Vérification des noms en double

    if len(markers) != len(set(markers)):

        messagebox.showerror(
            "Nom en double",
            "Chaque canal doit avoir un nom différent.",
            parent=channel_window
        )

        return


    dialog_validated = True

    channel_window.destroy()


# ============================================================
# BOUTON
# ============================================================

tk.Button(
    channel_window,
    text="Valider",
    command=validate_channels,
    width=15
).pack(
    pady=15
)


# Attendre la fermeture de la fenêtre

channel_window.grab_set()

root.wait_window(
    channel_window
)


# Si la fenêtre n'a pas été validée

if not dialog_validated:

    root.destroy()

    raise SystemExit


# ============================================================
# AFFICHAGE DE LA CORRESPONDANCE
# ============================================================

print()
print("=" * 60)
print("CORRESPONDANCE DES CANAUX")
print("=" * 60)

for i, marker in enumerate(
    markers,
    start=1
):

    print(
        f"Canal {i} -> {marker}"
    )

print()


# ============================================================
# VÉRIFICATION DES AUTRES CZI
# ============================================================

print("=" * 60)
print("VÉRIFICATION DES FICHIERS")
print("=" * 60)

print()


valid_czi_files = []


for czi_path in czi_files:

    try:

        czi_test = CziFile(
            str(czi_path)
        )

        dims_test = czi_test.get_dims_shape()

        first_series_test = dims_test[0]

        if "C" not in first_series_test:

            print(
                f"[ERREUR] {czi_path.name} : axe C absent."
            )

            continue


        n_channels_test = first_series_test["C"][1]


        if n_channels_test != n_channels:

            print(
                f"[ERREUR] {czi_path.name} : "
                f"{n_channels_test} canaux détectés "
                f"(attendu : {n_channels})."
            )

            continue


        print(
            f"[OK] {czi_path.name} : "
            f"{n_channels_test} canaux"
        )

        valid_czi_files.append(
            czi_path
        )


    except Exception as error:

        print(
            f"[ERREUR] {czi_path.name} : {error}"
        )


print()


if len(valid_czi_files) == 0:

    messagebox.showerror(
        "Aucun fichier valide",
        "Aucun fichier CZI ne peut être traité."
    )

    root.destroy()

    raise SystemExit


# ============================================================
# FONCTION DE LECTURE D'UN CANAL
# ============================================================

def read_channel(czi, channel_index):
    """
    Lit un canal donné dans un fichier CZI.

    Parameters
    ----------
    czi : CziFile
        Fichier CZI ouvert.

    channel_index : int
        Index du canal, commençant à 0.

    Returns
    -------
    numpy.ndarray
        Image du canal.
    """

    # Lecture du canal.
    #
    # Le format renvoyé par aicspylibczi peut contenir
    # des dimensions supplémentaires (S, T, Z, etc.).

    image, shape = czi.read_image(
        C=channel_index
    )

    image = np.asarray(
        image
    )


    # Suppression des dimensions de taille 1.

    image = np.squeeze(
        image
    )


    return image


# ============================================================
# TRAITEMENT DES FICHIERS
# ============================================================

print()
print("=" * 60)
print("DÉBUT DU TRAITEMENT")
print("=" * 60)
print()


processed_files = 0
failed_files = []


for file_index, czi_path in enumerate(
    valid_czi_files,
    start=1
):

    print()
    print("-" * 60)
    print(
        f"FICHIER {file_index}/{len(valid_czi_files)}"
    )
    print("-" * 60)

    print(
        czi_path.name
    )


    try:

        # ----------------------------------------------------
        # OUVERTURE DU CZI
        # ----------------------------------------------------

        czi = CziFile(
            str(czi_path)
        )


        # ----------------------------------------------------
        # DOSSIER DE SORTIE
        # ----------------------------------------------------

        output_dir = (
            input_dir.parent
            / "images_tiff"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        print()
        print(
            f"Dossier de sortie : {output_dir}"
        )


        # ----------------------------------------------------
        # EXTRACTION DES CANAUX
        # ----------------------------------------------------

        for channel_index, marker in enumerate(
            markers
        ):

            print()
            print(
                f"  Canal {channel_index + 1}/{n_channels} "
                f"-> {marker}"
            )


            # Lecture

            image = read_channel(
                czi,
                channel_index
            )


            print(
                f"    Dimensions : {image.shape}"
            )

            print(
                f"    Type : {image.dtype}"
            )


            # ------------------------------------------------
            # NOM DU TIFF
            # ------------------------------------------------

            output_name = (
                f"{czi_path.stem}_{marker}.tif"
            )

            output_path = (
                output_dir
                / output_name
            )


            # ------------------------------------------------
            # ÉCRITURE TIFF
            # ------------------------------------------------

            tifffile.imwrite(
                output_path,
                image
            )


            print(
                f"    -> {output_path.name}"
            )


        processed_files += 1


        print()
        print(
            "[OK] Fichier traité avec succès."
        )


    except Exception as error:

        print()
        print(
            "[ERREUR]"
        )

        print(
            error
        )


        failed_files.append(
            (
                czi_path.name,
                str(error)
            )
        )


# ============================================================
# FIN DU TRAITEMENT
# ============================================================

print()
print()
print("=" * 60)
print("TRAITEMENT TERMINÉ")
print("=" * 60)

print()

print(
    f"Fichiers traités avec succès : "
    f"{processed_files}/{len(valid_czi_files)}"
)


if failed_files:

    print()
    print(
        "Fichiers en erreur :"
    )

    for filename, error in failed_files:

        print()
        print(
            f"  {filename}"
        )

        print(
            f"    {error}"
        )


print()


# ============================================================
# MESSAGE FINAL
# ============================================================

if failed_files:

    messagebox.showwarning(
        "Traitement terminé",
        (
            f"{processed_files} fichier(s) traité(s).\n"
            f"{len(failed_files)} fichier(s) en erreur."
        )
    )

else:

    messagebox.showinfo(
        "Traitement terminé",
        (
            f"{processed_files} fichier(s) CZI ont été "
            "traités avec succès."
        )
    )


# ============================================================
# FERMETURE TKINTER
# ============================================================

root.destroy()

