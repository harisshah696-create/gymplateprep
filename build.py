#!/usr/bin/env python3
"""Gym Nutrition Blog — Static Site Generator
Zero dependencies, pure Python 3 standard library.
Converts markdown to HTML, applies templates, outputs to _site/
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# ─── Configuration ────────────────────────────────────────────
CONTENT_DIR = Path("content")
TEMPLATES_DIR = Path("templates")
STATIC_DIR = Path("static")
OUTPUT_DIR = Path("_site")

SITE_TITLE = "GymPlatePrep"
SITE_DESCRIPTION = "Science-backed gym nutrition guides, meal prep recipes, and diet plans for muscle gain and fat loss."
SITE_URL = "https://gymplateprep.com"
AUTHOR = "GymPlatePrep"

# ─── Simple Markdown → HTML Converter ─────────────────────────

def md_to_html(text):
    """Convert markdown text to HTML using only stdlib."""
    lines = text.split("\n")
    html = []
    i = 0
    in_code_block = False
    code_buffer = []
    code_lang = ""
    in_list = False
    list_type = None  # 'ul' or 'ol'
    list_buffer = []
    in_table = False
    table_buffer = []

    def flush_list():
        nonlocal list_buffer, in_list
        if not list_buffer:
            return
        tag = "ol" if list_type == "ol" else "ul"
        html.append(f"<{tag}>")
        for item in list_buffer:
            html.append(f"<li>{item}</li>")
        html.append(f"</{tag}>")
        list_buffer = []
        in_list = False

    def flush_table():
        nonlocal table_buffer, in_table
        if not table_buffer:
            return
        html.append("<table>")
        for idx, row in enumerate(table_buffer):
            cell_tag = "th" if idx == 0 else "td"
            html.append(f"<tr>{''.join(f'<{cell_tag}>{inline_md(c.strip())}</{cell_tag}>' for c in row)}</tr>")
        html.append("</table>")
        table_buffer = []
        in_table = False

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                code = "\n".join(code_buffer)
                lang = code_lang if code_lang else ""
                html.append(f'<pre><code class="language-{lang}">{escape_html(code)}</code></pre>')
                code_buffer = []
                code_lang = ""
                in_code_block = False
            else:
                flush_list()
                flush_table()
                in_code_block = True
                code_lang = line.strip()[3:].strip()
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # Tables
        if "|" in line and line.strip().startswith("|"):
            cells = [c for c in line.strip().split("|") if c.strip() or c == ""]
            # Remove first/last empty if pipe starts/ends
            parts = line.strip().split("|")
            if line.strip().startswith("|"):
                parts = parts[1:]
            if line.strip().endswith("|"):
                parts = parts[:-1]
            parts = [p.strip() for p in parts]

            # Skip separator row (|---|---|)
            if all(re.match(r'^[-:\s]+$', p) for p in parts if p):
                in_table = True
                i += 1
                continue

            if not in_table:
                flush_list()
                in_table = True
                table_buffer = [parts]
            else:
                table_buffer.append(parts)
            i += 1
            continue
        else:
            if in_table:
                flush_table()

        # Empty line
        if not line.strip():
            flush_list()
            flush_table()
            if html and html[-1] != "":
                html.append("")
            i += 1
            continue

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            flush_list()
            flush_table()
            level = len(heading_match.group(1))
            content = inline_md(heading_match.group(2))
            html.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}\s*$', line.strip()):
            flush_list()
            flush_table()
            html.append("<hr>")
            i += 1
            continue

        # Blockquote
        if line.strip().startswith(">"):
            flush_list()
            flush_table()
            content = inline_md(line.strip()[1:].strip())
            html.append(f"<blockquote>{content}</blockquote>")
            i += 1
            continue

        # Unordered list
        ul_match = re.match(r'^[\s]*[-*+]\s+(.+)$', line)
        if ul_match:
            if not in_list:
                flush_table()
                in_list = True
                list_type = "ul"
            elif list_type != "ul":
                flush_list()
                in_list = True
                list_type = "ul"
            list_buffer.append(inline_md(ul_match.group(1)))
            i += 1
            continue

        # Ordered list
        ol_match = re.match(r'^[\s]*\d+\.\s+(.+)$', line)
        if ol_match:
            if not in_list:
                flush_table()
                in_list = True
                list_type = "ol"
            elif list_type != "ol":
                flush_list()
                in_list = True
                list_type = "ol"
            list_buffer.append(inline_md(ol_match.group(1)))
            i += 1
            continue

        # Regular paragraph
        flush_list()
        flush_table()
        content = inline_md(line)
        # Check if next line continues the paragraph
        para_lines = [content]
        while i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip().startswith(('#', '>', '|', '```', '-', '*', '+', '1.')):
            i += 1
            if re.match(r'^\d+\.\s+', lines[i]):
                break
            if re.match(r'^[\s]*[-*+]\s+', lines[i]):
                break
            if lines[i].strip():
                para_lines.append(inline_md(lines[i]))
            else:
                break
        if para_lines:
            html.append(f"<p>{' '.join(para_lines)}</p>")
        i += 1

    if in_code_block:
        code = "\n".join(code_buffer)
        html.append(f'<pre><code>{escape_html(code)}</code></pre>')
    if in_list:
        flush_list()
    if in_table:
        flush_table()

    return "\n".join(html)


def inline_md(text):
    """Process inline markdown: bold, italic, code, links, images."""
    # Images ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy">', text)
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Bold **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    # Italic *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    # Inline code `text`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def escape_html(text):
    """Escape HTML special characters."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


# ─── Frontmatter Parser ───────────────────────────────────────

def parse_frontmatter(text):
    """Parse YAML-style frontmatter between --- markers.
    Handles multi-line values enclosed in single or double quotes."""
    metadata = {}
    content = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            content = parts[2].strip()

            lines = frontmatter.split("\n")
            current_key = None
            current_value = []
            in_multiline = False
            quote_char = None

            for line in lines:
                stripped = line.strip()

                if in_multiline:
                    current_value.append(line)
                    # Check if closing quote found
                    if quote_char and stripped.endswith(quote_char):
                        full_value = "\n".join(current_value)
                        # Remove the outer quotes
                        full_value = full_value.strip()
                        if full_value.startswith(quote_char) and full_value.endswith(quote_char):
                            full_value = full_value[len(quote_char):-len(quote_char)]
                        metadata[current_key] = full_value.strip()
                        in_multiline = False
                        current_key = None
                        current_value = []
                        quote_char = None
                    continue

                if ":" in stripped and current_key is None:
                    key, value = stripped.split(":", 1)
                    current_key = key.strip()
                    value = value.strip()

                    # Check if value starts a multi-line quote block
                    if value and value[0] in ("'", '"'):
                        quote_char = value[0]
                        # Check if it ends on the same line
                        if value.endswith(quote_char) and len(value) > 1:
                            metadata[current_key] = value.strip(quote_char)
                            current_key = None
                        else:
                            in_multiline = True
                            current_value = [value]
                    else:
                        metadata[current_key] = value
                        current_key = None

    return metadata, content


# ─── Template Engine ──────────────────────────────────────────

def render_template(template_name, **kwargs):
    """Simple {{ variable }} replacement template engine."""
    path = TEMPLATES_DIR / template_name
    template = path.read_text(encoding="utf-8")

    def replace_var(match):
        key = match.group(1).strip()
        return str(kwargs.get(key, ""))

    result = re.sub(r'\{\{\s*(\w+)\s*\}\}', replace_var, template)
    return result


# ─── Build Functions ──────────────────────────────────────────

def build_post(md_path):
    """Convert a markdown file to a full HTML post page."""
    text = md_path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text)

    title = metadata.get("title", md_path.stem.replace("-", " ").title())
    date = metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
    slug = metadata.get("slug", md_path.stem)
    description = metadata.get("description", SITE_DESCRIPTION)
    categories_raw = metadata.get("categories", "")
    categories = [c.strip() for c in categories_raw.split(",") if c.strip()]
    categories_html = "".join(
        f'<span class="category-tag">{escape_html(cat)}</span>' for cat in categories
    ) if categories else ""
    schema_json = metadata.get("schema", "")

    content_html = md_to_html(body)

    # Format date for display
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        date_display = dt.strftime("%B %d, %Y")
    except ValueError:
        date_display = date

    # Article meta (date + categories)
    article_meta = f"""
    <div class="article-meta">
        <time class="article-meta__date" datetime="{date}">{date_display}</time>
        {categories_html}
    </div>"""

    content_html = article_meta + "\n" + content_html

    # Article schema if not provided
    if not schema_json:
        schema_json = f"""{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{title}",
  "datePublished": "{date}",
  "description": "{description}",
  "author": {{
    "@type": "Person",
    "name": "{AUTHOR}"
  }}
}}"""

    full_html = render_template(
        "base.html",
        title=f"{title} | {SITE_TITLE}",
        site_title=SITE_TITLE,
        description=description,
        content=content_html,
        schema=schema_json,
        year=datetime.now().strftime("%Y"),
        date=date_display,
        page_title=title,
        canonical_url=f"{SITE_URL}/posts/{slug}.html",
        categories_html=categories_html,
        categories_list=",".join(categories)
    )

    return full_html, slug, title, date, description, categories


def build_index(posts):
    """Build the homepage listing all posts."""
    posts_html = ""
    for title, slug, date, description, categories in posts:
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            date_fmt = dt.strftime("%b %d, %Y")
        except ValueError:
            date_fmt = date
        categories_tag_html = ""
        if categories:
            for cat in categories:
                categories_tag_html += f'<span class="category-tag">{escape_html(cat)}</span>'

        posts_html += f"""
        <article class="post-card">
            <div class="post-card__meta">
                <time class="post-card__date">{date_fmt}</time>
                {categories_tag_html}
            </div>
            <h2 class="post-card__title"><a href="posts/{slug}.html">{escape_html(title)}</a></h2>
            <p class="post-card__excerpt">{escape_html(description)}</p>
            <a class="post-card__link" href="posts/{slug}.html">Read More →</a>
        </article>"""

    homepage = render_template(
        "base.html",
        title=SITE_TITLE,
        site_title=SITE_TITLE,
        description=SITE_DESCRIPTION,
        content=f"""
        <section class="hero">
            <div class="hero__content">
                <h1>{SITE_TITLE}</h1>
                <p>{SITE_DESCRIPTION}</p>
            </div>
        </section>
        <section class="posts-list">
            <h2 class="section-title">Latest Guides</h2>
            {posts_html}
        </section>
        """,
        schema="",
        year=datetime.now().strftime("%Y"),
        date="",
        page_title="Home",
        canonical_url=SITE_URL
    )

    (OUTPUT_DIR / "index.html").write_text(homepage, encoding="utf-8")


def copy_static():
    """Copy static assets to output."""
    if STATIC_DIR.exists():
        for item in STATIC_DIR.rglob("*"):
            if item.is_file():
                dest = OUTPUT_DIR / item.relative_to(STATIC_DIR)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)


def main():
    print("🏋️  Building Gym Nutrition Blog...\n")

    # Clean output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    # Copy static files
    copy_static()

    # Find and build all posts
    md_files = sorted(CONTENT_DIR.rglob("*.md"))
    if not md_files:
        print("⚠️  No markdown files found in content/")
        return

    posts_dir = OUTPUT_DIR / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    post_metadata = []
    for md_path in md_files:
        print(f"  📝 {md_path.relative_to(CONTENT_DIR)}")
        html, slug, title, date, description, categories = build_post(md_path)
        (posts_dir / f"{slug}.html").write_text(html, encoding="utf-8")
        post_metadata.append((title, slug, date, description, categories))

    # Build index
    post_metadata.sort(key=lambda p: p[2], reverse=True)  # Sort by date desc
    build_index(post_metadata)

    print(f"\n✅  Built {len(md_files)} posts → {OUTPUT_DIR}/")
    print(f"🌐  Open _site/index.html in your browser to preview.\n")


if __name__ == "__main__":
    main()
