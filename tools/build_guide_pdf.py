#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jose Di Lenola
# Markdown/ReportLab approach adapted from the MIT Mesh user-guide builder:
# Prophet60191/m5stack-cardputer-zero-mesh-app, scripts/user-guide/build.py.
"""Build a complete offline reading edition; never uploads or accesses hardware."""
import argparse
import hashlib
import html
import json
import re
import textwrap
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, LongTable, PageBreak, PageTemplate, Paragraph, Spacer, TableStyle, Preformatted, Flowable, KeepTogether, Image
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
MD = MarkdownIt('commonmark').enable('table')
INK, ACCENT, MUTED = map(colors.HexColor, ['#192b40', '#8b2447', '#536174'])
REPO = 'https://github.com/Prophet60191/m5stack-cardputer-zero-app-guide'
WIDTH = 516
GROUPS = [
    ('Getting started', ['README.md', 'docs/start-here.md', 'docs/first-app.md', 'docs/first-device-app.md', 'docs/device-app-troubleshooting.md', 'examples/counter-demo/README.md', 'examples/counter-demo/verification.md', 'docs/first-reader-check.md']),
    ('Common foundation', ['docs/'+x for x in ['01-platform.md','02-app-anatomy.md','03-architecture.md','04-ui-and-polish.md','05-keyboard.md','keyboard-system-actions.md','06-building-and-packaging.md','08-security-and-publishing.md']]),
    ('Project recipes', ['docs/projects/'+x for x in ['README.md','local-utilities.md','messaging.md','gps-and-maps.md','camera-and-qr.md','hardware.md','networking.md','audio-and-media.md']] + ['docs/07-radio-bring-up.md']),
    ('Components and personal library', ['docs/'+x for x in ['components.md','library-principles.md','library-inventory.md','official-input-evaluation.md','official-ui-evaluation.md','ui-preferences.md']] + ['examples/ui-patterns/carousel-position/README.md']),
    ('Release references and preserved learning', ['docs/store-readiness.md','tools/README.md','docs/lesson-index.md','docs/case-studies/mesh.md','contributions/template-keyboard/README.md','contributions/template-keyboard/VALIDATION.md']),
]
PATHS = [(ROOT/p).resolve() for _, paths in GROUPS for p in paths]
IMAGE_DIR = ROOT/'docs/images'


def slug(s):
    return re.sub(r'[^\w\- ]', '', s.lower()).replace(' ', '-')


def key(path):
    return 'doc-' + path.relative_to(ROOT).as_posix().replace('/', '-').replace('.', '-')


def normalize(s):
    return s.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u2010','-')


class Anchor(Flowable):
    def __init__(self, name):
        super().__init__()
        self.name = name
    def draw(self):
        self.canv.bookmarkPage(self.name)


class Document(BaseDocTemplate):
    def afterFlowable(self, f):
        if not hasattr(f, 'bookmark'):
            return
        anchor, title, level = f.bookmark
        self.canv.bookmarkPage(anchor)
        self.canv.addOutlineEntry(title, anchor, level, False)
        if level < 2 and anchor != 'contents':
            self.notify('TOCEntry', (level, html.escape(title), self.page, anchor))


class Renderer:
    def __init__(self):
        self.body = ParagraphStyle('Body',fontName='Body',fontSize=10,leading=14.4,textColor=INK,spaceAfter=7,splitLongWords=True,allowWidows=0,allowOrphans=0)
        self.small = ParagraphStyle('Small',parent=self.body,fontSize=8.4,leading=11.5,textColor=MUTED)
        self.cell = ParagraphStyle('Cell',parent=self.body,fontSize=8.1,leading=11,spaceAfter=0)
        self.h = {1:ParagraphStyle('Chapter',parent=self.body,fontName='Body-Bold',fontSize=23,leading=28,textColor=ACCENT,spaceAfter=18,keepWithNext=True),
                  2:ParagraphStyle('Section',parent=self.body,fontName='Body-Bold',fontSize=13,leading=18,spaceBefore=13,spaceAfter=7,keepWithNext=True),
                  3:ParagraphStyle('Subsection',parent=self.body,fontName='Body-Bold',fontSize=10.5,leading=15,spaceBefore=9,spaceAfter=5,keepWithNext=True)}
        self.code = ParagraphStyle('Code',fontName='Code',fontSize=7.5,leading=10.5,textColor=INK,backColor=colors.HexColor('#f1f3f6'),borderPadding=7,spaceBefore=4,spaceAfter=10)

    def link(self, target, path):
        u=urlsplit(target)
        if u.scheme:
            return target
        dest=(path.parent/unquote(u.path)).resolve() if u.path else path
        if dest in PATHS:
            return '#'+key(dest)+('--'+unquote(u.fragment) if u.fragment else '')
        if dest.suffix=='.json' and dest.is_relative_to(ROOT):
            return '#source-notes'
        if dest.is_relative_to(ROOT):
            return REPO+'/blob/main/'+dest.relative_to(ROOT).as_posix()+('#'+u.fragment if u.fragment else '')
        raise ValueError('Link escapes repository')

    def inline(self, tokens, path):
        out=[]
        for t in tokens or []:
            if t.type in ('text','code_inline'):
                text=normalize(t.content)
                missing=set(text)-set(map(chr,pdfmetrics.getFont('Body').face.charWidths))-{'\n','\r'}
                if missing:
                    raise ValueError('Missing font glyphs: '+repr(sorted(missing)))
                out.append(html.escape(text))
            elif t.type in ('strong_open','strong_close','em_open','em_close'):
                tag='b' if t.type.startswith('strong') else 'i'
                out.append('<'+('/' if t.nesting==-1 else '')+tag+'>')
            elif t.type=='link_open':
                out.append('<a href="'+html.escape(self.link(t.attrGet('href'),path),quote=True)+'" color="#8b2447">')
            elif t.type=='link_close':
                out.append('</a>')
            elif t.type=='softbreak':
                out.append(' ')
            elif t.type=='hardbreak' or t.type=='html_inline' and t.content.startswith('<br'):
                out.append('<br/>')
            elif t.type=='html_inline':
                for alias in re.findall(r'<a\s+id="([^"]+)"', t.content):
                    out.append('<a name="'+key(path)+'--'+html.escape(alias,quote=True)+'"/>')
            else:
                raise ValueError('Unsupported inline '+t.type)
        return ''.join(out)

    def table(self, ts, i, path):
        rows=[];row=[];i+=1
        while ts[i].type!='table_close':
            t=ts[i]
            if t.type=='tr_open': row=[]
            elif t.type=='inline': row.append(Paragraph(self.inline(t.children,path) or ' ',self.cell))
            elif t.type=='tr_close': rows.append(row)
            i+=1
        n=len(rows[0])
        fractions={2:[.32,.68],3:[.25,.29,.46],4:[.14,.29,.34,.23]}.get(n,[1/n]*n)
        table=LongTable(rows,colWidths=[WIDTH*x for x in fractions],repeatRows=1,splitByRow=1,splitInRow=1,hAlign='LEFT',spaceAfter=11)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf3')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f7f9')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.6,ACCENT)]))
        return table,i

    def chapter(self,path):
        source=path.read_text();ts=MD.parse(source);headings=[ts[i+1].content for i,t in enumerate(ts) if t.type=='heading_open']
        title=normalize(headings[0]) if source.lstrip().startswith('# ') else ('About this guide' if path==ROOT/'README.md' else path.stem)
        title=re.sub(r'[*`]', '', title)
        p=Paragraph(html.escape(title),self.h[1]);p.bookmark=(key(path),title,1)
        output=[p];lists=[];item=False;first_h1=True;counts={};quote=0;i=0
        while i<len(ts):
            t=ts[i]
            if t.type=='heading_open':
                raw_label=''.join(x.content for x in ts[i+1].children if x.type in ('text','code_inline'))
                label=normalize(raw_label)
                a=slug(raw_label);count=counts.get(a,0);counts[a]=count+1
                if count:a+='-'+str(count)
                anchor=key(path)+'--'+a;level=int(t.tag[1])
                markup='<a name="'+anchor+'"/>'+self.inline(ts[i+1].children,path)
                if level==1 and first_h1:
                    output.append(Anchor(anchor));first_h1=False
                else:
                    f=Paragraph(markup,self.h[min(max(level,2),3)])
                    if level<=2:f.bookmark=(anchor,label,2)
                    output.append(f)
                i+=2
            elif t.type in ('bullet_list_open','ordered_list_open'):
                lists.append(None if t.type=='bullet_list_open' else int(t.attrGet('start') or 1))
            elif t.type in ('bullet_list_close','ordered_list_close'):lists.pop()
            elif t.type=='list_item_open':item=True
            elif t.type=='blockquote_open':quote+=1
            elif t.type=='blockquote_close':quote-=1
            elif t.type=='paragraph_open':
                children=ts[i+1].children or []
                if len(children)==1 and children[0].type=='image':
                    image_path=(path.parent/unquote(children[0].attrGet('src'))).resolve()
                    if not image_path.is_relative_to(IMAGE_DIR) or image_path.suffix.lower()!='.png':
                        raise ValueError('Illustrations must be local PNG assets under docs/images')
                    illustration=Image(str(image_path),width=WIDTH,height=190,kind='proportional')
                    illustration.hAlign='LEFT'
                    illustration.keepWithNext=True
                    illustration.spaceAfter=5
                    output.append(illustration)
                    i+=3
                    continue
                prefix=''
                if lists and item:
                    prefix='• ' if lists[-1] is None else str(lists[-1])+'. '
                    if lists[-1] is not None:lists[-1]+=1
                    item=False
                style=self.body
                if lists:style=ParagraphStyle('List',parent=self.body,leftIndent=12*len(lists))
                if quote:style=ParagraphStyle('Quote',parent=style,leftIndent=12,textColor=MUTED)
                output.append(Paragraph(prefix+self.inline(ts[i+1].children,path),style));i+=2
            elif t.type=='table_open':
                table,i=self.table(ts,i,path);output.append(table)
            elif t.type in ('fence','code_block'):
                lines=[]
                for line in normalize(t.content).expandtabs(4).splitlines():
                    lines.extend(textwrap.wrap(line,width=104,replace_whitespace=False,drop_whitespace=False) or [''])
                block=Preformatted('\n'.join(lines),self.code)
                output.append(KeepTogether([block]) if len(lines)<=40 else block)
            elif t.type=='html_block':
                for alias in re.findall(r'<a\s+id="([^"]+)"',t.content):output.append(Anchor(key(path)+'--'+alias))
            elif t.type in ('hr','list_item_close'):pass
            elif t.type not in ('paragraph_close','heading_close'):
                raise ValueError('Unsupported block '+t.type)
            i+=1
        return output


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--output',type=Path,default=ROOT/'build/guide-pdf/output/pdf')
    a.add_argument('--font-dir',type=Path,required=True)
    a.add_argument('--font-license',type=Path,required=True)
    a.add_argument('--edition',required=True,help='Explicit reading-edition date, YYYY-MM-DD')
    args=a.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    for name,file in [('Body','DejaVuSans.ttf'),('Body-Bold','DejaVuSans-Bold.ttf'),('Body-Italic','DejaVuSans-Oblique.ttf'),('Body-BoldItalic','DejaVuSans-BoldOblique.ttf'),('Code','DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(args.font_dir/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body-Bold',italic='Body-Italic',boldItalic='Body-BoldItalic')
    r=Renderer()
    raw=out/'.app-development-guide.pdf'
    doc=Document(str(raw),pagesize=letter,pageCompression=1,title='Building Apps for the M5Stack Cardputer Zero',author='Cardputer Zero App Guide')
    def page(canvas,document):
        if document.page==1:return
        canvas.setFillColor(MUTED);canvas.setFont('Body',8)
        canvas.drawString(48,760,'CARDPUTER ZERO  /  APP DEVELOPMENT')
        canvas.drawRightString(564,760,args.edition+'  |  WORKING EDITION')
        canvas.setStrokeColor(ACCENT);canvas.setLineWidth(.7);canvas.line(48,751,564,751)
        canvas.drawString(48,27,'Independent community guide  |  CC BY 4.0')
        canvas.drawRightString(564,27,str(document.page))
    doc.addPageTemplates(PageTemplate('Reading',[Frame(48,45,WIDTH,692,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=page))
    cover=ParagraphStyle('Cover',parent=r.h[1],fontSize=34,leading=41,textColor=INK,spaceAfter=22)
    story=[Spacer(1,53),Paragraph('CARDPUTER ZERO',r.h[2]),Spacer(1,15),Paragraph('Building apps<br/>with confidence',cover),Paragraph('A practical development guide for the<br/>M5Stack Cardputer Zero',ParagraphStyle('Subtitle',parent=r.body,fontSize=15,leading=23)),Spacer(1,24),Paragraph('Official foundations. Deliberate design.<br/>Reusable components. Verified delivery.',r.h[2]),Spacer(1,43),Paragraph('Working edition / '+args.edition,r.body),Paragraph('<link href="https://github.com/Prophet60191">https://github.com/Prophet60191</link>',r.small),Spacer(1,12),Paragraph('Core chapters, project recipes, official component evaluations,<br/>personal library principles and release checklists.',r.body),Spacer(1,25),Paragraph('Personal preferences are identified separately from platform requirements. Pending decisions and hardware qualification limits remain explicit. This edition records the current guide; it does not certify a new app, library or device.',r.small),Spacer(1,22),Paragraph('Independent community documentation. M5Stack and Cardputer are trademarks of their owners. Attribution and source details are included at the end.',r.small),PageBreak()]
    p=Paragraph('Contents',r.h[1]);p.bookmark=('contents','Contents',0);story.append(p)
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('T0',parent=r.body,fontName='Body-Bold',fontSize=12,leading=17,spaceBefore=12),ParagraphStyle('T1',parent=r.body,leftIndent=10,fontSize=9.8,leading=14,spaceBefore=4),ParagraphStyle('T2',parent=r.small,leftIndent=22,leading=11,spaceAfter=0)]
    story.append(toc)
    for number,(group,paths) in enumerate(GROUPS,1):
        story.extend([PageBreak(),Spacer(1,35)])
        f=Paragraph('Part '+str(number)+'<br/>'+group,cover);f.bookmark=('part-'+str(number),group,0);story.append(f)
        story.append(Paragraph(str(len(paths))+' chapters',r.body))
        for path in paths:
            story.append(PageBreak());story.extend(r.chapter((ROOT/path).resolve()))
    story.append(PageBreak());f=Paragraph('Source snapshot and attribution',r.h[1]);f.bookmark=('source-notes','Source snapshot and attribution',0);story.append(f)
    for text in ['This edition includes all Markdown chapters under docs/, plus the guide introduction, offline-tool instructions and the prepared keyboard contribution overview/validation. Source references and qualification dates remain as recorded in those chapters.',
                 'The guide is licensed CC BY 4.0. Attribution: Cardputer Zero App Guide. The source repository is '+REPO+'. Runnable tools have their own MIT terms. Official and third-party component licenses remain applicable.',
                 'The Markdown snapshot, source-hash manifest, evidence JSON and DejaVu font notices are embedded as attachments for offline reference. Links to included chapters work within this PDF; external repositories and tools require Internet access.',
                 'Personal UI choices are recorded in the UI preference chapter. That record is authoritative for confirmed and pending decisions; recording a choice does not implement a library feature.']:
        story.append(Paragraph(html.escape(text),r.body))
    doc.multiBuild(story)
    writer=PdfWriter(clone_from=raw)
    snapshot_paths=PATHS+sorted(IMAGE_DIR.glob('*.png'))
    source_manifest={'edition':args.edition,'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in snapshot_paths}}
    import zipfile,io
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        for p in snapshot_paths:z.write(p,p.relative_to(ROOT).as_posix())
        z.write(ROOT/'LICENSE','LICENSE')
        for p in sorted((ROOT/'docs').glob('*evidence.json')):z.write(p,p.relative_to(ROOT).as_posix())
    writer.add_attachment('guide-source-snapshot.zip',buf.getvalue())
    writer.add_attachment('source-manifest.json',json.dumps(source_manifest,indent=2).encode())
    writer.add_attachment('DejaVu-LICENSE.txt',args.font_license.read_bytes())
    writer.add_metadata({'/Title':'Building Apps for the M5Stack Cardputer Zero','/Author':'Cardputer Zero App Guide','/Subject':'App development, official foundations and personal reusable-library principles','/Creator':'Cardputer Zero App Guide PDF builder'})
    final=out/'Cardputer-Zero-App-Development-Guide.pdf'
    with final.open('wb') as stream:writer.write(stream)
    raw.unlink()
    reader=PdfReader(final);text='\n'.join(p.extract_text() for p in reader.pages)
    assert '/Users/' not in text and '\ufffd' not in text
    all_docs=set((ROOT/'docs').rglob('*.md'));assert all_docs.issubset(set(PATHS)),all_docs-set(PATHS)
    result={'file':final.name,'pages':len(reader.pages),'chapters':len(PATHS),'bytes':final.stat().st_size,'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'edition':args.edition}
    (out/'pdf-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
