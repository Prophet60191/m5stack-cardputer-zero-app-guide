#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Render the maintained report and assemble an offline review bundle.

No fetch, build, install, authentication, RF or submission operation is performed.
Full bundles require exact local source revisions and completed CI evidence.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlsplit
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEMPLATE = ROOT / "contributions/template-keyboard"
REPO = "https://github.com/Prophet60191/m5stack-cardputer-zero-app-guide"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def validate_evidence(meta, evidence, proposal):
    if evidence["mesh_source"] != meta["mesh_commit"]:
        raise ValueError("Mesh evidence source differs from the report")
    if evidence["template_baseline"] != meta["template_commit"]:
        raise ValueError("Template evidence source differs from the report")
    if meta["template_patch_sha256"] != proposal["patch_sha256"] or evidence["template_patch_sha256"] != proposal["patch_sha256"]:
        raise ValueError("Template patch/evidence differ")
    if set(evidence) != {"reviewed_on", "mesh_source", "template_baseline", "template_patch_sha256",
                        "local", "mesh_ci", "installed_mesh", "limits", "upstream_submission"}:
        raise ValueError("Use only the reviewed evidence fields; exclude raw device state")
    expected_local = {"mesh_backend_cases", "mesh_macos_sanitizers", "mesh_debian_arm64_reader_sanitizers",
                      "mesh_debian_arm64_package_upgrade_firewall", "template_macos_sanitizers",
                      "template_arm64_clean_source_sanitizers"}
    if set(evidence["local"]) != expected_local or evidence["local"]["mesh_backend_cases"] != 98:
        raise ValueError("Unexpected local validation record")
    if any(value != "passed" for name, value in evidence["local"].items() if name != "mesh_backend_cases"):
        raise ValueError("Local validation is not complete")
    if set(evidence["mesh_ci"]) != {"run_id", "conclusion"} or evidence["mesh_ci"]["conclusion"] != "success":
        raise ValueError("Mesh exact-source CI is not successful")
    required = {"status", "version", "package_sha256", "runtime_files_match", "settings_preserved",
                "history_preserved", "live_version_verified", "input_replay", "native_ui_startup",
                "ordinary_user", "firewall_healthy"}
    installed = evidence["installed_mesh"]
    if set(installed) != required or installed["status"] != "verified" or installed["version"] != meta["mesh_version"]:
        raise ValueError("Installed-runtime evidence is incomplete or contains unreviewed fields")
    if not re.fullmatch(r"[a-f0-9]{64}", installed["package_sha256"]):
        raise ValueError("Invalid package hash")
    if any(installed[name] is not True for name in required - {"status", "version", "package_sha256"}):
        raise ValueError("Installed-runtime checks are incomplete")
    text = json.dumps(evidence)
    if any(value in text for value in ("/Users/", "/home/", "CardputerZero-", "ssh-", "PRIVATE KEY")) or re.search(r"\b[\w-]+\.local\b", text):
        raise ValueError("Unexpected private/device material in evidence")


def validate_ci(snapshot, guide_sha, meta):
    if snapshot["guide_commit"] != guide_sha or snapshot["mesh_commit"] != meta["mesh_commit"]:
        raise ValueError("CI snapshot source mismatch")
    if snapshot["template_patch_sha256"] != meta["template_patch_sha256"]:
        raise ValueError("CI snapshot patch mismatch")
    required = {"Guide and offline preflight", "Prepared Template keyboard contribution", "M5Stack review report"}
    found = set()
    app_found = False
    for run in snapshot["runs"]:
        if set(run) != {"repository", "run_id", "name", "head_sha", "conclusion", "url"}:
            raise ValueError("Use a reviewed CI summary, not an arbitrary raw record")
        if run["conclusion"] != "success":
            raise ValueError("CI run is not successful")
        if run["repository"] == "Prophet60191/m5stack-cardputer-zero-app-guide" and run["head_sha"] == guide_sha:
            found.add(run["name"])
        if run["repository"] == "Prophet60191/m5stack-cardputer-zero-mesh-app" and run["head_sha"] == meta["mesh_commit"]:
            app_found |= run["name"] == "Offline regressions"
        expected_url = f"https://github.com/{run['repository']}/actions/runs/{run['run_id']}"
        if run["url"] != expected_url:
            raise ValueError("Unexpected CI link")
    if not required <= found or not app_found:
        raise ValueError("Missing successful exact-source application/guide/report CI")


def render_pdf(source, output, guide_sha):
    from markdown_it import MarkdownIt
    from pypdf import PdfReader
    from reportlab import rl_config
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (Flowable, SimpleDocTemplate, Paragraph, Spacer,
                                   Table, TableStyle, PageBreak, XPreformatted)
    rl_config.invariant = 1
    ink, red, muted = (colors.HexColor(x) for x in ("#173047", "#B52832", "#536271"))
    width = letter[0] - 88
    styles = {
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=14,
                               textColor=ink, spaceAfter=7, splitLongWords=True),
        "h1": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=23, leading=28,
                             textColor=ink, spaceAfter=15, keepWithNext=True),
        "h2": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=14, leading=18,
                             textColor=red, spaceBefore=14, spaceAfter=8, keepWithNext=True),
        "h3": ParagraphStyle("subsection", fontName="Helvetica-Bold", fontSize=11, leading=15,
                             textColor=ink, spaceBefore=9, spaceAfter=5, keepWithNext=True),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8.8, leading=12,
                               textColor=ink, splitLongWords=True),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=7.7, leading=10,
                               textColor=ink, backColor=colors.HexColor("#F1F4F6"), spaceAfter=8),
    }
    def inline(children):
        parts = []
        for token in children or []:
            if token.type == "text": parts.append(html.escape(token.content))
            elif token.type == "code_inline": parts.append('<font name="Courier" size="8.5">' + html.escape(token.content) + '</font>')
            elif token.type in ("softbreak", "hardbreak"): parts.append(" ")
            elif token.type == "strong_open": parts.append("<b>")
            elif token.type == "strong_close": parts.append("</b>")
            elif token.type == "em_open": parts.append("<i>")
            elif token.type == "em_close": parts.append("</i>")
            elif token.type == "link_open":
                target = token.attrGet("href")
                if not urlsplit(target).scheme:
                    dest = (HERE / target).resolve()
                    target = f"{REPO}/blob/{guide_sha}/{dest.relative_to(ROOT).as_posix()}"
                if urlsplit(target).scheme != "https": raise ValueError("Unexpected link scheme")
                parts.append('<a color="#23588A" href="' + html.escape(target, quote=True) + '">')
            elif token.type == "link_close": parts.append("</a>")
        return "".join(parts)

    class Architecture(Flowable):
        def __init__(self):
            super().__init__(); self.width=width; self.height=156
        def draw(self):
            canvas=self.canv
            boxes=[(0,86,130,"Native UI / input","Presentation and intents"),
                   (190,86,140,"Python supervisor","Radio / state authority"),
                   (390,86,134,"Guardian + daemon","Containment / radio API"),
                   (190,16,140,"Firewall monitor","Narrow health verdict")]
            for x,y,w,title,detail in boxes:
                canvas.setFillColor(colors.HexColor("#F0F4F7"));canvas.setStrokeColor(ink)
                canvas.roundRect(x,y,w,46,5,fill=1,stroke=1)
                canvas.setFillColor(ink);canvas.setFont("Helvetica-Bold",9);canvas.drawCentredString(x+w/2,y+29,title)
                canvas.setFont("Helvetica",7.7);canvas.drawCentredString(x+w/2,y+13,detail)
            def arrow(x1,y1,x2,y2):
                canvas.setStrokeColor(red);canvas.setFillColor(red);canvas.line(x1,y1,x2,y2)
                path=canvas.beginPath();path.moveTo(x2,y2)
                if x1 == x2: path.lineTo(x2-3,y2-6);path.lineTo(x2+3,y2-6)
                else: path.lineTo(x2-6,y2-3);path.lineTo(x2-6,y2+3)
                path.close();canvas.drawPath(path,fill=1,stroke=0)
            arrow(130,109,190,109);arrow(330,109,390,109);arrow(260,62,260,86)
            canvas.setFillColor(muted);canvas.setFont("Helvetica",6.8)
            canvas.drawCentredString(160,122,"Private socket")
            canvas.drawCentredString(360,122,"Fixed actions / API")
            canvas.drawString(0,0,"Simplified responsibilities: guardian and daemon are distinct processes.")

    tokens=MarkdownIt("commonmark").enable("table").parse(source)
    story=[];index=0;list_depth=0
    while index<len(tokens):
        token=tokens[index]
        if token.type=="heading_open":
            label=tokens[index+1].content
            if label.startswith("3. Why Mesh"):
                story.append(PageBreak())
            story.append(Paragraph(inline(tokens[index+1].children), styles.get(token.tag,styles["h3"])))
            index+=3;continue
        if token.type=="paragraph_open":
            text=inline(tokens[index+1].children)
            story.append(Paragraph(("&#8226; " if list_depth else "")+text,styles["body"]))
            index+=3;continue
        if token.type in ("bullet_list_open","ordered_list_open"): list_depth+=1
        elif token.type in ("bullet_list_close","ordered_list_close"): list_depth-=1
        elif token.type=="table_open":
            rows=[];row=[]
            while tokens[index].type!="table_close":
                current=tokens[index]
                if current.type=="tr_open": row=[]
                elif current.type=="inline": row.append(Paragraph(inline(current.children),styles["cell"]))
                elif current.type=="tr_close": rows.append(row)
                index+=1
            widths=[width*.24,width*.26,width*.5] if len(rows[0])==3 else [width*.29,width*.71]
            table=Table(rows,colWidths=widths,repeatRows=1,hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#DFE7ED")),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#F4F7F9"),colors.white]),
                ("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),7),
                ("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),7),
                ("BOTTOMPADDING",(0,0),(-1,-1),7),("LINEBELOW",(0,0),(-1,0),.7,red)]))
            story.extend([table,Spacer(1,10)])
        elif token.type=="html_block" and "architecture-diagram" in token.content:
            story.extend([Architecture(),Spacer(1,8)])
        elif token.type=="fence": story.append(XPreformatted(html.escape(token.content),styles["code"]))
        index+=1
    def page(canvas,doc):
        canvas.setStrokeColor(red);canvas.line(44,750,568,750)
        canvas.setFillColor(muted);canvas.setFont("Helvetica-Bold",8)
        canvas.drawString(44,760,"CARDPUTERZERO  /  COMMUNITY ENGINEERING REVIEW")
        canvas.setFont("Helvetica",8);canvas.drawRightString(568,760,"16 NOVEMBER 2026")
        canvas.line(44,40,568,40)
        canvas.setFont("Helvetica",7.7);canvas.drawString(44,27,"Prepared for review | source, evidence and licenses supplied separately")
        canvas.drawRightString(568,27,str(doc.page))
    doc=SimpleDocTemplate(str(output),pagesize=letter,leftMargin=44,rightMargin=44,topMargin=58,bottomMargin=56,
                          title="CardputerZero keyboard improvements and modular architecture",
                          author="Cardputer Zero Mesh community project")
    doc.build(story,onFirstPage=page,onLaterPages=page)
    reader=PdfReader(output);text="\n".join(p.extract_text() for p in reader.pages)
    for required in ("Executive summary","128 raw","700 ms","Why Mesh deliberately uses modularity",
                     "Costs and limits","not submitted","Licensing, sensitivity"):
        if required not in text: raise ValueError("Missing PDF content: "+required)
    return len(reader.pages)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--report-only",action="store_true")
    parser.add_argument("--mesh-repo",type=Path)
    parser.add_argument("--template-repo",type=Path)
    parser.add_argument("--ci-evidence",type=Path)
    args=parser.parse_args()
    meta=json.loads((HERE/"revisions.json").read_text())
    evidence=json.loads((HERE/"evidence.json").read_text())
    proposal=json.loads((TEMPLATE/"upstream.json").read_text())
    validate_evidence(meta,evidence,proposal)
    if digest(TEMPLATE/"keyboard.patch") != meta["template_patch_sha256"] or digest(HERE/"mesh-input-maintenance.patch") != meta["mesh_patch_sha256"]:
        raise ValueError("Review patch bytes differ from revisions.json")
    sha=git(ROOT,"rev-parse","HEAD")
    if not args.report_only:
        if not all((args.mesh_repo,args.template_repo,args.ci_evidence)):
            parser.error("A full bundle requires exact local source checkouts and completed CI evidence")
        if git(ROOT,"status","--porcelain","--untracked-files=all"):
            raise ValueError("Commit/review the guide before creating a final source-correlated bundle")
        if git(args.mesh_repo,"rev-parse","HEAD") != meta["mesh_commit"] or git(args.template_repo,"rev-parse","HEAD") != meta["template_commit"]:
            raise ValueError("Source archive checkout differs from the reviewed revision")
        validate_ci(json.loads(args.ci_evidence.read_text()),sha,meta)
    out=args.output.resolve()
    if out==ROOT or (ROOT in out.parents and ROOT/"build" not in out.parents):
        raise ValueError("Repository outputs belong under build/, not the maintained source tree")
    if out.exists() and any(out.iterdir()): raise ValueError("Use a fresh output directory")
    out.mkdir(parents=True,exist_ok=True)
    pdf=out/"M5Stack-CardputerZero-Engineering-Report.pdf"
    pages=render_pdf((HERE/"REPORT.md").read_text(),pdf,sha)
    if args.report_only:
        print(json.dumps({"pages":pages,"sha256":digest(pdf),"mode":"report-only"}));return
    for name in ("REPORT.md","README.md","revisions.json","evidence.json","mesh-input-maintenance.patch"):
        shutil.copyfile(HERE/name,out/name)
    shutil.copyfile(ROOT/"LICENSE",out/"REPORT-LICENSE-CC-BY-4.0")
    target=out/"template";target.mkdir()
    for name in ("README.md","VALIDATION.md","PR-DRAFT.md","LICENSE","Dockerfile","verify.py","keyboard.patch","upstream.json"):
        shutil.copyfile(TEMPLATE/name,target/name)
    # Preserve working in-bundle links; point repository-only links to the exact
    # reviewed source instead of leaving broken ../../ paths in the ZIP.
    for original, copied in [(HERE/"README.md",out/"README.md"),
                             (TEMPLATE/"README.md",target/"README.md"),
                             (TEMPLATE/"VALIDATION.md",target/"VALIDATION.md")]:
        def resolve_link(match):
            href=match[1]
            if urlsplit(href).scheme or href.startswith("#"): return match[0]
            candidate=(copied.parent/href).resolve()
            if candidate.is_relative_to(out) and candidate.exists(): return match[0]
            source=(original.parent/href).resolve()
            return "]("+f"{REPO}/blob/{sha}/{source.relative_to(ROOT).as_posix()}"+")"
        copied.write_text(re.sub(r"\]\(([^)]+)\)",resolve_link,copied.read_text()))
    for repo,revision,name in [(args.mesh_repo,meta["mesh_commit"],"mesh-source.tar.gz"),
                               (args.template_repo,meta["template_commit"],"template-baseline-source.tar.gz"),
                               (ROOT,sha,"guide-source.tar.gz")]:
        subprocess.run(["git","-C",str(repo),"archive","--format=tar.gz","--output",str(out/name),revision],check=True)
    for name in ("LICENSE","NOTICE","THIRD_PARTY_NOTICES.md"):
        shutil.copyfile(args.mesh_repo/name,out/("MESH-"+name))
    shutil.copyfile(args.ci_evidence,out/"CI-EVIDENCE.json")
    (out/"SOURCE_GUIDE_COMMIT").write_text(sha+"\n")
    files={p.relative_to(out).as_posix():digest(p) for p in sorted(out.rglob("*")) if p.is_file()}
    manifest={"format":1,"guide_commit":sha,"mesh_commit":meta["mesh_commit"],
              "template_commit":meta["template_commit"],"report_pages":pages,
              "status":"prepared for review; not submitted", "files":files}
    (out/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    files["MANIFEST.json"]=digest(out/"MANIFEST.json")
    (out/"SHA256SUMS").write_text("".join(f"{value}  {name}\n" for name,value in sorted(files.items())))
    archive=out.parent/(out.name+".zip")
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(out.rglob("*")):
            if path.is_file():bundle.write(path,path.relative_to(out))
    print(json.dumps({"report_pages":pages,"files":len(files)+1,"bundle_sha256":digest(archive),"guide_commit":sha}))


if __name__=="__main__": main()
