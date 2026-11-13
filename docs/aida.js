/* AIDA website: sentence <-> URI conversion, the converter on the landing
   page, and the sentence page. No dependencies. */
(function () {
  'use strict';

  const PREFIX = 'http://purl.org/aida/';

  // Directory this script is served from, i.e. the root of the site.
  const BASE = new URL('.', document.currentScript.src);

  // Relations as used in tables/all.csv, in display order, with the label
  // for one source and for several.
  const RELATIONS = [
    ['claims', 'claims it', 'claim it'],
    ['hypothesizes', 'hypothesizes it', 'hypothesize it'],
    ['investigates', 'investigates it', 'investigate it'],
    ['discusses', 'discusses it', 'discuss it'],
    ['reviews', 'reviews it', 'review it'],
    ['refutes', 'refutes it', 'refute it']
  ];

  // Same encoding as scripts/make-aida-uri.sh: percent-encode everything
  // except A-Z a-z 0-9 - _ . ~ and write spaces as "+".
  function encodeSentence(sentence) {
    let encoded;
    try {
      encoded = encodeURIComponent(sentence);
    } catch (e) {
      // Lone surrogate: not encodable as UTF-8.
      encoded = encodeURIComponent(sentence.replace(/[\uD800-\uDFFF]/g, '�'));
    }
    return encoded
      .replace(/[!'()*]/g, (c) => '%' + c.charCodeAt(0).toString(16).toUpperCase())
      .replace(/%20/g, '+');
  }

  function decodeSentence(encoded) {
    const spaced = encoded.replace(/\+/g, ' ');
    try {
      return decodeURIComponent(spaced);
    } catch (e) {
      // A stray "%" somewhere: decode the well-formed runs and keep the rest.
      return spaced.replace(/(?:%[0-9A-Fa-f]{2})+/g, (run) => {
        try { return decodeURIComponent(run); } catch (e2) { return run; }
      });
    }
  }

  // The sentence page takes the encoded sentence after "?" (or "?s=", or
  // "#"). Literal "&" and "=" never occur in an encoded sentence, so anything
  // split off by them is an unrelated parameter such as a tracking id.
  function encodedSentenceFromLocation() {
    const parts = location.search.slice(1).split('&');
    for (const part of parts) {
      if (part.startsWith('s=')) return part.slice(2);
    }
    for (const part of parts) {
      if (part && !part.includes('=')) return part;
    }
    return location.hash.slice(1);
  }

  // Show a URI so that long ones wrap after a "+" rather than mid-word.
  function showUri(el, uri) {
    el.textContent = '';
    const pieces = uri.split('+');
    pieces.forEach((piece, i) => {
      if (i < pieces.length - 1) el.append(piece + '+', document.createElement('wbr'));
      else el.append(piece);
    });
  }

  function copyText(text, button, status) {
    const done = () => {
      button.textContent = 'Copied';
      if (status) status.textContent = 'URI copied';
      setTimeout(() => {
        button.textContent = button.dataset.label;
        if (status) status.textContent = '';
      }, 1600);
    };
    const fallback = () => {
      const area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      try { if (document.execCommand('copy')) done(); } catch (e) { /* nothing more to try */ }
      area.remove();
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else {
      fallback();
    }
  }

  function initCopy(root, getText) {
    const button = root.querySelector('[data-copy]');
    button.dataset.label = button.textContent;
    button.addEventListener('click', () => copyText(getText(), button, root.querySelector('[data-status]')));
  }

  // Landing page: type a sentence, get its URI.
  function initConverter(root) {
    const input = root.querySelector('[data-sentence-input]');
    const output = root.querySelector('[data-uri-output]');
    const open = root.querySelector('[data-open]');
    const update = () => {
      const encoded = encodeSentence(input.value.trim());
      showUri(output, PREFIX + encoded);
      open.href = new URL('s/?' + encoded, BASE).href;
      open.hidden = !encoded;
    };
    input.addEventListener('input', update);
    initCopy(root, () => output.textContent);
    update();
  }

  function sourceLabel(source) {
    let m;
    if ((m = /^https?:\/\/(?:dx\.)?doi\.org\/(.+)$/.exec(source))) return 'doi:' + m[1];
    if ((m = /^https?:\/\/identifiers\.org\/pubmed\/(.+)$/.exec(source))) return 'pubmed:' + m[1];
    if ((m = /^urn:isbn:(.+)$/i.exec(source))) return 'isbn:' + m[1];
    return source.replace(/^https?:\/\/(?:www\.)?/, '');
  }

  function renderSources(section, links) {
    const columns = section.querySelector('[data-source-columns]');
    columns.textContent = '';
    const byRelation = new Map();
    for (const [relation, source] of links) {
      if (!byRelation.has(relation)) byRelation.set(relation, []);
      byRelation.get(relation).push(source);
    }
    const order = RELATIONS.filter(([name]) => byRelation.has(name));
    for (const name of byRelation.keys()) {
      if (!RELATIONS.some(([known]) => known === name)) order.push([name, name, name]);
    }
    for (const [name, one, many] of order) {
      const sources = byRelation.get(name);
      const column = document.createElement('div');
      column.className = 'column';
      const heading = document.createElement('h3');
      const count = document.createElement('span');
      count.className = 'count';
      count.textContent = sources.length;
      heading.append(count, sources.length === 1 ? one : many);
      const list = document.createElement('ul');
      for (const source of sources) {
        const item = document.createElement('li');
        const isLink = /^https?:\/\//.test(source);
        const el = document.createElement(isLink ? 'a' : 'span');
        if (isLink) el.href = source;
        el.textContent = sourceLabel(source);
        item.append(el);
        list.append(item);
      }
      column.append(heading, list);
      columns.append(column);
    }
    section.hidden = false;
  }

  // Sentence page: show the sentence given in the URL, its URI, and the
  // sources linked to it in the repository, if any.
  function initSentencePage(root) {
    const found = root.querySelector('[data-found]');
    const empty = root.querySelector('[data-empty]');
    const heading = root.querySelector('[data-sentence]');
    const uri = root.querySelector('[data-uri]');
    const hint = root.querySelector('[data-hint]');
    const sources = root.querySelector('[data-sources]');
    let dataset;

    const render = () => {
      const sentence = decodeSentence(encodedSentenceFromLocation());
      found.hidden = !sentence;
      empty.hidden = !!sentence;
      sources.hidden = true;
      if (!sentence) return;

      heading.textContent = sentence;
      heading.dataset.size = sentence.length > 280 ? 'l' : sentence.length > 160 ? 'm' : 's';
      showUri(uri, PREFIX + encodeSentence(sentence));
      document.title = sentence + ' · AIDA';

      // Trailing full stops often get lost when URLs are turned into links.
      const lostStop = !sentence.trim().endsWith('.');
      hint.hidden = !lostStop;
      if (lostStop) {
        const link = hint.querySelector('[data-hint-link]');
        link.textContent = sentence.trim() + '.';
        link.href = '?' + encodeSentence(sentence.trim() + '.');
      }

      dataset = dataset || fetch(new URL('data/sentences.json', BASE))
        .then((response) => (response.ok ? response.json() : null))
        .catch(() => null);
      dataset.then((data) => {
        if (!data || !data.sentences) return;
        // Some URIs in exported/data.nt carry doubled double quotes (%22%22)
        // left over from the CSV escaping; look those up as well.
        const key = [sentence, sentence.replace(/""/g, '"')]
          .find((k) => Object.prototype.hasOwnProperty.call(data.sentences, k));
        if (key !== undefined) renderSources(sources, data.sentences[key]);
      });
    };

    initCopy(root, () => uri.textContent);
    window.addEventListener('hashchange', render);
    render();
  }

  const converter = document.querySelector('[data-converter]');
  if (converter) initConverter(converter);

  const sentencePage = document.querySelector('[data-sentence-page]');
  if (sentencePage) initSentencePage(sentencePage);
})();
