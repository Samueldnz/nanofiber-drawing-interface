from pathlib import Path

# =====================================================
# DATA
# =====================================================

DATA_DIR = Path("data")

# =====================================================
# OUTPUT
# =====================================================

OUTPUT_DIR = Path("output")

HISTOGRAM_DIR = OUTPUT_DIR / "histograms"
SCALE30_DIR = HISTOGRAM_DIR / "scale_30um"
SCALE100_DIR = HISTOGRAM_DIR/ "scale_100um"
BOXPLOT_DIR = OUTPUT_DIR / "boxplots"
TREND_DIR = OUTPUT_DIR / "trends"

# =====================================================
# FILES
# =====================================================

DESCRIPTIVE_CSV = OUTPUT_DIR / "fiber_statistics.csv"
DESCRIPTIVE_XLSX = OUTPUT_DIR / "fiber_statistics.xlsx"

ANOVA_DATASET = OUTPUT_DIR / "anova_dataset.csv"
ANOVA_RESULTS = OUTPUT_DIR / "anova_results.csv"

TUKEY_ALL = OUTPUT_DIR / "tukey_all_groups.csv"
TUKEY_OLD_VS_NEW = OUTPUT_DIR / "tukey_old_vs_new_same_speed.csv"

# =====================================================
# SAMPLE METADATA
# =====================================================

SAMPLES = {
    "A": {
        "Polymer": "AS",
        "Speed": 21
    },

    "B": {
        "Polymer": "AS",
        "Speed": 42
    },

    "C": {
        "Polymer": "AS",
        "Speed": 84
    },

    "D": {
        "Polymer": "FS",
        "Speed": 21
    },

    "E": {
        "Polymer": "FS",
        "Speed": 42
    },

    "F": {
        "Polymer": "FS",
        "Speed": 84
    },
    "G": {
        "Polymer": "FDM",
        "Speed": 21
    },
    "H": {
        "Polymer": "FDM",
        "Speed": 42
    },
    "I": {
        "Polymer": "FDM",
        "Speed": 54
    },
    "J": {
        "Polymer": "FDM",
        "Speed": 84
    },
    "K": {
        "Polymer": "FDM",
        "Speed": 42
    },
    "L": {
        "Polymer": "FDM",
        "Speed": 54
    },
    "M": {
        "Polymer": "FDM",
        "Speed": 84
    }
}

SAMPLES_ZOOM = {
    "D": {
        "Polymer": "FS",
        "Speed": 21
    },

    "E": {
        "Polymer": "FS",
        "Speed": 42
    },

    "F": {
        "Polymer": "FS",
        "Speed": 84
    },
    "G": {
        "Polymer": "FDM",
        "Speed": 21
    },
    "H": {
        "Polymer": "FDM",
        "Speed": 42
    },
    "I": {
        "Polymer": "FDM",
        "Speed": 54
    },
    "J": {
        "Polymer": "FDM",
        "Speed": 84
    },
    "K": {
        "Polymer": "FDM",
        "Speed": 42
    },
    "L": {
        "Polymer": "FDM",
        "Speed": 54
    },
    "M": {
        "Polymer": "FDM",
        "Speed": 84
    }
}

# =====================================================
# PLOT SETTINGS
# =====================================================

OLD_COLOR = "steelblue"
NEW_COLOR = "darkorange"

FIG_DPI = 600

HISTOGRAM_BINS = 15

# =====================================================
# ANOVA SETTINGS
# =====================================================

ALPHA = 0.05

INTERESTING_TUKEY_PAIRS = [
    ("AS-21", "FS-21"),
    ("AS-42", "FS-42"),
    ("AS-84", "FS-84")
]