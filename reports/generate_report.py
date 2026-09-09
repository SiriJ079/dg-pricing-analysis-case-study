from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.doctemplate import BaseDocTemplate

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
FIGURES_DIR = BASE_DIR.parent / "outputs" / "figures"
TABLES_DIR = BASE_DIR.parent / "outputs" / "tables"
OUTPUT_PATH = BASE_DIR / "executive_summary.pdf"

# --------------------------------------------------------------------------
# Brand palette - inspired by Domestic & General's corporate reporting
# (deep navy headers, a single blue accent, light neutral greys, white space)
# --------------------------------------------------------------------------
NAVY = colors.HexColor("#132A4C")
NAVY_DARK = colors.HexColor("#0B1B33")
ACCENT_BLUE = colors.HexColor("#1F7AE0")
LIGHT_BLUE_BG = colors.HexColor("#EEF4FC")
GREY_TEXT = colors.HexColor("#3A3F47")
GREY_MUTED = colors.HexColor("#7A828E")
ROW_ALT = colors.HexColor("#F4F6F9")
BORDER_GREY = colors.HexColor("#D8DCE2")
GREEN_GOOD = colors.HexColor("#1E8E5A")
AMBER_CAUTION = colors.HexColor("#B9770E")
WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN_L = 2.0 * cm
MARGIN_R = 2.0 * cm
MARGIN_TOP = 2.6 * cm
MARGIN_BOTTOM = 2.0 * cm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="ReportTitle", fontName="Helvetica-Bold", fontSize=26,
    leading=30, textColor=NAVY, alignment=TA_CENTER, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="ReportSubtitle", fontName="Helvetica", fontSize=13.5,
    leading=17, textColor=GREY_TEXT, alignment=TA_CENTER, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="CoverMeta", fontName="Helvetica", fontSize=10, leading=14,
    textColor=GREY_MUTED, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="CoverRecTitle", fontName="Helvetica-Bold", fontSize=11.5,
    leading=15, textColor=WHITE, alignment=TA_CENTER, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="CoverRecBody", fontName="Helvetica", fontSize=10.5, leading=15,
    textColor=WHITE, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="SectionTitle", fontName="Helvetica-Bold", fontSize=15,
    leading=18, textColor=NAVY, spaceBefore=4, spaceAfter=2,
))
styles.add(ParagraphStyle(
    name="SectionKicker", fontName="Helvetica-Bold", fontSize=8.5,
    leading=10, textColor=ACCENT_BLUE, spaceAfter=1,
))
styles.add(ParagraphStyle(
    name="SubHeading", fontName="Helvetica-Bold", fontSize=11,
    leading=14, textColor=NAVY_DARK, spaceBefore=10, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="Body", fontName="Helvetica", fontSize=9.7, leading=14.5,
    textColor=GREY_TEXT, alignment=TA_LEFT, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="BodySmall", fontName="Helvetica", fontSize=8.7, leading=12.5,
    textColor=GREY_TEXT, alignment=TA_LEFT, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="BulletText", fontName="Helvetica", fontSize=9.7, leading=14,
    textColor=GREY_TEXT, spaceAfter=4, leftIndent=0,
))
styles.add(ParagraphStyle(
    name="Caption", fontName="Helvetica-Oblique", fontSize=8.3, leading=11,
    textColor=GREY_MUTED, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="StatNumber", fontName="Helvetica-Bold", fontSize=20, leading=22,
    textColor=NAVY, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="StatLabel", fontName="Helvetica", fontSize=8, leading=10.5,
    textColor=GREY_MUTED, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="TableHeader", fontName="Helvetica-Bold", fontSize=8.3,
    leading=10, textColor=WHITE, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="TableCell", fontName="Helvetica", fontSize=8.3, leading=10,
    textColor=GREY_TEXT, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="TableCellLeft", fontName="Helvetica-Bold", fontSize=8.3,
    leading=10, textColor=NAVY_DARK, alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    name="CalloutLabel", fontName="Helvetica-Bold", fontSize=9,
    leading=12, textColor=ACCENT_BLUE,
))
styles.add(ParagraphStyle(
    name="CalloutBody", fontName="Helvetica", fontSize=9.3, leading=13,
    textColor=GREY_TEXT,
))
styles.add(ParagraphStyle(
    name="TocEntry", fontName="Helvetica", fontSize=10, leading=20,
    textColor=GREY_TEXT,
))


def bullets(items, style="BulletText"):
    """A tidy bullet list flowable."""
    return ListFlowable(
        [ListItem(Paragraph(item, styles[style]), spaceAfter=5,
                  bulletColor=ACCENT_BLUE, value="circle") for item in items],
        bulletType="bullet", start="circle", bulletFontSize=5.5,
        leftIndent=13, bulletOffsetY=-1.2, bulletDedent=10,
    )


def stat_row(stats):
    """A row of big-number callouts, D&G annual-report style."""
    cells = []
    for value, label in stats:
        cell = [Paragraph(value, styles["StatNumber"]), Paragraph(label, styles["StatLabel"])]
        cells.append(cell)
    n = len(cells)
    col_w = CONTENT_W / n
    t = Table([cells], colWidths=[col_w] * n)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEAFTER", (0, 0), (-2, 0), 0.6, BORDER_GREY),
    ]))
    return t


def callout_box(label, body_html, fill=LIGHT_BLUE_BG, border=ACCENT_BLUE):
    """A soft highlight box for a key caveat / takeaway."""
    p1 = Paragraph(label, styles["CalloutLabel"])
    p2 = Paragraph(body_html, styles["CalloutBody"])
    t = Table([[p1], [p2]], colWidths=[CONTENT_W - 0.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fill),
        ("BOX", (0, 0), (-1, -1), 1, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (0, 0), 8),
        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ("TOPPADDING", (0, 1), (0, 1), 2),
        ("BOTTOMPADDING", (0, 1), (0, 1), 9),
    ]))
    return t


def data_table(headers, rows, col_widths=None, highlight_col=None, highlight_rows=None):
    """A styled data table with navy header row and alternating row shading."""
    header_cells = [Paragraph(h, styles["TableHeader"]) for h in headers]
    body = [header_cells]
    for r in rows:
        row_cells = []
        for i, val in enumerate(r):
            style = "TableCellLeft" if i == 0 else "TableCell"
            row_cells.append(Paragraph(str(val), styles[style]))
        body.append(row_cells)

    n_cols = len(headers)
    if col_widths is None:
        col_widths = [CONTENT_W / n_cols] * n_cols

    t = Table(body, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, 0), 0.75, NAVY),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, BORDER_GREY),
    ]
    for i in range(1, len(body)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    if highlight_rows:
        for idx in highlight_rows:
            style_cmds.append(("BACKGROUND", (0, idx + 1), (-1, idx + 1), LIGHT_BLUE_BG))
    t.setStyle(TableStyle(style_cmds))
    return t


def figure(path, width=None, caption=None, max_height=9.0 * cm):
    """Embed a figure, scaled to fit content width and a sane max height."""
    path = Path(path)
    flow = []
    if not path.exists():
        flow.append(Paragraph(f"[Missing figure: {path.name}]", styles["BodySmall"]))
        return flow
    img = Image(str(path))
    iw, ih = img.imageWidth, img.imageHeight
    target_w = width or CONTENT_W
    scale = target_w / iw
    target_h = ih * scale
    if target_h > max_height:
        scale = max_height / ih
        target_h = max_height
        target_w = iw * scale
    img.drawWidth = target_w
    img.drawHeight = target_h
    img.hAlign = "CENTER"
    flow.append(img)
    if caption:
        flow.append(Paragraph(caption, styles["Caption"]))
    return flow


def section_header(kicker, title):
    return [
        Paragraph(kicker, styles["SectionKicker"]),
        Paragraph(title, styles["SectionTitle"]),
        HRFlowable(width="100%", thickness=1.4, color=ACCENT_BLUE, spaceAfter=10, spaceBefore=2),
    ]


# --------------------------------------------------------------------------
# Load real results from the notebooks' saved outputs
# --------------------------------------------------------------------------
def load_csv(name, **kwargs):
    path = TABLES_DIR / name
    try:
        return pd.read_csv(path, **kwargs)
    except FileNotFoundError:
        print(f"[warn] missing table: {path}")
        return None


summary_table = load_csv("summary_table.csv")
elasticity_table = load_csv("task_c_elasticity.csv")
ranking_table = load_csv("task_d_ranking.csv")
calibration_table = load_csv("calibration_by_strategy.csv")
revenue_table = load_csv("revenue_realisation_by_strategy.csv")
stat_tests_table = load_csv("statistical_tests.csv")
claims_table = load_csv("claims_summary_by_strategy.csv")
appliance_table = load_csv("appliance_profile_by_strategy.csv")

# --------------------------------------------------------------------------
# Document + page templates (cover page has no header/footer; content pages do)
# --------------------------------------------------------------------------
doc = BaseDocTemplate(
    str(OUTPUT_PATH),
    pagesize=A4,
    leftMargin=MARGIN_L, rightMargin=MARGIN_R,
    topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
    title="D&G Pricing Analysis - Executive Summary",
    author="Siraj Tausif Shaik",
)

PAGE_STATE = {"section": ""}


def draw_cover_background(canvas, doc_):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 8.6 * cm, PAGE_W, 8.6 * cm, stroke=0, fill=1)
    canvas.setFillColor(ACCENT_BLUE)
    canvas.rect(0, PAGE_H - 8.6 * cm, PAGE_W, 0.12 * cm, stroke=0, fill=1)
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, 1.4 * cm, stroke=0, fill=1)
    canvas.restoreState()


def draw_content_frame(canvas, doc_):
    canvas.saveState()
    # Running header
    canvas.setStrokeColor(BORDER_GREY)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN_L, PAGE_H - 1.55 * cm, PAGE_W - MARGIN_R, PAGE_H - 1.55 * cm)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.setFillColor(NAVY)
    canvas.drawString(MARGIN_L, PAGE_H - 1.25 * cm, "D&G PRICING ANALYSIS")
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(GREY_MUTED)
    canvas.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 1.25 * cm, "Pricing Analyst Case Study")
    # Footer
    canvas.setStrokeColor(BORDER_GREY)
    canvas.line(MARGIN_L, 1.35 * cm, PAGE_W - MARGIN_R, 1.35 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY_MUTED)
    canvas.drawString(MARGIN_L, 1.0 * cm, "Prepared by Siraj Tausif Shaik")
    canvas.drawCentredString(PAGE_W / 2, 1.0 * cm, "Domestic & General")
    canvas.drawRightString(PAGE_W - MARGIN_R, 1.0 * cm, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, rightPadding=0,
                     topPadding=0, bottomPadding=0)
content_frame = Frame(MARGIN_L, MARGIN_BOTTOM, CONTENT_W, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
                       id="content")

doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[cover_frame], onPage=draw_cover_background),
    PageTemplate(id="Content", frames=[content_frame], onPage=draw_content_frame),
])

# --------------------------------------------------------------------------
# Build the story (flowables)
# --------------------------------------------------------------------------
story = []

# ============================== COVER PAGE ===============================
story.append(Spacer(1, 3.6 * cm))
cover_title_tbl = Table(
    [[Paragraph("D&amp;G Pricing Analysis", ParagraphStyle(
        "cvt", parent=styles["ReportTitle"], textColor=WHITE))],
     [Paragraph("Evaluating Customer-Level Optimised Pricing for New Business",
                ParagraphStyle("cvs", parent=styles["ReportSubtitle"], textColor=colors.HexColor("#C9D9F2")))]],
    colWidths=[PAGE_W - 6 * cm],
)
cover_title_tbl.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
story.append(cover_title_tbl)
story.append(Spacer(1, 1.0 * cm))

meta_style_white = ParagraphStyle("cmw", parent=styles["CoverMeta"], textColor=colors.HexColor("#AEC2E8"))
story.append(Paragraph("Pricing Analyst Case Study &bull; Executive Summary Report", meta_style_white))
story.append(Spacer(1, 5.4 * cm))

story.append(Paragraph("KEY RECOMMENDATION", ParagraphStyle(
    "krlbl", parent=styles["SectionKicker"], alignment=TA_CENTER, textColor=ACCENT_BLUE, fontSize=9.5)))
story.append(Spacer(1, 0.15 * cm))
rec_box = Table(
    [[Paragraph(
        "Adopt the <b>@22% customer-level optimised pricing strategy</b> in place of the current ASIS "
        "approach. It generates substantially more revenue per offer with no statistically proven cost "
        "to conversion, though it should be rolled out alongside a proper live test given the caveats "
        "detailed in this report.",
        styles["CoverRecBody"])]],
    colWidths=[PAGE_W - 5 * cm],
)
rec_box.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), NAVY_DARK),
    ("BOX", (0, 0), (-1, -1), 1, ACCENT_BLUE),
    ("LEFTPADDING", (0, 0), (-1, -1), 22),
    ("RIGHTPADDING", (0, 0), (-1, -1), 22),
    ("TOPPADDING", (0, 0), (-1, -1), 14),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
story.append(rec_box)
story.append(Spacer(1, 1.6 * cm))
author_style = ParagraphStyle("auth", parent=styles["CoverMeta"], textColor=GREY_MUTED)
story.append(Paragraph("Prepared by Siraj Tausif Shaik", author_style))
story.append(Paragraph("dg-pricing-analysis-case-study &bull; github.com/SiriJ079", author_style))

story.append(NextPageTemplate("Content"))
story.append(PageBreak())

# ============================ EXECUTIVE SUMMARY ==========================
story += section_header("OVERVIEW", "Executive Summary")
story.append(Paragraph(
    "Domestic &amp; General currently prices new appliance-protection-plan offers using a fixed, "
    "unadjusted rate ('ASIS'). This project tests whether switching to a customer-level optimised "
    "pricing model, offered at two different strategy settings, <b>@22%</b> and <b>@23%</b>, would "
    "improve the business outcome, using a sample of 8,865 contact-centre offers. The analysis looks "
    "at conversion rate, revenue, how sensitive customers are to price (elasticity), whether the "
    "pricing models are well-calibrated, and whether a customer's claims history affects their "
    "likelihood to buy.", styles["Body"],
))

story.append(Spacer(1, 4))
story.append(stat_row([
    ("@22%", "Recommended strategy"),
    ("&pound;6.42", "Avg. revenue uplift per sale (@22%)"),
    ("2.4&times;", "Conversion boost from a prior claim"),
    ("p = 0.61", "Conversion difference is not significant"),
]))
story.append(Spacer(1, 10))

story.append(Paragraph("Headline findings", styles["SubHeading"]))
story.append(bullets([
    "<b>@22% is the clear revenue winner.</b> It produced &pound;6.42 of extra revenue per sale on "
    "average, and &pound;5,545 in total across the sample, more than double @23%'s &pound;2.92 and "
    "&pound;2,535.",
    "<b>That revenue gain does not come at a proven cost to conversion.</b> A chi-square test found "
    "no statistically significant difference in conversion rate between the three strategies "
    "(p = 0.61), so ASIS's slightly higher raw conversion number (23.3% vs 22.0%) cannot be relied "
    "on as a genuine strategy effect.",
    "<b>Customers do respond to price, but the direction flips depending on how you slice the data.</b> "
    "Comparing each strategy against ASIS, conversion clearly falls as price rises, exactly as basic "
    "economic theory predicts. But comparing low- versus high-priced customers <i>within</i> the same "
    "strategy shows the opposite pattern, a sign that the pricing model itself is quietly influencing "
    "who gets offered a higher price.",
    "<b>Claims history is a powerful, independent signal.</b> Customers with a previous claim convert "
    "at roughly 2.4 times the rate of those without one (48.1% vs 20.0%), and this holds up even after "
    "accounting for whether they already own a plan.",
    "<b>The underlying data has some quality issues worth flagging</b>, most notably that ASIS's "
    "'predicted conversion rate' field is a placeholder value of 1.0 rather than a genuine model "
    "output, which limits how fairly all three strategies can be compared on model accuracy.",
]))

story.append(PageBreak())

# ============================== DATA & METHOD =============================
story += section_header("METHODOLOGY", "How the Data Was Prepared")
story.append(Paragraph(
    "The raw dataset covers contact-centre offers for appliance protection plans, priced under three "
    "strategies: <b>ASIS FEE</b> (the existing fixed-rate approach) and two customer-level optimised "
    "strategies, <b>@22%</b> and <b>@23%</b>, which adjust the price up or down for each customer based "
    "on a predictive model. Before any analysis, the data was cleaned in a dedicated notebook "
    "(<font face='Courier'>01_dataset_cleaning.ipynb</font>) to make sure comparisons between strategies "
    "would be fair and not distorted by formatting issues or bad records.", styles["Body"],
))
story.append(Paragraph("Cleaning steps applied", styles["SubHeading"]))
story.append(bullets([
    "Standardised column names to lowercase and converted date fields (offer date, purchase date) and "
    "numeric fields (premiums, price difference, claims, plan counts) to their correct data types, "
    "since inconsistent types would silently break later calculations.",
    "Removed exact duplicate rows to avoid double-counting any offer.",
    "Dropped rows missing the fields essential for comparing strategies (pricing point, sale outcome, "
    "base rate, offered premium, price difference), while deliberately keeping rows with missing "
    "claims data, since claims history is only needed for one specific part of the analysis and "
    "removing those rows everywhere would have thrown away useful data unnecessarily.",
    "Added two data-quality flags rather than silently deleting anything: one for non-positive prices, "
    "and one checking that offered premium minus base rate roughly equals the recorded price "
    "difference. No rows tripped the invalid-price flag in the final dataset, which is a reassuring "
    "sign the pricing fields are internally consistent.",
    "Saved the cleaned dataset separately from the raw file, so every later notebook works from the "
    "same trusted version.",
]))
story.append(Paragraph(
    "<b>Result:</b> 8,865 of the original 8,867 rows were retained, meaning almost no data was lost "
    "at the cleaning stage, a good sign that the raw extract was already reasonably well-formed.",
    styles["Body"],
))

# ============================== SECTION A: EDA ============================
story.append(Spacer(1, 6))
story += section_header("SECTION A", "Exploratory Data Analysis")
story.append(Paragraph(
    "Before comparing the three pricing strategies head-to-head, it is important to check that the "
    "groups being compared are actually similar in every other respect, otherwise any difference in "
    "outcome could just reflect who was offered which strategy, not the strategy itself.", styles["Body"],
))
story.append(bullets([
    "<b>Offer volumes:</b> 1,115 ASIS offers, 3,923 @22% offers and 3,827 @23% offers were sampled. "
    "The two optimised strategies are represented in similar numbers, giving a reasonably balanced "
    "comparison between them.",
    "<b>Customer and appliance profiles were broadly comparable</b> across all three strategies: "
    "average purchase price (&pound;398-&pound;411), item age, and plan-ownership rates (around 20% "
    "in every group) did not differ meaningfully, which supports treating any outcome difference as "
    "a genuine effect of the pricing strategy rather than a difference in who was offered it.",
    "<b>price_diff is exactly zero for every ASIS row</b>, which makes sense: ASIS applies no "
    "customer-level adjustment by design. @22% and @23% both show a spread of price increases and "
    "decreases, visible as the two boxes in Figure 1 sitting away from the dashed zero-line that "
    "marks ASIS.",
    "<b>A data quality issue was found in the predicted-conversion field:</b> for every ASIS row, "
    "'predicted conversion rate' is a constant value of 1.0, a placeholder rather than a genuine "
    "model output. This means ASIS cannot be fairly included in any comparison of how well-calibrated "
    "each strategy's pricing model is (see Section D).",
]))
story += figure(FIGURES_DIR / "price_variation_by_strategy.png", width=11.5 * cm,
                caption="Figure 1: Spread of price adjustment (price_diff) applied under each strategy, relative to the ASIS baseline of zero.")

story.append(Paragraph(
    "The correlation matrix below (Figure 2) was used to sanity-check relationships between all the "
    "key numeric fields before running any formal statistical tests. A few things stand out: base "
    "rate and offered premium are very strongly related (0.91), as expected since the offered premium "
    "is mostly built from the base rate; plan-related fields (plan count, active plans, cancelled "
    "plans) cluster together strongly (0.45-0.85), suggesting they largely capture the same underlying "
    "customer behaviour; and claims count and claim amount are highly correlated (0.79), which is "
    "intuitive, more claims tend to mean a higher total claim amount.", styles["Body"],
))
story += figure(FIGURES_DIR / "correlation_matrix.png", width=12 * cm,
                caption="Figure 2: Correlation matrix across all key numeric variables in the cleaned dataset.")

# ============================== SECTION B ============================
story.append(PageBreak())
story += section_header("SECTION B", "Pricing Strategy Performance")
story.append(Paragraph(
    "The core comparison of the three strategies is summarised below. ASIS is the current baseline; "
    "@22% and @23% are the two customer-level optimised alternatives being evaluated as replacements.",
    styles["Body"],
))
if summary_table is not None:
    rows = []
    for _, r in summary_table.iterrows():
        rows.append([
            r["pricing_point"], f"{int(r['no_of_offers']):,}", f"£{r['avg_base_rate']:.2f}",
            f"£{r['avg_offered_premium']:.2f}", f"£{r['avg_sold_premium']:.2f}",
            f"£{r['avg_price_increase']:.3f}", f"{Decimal(str(r['conversion_rate_pct'])).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}%",
        ])
    story.append(data_table(
        ["Strategy", "Offers", "Avg Base Rate", "Avg Offered Prem.", "Avg Sold Prem.", "Avg Price Incr.", "Conversion"],
        rows,
        col_widths=[2.3*cm, 1.9*cm, 2.6*cm, 2.9*cm, 2.6*cm, 2.6*cm, 2.4*cm],
    ))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Read on its own, ASIS looks like it converts best (23.3% vs 22.0% and 22.7%). But raw percentages "
    "like this can be misleading without a statistical test to check whether the gap is real or just "
    "noise from sampling.", styles["Body"],
))
story.append(Paragraph("Statistical testing", styles["SubHeading"]))
story.append(bullets([
    "<b>Conversion (a yes/no outcome):</b> a chi-square test of independence across all three "
    "strategies returned <b>p = 0.61</b>, far above the usual 0.05 significance threshold. In plain "
    "terms, there is no strong statistical evidence that conversion rate genuinely differs by "
    "strategy, the small gaps seen in the table above are consistent with random variation.",
    "<b>Offered premium and price increase (continuous numbers):</b> Welch's t-tests were run between "
    "every pair of strategies. Every single comparison came back highly significant (all "
    "<b>p &lt; 0.001</b>), confirming the strategies genuinely do price very differently from one "
    "another. This matters because it means the strategies are meaningfully distinct pricing "
    "treatments, even though that pricing difference is not currently translating into a proven "
    "conversion difference.",
]))
story.append(callout_box(
    "WHY THIS MATTERS",
    "Because conversion is statistically flat across strategies but revenue is not (see Section D), "
    "the business case for switching strategy has to rest on the revenue evidence rather than a "
    "conversion improvement. This is an important nuance carried through to the final recommendation.",
))

# ============================== SECTION C ============================
story.append(PageBreak())
story += section_header("SECTION C", "Price Elasticity")
story.append(Paragraph(
    "Elasticity measures how sensitive conversion is to a change in price, essentially, how much "
    "conversion moves for a given percentage change in premium. Two versions of this were calculated: "
    "a <b>between-group</b> comparison (each optimised strategy versus the ASIS baseline) and a "
    "<b>within-group</b> comparison (customers offered a low price versus a high price, inside the "
    "same strategy).", styles["Body"],
))
if elasticity_table is not None:
    rows = [[r["strategy"], f"{r['elasticity']:+.3f}"] for _, r in elasticity_table.iterrows()]
    story.append(data_table(["Comparison", "Elasticity"], rows, col_widths=[9*cm, 4*cm]))
story.append(Spacer(1, 6))
story.append(bullets([
    "<b>Between-group elasticity is negative for both strategies, exactly as economic theory "
    "predicts:</b> @22% is -0.44 and @23% is -0.46 versus ASIS. A higher price relative to the ASIS "
    "baseline is associated with lower conversion, a sensible, expected result.",
    "<b>Within-group elasticity flips to positive for both strategies</b> (@22%: +0.66, @23%: +0.17), "
    "the opposite direction. On the surface this looks like customers convert <i>more</i> when charged "
    "<i>more</i>, which does not make economic sense taken at face value.",
    "<b>The likely explanation for @22% is a selection effect, not a real price response.</b> A weak "
    "positive correlation (r = +0.11) was found between the price adjustment and the model's own "
    "predicted conversion rate: the optimisation model tends to assign slightly higher prices to "
    "customers it already believes are more likely to buy. This means the model is partly pricing "
    "based on its own prediction of who will convert, so the positive within-group elasticity is "
    "reflecting that bias rather than customers genuinely preferring higher prices.",
    "<b>For @23%, this explanation does not fully hold</b> (correlation of only -0.04 with predicted "
    "conversion). None of the other variables tested, plan status, claims, item age, or plan count, "
    "fully explained the positive result either, so this remains a partially open question worth "
    "investigating further with additional data.",
]))
story += figure(FIGURES_DIR / "price_diff_vs_predicted_conversion.png", width=14.5 * cm,
                caption="Figure 3: Price adjustment plotted against the model's predicted conversion rate, by strategy. The upward-sloping trend line for @22% (left) illustrates the selection effect described above.")

# ============================== SECTION D ============================
story.append(PageBreak())
story += section_header("SECTION D", "Strategy Ranking and Model Bias")
story.append(Paragraph(
    "Pulling the statistical and revenue evidence together, this section ranks the three strategies "
    "across several different criteria, since 'which strategy is best' depends on which outcome "
    "matters most to the business.", styles["Body"],
))
if ranking_table is not None:
    rows = []
    for _, r in ranking_table.iterrows():
        val = r["value"]
        val_str = f"{val:.3f}" if val < 10 else f"{val:,.2f}"
        rows.append([r["criterion"], r["best_strategy"], val_str])
    story.append(data_table(
        ["Criterion", "Best Strategy", "Value"], rows,
        col_widths=[9.5*cm, 3.3*cm, 3.1*cm],
    ))
story.append(Spacer(1, 8))
story.append(Paragraph("Is @22% the winner across the board?", styles["SubHeading"]))
story.append(bullets([
    "<b>Revenue:</b> @22% wins decisively on both average uplift per sale (&pound;6.42 vs &pound;2.92) "
    "and total realised uplift across the sample (&pound;5,545 vs &pound;2,535). This is the strongest "
    "and clearest piece of evidence in @22%'s favour.",
    "<b>Premium:</b> @22% also produces the highest average offered premium of the two optimised "
    "strategies, consistent with it taking a bolder pricing approach.",
    "<b>Conversion:</b> @23% edges out @22% numerically (22.7% vs 22.0%), but as shown in Section B, "
    "this difference is not statistically significant overall (p = 0.61), so it should not be read as "
    "a genuine advantage for @23%.",
]))
story.append(Paragraph("Model calibration and bias", styles["SubHeading"]))
if calibration_table is not None:
    rows = []
    for _, r in calibration_table.iterrows():
        if r["pricing_point"] == "ASIS FEE":
            continue
        rows.append([
            r["pricing_point"], f"{r['avg_predicted_conversion']:.3f}",
            f"{r['actual_conversion']:.3f}", f"{r['gap']:+.4f}",
        ])
    story.append(data_table(
        ["Strategy", "Avg. Predicted Conversion", "Actual Conversion", "Calibration Gap"],
        rows, col_widths=[3.5*cm, 4.5*cm, 3.5*cm, 4.4*cm],
    ))
story.append(Spacer(1, 6))
story.append(bullets([
    "Both optimised models are well calibrated: the gap between what each model predicted and what "
    "actually happened is small for @22% (0.008) and even smaller for @23% (0.004). ASIS is excluded "
    "here since its predicted-conversion field is the placeholder value flagged in Section A.",
    "However, calibration on average is not the same as being unbiased in <i>how</i> prices are set. "
    "The elasticity work in Section C shows @22%'s pricing decisions are mildly linked to its own "
    "conversion predictions, a selection bias that a simple average calibration check would not catch "
    "on its own.",
]))
story.append(callout_box(
    "CAVEAT TO FLAG",
    "@22%'s revenue advantage is genuine, but its pricing logic shows a mild selection bias that "
    "should be validated with a proper randomised or holdout test before scaling the strategy "
    "significantly, rather than relying solely on this observational sample.",
    fill=colors.HexColor("#FFF6E8"), border=AMBER_CAUTION,
))

# ============================== SECTION E ============================
story.append(PageBreak())
story += section_header("SECTION E", "Claims History and Conversion")
story.append(Paragraph(
    "One question outside the direct strategy comparison was whether a customer's claims history "
    "relates to how likely they are to buy a new plan. This turned out to be one of the strongest "
    "patterns in the whole dataset.", styles["Body"],
))
story.append(stat_row([
    ("48.1%", "Conversion with a prior claim"),
    ("20.0%", "Conversion with no prior claim"),
    ("2.4&times;", "Relative increase"),
    ("p &lt; 0.0001", "Chi-square significance"),
]))
story.append(Spacer(1, 8))
story += figure(FIGURES_DIR / "conversion_by_claims.png", width=11 * cm,
                caption="Figure 4: Conversion rate by claim history, with 95% confidence intervals. The non-overlapping intervals confirm this is a real, not a random, difference.")
story.append(bullets([
    "A chi-square test confirmed this relationship is highly statistically significant "
    "(<b>p &lt; 0.0001</b>), and the gap held up consistently across all three pricing strategies "
    "(ASIS: 50.5% vs 20.4%; @22%: 48.4% vs 19.5%; @23%: 47.0% vs 20.3%), ruling out the idea that "
    "claim holders were simply being steered toward whichever strategy converts best.",
    "Claim holders are disproportionately likely to already hold a plan (84.8% of them do, versus "
    "13.4% of non-claimants), which makes intuitive sense, you generally need an active plan to make "
    "a claim in the first place. This raised the question of whether claims are simply a proxy for "
    "plan ownership rather than an independent effect.",
    "Controlling for plan ownership confirmed claims still matter on their own: among customers with "
    "<i>no</i> existing plan, having a claim on record still roughly doubles conversion (16.3% to "
    "33.3%). Among customers who already hold a plan, claims still add a smaller but real boost "
    "(43.9% to 50.7%).",
    "The most likely explanation is behavioural rather than purely statistical: a customer who has "
    "recently experienced the value of their cover through a successful claim is probably more "
    "receptive to buying further protection, since the benefit feels concrete rather than abstract.",
]))
story.append(callout_box(
    "OPPORTUNITY FOR THE BUSINESS",
    "Claims history is a genuinely new, independent segmentation variable that is not yet built into "
    "the pricing models. Incorporating it, particularly for non-plan customers where the effect is "
    "largest, is a promising and low-risk next step for improving targeting.",
))

# ============================== SECTION F: RECOMMENDATION ============================
story.append(PageBreak())
story += section_header("SECTION F", "Final Recommendation")
story.append(Paragraph(
    "Bringing together the evidence from every section above, the recommendation is to move away "
    "from the current ASIS pricing approach and adopt the @22% customer-level optimised strategy, "
    "while continuing to monitor @23% as a lower-risk fallback.", styles["Body"],
))
story.append(callout_box(
    "RECOMMENDATION",
    "<b>Adopt @22% as the primary pricing strategy</b>, replacing ASIS. The revenue case is strong "
    "and the conversion risk is not statistically proven, but this should be implemented alongside a "
    "proper live test rather than a full, immediate rollout, given the caveats below.",
    fill=colors.HexColor("#EAF7EF"), border=GREEN_GOOD,
))
story.append(Paragraph("Why @22%", styles["SubHeading"]))
story.append(bullets([
    "It generates substantially more revenue than @23%: &pound;6.42 average uplift per sale versus "
    "&pound;2.92, and &pound;5,545 total uplift versus &pound;2,535 across the sample.",
    "The chi-square test found no statistically significant difference in conversion rate between "
    "strategies (p = 0.61), meaning this revenue gain does not come at a meaningful, provable cost to "
    "conversion volume.",
    "Both optimised strategies showed reasonable calibration between predicted and actual conversion "
    "(gaps of 0.008 and 0.004 respectively), suggesting the underlying models are not grossly "
    "miscalibrated on average.",
]))
story.append(Paragraph("Caveats to flag to the business", styles["SubHeading"]))
story.append(bullets([
    "@22%'s pricing decisions are weakly but measurably linked to its own predicted conversion rate "
    "(r = +0.11), meaning higher-priced customers within that strategy were already somewhat more "
    "likely to convert. This mild selection bias should be investigated further, ideally with a "
    "proper randomised or holdout test, before scaling @22% significantly.",
    "Conversion differences between strategies are not statistically significant at the overall level "
    "(p = 0.61), so this recommendation rests more heavily on the revenue evidence than on a proven "
    "conversion advantage.",
    "Claims history is a strong, independent driver of conversion (48.1% vs 20.0%, p &lt; 0.0001), "
    "robust even after controlling for plan ownership. This is a genuinely new and actionable "
    "segmentation variable that is not yet used in the pricing models.",
    "ASIS's predicted-conversion field was found to be a constant placeholder value (1.0) rather than "
    "a genuine model output, meaning ASIS could not be included in the model-calibration comparison. "
    "This should be corrected in future data extracts to allow a fairer three-way comparison.",
]))
story.append(Paragraph("Suggested next steps", styles["SubHeading"]))
story.append(bullets([
    "Run a properly powered A/B test (or extend a current live test) comparing @22% against @23%, "
    "specifically designed to detect a conversion difference of the size observed here "
    "(around 2 percentage points), since the current sample was not statistically conclusive.",
    "Investigate incorporating claims history and plan status jointly into the pricing model's "
    "customer segmentation, given both showed large and partly independent conversion effects.",
    "Fix the ASIS predicted-conversion data gap so future analyses can properly assess model bias "
    "for all three strategies on an equal footing.",
]))

closing = Table(
    [[Paragraph(
        "This analysis was completed end-to-end in Python (pandas, seaborn, scipy) as part of the "
        "Domestic &amp; General Pricing Analyst case study. Full code, notebooks and outputs are "
        "available in the accompanying GitHub repository.", styles["BodySmall"])]],
    colWidths=[CONTENT_W],
)
closing.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), ROW_ALT),
    ("BOX", (0, 0), (-1, -1), 0.5, BORDER_GREY),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story.append(KeepTogether([Spacer(1, 10), closing]))

# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
doc.build(story)
print(f"Report saved to: {OUTPUT_PATH}")