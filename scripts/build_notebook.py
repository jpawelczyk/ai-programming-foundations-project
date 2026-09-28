"""Build the submitted Jupyter notebook from reviewed source cells."""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data_workflow.ipynb"


def md(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(source.strip())


def code(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(source.strip())


cells = [
    md(
        """
        # Titanic Data Workflow

        **Author:** Johannes Pawelczyk  
        **Dataset:** [Titanic - Machine Learning from Disaster](https://www.kaggle.com/c/titanic/data)

        This notebook presents a reproducible exploratory workflow for the Titanic
        passenger training dataset. It audits and cleans the data, summarizes relevant
        passenger groups, produces three labeled visualizations, and interprets the
        patterns without training a machine-learning model or making causal claims.
        """
    ),
    md(
        """
        ## 1. Setup

        Import the required libraries, configure a consistent plotting style, and define
        relative project paths. A fixed seed is included so any future sampling added to
        the workflow remains reproducible.
        """
    ),
    code(
        """
        from pathlib import Path

        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns

        RANDOM_SEED = 42
        np.random.seed(RANDOM_SEED)
        pd.set_option("display.max_columns", 20)
        sns.set_theme(style="whitegrid", context="notebook")

        DATA_PATH = Path("data/titanic.csv")
        FIGURE_DIR = Path("figures")
        FIGURE_DIR.mkdir(exist_ok=True)
        """
    ),
    md(
        """
        ## 2. Data Ingestion

        Load the CSV with Pandas, display the first rows, and verify its dimensions and
        column types before changing anything.
        """
    ),
    code(
        """
        raw_df = pd.read_csv(DATA_PATH)
        print(f"Raw shape: {raw_df.shape[0]} rows x {raw_df.shape[1]} columns")
        raw_df.head()
        """
    ),
    code(
        """
        ingestion_audit = pd.DataFrame(
            {
                "dtype": raw_df.dtypes.astype(str),
                "missing_count": raw_df.isna().sum(),
                "missing_percent": (raw_df.isna().mean() * 100).round(1),
                "unique_values": raw_df.nunique(dropna=True),
            }
        )
        ingestion_audit
        """
    ),
    md(
        """
        The source contains **891 rows and 12 columns**. Age has 177 missing values,
        Cabin has 687, and Embarked has 2. The cleaning workflow therefore preserves
        missingness information rather than deleting every incomplete passenger.
        """
    ),
    md(
        """
        ## 3. Data Cleaning

        Two reusable functions are defined and applied below. Column normalization makes
        names predictable. Dataset-specific cleaning then removes exact duplicates,
        handles missing values, preserves missingness indicators, and creates a small set
        of transparent features used in the exploratory analysis.
        """
    ),
    code(
        """
        def normalize_column_names(data: pd.DataFrame) -> pd.DataFrame:
            \"\"\"Return a copy with stripped, lowercase, snake_case column names.\"\"\"
            normalized = data.copy()
            normalized.columns = (
                normalized.columns.str.strip()
                .str.replace(r"[^0-9A-Za-z]+", "_", regex=True)
                .str.strip("_")
                .str.lower()
            )
            return normalized


        def clean_titanic_data(data: pd.DataFrame) -> pd.DataFrame:
            \"\"\"Clean Titanic records while preserving signals about missing data.

            Exact duplicates are removed. Missing age is imputed with the median for the
            passenger's sex/class group and tracked in ``age_missing``. The two missing
            embarkation ports use the modal port. Raw cabin strings are replaced by a
            ``cabin_known`` indicator because 77% are missing. Family-size features are
            derived from the documented sibling/spouse and parent/child counts.
            \"\"\"
            cleaned = data.copy().drop_duplicates().reset_index(drop=True)

            for column in ["name", "sex", "ticket", "cabin", "embarked"]:
                cleaned[column] = cleaned[column].astype("string").str.strip()

            cleaned["age_missing"] = cleaned["age"].isna()
            grouped_age_median = cleaned.groupby(["sex", "pclass"])["age"].transform(
                "median"
            )
            cleaned["age"] = (
                cleaned["age"].fillna(grouped_age_median).fillna(cleaned["age"].median())
            )

            cleaned["embarked"] = cleaned["embarked"].fillna(
                cleaned["embarked"].mode().iloc[0]
            )
            cleaned["cabin_known"] = cleaned["cabin"].notna()
            cleaned["family_size"] = cleaned["sibsp"] + cleaned["parch"] + 1
            cleaned["is_alone"] = cleaned["family_size"].eq(1)
            cleaned = cleaned.drop(columns=["cabin"])
            return cleaned
        """
    ),
    code(
        """
        normalized_df = normalize_column_names(raw_df)
        clean_df = clean_titanic_data(normalized_df)

        cleaning_audit = pd.DataFrame(
            {
                "raw_missing": normalized_df.isna().sum(),
                "clean_missing": clean_df.isna().sum(),
            }
        ).fillna(0).astype(int)

        print(f"Exact duplicate rows removed: {len(normalized_df) - len(clean_df)}")
        print(f"Clean shape: {clean_df.shape[0]} rows x {clean_df.shape[1]} columns")
        cleaning_audit.loc[
            cleaning_audit.sum(axis=1).gt(0) | cleaning_audit.index.isin(["age", "embarked"])
        ]
        """
    ),
    code(
        """
        required_columns = {
            "survived", "pclass", "sex", "age", "fare", "embarked",
            "age_missing", "cabin_known", "family_size", "is_alone",
        }
        assert len(clean_df) == 891
        assert required_columns.issubset(clean_df.columns)
        assert clean_df[["age", "embarked"]].isna().sum().sum() == 0
        assert clean_df["survived"].isin([0, 1]).all()
        assert clean_df["family_size"].ge(1).all()
        print("All cleaning validation checks passed.")
        """
    ),
    md(
        """
        **Cleaning justification.** Dropping all incomplete rows would remove nearly
        four-fifths of the dataset because Cabin is sparse. Instead, the workflow avoids
        inventing cabin labels and preserves only whether a cabin was recorded. Age is
        imputed within sex and passenger class to retain observations while respecting
        broad group structure; `age_missing` keeps the fact of imputation available for
        later sensitivity analysis. These choices are assumptions, not recovered facts.
        """
    ),
    md(
        """
        ## 4. Exploratory Data Analysis

        The function below returns group sizes, survivor counts, and survival rates. Group
        counts are shown with rates so visually striking results from very small groups are
        not mistaken for equally precise evidence.
        """
    ),
    code(
        """
        def summarize_survival(
            data: pd.DataFrame, group_columns: str | list[str]
        ) -> pd.DataFrame:
            \"\"\"Summarize passenger count, survivor count, and survival rate by group.\"\"\"
            if isinstance(group_columns, str):
                group_columns = [group_columns]
            return (
                data.groupby(group_columns, dropna=False)["survived"]
                .agg(passengers="size", survivors="sum", survival_rate="mean")
                .assign(survival_rate=lambda frame: frame["survival_rate"].round(3))
                .reset_index()
            )


        overall_survival_rate = clean_df["survived"].mean()
        print(f"Overall survival rate: {overall_survival_rate:.1%}")
        survival_by_class_and_sex = summarize_survival(clean_df, ["pclass", "sex"])
        survival_by_class_and_sex
        """
    ),
    code(
        """
        family_summary = summarize_survival(clean_df, "family_size")
        family_summary
        """
    ),
    md(
        """
        The overall observed survival rate is 38.4%. Rates vary strongly by recorded sex
        and passenger class: women have higher observed rates in every class, while first-
        class passengers have higher rates than third-class passengers. Family-size rates
        are non-linear, but groups above seven members contain fewer than ten passengers,
        so those extreme percentages should be interpreted cautiously.
        """
    ),
    md("## 5. Visualizations"),
    code(
        """
        fig, ax = plt.subplots(figsize=(9, 5.5))
        sns.barplot(
            data=clean_df,
            x="pclass",
            y="survived",
            hue="sex",
            estimator="mean",
            errorbar=None,
            palette="Set2",
            ax=ax,
        )
        ax.set_title("Figure 1. Observed Survival Rate by Passenger Class and Sex")
        ax.set_xlabel("Passenger class")
        ax.set_ylabel("Survival rate")
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0%}"))
        ax.legend(title="Recorded sex")
        fig.tight_layout()
        fig.savefig(FIGURE_DIR / "figure_1_survival_by_class_and_sex.png", dpi=180)
        plt.show()
        """
    ),
    md(
        """
        **Figure 1 interpretation.** Recorded women had higher observed survival in every
        passenger class. First-class women had the highest rate (96.8%), while third-class
        men had the lowest (13.5%). These are historical associations shaped by evacuation
        practices and social structure, not causal effects or measures of individual merit.
        """
    ),
    code(
        """
        fig, ax = plt.subplots(figsize=(9, 5.5))
        plot_df = clean_df.assign(
            survival_status=clean_df["survived"].map({0: "Did not survive", 1: "Survived"})
        )
        sns.histplot(
            data=plot_df,
            x="age",
            hue="survival_status",
            bins=24,
            stat="density",
            common_norm=False,
            element="step",
            alpha=0.35,
            ax=ax,
        )
        ax.set_title("Figure 2. Age Distribution by Survival Status")
        ax.set_xlabel("Age in years (group-median imputed where missing)")
        ax.set_ylabel("Density within survival group")
        fig.tight_layout()
        fig.savefig(FIGURE_DIR / "figure_2_age_by_survival.png", dpi=180)
        plt.show()
        """
    ),
    md(
        """
        **Figure 2 interpretation.** The age distributions overlap substantially and both
        groups have a median age of about 28 years before imputation. A visible child peak
        among survivors warrants follow-up, but 177 ages were originally missing and the
        plot uses imputed values, so fine-grained age differences should not be overstated.
        """
    ),
    code(
        """
        family_plot = family_summary.copy()
        family_plot["family_label"] = family_plot["family_size"].astype(str)

        fig, ax = plt.subplots(figsize=(9, 5.5))
        sns.barplot(
            data=family_plot,
            x="family_label",
            y="survival_rate",
            color="#4C78A8",
            ax=ax,
        )
        ax.set_title("Figure 3. Observed Survival Rate by Family Size")
        ax.set_xlabel("Family size aboard (passenger + SibSp + Parch)")
        ax.set_ylabel("Survival rate")
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0%}"))
        for index, row in family_plot.reset_index(drop=True).iterrows():
            ax.text(
                index,
                min(row["survival_rate"] + 0.035, 0.97),
                f"n={int(row['passengers'])}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        fig.tight_layout()
        fig.savefig(FIGURE_DIR / "figure_3_survival_by_family_size.png", dpi=180)
        plt.show()
        """
    ),
    md(
        """
        **Figure 3 interpretation.** Passengers in families of two to four had higher
        observed survival than passengers traveling alone. Rates fall for larger families,
        but the labels show that the largest family-size categories contain few passengers;
        those unstable rates should not drive a general conclusion without uncertainty
        analysis and additional context.
        """
    ),
    md(
        """
        ## 6. Summary and Interpretation

        The workflow found an overall observed survival rate of 38.4%. Recorded sex and
        passenger class show the clearest descriptive separation: female passengers had
        higher survival rates in every class, and first-class passengers had higher rates
        than third-class passengers. Family size also shows a non-linear pattern, with the
        highest observed rate among families of four, while age distributions overlap.

        The analysis assumes that the Kaggle training file faithfully represents the
        underlying passenger records and that `SibSp` and `Parch` can be combined into a
        useful household-size proxy. Group-median age imputation reduces row loss but can
        compress within-group variation, and missingness may itself be informative. Cabin
        was too incomplete for responsible category-level analysis, so the workflow keeps
        only a missingness indicator.

        Important limitations remain. The data are historical and observational, several
        groups are small, and selection or recording processes may not be random. The
        visualizations describe associations rather than causes. A future analysis should
        add uncertainty intervals, test sensitivity to alternative age handling, document
        dataset provenance in greater depth, and evaluate whether conclusions change when
        imputed ages are excluded.

        One surprising feature is that the median recorded age is similar for survivors and
        non-survivors even though the distributions differ locally. This is a useful reminder
        that a single summary statistic can conceal important structure and that plots should
        be interpreted alongside data-quality information and group counts.
        """
    ),
]

notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3"},
    },
)
nbf.write(notebook, OUTPUT)
print(f"Wrote {OUTPUT}")
