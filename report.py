from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib.pyplot as plt


def generate_pdf_report(user, df, total, ml_prediction):

    # ---------------- USER INFO ---------------- #
    name = user[1]
    email = user[3]

    file_path = "expense_report.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    elements = []

    # ================= HEADER ================= #
    elements.append(Paragraph("📊 AI Expense Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"<b>Name:</b> {name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Email:</b> {email}", styles["Normal"]))
    elements.append(Spacer(1, 15))

    # ================= SUMMARY ================= #
    elements.append(Paragraph("💰 Summary", styles["Heading2"]))

    summary_data = [
        ["Total Expense", f"₹{total}"],
        ["Next Prediction", f"₹{ml_prediction}"]
    ]

    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold")
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # ================= RECENT EXPENSE TABLE ================= #
    elements.append(Paragraph("📋 Recent Expenses", styles["Heading2"]))

    df_recent = df.tail(10)

    table_data = [["Date", "Category", "Amount"]]

    for _, row in df_recent.iterrows():
        table_data.append([
            str(row["Date"].date()),
            row["Category"],
            f"₹{row['Amount']}"
        ])

    table = Table(table_data, colWidths=[120, 150, 100])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ================= CHARTS ================= #

    # PIE CHART
    cat_sum = df.groupby("Category")["Amount"].sum()

    plt.figure()
    cat_sum.plot(kind="pie", autopct="%1.1f%%")
    plt.ylabel("")
    pie_path = "pie.png"
    plt.savefig(pie_path)
    plt.close()

    # BAR CHART
    monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()

    plt.figure()
    monthly.plot(kind="bar")
    plt.title("Monthly Spending")
    bar_path = "bar.png"
    plt.savefig(bar_path)
    plt.close()

    # IMAGE OBJECTS
    pie_img = Image(pie_path, width=250, height=200)
    bar_img = Image(bar_path, width=250, height=200)

    # SIDE BY SIDE TABLE
    chart_table = Table([[pie_img, bar_img]])

    chart_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))

    elements.append(Paragraph("📊 Expense Charts", styles["Heading2"]))
    elements.append(chart_table)

    # ================= BUILD ================= #
    doc.build(elements)

    return file_path