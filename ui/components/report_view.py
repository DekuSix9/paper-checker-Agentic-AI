import os
import io
import streamlit as st


def generate_pdf_report(state: dict) -> bytes:
    """Generate IEEE-style PDF report using ReportLab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        story = []
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, alignment=1)
        subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=10, leading=12, alignment=1, textColor=colors.gray)
        heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.navy)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=12)
        
        structured = state.get("paper_structured", {})
        paper_title = structured.get("title", "Research Paper Review Report")
        
        story.append(Paragraph("IEEE/ACM Conference Multi-Agent Review Report", title_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>Paper Title:</b> {paper_title}", subtitle_style))
        story.append(Spacer(1, 14))

        # Final Decision Table
        decision = state.get("final_decision", "pending").upper()
        dec_color = colors.green if decision == "ACCEPT" else (colors.red if decision == "REJECT" else colors.orange)
        
        table_data = [
            ["Final Decision", decision],
            ["Human Review Status", "Approved" if state.get("human_approved") else "Pending/Edited"]
        ]
        t = Table(table_data, colWidths=[150, 350])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('TEXTCOLOR', (1,0), (1,0), dec_color),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 14))

        # Meta-Review
        story.append(Paragraph("Area Chair Meta-Review", heading_style))
        story.append(Spacer(1, 4))
        meta_text = state.get("meta_review", "No meta review available.").replace("\n", "<br/>")
        story.append(Paragraph(meta_text, body_style))
        story.append(Spacer(1, 14))

        # 6 Specialist Reviews
        reports = [
            ("Novelty Checker", state.get("novelty_report")),
            ("Methodology Reviewer", state.get("methodology_report")),
            ("Statistical Rigor Checker", state.get("stats_report")),
            ("Writing Quality Reviewer", state.get("writing_report")),
            ("Ethics/Plagiarism Flagging Agent", state.get("ethics_report")),
            ("AI Content & Sentence Detection Agent", state.get("ai_detection_report"))
        ]

        for name, r in reports:
            if r:
                story.append(Paragraph(f"Specialist Review: {name}", heading_style))
                story.append(Paragraph(f"Score: {r.get('score')}/10 | Recommendation: {r.get('recommendation').upper()}", body_style))
                story.append(Paragraph(f"<b>Strengths:</b> {', '.join(r.get('strengths', []))}", body_style))
                story.append(Paragraph(f"<b>Weaknesses:</b> {', '.join(r.get('weaknesses', []))}", body_style))
                if r.get("flags"):
                    story.append(Paragraph(f"<b>Flags:</b> {', '.join(r.get('flags', []))}", body_style))
                story.append(Spacer(1, 10))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    except Exception as e:
        print(f"[PDF Generation Warning] ReportLab error: {e}")
        return b"%PDF-1.4 Mock PDF Report Content"


def render_report_view(state: dict):
    st.subheader("📄 IEEE-Style Final Conference Decision Report")
    
    if not state or not state.get("paper_structured"):
        st.info("No report generated yet. Run a paper review from the sidebar.")
        return

    structured = state.get("paper_structured", {})
    decision = state.get("final_decision", "pending").upper()

    st.markdown(f"## **Paper Title**: {structured.get('title')}")
    st.markdown(f"### **Final Decision**: `{decision}`")

    st.divider()
    st.markdown("### 🏛️ Area Chair Meta-Review Synthesis")
    st.markdown(state.get("meta_review", "Pending Area Chair meta-review synthesis."))

    st.divider()
    st.markdown("### 📑 Specialist Reviewer Reports")

    reports = [
        ("Novelty Checker", state.get("novelty_report")),
        ("Methodology Reviewer", state.get("methodology_report")),
        ("Statistical Rigor Checker", state.get("stats_report")),
        ("Writing Quality Reviewer", state.get("writing_report")),
        ("Ethics/Plagiarism Flagging Agent", state.get("ethics_report")),
        ("AI Content & Sentence Detection Agent", state.get("ai_detection_report"))
    ]

    for name, r in reports:
        if r:
            with st.expander(f"📌 {name} (Score: {r.get('score')}/10 | Rec: {r.get('recommendation').upper()})", expanded=True):
                st.markdown(f"**Score**: `{r.get('score')}/10` | **Confidence**: `{r.get('confidence')}`")
                st.markdown("**Strengths**:")
                for s in r.get("strengths", []):
                    st.markdown(f"- ✅ {s}")
                st.markdown("**Weaknesses**:")
                for w in r.get("weaknesses", []):
                    st.markdown(f"- ⚠️ {w}")
                if r.get("flags"):
                    st.markdown("**Flags**:")
                    for f in r.get("flags", []):
                        st.markdown(f"- 🚩 `{f}`")
                st.markdown(f"**Notes**: {r.get('raw_notes')}")

    st.divider()
    st.markdown("### 📥 Export Final Review Report")
    
    col1, col2 = st.columns(2)
    with col1:
        # Markdown Export
        md_text = f"# Review Report: {structured.get('title')}\n\nDecision: {decision}\n\n{state.get('meta_review')}"
        st.download_button("📥 Download Report (Markdown)", data=md_text, file_name="conference_review_report.md", mime="text/markdown")
        
    with col2:
        # PDF Export
        pdf_bytes = generate_pdf_report(state)
        st.download_button("📥 Download Report (PDF)", data=pdf_bytes, file_name="conference_review_report.pdf", mime="application/pdf")
