#!/usr/bin/env python3
"""Gym Nutrition Blog — Static Site Generator
Zero dependencies, pure Python 3 standard library.
Converts markdown to HTML, applies templates, outputs to _site/

New in v2: RSS feed, XML sitemap, category archives, standalone pages,
custom 404 page, and dynamic navigation from post categories.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ─── Configuration ────────────────────────────────────────────
CONTENT_DIR = Path("content")
TEMPLATES_DIR = Path("templates")
STATIC_DIR = Path("static")
OUTPUT_DIR = Path("_site")

SITE_TITLE = "GymPlatePrep"
SITE_DESCRIPTION = "Science-backed gym nutrition guides, meal prep recipes, and diet plans for muscle gain and fat loss."
SITE_URL = "https://gymplateprep.pages.dev"
AUTHOR = "GymPlatePrep"


# ─── Simple Markdown → HTML Converter ─────────────────────────

def md_to_html(text: str) -> tuple:
    """Convert markdown text to HTML using only stdlib.

    Returns (html_string, headings_list) where headings_list contains
    (level, text, id) tuples for h2+ headings (used for ToC generation).
    """
    lines = text.split("\n")
    html = []
    headings = []  # (level, text, id) for h2+
    used_ids = set()
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
            content_raw = heading_match.group(2)
            content = inline_md(content_raw)
            # Add anchor ID (deduplicated) and track h2+ for ToC
            heading_id = slugify(content_raw)
            unique_id = heading_id
            counter = 2
            while unique_id in used_ids:
                unique_id = f"{heading_id}-{counter}"
                counter += 1
            used_ids.add(unique_id)
            if level >= 2:
                headings.append((level, content, unique_id))
            html.append(f'<h{level} id="{unique_id}">{content}</h{level}>')
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

        # Raw HTML passthrough (for interactive pages like calculators)
        stripped = line.strip()
        if stripped.startswith('<') and not stripped.startswith('</'):
            flush_list()
            flush_table()
            raw_lines = [line]
            # <script> blocks: collect everything until </script>
            if stripped.startswith('<script'):
                while i + 1 < len(lines):
                    i += 1
                    raw_lines.append(lines[i])
                    if lines[i].strip().startswith('</script>'):
                        break
            # <style> blocks: collect everything until </style>
            elif stripped.startswith('<style'):
                while i + 1 < len(lines):
                    i += 1
                    raw_lines.append(lines[i])
                    if lines[i].strip().startswith('</style>'):
                        break
            # Other block-level HTML tags: collect consecutive lines
            else:
                while i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('<') and not next_line.startswith('</') or next_line == '':
                        i += 1
                        raw_lines.append(lines[i])
                    else:
                        break
            html.append("\n".join(raw_lines))
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

    return "\n".join(html), headings


def inline_md(text: str) -> str:
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


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def slugify(text: str) -> str:
    """Convert text to URL-safe HTML ID."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    slug = slug.strip('-')
    return slug or "heading"


# ─── Frontmatter Parser ───────────────────────────────────────

def parse_frontmatter(text: str) -> tuple:
    """Parse YAML-style frontmatter between --- markers.

    Returns (metadata_dict, body_string).
    Handles multi-line values enclosed in single or double quotes.
    """
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

def render_template(template_name: str, **kwargs) -> str:
    """Simple {{ variable }} replacement template engine."""
    path = TEMPLATES_DIR / template_name
    template = path.read_text(encoding="utf-8")

    def replace_var(match):
        key = match.group(1).strip()
        return str(kwargs.get(key, ""))

    result = re.sub(r'\{\{\s*(\w+)\s*\}\}', replace_var, template)
    return result


# ─── Navigation ───────────────────────────────────────────────

def build_nav_links(posts_metadata: list) -> str:
    """Generate navigation links HTML from all post categories."""
    cats = set()
    for _, _, _, _, categories, _ in posts_metadata:
        for cat in categories:
            cats.add(cat)

    links = ['<a href="/">Home</a>']
    for cat in sorted(cats):
        slug = cat.lower().replace(" ", "-")
        links.append(f'<a href="/categories/{slug}/">{escape_html(cat)}</a>')
    links.append('<a href="/macro-calculator">Macro Calculator</a>')
    links.append('<a href="/about">About</a>')

    return "\n                ".join(links)


# ─── Build Functions ──────────────────────────────────────────

def generate_toc(headings: list) -> str:
    """Generate table of contents HTML from headings list.

    Only renders when there are 2+ headings (meaningful navigation).
    """
    if len(headings) < 2:
        return ""

    items = []
    for level, text, heading_id in headings:
        cls = "toc__item toc__item--h2" if level == 2 else "toc__item toc__item--h3"
        items.append(f'          <li class="{cls}"><a href="#{heading_id}">{text}</a></li>')

    return f"""
    <nav class="toc" aria-label="Table of Contents">
        <h2 class="toc__title">On This Page</h2>
        <ul class="toc__list">
{chr(10).join(items)}
        </ul>
    </nav>"""


def find_related(current_slug: str, current_categories: list,
                 post_metadata: list, max_results: int = 3) -> list:
    """Find related posts by shared categories, excluding the current post."""
    scored = []
    for title, slug, date, description, categories, feat_img in post_metadata:
        if slug == current_slug:
            continue
        shared = len(set(current_categories) & set(categories))
        if shared > 0:
            scored.append((shared, title, slug, description, feat_img))

    scored.sort(key=lambda x: -x[0])
    return [(t, s, d, f) for _, t, s, d, f in scored[:max_results]]


def render_related(related: list) -> str:
    """Generate related posts HTML section."""
    if not related:
        return ""

    items = []
    for title, slug, description, featured_image in related:
        thumb = (f'<img class="related-card__thumb" src="{featured_image}"'
                 f' alt="" loading="lazy" />') if featured_image else ""
        items.append(f"""
        <article class="related-card">
            {thumb}
            <div class="related-card__body">
                <h3 class="related-card__title"><a href="/posts/{slug}">{escape_html(title)}</a></h3>
                <p class="related-card__excerpt">{escape_html(description)}</p>
                <a class="related-card__link" href="/posts/{slug}">Read More →</a>
            </div>
        </article>""")

    return f"""
    <section class="related-posts">
        <h2 class="section-title">Related Guides</h2>
        <div class="related-posts__grid">
            {''.join(items)}
        </div>
    </section>"""


def render_email_capture() -> str:
    """Generate email capture form HTML."""
    return f"""
    <section class="email-capture">
        <div class="email-capture__content">
            <h2 class="email-capture__title">Free 7-Day Meal Prep Starter Kit</h2>
            <p class="email-capture__text">Get a printable meal plan, shopping list, and calorie calculator delivered to your inbox. Start your transformation today.</p>
            <form class="email-capture__form" id="email-capture-form">
                <div class="email-capture__fields">
                    <input class="email-capture__input" id="email-input" type="email" name="email" placeholder="Your email address" required>
                    <button class="email-capture__btn" id="email-submit-btn" type="submit">Get the Kit</button>
                </div>
                <p class="email-capture__msg" id="email-msg"></p>
            </form>
        </div>
    </section>"""


def build_post(md_path: Path, nav_links: str, post_metadata: list = None) -> tuple:
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
    featured_image = metadata.get("featured_image", "")

    content_html, headings = md_to_html(body)
    toc_html = generate_toc(headings)

    # Format date for display
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        date_display = dt.strftime("%B %d, %Y")
    except ValueError:
        date_display = date

    # Article hero with featured image or gradient fallback
    article_meta_html = f"""
        <div class="article-meta">
            <time class="article-meta__date" datetime="{date}">{date_display}</time>
            {categories_html}
        </div>"""

    if featured_image:
        article_hero = f"""
    <section class="article-hero article-hero--with-image" style="background-image: url({featured_image})">
        <div class="article-hero__overlay"></div>
        <div class="article-hero__content">
            <h1>{title}</h1>
            {article_meta_html}
        </div>
    </section>"""
    else:
        article_hero = f"""
    <section class="article-hero article-hero--gradient">
        <div class="article-hero__content">
            <h1>{title}</h1>
            {article_meta_html}
        </div>
    </section>"""

    email_capture_html = render_email_capture()

    related_html = ""
    if post_metadata:
        related = find_related(slug, categories, post_metadata)
        related_html = render_related(related)

    calc_promo = """
    <div class="calc-promo">
        <p><strong>🎯 Know your numbers?</strong> Get your personalized daily macros — <a href="/macro-calculator">try the free Macro Calculator →</a></p>
    </div>"""

    content_html = article_hero + "\n" + f"""
    <article>
        {toc_html}
        {content_html}
    </article>
    {email_capture_html}
    {calc_promo}
    {related_html}"""

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
        canonical_url=f"{SITE_URL}/posts/{slug}",
        categories_html=categories_html,
        categories_list=",".join(categories),
        nav_links=nav_links
    )

    return full_html, slug, title, date, description, categories, featured_image


def build_index(posts_metadata: list, nav_links: str) -> None:
    """Build the homepage listing all posts."""
    posts_html = ""
    for title, slug, date, description, categories, featured_image in posts_metadata:
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            date_fmt = dt.strftime("%b %d, %Y")
        except ValueError:
            date_fmt = date
        categories_tag_html = ""
        if categories:
            for cat in categories:
                categories_tag_html += f'<span class="category-tag">{escape_html(cat)}</span>'

        thumb_html = ""
        card_class = "post-card"
        if featured_image:
            thumb_html = f'<img class="post-card__thumb" src="{featured_image}" alt="" loading="lazy" />'
            card_class = "post-card post-card--has-image"

        posts_html += f"""
        <article class="{card_class}">
            {thumb_html}
            <div class="post-card__body">
                <div class="post-card__meta">
                    <time class="post-card__date">{date_fmt}</time>
                    {categories_tag_html}
                </div>
                <h2 class="post-card__title"><a href="posts/{slug}">{escape_html(title)}</a></h2>
                <p class="post-card__excerpt">{escape_html(description)}</p>
                <a class="post-card__link" href="posts/{slug}">Read More →</a>
            </div>
        </article>"""

    homepage = render_template(
        "base.html",
        title=SITE_TITLE,
        site_title=SITE_TITLE,
        description=SITE_DESCRIPTION,
        content=f"""
        <section class="hero hero--with-image" style="background-image: url(/images/hero-gym.jpg)">
            <div class="hero__overlay"></div>
            <div class="hero__content">
                <div class="brand-hero">
                    <div class="brand-hero__icon">
                        <svg viewBox="0 0 100 100" width="80" height="80" fill="none" stroke="#f97316" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="20" y="35" width="60" height="30" rx="6" />
                            <rect x="10" y="42" width="10" height="16" rx="3" />
                            <rect x="80" y="42" width="10" height="16" rx="3" />
                            <rect x="28" y="28" width="8" height="44" rx="3" />
                            <rect x="64" y="28" width="8" height="44" rx="3" />
                            <line x1="36" y1="32" x2="36" y2="68" stroke-width="2" opacity="0.4" />
                            <line x1="44" y1="28" x2="44" y2="72" stroke-width="2" opacity="0.4" />
                            <line x1="52" y1="28" x2="52" y2="72" stroke-width="2" opacity="0.4" />
                            <line x1="60" y1="32" x2="60" y2="68" stroke-width="2" opacity="0.4" />
                        </svg>
                    </div>
                    <h1 class="brand-hero__title">{SITE_TITLE}</h1>
                    <p class="brand-hero__tagline">{SITE_DESCRIPTION}</p>
                    <div class="brand-hero__cta">
                        <a href="/posts/complete-guide-gym-nutrition-muscle-gain" class="brand-hero__btn">Start Here →</a>
                        <a href="/macro-calculator" class="brand-hero__btn brand-hero__btn--secondary">Try the Calculator</a>
                    </div>
                </div>
            </div>
        </section>
        <section class="promo-banner">
            <div class="promo-banner__content">
                <h2>🔢 Find Your Perfect Macros</h2>
                <p>Not sure how much protein, carbs, or fat you actually need? Use our <strong>free Macro Calculator</strong> — get personalized daily targets based on your body, activity, and goals in seconds.</p>
                <a href="/macro-calculator" class="promo-banner__btn">Calculate My Macros →</a>
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
        canonical_url=SITE_URL,
        nav_links=nav_links
    )

    (OUTPUT_DIR / "index.html").write_text(homepage, encoding="utf-8")


def build_rss(posts_metadata: list) -> None:
    """Generate RSS 2.0 feed at _site/rss.xml."""
    def rfc2822(date_str: str) -> str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        except ValueError:
            return date_str

    items = []
    for title, slug, date, description, categories, _ in posts_metadata:
        items.append(f"""    <item>
      <title>{escape_html(title)}</title>
      <link>{SITE_URL}/posts/{slug}</link>
      <description>{escape_html(description)}</description>
      <pubDate>{rfc2822(date)}</pubDate>
      <guid isPermaLink="true">{SITE_URL}/posts/{slug}</guid>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE_TITLE}</title>
    <link>{SITE_URL}</link>
    <description>{SITE_DESCRIPTION}</description>
    <language>en-us</language>
    <lastBuildDate>{rfc2822(datetime.now().strftime("%Y-%m-%d"))}</lastBuildDate>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>"""

    (OUTPUT_DIR / "rss.xml").write_text(rss.strip(), encoding="utf-8")
    print(f"  📡 rss.xml")


def build_sitemap(posts_metadata: list) -> None:
    """Generate XML sitemap at _site/sitemap.xml."""
    urls = [f"""  <url>
    <loc>{SITE_URL}/</loc>
    <priority>1.0</priority>
    <changefreq>weekly</changefreq>
  </url>"""]

    for title, slug, date, description, categories, _ in posts_metadata:
        urls.append(f"""  <url>
    <loc>{SITE_URL}/posts/{slug}</loc>
    <lastmod>{date}</lastmod>
    <priority>0.8</priority>
    <changefreq>monthly</changefreq>
  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap.strip(), encoding="utf-8")
    print(f"  🗺️  sitemap.xml")


def build_category_pages(posts_metadata: list, nav_links: str) -> None:
    """Generate category archive pages at _site/categories/{slug}/index.html."""
    categories = defaultdict(list)
    for title, slug, date, description, categories_list, featured_image in posts_metadata:
        for cat in categories_list:
            categories[cat].append((title, slug, date, description, categories_list, featured_image))

    for category, cat_posts in categories.items():
        posts_html = ""
        for title, slug, date, description, cats, featured_image in cat_posts:
            try:
                dt = datetime.strptime(date, "%Y-%m-%d")
                date_fmt = dt.strftime("%b %d, %Y")
            except ValueError:
                date_fmt = date

            categories_tag_html = ""
            if cats:
                for cat in cats:
                    categories_tag_html += f'<span class="category-tag">{escape_html(cat)}</span>'

            thumb_html = ""
            card_class = "post-card"
            if featured_image:
                thumb_html = f'<img class="post-card__thumb" src="{featured_image}" alt="" loading="lazy" />'
                card_class = "post-card post-card--has-image"

            posts_html += f"""
        <article class="{card_class}">
            {thumb_html}
            <div class="post-card__body">
                <div class="post-card__meta">
                    <time class="post-card__date">{date_fmt}</time>
                    {categories_tag_html}
                </div>
                <h2 class="post-card__title"><a href="/posts/{slug}">{escape_html(title)}</a></h2>
                <p class="post-card__excerpt">{escape_html(description)}</p>
                <a class="post-card__link" href="/posts/{slug}">Read More →</a>
            </div>
        </article>"""

        cat_slug = category.lower().replace(" ", "-")

        page = render_template(
            "base.html",
            title=f"{category} | {SITE_TITLE}",
            site_title=SITE_TITLE,
            description=f"Articles about {category.lower()} — {SITE_DESCRIPTION}",
            content=f"""
        <section class="category-header">
            <h1>{escape_html(category)}</h1>
            <p>All articles about {category.lower()}.</p>
        </section>
        <section class="posts-list">
            {posts_html}
        </section>
            """,
            schema="",
            year=datetime.now().strftime("%Y"),
            date="",
            page_title=category,
            canonical_url=f"{SITE_URL}/categories/{cat_slug}/",
            nav_links=nav_links
        )

        cat_dir = OUTPUT_DIR / "categories" / cat_slug
        cat_dir.mkdir(parents=True, exist_ok=True)
        (cat_dir / "index.html").write_text(page, encoding="utf-8")
        print(f"  📂 categories/{cat_slug}/")


def build_pages(nav_links: str) -> None:
    """Build standalone pages from content/pages/ (about, contact, etc.)."""
    pages_dir = CONTENT_DIR / "pages"
    if not pages_dir.exists():
        return

    for md_path in sorted(pages_dir.rglob("*.md")):
        print(f"  📄 {md_path.relative_to(CONTENT_DIR)}")
        text = md_path.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(text)

        title = metadata.get("title", md_path.stem.replace("-", " ").title())
        description = metadata.get("description", SITE_DESCRIPTION)

        content_html, _ = md_to_html(body)

        full_html = render_template(
            "base.html",
            title=f"{title} | {SITE_TITLE}",
            site_title=SITE_TITLE,
            description=description,
            content=f"""
        <article>
            <h1>{title}</h1>
            {content_html}
        </article>
            """,
            schema="",
            year=datetime.now().strftime("%Y"),
            date="",
            page_title=title,
            canonical_url=f"{SITE_URL}/{md_path.stem}",
            nav_links=nav_links
        )

        (OUTPUT_DIR / f"{md_path.stem}.html").write_text(full_html, encoding="utf-8")


def build_404(nav_links: str, posts_metadata: list = None) -> None:
    """Build custom 404 page with links to recent posts."""
    recent_posts_html = ""
    if posts_metadata:
        recent = posts_metadata[:3]
        for title, slug, date, desc, cats, _ in recent:
            recent_posts_html += f"""
            <li><a href="/posts/{slug}">{escape_html(title)}</a></li>"""

    content = f"""
    <article class="error-page">
        <h1>404 — Page Not Found</h1>
        <p>Looks like this page took a rest day. The page you're looking for doesn't exist or has moved.</p>
        <p><a href="/">← Back to Home</a></p>
        {f'<h2>Try these popular guides:</h2><ul>{recent_posts_html}</ul>' if recent_posts_html else ''}
    </article>
    """

    html = render_template(
        "base.html",
        title=f"404 Not Found | {SITE_TITLE}",
        site_title=SITE_TITLE,
        description="Page not found. Browse our gym nutrition guides.",
        content=content,
        schema="",
        year=datetime.now().strftime("%Y"),
        date="",
        page_title="Page Not Found",
        canonical_url=SITE_URL,
        nav_links=nav_links
    )

    (OUTPUT_DIR / "404.html").write_text(html, encoding="utf-8")
    print(f"  🚫 404.html")


def copy_static() -> None:
    """Copy static assets to output."""
    if STATIC_DIR.exists():
        for item in STATIC_DIR.rglob("*"):
            if item.is_file():
                dest = OUTPUT_DIR / item.relative_to(STATIC_DIR)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)


def main() -> None:
    print("🏋️  Building Gym Nutrition Blog...\n")

    # Clean output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    # Copy static files
    copy_static()

    # Find pillar articles
    pillars_dir = CONTENT_DIR / "pillars"
    md_files = sorted(pillars_dir.rglob("*.md")) if pillars_dir.exists() else []

    if not md_files:
        print("⚠️  No markdown files found in content/pillars/")
        return

    # ── Pass 1: Parse frontmatter only (to build nav from categories) ──
    post_metadata = []
    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8")
        metadata, _ = parse_frontmatter(text)
        title = metadata.get("title", md_path.stem.replace("-", " ").title())
        date = metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
        slug = metadata.get("slug", md_path.stem)
        description = metadata.get("description", SITE_DESCRIPTION)
        categories_raw = metadata.get("categories", "")
        categories = [c.strip() for c in categories_raw.split(",") if c.strip()]
        featured_image = metadata.get("featured_image", "")
        post_metadata.append((title, slug, date, description, categories, featured_image))

    # Build nav links from all categories
    nav_links = build_nav_links(post_metadata)

    # ── Pass 2: Build full HTML with complete navigation ──
    posts_dir = OUTPUT_DIR / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    for md_path in md_files:
        print(f"  📝 {md_path.relative_to(CONTENT_DIR)}")
        html, slug, title, date, description, categories, featured_image = build_post(md_path, nav_links, post_metadata)
        (posts_dir / f"{slug}.html").write_text(html, encoding="utf-8")

    # Sort by date descending for index/rss/sitemap
    post_metadata.sort(key=lambda p: p[2], reverse=True)

    # Build everything
    build_index(post_metadata, nav_links)
    build_rss(post_metadata)
    build_sitemap(post_metadata)
    build_category_pages(post_metadata, nav_links)
    build_pages(nav_links)
    build_404(nav_links, post_metadata)

    print(f"\n✅  Built {len(md_files)} posts → {OUTPUT_DIR}/")
    print(f"🌐  Open _site/index.html in your browser to preview.\n")


if __name__ == "__main__":
    main()
