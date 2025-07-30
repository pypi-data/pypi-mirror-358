# tests/test_analyzer.py

import os
import tempfile
import json
from flat_ray.analyzer import analyze_directory


def test_analyze_html():
    html_content = """
    <html>
        <head>
            <title>Ancient Manuscript</title>
        </head>
        <body>
            <section id="intro">
                <h1>History of the Empire</h1>
                <p>The empire was founded in <b>476 AD</b> after the fall of Rome.</p>
            </section>
            <section id="catalog">
                <entry type="scroll" lang="latin">
                    <title>De Bello Gallico</title>
                    <author>Julius Caesar</author>
                    <date>-58</date>
                </entry>
                <entry type="codex" lang="greek">
                    <title>Histories</title>
                    <author>Herodotus</author>
                    <date>-430</date>
                </entry>
            </section>
        </body>
    </html>
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = os.path.join(tmpdir, "historical.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        output_path = os.path.join(tmpdir, "report.json")

        analyze_directory(
            input_dir=tmpdir,
            output_path=output_path,
            max_values=5,
            extensions=(".html",),
            verbose=False,
            display_format="flat",
            text_output=None,
            sample_csv=None,
            n_jobs=1,
        )

        with open(output_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        assert "html/head/title" in report["tags"]
        assert "html/body/section/h1" in report["tags"]
        assert "html/body/section/entry/title" in report["tags"]
        assert "html/body/section/@id" in report["attributes"]
        assert set(report["attributes"]["html/body/section/@id"]["value_counts"].keys()) == {"intro", "catalog"}
        assert "html/body/section/entry/@type" in report["attributes"]
        assert set(report["attributes"]["html/body/section/entry/@type"]["value_counts"].keys()) == {"scroll", "codex"}
        assert "entry" in report["texts"]
        assert any("De Bello Gallico" in t for t in report["texts"]["entry"])
        assert any("Herodotus" in t for t in report["texts"]["entry"])
        assert "p" in report["texts"]
        assert any("476 AD" in t for t in report["texts"]["p"])


def test_mallformed_xml():
    malformed_xml_content = """
    <div><p>Napoleon Bonaparte <br >was a French <span style='color: red;'>military leader</span> and emperor who rose to prominence during the French Revolution and led several successful campaigns during the Revolutionary Wars. He is best known for his role in the Napoleonic Wars, 
    where he established hegemony over most <br >of continental Europe and spread revolutionary ideals.</p>

    <a href="https://en.wikipedia.org/wiki/Napoleon" target="_blank">Learn more</a>
    </div>
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        malformed_xml_path = os.path.join(tmpdir, "malformed.xml")
        with open(malformed_xml_path, "w", encoding="utf-8") as f:
            f.write(malformed_xml_content)

        output_path = os.path.join(tmpdir, "report.json")

        analyze_directory(
            input_dir=tmpdir,
            output_path=output_path,
            max_values=5,
            extensions=(".xml",),
            verbose=False,
            display_format="flat",
            text_output=None,
            sample_csv=None,
            n_jobs=1,
        )

        with open(output_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        assert "div/p" in report["tags"]
        assert "div/a" in report["tags"]
        assert "p" in report["texts"]
        assert any("Napoleon" in t for t in report["texts"]["p"])

