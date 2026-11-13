AIDA Sentences
==============

AIDA is a scheme for English sentences. Such sentences are:

- **Atomic:** a sentence describing one thought that cannot be further broken
  down in a practical way
- **Independent:** a sentence that can stand on its own, without external
  references like "this effect" or "we"
- **Declarative:** a complete sentence ending with a full stop that could in
  theory be either true or false
- **Absolute:** a sentence describing the core of a claim ignoring the
  (un)certainty about its truth and ignoring how it was discovered (no
  "probably" or "evaluation showed that"); typically in present tense


Publications
------------

See the following publications for the details:

- Tobias Kuhn. [Using the AIDA Language to Formally Organize Scientific
  Claims](https://doi.org/10.3233/978-1-61499-904-1-52). In _Proceedings of the
  Sixth International Workshop on Controlled Natural Language (CNL 2018)_. IOS
  Press, 2018.
- Tobias Kuhn, Paolo Emilio Barbano, Mate Levente Nagy, and Michael Krauthammer.
  [Broadening the Scope of Nanopublications.](http://www.tkuhn.org/pub/kuhn2013eswc.pdf)
  In _Proceedings of the 10th Extended Semantic Web Conference (ESWC)_.
  Springer, 2013.


Examples
--------

A simple example of an AIDA sentence is:

> Malaria is transmitted by moquitoes.

This is a more specific and more complex example:

> The degree of hepatic reticuloendothelial function impairment does not differ
> between cirrhotic patients with and without previous history of SBP.


URIs
----

AIDA sentences can be represented by URIs of the following form:

- http://purl.org/aida/Malaria+is+transmitted+by+moquitoes.
- http://purl.org/aida/The+degree+of+hepatic+reticuloendothelial+function+impairment+does+not+differ+between+cirrhotic+patients+with+and+without+previous+history+of+SBP.


Website
-------

The `docs` directory contains the AIDA website, made to be served with GitHub
Pages (repository settings > Pages > deploy from branch `master`, folder
`/docs`):

- `index.html` is the landing page.
- `s/index.html` shows a single AIDA sentence, given URL-encoded after a `?`
  as in `s/?Malaria+is+transmitted+by+mosquitoes.`, together with its URI and
  the sources linked to it.
- `404.html` forwards any other path to that sentence page, so that
  `/aida/Malaria+is+transmitted+by+mosquitoes.` works too (but is first
  answered with HTTP status 404).
- `data/sentences.json` holds the sources of each sentence. It is generated
  from `tables/all.csv` with `scripts/make-site-data.py`, which also prints
  the sentence and source counts shown on the landing page.
- `usecases/*/index.html` are the use case pages. They are generated from the
  Markdown files in `usecases` with `scripts/make-site-usecases.py` and should
  not be edited by hand.

For `http://purl.org/aida/...` URIs to end up on the website, the PURL has to
be a partial redirect to the address of the sentence page followed by `?`,
that is `<site address>/s/?`. A partial redirect to the site address itself
works as well, via `404.html`.


Related Repositories
--------------------

- [TomJansen25/Extracting-Core-Claims](https://github.com/TomJansen25/Extracting-Core-Claims)
- [tkuhn/nanopubstudies-supplementary](https://github.com/tkuhn/nanopubstudies-supplementary)

