#!/usr/bin/env python3
"""
naming-roots.py — Etymology and root word explorer for naming projects.

Queries Wiktionary API for etymologies, roots, and derived terms.
Falls back to web scraping Etymonline when Wiktionary lacks data.

Usage:
    naming-roots.py <concept> [<concept>...]
    naming-roots.py --root <root>
    naming-roots.py --blend <word1> <word2>

Examples:
    naming-roots.py light speed transform
    naming-roots.py --root "lux"
    naming-roots.py --blend "swift" "feather"
"""

import sys
import json
import urllib.request
import urllib.parse
import re
from typing import Optional


def fetch_json(url: str, timeout: int = 10) -> Optional[dict]:
    """Fetch JSON from a URL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NamingRoots/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def wiktionary_lookup(word: str) -> dict:
    """Look up a word on Wiktionary for etymology and related terms."""
    url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{urllib.parse.quote(word)}"
    data = fetch_json(url)
    result = {"word": word, "definitions": [], "etymology": None}

    if not data:
        return result

    for lang_section in data.get("en", []):
        part = lang_section.get("partOfSpeech", "")
        for defn in lang_section.get("definitions", []):
            text = re.sub(r"<[^>]+>", "", defn.get("definition", ""))
            if text:
                result["definitions"].append({"pos": part, "text": text[:200]})

    # Try to get etymology from the HTML page
    html_url = f"https://en.wiktionary.org/w/api.php?action=parse&page={urllib.parse.quote(word)}&prop=wikitext&format=json"
    html_data = fetch_json(html_url)
    if html_data:
        wikitext = html_data.get("parse", {}).get("wikitext", {}).get("*", "")
        etym_match = re.search(r"===Etymology===\n(.*?)(?=\n===|\n\[\[Category|\Z)", wikitext, re.DOTALL)
        if etym_match:
            etym = etym_match.group(1).strip()
            # Clean up wiki markup
            etym = re.sub(r"\{\{[^}]*\}\}", "", etym)
            etym = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", etym)
            etym = etym.strip()
            if etym:
                result["etymology"] = etym[:500]

    return result


def etymonline_lookup(word: str) -> Optional[str]:
    """Scrape Etymonline for a word's etymology."""
    url = f"https://www.etymonline.com/word/{urllib.parse.quote(word)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NamingRoots/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode()
        # Extract the etymology text from the page
        match = re.search(r'class="word--[^"]*__defination[^"]*"[^>]*>(.*?)</section>', html, re.DOTALL)
        if match:
            text = re.sub(r"<[^>]+>", "", match.group(1))
            text = re.sub(r"\s+", " ", text).strip()
            return text[:600] if text else None
    except Exception:
        pass
    return None


def find_related_words(concept: str) -> list:
    """Use Wiktionary category/search to find related words."""
    url = f"https://en.wiktionary.org/w/api.php?action=opensearch&search={urllib.parse.quote(concept)}&limit=20&format=json"
    data = fetch_json(url)
    if data and len(data) > 1:
        return data[1][:15]
    return []


def generate_blends(word1: str, word2: str) -> list:
    """Generate portmanteau/blend candidates from two words."""
    blends = []

    # Front of word1 + back of word2
    for i in range(2, len(word1)):
        for j in range(0, len(word2) - 1):
            blend = word1[:i] + word2[j:]
            if 4 <= len(blend) <= 10:
                blends.append(blend)

    # Front of word2 + back of word1
    for i in range(2, len(word2)):
        for j in range(0, len(word1) - 1):
            blend = word2[:i] + word1[j:]
            if 4 <= len(blend) <= 10:
                blends.append(blend)

    # Deduplicate and filter
    seen = set()
    unique = []
    for b in blends:
        b_lower = b.lower()
        if b_lower not in seen and b_lower != word1.lower() and b_lower != word2.lower():
            seen.add(b_lower)
            unique.append(b)

    # Score by pronounceability (vowel/consonant alternation)
    def score(w):
        vowels = set("aeiou")
        transitions = sum(1 for i in range(len(w)-1) if (w[i].lower() in vowels) != (w[i+1].lower() in vowels))
        ratio = transitions / max(len(w) - 1, 1)
        return ratio

    unique.sort(key=score, reverse=True)
    return unique[:25]


def explore_concept(concept: str):
    """Full exploration of a concept for naming purposes."""
    print(f"\n{'='*60}")
    print(f"  CONCEPT: {concept.upper()}")
    print(f"{'='*60}")

    # 1. Direct lookup
    print(f"\n--- Wiktionary: '{concept}' ---")
    wiki = wiktionary_lookup(concept)
    if wiki["etymology"]:
        print(f"Etymology: {wiki['etymology']}")
    if wiki["definitions"]:
        for d in wiki["definitions"][:3]:
            print(f"  [{d['pos']}] {d['text']}")

    # 2. Etymonline
    print(f"\n--- Etymonline: '{concept}' ---")
    etym = etymonline_lookup(concept)
    if etym:
        print(etym)
    else:
        print("(no entry found)")

    # 3. Related words
    print(f"\n--- Related words ---")
    related = find_related_words(concept)
    if related:
        print(", ".join(related))
    else:
        print("(none found)")

    # 4. Common roots for this concept
    print(f"\n--- Suggested roots to explore ---")
    roots = find_related_words(concept + " root")
    latin = find_related_words(concept + " Latin")
    greek = find_related_words(concept + " Greek")
    all_suggestions = list(set(roots + latin + greek))[:15]
    if all_suggestions:
        print(", ".join(all_suggestions))
    else:
        print("(use the roots-and-morphemes.md reference file)")


def explore_root(root: str):
    """Deep dive on a specific root."""
    print(f"\n{'='*60}")
    print(f"  ROOT: {root}")
    print(f"{'='*60}")

    wiki = wiktionary_lookup(root)
    if wiki["etymology"]:
        print(f"\nEtymology: {wiki['etymology']}")
    if wiki["definitions"]:
        print("\nDefinitions:")
        for d in wiki["definitions"][:5]:
            print(f"  [{d['pos']}] {d['text']}")

    etym = etymonline_lookup(root)
    if etym:
        print(f"\nEtymonline: {etym}")

    related = find_related_words(root)
    if related:
        print(f"\nRelated/derived: {', '.join(related)}")


def blend_words(word1: str, word2: str):
    """Generate and display blend candidates."""
    print(f"\n{'='*60}")
    print(f"  BLENDING: {word1} + {word2}")
    print(f"{'='*60}")

    blends = generate_blends(word1, word2)
    if blends:
        print(f"\nTop blend candidates (sorted by pronounceability):\n")
        for i, b in enumerate(blends, 1):
            print(f"  {i:2d}. {b}")
    else:
        print("(no viable blends found)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--root" and len(sys.argv) >= 3:
        explore_root(sys.argv[2])
    elif sys.argv[1] == "--blend" and len(sys.argv) >= 4:
        blend_words(sys.argv[2], sys.argv[3])
    else:
        concepts = sys.argv[1:] if sys.argv[1] != "--" else sys.argv[2:]
        for concept in concepts:
            explore_concept(concept)


if __name__ == "__main__":
    main()
