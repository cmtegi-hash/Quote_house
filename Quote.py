import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re

st.set_page_config(page_title="Tech Service Tools", layout="wide")

# ======================================================
# SESSION STATE — navegación
# ======================================================
if "app_mode" not in st.session_state:
    st.session_state.app_mode = None

# ======================================================
# HOME SCREEN
# ======================================================
if st.session_state.app_mode is None:
    st.markdown("""
        <div style='text-align:center; padding: 3rem 1rem 1rem;'>
            <h1>🛠️ Tech Service Tools</h1>
            <p style='font-size:1.1rem; color:gray;'>Select the tool you need</p>
        </div>
    """, unsafe_allow_html=True)

    _, col_c1, col_c2, _ = st.columns([1, 2, 2, 1])

    with col_c1:
        st.markdown("""
            <div style='border:1px solid #ddd;border-radius:12px;padding:2rem;text-align:center;'>
                <div style='font-size:3rem;'>🏢</div>
                <h3>Commercial</h3>
                <p style='color:gray;font-size:0.9rem;'>Buildings, hallways & stairwells.<br>Template-based text report.</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Open Commercial", use_container_width=True, key="btn_commercial"):
            st.session_state.app_mode = "commercial"
            st.rerun()

    with col_c2:
        st.markdown("""
            <div style='border:1px solid #ddd;border-radius:12px;padding:2rem;text-align:center;'>
                <div style='font-size:3rem;'>🏠</div>
                <h3>Residential</h3>
                <p style='color:gray;font-size:0.9rem;'>Rooms, floors & stairs.<br>Interactive form-based calculator.</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Open Residential", use_container_width=True, key="btn_residential"):
            st.session_state.app_mode = "residential"
            st.rerun()

    st.stop()

# ======================================================
# BACK BUTTON
# ======================================================
if st.button("← Back to Home"):
    st.session_state.app_mode = None
    st.rerun()

st.markdown("---")

# ======================================================
# COMMERCIAL APP
# ======================================================
if st.session_state.app_mode == "commercial":

    ARROW = "→"
    SKIP_DIM = "0x0"
    FLAG_SKIP = "#"
    FLAG_UNAVAIL = "x"
    LOG_KEYS = ["Parking", "Water", "Electricity", "Bathroom", "Elevator", "Laundry"]
    EQUIP_KEYS = ["Mount", "Portable", "Cimex"]
    SOIL_KEYS = ["Light", "Medium", "Heavy"]
    SECTION_KEYS = ["Floor", "Stairwell", "Logistics", "Equipment", "Soil", "Notes"]

    for key, val in [("template_text",""),("final_report",""),("audit_data",None),("audit_ready",False)]:
        if key not in st.session_state:
            st.session_state[key] = val

    def copy_button(text_to_copy, label="📋 Copy to Clipboard"):
        escaped = text_to_copy.replace("\\","\\\\").replace("`","\\`").replace("$","\\$")
        components.html(f"""<button onclick="navigator.clipboard.writeText(`{escaped}`).then(()=>{{
            this.innerText='✅ Copied!';setTimeout(()=>this.innerText='{label}',2000);
        }})" style="background:transparent;border:1px solid #ccc;border-radius:8px;
            padding:6px 16px;font-size:14px;cursor:pointer;color:inherit;width:100%;">{label}</button>
        """, height=45)

    def parse_input(lines):
        sqft_rate=0.30; step_rate=3.50; hallway_sqft=0.0; landing_sqft=0.0
        total_steps=0; est_hours=1.0; tech_count="0"
        breakdown={}; available=[]; not_available=[]; equip_used=[]
        soil_levels=[]; audit_log=[]; current_section=""; current_subsection=""

        for raw_line in lines:
            clean = raw_line.strip()
            if not clean: continue

            if clean.startswith(FLAG_SKIP):
                name = clean[1:].strip()
                if any(k in name for k in EQUIP_KEYS):
                    audit_log.append({"type":"skip","label":"Skipped","detail":clean,"value":"not in report"})
                continue

            if "Rate SQFT" in clean:
                m = re.search(r"(\d+\.?\d*)", clean)
                if m:
                    sqft_rate = float(m.group(1))
                    audit_log.append({"type":"config","label":"Config","detail":"Rate SQFT","value":f"${sqft_rate:.2f} / ft²"})
                continue

            if "Rate Step" in clean:
                m = re.search(r"(\d+\.?\d*)", clean)
                if m:
                    step_rate = float(m.group(1))
                    audit_log.append({"type":"config","label":"Config","detail":"Rate Step","value":f"${step_rate:.2f} / step"})
                continue

            if clean.startswith("---"): continue

            if any(x in clean for x in SECTION_KEYS):
                current_section = clean.replace(":","").strip()
                current_subsection = ""
                if current_section not in breakdown:
                    breakdown[current_section] = {"sqft":0.0,"details":[],"sub":{}}
                continue

            if "Technicians" in clean:
                m = re.search(r"(\d+)", clean)
                tech_count = m.group(1) if m else "0"
                continue

            if "Estimated Hours" in clean:
                m = re.search(r"(\d+\.?\d*)", clean)
                if m: est_hours = float(m.group(1))
                continue

            is_unavail = clean.lower().startswith(FLAG_UNAVAIL) and len(clean)>1 and clean[1].isupper()
            name = clean[1:].strip() if is_unavail else clean.strip()

            if any(k in name for k in LOG_KEYS):
                (not_available if is_unavail else available).append(name)
                continue

            if any(k in name for k in EQUIP_KEYS):
                equip_used.append(name)
                continue

            if any(k in name for k in SOIL_KEYS):
                if not is_unavail: soil_levels.append(name)
                continue

            if SKIP_DIM in clean:
                audit_log.append({"type":"skip","label":"Skipped","detail":f'"{clean}" — zero dims',"value":"—"})
                continue

            if ARROW in clean:
                current_subsection = clean
                if current_section in breakdown:
                    breakdown[current_section]["sub"].setdefault(current_subsection,{"sqft":0.0,"steps":0,"details":[]})
                continue

            if "steps" in clean.lower():
                m = re.search(r"(\d+)", clean)
                if m:
                    v = int(m.group(1))
                    total_steps += v
                    if current_section and current_subsection and current_section in breakdown:
                        breakdown[current_section]["sub"].setdefault(current_subsection,{"sqft":0.0,"steps":0,"details":[]})["steps"] += v
                continue

            dims = re.findall(r"(\d+\.?\d*)x(\d+\.?\d*)", clean)
            if dims:
                sub_total = sum(float(w)*float(l) for w,l in dims)
                is_stair = "Stairwell" in current_section or ARROW in current_subsection
                if is_stair:
                    landing_sqft += sub_total
                    if current_section in breakdown and current_subsection:
                        breakdown[current_section]["sub"].setdefault(current_subsection,{"sqft":0.0,"steps":0,"details":[]})
                        breakdown[current_section]["sub"][current_subsection]["sqft"] += sub_total
                        breakdown[current_section]["sub"][current_subsection]["details"].append(clean)
                else:
                    hallway_sqft += sub_total
                    if current_section in breakdown:
                        breakdown[current_section]["sqft"] += sub_total
                        breakdown[current_section]["details"].append(clean)
                cost = sub_total * sqft_rate
                section_label = current_section or "?"
                subsec = f" ({current_subsection})" if current_subsection else ""
                audit_log.append({"type":"ok","label":f"{section_label}{subsec}","detail":clean,"value":f"{sub_total:.1f} ft² → ${cost:.2f}"})

        return {"sqft_rate":sqft_rate,"step_rate":step_rate,"hallway_sqft":hallway_sqft,
                "landing_sqft":landing_sqft,"total_steps":total_steps,"est_hours":est_hours,
                "tech_count":tech_count,"available":available,"not_available":not_available,
                "equip_used":equip_used,"soil_levels":soil_levels,"breakdown":breakdown,"audit_log":audit_log}

    def build_report(d, building_name):
        sqft_rate=d["sqft_rate"]; step_rate=d["step_rate"]
        inv=((d["hallway_sqft"]+d["landing_sqft"])*sqft_rate)+(d["total_steps"]*step_rate)
        h_rate=inv/d["est_hours"] if d["est_hours"]>0 else 0
        sep="="*40; res=[]
        res.extend([sep,"TECH SERVICE REPORT",f"Building: {building_name.upper()}",sep,""])
        res.extend(["SERVICE SUMMARY","-"*24])
        res.extend([f"Hallways Area:    {d['hallway_sqft']:.2f} ft2",
                    f"Landings Area:    {d['landing_sqft']:.2f} ft2",
                    f"Total Steps:      {d['total_steps']} units",""])
        breakdown=d["breakdown"]
        for section,data in breakdown.items():
            if "Floor" in section and data["sqft"]>0:
                res.append(f"{section}:  {data['sqft']:.2f} ft2")
        res.append("")
        for section,data in breakdown.items():
            if "Stairwell" in section:
                sub_lines=[]
                for subsec,v in data["sub"].items():
                    if v["sqft"]>0 or v["steps"]>0:
                        parts=[]
                        if v["sqft"]>0: parts.append(f"{v['sqft']:.2f} ft2")
                        if v["steps"]>0: parts.append(f"{v['steps']} steps")
                        sub_lines.append(f"{subsec}:  {', '.join(parts)}")
                if sub_lines:
                    res.append(f"-- {section} --")
                    res.extend(sub_lines)
                    res.append("")
        res.extend(["LOGISTICS & SITE STATUS","-"*24,
                    f"Technicians:      {d['tech_count']}",
                    f"Estimated Hours:  {d['est_hours']}"])
        if d["available"]: res.append(f"Available:        {', '.join(d['available'])}")
        if d["not_available"]:
            clean_na=[n.lstrip("xX").strip() for n in d["not_available"]]
            res.append(f"Not Available:    {', '.join(clean_na)}")
        if d["equip_used"]: res.append(f"Equipment Used:   {', '.join(d['equip_used'])}")
        if d["soil_levels"]:
            res.extend(["","SOIL ASSESSMENT","-"*24,f"Soil Level:       {', '.join(d['soil_levels'])}"])
        res.extend(["","FINAL SUMMARY","-"*24,f"Project Total:    ${inv:.2f}",f"Hourly Profit:    ${h_rate:.2f}/hr","",sep])
        return "\n".join(res)

    # UI
    st.title("🏢 Commercial — Tech Service Report")
    col_gen, col_paste = st.columns([1,2])

    with col_gen:
        st.subheader("Step 1: Setup")
        f_count = st.number_input("Total Floors", min_value=1, value=3)
        s_count = st.number_input("Stairwells", min_value=0, value=2)
        if st.button("Generate Master Template"):
            temp = ["--- CONFIGURATION (DO NOT DELETE) ---","Rate SQFT: 0.30","Rate Step: 3.50",
                    "---------------------------------------","\nBuilding: [Name]","Type: Commercial",f"Total Floors: {f_count}\n"]
            for i in range(1,f_count+1): temp+=[f"Floor {i}:","0x0\n"]
            for s in range(1,s_count+1):
                temp+=[f"Stairwell {s}:",f"Basement {ARROW} 1","0 steps","0x0\n"]
                for f in range(1,f_count): temp+=[f"{f} {ARROW} {f+1}","0 steps","0x0\n"]
                temp+=[f"{f_count} {ARROW} Roof","0 steps","0x0\n"]
            temp.extend(["Logistics & Site Resources:","Technicians: 0","Estimated Hours: 0",
                "xParking","xWater Access","xElectricity","xBathroom","xElevator","xLaundry Room",
                "\nEquipment Checklist:","#Truck Mount","#Portable","#Cimex",
                "\nSoil Level Assessment:","Light","xMedium","xHeavy","\nAdditional Notes:"])
            st.session_state["template_text"] = "\n".join(temp)
        if st.session_state["template_text"]:
            st.text_area("Master Template:", st.session_state["template_text"], height=380)
            copy_button(st.session_state["template_text"], "📋 Copy Template")

    with col_paste:
        st.subheader("Step 2: Process Data")
        user_input = st.text_area("Input Area (Paste here)", height=380)
        if st.button("🔍 Preview / Audit", use_container_width=True):
            if user_input.strip():
                st.session_state["audit_data"] = parse_input(user_input.splitlines())
                st.session_state["audit_ready"] = True
                st.session_state["final_report"] = ""
        if st.session_state["audit_ready"]:
            if st.button("📄 Generate Final Report", use_container_width=True):
                d = st.session_state["audit_data"]
                b_match = re.search(r'Building:\s*\[?(.*?)\]?\s*$', user_input, re.MULTILINE)
                building_name = b_match.group(1).strip() if b_match else "BUILDING"
                st.session_state["final_report"] = build_report(d, building_name)
        else:
            st.info("▲ Run Preview / Audit first to enable the report")

    if st.session_state["audit_ready"] and st.session_state["audit_data"]:
        d = st.session_state["audit_data"]
        breakdown = d["breakdown"]
        sqft_rate = d["sqft_rate"]; step_rate = d["step_rate"]
        st.markdown("---")
        st.subheader("🔍 1. Audit Dashboard (Friendly View)")
        inv = ((d["hallway_sqft"]+d["landing_sqft"])*sqft_rate)+(d["total_steps"]*step_rate)
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Hallway ft²",f"{d['hallway_sqft']:.2f}")
        m2.metric("Landing ft²",f"{d['landing_sqft']:.2f}")
        m3.metric("Steps",d["total_steps"])
        m4.metric("Est. Total",f"${inv:.2f}")
        st.markdown("#### 🏢 Hallways & Floors")
        floor_found = False
        for section,data in breakdown.items():
            if "Floor" in section and data["sqft"]>0:
                floor_found=True
                dims_str=" + ".join(data["details"])
                subtotal=data["sqft"]*sqft_rate
                st.write(f"**{section}:** {dims_str} = **{data['sqft']:.2f} ft²** | Subtotal: **${subtotal:.2f}**")
        if not floor_found: st.write("*No hallways processed.*")
        st.markdown("#### 🪜 Staircases (Landings & Steps)")
        stair_found = False
        for section,data in breakdown.items():
            if "Stairwell" in section:
                for subsec,v in data["sub"].items():
                    if v["sqft"]>0 or v["steps"]>0:
                        stair_found=True
                        dims_str=" + ".join(v["details"]) if v["details"] else "—"
                        cost=(v["sqft"]*sqft_rate)+(v["steps"]*step_rate)
                        st.write(f"**{section} ({subsec}):** {dims_str} (**{v['sqft']:.2f} ft²**) + **{v['steps']} steps** = **${cost:.2f}**")
        if not stair_found: st.write("*No stairwells processed.*")
        st.markdown("#### 📦 Logistics & Soil")
        if d["available"]: st.markdown("**Available:** "+" · ".join(f"✓ {x}" for x in d["available"]))
        if d["not_available"]:
            clean_na_display=[n.lstrip("xX").strip() for n in d["not_available"]]
            st.markdown("**Not Available:** "+" · ".join(f"✗ {x}" for x in clean_na_display))
        if d["equip_used"]: st.markdown("**Equipment:** "+" · ".join(d["equip_used"]))
        if d["soil_levels"]: st.markdown("**Soil Level:** "+" · ".join(d["soil_levels"]))

    if st.session_state["final_report"]:
        st.markdown("---")
        st.subheader("📋 Final Tech Report")
        st.code(st.session_state["final_report"], language=None)
        copy_button(st.session_state["final_report"], "📋 Copy Report")


# ======================================================
# RESIDENTIAL APP
# ======================================================
elif st.session_state.app_mode == "residential":

    FLOORS = ["Basement","Floor 1","Floor 2","Floor 3"]

    for key,val in {"rooms":[],"stairs":[],"active_floor":"Basement",
        "room_name":"","width_input":"","length_input":"","include_input":True,
        "stair_from":"Floor 1","stair_to":"Floor 2","steps_input":"",
        "has_landing":True,"landing_width_input":"","landing_length_input":""}.items():
        if key not in st.session_state:
            st.session_state[key] = val

    def add_room():
        try:
            name = st.session_state.room_name.strip()
            width = float(st.session_state.width_input)
            length = float(st.session_state.length_input)
            if not name:
                st.warning("Room name cannot be empty.")
                return
            st.session_state.rooms.append({"name":name,"floor":st.session_state.active_floor,
                "width":width,"length":length,"include":st.session_state.include_input})
            st.session_state.room_name=""
            st.session_state.width_input=""
            st.session_state.length_input=""
            st.session_state.include_input=True
        except ValueError:
            st.warning("Width and length must be numbers.")

    def add_stair():
        try:
            steps = int(st.session_state.steps_input)
            landing_area = 0
            if st.session_state.has_landing:
                lw=float(st.session_state.landing_width_input)
                ll=float(st.session_state.landing_length_input)
                landing_area=int(round(lw*ll))
            st.session_state.stairs.append({"name":f"{st.session_state.stair_from} → {st.session_state.stair_to}",
                "from":st.session_state.stair_from,"to":st.session_state.stair_to,
                "steps":steps,"landing_area":landing_area})
            st.session_state.steps_input=""
            st.session_state.has_landing=True
            st.session_state.landing_width_input=""
            st.session_state.landing_length_input=""
        except ValueError:
            st.warning("Steps must be integer and landing dimensions must be numbers.")

    st.title("🏠 Residential — Area & Stairs Calculator")
    st.markdown("## 🏢 Active Floor")
    st.selectbox("Current working floor", FLOORS, key="active_floor")

    st.markdown("## ➕ Add Room Section")
    with st.form("add_room_form"):
        st.text_input("Room Name", key="room_name")
        st.text_input("Width (ft)", key="width_input")
        st.text_input("Length (ft)", key="length_input")
        st.checkbox("Include in total?", key="include_input")
        st.form_submit_button("Add Room Section", on_click=add_room)

    st.markdown("### ✏️ Room Sections")
    if st.session_state.rooms:
        rooms_df = pd.DataFrame(st.session_state.rooms)
        rooms_df["area"] = (rooms_df["width"]*rooms_df["length"]).round().astype(int)
        edited_rooms = st.data_editor(rooms_df, num_rows="dynamic",
            column_config={"include":st.column_config.CheckboxColumn("Include?",default=True),
                           "area":st.column_config.NumberColumn("Area (ft²)",disabled=True)},
            use_container_width=True)
        st.session_state.rooms = edited_rooms.to_dict(orient="records")
        if st.button("🗑️ Remove rooms not included"):
            st.session_state.rooms=[r for r in st.session_state.rooms if r["include"]]
            st.rerun()
    else:
        edited_rooms = pd.DataFrame()

    st.markdown("## 🪜 Add Stairs")
    with st.form("add_stairs_form"):
        st.selectbox("From Floor", FLOORS, key="stair_from")
        st.selectbox("To Floor", FLOORS, key="stair_to")
        st.text_input("Total Steps", key="steps_input")
        st.checkbox("Has Landing?", key="has_landing")
        if st.session_state.has_landing:
            st.text_input("Landing Width (ft)", key="landing_width_input")
            st.text_input("Landing Length (ft)", key="landing_length_input")
        st.form_submit_button("Add Stairs", on_click=add_stair)

    st.markdown("### ✏️ Stairs List")
    if st.session_state.stairs:
        stairs_df = pd.DataFrame(st.session_state.stairs)
        edited_stairs = st.data_editor(stairs_df, num_rows="dynamic",
            column_config={"steps":st.column_config.NumberColumn("Steps"),
                           "landing_area":st.column_config.NumberColumn("Landing Area (ft²)")},
            use_container_width=True)
        st.session_state.stairs = edited_stairs.to_dict(orient="records")
    else:
        edited_stairs = pd.DataFrame()

    room_area_total=0; stairs_steps_total=0; stairs_landing_total=0
    if not edited_rooms.empty:
        included_rooms = edited_rooms[edited_rooms["include"]==True]
        room_area_total = int((included_rooms["width"]*included_rooms["length"]).round().astype(int).sum())
    else:
        included_rooms = pd.DataFrame()
    if not edited_stairs.empty:
        stairs_steps_total=int(edited_stairs["steps"].sum())
        stairs_landing_total=int(edited_stairs["landing_area"].sum())
    grand_total_area=room_area_total+stairs_landing_total

    st.divider()
    m1,m2=st.columns(2)
    m1.metric("📐 Total Area (incl. landings)",f"{grand_total_area} ft²")
    m2.metric("🪜 Total Steps",stairs_steps_total)

    summary_lines=[f"Total Area: {grand_total_area} ft²",f"Total Steps: {stairs_steps_total}\n"]
    if not included_rooms.empty:
        floor_order={f:i for i,f in enumerate(FLOORS)}
        inc=included_rooms.copy()
        inc["area"]=(inc["width"]*inc["length"]).round().astype(int)
        inc["floor_order"]=inc["floor"].map(floor_order)
        inc=inc.sort_values(["floor_order","name"])
        for floor in FLOORS:
            fd=inc[inc["floor"]==floor]
            if not fd.empty:
                summary_lines.append(f"{floor}:")
                for _,row in fd.iterrows():
                    summary_lines.append(f"  {row['name'].capitalize()}: {row['area']} ft²")
                summary_lines.append("")
    if not edited_stairs.empty:
        stairs_df2=pd.DataFrame(st.session_state.stairs).copy()
        stairs_df2["from_order"]=stairs_df2["from"].map({f:i for i,f in enumerate(FLOORS)})
        stairs_df2=stairs_df2.sort_values("from_order")
        summary_lines.append("Stairs:")
        for _,row in stairs_df2.iterrows():
            line=f"  {row['name']}: {int(row['steps'])} steps"
            if int(row["landing_area"])>0: line+=f", landing {int(row['landing_area'])} ft²"
            summary_lines.append(line)
        summary_lines.append(f"\nTotal landing area: {stairs_landing_total} ft²")

    summary="\n".join(summary_lines).strip()
    st.markdown("## 📋 Final Summary")
    st.code(summary, language=None)
    escaped_summary=summary.replace("\\","\\\\").replace("`","\\`").replace("$","\\$")
    components.html(f"""<button onclick="navigator.clipboard.writeText(`{escaped_summary}`).then(()=>{{
        this.innerText='✅ Copied!';setTimeout(()=>this.innerText='📋 Copy Summary',2000);
    }})" style="background:transparent;border:1px solid #ccc;border-radius:8px;
        padding:6px 16px;font-size:14px;cursor:pointer;color:inherit;width:100%;">📋 Copy Summary</button>
    """, height=45)
