import streamlit as st
import streamlit.components.v1 as components
import re

st.set_page_config(page_title="Tech Service Report", layout="wide")
st.title("🛠️ Tech Service Report & Audit")

# --------------------------
# SESSION STATE
# --------------------------
if "template_text" not in st.session_state:
    st.session_state.template_text = ""
if "final_report" not in st.session_state:
    st.session_state.final_report = ""
if "audit_lines_h" not in st.session_state:
    st.session_state.audit_lines_h = []
if "audit_lines_s" not in st.session_state:
    st.session_state.audit_lines_s = []

# --------------------------
# STEP 1: GENERATE MASTER TEMPLATE
# --------------------------
f_count = st.number_input("Total Floors", min_value=1, value=3)
s_count = st.number_input("Stairwells", min_value=0, value=2)

if st.button("Generate Master Template"):
    temp = [
        "--- CONFIGURATION (DO NOT DELETE) ---",
        "Rate SQFT: 0.30",
        "Rate Step: 3.50",
        "---------------------------------------",
        f"Building: [Name]",
        "Type: Commercial",
        f"Total Floors: {f_count}"
    ]
    for i in range(1, f_count+1):
        temp.append(f"Floor {i}:")
        temp.append("0x0")
    for s in range(1, s_count+1):
        temp.append(f"Stairwell {s}:")
        temp.append("Basement → 1")
        temp.append("0 steps")
        temp.append("0x0")
        for f in range(1, f_count):
            temp.append(f"{f} → {f+1}")
            temp.append("0 steps")
            temp.append("0x0")
    st.session_state.template_text = "\n".join(temp)

if st.session_state.template_text:
    st.text_area("Master Template", st.session_state.template_text, height=300)

# --------------------------
# STEP 2: PROCESS INPUT
# --------------------------
user_input = st.text_area("Paste your data here", height=300)

if st.button("Generate Final Report"):
    if user_input.strip():
        lines = user_input.splitlines()
        c_rate_sqft = 0.30
        c_rate_step = 3.50
        h_sqft_total = 0
        t_steps_total = 0

        breakdown = {}  # por piso y stairwell

        for line in lines:
            clean = line.strip()
            if not clean or clean.startswith("#"): 
                continue
            if "Rate SQFT" in clean:
                m = re.search(r"(\d+\.?\d*)", clean)
                if m: c_rate_sqft = float(m.group(1))
                continue
            if "Rate Step" in clean:
                m = re.search(r"(\d+\.?\d*)", clean)
                if m: c_rate_step = float(m.group(1))
                continue

            # Floors
            floor_match = re.match(r"Floor (\d+): (.+)", clean)
            if floor_match:
                floor_num = int(floor_match.group(1))
                details = floor_match.group(2).split("+")
                sqft_total = 0
                formula = []
                for d in details:
                    dims = re.findall(r"(\d+\.?\d*)x(\d+\.?\d*)", d)
                    for w,l in dims:
                        val = float(w)*float(l)
                        sqft_total += val
                        formula.append(f"{w}x{l}")
                subtotal = sqft_total*c_rate_sqft
                breakdown[f"Floor {floor_num}"] = {"formula": " + ".join(formula), "sqft": sqft_total, "subtotal": subtotal}
                h_sqft_total += sqft_total
                continue

            # Stairwells
            stair_match = re.match(r"(Stairwell \d+) \((.+?)\): (.+) \+ (\d+) steps", clean)
            if stair_match:
                stair_name = stair_match.group(1)
                path = stair_match.group(2)
                dims = stair_match.group(3)
                steps = int(stair_match.group(4))
                sqft_total = 0
                formula = []
                dims_found = re.findall(r"(\d+\.?\d*)x(\d+\.?\d*)", dims)
                for w,l in dims_found:
                    val = float(w)*float(l)
                    sqft_total += val
                    formula.append(f"{w}x{l}")
                subtotal = sqft_total*c_rate_sqft + steps*c_rate_step
                key = f"{stair_name} ({path})"
                breakdown[key] = {"formula": " + ".join(formula), "sqft": sqft_total, "steps": steps, "subtotal": subtotal}
                t_steps_total += steps
                continue

        # --------------------------
        # Crear auditoría amigable
        # --------------------------
        audit_lines_h = []
        audit_lines_s = []
        for k,v in breakdown.items():
            if k.startswith("Floor"):
                audit_lines_h.append(f"{k}: {v['formula']} = {v['sqft']:.2f} ft² | Subtotal: ${v['subtotal']:.2f}")
            else:
                audit_lines_s.append(f"{k}: {v['formula']} ({v['sqft']:.2f} ft²) + {v['steps']} steps = ${v['subtotal']:.2f}")

        st.session_state.audit_lines_h = audit_lines_h
        st.session_state.audit_lines_s = audit_lines_s

        # --------------------------
        # Final Report completo
        # --------------------------
        report = ["🔍 1. Audit Dashboard (Friendly View)", "🏢 Hallways & Floors"]
        report += audit_lines_h
        report.append("🪜 Staircases (Landings & Steps)")
        report += audit_lines_s
        report.append(f"\nTotal Hallways ft²: {h_sqft_total:.2f}")
        report.append(f"Total Steps: {t_steps_total}")
        st.session_state.final_report = "\n".join(report)

# --------------------------
# VISUALIZACIÓN + BOTÓN COPIAR
# --------------------------
if st.session_state.final_report:
    st.text_area("📋 Final Tech Report", st.session_state.final_report, height=400)

    safe_text = st.session_state.final_report.replace("`","\\`").replace("\n","\\n")
    components.html(f"""
    <button
        id="copyBtn"
        style="padding:8px 16px;font-size:16px;background-color:#1f77b4;color:white;
               border:none;border-radius:4px;cursor:pointer;"
        onclick="
            var textArea = document.createElement('textarea');
            textArea.value = `{safe_text}`;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            const btn = document.getElementById('copyBtn');
            btn.innerText='✅ Copied';
            btn.style.backgroundColor='#2ca02c';
        "
    >
        📎 Copy Final Report
    </button>
    """, height=50)
