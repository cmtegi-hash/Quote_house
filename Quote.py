import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# ======================================================
# Configuración de Página
# ======================================================
st.set_page_config(page_title="Quote Generator", layout="wide")
FLOORS = ["Basement", "Floor 1", "Floor 2", "Floor 3", "Floor 4", "Floor 5"]

# ======================================================
# Inicialización de Estado (Session State)
# ======================================================
if "rooms" not in st.session_state: st.session_state.rooms = []
if "stairs" not in st.session_state: st.session_state.stairs = []
if "active_floor" not in st.session_state: st.session_state.active_floor = "Floor 1"
if "notes" not in st.session_state: st.session_state.notes = ""

if "site_info" not in st.session_state: 
    st.session_state.site_info = {"laundry": False, "water": False, "bathroom": False, "elevator": False}

EQUIPMENT_OPTIONS = ["Truck mount", "Portable", "Cimex"]
PRODUCT_OPTIONS = [
    "Procyon", "Citrus", "Releasit", "Flex", "Bio Break", "Boost All", 
    "Pure O2", "Eco Cide", "Petzap IQ", "Wool Medic", "Groutmaster", 
    "Triplephase", "Volume 40", "Spot Stop", "Green Guard", "Rob Solvent"
]

# ======================================================
# Funciones Lógicas
# ======================================================
def add_room():
    try:
        name = st.session_state.room_name.strip()
        width = float(st.session_state.width_input)
        length = float(st.session_state.length_input)
        if name:
            st.session_state.rooms.append({
                "floor": st.session_state.active_floor,
                "name": name,
                "width": width,
                "length": length,
                "include": st.session_state.include_input
            })
            st.session_state.room_name = ""; st.session_state.width_input = ""; st.session_state.length_input = ""
    except ValueError: st.error("Invalid dimensions.")

def add_stair():
    try:
        steps = int(st.session_state.steps_input)
        l_area = 0
        if st.session_state.has_landing:
            l_area = float(st.session_state.l_width) * float(st.session_state.l_length)
        st.session_state.stairs.append({
            "name": f"{st.session_state.s_from} to {st.session_state.s_to}",
            "steps": steps,
            "landing_area": round(l_area, 2)
        })
        st.session_state.steps_input = ""; st.session_state.l_width = ""; st.session_state.l_length = ""
    except ValueError: st.error("Invalid stairs input.")

# ======================================================
# UI - SECCIÓN SUPERIOR
# ======================================================
st.title("📐 Quote & Area Calculator")

col1, col2 = st.columns([1, 1.2])

with col1:
    # CUADRO: PROJECT SETUP
    with st.container(border=True):
        st.subheader("📋 Project Setup")
        project_type = st.radio("Type of Project", ["House", "Office"], horizontal=True)
        report_main_title = "HOUSE" if project_type == "House" else "OFFICE"
        
        office_schedule = ""
        if project_type == "Office":
            st.write("**Service Schedule**")
            office_schedule = st.radio("Timing:", ["Weekdays (Regular)", "After Hours", "Weekends"], horizontal=True, label_visibility="collapsed")
        
        st.write("**Observations/Notes**")
        st.text_area("Notes:", key="notes", height=80, label_visibility="collapsed", placeholder="Add any special instructions...")

    # CUADRO: SITE ACCESS & LOGISTICS (ACTUALIZADO CON HORAS Y TÉCNICOS)
    with st.container(border=True):
        st.subheader("🚚 Logistics & Labor")
        
        # --- NUEVA SECCIÓN DE LABOR ---
        c_l1, c_l2 = st.columns(2)
        techs = c_l1.text_input("Number of Technicians", placeholder="e.g. 2")
        hours = c_l2.text_input("Estimated Hours", placeholder="e.g. 4.5")
        st.divider()
        
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            st.write("**Access**")
            st.session_state.site_info["laundry"] = st.checkbox("Laundry", value=st.session_state.site_info["laundry"])
            st.session_state.site_info["water"] = st.checkbox("Water", value=st.session_state.site_info["water"])
            st.session_state.site_info["bathroom"] = st.checkbox("Bathroom", value=st.session_state.site_info["bathroom"])
            st.session_state.site_info["elevator"] = st.checkbox("Elevator", value=st.session_state.site_info["elevator"])
        with c_s2:
            st.write("**Parking**")
            parking = st.radio("P_Select", ["Easy", "Medium", "Difficult"], horizontal=False, label_visibility="collapsed")
            st.write("**Dirt Level**")
            dirt = st.radio("D_Select", ["Light", "Medium", "Heavy"], horizontal=False, label_visibility="collapsed")

with col2:
    # CUADRO: EQUIPMENT & PRODUCTS
    with st.container(border=True):
        st.subheader("🛠️ Tools & Chemicals")
        
        st.write("**Equipment Used:**")
        eq_cols = st.columns(3)
        selected_equip = []
        for i, opt in enumerate(EQUIPMENT_OPTIONS):
            if eq_cols[i % 3].checkbox(opt, key=f"check_eq_{opt}"):
                selected_equip.append(opt)
        
        st.divider()
        
        st.write("**Products Applied:**")
        pr_cols = st.columns(4)
        selected_prod = []
        for i, opt in enumerate(PRODUCT_OPTIONS):
            if pr_cols[i % 4].checkbox(opt, key=f"check_pr_{opt}"):
                selected_prod.append(opt)

st.divider()

# ======================================================
# UI - DATOS
# ======================================================
d_col1, d_col2 = st.columns(2)

with d_col1:
    with st.container(border=True):
        st.subheader("🏠 Rooms Breakdown")
        st.selectbox("Select Floor", FLOORS, key="active_floor")
        with st.form("room_form", clear_on_submit=True):
            st.text_input("Room Name", key="room_name")
            c_dim1, c_dim2 = st.columns(2)
            c_dim1.text_input("Width (ft)", key="width_input")
            c_dim2.text_input("Length (ft)", key="length_input")
            st.checkbox("Include in total", key="include_input", value=True)
            st.form_submit_button("Add Room", on_click=add_room)
        
        if st.session_state.rooms:
            df_r = pd.DataFrame(st.session_state.rooms)
            df_r["area"] = (df_r["width"] * df_r["length"]).astype(int)
            edited_r = st.data_editor(df_r, num_rows="dynamic", use_container_width=True, key="ed_rooms")
            st.session_state.rooms = edited_r.to_dict(orient="records")
        else: edited_r = pd.DataFrame()

with d_col2:
    with st.container(border=True):
        st.subheader("🪜 Stairs & Landings")
        with st.form("stair_form", clear_on_submit=True):
            c_st1, c_st2 = st.columns(2)
            c_st1.selectbox("From", FLOORS, key="s_from")
            c_st2.selectbox("To", FLOORS, key="s_to")
            st.text_input("Steps Count", key="steps_input")
            st.checkbox("Has Landing?", key="has_landing", value=True)
            c_l1, c_l2 = st.columns(2)
            c_l1.text_input("Landing W", key="l_width")
            c_l2.text_input("Landing L", key="l_length")
            st.form_submit_button("Add Stairs", on_click=add_stair)
        
        if st.session_state.stairs:
            edited_s = st.data_editor(pd.DataFrame(st.session_state.stairs), num_rows="dynamic", use_container_width=True, key="ed_stairs")
            st.session_state.stairs = edited_s.to_dict(orient="records")
        else: edited_s = pd.DataFrame()

# ======================================================
# CÁLCULOS Y REPORTE
# ======================================================
total_carpet_area = 0; total_steps = 0; total_landing_area = 0

if not edited_r.empty:
    total_carpet_area = edited_r[edited_r["include"]]["area"].sum()

if not edited_s.empty:
    total_steps = pd.to_numeric(edited_s["steps"], errors='coerce').fillna(0).sum()
    total_landing_area = pd.to_numeric(edited_s["landing_area"], errors='coerce').fillna(0).sum()

def get_status(key): return "Yes" if st.session_state.site_info.get(key) else "No"

proj_info_str = report_main_title
if project_type == "Office":
    proj_info_str += f" ({office_schedule.upper()})"

report = [
    f"*** {report_main_title} REPORT ***",
    "===============================",
    f"TOTAL CARPET AREA: {int(total_carpet_area)} sq ft",
    f"TOTAL LANDINGS: {int(total_landing_area)} sq ft",
    f"TOTAL STEPS: {int(total_steps)}",
    "===============================",
    # LÍNEA DE LABOR AÑADIDA AL REPORTE
    f"LABOR: {techs if techs else '0'} Technician(s) | EST. TIME: {hours if hours else '0'} Hours",
    "===============================",
    f"NOTES: {st.session_state.notes if st.session_state.notes else 'None'}",
    "-------------------------------",
    f"PROJECT TYPE: {proj_info_str}",
    f"Dirt Level: {dirt} | Parking: {parking}",
    f"Equipment: {', '.join(selected_equip) if selected_equip else 'None'}",
    f"Products: {', '.join(selected_prod) if selected_prod else 'None'}",
    "-------------------------------",
    "SITE ACCESS:",
    f" - Laundry: {get_status('laundry')}",
    f" - Water: {get_status('water')}",
    f" - Bathroom: {get_status('bathroom')}",
    f" - Elevator: {get_status('elevator')}",
    "-------------------------------",
    "DETAILED BREAKDOWN:"
]

if not edited_r.empty:
    inc_only = edited_r[edited_r["include"]]
    if not inc_only.empty:
        grouped = inc_only.groupby(["floor", "name"])["area"].sum().reset_index()
        for f in FLOORS:
            f_data = grouped[grouped["floor"] == f]
            if not f_data.empty:
                report.append(f"\n[{f}]")
                for _, r in f_data.iterrows():
                    report.append(f" - {r['name']}: {int(r['area'])} sq ft")

if not edited_s.empty:
    report.append("\n[STAIRS]")
    for _, r in edited_s.iterrows():
        report.append(f" - {r['name']}: {r['steps']} steps (Landing: {r['landing_area']} sq ft)")

summary_text = "\n".join(report)

# ======================================================
# REPORTE FINAL
# ======================================================
st.divider()
with st.container(border=True):
    st.subheader(f"📋 Final Summary: {report_main_title}")
    st.text_area("Ready to copy:", summary_text, height=450)

    components.html(f"""
        <button id="copyBtn" style="padding:12px 24px;background-color:#007bff;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold;width:100%;font-family:sans-serif;"
        onclick="navigator.clipboard.writeText(`{summary_text}`); this.innerText='✓ Copied to Clipboard'; this.style.backgroundColor='#28a745';">
        📎 Copy Report to Clipboard
        </button>""", height=80)

if st.button("🗑️ Reset All Data"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()