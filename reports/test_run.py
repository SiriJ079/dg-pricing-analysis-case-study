from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", "B", 16)
pdf.cell(0, 10, "Test Page - If you see this, FPDF works.")
pdf.output("test.pdf")
print("Test PDF created.")