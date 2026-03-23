import streamlit as st
import streamlit.components.v1 as components
import json
import uuid

st.set_page_config(page_title="Master Template Generator", layout="centered")
st.title("Master Template Generator")

# -------------------------
# SESSION STATE
# -------------------------
if "master_template" not in st.session_state:
    st.session_state.master_template = ""

# -------------------------
# HELPERS
# -------------------------
def copy_button(text, label="Copy Template", copied_label="Copied"):
    """
    Botón para copiar texto al portapapeles, compatible con iPhone/iPad y otros navegadores.
    """
    button_id = f"copyBtn_{uuid.uuid4().hex}"
    safe_text = json.dumps(text)  # Escapa comillas y saltos de línea

    components.html(
        f"""
        <button id="{button_id}"
                style="padding:12px 20px;font-size:16px;background:#4CAF50;color:white;
                       border:none;border-radius:8px;cursor:pointer;margin-top:5px;">
            {label}
        </button>

        <script>
        const btn = document.getElementById("{button_id}");

        btn.addEventListener("click", () => {{
            const text = {safe_text};

            // Método moderno
            if (navigator.clipboard && window.isSecureContext) {{
                navigator.clipboard.writeText(text).then(() => {{
                    btn.innerText = "{copied_label}";
                }}).catch(() => fallbackCopy(text));
            }} else {{
                fallbackCopy(text);
            }}

            function fallbackCopy(text) {{
                const textarea = document.createElement("textarea");
                textarea.value = text;
                textarea.style.position = "fixed";
                textarea.style.opacity = "0";
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();

                try {{
                    document.execCommand("copy");
                    btn.innerText = "{copied_label}";
                }} catch (err) {{
                    btn.innerText = "Error";
                }}

                document.body.removeChild(textarea);
            }}

            setTimeout(() => {{
                btn.innerText = "{label}";
            }}, 2000);
        }});
        </script>
        """,
        height=80
    )

def format_list_with_and(items):
    if not items:
        return ""
    if isinstance(items, str):
        items = [items]
    if len(items) == 1:
        return f"{items[0]}"
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])} and {items[-1]}"

def section_divider():
    return "-----------------------------\n"

# -------------------------
# TEMPLATE INPUTS
# -------------------------
st.header("Master Template Inputs")

check_in = st.text_input("Check-in time")
check_out = st.text_input("Check-out time")

surfaces = st.multiselect("Surfaces Cleaned", ["Carpet", "Upholstery", "Hard Surface Floors"])
carpet_fiber = []
surface_type = []

if "Carpet" in surfaces:
    carpet_fiber = st.radio("Carpet Fiber", ["Wool", "Synthetic"], horizontal=True)
if "Hard Surface Floors" in surfaces:
    surface_type = st.multiselect("Floor Type", ["Tile / Grout", "Laminated"])

equipment_used = st.multiselect("Equipment Used", ["Portable", "Truck mount", "Cimex"])
products_applied = st.multiselect(
    "Products Applied",
    ["Procyon", "Citrus", "Releasit", "Flex", "Bio Break", "Boost All", "Pure O2", "Eco Cide"]
)

description = st.text_area("Job Description")

# -------------------------
# GENERATE MASTER TEMPLATE
# -------------------------
if st.button("Generate Master Template"):
    template = ""

    # Job Time
    template += "JOB TIME\n"
    if check_in:
        template += f"Check-in: {check_in}\n"
    if check_out:
        template += f"Check-out: {check_out}\n"
    template += section_divider()

    # Surfaces
    if surfaces:
        template += "SURFACES CLEANED\n"
        template += f"{format_list_with_and(surfaces)}.\n"
        if carpet_fiber:
            template += f"Carpet Fiber: {carpet_fiber}\n"
        if surface_type:
            template += f"Floor Type: {format_list_with_and(surface_type)}\n"
        template += section_divider()

    # Equipment
    if equipment_used:
        template += "EQUIPMENT USED\n"
        template += f"{format_list_with_and(equipment_used)}.\n"
        template += section_divider()

    # Products
    if products_applied:
        template += "PRODUCTS APPLIED\n"
        template += f"{format_list_with_and(products_applied)}.\n"
        template += section_divider()

    # Description
    if description.strip():
        clean_description = description.strip()
        clean_description = clean_description[0].upper() + clean_description[1:]
        if not clean_description.endswith("."):
            clean_description += "."
        template += "JOB DESCRIPTION\n"
        template += f"{clean_description}\n"
        template += section_divider()

    st.session_state.master_template = template

# -------------------------
# OUTPUT AND COPY BUTTON
# -------------------------
if st.session_state.master_template:
    st.header("Master Template")
    st.text_area("Review or copy:", st.session_state.master_template, height=300)
    copy_button(st.session_state.master_template)
