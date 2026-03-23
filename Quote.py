import streamlit as st
import streamlit.components.v1 as components
import re

st.set_page_config(page_title="Tech Service Report", layout="wide")
st.title("🛠️ Tech Service Report & Audit")

# --- SESSION STATE ---
if "template_text" not in st.session_state:
    st.session_state["template_text"] = ""
if "final_report" not in st.session_state:
    st.session_state["final_report"] = ""
if "audit_lines_h" not in st.session_state:
    st.session_state["audit_lines_h"] = []
if "audit_lines_s" not in st.session_state:
    st.session_state["audit_lines_s"] = []

# --- MAIN INTERFACE ---
col_gen, col_paste = st.columns([1, 2])

with col_gen:
    st.subheader("Step 1: Setup")
    f_count = st.number_input("Total Floors", min_value=1, value=3)
    s_count = st.number_input("Stairwells", min_value=0, value=2)
    
    if st.button("Generate Master Template"):
        temp = [
            "--- CONFIGURATION (DO NOT DELETE) ---",
            "Rate SQFT: 0.30",
            "Rate Step: 3.50",
            "---------------------------------------",
            f"\nBuilding: [Name]", 
            "Type: Commercial", 
            f"Total Floors: {f_count}\n"
        ]
        for i in range(1, f_count + 1):
            temp.append(f"Floor {i}:")
            temp.append("0x0\n")
        for s in range(1, s_count + 1):
            temp.append(f"Stairwell {s}:")
            temp.append("Basement → 1")
            temp.append("0 steps")
            temp.append("0x0\n")
            for f in range(1, f_count):
                temp.append(f"{f} → {f+1}")
                temp.append("0 steps")
                temp.append("0x0\n")
            temp.append(f"{f_count} → Roof")
            temp.append("0 steps")
            temp.append("0x0\n")
        
        temp.extend([
            "Logistics & Site Resources:",
            "Technicians: 0",
            "Estimated Hours: 0",
            "xParking", "xWater Access", "xElectricity", "xBathroom", "xElevator", "xLaundry Room",
            "\nEquipment Checklist:",
            "#Truck Mount", "#Portable", "#Cimex",
            "\nSoil Level Assessment:",
            "Light", "xMedium", "xHeavy",
            "\nAdditional Notes:"
        ])
        st.session_state["template_text"] = "\n".join(temp)
    
    if st.session_state["template_text"]:
        st.text_area("Master Template:", st.session_state["template_text"], height=400)

with col_paste:
    st.subheader("Step 2: Process Data")
    user_input = st.text_area("Input Area (Paste here)", height=415)
    
    if st.button("Generate Final Tech Report"):
        if user_input.strip():
            # --- Simulación de procesamiento para ejemplo ---
            st.session_state.final_report = f"Processed report for building:\n{user_input}"

# --- FINAL REPORT VISUALIZATION ---
if st.session_state.final_report:
    st.markdown("---")
    st.subheader("📋 Final Tech Report")
    st.text_area("You can review it here:", st.session_state.final_report, height=350)

    # --- BOTÓN DE COPIADO COMPATIBLE CON IPAD/IPHONE ---
    # Método: textarea temporal + execCommand('copy')
    safe_text = st.session_state.final_report.replace("`", "\\`").replace("\n", "\\n")
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
