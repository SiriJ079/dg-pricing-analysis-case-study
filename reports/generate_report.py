from fpdf import FPDF
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
FIGURES_DIR = BASE_DIR.parent / "outputs" / "figures"
TABLES_DIR = BASE_DIR.parent / "outputs" / "tables"
OUTPUT_PATH = BASE_DIR / "executive_summary.pdf"

NAVY = (30, 50, 90)
GREY = (110, 110, 110)
LIGHT_GREY = (245, 245, 245)
BORDER_GREY = (200, 200, 200)
ACCENT = (0, 110, 180)

COLUMN_LABELS = {
    "no_of_offers": "Offers",
    "avg_base_rate": "Avg Base Rate",
    "avg_offered_premium": "Avg Offered Prem.",
    "avg_sold_premium": "Avg Sold Prem.",
    "avg_price_increase": "Avg Price Incr.",
    "conversion_rate": "Conversion",
    "avg_realised_uplift": "Avg Uplift/Sale",
    "total_realised_uplift": "Total Uplift",
    "elasticity": "Elasticity",
    "best_strategy": "Best Strategy",
    "value": "Value"
}

PCT_COLUMNS = {"conversion_rate"}


def format_value(col_name, val):
    if isinstance(val, str):
        return val
    if col_name in PCT_COLUMNS:
        return f"{val * 100:.1f}%"
    if abs(val) < 1:
        return f"{val:,.3f}"
    return f"{val:,.2f}"


class Report(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, "D&G Pricing Analysis | Executive Summary")
        self.set_x(-25)
        self.cell(15, 6, f"{self.page_no()}", align="R")
        self.set_draw_color(*BORDER_GREY)
        self.set_line_width(0.3)
        self.line(10, 13, 200, 13)
        self.ln(9)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*GREY)
        self.cell(0, 8, "Domestic & General - Pricing Analyst Case Study", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*NAVY)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.6)
        self.line(self.get_x(), self.get_y(), self.get_x() + 40, self.get_y())
        self.ln(5)
        self.set_text_color(20, 20, 20)

    def subheading(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*ACCENT)
        self.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(20, 20, 20)

    def body_text(self, text):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def bullet_list(self, items):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(40, 40, 40)
        for item in items:
            self.set_x(14)
            self.multi_cell(180, 5, f"-  {item}")
        self.ln(1)

    def stat_callout(self, label, value):
        self.set_fill_color(*LIGHT_GREY)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*ACCENT)
        self.cell(0, 7, f"  {label}: {value}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(40, 40, 40)
        self.ln(2)

    def add_table(self, df, first_col_label="Strategy"):
        n_cols = len(df.columns) + 1
        col_width = 190 / n_cols

        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(*NAVY)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(*NAVY)
        self.cell(col_width, 7, first_col_label, border=1, fill=True, align="C")
        for col in df.columns:
            label = COLUMN_LABELS.get(col, col)
            self.cell(col_width, 7, label, border=1, fill=True, align="C")
        self.ln()

        self.set_draw_color(*BORDER_GREY)
        fill = False
        for idx, row in df.iterrows():
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(20, 20, 20)
            self.set_fill_color(*LIGHT_GREY) if fill else self.set_fill_color(255, 255, 255)
            self.cell(col_width, 7, str(idx), border=1, fill=True, align="C")
            self.set_font("Helvetica", "", 8)
            for col, val in row.items():
                text = format_value(col, val)
                self.cell(col_width, 7, text, border=1, fill=True, align="C")
            self.ln()
            fill = not fill
        self.ln(4)

    def add_figure(self, path, width=170, caption=None):
        path = Path(path)
        if path.exists():
            x_center = (210 - width) / 2
            self.set_x(x_center)
            self.image(str(path), w=width)
            if caption:
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(*GREY)
                self.cell(0, 5, caption, align="C", new_x="LMARGIN", new_y="NEXT")
                self.set_text_color(20, 20, 20)
            self.ln(3)
        else:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(200, 0, 0)
            self.cell(0, 6, f"[Missing figure: {path.name}]", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(20, 20, 20)


pdf = Report()
pdf.set_auto_page_break(auto=True, margin=18)

# ---------- Title page ----------
pdf.add_page()
pdf.set_y(60)
pdf.set_font("Helvetica", "B", 24)
pdf.set_text_color(*NAVY)
pdf.cell(0, 14, "D&G Pricing Analysis", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(60, 60, 60)
pdf.cell(0, 10, "Executive Summary & Findings", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_draw_color(*ACCENT)
pdf.set_line_width(0.6)
pdf.line(85, pdf.get_y(), 125, pdf.get_y())
pdf.ln(14)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 6, "Prepared by: Siraj Tausif Shaik", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, "Domestic & General - Pricing Analyst Case Study", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(20)
pdf.set_font("Helvetica", "B", 11)
pdf.set_text_color(*NAVY)
pdf.cell(0, 6, "Key Recommendation", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(40, 40, 40)
pdf.set_x(30)
pdf.multi_cell(150, 6, "Adopt the @22% customer-level optimised pricing strategy, replacing ASIS, "
                       "based on significantly higher revenue uplift with no statistically proven "
                       "cost to conversion.", align="C")

# ---------- Executive Summary ----------
pdf.add_page()
pdf.section_title("Executive Summary")
pdf.body_text(
    "This report analyses offer-level pricing data across three strategies, ASIS "
    "(unadjusted appliance-level pricing), @22% and @23% (customer-level optimised "
    "strategies), to evaluate conversion, revenue, price elasticity, model bias, and "
    "the relationship between claims history and conversion."
)
pdf.subheading("Headline findings")
pdf.bullet_list([
    "@22% delivers the highest revenue uplift of the three strategies: £6.42 average uplift per sale and £5,545 total uplift, more than double @23%'s £2.92 and £2,535.",
    "Conversion rate does NOT differ significantly across strategies (chi-square p = 0.61), so @22%'s revenue gain does not come at a statistically proven cost to conversion.",
    "Offered premium differs significantly between every strategy pair (Welch's t-test, all p < 0.001).",
    "Claims history is a strong, independent driver of conversion (48.1% vs 20.0%, p < 0.0001), consistent across all strategies and after controlling for plan ownership.",
    "@22%'s pricing shows a mild link to its own predicted conversion rate (r = +0.11), a selection effect worth monitoring before scaling further."
])

# ---------- A. EDA ----------
pdf.section_title("A.  Exploratory Data Analysis")
pdf.body_text(
    "Before comparing strategies, the underlying data was profiled to confirm the three "
    "groups were reasonably comparable and to identify any data quality issues."
)
pdf.bullet_list([
    "Offer volumes: 1,115 ASIS offers, 3,923 @22% offers, 3,827 @23% offers.",
    "Customer and appliance profiles (purchase price, item age, manufacturer mix) were broadly similar across strategies, supporting a fair comparison.",
    "price_diff is exactly zero for every ASIS row by construction, since no optimisation is applied under this strategy.",
    "predictedconversionrate is a constant placeholder value (1.0) for all ASIS rows, indicating no real conversion model was run for this strategy. This field is excluded from later model-calibration comparisons involving ASIS."
])
pdf.add_figure(FIGURES_DIR / "price_variation_by_strategy.png",
               caption="Figure 1: Distribution of price adjustment (price_diff) by pricing strategy.")

pdf.add_page()
pdf.add_figure(FIGURES_DIR / "correlation_matrix.png",
               caption="Figure 2: Correlation matrix of key numeric variables.")

# ---------- B. Strategy performance ----------
pdf.add_page()
pdf.section_title("B.  Pricing Strategy Performance")
pdf.body_text("Summary of offer volumes, pricing, and conversion across the three strategies:")
try:
    summary_table = pd.read_csv(TABLES_DIR / "summary_table.csv", index_col=0)
    cols = [c for c in ["no_of_offers", "avg_base_rate", "avg_offered_premium", "avg_price_increase", "conversion_rate"] if c in summary_table.columns]
    pdf.add_table(summary_table[cols])
except FileNotFoundError:
    pdf.body_text("[summary_table.csv not found in outputs/tables/]")

pdf.subheading("Statistical testing")
pdf.bullet_list([
    "Conversion (binary outcome): chi-square test of independence across all three strategies gave p = 0.61, not significant. No strong evidence conversion rate genuinely differs by strategy.",
    "Offered premium and price increase (continuous): Welch's t-tests between every strategy pair were all highly significant (p < 0.001), confirming the strategies price very differently even though this doesn't translate into a proven conversion difference."
])

# ---------- C. Elasticity ----------
pdf.section_title("C.  Price Elasticity")
pdf.body_text(
    "Elasticity measures how sensitive conversion is to a percentage change in price. "
    "Between-group elasticity compares each optimised strategy to the ASIS baseline; "
    "within-group elasticity compares low-price vs high-price customers inside the same strategy."
)
try:
    elasticity_summary = pd.read_csv(TABLES_DIR / "task_c_elasticity.csv")
    label_col = elasticity_summary.columns[1]
    pdf.add_table(elasticity_summary.set_index(label_col)[["elasticity"]], first_col_label="Comparison")
except FileNotFoundError:
    pdf.body_text("[task_c_elasticity.csv not found]")

pdf.bullet_list([
    "Between-group elasticity is negative for both strategies, as expected: conversion falls as premium rises relative to ASIS (@22%: -0.44, @23%: -0.46).",
    "Within-group elasticity is positive for both (@22%: +0.66, @23%: +0.17), the opposite direction, an unexpected result investigated further.",
    "For @22%, this was partly explained by a weak positive correlation between price_diff and predictedconversionrate (r = +0.11): the model assigns slightly higher prices to customers it already predicts are more likely to convert, a selection effect rather than a genuine causal price response.",
    "For @23%, no tested variable (plan status, claims, item age, plan count) fully explained the positive within-group result; this remains a partially open question."
])

# ---------- D. Ranking & bias ----------
pdf.add_page()
pdf.section_title("D.  Strategy Ranking and Model Bias")
try:
    ranking_table = pd.read_csv(TABLES_DIR / "task_d_ranking.csv")
    pdf.add_table(ranking_table.set_index("criterion")[["best_strategy", "value"]], first_col_label="Criterion")
except FileNotFoundError:
    pdf.body_text("[task_d_ranking.csv not found]")

pdf.subheading("Is @22% the winner across the board?")
pdf.bullet_list([
    "Revenue: @22% wins decisively on both average uplift per sale (£6.42 vs £2.92) and total realised uplift (£5,545 vs £2,535).",
    "Premium: @22% produces the highest average offered premium of the optimised strategies.",
    "Conversion: @23% edges out @22% numerically (22.7% vs 22.0%), but this difference is not statistically significant overall (p = 0.61)."
])
pdf.subheading("Model bias assessment")
pdf.bullet_list([
    "Predicted-vs-actual conversion calibration gaps were small for both optimised models (@22%: 0.008, @23%: 0.004), suggesting reasonable calibration.",
    "However, @22%'s elasticity behaviour suggests a mild selection bias: pricing decisions are weakly but measurably linked to the model's own conversion prediction.",
    "Recommendation: this should be validated with a proper randomised or holdout test before scaling @22% significantly."
])

# ---------- E. Claims ----------
pdf.add_page()
pdf.section_title("E.  Claims and Conversion Relationship")
pdf.stat_callout("Chi-square statistic", "324.81 (p < 0.0001)")
pdf.body_text(
    "A chi-square test of independence confirmed a highly significant relationship "
    "between prior claims and conversion on a new offer."
)
pdf.add_figure(FIGURES_DIR / "conversion_by_claims.png", width=120,
               caption="Figure 3: Conversion rate by claim history, with 95% confidence intervals.")
pdf.bullet_list([
    "Customers with a claim on record converted at 48.1%, versus 20.0% for those without, roughly 2.4x higher.",
    "This gap held consistently across all three strategies (ASIS: 50.5% vs 20.4%; @22%: 48.4% vs 19.5%; @23%: 47.0% vs 20.3%).",
    "Claims correlate strongly with plan ownership (84.8% of claim holders already hold a plan), but the effect survives controlling for plan status: claims still roughly double conversion among non-plan customers (16.3% to 33.3%) and add a smaller boost among plan holders (43.9% to 50.7%)."
])

# ---------- F. Recommendation ----------
pdf.add_page()
pdf.section_title("F.  Final Recommendation")
pdf.subheading("Recommendation")
pdf.body_text(
    "Adopt @22% as the primary pricing strategy, replacing ASIS, given its clear "
    "revenue advantage and lack of statistically proven conversion cost. Continue "
    "monitoring @23% as a lower-risk alternative and consider a formal A/B test "
    "before full rollout."
)
pdf.subheading("Caveats")
pdf.bullet_list([
    "Conversion differences between strategies are not statistically significant overall (p = 0.61); this recommendation leans more heavily on revenue evidence than proven conversion advantage.",
    "@22%'s mild selection bias (price linked to its own predicted conversion) should be investigated further via a proper randomised or holdout test before scaling.",
    "The ASIS predicted-conversion field was found to be a placeholder constant, limiting fair three-way model-bias comparison; this should be corrected in future data extracts."
])
pdf.subheading("Suggested next steps")
pdf.bullet_list([
    "Run a properly powered A/B test between @22% and @23%, specifically designed to detect the ~2 percentage point conversion gap observed here.",
    "Investigate incorporating claims history and plan status jointly into the pricing model's customer segmentation, given both showed large and partly independent conversion effects.",
    "Fix the ASIS predicted-conversion data gap to enable fair model-bias assessment across all three strategies."
])

pdf.output(str(OUTPUT_PATH))
print(f"Report saved to: {OUTPUT_PATH}")