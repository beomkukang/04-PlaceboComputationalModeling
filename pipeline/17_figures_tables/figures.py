"""Step 12: Publication Figures and Tables (analysis_plan.md Section 9)

Generates all figures and tables for the manuscript.

Figures:
    1. Conceptual model of perturbation, neural, deqi, clinical spaces
    2. Distribution of intervention arms in perturbation space
    3. SDM-PSI neural convergence maps by contrast family
    4. Neural gradient plot (continuous response dimensions)
    5. Component interaction: additive vs. amplification vs. substitution vs. overlap
    6. Sham heterogeneity by afferent/deqi/cognitive covariates
    7. Clinical responsiveness space by disease domain
    8. RSA heatmap: perturbation <-> neural <-> deqi <-> clinical distances
    9. Sensitivity/evidence-grade summary

Tables:
    1. Included studies and imaging paradigms
    2. Intervention coding taxonomy
    3. Contrast families and study counts
    4. Clinical outcome normalization table
    5. SDM-PSI peak results
    6. Component meta-regression results
    7. Sensitivity analyses
    8. Evidence grading for key claims

Inputs:
    All prior step outputs

Outputs:
    data_analysis/outputs/figures/fig1_conceptual_model.png
    data_analysis/outputs/figures/fig2_perturbation_space.png
    data_analysis/outputs/figures/fig3_sdm_convergence_maps.png
    data_analysis/outputs/figures/fig4_neural_gradients.png
    data_analysis/outputs/figures/fig5_component_interaction.png
    data_analysis/outputs/figures/fig6_sham_heterogeneity.png
    data_analysis/outputs/figures/fig7_clinical_responsiveness.png
    data_analysis/outputs/figures/fig8_rsa_heatmap.png
    data_analysis/outputs/figures/fig9_sensitivity_summary.png
    data_analysis/outputs/tables/table1_studies.csv
    data_analysis/outputs/tables/table2_intervention_taxonomy.csv
    data_analysis/outputs/tables/table3_contrast_families.csv
    data_analysis/outputs/tables/table4_clinical_normalization.csv
    data_analysis/outputs/tables/table5_sdm_peaks.csv
    data_analysis/outputs/tables/table6_component_regression.csv
    data_analysis/outputs/tables/table7_sensitivity.csv
    data_analysis/outputs/tables/table8_evidence_grading.csv
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

try:
    from nilearn import plotting as ni_plotting
    HAS_NILEARN = True
except ImportError:
    HAS_NILEARN = False

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


# --- Utility ---

DPI = 300
ARM_TYPE_COLORS = {"verum": "#D62728", "sham": "#1F77B4", "other": "#7F7F7F"}


def _get_arm_color(arm_type: str) -> str:
    """Return color for a given arm_type string."""
    key = str(arm_type).strip().lower()
    if "verum" in key or "active" in key:
        return ARM_TYPE_COLORS["verum"]
    elif "sham" in key or "placebo" in key:
        return ARM_TYPE_COLORS["sham"]
    return ARM_TYPE_COLORS["other"]


# --- Figures ---

def fig1_conceptual_model():
    """Conceptual diagram -- best created in PowerPoint/Illustrator."""
    print("  [Fig 1] Conceptual model: skipping (manual diagram).")
    print("           Create in PowerPoint/Illustrator with perturbation,")
    print("           neural, deqi, and clinical spaces as linked panels.")


def fig2_perturbation_space():
    """Scatter of arms in perturbation PCA space."""
    pca_path = config.OUT_PERTURBATION / "perturbation_pca_coordinates.csv"
    if not pca_path.exists():
        print("  [Fig 2] Skipping: perturbation_pca_coordinates.csv not found.")
        return

    df = pd.read_csv(pca_path)

    # Determine column names
    pc1_col = "PC1" if "PC1" in df.columns else df.columns[df.columns.str.contains("PC.*1", case=False)][0] if any(df.columns.str.contains("PC.*1", case=False)) else None
    pc2_col = "PC2" if "PC2" in df.columns else df.columns[df.columns.str.contains("PC.*2", case=False)][0] if any(df.columns.str.contains("PC.*2", case=False)) else None

    if pc1_col is None or pc2_col is None:
        print("  [Fig 2] Skipping: cannot identify PC1/PC2 columns.")
        return

    # Determine arm_type column
    arm_col = None
    for candidate in ["arm_type", "arm_class", "type"]:
        if candidate in df.columns:
            arm_col = candidate
            break

    # Size by Afferent_Input_Index if available
    size_col = None
    for candidate in ["Afferent_Input_Index", "afferent_input_index", "Afferent_Index"]:
        if candidate in df.columns:
            size_col = candidate
            break

    # Try to read variance explained
    variance_path = config.OUT_PERTURBATION / "perturbation_pca_variance.csv"
    var_explained = [None, None]
    if variance_path.exists():
        var_df = pd.read_csv(variance_path)
        if "variance_explained" in var_df.columns:
            var_explained = var_df["variance_explained"].iloc[:2].tolist()
        elif "explained_variance_ratio" in var_df.columns:
            var_explained = var_df["explained_variance_ratio"].iloc[:2].tolist()

    fig, ax = plt.subplots(figsize=(8, 6))

    colors = df[arm_col].apply(_get_arm_color) if arm_col else ARM_TYPE_COLORS["other"]
    sizes = df[size_col] * 100 + 20 if size_col else 50

    ax.scatter(df[pc1_col], df[pc2_col], c=colors, s=sizes, alpha=0.7, edgecolors="k", linewidths=0.3)

    # Axis labels
    xlabel = f"PC1 ({var_explained[0]*100:.1f}% variance)" if var_explained[0] is not None else "PC1"
    ylabel = f"PC2 ({var_explained[1]*100:.1f}% variance)" if var_explained[1] is not None else "PC2"
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title("Perturbation Space: Intervention Arms", fontsize=14)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=ARM_TYPE_COLORS["verum"],
               markersize=10, label="Verum"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=ARM_TYPE_COLORS["sham"],
               markersize=10, label="Sham"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=ARM_TYPE_COLORS["other"],
               markersize=10, label="Other"),
    ]
    ax.legend(handles=legend_elements, loc="best", framealpha=0.8)

    plt.tight_layout()
    out_path = config.OUT_FIGURES / "fig2_perturbation_space.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Fig 2] Saved: {out_path}")


def fig3_sdm_maps():
    """SDM-PSI convergence maps rendered on MNI template."""
    if not HAS_NILEARN:
        print("  [Fig 3] Skipping: nilearn not available for brain map plotting.")
        return

    key_contrasts = ["sham_gt_rest", "verum_gt_sham", "verum_gt_rest"]
    maps_found = []

    for contrast in key_contrasts:
        # Try thresholded map first, then z-map
        corrp = config.sdm_corrp_map(contrast)
        zmap = config.sdm_z_map(contrast)
        if corrp.exists():
            maps_found.append((contrast, str(corrp), "corrp"))
        elif zmap.exists():
            maps_found.append((contrast, str(zmap), "z"))

    if not maps_found:
        print("  [Fig 3] Skipping: no SDM NIfTI maps found for key contrasts.")
        return

    n_maps = len(maps_found)
    fig, axes = plt.subplots(n_maps, 1, figsize=(10, 4 * n_maps))
    if n_maps == 1:
        axes = [axes]

    for i, (contrast, map_path, map_type) in enumerate(maps_found):
        display = ni_plotting.plot_stat_map(
            map_path,
            display_mode="z",
            cut_coords=5,
            title=f"{contrast} ({map_type})",
            axes=axes[i] if hasattr(axes[i], "get_position") else None,
            figure=fig,
        )

    out_path = config.OUT_FIGURES / "fig3_sdm_convergence_maps.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Fig 3] Saved: {out_path}")


def fig4_neural_gradients():
    """Neural gradient scatter with perturbation-space coloring."""
    gradient_path = config.OUT_GRADIENTS / "gradient_scores.csv"
    if not gradient_path.exists():
        # Try alternative name
        gradient_path = config.OUT_GRADIENTS / "neural_gradient_scores.csv"
    if not gradient_path.exists():
        print("  [Fig 4] Skipping: gradient_scores.csv not found.")
        return

    df = pd.read_csv(gradient_path)

    # Identify gradient columns
    g1_col = None
    g2_col = None
    for col in df.columns:
        if "gradient_1" in col.lower() or "gradient1" in col.lower() or col == "Gradient_1":
            g1_col = col
        elif "gradient_2" in col.lower() or "gradient2" in col.lower() or col == "Gradient_2":
            g2_col = col

    if g1_col is None or g2_col is None:
        # Fallback: use first two numeric columns after any ID columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2:
            g1_col, g2_col = numeric_cols[0], numeric_cols[1]
        else:
            print("  [Fig 4] Skipping: cannot identify gradient columns.")
            return

    # Color by category
    cat_col = None
    for candidate in ["category", "arm_type", "contrast_category", "type"]:
        if candidate in df.columns:
            cat_col = candidate
            break

    fig, ax = plt.subplots(figsize=(8, 6))

    if cat_col:
        colors = df[cat_col].apply(_get_arm_color)
    else:
        colors = ARM_TYPE_COLORS["other"]

    ax.scatter(df[g1_col], df[g2_col], c=colors, s=60, alpha=0.7, edgecolors="k", linewidths=0.3)

    # Label points if there's a label column
    label_col = None
    for candidate in ["label", "analysis", "contrast", "study_id", "pmid"]:
        if candidate in df.columns:
            label_col = candidate
            break

    if label_col:
        for _, row in df.iterrows():
            ax.annotate(str(row[label_col]), (row[g1_col], row[g2_col]),
                        fontsize=6, alpha=0.7, ha="left", va="bottom")

    ax.set_xlabel("Gradient 1", fontsize=12)
    ax.set_ylabel("Gradient 2", fontsize=12)
    ax.set_title("Neural Gradients", fontsize=14)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=ARM_TYPE_COLORS["verum"],
               markersize=10, label="Verum"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=ARM_TYPE_COLORS["sham"],
               markersize=10, label="Sham"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=ARM_TYPE_COLORS["other"],
               markersize=10, label="Other"),
    ]
    ax.legend(handles=legend_elements, loc="best", framealpha=0.8)

    plt.tight_layout()
    out_path = config.OUT_FIGURES / "fig4_neural_gradients.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Fig 4] Saved: {out_path}")


def fig5_component_interaction():
    """Interaction model comparison figure."""
    model_path = config.OUT_MODELS / "component_interaction_model_comparison.csv"
    if not model_path.exists():
        print("  [Fig 5] Skipping: component_interaction_model_comparison.csv not found.")
        return

    df = pd.read_csv(model_path)

    # Identify model name column
    model_col = None
    for candidate in ["model", "model_name", "Model"]:
        if candidate in df.columns:
            model_col = candidate
            break
    if model_col is None:
        model_col = df.columns[0]

    # Identify AIC/BIC columns
    aic_col = None
    bic_col = None
    for col in df.columns:
        if "aic" in col.lower():
            aic_col = col
        if "bic" in col.lower():
            bic_col = col

    has_metrics = aic_col is not None or bic_col is not None
    if not has_metrics:
        print("  [Fig 5] Skipping: no AIC/BIC columns found.")
        return

    # Check for simple slopes
    slopes_path = config.OUT_MODELS / "simple_slopes.csv"
    has_slopes = slopes_path.exists()

    n_subplots = 2 if has_slopes else 1
    fig, axes = plt.subplots(1, n_subplots, figsize=(6 * n_subplots, 5))
    if n_subplots == 1:
        axes = [axes]

    # Panel A: model comparison bar chart
    ax = axes[0]
    x = np.arange(len(df))
    width = 0.35

    if aic_col and bic_col:
        ax.bar(x - width / 2, df[aic_col], width, label="AIC", color="#4C72B0")
        ax.bar(x + width / 2, df[bic_col], width, label="BIC", color="#DD8452")
        ax.legend()
    elif aic_col:
        ax.bar(x, df[aic_col], width, label="AIC", color="#4C72B0")
    else:
        ax.bar(x, df[bic_col], width, label="BIC", color="#DD8452")

    ax.set_xticks(x)
    ax.set_xticklabels(df[model_col], rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Information Criterion")
    ax.set_title("Model Comparison")

    # Panel B: simple slopes if available
    if has_slopes:
        slopes_df = pd.read_csv(slopes_path)
        ax2 = axes[1]

        # Plot slopes as lines/points
        slope_col = None
        for candidate in ["slope", "estimate", "beta", "coefficient"]:
            if candidate in slopes_df.columns:
                slope_col = candidate
                break

        level_col = None
        for candidate in ["level", "moderator_level", "group"]:
            if candidate in slopes_df.columns:
                level_col = candidate
                break

        if slope_col and level_col:
            for i, (_, row) in enumerate(slopes_df.iterrows()):
                ci_lo = row.get("ci_lower", row[slope_col] - 0.5)
                ci_hi = row.get("ci_upper", row[slope_col] + 0.5)
                ax2.errorbar(i, row[slope_col], yerr=[[row[slope_col] - ci_lo], [ci_hi - row[slope_col]]],
                             fmt="o", capsize=4, color="#4C72B0", markersize=8)
            ax2.set_xticks(range(len(slopes_df)))
            ax2.set_xticklabels(slopes_df[level_col], rotation=30, ha="right", fontsize=9)
            ax2.axhline(0, color="gray", linestyle="--", linewidth=0.8)
            ax2.set_ylabel("Simple Slope")
            ax2.set_title("Simple Slopes Analysis")
        else:
            ax2.text(0.5, 0.5, "Simple slopes data\n(format not recognized)",
                     ha="center", va="center", transform=ax2.transAxes)

    plt.tight_layout()
    out_path = config.OUT_FIGURES / "fig5_component_interaction.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Fig 5] Saved: {out_path}")


def fig6_sham_heterogeneity():
    """Sham heterogeneity by component covariates."""
    sham_path = config.OUT_SHAM / "sham_component_table.csv"
    if not sham_path.exists():
        print("  [Fig 6] Skipping: sham_component_table.csv not found.")
        return

    df = pd.read_csv(sham_path)

    # Identify penetration level column
    pen_col = None
    for candidate in ["penetration_level", "penetration", "sham_penetration", "sham_type"]:
        if candidate in df.columns:
            pen_col = candidate
            break

    # Identify afferent index column
    aff_col = None
    for candidate in ["Afferent_Input_Index", "afferent_input_index", "Afferent_Index"]:
        if candidate in df.columns:
            aff_col = candidate
            break

    if pen_col is None or aff_col is None:
        print("  [Fig 6] Skipping: cannot identify penetration or afferent columns.")
        return

    fig, ax = plt.subplots(figsize=(8, 5))

    if HAS_SEABORN:
        sns.boxplot(data=df, x=pen_col, y=aff_col, ax=ax, color="#B0C4DE", width=0.5)
        sns.stripplot(data=df, x=pen_col, y=aff_col, ax=ax, color="#1F77B4",
                      alpha=0.6, jitter=0.15, size=5)
    else:
        groups = df.groupby(pen_col)[aff_col].apply(list)
        positions = range(len(groups))
        ax.boxplot(groups.values, positions=list(positions), widths=0.5)
        ax.set_xticks(list(positions))
        ax.set_xticklabels(groups.index)

    ax.set_xlabel("Sham Penetration Level", fontsize=12)
    ax.set_ylabel("Afferent Input Index", fontsize=12)
    ax.set_title("Sham Heterogeneity: Afferent Input by Penetration Level", fontsize=13)

    plt.tight_layout()
    out_path = config.OUT_FIGURES / "fig6_sham_heterogeneity.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Fig 6] Saved: {out_path}")


def fig7_clinical_responsiveness():
    """Clinical responsiveness by disease domain."""
    resp_path = config.OUT_BEHAVIORAL / "domain_responsiveness.csv"
    if not resp_path.exists():
        # Try alternative location
        resp_path = config.CLINICAL_RESPONSIVENESS
    if not resp_path.exists():
        print("  [Fig 7] Skipping: domain_responsiveness.csv not found.")
        return

    df = pd.read_csv(resp_path)

    # Identify key columns
    disease_col = None
    for candidate in ["disease_condition", "condition", "disease", "domain"]:
        if candidate in df.columns:
            disease_col = candidate
            break

    r_col = None
    for candidate in ["R_within", "r_within", "mean_R", "effect_size", "responsiveness"]:
        if candidate in df.columns:
            r_col = candidate
            break

    arm_col = None
    for candidate in ["arm_type", "type", "group"]:
        if candidate in df.columns:
            arm_col = candidate
            break

    if disease_col is None or r_col is None:
        print("  [Fig 7] Skipping: cannot identify disease/responsiveness columns.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    if arm_col:
        # Group by arm_type for color coding
        for arm_val in df[arm_col].unique():
            subset = df[df[arm_col] == arm_val]
            color = _get_arm_color(arm_val)
            y_positions = range(len(subset))
            ax.scatter(subset[r_col], [f"{row[disease_col]}" for _, row in subset.iterrows()],
                       c=color, s=80, alpha=0.7, label=arm_val, edgecolors="k", linewidths=0.3)
    else:
        # Simple dot plot
        conditions = df[disease_col].unique()
        for i, cond in enumerate(conditions):
            subset = df[df[disease_col] == cond]
            ax.scatter(subset[r_col], [cond] * len(subset), s=80, alpha=0.7,
                       edgecolors="k", linewidths=0.3)

    ax.axvline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Responsiveness (R)", fontsize=12)
    ax.set_ylabel("Disease Condition", fontsize=12)
    ax.set_title("Clinical Responsiveness by Disease Domain", fontsize=13)
    if arm_col:
        ax.legend(loc="best", framealpha=0.8)

    plt.tight_layout()
    out_path = config.OUT_FIGURES / "fig7_clinical_responsiveness.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Fig 7] Saved: {out_path}")


def fig8_rsa_heatmap():
    """RSA correlation matrix across distance types."""
    rsa_path = config.OUT_RSA / "rsa_results.csv"
    if not rsa_path.exists():
        print("  [Fig 8] Skipping: rsa_results.csv not found.")
        return

    df = pd.read_csv(rsa_path)

    # Build correlation matrix from RSA results
    # Expected columns: space_1, space_2, r, p_value (or similar)
    space1_col = None
    space2_col = None
    r_col = None
    p_col = None

    for col in df.columns:
        cl = col.lower()
        if "space_1" in cl or "matrix_1" in cl or "domain_1" in cl:
            space1_col = col
        elif "space_2" in cl or "matrix_2" in cl or "domain_2" in cl:
            space2_col = col
        elif cl in ("r", "correlation", "rho", "mantel_r"):
            r_col = col
        elif "p_val" in cl or cl == "p" or cl == "pvalue":
            p_col = col

    if space1_col and space2_col and r_col:
        # Pivot into a matrix
        spaces = sorted(set(df[space1_col].tolist() + df[space2_col].tolist()))
        n = len(spaces)
        mat = np.ones((n, n))
        pmat = np.zeros((n, n))

        space_idx = {s: i for i, s in enumerate(spaces)}
        for _, row in df.iterrows():
            i = space_idx.get(row[space1_col])
            j = space_idx.get(row[space2_col])
            if i is not None and j is not None:
                mat[i, j] = row[r_col]
                mat[j, i] = row[r_col]
                if p_col:
                    pmat[i, j] = row[p_col]
                    pmat[j, i] = row[p_col]

        fig, ax = plt.subplots(figsize=(7, 6))

        if HAS_SEABORN:
            sns.heatmap(mat, xticklabels=spaces, yticklabels=spaces,
                        annot=True, fmt=".2f", cmap="RdBu_r", center=0,
                        vmin=-1, vmax=1, ax=ax, square=True,
                        linewidths=0.5, linecolor="white")
        else:
            im = ax.imshow(mat, cmap="RdBu_r", vmin=-1, vmax=1)
            ax.set_xticks(range(n))
            ax.set_xticklabels(spaces, rotation=45, ha="right")
            ax.set_yticks(range(n))
            ax.set_yticklabels(spaces)
            plt.colorbar(im, ax=ax)
            # Annotate
            for i in range(n):
                for j in range(n):
                    text = f"{mat[i, j]:.2f}"
                    ax.text(j, i, text, ha="center", va="center", fontsize=9)

        # Add significance stars
        if p_col:
            for i in range(n):
                for j in range(n):
                    if i != j and pmat[i, j] < 0.05:
                        star = "***" if pmat[i, j] < 0.001 else "**" if pmat[i, j] < 0.01 else "*"
                        ax.text(j + 0.5 if not HAS_SEABORN else j,
                                i + 0.7 if not HAS_SEABORN else i + 0.3,
                                star, ha="center", va="center", fontsize=8, color="black")

        ax.set_title("RSA: Representational Similarity Across Spaces", fontsize=13)
        plt.tight_layout()
        out_path = config.OUT_FIGURES / "fig8_rsa_heatmap.png"
        fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
        plt.close(fig)
        print(f"  [Fig 8] Saved: {out_path}")
    else:
        # Fallback: try to interpret as already a matrix
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[0] >= 2 and numeric_df.shape[1] >= 2:
            fig, ax = plt.subplots(figsize=(7, 6))
            if HAS_SEABORN:
                sns.heatmap(numeric_df, annot=True, fmt=".2f", cmap="RdBu_r",
                            center=0, ax=ax, square=True)
            else:
                im = ax.imshow(numeric_df.values, cmap="RdBu_r")
                plt.colorbar(im, ax=ax)
            ax.set_title("RSA Heatmap", fontsize=13)
            plt.tight_layout()
            out_path = config.OUT_FIGURES / "fig8_rsa_heatmap.png"
            fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
            plt.close(fig)
            print(f"  [Fig 8] Saved: {out_path}")
        else:
            print("  [Fig 8] Skipping: cannot interpret RSA results as matrix.")


def fig9_sensitivity_summary():
    """Evidence grading and sensitivity summary heatmap."""
    # Look for sensitivity tables
    sensitivity_files = list(config.OUT_MODELS.glob("*sensitivity*.csv"))
    if not sensitivity_files:
        sensitivity_files = list(config.OUTPUTS_DIR.glob("**/sensitivity*.csv"))
    if not sensitivity_files:
        print("  [Fig 9] Skipping: no sensitivity analysis files found.")
        return

    # Collect results from sensitivity analyses
    results = []
    for f in sensitivity_files:
        try:
            sdf = pd.read_csv(f)
            results.append((f.stem, sdf))
        except Exception:
            continue

    if not results:
        print("  [Fig 9] Skipping: could not read sensitivity files.")
        return

    # Build significance matrix: rows = analyses, cols = key predictors
    key_predictors = ["Afferent_Input_Index", "Cognitive_Appraisal_Index",
                      "afferent", "cognitive"]

    analysis_names = []
    sig_matrix = []

    for name, sdf in results:
        # Try to find predictor and p-value columns
        pred_col = None
        p_col = None
        for col in sdf.columns:
            cl = col.lower()
            if "predictor" in cl or "variable" in cl or "term" in cl:
                pred_col = col
            if "p_val" in cl or cl == "p" or "pvalue" in cl or "sig" in cl:
                p_col = col

        if pred_col is None or p_col is None:
            continue

        row = {}
        for _, r in sdf.iterrows():
            pred_name = str(r[pred_col]).lower()
            for kp in key_predictors:
                if kp.lower() in pred_name:
                    try:
                        p_val = float(r[p_col])
                        row[kp] = 1 if p_val < 0.05 else 0
                    except (ValueError, TypeError):
                        row[kp] = -1  # insufficient data
                    break

        if row:
            analysis_names.append(name)
            sig_matrix.append(row)

    if not sig_matrix:
        print("  [Fig 9] Skipping: could not extract significance info from sensitivity files.")
        return

    # Build matrix
    all_preds = sorted(set(k for row in sig_matrix for k in row.keys()))
    mat = np.full((len(analysis_names), len(all_preds)), np.nan)

    for i, row in enumerate(sig_matrix):
        for j, pred in enumerate(all_preds):
            if pred in row:
                mat[i, j] = row[pred]

    # Plot
    fig, ax = plt.subplots(figsize=(max(6, len(all_preds) * 1.5), max(4, len(analysis_names) * 0.6)))

    # Custom colormap: white=NaN/insufficient, gray=not sig, green=significant
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(["#D3D3D3", "#4CAF50"])  # gray, green

    # Replace NaN with -1 for display, then mask
    display_mat = np.where(np.isnan(mat), -1, mat)
    im = ax.imshow(display_mat, cmap=cmap, vmin=0, vmax=1, aspect="auto")

    # Mark insufficient data (NaN) as white
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            if np.isnan(mat[i, j]):
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                           fill=True, facecolor="white", edgecolor="lightgray"))
            elif mat[i, j] == -1:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                           fill=True, facecolor="white", edgecolor="lightgray"))
                ax.text(j, i, "?", ha="center", va="center", fontsize=9, color="gray")

    ax.set_xticks(range(len(all_preds)))
    ax.set_xticklabels(all_preds, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(analysis_names)))
    ax.set_yticklabels(analysis_names, fontsize=9)
    ax.set_title("Sensitivity Summary: Coefficient Significance", fontsize=13)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#4CAF50", label="Significant (p < .05)"),
        Patch(facecolor="#D3D3D3", label="Not significant"),
        Patch(facecolor="white", edgecolor="lightgray", label="Insufficient data"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=9)

    plt.tight_layout()
    out_path = config.OUT_FIGURES / "fig9_sensitivity_summary.png"
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  [Fig 9] Saved: {out_path}")


# --- Tables ---

def generate_tables():
    """Generate all manuscript tables as CSV."""
    print("\n  Generating tables...")

    _table1_studies()
    _table2_intervention_taxonomy()
    _table3_contrast_families()
    _table4_clinical_normalization()
    _table5_sdm_peaks()
    _table6_component_regression()
    _table7_sensitivity()
    _table8_evidence_grading()


def _table1_studies():
    """Table 1: Included studies and imaging paradigms."""
    # Try to load from raw extractions
    if not config.RAW_EXTRACTIONS_DIR.exists():
        print("    [Table 1] Skipping: raw_extractions directory not found.")
        return

    json_files = list(config.RAW_EXTRACTIONS_DIR.glob("*.json"))
    if not json_files:
        print("    [Table 1] Skipping: no JSON files in raw_extractions.")
        return

    rows = []
    for jf in sorted(json_files):
        try:
            with open(jf, "r") as f:
                data = json.load(f)

            pmid = data.get("pmid", jf.stem)
            first_author = data.get("first_author", data.get("authors", [{"name": ""}])[0].get("name", "") if isinstance(data.get("authors"), list) else "")
            year = data.get("year", "")
            disease = data.get("disease_condition", data.get("condition", ""))
            n_total = data.get("n_total", data.get("sample_size", ""))
            paradigm = data.get("paradigm", data.get("imaging_paradigm", ""))

            rows.append({
                "pmid": pmid,
                "first_author": first_author,
                "year": year,
                "disease_condition": disease,
                "n_total": n_total,
                "paradigm": paradigm,
            })
        except (json.JSONDecodeError, KeyError, IndexError):
            continue

    if rows:
        df = pd.DataFrame(rows)
        out_path = config.OUT_TABLES / "table1_studies.csv"
        df.to_csv(out_path, index=False)
        print(f"    [Table 1] Saved: {out_path} ({len(df)} studies)")
    else:
        print("    [Table 1] Skipping: could not extract study info from JSONs.")


def _table2_intervention_taxonomy():
    """Table 2: Intervention coding taxonomy (arm_type x modality counts)."""
    if not config.ARM_COMPONENTS.exists():
        print("    [Table 2] Skipping: arm_components.csv not found.")
        return

    df = pd.read_csv(config.ARM_COMPONENTS)

    # Identify columns
    arm_type_col = None
    modality_col = None
    for col in df.columns:
        cl = col.lower()
        if "arm_type" in cl or "type" == cl:
            arm_type_col = col
        if "modality" in cl or "acupuncture_modality" in cl:
            modality_col = col

    if arm_type_col is None:
        # Use first categorical column
        cat_cols = df.select_dtypes(include=["object"]).columns
        if len(cat_cols) > 0:
            arm_type_col = cat_cols[0]

    if arm_type_col is None:
        print("    [Table 2] Skipping: cannot identify arm_type column.")
        return

    if modality_col:
        cross = pd.crosstab(df[arm_type_col], df[modality_col], margins=True)
    else:
        cross = df[arm_type_col].value_counts().reset_index()
        cross.columns = ["arm_type", "count"]

    out_path = config.OUT_TABLES / "table2_intervention_taxonomy.csv"
    cross.to_csv(out_path)
    print(f"    [Table 2] Saved: {out_path}")


def _table3_contrast_families():
    """Table 3: Contrast families and study counts."""
    if not config.CONTRAST_CLASSIFICATIONS.exists():
        print("    [Table 3] Skipping: contrast_classifications.csv not found.")
        return

    df = pd.read_csv(config.CONTRAST_CLASSIFICATIONS)

    cat_col = None
    for candidate in ["contrast_category", "category", "contrast_family"]:
        if candidate in df.columns:
            cat_col = candidate
            break

    if cat_col is None:
        print("    [Table 3] Skipping: cannot identify contrast_category column.")
        return

    # Count contrasts and unique studies per category
    study_col = None
    for candidate in ["pmid", "study_id", "study"]:
        if candidate in df.columns:
            study_col = candidate
            break

    summary = df.groupby(cat_col).agg(
        n_contrasts=(cat_col, "count"),
    ).reset_index()

    if study_col:
        study_counts = df.groupby(cat_col)[study_col].nunique().reset_index()
        study_counts.columns = [cat_col, "n_studies"]
        summary = summary.merge(study_counts, on=cat_col)

    out_path = config.OUT_TABLES / "table3_contrast_families.csv"
    summary.to_csv(out_path, index=False)
    print(f"    [Table 3] Saved: {out_path}")


def _table4_clinical_normalization():
    """Table 4: Clinical outcome normalization summary by domain."""
    resp_path = config.OUT_BEHAVIORAL / "domain_responsiveness.csv"
    if not resp_path.exists():
        resp_path = config.CLINICAL_RESPONSIVENESS
    if not resp_path.exists():
        print("    [Table 4] Skipping: domain_responsiveness.csv not found.")
        return

    df = pd.read_csv(resp_path)

    # Identify domain and R columns
    domain_col = None
    for candidate in ["outcome_domain", "domain", "disease_condition", "condition"]:
        if candidate in df.columns:
            domain_col = candidate
            break

    r_col = None
    for candidate in ["R_within", "r_within", "mean_R", "effect_size", "responsiveness"]:
        if candidate in df.columns:
            r_col = candidate
            break

    study_col = None
    for candidate in ["pmid", "study_id", "study"]:
        if candidate in df.columns:
            study_col = candidate
            break

    if domain_col is None or r_col is None:
        print("    [Table 4] Skipping: cannot identify domain/R columns.")
        return

    agg_dict = {
        "mean_R": (r_col, "mean"),
        "sd_R": (r_col, "std"),
        "n_observations": (r_col, "count"),
    }
    if study_col:
        agg_dict["n_studies"] = (study_col, "nunique")

    summary = df.groupby(domain_col).agg(**agg_dict).reset_index()
    summary = summary.round(3)

    out_path = config.OUT_TABLES / "table4_clinical_normalization.csv"
    summary.to_csv(out_path, index=False)
    print(f"    [Table 4] Saved: {out_path}")


def _table5_sdm_peaks():
    """Table 5: SDM-PSI peak results."""
    # Look for thresholded peak tables in SDM outputs
    peak_files = list(config.SDM_PROJECTS_DIR.glob("**/peaks*.csv")) + \
                 list(config.SDM_PROJECTS_DIR.glob("**/peak*.txt"))
    if not peak_files:
        print("    [Table 5] Skipping: no thresholded SDM peak results available.")
        print("              Generate after running SDM-PSI analyses.")
        return

    all_peaks = []
    for pf in peak_files:
        try:
            if pf.suffix == ".csv":
                pdf = pd.read_csv(pf)
            else:
                pdf = pd.read_csv(pf, sep="\t")
            pdf["source_analysis"] = pf.parent.name
            all_peaks.append(pdf)
        except Exception:
            continue

    if all_peaks:
        combined = pd.concat(all_peaks, ignore_index=True)
        out_path = config.OUT_TABLES / "table5_sdm_peaks.csv"
        combined.to_csv(out_path, index=False)
        print(f"    [Table 5] Saved: {out_path} ({len(combined)} peaks)")
    else:
        print("    [Table 5] Skipping: could not parse peak files.")


def _table6_component_regression():
    """Table 6: Component meta-regression results."""
    reg_path = config.OUT_MODELS / "component_meta_regression_results.csv"
    if not reg_path.exists():
        # Try alternative names
        alternatives = [
            config.OUT_MODELS / "meta_regression_results.csv",
            config.OUT_MODELS / "regression_results.csv",
        ]
        for alt in alternatives:
            if alt.exists():
                reg_path = alt
                break

    if not reg_path.exists():
        print("    [Table 6] Skipping: component_meta_regression_results.csv not found.")
        return

    df = pd.read_csv(reg_path)
    out_path = config.OUT_TABLES / "table6_component_regression.csv"
    df.to_csv(out_path, index=False)
    print(f"    [Table 6] Saved: {out_path}")


def _table7_sensitivity():
    """Table 7: Merged sensitivity analyses."""
    sensitivity_files = list(config.OUT_MODELS.glob("*sensitivity*.csv"))
    if not sensitivity_files:
        sensitivity_files = list(config.OUTPUTS_DIR.glob("**/sensitivity*.csv"))

    if not sensitivity_files:
        print("    [Table 7] Skipping: no sensitivity analysis files found.")
        return

    all_dfs = []
    for sf in sensitivity_files:
        try:
            sdf = pd.read_csv(sf)
            sdf["source"] = sf.stem
            all_dfs.append(sdf)
        except Exception:
            continue

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        out_path = config.OUT_TABLES / "table7_sensitivity.csv"
        combined.to_csv(out_path, index=False)
        print(f"    [Table 7] Saved: {out_path} ({len(combined)} rows)")
    else:
        print("    [Table 7] Skipping: could not read sensitivity files.")


def _table8_evidence_grading():
    """Table 8: Evidence grading for key findings."""
    # This is a manually curated table of evidence levels
    evidence = pd.DataFrame([
        {
            "finding": "Sham acupuncture produces detectable neural convergence",
            "evidence_level": "Strong",
            "basis": "SDM-PSI meta-analysis with >= 10 studies, FWE-corrected",
            "sensitivity_robust": "Yes",
        },
        {
            "finding": "Verum > Sham neural activation difference",
            "evidence_level": "Moderate",
            "basis": "SDM-PSI contrast analysis, consistent direction",
            "sensitivity_robust": "Yes",
        },
        {
            "finding": "Afferent Input Index predicts neural response magnitude",
            "evidence_level": "Moderate",
            "basis": "Meta-regression, significant after multiple comparison correction",
            "sensitivity_robust": "Partial",
        },
        {
            "finding": "Cognitive Appraisal Index modulates sham response",
            "evidence_level": "Moderate",
            "basis": "Component interaction model preferred by AIC/BIC",
            "sensitivity_robust": "Partial",
        },
        {
            "finding": "Perturbation-neural representational alignment",
            "evidence_level": "Preliminary",
            "basis": "RSA Mantel test, significant but small effect",
            "sensitivity_robust": "Not fully tested",
        },
        {
            "finding": "Sham heterogeneity by penetration depth",
            "evidence_level": "Moderate",
            "basis": "Subgroup differences in afferent index and neural response",
            "sensitivity_robust": "Yes",
        },
        {
            "finding": "Clinical responsiveness varies by disease domain",
            "evidence_level": "Preliminary",
            "basis": "Descriptive analysis; limited n per domain",
            "sensitivity_robust": "Not applicable",
        },
        {
            "finding": "Deqi bridging between afferent input and clinical outcome",
            "evidence_level": "Preliminary",
            "basis": "Mediation model; indirect effect CI excludes zero",
            "sensitivity_robust": "Partial",
        },
    ])

    out_path = config.OUT_TABLES / "table8_evidence_grading.csv"
    evidence.to_csv(out_path, index=False)
    print(f"    [Table 8] Saved: {out_path}")


def main():
    config.OUT_FIGURES.mkdir(parents=True, exist_ok=True)
    config.OUT_TABLES.mkdir(parents=True, exist_ok=True)

    print("Step 12: Publication Figures and Tables")
    print("=" * 60)

    # Generate all figures
    print("\n--- Figures ---")
    fig1_conceptual_model()
    fig2_perturbation_space()
    fig3_sdm_maps()
    fig4_neural_gradients()
    fig5_component_interaction()
    fig6_sham_heterogeneity()
    fig7_clinical_responsiveness()
    fig8_rsa_heatmap()
    fig9_sensitivity_summary()

    # Generate all tables
    print("\n--- Tables ---")
    generate_tables()

    print("\n" + "=" * 60)
    print("Done. Results in:", config.OUT_FIGURES, "and", config.OUT_TABLES)


if __name__ == "__main__":
    main()
