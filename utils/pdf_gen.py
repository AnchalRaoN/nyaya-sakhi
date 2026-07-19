import time
from pathlib import Path

OUTPUT_DIR = Path("static")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_pdf(session: dict, user_id: str) -> str | None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )
        from reportlab.lib.enums import TA_CENTER

        fir_text = session.get("fir_draft", "")
        case = session.get("extracted", {})
        laws = session.get("law_sections", [])

        timestamp = int(time.time())
        safe_id = user_id.replace(":", "_").replace("+", "")
        filename = OUTPUT_DIR / f"nyaya_sakhi_{safe_id}_{timestamp}.pdf"

        doc = SimpleDocTemplate(str(filename), pagesize=A4,
                                 rightMargin=2*cm, leftMargin=2*cm,
                                 topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        SAFFRON = colors.HexColor("#FF6B00")
        DARK = colors.HexColor("#1A1A2E")
        GRAY = colors.HexColor("#6B7280")

        title_style = ParagraphStyle("Title2", parent=styles["Title"],
                                      fontSize=20, textColor=SAFFRON,
                                      alignment=TA_CENTER, fontName="Helvetica-Bold")
        section_header = ParagraphStyle("Sec", parent=styles["Heading2"],
                                         fontSize=12, textColor=DARK,
                                         spaceBefore=16, spaceAfter=6,
                                         fontName="Helvetica-Bold")
        body_style = ParagraphStyle("Body2", parent=styles["Normal"],
                                     fontSize=10, leading=16, spaceAfter=8, textColor=DARK)
        disclaimer_style = ParagraphStyle("Disc", parent=styles["Normal"],
                                           fontSize=8, textColor=GRAY, spaceBefore=12)

        story = []
        story.append(Paragraph("NYAYA SAKHI", title_style))
        story.append(Paragraph("AI-Powered Legal Aid for Indian Women", body_style))
        story.append(HRFlowable(width="100%", thickness=2, color=SAFFRON, spaceAfter=12))

        if case:
            story.append(Paragraph("CASE DETAILS", section_header))
            field_map = {
                "complainant_name": "Complainant Name",
                "complainant_phone": "Contact Number",
                "fathers_name": "Father's Name",
                "email": "Email",
                "incident_type": "Type of Incident",
                "incident_date": "Date",
                "incident_location": "Location",
                "perpetrator": "Perpetrator",
                "narrative_detail": "Details",
                "evidence": "Evidence",
                "desired_outcome": "Requested Relief",
            }
            table_data = [[label, str(case[key])] for key, label in field_map.items() if case.get(key)]
            if table_data:
                t = Table(table_data, colWidths=[5*cm, 11*cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#FFF7ED")),
                    ("TEXTCOLOR", (0,0), (0,-1), SAFFRON),
                    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
                    ("FONTSIZE", (0,0), (-1,-1), 9),
                    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
                    ("PADDING", (0,0), (-1,-1), 6),
                ]))
                story.append(t)
                story.append(Spacer(1, 12))

        if laws:
            story.append(Paragraph("APPLICABLE LAWS", section_header))
            for law in laws:
                story.append(Paragraph(f"<b>{law.get('act','')}</b> — {law.get('section','')}", body_style))
                story.append(Paragraph(law.get("description",""), body_style))

        if fir_text:
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB")))
            story.append(Paragraph("FIR APPLICATION DRAFT", section_header))
            for para in fir_text.split("\n\n"):
                if para.strip():
                    story.append(Paragraph(para.strip().replace("\n","<br/>"), body_style))

        story.append(HRFlowable(width="100%", thickness=2, color=SAFFRON, spaceBefore=16))
        story.append(Paragraph("EMERGENCY HELPLINES", section_header))
        helplines = [["NCW Helpline","7827-170-170"],["Women's Helpline","181"],
                     ["Police Emergency","100"],["NALSA Legal Aid","15100"]]
        ht = Table(helplines, colWidths=[8*cm, 8*cm])
        ht.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFF7ED")),
            ("FONTNAME", (1,0), (1,-1), "Helvetica-Bold"),
            ("TEXTCOLOR", (1,0), (1,-1), SAFFRON),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
            ("PADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(ht)

        story.append(Paragraph(
            "DISCLAIMER: AI-generated legal aid, not a substitute for professional advice. "
            "Consult your nearest DLSA for free legal representation.",
            disclaimer_style
        ))

        doc.build(story)
        return str(filename)

    except Exception as e:
        print(f"PDF generation error: {e}")
        return None