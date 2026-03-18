import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# ======================================================
# 1. CONFIGURACIÓN Y ESTADO
# ======================================================
st.set_page_config(page_title="Pro Quote Master", layout="wide")
FLOORS = ["Basement", "Floor 1", "Floor 2", "Floor 3", "Floor 4", "Floor 5"]

if "rooms" not in st.session_state: st.session_state.rooms = []
if "stairs" not in st.session_state: st.session_state.stairs = []

EQUIPMENT_OPTIONS = ["Truck mount", "Portable", "Cimex"]
PRODUCT_OPTIONS = ["Procyon", "Citrus", "Releasit", "Flex", "Bio Break", "Boost All", "Pure O2", "Eco Cide", "Petzap IQ", "Groutmaster", "Triplephase"]

def safe_sum(data, key):
    if not data: return 0
    return pd.to_numeric(pd.DataFrame(data)[key], errors='coerce').fillna(0).sum()

# ======================================================
# 2. PHASE 1: PHYSICAL WALKTHROUGH (UNIFICADA)
# ======================================================
st.title("📏 Inspection & Quote Master")
st.subheader("📍 Phase 1: Physical Walkthrough")

d_col1, d_col2 = st.columns(2)

with d_col1:
    with st.container(border=True):
        st.write("**Rooms & Floor Spaces**")
        f_level = st.selectbox("Select Floor Level", FLOORS)
        with st.form("room_form", clear_on_submit=True):
            r_name = st.text_input("Room Name", placeholder="Living Room, Suite A...")
            c_dim1, c_dim2 = st.columns(2)
            rw = c_dim1.text_input("Width (ft)")
            rl = c_dim2.text_input("Length (ft)")
            if st.form_submit_button("➕ Add Area"):
                try:
                    area = float(rw) * float(rl)
                    st.session_state.rooms.append({"floor": f_level, "name": r_name, "w": rw, "l": rl, "area": int(area)})
                except: st.error("Invalid dimensions")
        
        if st.session_state.rooms:
            df_rooms = pd.DataFrame(st.session_state.rooms)
            edited_r = st.data_editor(df_rooms, num_rows="dynamic", use_container_width=True, key="editor_rooms")
            st.session_state.rooms = edited_r.to_dict(orient="records")

with d_col2:
    with st.container(border=True):
        st.write("**Stairs & Landings**")
        with st.form("stair_form", clear_on_submit=True):
            c_st1, c_st2 = st.columns(2)
            s_from = c_st1.selectbox("From Level", FLOORS)
            s_to = c_st2.selectbox("To Level", FLOORS)
            s_steps = st.text_input("Steps Count")
            st.write("---")
            st.write("**Landing Area (W x L):**")
            l_c1, l_c2 = st.columns(2)
            lw = l_c1.text_input("W")
            ll = l_c2.text_input("L")
            if st.form_submit_button("➕ Add Stairs"):
                try:
                    l_area = float(lw or 0) * float(ll or 0)
                    st.session_state.stairs.append({
                        "name": f"{s_from} to {s_to}", 
                        "steps": int(s_steps or 0), 
                        "l_w": lw or "0", 
                        "l_l": ll or "0", 
                        "l_area": int(l_area)
                    })
                except: st.error("Invalid input")
        
        if st.session_state.stairs:
            df_stairs = pd.DataFrame(st.session_state.stairs)
            edited_s = st.data_editor(df_stairs, num_rows="dynamic", use_container_width=True, key="editor_stairs")
            st.session_state.stairs = edited_s.to_dict(orient="records")

st.divider()

# ======================================================
# 3. PHASE 2: LOGISTICS (DINÁMICA SEGÚN TIPO)
# ======================================================
st.subheader("⚙️ Phase 2: Technical Strategy & Logistics")
p_type = st.radio("Select Project Type:", ["House", "Office"], horizontal=True)

s1, s2, s3 = st.columns(3)

with s1:
    with st.container(border=True):
        st.write("**Labor Assignment**")
        techs = st.text_input("Technicians Assigned", placeholder="e.g. 2")
        hours = st.text_input("Estimated Hours", placeholder="e.g. 4.5")
        shift = ""
        if p_type == "Office":
            shift = st.selectbox("Shift Schedule", ["Regular Hours", "After Hours", "Weekends"])

with s2:
    with st.container(border=True):
        if p_type == "Office":
            st.write("**Logistics & Access**")
            water = st.checkbox("Water Source Provided", value=True)
            elev = st.checkbox("Elevator Access")
            parking = st.radio("Parking Status", ["Easy", "Medium", "Difficult"], horizontal=True)
            soil = st.radio("Soil Level", ["Light", "Medium", "Heavy Restoration"], horizontal=True)
        else:
            st.write("**Home Conditions**")
            soil = st.radio("Soil Level", ["Light", "Medium", "Heavy Restoration"], horizontal=True)
            pet_stains = st.checkbox("Pet Stains/Odors Present?")
            parking = st.radio("Parking", ["Street", "Driveway"], horizontal=True)

with s3:
    with st.container(border=True):
        st.write("**Technical Strategy**")
        selected_eq = [eq for eq in EQUIPMENT_OPTIONS if st.checkbox(eq, key=f"cb_{eq}")]
        selected_chem = st.multiselect("Chemistry Suggested", PRODUCT_OPTIONS)
        notes = st.text_area("Field Notes (Technical Observations):")

# ======================================================
# 4. GENERACIÓN DE REPORTES DIFERENCIADOS
# ======================================================
total_rooms_sqft = safe_sum(st.session_state.rooms, 'area')
total_steps_count = safe_sum(st.session_state.stairs, 'steps')
total_landing_sqft = safe_sum(st.session_state.stairs, 'l_area')
global_surface = int(total_rooms_sqft + total_landing_sqft)

if p_type == "Office":
    # --- REPORTE OFFICE (CORPORATIVO) ---
    report = [
        f"*** OFFICE SERVICE INSPECTION & QUOTE ***",
        f"Date: 03/18/2026",
        "--------------------------------------------------------------",
        "I. SCOPE OF WORK SUMMARY",
        f" - Total Surface Area: {global_surface} sq ft",
        f" - Total Steps: {int(total_steps_count)}",
        f" - Soil Level: {soil}",
        "--------------------------------------------------------------",
        "II. LABOR & ESTIMATED TIME",
        f" - Technicians Assigned: {techs if techs else '0'} Specialists",
        f" - Estimated Production Time: {hours if hours else '0'} Hours",
        f" - Shift Schedule: {shift}",
        "--------------------------------------------------------------",
        "III. LOGISTICS & SITE ACCESS",
        f" - Water Source: {'Provided on-site' if water else 'To be determined'}",
        f" - Elevator Access: {'Yes' if elev else 'No'}",
        f" - Parking: {parking}",
        "--------------------------------------------------------------",
        "IV. TECHNICAL STRATEGY",
        f" - Equipment: {', '.join(selected_eq) if selected_eq else 'None'}",
        f" - Chemistry Suggested: {', '.join(selected_chem) if selected_chem else 'None'}",
        f" - Field Notes: {notes if notes else 'No specific observations.'}",
        "--------------------------------------------------------------"
    ]
else:
    # --- REPORTE HOUSE (RESIDENCIAL) ---
    report = [
        f"*** RESIDENTIAL CLEANING ESTIMATE ***",
        f"Date: 03/18/2026",
        "--------------------------------------------------------------",
        "SUMMARY OF AREAS",
        f" - Total Surface to Clean: {global_surface} sq ft",
        f" - Total Steps: {int(total_steps_count)}",
        f" - Soil Condition: {soil}",
        f" - Pet Treatment: {'Required' if pet_stains else 'Not requested'}",
        "--------------------------------------------------------------",
        "SERVICE DETAILS",
        f" - Estimated Time: {hours if hours else '0'} Hours",
        f" - Equipment: {', '.join(selected_eq) if selected_eq else 'Standard'}",
        f" - Products: {', '.join(selected_chem) if selected_chem else 'Eco-friendly Professional'}",
        "--------------------------------------------------------------",
        "TECHNICAL NOTES",
        f"> {notes if notes else 'Areas ready for professional cleaning.'}",
        "--------------------------------------------------------------"
    ]

# Sección común: Desglose Matemático
report.append("DETAILED BREAKDOWN:")
for f in FLOORS:
    f_rooms = [r for r in st.session_state.rooms if r.get('floor') == f]
    if f_rooms:
        report.append(f"\n[{f.upper()}]")
        for r in f_rooms:
            report.append(f" - {r.get('name', 'Area')}: {r.get('w',0)}ft x {r.get('l',0)}ft = {int(r.get('area',0))} sq ft")

if st.session_state.stairs:
    report.append("\n[STAIRS & LANDINGS]")
    for s in st.session_state.stairs:
        if s.get('steps', 0) > 0 or s.get('l_area', 0) > 0:
            report.append(f" - {s.get('name')}: {int(s.get('steps',0))} steps | Landing: {s.get('l_w',0)}ft x {s.get('l_l',0)}ft = {int(s.get('l_area',0))} sq ft")

report.append("--------------------------------------------------------------")
summary_text = "\n".join(report)

# ======================================================
# 5. UI: REPORTE FINAL Y BOTONES
# ======================================================
st.divider()
with st.container(border=True):
    st.subheader(f"📋 Final Report: {p_type}")
    st.text_area("Ready for Client:", summary_text, height=450)
    components.html(f"""
        <button style="padding:12px;background-color:#007bff;color:white;border:none;border-radius:6px;width:100%;font-weight:bold;cursor:pointer;font-family:sans-serif;"
        onclick="navigator.clipboard.writeText(`{summary_text}`); this.innerText='✓ Report Copied to Clipboard'; this.style.backgroundColor='#28a745';">
        📎 Copy Executive Report</button>""", height=70)

if st.button("🗑️ Reset All Data"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()
