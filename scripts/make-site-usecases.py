#!/usr/bin/env python3
#
# Usage:
# $ scripts/make-site-usecases.py
#
# Writes the use case pages of the website (docs/usecases/*/index.html) from
# the Markdown files in usecases/. The titles and lead texts of the pages are
# defined below; the sentences, sources and notes come from the Markdown files.
#

import html
import os
import re
import sys
import urllib.parse

REPO = 'https://github.com/tkuhn/aida/blob/master/'
PREFIX = 'http://purl.org/aida/'

# Page title and lead text of each use case, in the order they are listed.
# The landing page (docs/index.html) uses the same texts.
USECASES = {
    'alzheimers': (
        'A Cochrane review on Alzheimer’s disease',
        'The conclusions and outcomes of one review article, restated as AIDA sentences.',
    ),
    'openaccess': (
        'The Open Access citation advantage',
        'Publications that claim, investigate or refute one sentence and its field-specific variants.',
    ),
    'famous-cs': (
        'Insights from famous computer scientists',
        'Landmark results from Babbage to Turing, each written as one sentence. Work in progress.',
    ),
}

# Explanations shown under section headings of the Markdown files.
SECTION_INTROS = {
    'Summarized Outcomes': 'Each sentence summarizes the outcomes with the given numbers, which are listed below.',
}

# List item of the form: - relation. label: "sentence"
# where the relation and the label are optional.
ITEM = re.compile(r'(?:([A-Za-z]+)\. )?(?:([^"]+?): )?"(.+)"')


def esc(text):
    return html.escape(text)


def encode(sentence):
    # Same encoding as scripts/make-aida-uri.sh.
    return urllib.parse.quote(sentence, safe='-_.~').replace('%20', '+')


def sentence_link(sentence, text=None):
    return f'<a class="sentence-link" href="../../s/?{esc(encode(sentence))}">{text or esc(sentence)}</a>'


def uri_html(sentence):
    # Let long URIs wrap after a "+".
    return esc(PREFIX + encode(sentence)).replace('+', '+<wbr>')


def source_label(source):
    m = re.fullmatch(r'https?://(?:dx\.)?doi\.org/(.+)', source)
    if m:
        return 'doi:' + m[1]
    return re.sub(r'^https?://(?:www\.)?', '', source)


def autolink(text):
    return re.sub(r'https?://[^\s<]+', lambda m: f'<a href="{m[0]}">{m[0]}</a>', esc(text))


def sentence_case(title):
    return title[:1] + title[1:].lower()


def placeholder(template):
    # The placeholder of a template sentence is its word in capitals,
    # such as QUALIFICATION or ADVERSE-EVENT.
    return re.search(r'[A-Z]{3,}(?:-[A-Z]{3,})*', template)[0]


def template_html(template):
    name = placeholder(template)
    before, after = template.split(name)
    slot = name.lower().replace('-', ' ')
    return f'{esc(before)}<span class="slot">{esc(slot)}</span>{esc(after)}'


def template_value(template, sentence):
    # The value that a sentence puts in the placeholder of the template, for
    # sentences written out in full and for abbreviated ones of the form
    # "... adverse event of nausea ...". None if the template does not apply.
    before, after = template.split(placeholder(template))
    m = re.fullmatch(re.escape(before) + '(.+)' + re.escape(after), sentence)
    if m:
        return m[1]
    m = re.fullmatch(r'\.\.\. (.+) \.\.\.', sentence)
    if m:
        words = before.split()
        for n in range(len(words), 0, -1):
            context = ' '.join(words[-n:]) + ' '
            if m[1].startswith(context):
                return m[1][len(context):]
    return None


def blocks(slug):
    # The Markdown file as a list of (kind, text) with the kinds h1 to h6,
    # item and para.
    with open(f'usecases/{slug}.md', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f] + ['']
    out = []
    para = []

    def flush():
        if para:
            out.append(('para', ' '.join(para)))
            para.clear()

    i = 0
    while i < len(lines) - 1:
        line, underline = lines[i], lines[i + 1]
        atx = re.fullmatch(r'(#{1,6}) (.+)', line)
        if not line:
            flush()
        elif re.fullmatch(r'={3,}', underline):
            flush()
            out.append(('h1', line))
            i += 1
        elif re.fullmatch(r'-{3,}', underline):
            flush()
            out.append(('h2', line))
            i += 1
        elif atx:
            flush()
            out.append((f'h{len(atx[1])}', atx[2]))
        elif line.startswith('- '):
            flush()
            out.append(('item', line[2:]))
        else:
            para.append(line.strip())
        i += 1
    flush()
    return out


def key_html(label):
    # '10 (subsumes 11)' becomes the key 10 with a note, '6-8' becomes 6–8.
    def nice(text):
        return re.sub(r',\s*', ', ', text).replace('-', '–')
    m = re.fullmatch(r'([^()]+?)(?: \((.+)\))?', label or '')
    if not m:
        return '<span class="key"></span>'
    note = f'<small>{esc(nice(m[2]))}</small>' if m[2] else ''
    return f'<span class="key">{esc(nice(m[1]))}{note}</span>'


def alzheimers():
    articles = []
    article = section = group = None
    for kind, text in blocks('alzheimers'):
        if kind == 'h2':
            article = {'title': text, 'citation': '', 'template': None, 'sections': []}
            articles.append(article)
            section = group = None
        elif kind == 'h3':
            section = {'title': text, 'groups': []}
            article['sections'].append(section)
            group = None
        elif kind == 'para' and article and section is None:
            article['citation'] = text
        elif kind == 'para' and section and text.endswith(':'):
            group = {'title': text[:-1], 'items': []}
            section['groups'].append(group)
        elif kind == 'item' and section:
            m = ITEM.fullmatch(text)
            relation, label, sentence = m.groups()
            if relation == 'TEMPLATE':
                # The paragraph before the template is its description.
                article['template'] = (group['title'], sentence)
                section['groups'].remove(group)
                group = None
                continue
            if group is None:
                group = {'title': None, 'items': []}
                section['groups'].append(group)
            group['items'].append((label, sentence))
        # Other paragraphs ("...") stand for content that is still to come.

    out = []
    count = 0
    for article in articles:
        citation = re.sub(
            r'DOI: (10\.\S+?)(\.?)$',
            lambda m: f'DOI: <a href="https://doi.org/{m[1]}">{m[1]}</a>{m[2]}',
            esc(article['citation']))
        out.append(f'''
  <section class="band compact">
    <div class="wrap">
      <h2 class="eyebrow">{esc(article['title'])}</h2>
      <p class="citation">{citation}</p>
    </div>
  </section>''')
        intro, template = article['template'] or (None, None)
        for section in article['sections']:
            out.append(f'''
  <section class="wrap block">
    <h2>{esc(sentence_case(section['title']))}</h2>''')
            if section['title'] in SECTION_INTROS:
                out.append(f'    <p class="block-intro">{esc(SECTION_INTROS[section["title"]])}</p>')
            for group in section['groups']:
                rows, chips = [], []
                for label, sentence in group['items']:
                    value = template_value(template, sentence) if template else None
                    if value is None:
                        rows.append((label, sentence))
                    else:
                        chips.append((label, value, template.replace(placeholder(template), value)))
                count += len(rows) + len(chips)
                out.append('    <div class="group">')
                if group['title']:
                    out.append(f'      <h3>{esc(group["title"])}</h3>')
                if rows:
                    keyed = any(label for label, _ in rows)
                    out.append(f'      <ul class="{"rows" if keyed else "rows large"}">')
                    for label, sentence in rows:
                        key = key_html(label) if keyed else ''
                        out.append(f'        <li>{key}<p class="statement">{sentence_link(sentence)}</p></li>')
                    out.append('      </ul>')
                if chips:
                    out.append(f'''      <div class="pattern">
        <p class="eyebrow">{esc(intro)}</p>
        <p>{template_html(template)}</p>
      </div>
      <ul class="chips">''')
                    for label, value, sentence in chips:
                        num = f'<span class="num">{esc(label)}</span>' if label else ''
                        out.append(f'        <li>{sentence_link(sentence, num + esc(value))}</li>')
                    out.append('      </ul>')
                out.append('    </div>')
            out.append('  </section>')
    return '\n'.join(out), count


def openaccess():
    relations = {
        'claims': ('claims it', 'claim it', ''),
        'investigates': ('investigates it', 'investigate it',
                         'Without conclusive results in either direction.'),
        'refutes': ('refutes it', 'refute it',
                    'They find more citations for publications that are not Open Access.'),
    }
    general = template = None
    publications = {}
    source, notes = [], []
    heading = None
    for kind, text in blocks('openaccess'):
        if kind == 'h2':
            heading = text
        elif kind == 'para' and heading == 'Source':
            source.append(text)
        elif kind == 'item' and heading == 'Notes':
            notes.append(text)
        elif kind == 'item':
            m = ITEM.fullmatch(text)
            if m and m[1] == 'GENERAL':
                general = m[3]
            elif m and m[1] == 'TEMPLATE':
                template = m[3]
            else:
                relation, url, qualification = re.fullmatch(r'([a-z]+)\. (\S+)(?: "(.+)")?', text).groups()
                publications.setdefault(relation, []).append((url, qualification))

    out = [f'''
  <section class="band">
    <div class="wrap">
      <div class="example">
        <h2 class="eyebrow">The general sentence</h2>
        <p class="example-sentence long">{sentence_link(general)}</p>
        <p class="uri">{uri_html(general)}</p>
      </div>
      <div class="pattern">
        <h2 class="eyebrow">Pattern for more specific sentences</h2>
        <p>{template_html(template)}</p>
      </div>
    </div>
  </section>''']
    count = 0
    for relation, items in publications.items():
        one, many, note = relations.get(relation, (relation, relation, ''))
        count += len(items)
        out.append(f'''
  <section class="wrap block">
    <h2 class="counted"><span class="count">{len(items)}</span>{one if len(items) == 1 else many}</h2>''')
        if note:
            out.append(f'    <p class="block-intro">{esc(note)}</p>')
        out.append('    <ul class="pubs">')
        for url, qualification in items:
            if qualification:
                link = sentence_link(template.replace(placeholder(template), qualification), esc(qualification))
            else:
                link = sentence_link(general, 'in general')
            out.append(f'      <li>{link}<a class="source" href="{esc(url)}">{esc(source_label(url))}</a></li>')
        out.append('    </ul>\n  </section>')
    out.append('''
  <section class="wrap block notes">
    <h2>Source</h2>''')
    out.extend(f'    <p>{autolink(text)}</p>' for text in source)
    if notes:
        out.append('    <h2>Notes</h2>\n    <ul>')
        out.extend(f'      <li>{autolink(text)}</li>' for text in notes)
        out.append('    </ul>')
    out.append('  </section>')
    return '\n'.join(out), count


def famous_cs():
    people = []
    for kind, text in blocks('famous-cs'):
        if kind == 'h4':
            name, years = re.fullmatch(r'(.+?)(?: \((.+)\))?', text).groups()
            people.append({'name': name, 'years': years, 'items': []})
        elif kind == 'item' and people:
            # An item can start with a note such as _(with Peter Naur)_.
            people[-1]['items'].append(re.fullmatch(r'(?:_\((.+?)\)_ )?(.+)', text).groups())

    out = ['''
  <section class="wrap block">
    <ul class="rows people">''']
    count = 0
    for person in people:
        years = person['years'] or ''
        years = re.sub(r'^(\d+)-\*$', r'born \1', years).replace('-', '–')
        out.append(f'''      <li>
        <div class="key">
          <h2 class="person">{esc(person['name'])}</h2>''')
        if years:
            out.append(f'          <span class="years">{esc(years)}</span>')
        out.append('        </div>\n        <ul class="statements">')
        for note, sentence in person['items']:
            note = f'<span class="note">{esc(note)}</span>' if note else ''
            out.append(f'          <li>{sentence_link(sentence)}{note}</li>')
            count += 1
        out.append('        </ul>\n      </li>')
    out.append('    </ul>\n  </section>')
    return '\n'.join(out), count


def page(slug, body):
    title, lead = USECASES[slug]
    others = '\n'.join(f'''      <div class="column">
        <h3>{esc(other_title)}</h3>
        <p>{esc(other_lead)}</p>
        <a class="more" href="../{other}/">Open the use case →</a>
      </div>''' for other, (other_title, other_lead) in USECASES.items() if other != slug)
    return f'''<!doctype html>
<!-- Generated by scripts/make-site-usecases.py from usecases/{slug}.md. Do not edit by hand. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · AIDA</title>
<meta name="description" content="{esc(lead)}">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;700&family=Space+Mono:wght@400;700&display=swap">
<link rel="stylesheet" href="../../style.css">
</head>
<body>

<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="wrap">
    <a class="wordmark" href="../../">AIDA</a>
    <nav class="site-nav" aria-label="Main">
      <a href="../../">What is AIDA?</a>
      <a href="../../#use">Use cases</a>
      <a href="https://github.com/tkuhn/aida">GitHub</a>
    </nav>
  </div>
</header>

<main id="main">

  <section class="page-head">
    <div class="wrap usecase-head">
      <p class="eyebrow">Use case</p>
      <h1 class="display">{esc(title)}</h1>
      <p class="lead">{esc(lead)} Each sentence links to its own page.</p>
    </div>
  </section>
{body}

  <section class="wrap section">
    <h2>More use cases</h2>
    <div class="columns">
{others}
    </div>
    <p class="generated">This page is generated from <a href="{REPO}usecases/{slug}.md">usecases/{slug}.md</a> in the AIDA repository.</p>
  </section>

</main>

<footer class="site-footer">
  <div class="wrap">
    <span>Atomic. Independent. Declarative. Absolute.</span>
    <a href="https://github.com/tkuhn/aida">github.com/tkuhn/aida</a>
  </div>
</footer>

</body>
</html>
'''


for slug, render in (('alzheimers', alzheimers), ('openaccess', openaccess), ('famous-cs', famous_cs)):
    body, count = render()
    os.makedirs(f'docs/usecases/{slug}', exist_ok=True)
    with open(f'docs/usecases/{slug}/index.html', 'w', encoding='utf-8') as f:
        f.write(page(slug, body))
    print(f'docs/usecases/{slug}/index.html: {count} sentence links', file=sys.stderr)
