from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
import os

def create_shopping_list_pdf(shopping_data, filename):
    """
    shopping_data: list of tuples like (recipe_title, [ingredients])
    """
    # Register font that supports wide Unicode range (but not emoji)
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

    path = os.path.join(os.getcwd(), filename)

    doc = SimpleDocTemplate(path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()

    # Ingredient bullet style
    styles.add(ParagraphStyle(
        name="ListItem",
        fontName="HeiseiMin-W3",
        fontSize=12,
        leading=16,
        spaceAfter=4,
        alignment=TA_LEFT,
    ))

    # Recipe title style
    styles.add(ParagraphStyle(
        name="TitleItem",
        fontName="HeiseiMin-W3",
        fontSize=14,
        textColor="#2E86C1",
        leading=18,
        spaceAfter=8,
        spaceBefore=12,
        alignment=TA_LEFT,
    ))

    # Main header style (centered)
    styles.add(ParagraphStyle(
        name="Header",
        fontName="HeiseiMin-W3",
        fontSize=18,
        textColor="#1A5276",
        leading=24,
        spaceAfter=16,
        alignment=TA_CENTER,
    ))

    story = []
    story.append(Paragraph("Shopping List", styles["Header"]))
    story.append(Spacer(1, 12))

    for idx, (recipe_title, ingredients) in enumerate(shopping_data):
        story.append(Paragraph(f"<b>{recipe_title}</b>", styles["TitleItem"]))
        for item in ingredients:
            story.append(Paragraph(f"• {item}", styles["ListItem"]))  # ✅ Bullet instead of checkbox
        if idx != len(shopping_data) - 1:
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="80%", color="#CCCCCC"))
            story.append(Spacer(1, 6))

    doc.build(story)
    return path
