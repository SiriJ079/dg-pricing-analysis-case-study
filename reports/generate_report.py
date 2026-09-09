from fpdf import FPDF
from pathlib import Path
import pandas as pd

FIGURES_DIR = Path("../outputs/figures")
TABLES_DIR = Path("../outputs/tables")
OUTPUT_PATH = Path("executive_summary.pdf")

class Report(PDF := FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "D&G Pricing Analysis - Executive Summary", align="R")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(20, 20, 20)
        self.ln(3)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(3)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def add_table(self, df, col_width=None):
        self.set_font("Helvetica", "B", 8)
        n_cols = len(df.columns) + 1
        col_width = col_width or (190 / n_cols)

        self.set_fill_color(230, 230, 230)
        self.cell(col_width, 6, "", border=1, fill=True)
        for col in df.columns:
            self.cell(col_width, 6, str(col)[:15], border=1, fill=True, align="C")
        self.ln()

        self.set_font("Helvetica", "", 8)
        for idx, row in df.iterrows():
            self.cell(col_width, 6, str(idx)[:15], border=1)
            for val in row:
                text = f"{val:.2f}" if isinstance(val, float) else str(val)
                self.cell(col_width, 6, text[:15], border=1, align="C")
            self.ln()
        self.ln(3)

    def add_figure(self, path, width=170):
        if Path(path).exists():
            self.image(str(path), w=width)
            self.ln(3)
        else:
            self.body_text(f"[Figure not found: {path}]")


pdf = Report()
pdf.set_auto_page_break(auto=True, margin=15)

# --- Title page ---
pdf.add_page()
pdf.set_font("Helvetica", "B", 20)
pdf.ln(30)
pdf.cell(0, 12, "D&G Pricing Analysis", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 12)
pdf.cell(0, 8, "Executive Summary & Findings", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font("Helvetica", "", 10)
pdf.cell(0, 6, "Prepared by: Siraj Tausif Shaik", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Domestic & General - Pricing Analyst Case Study", align="C", new_x="LMARGIN", new_y="NEXT")

# --- Executive summary ---
pdf.add_page()
pdf.section_title("Executive Summary")
pdf.body_text(
    "This report analyses offer-level pricing data across three strategies "
    "(ASIS, @22%, @23%) to evaluate conversion, revenue, elasticity, and "
    "claims relationships. @22% is recommended as the primary pricing "
    "strategy, delivering significantly higher revenue uplift than @23% "
    "with no statistically proven cost to conversion. Claims history was "
    "found to be an independent, strong driver of conversion that could "
    "improve future targeting."
)

# --- Task A: EDA ---
pdf.section_title("A. Exploratory Data Analysis")
pdf.body_text(
    "Offer volumes and customer/appliance profiles were broadly comparable "
    "across strategies. ASIS price_diff is exactly zero (no optimisation "
    "applied), while @22% and @23% show a spread of price increases and "
    "decreases. predictedconversionrate was found to be a constant "
    "placeholder (1.0) for all ASIS rows, excluded from later model "
    "calibration checks."
)
pdf.add_figure(FIGURES_DIR / "price_variation_by_strategy.png")

# --- Task B: Strategy performance ---
pdf.add_page()
pdf.section_title("B. Pricing Strategy Performance")
try:
    summary_table = pd.read_csv(TABLES_DIR / "summary_table.csv", index_col=0)
    pdf.add_table(summary_table[["no_of_offers", "avg_offered_premium", "avg_price_increase", "conversion_rate"]])
except FileNotFoundError:
    pdf.body_text("[summary_table.csv not found]")

pdf.body_text(
    "Chi-square test found no significant difference in conversion between "
    "strategies (p = 0.61). Welch's t-tests confirmed offered premium "
    "differs significantly between every strategy pair (p < 0.001)."
)

# --- Task C: Elasticity ---
pdf.section_title("C. Price Elasticity")
try:
    elasticity_summary = pd.read_csv(TABLES_DIR / "task_c_elasticity.csv")
    pdf.add_table(elasticity_summary.set_index("strategy")[["elasticity"]])
except FileNotFoundError:
    pdf.body_text("[task_c_elasticity.csv not found]")

pdf.body_text(
    "Between-group elasticity was negative as expected (@22%: -0.44, @23%: "
    "-0.46). Within-group elasticity was positive for both strategies "
    "(@22%: +0.66, @23%: +0.17), traced partly to a selection effect where "
    "the optimisation model links price to its own predicted conversion "
    "rate for @22% (r = +0.11)."
)

# --- Task D: Ranking and bias ---
pdf.add_page()
pdf.section_title("D. Strategy Ranking and Model Bias")
try:
    ranking_table = pd.read_csv(TABLES_DIR / "task_d_ranking.csv")
    pdf.add_table(ranking_table.set_index("criterion"))
except FileNotFoundError:
    pdf.body_text("[task_d_ranking.csv not found]")

pdf.body_text(
    "@22% outperforms @23% on revenue (avg uplift £6.42 vs £2.92; total "
    "uplift £5,545 vs £2,535). Calibration gaps for both optimised models "
    "were small (0.008 and 0.004), though @22% shows mild selection bias "
    "linked to predicted conversion, worth monitoring if scaled further."
)

# --- Task E: Claims ---
pdf.section_title("E. Claims and Conversion")
pdf.add_figure(FIGURES_DIR / "conversion_by_claims.png", width=140)
pdf.body_text(
    "Chi-square confirmed a highly significant relationship between claims "
    "and conversion (chi2 = 324.81, p < 0.0001). Claim holders converted at "
    "48.1% vs 20.0% for non-claimants, roughly 2.4x higher, consistent "
    "across all three strategies and independent of plan ownership."
)

# --- Task F: Recommendation ---
pdf.add_page()
pdf.section_title("F. Final Recommendation")
pdf.body_text(
    "Adopt @22% as the primary pricing strategy, replacing ASIS, given its "
    "clear revenue advantage and lack of statistically proven conversion "
    "cost (p = 0.61). Continue monitoring @23% as a lower-risk alternative.\n\n"
    "Caveats: conversion differences are not statistically significant "
    "overall, so this recommendation leans on revenue evidence. @22%'s mild "
    "selection bias should be investigated via a proper A/B test before "
    "scaling. Claims history is recommended as a new segmentation variable "
    "for future pricing models, given its strong, independent effect on "
    "conversion."
)

pdf.output(str(OUTPUT_PATH))
print(f"Report saved to: {OUTPUT_PATH}")