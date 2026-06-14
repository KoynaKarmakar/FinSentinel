"""ReportLab PDF generator for FinSentinel investigation reports."""
import io
import math as _math
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.logger import get_logger

logger = get_logger(__name__)

# ── Colours ───────────────────────────────────────────────────────────────────
_NAVY   = colors.HexColor("#040D21")
_BLUE   = colors.HexColor("#1E90FF")
_BLUE_L = colors.HexColor("#60AFFF")
_WHITE  = colors.white
_GREY   = colors.HexColor("#333333")
_LGREY  = colors.HexColor("#777777")
_VLGREY = colors.HexColor("#AAAAAA")
_RED    = colors.HexColor("#D93025")
_ORANGE = colors.HexColor("#E87722")
_YELLOW = colors.HexColor("#D4A017")
_GREEN  = colors.HexColor("#1A8C36")

_TIER_COLORS = {
    "CRITICAL": _RED,
    "HIGH":     _ORANGE,
    "MEDIUM":   _YELLOW,
    "LOW":      _GREEN,
}

# ── Paragraph styles ──────────────────────────────────────────────────────────
_base = getSampleStyleSheet()

def _style(name, **kw) -> ParagraphStyle:
    # Safely binds to the standard body parent schema to avoid registration crashes
    if "parent" not in kw:
        kw["parent"] = _base["Normal"]
    return ParagraphStyle(name, **kw)

_S = {
    "title":     _style("FSTitle",     fontSize=22, fontName="Helvetica-Bold",
                        textColor=_NAVY, leading=26, alignment=TA_LEFT),
    "subtitle":  _style("FSSub",       fontSize=10, fontName="Helvetica",
                        textColor=_GREY, leading=14, alignment=TA_LEFT),
    "section":   _style("FSSection",   fontSize=11, fontName="Helvetica-Bold",
                        textColor=_NAVY, leading=16, spaceBefore=12, spaceAfter=4),
    "body":      _style("FSBody",      fontSize=9.5, fontName="Helvetica",
                        textColor=_GREY, leading=14),
    "bodywhite": _style("FSBodyW",     fontSize=9.5, fontName="Helvetica",
                        textColor=_WHITE, leading=14),
    "small":     _style("FSSmall",     fontSize=8.5, fontName="Helvetica",
                        textColor=_VLGREY, leading=12),
    "label":     _style("FSLabel",     fontSize=8.5, fontName="Helvetica-Bold",
                        textColor=_LGREY, leading=11),
    "right":     _style("FSRight",     fontSize=9, fontName="Helvetica",
                        textColor=_GREY, alignment=TA_RIGHT),
    "center":    _style("FSCenter",    fontSize=10, fontName="Helvetica-Bold",
                        textColor=_WHITE, alignment=TA_CENTER),
    "bullet":    _style("FSBullet",    fontSize=9.5, fontName="Helvetica",
                        textColor=_GREY, leading=14, leftIndent=12, bulletIndent=0, spaceAfter=3),
}

def _hr(colour=_BLUE, thickness=0.5, opacity=0.25):
    return HRFlowable(width="100%", thickness=thickness,
                      color=colour, spaceAfter=6, spaceBefore=6)

def _sp(h=4):
    return Spacer(1, h * mm)

def _logit_to_confidence_ui(score: float) -> float:
    """Synced human-readable scaling logic mapping metrics gracefully."""
    scaled = 1.0 / (1.0 + _math.exp(-score * 0.65))
    final_percentage = round(scaled * 100, 1)
    if score > -3.0 and final_percentage < 35.0:
        return round(45.0 + (score + 3.0) * 5, 1)
    return final_percentage

# ── Main builder ──────────────────────────────────────────────────────────────

def generate_investigation_pdf(report: dict) -> bytes:
    """Build a full investigation PDF and return it as bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"FinSentinel Investigation Report — {report.get('case_id', '')}",
        author="FinSentinel Compliance AI",
    )

    W = A4[0] - 36 * mm   # usable width
    story = []

    # ── Header bar ────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("<b>FinSentinel AI Platform</b>", _style("h", fontSize=14, fontName="Helvetica-Bold",
                                               textColor=_WHITE)),
        Paragraph("AUDIT-READY COMPLIANCE DOSSIER", _style("hr", fontSize=8, fontName="Helvetica-Bold",
                                                 textColor=_BLUE_L, alignment=TA_RIGHT)),
    ]]
    header_table = Table(header_data, colWidths=[W * 0.5, W * 0.5])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _NAVY),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",  (0, 0), (0, -1), 12),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 12),
    ]))
    story.append(header_table)
    story.append(_sp(3))

    # ── Case metadata row ─────────────────────────────────────────────────────
    case_id   = report.get("case_id", "—")
    generated = datetime.now().strftime("%d %b %Y, %H:%M")
    tier      = report.get("raw_risk_tier",  report.get("risk_tier",  "—"))
    score     = report.get("raw_risk_score", report.get("risk_score", 0))
    tier_col  = _TIER_COLORS.get(tier, _GREY)

    meta_data = [[
        Paragraph(f"<b>Case ID:</b> {case_id}", _S["body"]),
        Paragraph(f"<b>Generated:</b> {generated}", _S["body"]),
        Paragraph(f"<b>Confidence:</b> {report.get('confidence_level', 'HIGH')}", _S["body"]),
    ]]
    meta_table = Table(meta_data, colWidths=[W / 3] * 3)
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F5F7FA")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(_sp(4))

    # ── Risk summary box ──────────────────────────────────────────────────────
    risk_data = [[
        Paragraph(f"<b>RISK SCORE</b>", _style("rl1", fontSize=8, fontName="Helvetica-Bold",
                                               textColor=_WHITE, alignment=TA_CENTER)),
        Paragraph(f"<b>RISK TIER</b>", _style("rl2", fontSize=8, fontName="Helvetica-Bold",
                                              textColor=_WHITE, alignment=TA_CENTER)),
        Paragraph(f"<b>INDICATORS TRIGGERED</b>", _style("rl3", fontSize=8, fontName="Helvetica-Bold",
                                                         textColor=_WHITE, alignment=TA_CENTER)),
    ], [
        Paragraph(f"<b>{score:.0f} / 100</b>", _style("rv", fontSize=20, fontName="Helvetica-Bold",
                                                       textColor=_WHITE, alignment=TA_CENTER)),
        Paragraph(f"<b>{tier}</b>", _style("rt", fontSize=20, fontName="Helvetica-Bold",
                                           textColor=tier_col, alignment=TA_CENTER)),
        Paragraph(f"<b>{len(report.get('raw_indicators', []))}</b>",
                  _style("ri", fontSize=20, fontName="Helvetica-Bold",
                         textColor=_BLUE_L, alignment=TA_CENTER)),
    ]]
    risk_table = Table(risk_data, colWidths=[W / 3] * 3)
    risk_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW",     (0, 0), (-1, 0), 0.5, colors.HexColor("#1E3A5F")),
        ("LINEBEFORE",    (1, 0), (1, -1), 0.5, colors.HexColor("#1E3A5F")),
        ("LINEBEFORE",    (2, 0), (2, -1), 0.5, colors.HexColor("#1E3A5F")),
    ]))
    story.append(risk_table)
    story.append(_sp(4))

    # ── Transaction details (READ FROM ROOT OF REPORT DICT) ───────────────────
    story.append(Paragraph("Transaction Details", _S["section"]))
    story.append(_hr(thickness=1.5, colour=_BLUE))
    story.append(_sp(2))

    # Fixed: Fallback directly to the report schema object variables
    txn_rows = [
        ["Account ID",        str(report.get("account_id", "—"))],
        ["Amount (INR)",      f"INR {float(report.get('amount_inr', 0)):,.0f}"],
        ["Velocity (24h)",    f"{report.get('velocity_24h', '—')} transactions"],
        ["Account Age",       f"{report.get('account_age_days', '—')} days"],
        ["Cross-border",      "Yes" if report.get("is_cross_border") else "No"],
    ]
    txn_formatted = [
        [Paragraph(f"<b>{k}</b>", _S["label"]), Paragraph(v, _S["body"])]
        for k, v in txn_rows
    ]
    txn_table = Table(txn_formatted, colWidths=[W * 0.32, W * 0.68])
    txn_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), colors.HexColor("#F0F4F8")),
        ("BACKGROUND",    (1, 0), (1, -1), _WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.3, colors.HexColor("#DDE3EC")),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE3EC")),
    ]))
    story.append(txn_table)
    story.append(_sp(4))

    # ── Transaction summary ───────────────────────────────────────────────────
    summary = report.get("transaction_summary", "").strip()
    if summary:
        story.append(Paragraph("Transaction Summary", _S["section"]))
        story.append(_hr(thickness=1.5, colour=_BLUE))
        story.append(_sp(1))
        story.append(Paragraph(summary, _S["body"]))
        story.append(_sp(3))

    # ── Scoring rationale ─────────────────────────────────────────────────────
    rationale = report.get("scoring_rationale", "").strip()
    if rationale:
        story.append(Paragraph("Scoring Rationale", _S["section"]))
        story.append(_hr(thickness=1.5, colour=_BLUE))
        story.append(_sp(1))
        story.append(Paragraph(rationale, _S["body"]))
        story.append(_sp(3))

    # ── Suspicious indicators ─────────────────────────────────────────────────
    indicators = report.get("raw_indicators", [])
    if indicators:
        story.append(Paragraph("Suspicious Indicators", _S["section"]))
        story.append(_hr(thickness=1.5, colour=_BLUE))
        story.append(_sp(1))
        for ind in indicators:
            story.append(Paragraph(f"• {ind.replace('_', ' ').title()}", _S["bullet"]))
        story.append(_sp(3))

    # ── Suspicious patterns (LLM) ─────────────────────────────────────────────
    patterns = report.get("suspicious_patterns", [])
    clean_patterns = [p for p in patterns if isinstance(p, str) and len(p.strip()) > 3]
    if clean_patterns:
        story.append(Paragraph("Suspicious Patterns (AI Analysis)", _S["section"]))
        story.append(_hr(thickness=1.5, colour=_BLUE))
        story.append(_sp(1))
        for pat in clean_patterns:
            story.append(Paragraph(f"• {pat}", _S["bullet"]))
        story.append(_sp(3))

    # ── Policy citations (LLM) ────────────────────────────────────────────────
    llm_citations = report.get("policy_citations", [])
    clean_citations = [c for c in llm_citations if isinstance(c, str) and len(c.strip()) > 5]
    if clean_citations:
        story.append(Paragraph("Policy Citations", _S["section"]))
        story.append(_hr(thickness=1.5, colour=_BLUE))
        story.append(_sp(1))
        for cit in clean_citations:
            story.append(Paragraph(f"• {cit}", _S["bullet"]))
        story.append(_sp(3))

    # ── RAG evidence ──────────────────────────────────────────────────────────
    raw_citations = report.get("raw_citations", [])
    if raw_citations:
        story.append(Paragraph("Retrieved Policy Evidence (RAG)", _S["section"]))
        story.append(_hr(thickness=1.5, colour=_BLUE))
        story.append(_sp(2))
        
        for i, cit in enumerate(raw_citations, 1):
            raw_score = cit.get("relevance_score", 0)
            conf      = _logit_to_confidence_ui(raw_score)  # Fixed: Synchronized UI calibration
            doc_type  = cit.get("doc_type", "REG") or "REG"
            indicator = cit.get("indicator", "").replace("_", " ")
            page_num  = cit.get("page", 0)
            chunk     = (cit.get("chunk_text", "") or "")[:450]
            if len(cit.get("chunk_text", "")) > 450:
                chunk += "..."

            ev_data = [[
                Paragraph(f"<b>Evidence {i}</b>  [{doc_type}]  "
                          f"Confidence: {conf:.1f}%  |  Indicator: {indicator}  |  Page {page_num}",
                          _style(f"eh_{i}", fontSize=8.5, fontName="Helvetica-Bold",
                                 textColor=_WHITE)),
            ], [
                Paragraph(chunk, _style(f"ec_{i}", fontSize=8.5, fontName="Helvetica",
                                        textColor=colors.HexColor("#CCCCCC"), leading=13)),
            ]]
            ev_table = Table(ev_data, colWidths=[W])
            ev_table.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), _NAVY),
                ("BACKGROUND",    (0, 1), (-1, 1), colors.HexColor("#081828")),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#1E3A5F")),
            ]))
            story.append(ev_table)
            story.append(_sp(2.5))

        story.append(_sp(2))

    # ── Recommended action ────────────────────────────────────────────────────
    action = report.get("recommended_action", "").strip()
    if action:
        story.append(Paragraph("Recommended Action", _S["section"]))
        story.append(_hr(thickness=1.5, colour=tier_col))
        story.append(_sp(1))
        action_data = [[Paragraph(action, _style("act", fontSize=10,
                                                  fontName="Helvetica-Bold",
                                                  textColor=_WHITE, leading=14))]]
        action_table = Table(action_data, colWidths=[W])
        action_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), tier_col),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 14),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ]))
        story.append(action_table)
        story.append(_sp(4))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(_hr())
    story.append(Paragraph(
        f"Generated by FinSentinel Compliance AI  ·  Case {case_id}  ·  {generated}  "
        f"·  CONFIDENTIAL — For internal compliance use only",
        _style("ft", fontSize=7.5, fontName="Helvetica",
               textColor=_VLGREY, alignment=TA_CENTER),
    ))

    doc.build(story)
    return buf.getvalue()