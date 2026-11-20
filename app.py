import io
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Advanced Cotton vs. Polyester Blend Calculator",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Theme ---------------------------------
st.markdown(
    """
    <style>
    .stApp { background: #f6f9fc; }
    .block-container { padding-top: 1.35rem; padding-bottom: 2.2rem; }
    .hero {
      padding: 1.5rem 1.7rem; border-radius: 18px; color: white;
      background: linear-gradient(115deg,#102a43 0%,#176b87 65%,#159a9c 100%);
      margin-bottom: 1rem;
    }
    .hero h1 { color: white; margin: 0; font-size: 2rem; }
    .hero p { color: #e5f4f7; margin: .35rem 0 0; }
    .metric {
      background: white; border: 1px solid #e3ebf2; border-radius: 14px;
      padding: 1rem 1.1rem; min-height: 112px;
      box-shadow: 0 2px 10px rgba(16,42,67,.035);
    }
    .metric-label { color: #607386; font-size: .85rem; }
    .metric-value { color: #102a43; font-size: 1.55rem; font-weight: 750; margin-top: .25rem; }
    .metric-help { color: #8090a0; font-size: .76rem; margin-top: .15rem; }
    .small-muted { color: #607386; font-size: .88rem; }
    div[data-testid="stProgressBar"] > div > div { background: #159a9c; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- Calculation engine -------------------
def score_comfort(cotton_pct: float) -> float:
    """Transparent illustrative score; not a standardized test result."""
    return round(3.5 + 6.0 * cotton_pct / 100.0, 1)


def score_durability(polyester_pct: float) -> float:
    """Transparent illustrative score; not a standardized test result."""
    return round(4.0 + 5.5 * polyester_pct / 100.0, 1)


def calculate(
    cotton_pct: float,
    cotton_price: float,
    polyester_price: float,
    gsm: float,
    width: float,
    waste_pct: float,
    processing_cost: float,
    overhead_pct: float,
):
    polyester_pct = 100.0 - cotton_pct
    net_fabric_mass = gsm * width / 1000.0
    gross_fiber_input = net_fabric_mass / (1.0 - waste_pct / 100.0)
    weighted_price = (
        cotton_pct * cotton_price + polyester_pct * polyester_price
    ) / 100.0
    cotton_mass = gross_fiber_input * cotton_pct / 100.0
    polyester_mass = gross_fiber_input * polyester_pct / 100.0
    cotton_cost = cotton_mass * cotton_price
    polyester_cost = polyester_mass * polyester_price
    raw_cost = cotton_cost + polyester_cost
    overhead_cost = (raw_cost + processing_cost) * overhead_pct / 100.0
    total_cost = raw_cost + processing_cost + overhead_cost
    return {
        "cotton_pct": cotton_pct,
        "polyester_pct": polyester_pct,
        "net_fabric_mass": net_fabric_mass,
        "gross_fiber_input": gross_fiber_input,
        "weighted_price": weighted_price,
        "cotton_mass": cotton_mass,
        "polyester_mass": polyester_mass,
        "cotton_cost": cotton_cost,
        "polyester_cost": polyester_cost,
        "raw_cost": raw_cost,
        "processing_cost": processing_cost,
        "overhead_pct": overhead_pct,
        "overhead_cost": overhead_cost,
        "total_cost": total_cost,
        "comfort": score_comfort(cotton_pct),
        "durability": score_durability(polyester_pct),
    }


def fmt_money(value, currency):
    return f"{currency} {value:,.2f}"


def metric_card(label, value, note=""):
    st.markdown(
        f'<div class="metric"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-help">{note}</div></div>',
        unsafe_allow_html=True,
    )


def build_pdf(result, settings, currency):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
        topMargin=17*mm, bottomMargin=17*mm
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="FinePrint", parent=styles["BodyText"], fontSize=8,
        leading=11, textColor=colors.HexColor("#526477")
    ))
    story = [
        Paragraph("Advanced Cotton vs. Polyester Blend Calculator", styles["Title"]),
        Paragraph("Textile Engineering Department | Student ID: 25TE006", styles["Normal"]),
        Spacer(1, 7*mm),
        Paragraph("Blend and production assumptions", styles["Heading2"]),
    ]
    data = [
        ["Input", "Value"],
        ["Cotton / Polyester", f'{result["cotton_pct"]:.1f}% / {result["polyester_pct"]:.1f}%'],
        ["Fabric GSM / width", f'{settings["gsm"]:.1f} GSM / {settings["width"]:.2f} m'],
        ["Cotton price", f'{currency} {settings["cotton_price"]:,.2f}/kg'],
        ["Polyester price", f'{currency} {settings["polyester_price"]:,.2f}/kg'],
        ["Waste allowance", f'{settings["waste_pct"]:.1f}%'],
        ["Processing cost", f'{currency} {settings["processing_cost"]:,.2f}/m'],
        ["Overhead", f'{settings["overhead_pct"]:.1f}%'],
    ]
    t = Table(data, colWidths=[75*mm, 85*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102A43")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#d9e2ec")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f3f7fa")]),
        ("PADDING",(0,0),(-1,-1),7),
    ]))
    story += [t, Spacer(1, 6*mm), Paragraph("Cost estimate per meter", styles["Heading2"])]
    cost_data = [
        ["Cost component", f"Amount ({currency}/m)"],
        ["Cotton fiber", f'{result["cotton_cost"]:,.2f}'],
        ["Polyester fiber", f'{result["polyester_cost"]:,.2f}'],
        ["Total raw fiber", f'{result["raw_cost"]:,.2f}'],
        ["Processing", f'{result["processing_cost"]:,.2f}'],
        ["Overhead", f'{result["overhead_cost"]:,.2f}'],
        ["Estimated total", f'{result["total_cost"]:,.2f}'],
    ]
    ct = Table(cost_data, colWidths=[75*mm,85*mm])
    ct.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#176B87")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#d9e2ec")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f3f7fa")]),
        ("PADDING",(0,0),(-1,-1),7),
    ]))
    story += [
        ct, Spacer(1, 6*mm),
        Paragraph("Illustrative fiber indicators", styles["Heading2"]),
        Paragraph(
            f'Comfort: {result["comfort"]:.1f}/10 &nbsp;&nbsp; '
            f'Durability: {result["durability"]:.1f}/10',
            styles["BodyText"]
        ),
        Spacer(1, 4*mm),
        Paragraph(
            "Method: net fabric mass per meter = GSM × width ÷ 1000. "
            "Gross fiber input adjusts net mass for the entered waste allowance. "
            "Fiber cost is calculated from the blend percentages and input prices. "
            "Processing cost is added, then overhead is applied to raw fiber plus processing.",
            styles["FinePrint"]
        ),
        Spacer(1, 2*mm),
        Paragraph(
            "Comfort and durability values are simplified educational estimates, "
            "not laboratory test results. Real fabric performance depends on fiber "
            "grade, yarn and fabric construction, finishing, and test conditions. "
            "Cost estimates depend on user inputs and do not replace factory costing.",
            styles["FinePrint"]
        ),
        Spacer(1, 2*mm),
        Paragraph(f"Generated {datetime.now().strftime('%d %b %Y, %H:%M')}", styles["FinePrint"]),
    ]
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


# -------------------------------- Header ------------------------------
st.markdown(
    """
    <div class="hero">
      <h1>🧵 Advanced Cotton vs. Polyester Blend Calculator</h1>
      <p>Textile Engineering Department &nbsp; | &nbsp; Student ID: <b>25TE006</b></p>
      <p>Blend engineering • Material costing • Scenario comparison • Production assumptions</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------- Sidebar -----------------------------
with st.sidebar:
    st.header("⚙️ Production inputs")
    currency = st.selectbox("Currency", ["PKR", "USD", "EUR", "GBP"], index=0)
    st.markdown("**Raw fiber prices**")
    cotton_price = st.number_input(f"Cotton price ({currency}/kg)", 0.0, value=500.0, step=10.0)
    polyester_price = st.number_input(f"Polyester price ({currency}/kg)", 0.0, value=350.0, step=10.0)
    st.markdown("**Fabric specifications**")
    gsm = st.number_input("Fabric GSM", min_value=1.0, value=180.0, step=5.0)
    width = st.number_input("Usable fabric width (m)", min_value=0.01, value=1.50, step=0.05)
    st.markdown("**Production assumptions**")
    waste_pct = st.slider("Fiber waste allowance (%)", 0.0, 30.0, 5.0, 0.5)
    processing_cost = st.number_input(
        f"Processing cost ({currency}/meter)", min_value=0.0, value=25.0, step=1.0
    )
    overhead_pct = st.slider("Overhead on fiber + processing (%)", 0.0, 50.0, 10.0, 0.5)
    st.caption("Use one currency consistently for both fiber prices and all costs.")

# -------------------------------- Blend slider ------------------------
st.subheader("1. Blend composition")
if "adv_cotton_pct" not in st.session_state:
    st.session_state.adv_cotton_pct = 65

cotton_pct = st.slider(
    "Cotton percentage (%)", 0, 100, key="adv_cotton_pct",
    help="Polyester automatically adjusts so the total always equals 100%."
)
poly_pct = 100 - cotton_pct
c1, c2, c3 = st.columns(3)
with c1:
    metric_card("Cotton", f"{cotton_pct}%", "Natural cellulosic fiber")
with c2:
    metric_card("Polyester", f"{poly_pct}%", "Synthetic polymer fiber")
with c3:
    metric_card("Blend validation", "100%", "Cotton + Polyester")
st.caption(f"Composition: {cotton_pct}% cotton + {poly_pct}% polyester = 100%")

current = calculate(
    cotton_pct, cotton_price, polyester_price, gsm, width,
    waste_pct, processing_cost, overhead_pct
)
settings = {
    "cotton_price": cotton_price, "polyester_price": polyester_price,
    "gsm": gsm, "width": width, "waste_pct": waste_pct,
    "processing_cost": processing_cost, "overhead_pct": overhead_pct,
}

# -------------------------------- Dashboard tabs ----------------------
tab_overview, tab_cost, tab_compare, tab_learning = st.tabs(
    ["📊 Overview", "💰 Cost analysis", "⚖️ Blend comparison", "🧶 Fiber guide"]
)

with tab_overview:
    st.subheader("Live calculation dashboard")
    a, b, c, d = st.columns(4)
    with a:
        metric_card("Estimated total cost / m", fmt_money(current["total_cost"], currency), "Includes waste, processing and overhead")
    with b:
        metric_card("Raw fiber cost / m", fmt_money(current["raw_cost"], currency), "Cotton + polyester material")
    with c:
        metric_card("Comfort indicator", f'{current["comfort"]:.1f}/10', "Illustrative blend-based score")
    with d:
        metric_card("Durability indicator", f'{current["durability"]:.1f}/10', "Illustrative blend-based score")

    col_chart, col_rating = st.columns([1.1, 1])
    with col_chart:
        st.markdown("#### Blend composition")
        pie = go.Figure(data=[go.Pie(
            labels=["Cotton", "Polyester"],
            values=[cotton_pct, poly_pct],
            hole=.58,
            marker=dict(colors=["#176B87", "#55B6B0"]),
            textinfo="label+percent",
        )])
        pie.update_layout(height=310, showlegend=False, margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(pie, use_container_width=True)
    with col_rating:
        st.markdown("#### Educational performance indicators")
        st.write(f"**Comfort — {current['comfort']:.1f}/10**")
        st.progress(current["comfort"] / 10)
        st.caption("Cotton is generally more moisture-absorbent; comfort also depends on construction and finishing.")
        st.write(f"**Durability — {current['durability']:.1f}/10**")
        st.progress(current["durability"] / 10)
        st.caption("Polyester can contribute abrasion resistance and dimensional stability; actual results require testing.")
        st.warning("These ratings are illustrative estimates, not standardized test results.")

    st.markdown("#### Fabric specification summary")
    summary = pd.DataFrame([
        ["Fabric mass (net)", f'{current["net_fabric_mass"]:.4f} kg/m'],
        ["Fiber input (after waste allowance)", f'{current["gross_fiber_input"]:.4f} kg/m'],
        ["Weighted raw fiber price", f'{current["weighted_price"]:,.2f} {currency}/kg'],
        ["Waste allowance", f'{waste_pct:.1f}%'],
        ["Usable width", f'{width:.2f} m'],
        ["Fabric weight", f'{gsm:.1f} GSM'],
    ], columns=["Parameter", "Value"])
    st.dataframe(summary, use_container_width=True, hide_index=True)

with tab_cost:
    st.subheader("Detailed cost breakdown")
    st.markdown("All amounts are estimates per meter of finished fabric.")
    cost_df = pd.DataFrame({
        "Component": ["Cotton fiber", "Polyester fiber", "Processing", "Overhead"],
        "Cost": [
            current["cotton_cost"], current["polyester_cost"],
            current["processing_cost"], current["overhead_cost"]
        ],
    })
    cost_df["Share (%)"] = cost_df["Cost"].apply(
        lambda x: (x / current["total_cost"] * 100) if current["total_cost"] else 0
    )
    k1, k2 = st.columns(2)
    with k1:
        st.dataframe(
            cost_df.assign(**{
                f"Cost ({currency}/m)": cost_df["Cost"].round(2),
                "Share (%)": cost_df["Share (%)"].round(1),
            })[["Component", f"Cost ({currency}/m)", "Share (%)"]],
            use_container_width=True, hide_index=True
        )
    with k2:
        bar = px.bar(
            cost_df, x="Component", y="Cost", color="Component",
            title=f"Cost contribution ({currency}/m)",
            color_discrete_sequence=["#176B87", "#55B6B0", "#79A7C7", "#9AB8C9"],
        )
        bar.update_layout(showlegend=False, margin=dict(l=5,r=5,t=45,b=5))
        st.plotly_chart(bar, use_container_width=True)
    st.metric("Estimated total cost per meter", fmt_money(current["total_cost"], currency))
    with st.expander("Show calculation formulas"):
        st.code(
            f"Net fabric mass = GSM × width ÷ 1000\n"
            f"                 = {gsm:.1f} × {width:.2f} ÷ 1000\n"
            f"                 = {current['net_fabric_mass']:.4f} kg/m\n\n"
            f"Gross fiber input = net mass ÷ (1 - waste%/100)\n"
            f"                   = {current['gross_fiber_input']:.4f} kg/m\n\n"
            f"Cotton cost = gross input × cotton% × cotton price\n"
            f"Polyester cost = gross input × polyester% × polyester price\n"
            f"Overhead = (raw fiber cost + processing) × overhead%\n"
            f"Total = raw fiber cost + processing + overhead\n"
            f"Total = {current['total_cost']:.2f} {currency}/m"
        )
    st.caption("The waste allowance is modeled as a fraction of gross fiber input: net fabric mass = gross input × (1 − waste rate).")

with tab_compare:
    st.subheader("Compare multiple blend scenarios")
    st.write("Select standard blends and/or enter custom cotton percentages. Current prices and production settings apply to every scenario.")
    preset = {
        "100/0": 100, "80/20": 80, "65/35": 65,
        "50/50": 50, "35/65": 35, "0/100": 0,
    }
    chosen = st.multiselect(
        "Standard blends (Cotton / Polyester)",
        options=list(preset.keys()),
        default=["100/0", "65/35", "50/50", "0/100"],
    )
    custom_text = st.text_input(
        "Optional custom cotton percentages, comma-separated",
        placeholder="Example: 72, 45, 25",
        help="Enter values from 0 to 100. Polyester is calculated as the remainder."
    )
    compare_values = [preset[x] for x in chosen]
    custom_errors = []
    if custom_text.strip():
        for item in custom_text.split(","):
            try:
                val = float(item.strip())
                if not 0 <= val <= 100:
                    raise ValueError
                compare_values.append(val)
            except ValueError:
                custom_errors.append(item.strip())
    if custom_errors:
        st.error("Could not read these custom values (enter numbers from 0 to 100): " + ", ".join(custom_errors))

    # Keep order while removing duplicates.
    compare_values = list(dict.fromkeys(compare_values))
    compare_rows = []
    for cp in compare_values:
        r = calculate(cp, cotton_price, polyester_price, gsm, width, waste_pct, processing_cost, overhead_pct)
        compare_rows.append({
            "Blend": f"{cp:g}% Cotton / {100-cp:g}% Polyester",
            "Cotton (%)": cp,
            "Polyester (%)": 100-cp,
            f"Raw fiber ({currency}/m)": round(r["raw_cost"], 2),
            f"Total ({currency}/m)": round(r["total_cost"], 2),
            "Comfort (/10)": r["comfort"],
            "Durability (/10)": r["durability"],
        })
    if compare_rows:
        compare_df = pd.DataFrame(compare_rows)
        st.dataframe(compare_df, use_container_width=True, hide_index=True)
        chart = px.bar(
            compare_df, x="Blend",
            y=[f"Raw fiber ({currency}/m)", f"Total ({currency}/m)"],
            barmode="group", title="Cost comparison by blend",
            color_discrete_sequence=["#176B87", "#55B6B0"],
        )
        chart.update_layout(xaxis_tickangle=-25, margin=dict(l=5,r=5,t=50,b=90))
        st.plotly_chart(chart, use_container_width=True)
        csv = compare_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download comparison as CSV", data=csv,
            file_name="blend_comparison.csv", mime="text/csv"
        )
    else:
        st.info("Choose at least one standard blend or add a custom cotton percentage.")

    st.markdown("#### Target-cost blend explorer")
    target = st.number_input(
        f"Target total cost ({currency}/meter)",
        min_value=0.0, value=float(round(current["total_cost"], 2)), step=5.0
    )
    cost_0 = calculate(0, cotton_price, polyester_price, gsm, width, waste_pct, processing_cost, overhead_pct)["total_cost"]
    cost_100 = calculate(100, cotton_price, polyester_price, gsm, width, waste_pct, processing_cost, overhead_pct)["total_cost"]
    low, high = min(cost_0, cost_100), max(cost_0, cost_100)
    if low - 1e-8 <= target <= high + 1e-8 and abs(cost_100 - cost_0) > 1e-8:
        # Cost is linear in cotton percentage under the model assumptions.
        target_cotton = (target - cost_0) * 100 / (cost_100 - cost_0)
        st.success(
            f"Estimated blend at the target: {target_cotton:.1f}% cotton / "
            f"{100-target_cotton:.1f}% polyester."
        )
        st.caption("This is a mathematical estimate under the entered prices and assumptions, not a product recommendation.")
    elif abs(cost_100 - cost_0) <= 1e-8:
        st.info("The model estimates the same cost at every blend ratio with the current input prices.")
    else:
        st.warning(
            f"Target is outside the modeled blend-cost range "
            f"({fmt_money(low, currency)} to {fmt_money(high, currency)} per meter)."
        )

with tab_learning:
    st.subheader("Fiber guide and interpretation")
    f1, f2 = st.columns(2)
    with f1:
        st.markdown("### 🌿 Cotton")
        st.write(
            "- Natural cellulosic fiber obtained from the cotton plant.\n"
            "- Generally has good moisture absorption.\n"
            "- Often selected for a soft, familiar hand feel.\n"
            "- Can wrinkle and may shrink unless controlled by construction and finishing."
        )
    with f2:
        st.markdown("### 🧪 Polyester")
        st.write(
            "- Synthetic fiber produced from polymer materials.\n"
            "- Generally has low moisture regain and dries relatively quickly.\n"
            "- Often contributes crease recovery and abrasion resistance.\n"
            "- Can improve dimensional stability in many blended constructions."
        )
    st.markdown("### What blend ratios can indicate")
    st.write(
        "Increasing cotton share generally increases the contribution of cotton's "
        "moisture-absorbing characteristics. Increasing polyester share generally "
        "increases polyester's contribution to quick drying, crease recovery and "
        "abrasion resistance. The actual outcome depends on yarn count, twist, "
        "spinning system, weave or knit structure, fabric density, dyeing and finishing."
    )
    st.info(
        "For technical product decisions, validate performance using relevant "
        "standardized tests (for example, tensile, abrasion, pilling, dimensional "
        "stability and moisture-management tests). The app's comfort and durability "
        "scores are deliberately simplified teaching indicators."
    )

# -------------------------------- Export ------------------------------
st.divider()
st.subheader("5. Export current calculation")
st.write("Download a PDF report containing current blend settings, assumptions, cost breakdown and illustrative ratings.")
try:
    pdf_data = build_pdf(current, settings, currency)
    st.download_button(
        "📄 Download current calculation report (PDF)",
        data=pdf_data,
        file_name="advanced_cotton_polyester_blend_report.pdf",
        mime="application/pdf",
    )
except ImportError:
    st.error("PDF export dependency is missing. Install packages from requirements.txt.")

st.caption(
    "Advanced educational project | Textile Engineering Department | Student ID: 25TE006. "
    "Estimates depend on user-entered prices, fabric specifications and assumptions."
)
