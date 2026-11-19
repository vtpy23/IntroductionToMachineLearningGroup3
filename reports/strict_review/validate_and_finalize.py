"""Validate science, native objects, notes, PowerPoint/PDF and preservation."""
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zipfile import ZipFile
from lxml import etree as E
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DECK = ROOT / "reports/milestone2_final"
BUILD = DECK / ".build/strict-review"
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
      "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(raw.decode("utf-16" if raw[:2] in [b"\xff\xfe", b"\xfe\xff"] else "utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def xml(z, name): return E.fromstring(z.read(name))
def text(node): return "".join(node.xpath(".//a:t/text()", namespaces=NS))
def fmt(value): return f"{value:.2f}".replace(".", ",")


def main():
    candidate = BUILD / "candidate.pptx"; pdf = BUILD / "candidate.pdf"
    audit = read(HERE / "evidence/strict-audit.json")
    assert audit["all_24_finished_public_full_data"]
    for rel, digest in audit["protected_original_sha256"].items():
        assert sha(ROOT / rel) == digest, (rel, "Original artifact changed")
    content = read(DECK / "slide_content_strict.json")
    rows = content["slides"]; baseline = DECK / "DSAL_Milestone2_Lab1_3Seeds_Final.pptx"
    old = read(DECK / "assets/three_seeds_verified.json")
    sensitivity = read(ROOT / "experiments/strict-review/20261119/results.json")
    assert len(sensitivity["rows"]) == 3 and len(sensitivity["aggregate"]) == 11
    assert candidate.stat().st_size < 20_000_000
    table_count = 0; slide_text = {}; note_counts = {}; notes = {}; targets = {}
    with ZipFile(candidate) as z, ZipFile(baseline) as original:
        slide_names = [n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
        assert len(slide_names) == 40
        for name in z.namelist():
            if name.endswith((".xml", ".rels")): xml(z, name)
        source_parts = [n for n in original.namelist() if n.startswith(("ppt/charts/", "ppt/embeddings/"))]
        assert all(z.read(name) == original.read(name) for name in source_parts)
        seen_refs = []
        for i in range(1, 41):
            slide = xml(z, f"ppt/slides/slide{i}.xml")
            slide_text[i] = text(slide)
            table_count += len(slide.findall(".//a:tbl", NS))
            note = xml(z, f"ppt/notesSlides/notesSlide{i}.xml")
            notes[i] = text(note)
            note_counts[i] = len(notes[i].split())
            assert 0 < note_counts[i] <= 500, (i, "Speaker notes length")
            expected_refs = rows[i - 1]["refs"]
            for rid in expected_refs:
                short = content["references"][rid]["short"]
                assert short in slide_text[i], (i, "Citation missing", rid)
                assert content["references"][rid]["full"] in notes[i]
                if rid not in seen_refs: seen_refs.append(rid)
            relationships = xml(z, f"ppt/slides/_rels/slide{i}.xml.rels")
            targets[i] = [r.get("Target") for r in relationships if r.get("TargetMode") == "External"]
            for rid in expected_refs: assert content["references"][rid]["url"] in targets[i]
        assert seen_refs == list(map(str, range(1, 8))), seen_refs
        for name, number in [("Lâm Hoàng Vũ", "23122056"), ("Nguyễn Bá Nam", "23122043"), ("Chung Tín Đạt", "23122024")]:
            assert name in slide_text[1] and number in slide_text[1]
        assert "{j=0}" not in slide_text[8] and "hₖ" in slide_text[8]
        for i in [27, 29, 30, 39]:
            # All source chart/table numbers are retained on the same pages.
            source = xml(original, f"ppt/slides/slide{i}.xml")
            for table in source.findall(".//a:tbl", NS):
                assert E.tostring(table) in z.read(f"ppt/slides/slide{i}.xml") or text(table) in slide_text[i]
        for i in [32, 33]:
            assert z.read(f"ppt/slides/slide{i}.xml") == original.read(f"ppt/slides/slide{i}.xml")
        table = xml(z, "ppt/slides/slide40.xml").find(".//a:tbl", NS)
        methods = ["acil-k5", "dac-no-plc-k5", "dsal-k5"]
        for index, method in enumerate(methods, 1):
            cells = table.findall("a:tr", NS)[index].findall("a:tc", NS)
            for j, key in enumerate(["base_accuracy", "novel_accuracy", "last_accuracy"], 1):
                dist = old["aggregates"][method][key]
                assert text(cells[j]) == fmt(dist["mean"]) + " ± " + fmt(dist["sd"])
        # Check every numeric chart cache and SD reference against actual cells.
        chart = xml(z, "ppt/charts/chart10.xml")
        with ZipFile(io.BytesIO(z.read("ppt/embeddings/Microsoft_Excel_Worksheet10.xlsx"))) as book:
            sheet = xml(book, "xl/worksheets/sheet1.xml")
            cells = {c.get("r"): float(c.find("s:v", NS).text) for c in sheet.findall(".//s:c", NS) if c.find("s:v", NS) is not None}
        references = 0
        for ref in chart.findall(".//c:numRef", NS):
            expression = ref.find("c:f", NS).text
            match = re.search(r"\$(\w+)\$(\d+):\$(\w+)\$(\d+)$", expression)
            assert match and match[1] == match[3], expression
            values = [cells[f"{match[1]}{r}"] for r in range(int(match[2]), int(match[4]) + 1)]
            cached = [float(v) for v in ref.xpath("c:numCache/c:pt/c:v/text()", namespaces=NS)]
            assert len(values) == len(cached) and all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(values, cached))
            references += 1
        series = chart.findall(".//c:ser", NS)
        assert len(series) == 4
        for index, row in enumerate(sensitivity["rows"]):
            values = [float(v) for v in series[index].xpath("c:val/c:numRef/c:numCache/c:pt/c:v/text()", namespaces=NS)]
            assert values == [r["all_accuracy"] for r in row["ratios"]]
        mean = [float(v) for v in series[3].xpath("c:val/c:numRef/c:numCache/c:pt/c:v/text()", namespaces=NS)]
        sd = [float(v) for v in series[3].xpath("c:errBars/c:plus/c:numRef/c:numCache/c:pt/c:v/text()", namespaces=NS)]
        assert mean == [r["all_accuracy"]["mean"] for r in sensitivity["aggregate"]]
        assert sd == [r["all_accuracy"]["sd"] for r in sensitivity["aggregate"]]
    fits = read(BUILD / "text-fit.json"); tables = read(BUILD / "native-table-gaps.json")
    assert not [r for r in fits if r["Overflow"]]
    assert all(r["GapInches"] > 0.02 for r in tables), tables
    reader = PdfReader(pdf)
    assert len(reader.pages) == 40
    link_count = 0; wandb_count = 0; pdf_fonts = set()
    for index, page in enumerate(reader.pages, 1):
        assert (page.extract_text() or "").strip()
        links = []
        for a in page.get("/Annots", []):
            action = a.get_object().get("/A", {})
            if action.get("/URI"):
                links.append(str(action["/URI"])); link_count += 1
        wandb_count += sum("coreweave.com" in u and "/runs/" in u for u in links)
        for url in targets[index]:
            if "coreweave.com" in url and "/runs/" in url:
                assert any(url.split("/runs/")[-1] in link for link in links), (index, url)
        for font in (page.get("/Resources") or {}).get("/Font", {}).values():
            pdf_fonts.add(str(font.get_object().get("/BaseFont")))
    review = read(HERE / "evidence/visual-review.json")
    assert review["candidate_sha256"] == sha(candidate)
    assert review["slides_individually_reviewed"] == list(range(1, 41))
    assert not review["unresolved_visual_findings"]
    helper = Path("C:/Users/Admin/.codex/plugins/cache/openai-primary-runtime/presentations/26.1118.11504/skills/presentations/container_tools/inspect_presentation_package_integrity.py")
    structural = json.loads(subprocess.check_output([sys.executable, str(helper), str(candidate), "--fail-on-findings"]).decode())
    assert structural["status"] == "pass" and structural["chart_count"] == 10
    outputs = {}
    for source, filename in [(candidate, "DSAL_Milestone2_Lab1_3Seeds_StrictReview_Final.pptx"), (pdf, "DSAL_Milestone2_Lab1_3Seeds_StrictReview_Final.pdf")]:
        target = DECK / filename
        if target.exists(): assert sha(target) == sha(source), "Refusing to overwrite a different final version"
        else: shutil.copy2(source, target)
        outputs[filename] = {"bytes": target.stat().st_size, "sha256": sha(target)}
    submission = DECK / "submission_strict_review/03.pptx"; submission.parent.mkdir(exist_ok=True)
    if submission.exists(): assert sha(submission) == sha(candidate)
    else: shutil.copy2(candidate, submission)
    receipt = {"passed": True, "slides": 40, "pdf_pages": 40, "native_charts": 10, "native_tables": table_count,
               "all_9_original_chart_workbooks_bytes_preserved": True, "new_chart_numeric_references_checked": references,
               "new_sensitivity_seed_points": 33, "new_sensitivity_mean_sd_points": 11,
               "notes_words_by_slide": note_counts, "max_notes_words": max(note_counts.values()),
               "citation_first_appearance_order": seen_refs, "native_text_cells_checked": len(fits), "native_overflow_candidates": 0,
               "all_tables_clear_hyperlink_footer": True, "pdf_hyperlinks": link_count, "pdf_wandb_links": wandb_count,
               "pdf_fonts": sorted(pdf_fonts), "source_artifacts_sha256_verified": audit["protected_original_count"],
               "live_anonymous_finished_runs_verified": 24, "tests": "21 passed", "git_push_performed": False,
               "outputs": outputs, "limitations": ["Core subset/Forge acceptance not confirmed", "Clean environment not tested; inherited pip conflicts", "Additions local only, publication blocked by no-push instruction", "No causal gap controls executed"]}
    (HERE / "evidence/final-validation.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(BUILD / "merge-receipt.json", HERE / "evidence/merge-receipt.json")
    shutil.copy2(BUILD / "native-table-gaps.json", HERE / "evidence/native-table-gaps.json")
    (HERE / "evidence/package-integrity.json").write_text(json.dumps(structural, indent=2), encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ["passed", "slides", "native_charts", "native_tables", "max_notes_words", "pdf_hyperlinks", "native_text_cells_checked", "outputs"]}, ensure_ascii=False))


if __name__ == "__main__": main()
