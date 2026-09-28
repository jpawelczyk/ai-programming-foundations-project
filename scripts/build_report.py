"""Generate the submitted module summary PDF with ReportLab."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "module_summary.pdf"
FIGURES = ROOT / "figures"

NAVY = colors.HexColor("#18324B")
BLUE = colors.HexColor("#3A6EA5")
TEAL = colors.HexColor("#4C9A8A")
LIGHT_TEAL = colors.HexColor("#EAF4F2")
LIGHT_BLUE = colors.HexColor("#EDF3F9")
INK = colors.HexColor("#24313B")
MUTED = colors.HexColor("#5F6B74")
RULE = colors.HexColor("#D6DEE5")
WHITE = colors.white


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str) -> None:
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=19 * mm,
            rightMargin=19 * mm,
            topMargin=20 * mm,
            bottomMargin=18 * mm,
            title="AI Programming Foundations Project - Module Summary",
            author="Johannes Pawelczyk",
            subject="Reproducible exploratory analysis of the Titanic training dataset",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="content",
        )
        self.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=draw_page))


def draw_page(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    if doc.page == 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, height - 18 * mm, width, 18 * mm, stroke=0, fill=1)
        canvas.setFillColor(TEAL)
        canvas.rect(0, height - 20 * mm, width, 2 * mm, stroke=0, fill=1)
    else:
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.6)
        canvas.line(19 * mm, height - 13 * mm, width - 19 * mm, height - 13 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(19 * mm, height - 9.5 * mm, "AI PROGRAMMING FOUNDATIONS PROJECT")
        canvas.drawRightString(width - 19 * mm, height - 9.5 * mm, "MODULE SUMMARY")

    canvas.setStrokeColor(RULE)
    canvas.line(19 * mm, 12 * mm, width - 19 * mm, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(19 * mm, 8 * mm, "Titanic reproducible data workflow")
    canvas.drawRightString(width - 19 * mm, 8 * mm, f"{doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=TEAL,
        spaceAfter=10,
        tracking=1.2,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=29,
        leading=34,
        alignment=TA_LEFT,
        textColor=NAVY,
        spaceAfter=14,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=14,
        leading=20,
        textColor=MUTED,
        spaceAfter=24,
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=8,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="Subsection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=BLUE,
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyReport",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.6,
        leading=14.2,
        textColor=INK,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="Callout",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.2,
        leading=15,
        textColor=NAVY,
        spaceAfter=0,
    )
)
styles.add(
    ParagraphStyle(
        name="FigureCaption",
        parent=styles["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
        spaceBefore=4,
        spaceAfter=9,
    )
)
styles.add(
    ParagraphStyle(
        name="Reference",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.6,
        leading=12.5,
        leftIndent=12,
        firstLineIndent=-12,
        textColor=INK,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
        spaceAfter=5,
    )
)


def section(number: str, title: str) -> list:
    return [
        Paragraph(f"{number}  {title}", styles["Section"]),
        HRFlowable(width="100%", thickness=1.2, color=TEAL, spaceAfter=9),
    ]


def body(text: str) -> Paragraph:
    return Paragraph(text, styles["BodyReport"])


def figure(filename: str, caption: str) -> KeepTogether:
    path = FIGURES / filename
    image = Image(str(path), width=6.65 * inch, height=4.06 * inch)
    return KeepTogether([image, Paragraph(caption, styles["FigureCaption"])])


story: list = []

# Cover
story.extend(
    [
        Spacer(1, 22 * mm),
        Paragraph("MASTER'S DEGREE IN AI CAPSTONE", styles["CoverLabel"]),
        Paragraph("AI Programming<br/>Foundations Project", styles["CoverTitle"]),
        Paragraph(
            "A reproducible exploratory workflow for the Titanic passenger dataset",
            styles["CoverSubtitle"],
        ),
        HRFlowable(width="34%", thickness=3, color=TEAL, hAlign="LEFT", spaceAfter=18),
        Paragraph("Johannes Pawelczyk", styles["Subsection"]),
        Paragraph("Module summary | 28 September 2026", styles["Small"]),
        Spacer(1, 18 * mm),
        Table(
            [
                [
                    Paragraph(
                        "<b>Project objective</b><br/>Build a transparent Python workflow "
                        "that ingests, cleans, explores, visualizes, and communicates a "
                        "real tabular dataset without training a model.",
                        styles["Callout"],
                    )
                ]
            ],
            colWidths=[165 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_TEAL),
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#B8D7D1")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ]
            ),
        ),
        PageBreak(),
    ]
)

# Overview and data
story.extend(section("1", "Overview"))
story.append(
    body(
        "This project builds an end-to-end exploratory data workflow in Python using "
        "NumPy, Pandas, Matplotlib, Seaborn, and Jupyter. The submitted notebook loads "
        "the Titanic training dataset, audits and cleans its records, computes grouped "
        "summaries, produces three labeled figures, and documents assumptions and "
        "limitations. The dataset is available from the <a href='https://www.kaggle.com/c/titanic/data'>"
        "Titanic - Machine Learning from Disaster</a> project page."
    )
)
story.append(
    body(
        "The workflow was designed for rerunning rather than as a one-off analysis. "
        "Danchev (2022) presents open-source Python, Jupyter notebooks, Markdown, and "
        "real-world datasets as an integrated basis for transparent, reproducible, and "
        "ethical data analysis. Following that principle, this project keeps code, "
        "narrative, outputs, dependency versions, source data, and figures together."
    )
)

story.extend(section("2", "Dataset Description"))
story.append(
    body(
        "The CSV contains 891 passenger observations and 12 source variables. Key fields "
        "include survival status, passenger class, recorded sex, age, family relations "
        "aboard, fare, cabin, and embarkation port. Survival is binary: 342 passengers "
        "survived and 549 did not, for an observed survival rate of 38.4%."
    )
)
profile_data = [
    ["Quality check", "Observed value", "Workflow response"],
    ["Age missing", "177 (19.9%)", "Group-median imputation + indicator"],
    ["Cabin missing", "687 (77.1%)", "Retain only cabin-known indicator"],
    ["Embarked missing", "2 (0.2%)", "Fill with modal port S"],
    ["Exact duplicates", "0", "Checked; none removed"],
]
profile = Table(profile_data, colWidths=[39 * mm, 39 * mm, 83 * mm], repeatRows=1)
profile.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.6),
            ("LEADING", (0, 0), (-1, -1), 11),
            ("GRID", (0, 0), (-1, -1), 0.45, RULE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BLUE]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )
)
story.extend([profile, Spacer(1, 8)])
story.append(
    body(
        "The analysis focuses on survival rates across passenger class, recorded sex, "
        "age, and derived family size. The file is historical and observational, so "
        "the analysis describes associations and does not interpret these attributes as "
        "causal mechanisms or normative categories."
    )
)

story.extend(section("3", "Workflow Description"))
workflow_rows = [
    ["1", "Ingestion", "Load the local CSV; show first rows, dimensions, types, and missingness."],
    ["2", "Cleaning", "Normalize names; preserve missingness; impute age; derive transparent features."],
    ["3", "EDA", "Compute passenger counts, survivor counts, and survival rates by group."],
    ["4", "Visualization", "Create three labeled plots and save reproducible PNG outputs."],
    ["5", "Summary", "Interpret patterns with explicit assumptions, limitations, and next steps."],
]
workflow = Table(workflow_rows, colWidths=[10 * mm, 30 * mm, 121 * mm])
workflow.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (0, -1), TEAL),
            ("TEXTCOLOR", (0, 0), (0, -1), WHITE),
            ("FONTNAME", (0, 0), (1, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("LEADING", (0, 0), (-1, -1), 11.5),
            ("GRID", (0, 0), (-1, -1), 0.45, RULE),
            ("ROWBACKGROUNDS", (1, 0), (-1, -1), [WHITE, LIGHT_BLUE]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )
)
story.append(workflow)
story.append(PageBreak())

# Decisions
story.extend(section("4", "Key Decisions and Assumptions"))
story.append(Paragraph("Cleaning choices", styles["Subsection"]))
story.append(
    body(
        "The workflow defines and uses two documented cleaning functions. The first "
        "standardizes column names. The second removes exact duplicates, trims text, "
        "tracks missing age, fills age with the median of each sex/class group, fills two "
        "missing embarkation values with the modal port, replaces sparse cabin strings "
        "with a cabin-known indicator, and derives family size and solo-travel status."
    )
)
story.append(
    body(
        "This strategy keeps all 891 rows without pretending that missing values were "
        "observed. Wickham (2014) argues that a consistent tabular structure - one "
        "variable per column and one observation per row - makes data easier to manipulate, "
        "model, and visualize. The cleaned table follows that structure and avoids storing "
        "multiple meanings in a single field."
    )
)
story.append(Paragraph("EDA and plot design", styles["Subsection"]))
story.append(
    body(
        "The exploratory function reports group size, survivor count, and survival rate "
        "together. Counts are essential because rates for large family sizes are based on "
        "very few passengers. Figure 1 emphasizes the strongest class/sex differences; "
        "Figure 2 shows distribution overlap rather than only means; Figure 3 pairs every "
        "rate with its group size. Percent axes are bounded at 0-100% to avoid exaggerated "
        "visual differences."
    )
)
story.append(Paragraph("Assumptions", styles["Subsection"]))
story.append(
    body(
        "The workflow assumes the Kaggle file accurately transcribes the passenger records, "
        "that `SibSp + Parch + 1` is a useful family-size proxy, and that group-median age "
        "imputation is acceptable for descriptive plots. Imputed ages are not recovered "
        "facts; the `age_missing` indicator is retained so later work can test sensitivity "
        "to that choice."
    )
)

story.extend(section("5", "Results and Interpretation"))
story.append(
    body(
        "The overall observed survival rate is 38.4%. The figures below correspond directly "
        "to the labeled outputs in `data_workflow.ipynb`."
    )
)
story.append(
    figure(
        "figure_1_survival_by_class_and_sex.png",
        "Figure 1. Recorded women had higher observed survival in every class. First-class "
        "women had the highest rate (96.8%); third-class men had the lowest (13.5%).",
    )
)
story.append(PageBreak())
story.append(
    figure(
        "figure_2_age_by_survival.png",
        "Figure 2. The age distributions overlap substantially. Both raw groups have a "
        "median age of about 28 years, while the child range contains a visible survivor peak. "
        "Because 177 ages were imputed for plotting, fine-grained differences remain uncertain.",
    )
)
story.append(
    figure(
        "figure_3_survival_by_family_size.png",
        "Figure 3. Families of two to four show higher observed survival than solo travelers. "
        "The sharp rates for family sizes 8 and 11 are based on only 6 and 7 passengers, so "
        "they should not support broad claims.",
    )
)
story.append(
    body(
        "Taken together, the plots show that class and recorded sex separate outcomes more "
        "clearly than age alone, while family size has a non-linear association. One "
        "surprising result is that similar age medians coexist with local distribution "
        "differences. That contrast demonstrates why summary statistics and plots should "
        "be read together."
    )
)
story.append(PageBreak())

# Responsible practice and reproducibility
story.extend(section("6", "Responsible Practice: Bias and Data Quality"))
story.append(
    body(
        "Cleaning can create bias when missingness is uneven across the same social groups "
        "being compared. Deleting every row with missing Cabin would remove 77.1% of the "
        "data; deleting missing ages would remove 19.9%. Either choice could change class "
        "and sex distributions. The workflow therefore retains all passengers, preserves "
        "missingness indicators, reports group counts, and avoids category-level claims "
        "about Cabin."
    )
)
story.append(
    body(
        "Group-median age imputation can still reduce variation and reproduce existing "
        "group structure. A stronger follow-up would compare complete-case results, multiple "
        "imputation, and models that use the missingness indicator. The historical labels "
        "also reflect a disaster and unequal social conditions. Any predictive extension "
        "would need subgroup evaluation, leakage controls, explicit justification for using "
        "sensitive attributes, and human review before deployment."
    )
)

story.extend(section("7", "Reproducibility"))
story.append(
    body(
        "The repository contains the source CSV, executed notebook, generated figures, "
        "pinned `requirements.txt`, concise run instructions, and this report. Relative "
        "paths let a reviewer run the project from the repository root. Every code cell "
        "has been executed from top to bottom without errors, and validation assertions "
        "check row count, required columns, resolved age/embarkation values, valid survival "
        "labels, and family-size bounds."
    )
)
story.append(
    body(
        "Version control records separate scaffold, analysis, and reporting stages. Work was "
        "performed on a `development` branch and integrated into `main`, leaving both the "
        "history and the additional branch visible. This supports the transparent workflow "
        "that Danchev (2022) advocates: another analyst can inspect not only the final "
        "results but also the environment, decisions, and evolution of the work."
    )
)

story.extend(section("8", "Sources and Citations"))
story.append(
    Paragraph(
        "Danchev, V. (2022). Reproducible data science with Python: An open learning "
        "resource. <i>Journal of Open Source Education, 5</i>(56), 156. "
        "<a href='https://doi.org/10.21105/jose.00156'>https://doi.org/10.21105/jose.00156</a>",
        styles["Reference"],
    )
)
story.append(
    Paragraph(
        "Kaggle. (n.d.). <i>Titanic - Machine Learning from Disaster: Data</i>. "
        "Retrieved September 28, 2026, from "
        "<a href='https://www.kaggle.com/c/titanic/data'>https://www.kaggle.com/c/titanic/data</a>",
        styles["Reference"],
    )
)
story.append(
    Paragraph(
        "Wickham, H. (2014). Tidy data. <i>Journal of Statistical Software, 59</i>(10), "
        "1-23. <a href='https://doi.org/10.18637/jss.v059.i10'>"
        "https://doi.org/10.18637/jss.v059.i10</a>",
        styles["Reference"],
    )
)

doc = ReportDocTemplate(str(OUTPUT))
doc.build(story)
print(f"Wrote {OUTPUT}")
