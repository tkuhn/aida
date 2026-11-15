#!/usr/bin/env python3
#
# Usage:
# $ scripts/make-site-datasets.py
#
# Writes the dataset pages of the website (docs/datasets/*/index.html) from
# the tables in tables/. The titles and texts of the pages are defined below;
# the sentences and sources come from the tables. Prints the number of
# sentences of each dataset, which the landing page (docs/index.html) shows.
#

import csv
import os
import sys

from sitepage import REPO, esc, page, sentence_link, source_label, source_link

PAPER_2013 = ('<a href="http://www.tkuhn.org/pub/kuhn2013eswc.pdf">'
              'Broadening the Scope of Nanopublications</a> (2013)')

# Each dataset in the order they are listed: its table, title and lead text
# (the landing page uses the same texts), what one source is called, and what
# is said about the table on the page (HTML).
DATASETS = {
    'papers': {
        'table': 'papers',
        'title': 'Claims from publications',
        'lead': 'Claims and hypotheses of publications, each restated as an AIDA sentence.',
        'source': ('source', 'sources'),
        'about': '',
    },
    'user-study': {
        'table': 'npuserstudy',
        'title': 'Sentences from a user study',
        'lead': 'Biomedical researchers rewrote the conclusions of five PubMed abstracts as AIDA sentences.',
        'source': ('abstract', 'abstracts'),
        'about': 'The distinct sentences that the participants of the user study wrote for each of '
                 f'the five abstracts. The study is described in {PAPER_2013}.',
    },
    'bot-study': {
        'table': 'npbotstudy',
        'title': 'Sentences extracted from GeneRIF',
        'lead': 'Sentences about the functions of genes and proteins, extracted automatically from the GeneRIF dataset.',
        'source': ('article', 'articles'),
        'about': 'Each sentence is linked to a PubMed article, an organism and a gene. '
                 f'The extraction is described in {PAPER_2013}.',
    },
    'core-claims': {
        'table': 'jansenstudy',
        'title': 'Core claims of articles',
        'lead': 'Core claims of scientific articles as AIDA sentences, one per article, from a study on extracting such claims.',
        'source': ('article', 'articles'),
        'about': '',
    },
}


def rows(table):
    with open(f'tables/{table}.csv', newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def grouped(items, key):
    # The items in groups by key, in the order the keys first appear.
    groups = {}
    for item in items:
        groups.setdefault(item[key], []).append(item)
    return groups


def plural(count, one, many):
    return one if count == 1 else many


def counted(count, label):
    # A section heading that starts with a large number.
    return f'<h2 class="counted"><span class="count">{count}</span>{label}</h2>'


def relation_note(row):
    # What the source does with the sentence, unless it simply claims it, and
    # the publication through which the link was found.
    notes = []
    if row['RELATION'] != 'claims':
        notes.append(f'The source {esc(row["RELATION"])} this.')
    if row.get('VIA'):
        notes.append(f'Via {source_link(row["VIA"])}.')
    return f'<span class="note">{" ".join(notes)}</span>' if notes else ''


def by_source(table, source_names):
    # One row per source with all its sentences.
    groups = grouped(table, 'SOURCE')
    sentences = len({row['AIDA-SENTENCE'] for row in table})
    out = [f'''
  <section class="wrap block">
    {counted(sentences, f'{plural(sentences, "sentence", "sentences")} from {len(groups)} {plural(len(groups), *source_names)}')}
    <ul class="rows by-source dense">''']
    for source, items in groups.items():
        out.append(f'''      <li>
        <div class="key">{source_link(source)}</div>
        <ul class="statements">''')
        for row in items:
            out.append(f'          <li>{sentence_link(row["AIDA-SENTENCE"])}{relation_note(row)}</li>')
        out.append('        </ul>\n      </li>')
    out.append('    </ul>\n  </section>')
    return '\n'.join(out)


def by_task(table, source_names):
    # One section per source, for sources with many sentences each.
    out = []
    for number, (source, items) in enumerate(grouped(table, 'SOURCE').items(), start=1):
        out.append(f'''
  <section class="wrap block">
    {counted(len(items), f'{plural(len(items), "sentence", "sentences")} for {source_names[0]} {number}')}
    <p class="block-intro">The {source_names[0]}: <a href="{esc(source)}">{esc(source_label(source))}</a></p>
    <ul class="rows dense">''')
        for row in items:
            out.append(f'      <li><p class="statement">{sentence_link(row["AIDA-SENTENCE"])}</p></li>')
        out.append('    </ul>\n  </section>')
    return '\n'.join(out)


def by_sentence(table, source_names):
    # One entry per sentence with its sources and components.
    groups = grouped(table, 'AIDA-SENTENCE')
    sources = len({row['SOURCE'] for row in table})
    out = [f'''
  <section class="wrap block">
    {counted(len(groups), f'{plural(len(groups), "sentence", "sentences")} from {sources} {plural(sources, *source_names)}')}
    <ul class="pubs wide">''']
    for sentence, items in groups.items():
        out.append(f'      <li>{sentence_link(sentence)}')
        for row in items:
            links = [source_link(row['SOURCE'])]
            links += [source_link(component, component_label(component))
                      for component in row.get('COMPONENTS', '').split()]
            out.append(f'        <span class="meta">{"".join(links)}</span>')
        out.append('      </li>')
    out.append('    </ul>\n  </section>')
    return '\n'.join(out)


def component_label(component):
    for prefix, label in (('http://purl.uniprot.org/taxonomy/', 'taxonomy:'),
                          ('http://www.ncbi.nlm.nih.gov/gene/', 'gene:')):
        if component.startswith(prefix):
            return label + component[len(prefix):]
    return source_label(component)


LAYOUTS = {'papers': by_source, 'user-study': by_task, 'bot-study': by_sentence, 'core-claims': by_sentence}

for slug, dataset in DATASETS.items():
    table = rows(dataset['table'])
    path = f'tables/{dataset["table"]}.csv'
    about = f'\n      <p class="about">{dataset["about"]}</p>' if dataset['about'] else ''
    body = f'''
  <section class="band compact">
    <div class="wrap">
      <h2 class="eyebrow">Table</h2>
      <p class="uri"><a href="{REPO}{path}">{path}</a></p>{about}
    </div>
  </section>''' + LAYOUTS[slug](table, dataset['source'])
    os.makedirs(f'docs/datasets/{slug}', exist_ok=True)
    with open(f'docs/datasets/{slug}/index.html', 'w', encoding='utf-8') as f:
        f.write(page(
            title=dataset['title'],
            lead=dataset['lead'],
            eyebrow='Dataset',
            body=body,
            generator='make-site-datasets.py',
            generated_from=path,
            more_title='More datasets',
            more=[(other['title'], other['lead'], f'../{name}/', 'Open the dataset')
                  for name, other in DATASETS.items() if name != slug],
        ))
    sentences = len({row['AIDA-SENTENCE'] for row in table})
    sources = len({row['SOURCE'] for row in table})
    print(f'docs/datasets/{slug}/index.html: {sentences} sentences from {sources} sources', file=sys.stderr)
