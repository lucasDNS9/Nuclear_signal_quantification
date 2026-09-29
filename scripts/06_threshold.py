
import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd
import numpy as np

from scipy.stats import gaussian_kde

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# 1. SÉLECTION DU FICHIER CSV
# ============================================================

root = tk.Tk()
root.withdraw()

csv_file = filedialog.askopenfilename(
    title="Sélectionner le fichier de quantification",
    filetypes=[
        ("CSV files", "*.csv"),
        ("All files", "*.*")
    ]
)

if not csv_file:
    root.destroy()
    raise SystemExit


# ============================================================
# 2. LECTURE DU CSV
# ============================================================

df = pd.read_csv(csv_file)


# ============================================================
# 3. RÉCUPÉRATION DES MARQUEURS
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

print("Marqueurs détectés :", markers)


# ============================================================
# 4. FENÊTRE PRINCIPALE
# ============================================================

root.deiconify()

root.title(
    "Sélection des seuils d'intensité"
)

root.geometry(
    "1000x1200"
)


# ============================================================
# 5. STOCKAGE
# ============================================================

thresholds = {}

plot_data = {}


# ============================================================
# 6. ZONE SCROLLABLE
# ============================================================

canvas_container = tk.Frame(root)

canvas_container.pack(
    fill=tk.BOTH,
    expand=True
)


# Canvas Tkinter
scroll_canvas = tk.Canvas(
    canvas_container,
    highlightthickness=0
)

scrollbar = tk.Scrollbar(
    canvas_container,
    orient="vertical",
    command=scroll_canvas.yview
)

scrollable_frame = tk.Frame(
    scroll_canvas
)


# ------------------------------------------------------------
# Mise à jour de la zone scrollable
# ------------------------------------------------------------

scrollable_frame.bind(
    "<Configure>",
    lambda event: scroll_canvas.configure(
        scrollregion=scroll_canvas.bbox("all")
    )
)


window_id = scroll_canvas.create_window(
    (0, 0),
    window=scrollable_frame,
    anchor="nw"
)


scroll_canvas.configure(
    yscrollcommand=scrollbar.set
)


scroll_canvas.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


# ============================================================
# 7. SCROLL AVEC LA MOLETTE
# ============================================================

def mousewheel(event):

    # Windows / Linux
    if event.delta:

        scroll_canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )


# Souris sur le canvas
scroll_canvas.bind(
    "<MouseWheel>",
    mousewheel
)

# Souris sur la zone des graphiques
scrollable_frame.bind(
    "<MouseWheel>",
    mousewheel
)


# ============================================================
# 8. CRÉATION DES GRAPHIQUES
# ============================================================

for marker in markers:

    column = f"mean_{marker}"

    values = (
        df[column]
        .dropna()
        .astype(float)
        .values
    )

    if len(values) < 10:
        continue


    # ========================================================
    # KDE
    # ========================================================

    kde = gaussian_kde(values)

    x = np.linspace(
        values.min(),
        values.max(),
        1000
    )

    y = kde(x)


    # ========================================================
    # FRAME
    # ========================================================

    marker_frame = tk.Frame(
        scrollable_frame,
        bd=1,
        relief=tk.SOLID
    )

    marker_frame.pack(
        fill=tk.X,
        padx=10,
        pady=10
    )


    # ========================================================
    # FIGURE
    # ========================================================

    fig = Figure(
        figsize=(9, 4),
        dpi=100
    )

    ax = fig.add_subplot(111)


    # ========================================================
    # COURBE KDE
    # ========================================================

    ax.plot(
        x,
        y,
        linewidth=1.2
    )


    # ========================================================
    # AXES
    # ========================================================

    ax.set_xlabel(
        f"Mean intensity {marker}"
    )

    ax.set_ylabel(
        "Density"
    )

    ax.set_title(
        marker
    )


    # --------------------------------------------------------
    # IMPORTANT :
    #
    # On garde un peu de marge en X pour ne pas couper
    # la courbe.
    # --------------------------------------------------------

    ax.margins(y=0)


    # --------------------------------------------------------
    # La KDE touche l'axe X
    # --------------------------------------------------------

    ax.set_ylim(
        bottom=0
    )


    # ========================================================
    # SEUIL INITIAL
    # ========================================================

    threshold = np.median(values)

    thresholds[marker] = threshold


    # ========================================================
    # LIGNE DRAGGABLE
    # ========================================================

    line = ax.axvline(
        threshold,
        linestyle="-",
        linewidth=1,
        color="red"
    )


    # ========================================================
    # TEXTE SEUIL
    # ========================================================

    text = ax.text(
        threshold,
        y.max(),
        f"{threshold:.2f}",
        rotation=0,
        verticalalignment="top",
        horizontalalignment="right"
    )


    # ========================================================
    # TEXTE POURCENTAGES
    # ========================================================

    percentage_label = tk.Label(
        marker_frame,
        text="",
        font=("Arial", 12)
    )

    percentage_label.pack(
        pady=(0, 8)
    )


    # ========================================================
    # STOCKAGE
    # ========================================================

    plot_data[marker] = {
        "fig": fig,
        "ax": ax,
        "line": line,
        "text": text,
        "values": values,
        "canvas": None,
        "dragging": False,
        "percentage_label": percentage_label
    }


    # ========================================================
    # CANVAS MATPLOTLIB
    # ========================================================

    mpl_canvas = FigureCanvasTkAgg(
        fig,
        master=marker_frame
    )

    mpl_canvas.draw()

    mpl_canvas.get_tk_widget().pack(
        fill=tk.X,
        expand=True
    )


    plot_data[marker]["canvas"] = mpl_canvas


    # ========================================================
    # SCROLL SUR LE GRAPHIQUE
    # ========================================================

    mpl_widget = mpl_canvas.get_tk_widget()

    mpl_widget.bind(
        "<MouseWheel>",
        mousewheel
    )


    # ========================================================
    # MISE À JOUR DES POURCENTAGES
    # ========================================================

    def update_threshold(
        threshold,
        marker=marker
    ):

        data = plot_data[marker]

        values = data["values"]

        positive = np.sum(
            values >= threshold
        )

        negative = np.sum(
            values < threshold
        )

        total = len(values)

        positive_percent = (
            positive / total * 100
        )

        negative_percent = (
            negative / total * 100
        )

        data["percentage_label"].config(
            text=(
                f"Négatif : "
                f"{negative_percent:.1f}% ({negative}/{total})"
                f"    |    "
                f"Positif : "
                f"{positive_percent:.1f}% ({positive}/{total})"
            )
        )


    # ========================================================
    # INITIALISATION
    # ========================================================

    update_threshold(
        threshold
    )


    # ========================================================
    # CLIQUE
    # ========================================================

    def on_press(
        event,
        marker=marker
    ):

        data = plot_data[marker]

        ax = data["ax"]

        if event.inaxes != ax:
            return

        if event.xdata is None:
            return


        current_threshold = (
            data["line"].get_xdata()[0]
        )


        x_range = (
            ax.get_xlim()[1]
            - ax.get_xlim()[0]
        )


        tolerance = (
            x_range * 0.02
        )


        if abs(
            event.xdata - current_threshold
        ) < tolerance:

            data["dragging"] = True


    # ========================================================
    # DÉPLACEMENT
    # ========================================================

    def on_motion(
        event,
        marker=marker
    ):

        data = plot_data[marker]

        if not data["dragging"]:
            return

        ax = data["ax"]

        if event.inaxes != ax:
            return

        if event.xdata is None:
            return


        values = data["values"]


        threshold = event.xdata


        # ----------------------------------------------------
        # Limites
        # ----------------------------------------------------

        threshold = max(
            values.min(),
            min(
                values.max(),
                threshold
            )
        )


        # ----------------------------------------------------
        # Ligne
        # ----------------------------------------------------

        data["line"].set_xdata(
            [threshold, threshold]
        )


        # ----------------------------------------------------
        # Texte
        # ----------------------------------------------------

        data["text"].set_x(
            threshold
        )

        data["text"].set_text(
            f"{threshold:.2f}"
        )


        # ----------------------------------------------------
        # Pourcentages
        # ----------------------------------------------------

        update_threshold(
            threshold,
            marker
        )


        # ----------------------------------------------------
        # Sauvegarde
        # ----------------------------------------------------

        thresholds[marker] = threshold


        # ----------------------------------------------------
        # Redessiner
        # ----------------------------------------------------

        data["canvas"].draw_idle()


    # ========================================================
    # RELÂCHEMENT
    # ========================================================

    def on_release(
        event,
        marker=marker
    ):

        data = plot_data[marker]

        if data["dragging"]:

            threshold = (
                data["line"].get_xdata()[0]
            )

            thresholds[marker] = threshold

            print(
                f"{marker} → seuil = {threshold:.3f}"
            )

        data["dragging"] = False


    # ========================================================
    # ÉVÉNEMENTS
    # ========================================================

    mpl_canvas.mpl_connect(
        "button_press_event",
        on_press
    )

    mpl_canvas.mpl_connect(
        "motion_notify_event",
        on_motion
    )

    mpl_canvas.mpl_connect(
        "button_release_event",
        on_release
    )


# ============================================================
# 9. BOUTON D'ENREGISTREMENT
# ============================================================

def save_thresholds():

    output_file = filedialog.asksaveasfilename(
        title="Enregistrer les seuils",
        defaultextension=".csv",
        filetypes=[
            ("CSV files", "*.csv")
        ]
    )

    if not output_file:
        return


    threshold_df = pd.DataFrame({
        "Marker": list(thresholds.keys()),
        "Threshold": list(thresholds.values())
    })


    threshold_df.to_csv(
        output_file,
        index=False
    )


    messagebox.showinfo(
        "Seuils enregistrés",
        "Les seuils ont été enregistrés."
    )


# ============================================================
# 10. BOUTON
# ============================================================

button = tk.Button(
    root,
    text="Enregistrer les seuils",
    command=save_thresholds,
    font=("Arial", 12),
    padx=20,
    pady=8
)

button.pack(
    pady=10
)


# ============================================================
# 11. LANCEMENT
# ============================================================

root.mainloop()