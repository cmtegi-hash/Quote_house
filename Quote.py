import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re

st.set_page_config(page_title="Tech Service Tools", layout="wide")

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

    CARD_STYLE = (
        "border:1px solid #ddd;border-radius:12px;padding:2rem;text-align:center;"
        "min-height:160px;display:flex;flex-direction:column;"
        "align-items:center;justify-content:center;"
    )

    with col_c1:
        st.markdown(f"""
            <div style='{CARD_STYLE}'>
                <div style='font-size:2.5rem;'>🏢</div>
                <h3 style='margin:0.5rem 0 0.25rem;'>Commercial</h3>
                <p style='color:gray;font-size:0.85rem;margin:0;'>Buildings, hallways & stairwells.</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("Open Commercial", use_container_width=True, key="btn_commercial"):
            st.session_state.app_mode = "commercial"
            st.rerun()

    with col_c2:
        st.markdown(f"""
            <div style='{CARD_STYLE}'>
                <div style='font-size:2.5rem;'>🏠</div>
                <h3 style='margin:0.5rem 0 0.25rem;'>Residential</h3>
                <p style='color:gray;font-size:0.85rem;margin:0;'>Rooms, floors & stairs.</p>
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
    LOG_KEYS = ["Parking", "Bathroom", "Elevator", "Laundry"]
    EQUIP_KEYS = ["Mount", "Portable", "Cimex"]
    SOIL_KEYS = ["Light", "Medium", "Heavy"]
    SECTION_KEYS = ["Floor", "Stairwell", "Logistics", "Equipment", "Soil", "Notes"]

    for key, val in [
        ("template_text", ""), ("final_report", ""),
        ("audit_data", None), ("audit_ready", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val

    def copy_button(text_to_copy, label="📋 Copy to Clipboard"):
        escaped = text_to_copy.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        components.html(f"""<button onclick="navigator.clipboard.writeText(`{escaped}`).then(()=>{{
            this.innerText='✅ Copied!';setTimeout(()=>this.innerText='{label}',2000);
        }})" style="background:transparent;border:1px solid #ccc;border-radius:8px;
            padding:6px 16px;font-size:14px;cursor:pointer;color:inherit;width:100%;">{label}</button>
        """, height=45)

    def parse_input(lines):
        sqft_rate = 0.30; step_rate = 3.50
        hallway_sqft = 0.0; landing_sqft = 0.0
        total_steps = 0; est_hours = 1.0; tech_count = 1
        breakdown = {}; available = []; not_available = []
        equip_used = []; soil_levels = []; notes = []
        audit_log = []; current_section = ""; current_subsection = ""

        for raw_line in lines:
            clean = raw_line.strip()
            if not clean:
                continue

            if clean.startswith(FLAG_SKIP):
                name = clean[1:].strip()
                if any(k in name for k in EQUIP_KEYS):
                    audit_log.append({"type": "skip", "label": "Skipped", "detail": clean, "value": "not in report"})
                continue

            if "Rate SQFT" in clean:
                m = re.search(r"(\d+\.?\d*)", clean)
                if m:
                    sqft_rate = float(m.group(1))
                    audit_log.append({"type": "config", "label": "Config", "detail": "Rate SQFT", "value": f"${sqft_rate:.2f} / ft²"})
                continue

            if "Rate Step" in clean:
                m = re.search(r"(\d+\.?\d*)", clean)
                if m:
                    step_rate = float(m.group(1))
                    audit_log.append({"type": "config", "label": "Config", "detail": "Rate Step", "value": f"${step_rate:.2f} / step"})
                continue

            if clean.startswith("---"):
                continue

            if any(x in clean for x in SECTION_KEYS) and not clean.startswith("Total Floors"):
                current_section = clean.replace(":", "").strip()
                current_subsection = ""
                if current_section not in breakdown:
                    breakdown[current_section] = {"sqft": 0.0, "details": [], "sub": {}}
                continue

            if "Notes" in current_section:
                notes.append(clean)
                continue

            if "Technicians" in clean:
                m = re.search(r"(\d+)", clean)
                tech_count = int(m.group(1)) if m else 1
                continue

            if "Estimated Hours" in clean:
                m = re.search(r"(\d+\.?\d*)", clean)
                if m:
                    est_hours = float(m.group(1))
                continue

            is_unavail = clean.lower().startswith(FLAG_UNAVAIL) and len(clean) > 1 and clean[1].isupper()
            name = clean[1:].strip() if is_unavail else clean.strip()

            if any(k in name for k in LOG_KEYS):
                (not_available if is_unavail else available).append(name)
                continue

            if any(k in name for k in EQUIP_KEYS):
                equip_used.append(name)
                continue

            if any(k in name for k in SOIL_KEYS):
                if not is_unavail:
                    soil_levels.append(name)
                continue

            if SKIP_DIM in clean:
                audit_log.append({"type": "skip", "label": "Skipped", "detail": f'"{clean}" — zero dims', "value": "—"})
                continue

            if ARROW in clean:
                current_subsection = clean
                if current_section in breakdown:
                    breakdown[current_section]["sub"].setdefault(
                        current_subsection, {"sqft": 0.0, "steps": 0, "details": []}
                    )
                continue

            if "steps" in clean.lower():
                m = re.search(r"(\d+)", clean)
                if m:
                    v = int(m.group(1))
                    total_steps += v
                    if current_section and current_subsection and current_section in breakdown:
                        breakdown[current_section]["sub"].setdefault(
                            current_subsection, {"sqft": 0.0, "steps": 0, "details": []}
                        )["steps"] += v
                continue

            dims = re.findall(r"(\d+\.?\d*)x(\d+\.?\d*)", clean)
            if dims:
                sub_total = sum(float(w) * float(l) for w, l in dims)
                is_stair = "Stairwell" in current_section or ARROW in current_subsection
                if is_stair:
                    landing_sqft += sub_total
                    if current_section in breakdown and current_subsection:
                        breakdown[current_section]["sub"].setdefault(
                            current_subsection, {"sqft": 0.0, "steps": 0, "details": []}
                        )
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
                audit_log.append({
                    "type": "ok", "label": f"{section_label}{subsec}",
                    "detail": clean, "value": f"{sub_total:.1f} ft² → ${cost:.2f}"
                })

        return {
            "sqft_rate": sqft_rate, "step_rate": step_rate,
            "hallway_sqft": hallway_sqft, "landing_sqft": landing_sqft,
            "total_steps": total_steps, "est_hours": est_hours,
            "tech_count": tech_count, "available": available,
            "not_available": not_available, "equip_used": equip_used,
            "soil_levels": soil_levels, "notes": notes,
            "breakdown": breakdown, "audit_log": audit_log,
        }

    def build_report(d, building_name):
        sep = "=" * 40
        res = []
        res.extend([sep, "TECH SERVICE REPORT", f"Building: {building_name.upper()}", sep, ""])

        # Service summary
        res.extend(["SERVICE SUMMARY", "-" * 24])
        res.extend([
            f"Hallways Area:    {d['hallway_sqft']:.2f} ft2",
            f"Landings Area:    {d['landing_sqft']:.2f} ft2",
            f"Total Steps:      {d['total_steps']} units", "",
        ])

        # Floors — show "No carpet" if sqft is 0
        breakdown = d["breakdown"]
        for section, data in breakdown.items():
            if "Floor" in section:
                if data["sqft"] > 0:
                    res.append(f"{section}:  {data['sqft']:.2f} ft2")
                else:
                    res.append(f"{section}:  No carpet")
        res.append("")

        # Stairwells — show "No carpet" if sqft is 0
        for section, data in breakdown.items():
            if "Stairwell" in section:
                sub_lines = []
                for subsec, v in data["sub"].items():
                    parts = []
                    if v["sqft"] > 0:
                        parts.append(f"{v['sqft']:.2f} ft2")
                    else:
                        parts.append("No carpet")
                    if v["steps"] > 0:
                        parts.append(f"{v['steps']} steps")
                    sub_lines.append(f"{subsec}:  {', '.join(parts)}")
                if sub_lines:
                    res.append(f"-- {section} --")
                    res.extend(sub_lines)
                    res.append("")

        # Logistics
        res.extend(["LOGISTICS & SITE STATUS", "-" * 24,
                    f"Technicians:      {d['tech_count']}",
                    f"Estimated Hours:  {d['est_hours']}"])
        if d["available"]:
            res.append(f"Available:        {', '.join(d['available'])}")
        if d["not_available"]:
            clean_na = [n.lstrip("xX").strip() for n in d["not_available"]]
            res.append(f"Not Available:    {', '.join(clean_na)}")
        if d["equip_used"]:
            res.append(f"Equipment Used:   {', '.join(d['equip_used'])}")

        # Soil
        if d["soil_levels"]:
            res.extend(["", "SOIL ASSESSMENT", "-" * 24,
                        f"Soil Level:       {', '.join(d['soil_levels'])}"])

        # Notes — last section, no amount after this
        if d["notes"]:
            res.extend(["", "ADDITIONAL NOTES", "-" * 24])
            res.extend(d["notes"])

        res.extend(["", sep])
        return "\n".join(res)

    # ── UI ────────────────────────────────────────────────
    st.title("🏢 Commercial — Tech Service Report")
    col_gen, col_paste = st.columns([1, 2])

    with col_gen:
        st.subheader("Step 1: Setup")
        f_count = st.number_input("Total Floors", min_value=1, value=3)
        s_count = st.number_input("Stairwells", min_value=0, value=2)
        if st.button("Generate Master Template"):
            temp = [
                "--- CONFIGURATION (DO NOT DELETE) ---",
                "Rate SQFT: 0.30", "Rate Step: 3.50",
                "---------------------------------------",
                "\nBuilding: [Name]", "Type: Commercial",
                f"Total Floors: {f_count}\n",
            ]
            for i in range(1, f_count + 1):
                temp += [f"Floor {i}:", "0x0\n"]
            for s in range(1, s_count + 1):
                temp += [f"Stairwell {s}:", f"Basement {ARROW} 1", "0 steps", "0x0\n"]
                for f in range(1, f_count):
                    temp += [f"{f} {ARROW} {f+1}", "0 steps", "0x0\n"]
                temp += [f"{f_count} {ARROW} Roof", "0 steps", "0x0\n"]
            temp.extend([
                "Logistics & Site Resources:",
                "Technicians: 0", "Estimated Hours: 0",
                "xParking", "xBathroom", "xElevator", "xLaundry Room",
                "\nEquipment Checklist:",
                "#Truck Mount", "#Portable", "#Cimex",
                "\nSoil Level Assessment:",
                "Light", "xMedium", "xHeavy",
                "\nAdditional Notes:",
            ])
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

    # ── AUDIT PANEL ───────────────────────────────────────
    if st.session_state["audit_ready"] and st.session_state["audit_data"]:
        d = st.session_state["audit_data"]
        breakdown = d["breakdown"]
        sqft_rate = d["sqft_rate"]; step_rate = d["step_rate"]
        inv = ((d["hallway_sqft"] + d["landing_sqft"]) * sqft_rate) + (d["total_steps"] * step_rate)
        tech_n = d["tech_count"] if d["tech_count"] > 0 else 1
        est_h = d["est_hours"] if d["est_hours"] > 0 else 1
        h_rate = inv / (est_h * tech_n)

        st.markdown("---")
        st.subheader("🔍 1. Audit Dashboard (Friendly View)")

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Hallway ft²", f"{d['hallway_sqft']:.2f}")
        m2.metric("Landing ft²", f"{d['landing_sqft']:.2f}")
        m3.metric("Steps", d["total_steps"])
        m4.metric("Project Total", f"${inv:.2f}")
        m5.metric("$/hr per tech", f"${h_rate:.2f}")

        st.markdown("#### 🏢 Hallways & Floors")
        floor_found = False
        for section, data in breakdown.items():
            if "Floor" in section:
                floor_found = True
                if data["sqft"] > 0:
                    dims_str = " + ".join(data["details"])
                    subtotal = data["sqft"] * sqft_rate
                    st.write(f"**{section}:** {dims_str} = **{data['sqft']:.2f} ft²** | Subtotal: **${subtotal:.2f}**")
                else:
                    st.write(f"**{section}:** No carpet")
        if not floor_found:
            st.write("*No floors processed.*")

        st.markdown("#### 🪜 Staircases (Landings & Steps)")
        stair_found = False
        for section, data in breakdown.items():
            if "Stairwell" in section:
                for subsec, v in data["sub"].items():
                    stair_found = True
                    if v["sqft"] > 0:
                        dims_str = " + ".join(v["details"])
                        cost = (v["sqft"] * sqft_rate) + (v["steps"] * step_rate)
                        st.write(
                            f"**{section} ({subsec}):** {dims_str} "
                            f"(**{v['sqft']:.2f} ft²**) + **{v['steps']} steps** = **${cost:.2f}**"
                        )
                    else:
                        st.write(f"**{section} ({subsec}):** No carpet · **{v['steps']} steps**")
        if not stair_found:
            st.write("*No stairwells processed.*")

        st.markdown("#### 📦 Logistics & Soil")
        if d["available"]:
            st.markdown("**Available:** " + " · ".join(f"✓ {x}" for x in d["available"]))
        if d["not_available"]:
            clean_na_display = [n.lstrip("xX").strip() for n in d["not_available"]]
            st.markdown("**Not Available:** " + " · ".join(f"✗ {x}" for x in clean_na_display))
        if d["equip_used"]:
            st.markdown("**Equipment:** " + " · ".join(d["equip_used"]))
        if d["soil_levels"]:
            st.markdown("**Soil Level:** " + " · ".join(d["soil_levels"]))
        if d["notes"]:
            st.markdown("**Notes:** " + " · ".join(d["notes"]))

    # ── FINAL REPORT ──────────────────────────────────────
    if st.session_state["final_report"]:
        st.markdown("---")
        st.subheader("📋 Final Tech Report")
        st.code(st.session_state["final_report"], language=None)
        copy_button(st.session_state["final_report"], "📋 Copy Report")


# ======================================================
# RESIDENTIAL APP
# ======================================================
elif st.session_state.app_mode == "residential":

    FLOORS = ["Basement", "Floor 1", "Floor 2", "Floor 3"]

    for key, val in {
        "rooms": [], "stairs": [],
        "r_floor": "Basement", "r_name": "", "r_width": "", "r_length": "",
        "s_from": "Floor 1", "s_to": "Floor 2",
        "s_steps": "", "s_has_landing": False,
        "s_lw": "", "s_ll": "",
        "res_show_stairs_form": False,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

    def res_add_room():
        try:
            name = st.session_state.r_name.strip()
            w = float(st.session_state.r_width)
            l = float(st.session_state.r_length)
            if not name:
                st.warning("Room name required.")
                return
            st.session_state.rooms.append({
                "floor": st.session_state.r_floor,
                "name": name, "width": w, "length": l,
                "area": int(round(w * l))
            })
            st.session_state.r_name = ""
            st.session_state.r_width = ""
            st.session_state.r_length = ""
        except ValueError:
            st.warning("Width and length must be numbers.")

    def res_add_stair():
        try:
            steps = int(st.session_state.s_steps)
            landing_area = 0
            if st.session_state.s_has_landing:
                landing_area = int(round(
                    float(st.session_state.s_lw) * float(st.session_state.s_ll)
                ))
            st.session_state.stairs.append({
                "name": f"{st.session_state.s_from} → {st.session_state.s_to}",
                "from": st.session_state.s_from,
                "to": st.session_state.s_to,
                "steps": steps,
                "landing_area": landing_area,
            })
            st.session_state.s_steps = ""
            st.session_state.s_has_landing = False
            st.session_state.s_lw = ""
            st.session_state.s_ll = ""
            st.session_state.res_show_stairs_form = False
        except ValueError:
            st.warning("Steps must be a whole number; landing dims must be numbers.")

    def res_build_summary():
        floor_order = {f: i for i, f in enumerate(FLOORS)}
        lines = []
        room_total = sum(r["area"] for r in st.session_state.rooms)
        landing_total = sum(s["landing_area"] for s in st.session_state.stairs)
        steps_total = sum(s["steps"] for s in st.session_state.stairs)
        grand = room_total + landing_total
        lines.append(f"Total Area: {grand} ft²")
        lines.append(f"Total Steps: {steps_total}\n")
        sorted_rooms = sorted(
            st.session_state.rooms,
            key=lambda r: (floor_order.get(r["floor"], 99), r["name"])
        )
        current_floor = None
        for r in sorted_rooms:
            if r["floor"] != current_floor:
                if current_floor is not None:
                    lines.append("")
                lines.append(f"{r['floor']}:")
                current_floor = r["floor"]
            lines.append(f"  {r['name'].capitalize()}: {r['area']} ft²")
        if sorted_rooms:
            lines.append("")
        if st.session_state.stairs:
            sorted_stairs = sorted(
                st.session_state.stairs,
                key=lambda s: floor_order.get(s["from"], 99)
            )
            lines.append("Stairs:")
            for s in sorted_stairs:
                line = f"  {s['name']}: {s['steps']} steps"
                if s["landing_area"] > 0:
                    line += f", landing {s['landing_area']} ft²"
                lines.append(line)
            lines.append(f"\nTotal landing area: {landing_total} ft²")
        return "\n".join(lines).strip(), grand, steps_total

    # ── UI ────────────────────────────────────────────────
    st.title("🏠 Residential — Area & Stairs Calculator")

    st.markdown("#### ➕ Add Room")
    with st.form("res_room_form", clear_on_submit=False):
        st.selectbox("Floor", FLOORS, key="r_floor")
        st.text_input("Room name", key="r_name", placeholder="e.g. Lobby")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Width (ft)", key="r_width", placeholder="0")
        with c2:
            st.text_input("Length (ft)", key="r_length", placeholder="0")
        st.form_submit_button("＋ Add Room", on_click=res_add_room, use_container_width=True)

    if st.session_state.rooms:
        st.markdown("---")
        st.markdown("#### 🏠 Rooms")
        grouped = {}
        for r in st.session_state.rooms:
            grouped.setdefault(r["floor"], []).append(r)
        for floor in FLOORS:
            if floor not in grouped:
                continue
            st.markdown(f"**{floor}**")
            for r in grouped[floor]:
                global_idx = st.session_state.rooms.index(r)
                col_name, col_area, col_del = st.columns([3, 2, 1])
                with col_name:
                    st.write(r["name"].capitalize())
                with col_area:
                    st.write(f"{r['area']} ft²")
                with col_del:
                    if st.button("🗑", key=f"del_room_{global_idx}"):
                        st.session_state.rooms.pop(global_idx)
                        st.rerun()

    st.markdown("---")
    if not st.session_state.res_show_stairs_form:
        if st.button("🪜 Add Stairs", use_container_width=True):
            st.session_state.res_show_stairs_form = True
            st.rerun()
    else:
        st.markdown("#### 🪜 Add Stairs")
        with st.form("res_stair_form", clear_on_submit=False):
            ca, cb = st.columns(2)
            with ca:
                st.selectbox("From", FLOORS, key="s_from")
            with cb:
                st.selectbox("To", FLOORS, key="s_to")
            st.text_input("Total steps", key="s_steps", placeholder="0")
            st.checkbox("Has landing?", key="s_has_landing")
            if st.session_state.s_has_landing:
                cw, cl = st.columns(2)
                with cw:
                    st.text_input("Landing W (ft)", key="s_lw", placeholder="0")
                with cl:
                    st.text_input("Landing L (ft)", key="s_ll", placeholder="0")
            cc1, cc2 = st.columns(2)
            with cc1:
                st.form_submit_button("＋ Add", on_click=res_add_stair, use_container_width=True)
            with cc2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.res_show_stairs_form = False
                    st.rerun()

    if st.session_state.stairs:
        st.markdown("#### Stairs added")
        for idx, s in enumerate(st.session_state.stairs):
            cs1, cs2, cs3 = st.columns([3, 2, 1])
            with cs1:
                st.write(s["name"])
            with cs2:
                info = f"{s['steps']} steps"
                if s["landing_area"] > 0:
                    info += f" · {s['landing_area']} ft²"
                st.write(info)
            with cs3:
                if st.button("🗑", key=f"del_stair_{idx}"):
                    st.session_state.stairs.pop(idx)
                    st.rerun()

    if st.session_state.rooms or st.session_state.stairs:
        st.markdown("---")
        summary, grand_total, steps_total = res_build_summary()
        m1, m2 = st.columns(2)
        m1.metric("📐 Total Area", f"{grand_total} ft²")
        m2.metric("🪜 Total Steps", steps_total)
        st.markdown("#### 📋 Final Summary")
        st.code(summary, language=None)
        escaped = summary.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
        components.html(f"""<button onclick="navigator.clipboard.writeText(`{escaped}`).then(()=>{{
            this.innerText='✅ Copied!';setTimeout(()=>this.innerText='📋 Copy Summary',2000);
        }})" style="background:transparent;border:1px solid #ccc;border-radius:8px;
            padding:6px 16px;font-size:14px;cursor:pointer;color:inherit;width:100%;">📋 Copy Summary</button>
        """, height=45)
