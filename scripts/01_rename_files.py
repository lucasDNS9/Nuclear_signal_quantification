# -*- coding: utf-8 -*-

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


# ============================================================
# FONCTION DE RENOMMAGE
# ============================================================

def renommer_fichiers(dossier, ancien_texte, nouveau_texte):

    dossier = Path(dossier)

    fichiers_renommes = 0

    for fichier in dossier.iterdir():

        if not fichier.is_file():
            continue

        ancien_nom = fichier.name

        if ancien_texte not in ancien_nom:
            continue

        nouveau_nom = ancien_nom.replace(
            ancien_texte,
            nouveau_texte
        )

        nouveau_chemin = fichier.with_name(nouveau_nom)

        # Ne pas écraser un fichier existant
        if nouveau_chemin.exists():
            print(f"Fichier déjà existant : {nouveau_nom}")
            continue

        fichier.rename(nouveau_chemin)

        print(f"{ancien_nom}  →  {nouveau_nom}")

        fichiers_renommes += 1

    return fichiers_renommes


# ============================================================
# FENÊTRE DE RENOMMAGE
# ============================================================

def afficher_fenetre_renommage(dossier):

    fenetre = tk.Toplevel(root)

    fenetre.title("Renommer les fichiers")
    fenetre.geometry("450x220")
    fenetre.resizable(False, False)

    # Texte à remplacer
    tk.Label(
        fenetre,
        text="Remplacer :"
    ).pack(pady=(20, 5))

    champ_ancien = tk.Entry(
        fenetre,
        width=45
    )
    champ_ancien.pack()

    # Nouveau texte
    tk.Label(
        fenetre,
        text="Par :"
    ).pack(pady=(15, 5))

    champ_nouveau = tk.Entry(
        fenetre,
        width=45
    )
    champ_nouveau.pack()

    # --------------------------------------------------------
    # Fonction appelée lorsque l'on clique sur le bouton
    # --------------------------------------------------------

    def lancer_renommage():

        ancien_texte = champ_ancien.get()
        nouveau_texte = champ_nouveau.get()

        if ancien_texte == "":
            messagebox.showwarning(
                "Attention",
                "Veuillez entrer le texte à remplacer.",
                parent=fenetre
            )
            return

        nombre = renommer_fichiers(
            dossier,
            ancien_texte,
            nouveau_texte
        )

        messagebox.showinfo(
            "Terminé",
            f"{nombre} fichier(s) renommé(s).",
            parent=fenetre
        )

        # Ferme la fenêtre de renommage
        fenetre.destroy()

        # Ferme complètement Tkinter
        root.destroy()

    # Bouton
    tk.Button(
        fenetre,
        text="Renommer les fichiers",
        command=lancer_renommage,
        width=25
    ).pack(pady=25)

    # Empêche d'interagir avec une éventuelle autre fenêtre
    fenetre.grab_set()

    # Place le curseur directement dans le premier champ
    champ_ancien.focus_set()

    # Fermer proprement le programme avec la croix X
    def fermer_fenetre():
        fenetre.destroy()
        root.destroy()

    fenetre.protocol("WM_DELETE_WINDOW", fermer_fenetre)


# ============================================================
# CHOIX DU DOSSIER
# ============================================================

def choisir_dossier():

    dossier = filedialog.askdirectory(
        title="Sélectionner le dossier contenant les fichiers",
        parent=root
    )

    if not dossier:
        root.destroy()
        return

    afficher_fenetre_renommage(dossier)


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

root = tk.Tk()

# On cache la fenêtre principale
root.withdraw()

# Choix du dossier
choisir_dossier()

# Boucle Tkinter nécessaire pour maintenir
# la fenêtre "Renommer les fichiers" interactive
root.mainloop()