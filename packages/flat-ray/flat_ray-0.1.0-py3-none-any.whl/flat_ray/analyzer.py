#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
analyzer.py - Core logic for flat-ray CLI.
"""

import os
import json
import random
import csv
from io import StringIO
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Union

import sloppy_xml
from rich.console import Console
from rich.tree import Tree
from tqdm import tqdm
from joblib import Parallel, delayed
from termcolor import colored
import xml.etree.ElementTree as ET


def strip_ns(tag: str) -> str:
    """Remove namespace prefix from a tag."""
    return tag.split('}', 1)[-1] if '}' in tag else tag


def analyze_element(element: ET.Element, path: str,
                    report: Dict[str, Union[Dict, defaultdict]],
                    max_values: int) -> None:
    """
    Recursively analyze an XML element and collect structural data.

    Args:
        element: XML element to analyze.
        path: Current hierarchical path.
        report: Dictionary to accumulate structure, attributes, and text.
        max_values: Maximum number of values per field to collect.
    """
    tag = strip_ns(element.tag)
    current_path = f"{path}/{tag}" if path else tag
    report['tags'][current_path]['count'] += 1

    if "texts" not in report:
        report["texts"] = defaultdict(list)

    if max_values == -1 or len(report["texts"][tag]) < max_values:
        try:
            serialized = ET.tostring(element, encoding="unicode", method="xml").strip()
            report["texts"][tag].append(serialized)
        except Exception:
            pass  # ignore serialization errors

    for attr, value in element.attrib.items():
        attr = strip_ns(attr)
        attr_path = f"{current_path}/@{attr}"
        report['attributes'][attr_path]['count'] += 1
        if max_values == -1 or len(report['attributes'][attr_path]['values']) < max_values:
            report['attributes'][attr_path]['values'].append(value)

    for child in element:
        analyze_element(child, current_path, report, max_values)


def print_terminal_summary(report: dict, file_count: int,
                           format: str = "tree",
                           capture: bool = False) -> str:
    """
    Render the summary of tags and attributes to terminal or capture as string.

    Args:
        report: The analysis report dictionary.
        file_count: Number of files analyzed.
        format: Display format ('tree', 'flat', 'tree-flat', 'list').
        capture: Whether to return output as string instead of printing.

    Returns:
        str: Captured output if capture=True, otherwise an empty string.
    """
    buffer = StringIO() if capture else None
    console = Console(file=buffer, width=120, force_terminal=False, color_system=None) if capture else Console()

    title = f"📦 Files analyzed: {file_count}"
    if not capture:
        console.print(f"[green]{title}[/]\n")

    if format == "flat":
        tag_counts = defaultdict(int)
        attr_map = defaultdict(lambda: defaultdict(lambda: {"count": 0, "value_counts": defaultdict(int)}))

        for tag_path, tag_data in report["tags"].items():
            tag_name = tag_path.split("/")[-1]
            tag_counts[tag_name] += tag_data["count"]

        for attr_path, attr_data in report["attributes"].items():
            if "/@" not in attr_path:
                continue
            tag_path, attr = attr_path.split("/@")
            tag_name = tag_path.split("/")[-1]
            attr_map[tag_name][attr]["count"] += attr_data["count"]
            for val, c in attr_data["value_counts"].items():
                attr_map[tag_name][attr]["value_counts"][val] += c

        for tag in sorted(tag_counts):
            line = f"- {tag} ({tag_counts[tag]})"
            print_to = buffer.write if capture else lambda x: print(colored(x, "cyan"))
            print_to(line + "\n")
            for attr in sorted(attr_map[tag]):
                attr_data = attr_map[tag][attr]
                line = f"  - @{attr} ({attr_data['count']})"
                print_to = buffer.write if capture else lambda x: print(colored(x, "yellow"))
                print_to(line + "\n")
                for val, count in list(attr_data["value_counts"].items())[:3]:
                    buffer.write(f"    - {val} ({count})\n") if capture else print(f"    - {val} ({count})")

    elif format in {"tree", "tree-flat"}:
        tree = Tree(f"[bold green]📦 Files analyzed: {file_count}[/]")

        if format == "tree-flat":
            tag_counts = defaultdict(int)
            attr_map = defaultdict(lambda: defaultdict(lambda: {"count": 0, "value_counts": defaultdict(int)}))

            for tag_path, tag_data in report["tags"].items():
                tag_name = tag_path.split("/")[-1]
                tag_counts[tag_name] += tag_data["count"]

            for attr_path, attr_data in report["attributes"].items():
                if "/@" not in attr_path:
                    continue
                tag_path, attr = attr_path.split("/@")
                tag_name = tag_path.split("/")[-1]
                attr_map[tag_name][attr]["count"] += attr_data["count"]
                for val, c in attr_data["value_counts"].items():
                    attr_map[tag_name][attr]["value_counts"][val] += c

            for tag in sorted(tag_counts):
                tag_node = tree.add(f"[cyan]{tag}[/] [dim]({tag_counts[tag]})[/]")
                for attr in sorted(attr_map[tag]):
                    attr_data = attr_map[tag][attr]
                    attr_node = tag_node.add(f"[yellow]@{attr}[/] [dim]({attr_data['count']})[/]")
                    for val in list(attr_data["value_counts"].keys())[:3]:
                        attr_node.add(f"[dim]- {val} ({attr_data['value_counts'][val]})[/]")

        else:
            tag_nodes = {}
            for tag_path, tag_data in sorted(report["tags"].items()):
                parts = tag_path.split("/")
                current = tree
                built_path = ""
                for part in parts:
                    built_path = f"{built_path}/{part}" if built_path else part
                    if built_path not in tag_nodes:
                        node = current.add(
                            f"[cyan]{part}[/] [dim]({report['tags'].get(built_path, {}).get('count', 0)})[/]"
                        )
                        tag_nodes[built_path] = node
                    current = tag_nodes[built_path]

                for attr_path, attr_data in sorted(report["attributes"].items()):
                    if attr_path.startswith(f"{tag_path}/@"):
                        attr = attr_path.split("/@")[-1]
                        attr_node = current.add(
                            f"[yellow]@{attr}[/] [dim]({attr_data['count']})[/]"
                        )
                        for val in attr_data.get("value_counts", {}):
                            attr_node.add(f"[dim]- {val} ({attr_data['value_counts'][val]})[/]")

        console.print(tree)

    return buffer.getvalue() if capture else ""


def process_file(file_path: str,
                 extensions: Tuple[str, ...],
                 max_values: int) -> Optional[Tuple[dict, dict, dict]]:
    """
    Process a single XML/HTML file and extract its tag/attribute/text info.

    Args:
        file_path: Path to the file.
        extensions: Allowed file extensions.
        max_values: Max number of samples per attribute/text.

    Returns:
        Tuple of (tags, attributes, texts) or None on failure.
    """
    tags = defaultdict(lambda: {"count": 0})
    attributes = defaultdict(lambda: {"count": 0, "values": [], "value_counts": defaultdict(int)})
    texts = defaultdict(list)

    if not file_path.lower().endswith(tuple(ext.lower() for ext in extensions)):
        return None

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            root = sloppy_xml.tree_parse(content)
            analyze_element(root, "", {"tags": tags, "attributes": attributes, "texts": texts}, max_values)
        return tags, attributes, texts
    except Exception:
        return None


def merge_reports(reports: List[Optional[Tuple[dict, dict, dict]]],
                  max_values: int) -> dict:
    """
    Merge partial reports from multiple files.

    Args:
        reports: List of tuples (tags, attributes, texts).
        max_values: Limit for stored values/texts.

    Returns:
        Merged report dictionary.
    """
    final_tags = defaultdict(lambda: {"count": 0})
    final_attrs = defaultdict(lambda: {"count": 0, "values": [], "value_counts": defaultdict(int)})
    final_texts = defaultdict(list)

    for result in reports:
        if not result:
            continue
        tags, attrs, texts = result

        for path, data in tags.items():
            final_tags[path]["count"] += data["count"]

        for path, data in attrs.items():
            final_attrs[path]["count"] += data["count"]
            for val in data["values"]:
                if max_values == -1 or len(final_attrs[path]["values"]) < max_values:
                    final_attrs[path]["values"].append(val)
                final_attrs[path]["value_counts"][val] += 1

        for tag, lines in texts.items():
            final_texts[tag].extend(lines if max_values == -1 else lines[:max_values])

    return {"tags": final_tags, "attributes": final_attrs, "texts": final_texts}


def analyze_directory(input_dir: str,
                      output_path: str,
                      max_values: int = -1,
                      extensions: Tuple[str, ...] = (".xml", ".html"),
                      verbose: bool = False,
                      display_format: str = "tree",
                      text_output: Optional[str] = None,
                      n_jobs: int = -1,
                      sample_csv: Union[bool, str] = False) -> None:
    """
    Analyze all XML/HTML files in a directory recursively.

    Args:
        input_dir: Path to directory to scan.
        output_path: Path to write JSON summary.
        max_values: Max number of values per element or attribute.
        extensions: File extensions to consider.
        verbose: Display progress output.
        display_format: Output rendering format.
        text_output: Optional path to save plain-text output.
        n_jobs: Number of parallel jobs for processing.
        sample_csv: Path to optional CSV file to export content samples.
    """
    file_paths = [
        os.path.join(root, f)
        for root, _, files in os.walk(input_dir)
        for f in files
        if f.lower().endswith(tuple(ext.lower() for ext in extensions))
    ]

    results = Parallel(n_jobs=n_jobs)(
        delayed(process_file)(fp, extensions, max_values) for fp in tqdm(file_paths, desc="Analyzing files")
    )

    report = merge_reports(results, max_values)

    for attr_path, attr_data in report["attributes"].items():
        attr_data["values"] = list(set(attr_data["values"]))
        attr_data["value_counts"] = dict(attr_data["value_counts"])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print_terminal_summary(report, len(file_paths), format=display_format, capture=False)

    if text_output:
        # Get captured output without repeating header
        summary = print_terminal_summary(report, len(file_paths), format=display_format, capture=True)
        # Remove first line if it's the same as the title
        summary_lines = summary.splitlines()
        #if summary_lines and summary_lines[0].startswith("📦 Files analyzed"):
        #    summary = "\n".join(summary_lines[1:])
        with open(text_output, "w", encoding="utf-8") as f:
            f.write(summary)

    if sample_csv:
        with open(sample_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Element", "Content"])
            for tag, samples in report.get("texts", {}).items():
                unique_samples = list(set(samples))
                chosen = random.sample(unique_samples, min(3, len(unique_samples)))
                for val in chosen:
                    writer.writerow([tag, val])
        print(f"📄 Sample exported to: {sample_csv}")
