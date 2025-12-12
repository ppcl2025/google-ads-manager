#!/usr/bin/env python3
"""
Generate Combined Documentation PDF
Creates a single PDF from all documentation files with clickable table of contents
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict


def parse_markdown_headers(content: str) -> List[Tuple[int, str, str]]:
    """
    Parse markdown content to extract headers with their levels and anchor IDs.
    
    Args:
        content: Markdown content
    
    Returns:
        List of tuples: (level, header_text, anchor_id)
    """
    headers = []
    lines = content.split('\n')
    
    for line in lines:
        # Match markdown headers (# ## ###)
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))
            header_text = match.group(2).strip()
            # Create anchor ID from header text
            anchor_id = re.sub(r'[^a-zA-Z0-9\s-]', '', header_text.lower())
            anchor_id = re.sub(r'\s+', '_', anchor_id)
            anchor_id = anchor_id.strip('_')
            headers.append((level, header_text, anchor_id))
    
    return headers


def markdown_to_html(text: str) -> str:
    """
    Convert markdown formatting to HTML for ReportLab Paragraph.
    Handles: bold, italic, code, links, preserving original formatting.
    
    Args:
        text: Markdown text
    
    Returns:
        HTML-formatted text
    """
    from xml.sax.saxutils import escape
    
    if not text or not text.strip():
        return ""
    
    # Use a unique marker that won't appear in text
    MARKER = "___MARKER___"
    markers = {}
    marker_count = 0
    
    def get_marker():
        nonlocal marker_count
        marker = f"{MARKER}{marker_count}{MARKER}"
        marker_count += 1
        return marker
    
    # Step 1: Protect code blocks (backticks) - they should not be formatted
    def protect_code(match):
        code_text = match.group(1)
        marker = get_marker()
        markers[marker] = f'<font name="Courier" size="9">{escape(code_text)}</font>'
        return marker
    
    text = re.sub(r'`([^`]+?)`', protect_code, text)
    
    # Step 2: Protect markdown links - convert to HTML links
    def protect_link(match):
        link_text = match.group(1)
        link_url = match.group(2)
        marker = get_marker()
        # Handle internal links (starting with #) vs external links
        if link_url.startswith('#'):
            # Internal link - use destination attribute
            markers[marker] = f'<link destination="{link_url[1:]}" color="blue"><u>{escape(link_text)}</u></link>'
        else:
            # External link
            markers[marker] = f'<link href="{escape(link_url)}" color="blue"><u>{escape(link_text)}</u></link>'
        return marker
    
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', protect_link, text)
    
    # Step 3: Escape HTML special characters (but not our markers)
    # Replace markers temporarily, escape, then restore
    temp_markers = {}
    for marker, content in markers.items():
        temp_key = f"TEMP{marker_count}"
        temp_markers[temp_key] = marker
        text = text.replace(marker, temp_key)
        marker_count += 1
    
    text = escape(text)
    
    # Restore markers
    for temp_key, marker in temp_markers.items():
        text = text.replace(temp_key, marker)
    
    # Step 4: Process bold (**text** or __text__)
    # Process **text** first
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
    # Process __text__ but avoid matching markers
    text = re.sub(r'__(?![^_]*MARKER)([^_]+?)__', r'<b>\1</b>', text)
    
    # Step 5: Process italic (*text* or _text_)
    # Process *text* (single asterisk, not part of **)
    text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<i>\1</i>', text)
    # Process _text_ (single underscore, not part of __ and not in code/markers)
    text = re.sub(r'(?<!_)_(?![^_]*MARKER)([^_\s\n]+?)_(?!\d)', r'<i>\1</i>', text)
    
    # Step 6: Restore protected content (code and links)
    for marker, html_content in markers.items():
        text = text.replace(marker, html_content)
    
    # Step 7: Line breaks (but preserve single newlines within paragraphs)
    # Don't convert \n to <br/> here - let ReportLab handle paragraph breaks
    
    return text


def load_all_documentation() -> List[Tuple[str, str, List[Tuple[int, str, str]]]]:
    """
    Load all markdown files from docs folder.
    
    Returns:
        List of tuples: (doc_name, content, headers)
    """
    docs = []
    docs_path = Path(__file__).parent / 'docs'
    
    if not docs_path.exists():
        print(f"Error: docs folder not found at {docs_path}")
        return docs
    
    # Get all markdown files except README.md
    md_files = sorted([f for f in docs_path.glob('*.md') if f.name != 'README.md'])
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                doc_name = md_file.stem
                headers = parse_markdown_headers(content)
                docs.append((doc_name, content, headers))
                print(f"✓ Loaded {md_file.name} ({len(headers)} headers)")
        except Exception as e:
            print(f"⚠️  Warning: Could not load {md_file.name}: {e}")
    
    return docs


def generate_docs_pdf(output_path: str = None):
    """
    Generate a combined PDF from all documentation files.
    
    Args:
        output_path: Path to save PDF (default: docs/Combined_Documentation.pdf)
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor, black, darkblue, darkgreen
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
        from xml.sax.saxutils import escape
    except ImportError:
        print("❌ Error: reportlab not installed.")
        print("   Install with: pip install reportlab")
        return False
    
    # Set output path
    if output_path is None:
        output_path = Path(__file__).parent / 'docs' / 'Combined_Documentation.pdf'
    else:
        output_path = Path(output_path)
    
    print(f"\n📚 Generating Combined Documentation PDF...")
    print(f"   Output: {output_path}\n")
    
    # Load all documentation
    all_docs = load_all_documentation()
    
    if not all_docs:
        print("❌ No documentation files found!")
        return False
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor('#666666'),
        spaceAfter=40,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    doc_title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=HexColor('#1a5490'),
        spaceAfter=20,
        spaceBefore=40,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=HexColor('#1a5490'),
        borderPadding=10,
        backColor=HexColor('#e8f0f8')
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=HexColor('#1a5490'),
        spaceAfter=12,
        spaceBefore=24,
        fontName='Helvetica-Bold'
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#2c5f8d'),
        spaceAfter=10,
        spaceBefore=18,
        fontName='Helvetica-Bold'
    )
    
    h3_style = ParagraphStyle(
        'H3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=HexColor('#3d6fa3'),
        spaceAfter=8,
        spaceBefore=14,
        fontName='Helvetica-Bold'
    )
    
    toc_style = ParagraphStyle(
        'TOC',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#1a5490'),
        spaceAfter=6,
        leftIndent=0,
        fontName='Helvetica'
    )
    
    toc_h1_style = ParagraphStyle(
        'TOC_H1',
        parent=toc_style,
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceAfter=8,
        spaceBefore=12
    )
    
    toc_h2_style = ParagraphStyle(
        'TOC_H2',
        parent=toc_style,
        fontSize=11,
        leftIndent=20,
        spaceAfter=4
    )
    
    toc_h3_style = ParagraphStyle(
        'TOC_H3',
        parent=toc_style,
        fontSize=10,
        leftIndent=40,
        spaceAfter=2
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,  # Changed from TA_JUSTIFY for better readability
        spaceAfter=10
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        leading=12,
        leftIndent=20,
        backColor=HexColor('#f5f5f5'),
        borderWidth=1,
        borderColor=HexColor('#dddddd'),
        borderPadding=8
    )
    
    # Title page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Google Ads Account Manager", title_style))
    story.append(Paragraph("AI Agent", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Complete Documentation", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(PageBreak())
    
    # Build table of contents with destinations map
    print("📑 Building Table of Contents...")
    story.append(Paragraph("Table of Contents", doc_title_style))
    story.append(Spacer(1, 0.3*inch))
    
    toc_entries = []
    destinations = {}  # Track all destinations for TOC links
    
    for doc_name, content, headers in all_docs:
        # Document title in TOC
        doc_display_name = doc_name.replace('_', ' ').title()
        doc_anchor = f"doc_{doc_name}"
        toc_entries.append((1, doc_display_name, doc_anchor))
        destinations[doc_anchor] = True
        
        # Headers in TOC
        for level, header_text, anchor_id in headers:
            if level <= 3:  # Only include H1, H2, H3 in TOC
                full_anchor = f"{doc_name}_{anchor_id}"
                toc_entries.append((level + 1, header_text, full_anchor))
                destinations[full_anchor] = True
    
    # Add TOC entries with clickable links
    for level, text, anchor_id in toc_entries:
        style = toc_h1_style if level == 1 else (toc_h2_style if level == 2 else toc_h3_style)
        
        # Create clickable link using destination (ReportLab internal links)
        link_text = f'<link destination="{anchor_id}" color="blue"><u>{escape(text)}</u></link>'
        story.append(Paragraph(link_text, style))
    
    story.append(PageBreak())
    
    # Process each document
    print("📄 Processing documents...")
    for doc_idx, (doc_name, content, headers) in enumerate(all_docs):
        doc_display_name = doc_name.replace('_', ' ').title()
        print(f"   Processing {doc_display_name}...")
        
        # Document title with bookmark/destination
        doc_anchor = f"doc_{doc_name}"
        doc_title = Paragraph(f'<a name="{doc_anchor}"/>{escape(doc_display_name)}', doc_title_style)
        story.append(doc_title)
        story.append(Spacer(1, 0.2*inch))
        
        # Process content line by line
        lines = content.split('\n')
        i = 0
        last_was_paragraph = False
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Skip empty lines (but add minimal spacing)
            if not line:
                if last_was_paragraph:
                    story.append(Spacer(1, 0.05*inch))
                last_was_paragraph = False
                i += 1
                continue
            
            # Headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                header_text = header_match.group(2).strip()
                anchor_id = re.sub(r'[^a-zA-Z0-9\s-]', '', header_text.lower())
                anchor_id = re.sub(r'\s+', '_', anchor_id)
                anchor_id = anchor_id.strip('_')
                full_anchor = f"{doc_name}_{anchor_id}"
                
                # Choose style based on level
                if level == 1:
                    style = h1_style
                elif level == 2:
                    style = h2_style
                else:
                    style = h3_style
                
                # Create header with bookmark/destination
                header_html = f'<a name="{full_anchor}"/>{escape(header_text)}'
                story.append(Paragraph(header_html, style))
                last_was_paragraph = False
                i += 1
                continue
            
            # Code blocks (```code```)
            if line.strip().startswith('```'):
                code_lines = []
                i += 1  # Skip opening ```
                while i < len(lines) and not lines[i].strip().endswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1  # Skip closing ```
                
                if code_lines:
                    code_text = '\n'.join(code_lines).strip()
                    code_html = f'<font name="Courier" size="9">{escape(code_text)}</font>'
                    story.append(Paragraph(code_html, code_style))
                    story.append(Spacer(1, 0.1*inch))
                last_was_paragraph = False
                continue
            
            # Lists (bullets and numbered)
            if re.match(r'^[\s]*[-*+]\s+', line) or re.match(r'^[\s]*\d+\.\s+', line):
                # Collect all list items
                list_items = []
                while i < len(lines) and (re.match(r'^[\s]*[-*+]\s+', lines[i]) or 
                                          re.match(r'^[\s]*\d+\.\s+', lines[i]) or
                                          (lines[i].strip() and not lines[i].strip().startswith('#') and 
                                           re.match(r'^[\s]{4,}', lines[i]))):
                    list_line = lines[i]
                    # Remove list marker but preserve indentation for nested items
                    if re.match(r'^[\s]*[-*+]\s+', list_line):
                        list_line = re.sub(r'^[\s]*[-*+]\s+', '', list_line)
                    elif re.match(r'^[\s]*\d+\.\s+', list_line):
                        list_line = re.sub(r'^[\s]*\d+\.\s+', '', list_line)
                    list_items.append(list_line.strip())
                    i += 1
                
                # Add list items
                for item in list_items:
                    if item:
                        item_html = markdown_to_html(item)
                        story.append(Paragraph(f'• {item_html}', body_style))
                story.append(Spacer(1, 0.05*inch))
                last_was_paragraph = True
                continue
            
            # Horizontal rules (---)
            if re.match(r'^---+$', line):
                story.append(Spacer(1, 0.2*inch))
                story.append(Paragraph('_' * 80, body_style))
                story.append(Spacer(1, 0.2*inch))
                last_was_paragraph = False
                i += 1
                continue
            
            # Regular paragraph
            if line.strip():
                para_html = markdown_to_html(line)
                story.append(Paragraph(para_html, body_style))
                last_was_paragraph = True
            
            i += 1
        
        # Add page break between documents (except last)
        if doc_idx < len(all_docs) - 1:
            story.append(PageBreak())
    
    # Build PDF
    print("\n🔨 Building PDF...")
    try:
        doc.build(story)
        print(f"\n✅ Success! PDF generated: {output_path}")
        print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
        print(f"   📖 TOC links are clickable - click any entry to jump to that section!")
        return True
    except Exception as e:
        print(f"\n❌ Error building PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    # Get output path from command line if provided
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    success = generate_docs_pdf(output_path)
    
    if success:
        print("\n💡 Tip: All TOC entries are clickable links that jump to their sections!")
        sys.exit(0)
    else:
        sys.exit(1)
