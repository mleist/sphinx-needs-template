"""Minimal ReqIF reader/writer using the stdlib XML parser.

Round-trips a small subset of ReqIF that is enough to exchange the demo
requirements with mainstream RM tools (DOORS Next, Polarion, ...).
The mapping is deliberately small and explicit so the code stays auditable.

Mapping (sphinx-needs ↔ ReqIF SPEC-OBJECT attributes):

    id          ↔ ReqIF.ForeignID
    title       ↔ ReqIF.Name
    description ↔ ReqIF.Text
    status      ↔ Status (free-form string attribute)
    tags        ↔ Tags  (semicolon-separated string)
"""

from __future__ import annotations

import datetime as _dt
import json
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

REQIF_NS = "http://www.omg.org/spec/ReqIF/20110401/reqif.xsd"
XHTML_NS = "http://www.w3.org/1999/xhtml"

ET.register_namespace("", REQIF_NS)
ET.register_namespace("xhtml", XHTML_NS)


# --------------------------------------------------------------------- import
def import_reqif(reqif_path: Path) -> list[dict[str, Any]]:
    """Read SPEC-OBJECTs from a ReqIF file and return sphinx-needs-shaped dicts."""
    reqif_path = Path(reqif_path)
    tree = ET.parse(reqif_path)
    root = tree.getroot()

    # Build a lookup: ATTRIBUTE-DEFINITION-* identifier → LONG-NAME.
    attr_def_names: dict[str, str] = {}
    for ad in root.iter():
        if not ad.tag.endswith(
            ("ATTRIBUTE-DEFINITION-STRING", "ATTRIBUTE-DEFINITION-XHTML",
             "ATTRIBUTE-DEFINITION-ENUMERATION", "ATTRIBUTE-DEFINITION-INTEGER")
        ):
            continue
        ident = ad.attrib.get("IDENTIFIER")
        long_name = ad.attrib.get("LONG-NAME", "")
        if ident:
            attr_def_names[ident] = long_name

    needs: list[dict[str, Any]] = []
    for spec in root.iter():
        if not spec.tag.endswith("SPEC-OBJECT"):
            continue
        attrs: dict[str, str] = {}
        for v in spec.iter():
            if not v.tag.endswith(("ATTRIBUTE-VALUE-STRING", "ATTRIBUTE-VALUE-XHTML")):
                continue
            ref = v.find(".//{*}ATTRIBUTE-DEFINITION-STRING-REF")
            if ref is None:
                ref = v.find(".//{*}ATTRIBUTE-DEFINITION-XHTML-REF")
            ref_id = ref.text if ref is not None else None
            long_name = attr_def_names.get(ref_id or "", "")

            if v.tag.endswith("ATTRIBUTE-VALUE-STRING"):
                value = v.attrib.get("THE-VALUE", "")
            else:  # XHTML
                xhtml_root = v.find(".//{*}THE-VALUE")
                value = "".join(xhtml_root.itertext()).strip() if xhtml_root is not None else ""
            if long_name:
                attrs[long_name] = value

        need = {
            "id":          attrs.get("ReqIF.ForeignID") or spec.attrib.get("IDENTIFIER", ""),
            "title":       attrs.get("ReqIF.Name", ""),
            "description": attrs.get("ReqIF.Text", ""),
            "status":      attrs.get("Status", "open"),
            "tags":        [t.strip() for t in attrs.get("Tags", "").split(";") if t.strip()],
        }
        needs.append(need)
    return needs


# --------------------------------------------------------------------- export
def export_reqif(needs: list[dict[str, Any]], reqif_path: Path) -> None:
    """Write sphinx-needs-shaped dicts as a minimal ReqIF document."""
    reqif_path = Path(reqif_path)
    reqif_path.parent.mkdir(parents=True, exist_ok=True)

    nsmap = {"": REQIF_NS}

    def _ns(tag: str) -> str:
        return f"{{{REQIF_NS}}}{tag}"

    def _attr(elem: ET.Element, **kwargs: str) -> ET.Element:
        """Set XML attributes preserving hyphenated names (e.g. THE-VALUE)."""
        for k, v in kwargs.items():
            elem.set(k.replace("_", "-"), v)
        return elem

    root = ET.Element(_ns("REQ-IF"))
    header = ET.SubElement(root, _ns("THE-HEADER"))
    rh = ET.SubElement(header, _ns("REQ-IF-HEADER"))
    _attr(rh, IDENTIFIER=f"hdr-{uuid.uuid4()}")
    ET.SubElement(rh, _ns("CREATION-TIME")).text = _dt.datetime.now(
        _dt.timezone.utc
    ).isoformat()
    ET.SubElement(rh, _ns("REQ-IF-TOOL-ID")).text = "sphinx-needs-template/reqif_bridge"
    ET.SubElement(rh, _ns("REQ-IF-VERSION")).text = "1.0"
    ET.SubElement(rh, _ns("SOURCE-TOOL-ID")).text = "sphinx-needs-template"
    ET.SubElement(rh, _ns("TITLE")).text = "Garden requirements export"

    content = ET.SubElement(root, _ns("CORE-CONTENT"))
    reqif_content = ET.SubElement(content, _ns("REQ-IF-CONTENT"))

    # --- DATA-TYPES (one string type) ---
    dts = ET.SubElement(reqif_content, _ns("DATATYPES"))
    string_dt = ET.SubElement(dts, _ns("DATATYPE-DEFINITION-STRING"))
    _attr(string_dt, IDENTIFIER="DT-STRING", MAX_LENGTH="32000", LONG_NAME="String")

    # --- SPEC-TYPES (one type with a few attribute defs) ---
    spec_types = ET.SubElement(reqif_content, _ns("SPEC-TYPES"))
    spec_obj_type = ET.SubElement(spec_types, _ns("SPEC-OBJECT-TYPE"))
    _attr(spec_obj_type, IDENTIFIER="ST-NEED", LONG_NAME="Need")
    sa = ET.SubElement(spec_obj_type, _ns("SPEC-ATTRIBUTES"))
    attr_defs = {
        "AD-FOREIGN-ID":  "ReqIF.ForeignID",
        "AD-NAME":        "ReqIF.Name",
        "AD-TEXT":        "ReqIF.Text",
        "AD-STATUS":      "Status",
        "AD-TAGS":        "Tags",
    }
    for ident, long_name in attr_defs.items():
        ad = ET.SubElement(sa, _ns("ATTRIBUTE-DEFINITION-STRING"))
        _attr(ad, IDENTIFIER=ident, LONG_NAME=long_name)
        type_ref = ET.SubElement(ad, _ns("TYPE"))
        ET.SubElement(type_ref, _ns("DATATYPE-DEFINITION-STRING-REF")).text = "DT-STRING"

    # --- SPEC-OBJECTS ---
    spec_objects = ET.SubElement(reqif_content, _ns("SPEC-OBJECTS"))
    for need in needs:
        so = ET.SubElement(spec_objects, _ns("SPEC-OBJECT"))
        _attr(so, IDENTIFIER=need["id"])
        type_node = ET.SubElement(so, _ns("TYPE"))
        ET.SubElement(type_node, _ns("SPEC-OBJECT-TYPE-REF")).text = "ST-NEED"
        values = ET.SubElement(so, _ns("VALUES"))

        rendered = {
            "AD-FOREIGN-ID": need.get("id", ""),
            "AD-NAME":       need.get("title", ""),
            "AD-TEXT":       need.get("description", ""),
            "AD-STATUS":     need.get("status", ""),
            "AD-TAGS":       ";".join(need.get("tags") or []),
        }
        for ad_id, value in rendered.items():
            avs = ET.SubElement(values, _ns("ATTRIBUTE-VALUE-STRING"))
            _attr(avs, THE_VALUE=value)
            d = ET.SubElement(avs, _ns("DEFINITION"))
            ET.SubElement(d, _ns("ATTRIBUTE-DEFINITION-STRING-REF")).text = ad_id

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(reqif_path, encoding="utf-8", xml_declaration=True)


# --------------------------------------------------------------------- json bridge
def needs_json_to_dicts(needs_json_path: Path) -> list[dict[str, Any]]:
    """Read a sphinx-needs ``needs.json`` and yield need dicts.

    Used by the CLI to chain ``sphinx-build -b needs`` → ReqIF export.
    """
    data = json.loads(Path(needs_json_path).read_text(encoding="utf-8"))
    versions = data.get("versions") or {}
    if not versions:
        return []
    latest = list(versions.values())[-1]
    out: list[dict[str, Any]] = []
    for need_id, need in (latest.get("needs") or {}).items():
        out.append({
            "id":          need_id,
            "title":       need.get("title", ""),
            "description": need.get("content") or need.get("description") or "",
            "status":      need.get("status", "open") or "open",
            "tags":        need.get("tags") or [],
        })
    return out
