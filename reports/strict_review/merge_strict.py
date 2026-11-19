"""Splice reviewed objects into the actual three-seed PPTX, preserving data."""
import ast
import copy
import hashlib
import io
import json
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "reports/milestone2_final"
BUILD = HERE / ".build/strict-review"
BASE = HERE / "DSAL_Milestone2_Lab1_3Seeds_Final.pptx"
GENERATED = BUILD / "generated.pptx"
UPDATED = [4, 5, 8, 10, 16, 17, 20, 22, 24, 25, 28, 31, 34, 36, 37, 40]
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
      "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def serial(node):
    return E.tostring(node, encoding="UTF-8", xml_declaration=True, standalone=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    content = json.loads((HERE / "slide_content_strict.json").read_text(encoding="utf-8"))
    # Import only pure helper definitions, never the old module's build steps.
    tree = ast.parse((HERE / "merge_three_seeds.py").read_text(encoding="utf-8"))
    functions = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[])
    helpers = {"E": E, "NS": NS, "io": io, "ZipFile": ZipFile, "ZIP_DEFLATED": ZIP_DEFLATED, "hashlib": hashlib}
    exec(compile(functions, "pure_errorbar_helpers", "exec"), helpers)
    changes = {}; extra = {}
    with ZipFile(BASE) as base, ZipFile(GENERATED) as generated:
        for number in UPDATED:
            for name in [f"ppt/slides/slide{number}.xml", f"ppt/slides/_rels/slide{number}.xml.rels"]:
                changes[name] = generated.read(name)
        # Preserve original geometry while renumbering citations on other pages.
        for number in range(1, 41):
            if number in UPDATED: continue
            name = f"ppt/slides/slide{number}.xml"
            slide = E.fromstring(base.read(name))
            relname = f"ppt/slides/_rels/slide{number}.xml.rels"
            relationships = E.fromstring(base.read(relname))
            changed = False
            for text in slide.findall(".//a:t", NS):
                match = re.match(r"^\[(\d+)\] ", text.text or "")
                if not match: continue
                new_id = content["citation_renumbering"][match.group(1)]
                text.text = content["references"][new_id]["short"]
                run = text.getparent()
                link = run.find("a:rPr/a:hlinkClick", NS)
                if link is not None:
                    rid = link.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                    for relation in relationships:
                        if relation.get("Id") == rid:
                            relation.set("Target", content["references"][new_id]["url"])
                changed = True
            if changed:
                changes[name] = serial(slide); changes[relname] = serial(relationships)
        for number in range(1, 41):
            changes[f"ppt/notesSlides/notesSlide{number}.xml"] = generated.read(f"ppt/notesSlides/notesSlide{number}.xml")
            if number in UPDATED:
                continue
            name = f"ppt/slides/slide{number}.xml"
            node = E.fromstring(base.read(name))
            relname = f"ppt/slides/_rels/slide{number}.xml.rels"
            rels = E.fromstring(base.read(relname))
            rel_index = {r.get("Id"): r for r in rels}
            for text in node.findall(".//a:t", NS):
                value = text.text or ""
                if value.startswith("[") and "] " in value:
                    old = value[1:value.index("]")]
                    if old not in content["citation_renumbering"]:
                        continue
                    ref = content["references"][content["citation_renumbering"][old]]
                    text.text = ref["short"]
                    click = text.getparent().find("a:rPr/a:hlinkClick", NS)
                    if click is not None:
                        rid = click.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                        rel_index[rid].set("Target", ref["url"])
            changes[name] = serial(node); changes[relname] = serial(rels)
        # Source chart9 belongs to slide38. The generated chart9 now belongs to
        # the new slide36, so append it as chart10 without touching chart9.
        sensitivity = json.loads((ROOT / "experiments/strict-review/20261119/results.json").read_text(encoding="utf-8"))
        chart, workbook = helpers["patch_error_bars"](
            generated.read("ppt/charts/chart9.xml"),
            generated.read("ppt/embeddings/Microsoft_Excel_Worksheet9.xlsx"),
            {3: {"name": "Sample SD across seeds", "values": [r["all_accuracy"]["sd"] for r in sensitivity["aggregate"]]}})
        chart_node = E.fromstring(chart)
        for index, series in enumerate(chart_node.findall(".//c:ser", NS)):
            line = series.find("c:spPr/a:ln", NS)
            if line is not None:
                line.set("w", "34290" if index == 3 else "15240")
                dash = line.find("a:prstDash", NS)
                if dash is None: dash = E.SubElement(line, "{" + NS["a"] + "}prstDash")
                dash.set("val", "solid" if index == 3 else ["dash", "dot", "dashDot"][index])
        extra["ppt/charts/chart10.xml"] = serial(chart_node)
        extra["ppt/embeddings/Microsoft_Excel_Worksheet10.xlsx"] = workbook
        extra["ppt/charts/_rels/chart10.xml.rels"] = generated.read("ppt/charts/_rels/chart9.xml.rels").replace(b"Worksheet9.xlsx", b"Worksheet10.xlsx")
        relname = "ppt/slides/_rels/slide36.xml.rels"
        relationships = E.fromstring(changes[relname])
        for relation in relationships:
            if relation.get("Type", "").endswith("/chart"):
                relation.set("Target", "/ppt/charts/chart10.xml")
        changes[relname] = serial(relationships)
        types = E.fromstring(base.read("[Content_Types].xml"))
        E.SubElement(types, "{http://schemas.openxmlformats.org/package/2006/content-types}Override",
                     PartName="/ppt/charts/chart10.xml", ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml")
        changes["[Content_Types].xml"] = serial(types)
        changes["docProps/core.xml"] = generated.read("docProps/core.xml")
        with ZipFile(BUILD / "candidate.pptx", "w", ZIP_DEFLATED) as output:
            for part in base.infolist():
                output.writestr(copy.copy(part), changes.get(part.filename, base.read(part.filename)))
            for name, data in extra.items(): output.writestr(name, data)
        receipt = {"source": BASE.name, "source_sha256": sha(BASE.read_bytes()),
                   "candidate_sha256": sha((BUILD / "candidate.pptx").read_bytes()),
                   "layout_updated_slides": UPDATED, "notes_updated_slides": list(range(1, 41)),
                   "citation_numbering": content["citation_renumbering"],
                   "all_original_chart_and_workbook_bytes_preserved": all(name not in changes for name in base.namelist() if name.startswith(("ppt/charts/", "ppt/embeddings/"))),
                   "new_chart": "chart10: measured C sensitivity, sample SD, embedded workbook",
                   "source_geometry_preserved_except_selected_layouts": True}
    assert receipt["all_original_chart_and_workbook_bytes_preserved"]
    (BUILD / "merge-receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__": main()
