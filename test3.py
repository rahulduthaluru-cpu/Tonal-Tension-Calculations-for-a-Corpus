import os
import warnings
import matplotlib.pyplot as plt

import partitura
from partitura.musicanalysis import (
    estimate_tonaltension,
    estimate_key,
    estimate_spelling
)

import numpy as np
from numpy.lib import recfunctions as rfn
from partitura.utils import key_name_to_fifths_mode, key_mode_to_int
import warnings

warnings.filterwarnings(
    "ignore",
    message=".*Returning empty symbolic duration.*"
)

# ---------------------------
# COMPUTE TENSION FOR A CORPUS
# ---------------------------
def compute_corpus_tension(folder_path):

    all_momentum = []
    all_diameter = []
    all_strain = []

    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return all_momentum, all_diameter, all_strain

    midi_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith((".mid", ".midi"))
    ]

    print(f"\nProcessing {folder_path}")
    print(f"Files found: {len(midi_files)}")

    for fn in midi_files:

        full_path = os.path.join(folder_path, fn)

        try:
            # ---------------------------
            # LOAD FULL SCORE
            # ---------------------------
            score = partitura.load_score(full_path)

            # Use ALL notes from the score
            na = score.note_array()

            # ---------------------------
            # ADD PITCH SPELLING
            # ---------------------------
            needed_spelling = {"step", "alter", "octave"}

            if not needed_spelling.issubset(set(na.dtype.names)):

                spelling = estimate_spelling(score)

                for field in ["step", "alter", "octave"]:

                    if field not in na.dtype.names:

                        na = rfn.append_fields(
                            na,
                            field,
                            spelling[field],
                            usemask=False,
                            asrecarray=False,
                        )

            # ---------------------------
            # KS KEY ESTIMATION
            # ---------------------------
            key_name = estimate_key(score, method="krumhansl")

            fifths, mode = key_name_to_fifths_mode(key_name)

            # Add KS fifths
            if "ks_fifths" not in na.dtype.names:

                na = rfn.append_fields(
                    na,
                    "ks_fifths",
                    np.full(len(na), fifths, dtype=np.int32),
                    usemask=False,
                    asrecarray=False,
                )

            # Add KS mode
            if "ks_mode" not in na.dtype.names:

                na = rfn.append_fields(
                    na,
                    "ks_mode",
                    np.full(len(na), key_mode_to_int(mode), dtype=np.int32),
                    usemask=False,
                    asrecarray=False,
                )

            # ---------------------------
            # TONAL TENSION
            # ---------------------------
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                tension = estimate_tonaltension(
                    na,
                    ws=2.0
                )

            # ---------------------------
            # STORE RESULTS
            # ---------------------------
            all_momentum.extend(tension["cloud_momentum"])
            all_diameter.extend(tension["cloud_diameter"])
            all_strain.extend(tension["tensile_strain"])

            print(f"Processed: {fn} | Key: {key_name}")

        except Exception as e:
            print(f"Skipping {fn}: {e}")

    return all_momentum, all_diameter, all_strain


# ---------------------------
# PATHS
# ---------------------------
base_path = r"C:\Users\badsa\PycharmProjects\Tonal_Tension\midi_files"

jazz_path = os.path.join(base_path, "Jazz Corpus")
classical_path = os.path.join(base_path, "Classical Corpus")
rock_path = os.path.join(base_path, "Rock Corpus")
pop_path = os.path.join(base_path, "Pop Corpus")


# ---------------------------
# COMPUTE ALL GENRES
# ---------------------------
jazz_m, jazz_d, jazz_s = compute_corpus_tension(jazz_path)

classical_m, classical_d, classical_s = compute_corpus_tension(classical_path)

rock_m, rock_d, rock_s = compute_corpus_tension(rock_path)

pop_m, pop_d, pop_s = compute_corpus_tension(pop_path)


# ---------------------------
# FILTER NON-EMPTY GENRES
# ---------------------------
data_m = []
data_d = []
data_s = []

labels = []

if len(classical_m) > 0:
    data_m.append(classical_m)
    data_d.append(classical_d)
    data_s.append(classical_s)
    labels.append("Classical")

if len(jazz_m) > 0:
    data_m.append(jazz_m)
    data_d.append(jazz_d)
    data_s.append(jazz_s)
    labels.append("Jazz")

if len(rock_m) > 0:
    data_m.append(rock_m)
    data_d.append(rock_d)
    data_s.append(rock_s)
    labels.append("Rock")

if len(pop_m) > 0:
    data_m.append(pop_m)
    data_d.append(pop_d)
    data_s.append(pop_s)
    labels.append("Pop")


# ---------------------------
# VIOLIN PLOTS
# ---------------------------
if len(labels) == 0:

    print("No data available to plot.")

else:

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Calculate y-limits for annotation placement
    momentum_top = max(np.max(d) for d in data_m)
    diameter_top = max(np.max(d) for d in data_d)
    strain_top = max(np.max(d) for d in data_s)

    # ---------------------------
    # CLOUD MOMENTUM
    # ---------------------------
    axes[0].violinplot(
        data_m,
        showmeans=True,
        showmedians=True
    )

    axes[0].set_title("Cloud Momentum")
    axes[0].set_xticks(range(1, len(labels) + 1))
    axes[0].set_xticklabels(labels)
    axes[0].set_ylabel("Value")

    for i, d in enumerate(data_m, start=1):
        mean = np.mean(d)
        median = np.median(d)
        maximum = np.max(d)

        axes[0].text(
            i,
            momentum_top * 0.97,
            f"μ={mean:.3f}\nM={median:.3f}\nmax={maximum:.3f}",
            ha="center",
            va="top",
            fontsize=8
        )

    # ---------------------------
    # CLOUD DIAMETER
    # ---------------------------
    axes[1].violinplot(
        data_d,
        showmeans=True,
        showmedians=True
    )

    axes[1].set_title("Cloud Diameter")
    axes[1].set_xticks(range(1, len(labels) + 1))
    axes[1].set_xticklabels(labels)

    for i, d in enumerate(data_d, start=1):
        mean = np.mean(d)
        median = np.median(d)
        maximum = np.max(d)

        axes[1].text(
            i,
            diameter_top * 0.97,
            f"μ={mean:.3f}\nM={median:.3f}\nmax={maximum:.3f}",
            ha="center",
            va="top",
            fontsize=8
        )

    # ---------------------------
    # TENSILE STRAIN
    # ---------------------------
    axes[2].violinplot(
        data_s,
        showmeans=True,
        showmedians=True
    )

    axes[2].set_title("Tensile Strain")
    axes[2].set_xticks(range(1, len(labels) + 1))
    axes[2].set_xticklabels(labels)

    for i, d in enumerate(data_s, start=1):
        mean = np.mean(d)
        median = np.median(d)
        maximum = np.max(d)

        axes[2].text(
            i,
            strain_top * 0.97,
            f"μ={mean:.3f}\nM={median:.3f}\nmax={maximum:.3f}",
            ha="center",
            va="top",
            fontsize=8
        )

    # ---------------------------
    # GRID
    # ---------------------------
    for ax in axes:
        ax.grid(True, axis="y", alpha=0.3)

    plt.suptitle("Tonal Tension Across Musical Genres")
    plt.tight_layout()
    plt.show()

# =====================================================
# ZOOMED VIOLIN PLOTS
# =====================================================

# Use the 95th percentile to remove extreme outliers
momentum_lim = np.percentile(np.concatenate(data_m), 90)
diameter_lim = np.percentile(np.concatenate(data_d), 90)
strain_lim = np.percentile(np.concatenate(data_s), 90)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# =====================================================
# CLOUD MOMENTUM
# =====================================================

axes[0].violinplot(
    data_m,
    showmeans=True,
    showmedians=True
)

axes[0].set_title("Cloud Momentum (Zoomed)")
axes[0].set_xticks(range(1, len(labels) + 1))
axes[0].set_xticklabels(labels)
axes[0].set_ylabel("Value")
axes[0].set_ylim(0, momentum_lim)

for i, d in enumerate(data_m, start=1):

    mean = np.mean(d)
    median = np.median(d)
    maximum = np.max(d)

    axes[0].text(
        i,
        momentum_lim * 0.97,
        f"μ={mean:.3f}\nM={median:.3f}\nmax={maximum:.3f}",
        ha="center",
        va="top",
        fontsize=8
    )

# =====================================================
# CLOUD DIAMETER
# =====================================================

axes[1].violinplot(
    data_d,
    showmeans=True,
    showmedians=True
)

axes[1].set_title("Cloud Diameter (Zoomed)")
axes[1].set_xticks(range(1, len(labels) + 1))
axes[1].set_xticklabels(labels)
axes[1].set_ylim(0, diameter_lim)

for i, d in enumerate(data_d, start=1):

    mean = np.mean(d)
    median = np.median(d)
    maximum = np.max(d)

    axes[1].text(
        i,
        diameter_lim * 0.97,
        f"μ={mean:.3f}\nM={median:.3f}\nmax={maximum:.3f}",
        ha="center",
        va="top",
        fontsize=8
    )

# =====================================================
# TENSILE STRAIN
# =====================================================

axes[2].violinplot(
    data_s,
    showmeans=True,
    showmedians=True
)

axes[2].set_title("Tensile Strain (Zoomed)")
axes[2].set_xticks(range(1, len(labels) + 1))
axes[2].set_xticklabels(labels)
axes[2].set_ylim(0, strain_lim)

for i, d in enumerate(data_s, start=1):

    mean = np.mean(d)
    median = np.median(d)
    maximum = np.max(d)

    axes[2].text(
        i,
        strain_lim * 0.97,
        f"μ={mean:.3f}\nM={median:.3f}\nmax={maximum:.3f}",
        ha="center",
        va="top",
        fontsize=8
    )

# =====================================================
# GRID
# =====================================================

for ax in axes:
    ax.grid(True, axis="y", alpha=0.3)

plt.suptitle("Zoomed Tonal Tension Distributions")

plt.tight_layout()

plt.show()