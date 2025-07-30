# flat-ray

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/Lucaterre/flat-ray)](LICENSE)
[![CI - flat-ray](https://github.com/Lucaterre/flat-ray/actions/workflows/ci.yml/badge.svg)](https://github.com/Lucaterre/flat-ray/actions/workflows/ci.yml)

> A CLI tool for analyzing malformed or well-formed XML/HTML files, generating flat or hierarchical summaries of tags, attributes, and text content — ideal for structural insight and markup analysis before data cleanning & preprocessing for corpora integration project.

---

## Features

- Robust parsing of malformed XML/HTML using `sloppy-xml`
- Hierarchical and flattened structural reports
- sample extraction
- CLI output as rich tree/list views
- Export to JSON / TXT / CSV
- Supports parallel processing

---

## Installation

```bash
pip install flat-ray
```

### for development only:

```bash
git clone https://github.com/<ton-username>/flat-ray.git
cd flat-ray
pip install -e .
```

## Usage
```bash
flat-ray ./path/to/directory (.xml, .html, .txt with markup files)
```

## Options

```
flat-ray --help

arguments:
  directory            Path to input folder

options:
  -o, --output         Output JSON file (default: report.json)
    --max-values         Max number of values to keep per attribute or element content.
                       Use -1 for no limit. (default: -1)
  --ext                File extensions to scan (default: .xml .html .txt (with markup))
  --display-format     Format: tree, list, flat, tree-flat (default: tree-flat)
                        - `tree`: Full XML tree structure (hierarchical)
                        - `flat`: Flattened unique tags and attributes with occurences and list-style indentation view
                        - `tree-flat`: Flattened unique tags and attributes with occurences and tree view
  --text-output        Save terminal output to a text file (default: output.txt)
  --sample-csv         Export sample text content to CSV (default: samples.csv)
  --n-jobs             Number of cores for parallel processing (default: -1 for all)
  -v, --verbose        Print summary in terminal
```

## Output

By default, `flat-ray` generates the following files:

- `report.json`: structure, tags, attributes, attributes values

- `output.txt`: rich formatted terminal output

- `samples.csv`: sampled content per tag (text inside elements)

## Run Tests

```
pytest
```

## Exemple output

- `--display-format tree-flat`

```bash
📦 Files analyzed: 40570
├── a (212404)
│   ├── @class (212318)
│   │   ├── - footnote-ref (106107)
│   │   ├── - sdendnoteanc (1)
│   │   └── - footnote-backref (106116)
│   ├── @href (212404)
│   │   ├── - #fn:1 (40544)
│   │   ├── - #fn:2 (28558)
│   │   └── - #fn:3 (15258)
│   ├── @name (95)
│   │   ├── - sdfootnote99anc (1)
│   │   ├── - sdfootnote369sym (1)
│   │   └── - sdfootnote324sym (2)
│   ├── @target (30)
│   │   ├── - _blank (15)
│   │   ├── - Bataille de Lissa (1811) (1)
│   │   └── - 13 mars (1)
│   └── @title (106116)
│       ├── - Jump back to footnote 1 in the text (40547)
│       ├── - Jump back to footnote 2 in the text (28562)
│       └── - Jump back to footnote 3 in the text (15259)
├── article (40570)
│   └── @class (40570)
│       └── - md-html-article-container (40570)
├── b (41072)
│   └── @style (40570)
│       └── - text-transform: none (40570)
├── br (47087)
├── center (68)
├── col (5769)
│   └── @width (5769)
│       ├── - 41 (40)
│       ├── - 24 (103)
│       └── - 190 (11)
├── colgroup (1831)
├── dd (650)
├── div (40555)
│   ├── @class (40547)
│   │   └── - footnote (40547)
│   ├── @style (2)
│   │   └── - text-align: right (2)
│   └── @title (6)
│       └── - footer (6)
├── dl (1027)
├── em (4)
├── font (34452)
│   ├── @color (9659)
│   │   ├── - #000000 (9135)
│   │   ├── - #ff0000 (493)
│   │   └── - #0000ff (24)
│   ├── @face (1)
│   │   └── - Verdana, sans-serif (1)
│   ├── @size (24792)
│   │   ├── - 3 (11733)
│   │   ├── - 4 (18)
│   │   └── - 2 (12347)
│   └── @style (24767)
│       ├── - font-size: 12pt (11710)
│       ├── - font-size: 14pt (15)
│       └── - font-size: 11pt (4714)
├── h1 (40571)
│   ├── @align (1865)
│   │   └── - justify (1865)
│   ├── @lang (9758)
│   │   ├── - fr-FR (9737)
│   │   ├── - pt-BR (7)
│   │   └── - de-DE (5)
│   └── @style (40570)
│       └── - text-transform: uppercase; font-family: Chivo; font-size: 1.5rem; line-height: 1; (40570)
├── h2 (40566)
│   ├── @align (5)
│   │   └── - justify (5)
│   ├── @class (261)
│   │   └── - style-titre-2-+-interligne-:-double-western (261)
│   ├── @data-kind (40556)
│   │   └── - letter-context; (40556)
│   ├── @lang (8984)
│   │   ├── - fr-FR (8509)
│   │   ├── - en-GB (428)
│   │   └── - en-US (38)
│   └── @style (40561)
│       ├── - text-align: right; font-size: 1em; font-weight: normal (40553)
│       ├── - text-align: center; text-align: right; font-size: 1em; font-weight: normal (3)
│       └── - text-indent: 1.25cm (1)
├── h3 (26887)
│   ├── @align (32)
│   │   └── - justify (32)
│   ├── @class (1181)
│   │   ├── - style-titre-4-western (473)
│   │   ├── - style-titre-4-+-italique-western (140)
│   │   └── - style-titre-3-+-italique (430)
│   ├── @data-kind (26603)
│   │   └── - letter-signature (26603)
│   ├── @lang (6321)
│   │   ├── - fr-FR (6259)
│   │   ├── - nl-NL (2)
│   │   └── - en-GB (31)
│   └── @style (26734)
│       ├── - text-align: right; font-size: 1em; font-weight: normal (26579)
│       ├── -  (126)
│       └── - text-align: right; text-align: right; font-size: 1em; font-weight: normal (21)
├── h4 (404)
│   ├── @align (10)
│   │   └── - justify (10)
│   ├── @class (7)
│   │   ├── - style-titre-4-western (5)
│   │   ├── - style-titre-4-+-italique-rouge1 (1)
│   │   └── - style-titre-4-+-italique-western (1)
│   ├── @lang (56)
│   │   ├── - fr-FR (55)
│   │   └── - en-GB (1)
│   └── @style (199)
│       ├── -  (189)
│       ├── - line-height: 100% (2)
│       └── - text-indent: 0cm (2)
├── h5 (2)
├── h6 (1)
├── hr (40547)
├── i (101247)
├── img (5)
│   ├── @align (5)
│   │   └── - bottom (5)
│   ├── @border (5)
│   │   └── - 0 (5)
│   ├── @height (5)
│   │   ├── - 631 (1)
│   │   ├── - 718 (1)
│   │   └── - 451 (1)
│   ├── @name (5)
│   │   ├── - Image1 (3)
│   │   ├── - Image2 (1)
│   │   └── - Image 2 (1)
│   ├── @src (5)
│   │   ├── - CG9_1809_02_03_04_html_971e6afce34603bc.jpg (1)
│   │   ├── - CG9_1809_07_08_html_af22452c90090.jpg (1)
│   │   └── - CG11-02_1811_05_num_html_9850912d63ae31ec.jpg (1)
│   └── @width (5)
│       ├── - 518 (1)
│       ├── - 449 (1)
│       └── - 428 (1)
├── li (106136)
│   └── @id (106112)
│       ├── - fn:1 (40547)
│       ├── - fn:2 (28559)
│       └── - fn:3 (15258)
├── ol (40551)
├── p (397416)
│   ├── @align (6186)
│   │   └── - justify (6186)
│   ├── @class (1917)
│   │   ├── - sdfootnote-western (1881)
│   │   └── - sdfootnote (36)
│   ├── @lang (35933)
│   │   ├── - fr-FR (35470)
│   │   ├── - en-GB (165)
│   │   └── - nl-NL (13)
│   ├── @letter-signature (3)
│   │   └── -  (3)
│   └── @style (125738)
│       ├── - text-align: right; text-indent: 0cm; orphans: 0; widows: 0 (1959)
│       ├── - text-indent: 0cm; orphans: 0; widows: 0 (4243)
│       └── - text-align: left; text-indent: 0cm; orphans: 0; widows: 0 (303)
├── sdfield (6)
│   ├── @format (6)
│   │   └── - PAGE (6)
│   ├── @subtype (6)
│   │   └── - RANDOM (6)
│   └── @type (6)
│       └── - PAGE (6)
├── span (40251)
│   ├── @dir (23)
│   │   └── - ltr (23)
│   ├── @id (23)
│   │   ├── - Cadre1 (12)
│   │   ├── - Cadre3 (3)
│   │   └── - Frame1 (2)
│   ├── @lang (6409)
│   │   ├── - en-GB (2201)
│   │   ├── - en-US (600)
│   │   └── - it-IT (339)
│   └── @style (7826)
│       ├── - font-variant: normal (6307)
│       ├── - font-variant: small-caps (1038)
│       └── - text-transform: uppercase (142)
├── strike (10)
├── strong (15)
├── sup (262929)
│   └── @id (106107)
│       ├── - fnref:1 (40544)
│       ├── - fnref:2 (28555)
│       └── - fnref:3 (15257)
├── table (1438)
│   ├── @cellpadding (1427)
│   │   ├── - 7 (1139)
│   │   ├── - 4 (92)
│   │   └── - 1 (102)
│   ├── @cellspacing (1427)
│   │   ├── - 0 (1411)
│   │   └── - 1 (16)
│   ├── @dir (19)
│   │   └── - ltr (19)
│   ├── @hspace (1)
│   │   └── - 9 (1)
│   ├── @style (1)
│   │   └── - text-align: left (1)
│   └── @width (1428)
│       ├── - 299 (6)
│       ├── - 451 (9)
│       └── - 525 (3)
├── tbody (1766)
├── td (58269)
│   ├── @colspan (3411)
│   │   ├── - 4 (353)
│   │   ├── - 3 (816)
│   │   └── - 5 (268)
│   ├── @height (169)
│   │   ├── - 26 (3)
│   │   ├── - 4 (39)
│   │   └── - 23 (2)
│   ├── @rowspan (2695)
│   │   ├── - 7 (63)
│   │   ├── - 3 (541)
│   │   └── - 4 (396)
│   ├── @style (58117)
│   │   ├── - border: 1px solid #000000; padding: 0cm 0.19cm (3826)
│   │   ├── - border: none; padding: 0cm (37788)
│   │   └── - border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding-top: 0cm; 
│   │       padding-bottom: 0.1cm; padding-left: 0cm; padding-right: 0cm (61)
│   ├── @valign (15065)
│   │   ├── - top (13855)
│   │   └── - bottom (1210)
│   └── @width (58233)
│       ├── - 41 (352)
│       ├── - 24 (893)
│       └── - 190 (104)
├── thead (3)
├── tr (14972)
│   └── @valign (8310)
│       ├── - top (8277)
│       └── - bottom (33)
├── u (753)
└── ul (4)
📄 Sample exported to: samples.csv
[TERMINATED IN 9.24 secs]
```
## Citation

If you use this tool in your research, please check the [CITATION.cff](CITATION.cff) file for citation information.