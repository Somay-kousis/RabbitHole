#!/usr/bin/env python3
"""Seed courtroom legal data for future RAG.

This script intentionally avoids CAPTCHA-gated scraping. It fetches:
- curated Central Acts from India Code
- curated Supreme Court precedent PDFs from direct official URLs

Outputs are written under app/courtroom/data/.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "app" / "courtroom" / "data"
INDIA_CODE_BASE = "https://www.indiacode.nic.in"
CENTRAL_ACTS_BROWSE = (
    INDIA_CODE_BASE
    + "/handle/123456789/1362/browse?type=shorttitle&sort_by=3&order=ASC&rpp=100&etal=-1&offset={offset}"
)
USER_AGENT = "RabbitHole legal corpus seeder/0.1 (+local research corpus)"


@dataclass(frozen=True)
class LawTarget:
    category: str
    match: str
    title: str
    notes: str = ""


@dataclass(frozen=True)
class CaseTarget:
    category: str
    title: str
    year: str
    court: str
    url: str
    principle: str
    notes: str = ""


LAW_TARGETS: list[LawTarget] = [
    LawTarget("constitutional_admin", "administrative tribunals act 1985", "The Administrative Tribunals Act, 1985"),
    LawTarget("constitutional_admin", "right to information act 2005", "The Right to Information Act, 2005"),
    LawTarget("criminal", "bharatiya nyaya sanhita 2023", "The Bharatiya Nyaya Sanhita, 2023"),
    LawTarget("criminal", "bharatiya nagarik suraksha sanhita 2023", "The Bharatiya Nagarik Suraksha Sanhita, 2023"),
    LawTarget("criminal", "indian penal code 1860", "The Indian Penal Code, 1860"),
    LawTarget("criminal", "code of criminal procedure 1973", "The Code of Criminal Procedure, 1973"),
    LawTarget("criminal", "protection of children from sexual offences act 2012", "The Protection of Children from Sexual Offences Act, 2012"),
    LawTarget("criminal", "juvenile justice care and protection of children act 2015", "The Juvenile Justice (Care and Protection of Children) Act, 2015"),
    LawTarget("civil_procedure_evidence", "code of civil procedure 1908", "The Code of Civil Procedure, 1908"),
    LawTarget("civil_procedure_evidence", "indian evidence act 1872", "The Indian Evidence Act, 1872"),
    LawTarget("civil_procedure_evidence", "bharatiya sakshya adhiniyam 2023", "The Bharatiya Sakshya Adhiniyam, 2023"),
    LawTarget("civil_procedure_evidence", "limitation act 1963", "The Limitation Act, 1963"),
    LawTarget("contract_property", "indian contract act 1872", "The Indian Contract Act, 1872"),
    LawTarget("contract_property", "specific relief act 1963", "The Specific Relief Act, 1963"),
    LawTarget("contract_property", "transfer of property act 1882", "The Transfer of Property Act, 1882"),
    LawTarget("contract_property", "registration act 1908", "The Registration Act, 1908"),
    LawTarget("family_gender", "hindu marriage act 1955", "The Hindu Marriage Act, 1955"),
    LawTarget("family_gender", "special marriage act 1954", "The Special Marriage Act, 1954"),
    LawTarget("family_gender", "protection of women from domestic violence act 2005", "The Protection of Women from Domestic Violence Act, 2005"),
    LawTarget("family_gender", "sexual harassment of women at workplace prevention prohibition and redressal act 2013", "The Sexual Harassment of Women at Workplace Act, 2013"),
    LawTarget("labor_service", "industrial disputes act 1947", "The Industrial Disputes Act, 1947"),
    LawTarget("labor_service", "code on wages 2019", "The Code on Wages, 2019"),
    LawTarget("labor_service", "industrial relations code 2020", "The Industrial Relations Code, 2020"),
    LawTarget("commercial_corporate", "companies act 2013", "The Companies Act, 2013"),
    LawTarget("commercial_corporate", "insolvency and bankruptcy code 2016", "The Insolvency and Bankruptcy Code, 2016"),
    LawTarget("commercial_corporate", "competition act 2002", "The Competition Act, 2002"),
    LawTarget("commercial_corporate", "arbitration and conciliation act 1996", "The Arbitration and Conciliation Act, 1996"),
    LawTarget("commercial_corporate", "consumer protection act 2019", "The Consumer Protection Act, 2019"),
    LawTarget("tax_finance", "income tax act 1961", "The Income-tax Act, 1961"),
    LawTarget("tax_finance", "central goods and services tax act 2017", "The Central Goods and Services Tax Act, 2017"),
    LawTarget("environment_land", "environment protection act 1986", "The Environment (Protection) Act, 1986"),
    LawTarget("environment_land", "air prevention and control of pollution act 1981", "The Air (Prevention and Control of Pollution) Act, 1981"),
    LawTarget("environment_land", "water prevention and control of pollution act 1974", "The Water (Prevention and Control of Pollution) Act, 1974"),
    LawTarget("environment_land", "wild life protection act 1972", "The Wild Life (Protection) Act, 1972"),
    LawTarget("technology_privacy", "information technology act 2000", "The Information Technology Act, 2000"),
    LawTarget("technology_privacy", "digital personal data protection act 2023", "The Digital Personal Data Protection Act, 2023"),
    LawTarget("technology_privacy", "aadhaar targeted delivery of financial and other subsidies benefits and services act 2016", "The Aadhaar Act, 2016"),
    LawTarget("democracy_rights", "representation of the people act 1950", "The Representation of the People Act, 1950"),
    LawTarget("democracy_rights", "representation of the people act 1951", "The Representation of the People Act, 1951"),
    LawTarget("democracy_rights", "legal services authorities act 1987", "The Legal Services Authorities Act, 1987"),
    LawTarget("education_ip", "right of children to free and compulsory education act 2009", "The Right of Children to Free and Compulsory Education Act, 2009"),
    LawTarget("education_ip", "copyright act 1957", "The Copyright Act, 1957"),
    LawTarget("education_ip", "trade marks act 1999", "The Trade Marks Act, 1999"),
    LawTarget("education_ip", "patents act 1970", "The Patents Act, 1970"),
]


CASE_TARGETS: list[CaseTarget] = [
    CaseTarget(
        category="constitutional_admin",
        title="S. R. Bommai v. Union of India",
        year="1994",
        court="Supreme Court of India",
        url="https://api.sci.gov.in/jonew/judis/11570.pdf",
        principle="Federalism, Article 356, and limits on President's Rule.",
    ),
    CaseTarget(
        category="constitutional_admin",
        title="T. S. R. Subramanian v. Union of India",
        year="2013",
        court="Supreme Court of India",
        url="https://api.sci.gov.in/jonew/judis/40943.pdf",
        principle="Civil service independence, fixed tenure, and written directions.",
    ),
    CaseTarget(
        category="technology_privacy",
        title="Justice K. S. Puttaswamy (Retd.) v. Union of India",
        year="2017",
        court="Supreme Court of India",
        url="https://api.sci.gov.in/supremecourt/2012/35071/35071_2012_Judgement_24-Aug-2017.pdf",
        principle="Right to privacy as a fundamental right under Articles 14, 19, and 21.",
    ),
]


TAXONOMY = {
    "constitutional_admin": "Constitutional structure, administrative law, governance, judicial review, and public administration.",
    "criminal": "Criminal offences, investigation, procedure, sentencing, victims, child protection, and criminal justice.",
    "civil_procedure_evidence": "Civil litigation process, limitation, pleadings, evidence, proof, and court procedure.",
    "contract_property": "Contracts, remedies, property transfer, registration, and private-law disputes.",
    "family_gender": "Marriage, domestic violence, gender equality, workplace harassment, and family rights.",
    "labor_service": "Employment, industrial disputes, wages, worker rights, and public-service issues.",
    "commercial_corporate": "Companies, insolvency, competition, arbitration, consumers, and commercial disputes.",
    "tax_finance": "Taxation, revenue, finance, and statutory fiscal obligations.",
    "environment_land": "Environment, pollution, wildlife, forests, land-use, and ecological governance.",
    "technology_privacy": "Technology, cyber law, identity, data protection, privacy, and digital governance.",
    "democracy_rights": "Elections, legal aid, access to justice, public accountability, and democratic rights.",
    "education_ip": "Education rights and intellectual property.",
}


class BrowseParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_row = False
        self.row_text: list[str] = []
        self.row_links: list[str] = []
        self.items: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.in_row = True
            self.row_text = []
            self.row_links = []
        if self.in_row and tag == "a":
            href = dict(attrs).get("href")
            if href and "/handle/123456789/" in href and "view_type=browse" in href:
                self.row_links.append(urllib.parse.urljoin(INDIA_CODE_BASE, href))

    def handle_data(self, data: str) -> None:
        if self.in_row:
            text = data.strip()
            if text:
                self.row_text.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag != "tr" or not self.in_row:
            return
        row = " ".join(self.row_text)
        for href in self.row_links:
            title = title_from_browse_row(row)
            if title:
                self.items.append({"title": title, "url": href})
        self.in_row = False


def title_from_browse_row(row: str) -> str:
    row = re.sub(r"\s+", " ", row).strip()
    row = row.replace("View...", "").strip()
    match = re.match(r"^\d{1,2}-[A-Za-z]{3}-\d{4}\s+\d+\s+(.+)$", row)
    return match.group(1).strip() if match else ""


def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\bthe\b", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def slugify(text: str) -> str:
    text = normalize(text)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:120] or "document"


def fetch_bytes(url: str, timeout: int = 45) -> tuple[bytes, str]:
    result = subprocess.run(
        [
            "curl",
            "--location",
            "--silent",
            "--show-error",
            "--max-time",
            str(timeout),
            "--user-agent",
            USER_AGENT,
            "--write-out",
            "\n__CONTENT_TYPE__:%{content_type}",
            url,
        ],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"curl failed for {url}: {error}")

    marker = b"\n__CONTENT_TYPE__:"
    if marker not in result.stdout:
        return result.stdout, ""
    data, content_type = result.stdout.rsplit(marker, 1)
    return data, content_type.decode("utf-8", errors="replace").strip()


def fetch_text(url: str, timeout: int = 45) -> str:
    data, _ = fetch_bytes(url, timeout=timeout)
    return data.decode("utf-8", errors="replace")


def discover_central_acts(delay: float) -> list[dict[str, str]]:
    seen: set[str] = set()
    items: list[dict[str, str]] = []
    for offset in range(0, 1000, 100):
        print(f"Discovering India Code Central Acts offset={offset}", flush=True)
        html = fetch_text(CENTRAL_ACTS_BROWSE.format(offset=offset))
        parser = BrowseParser()
        parser.feed(html)
        new_items = 0
        for item in parser.items:
            if item["url"] in seen:
                continue
            seen.add(item["url"])
            items.append(item)
            new_items += 1
        if new_items == 0:
            break
        time.sleep(delay)
    print(f"Discovered {len(items)} India Code Central Act entries", flush=True)
    return items


def find_law_match(target: LawTarget, acts: Iterable[dict[str, str]]) -> dict[str, str] | None:
    needle = normalize(target.match)
    candidates = []
    for act in acts:
        title = normalize(act["title"])
        if needle in title:
            candidates.append(act)
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: len(item["title"]))[0]


def parse_act_details(html: str) -> dict[str, str]:
    text = re.sub(r"<[^>]+>", "\n", html)
    text = re.sub(r"\s+", " ", text)
    fields = {}
    for key in ["Act ID", "Act Number", "Enactment Date", "Act Year", "Short Title", "Ministry", "Enforcement Date", "Last Updated"]:
        pattern = rf"{re.escape(key)}:\s*(.*?)(?=Act ID:|Act Number:|Enactment Date:|Act Year:|Short Title:|Hindi Title:|Long Title:|Ministry:|Enforcement Date:|Last Updated:|TitleFiles|Show all section|$)"
        match = re.search(pattern, text)
        if match:
            fields[slugify(key).replace("-", "_")] = match.group(1).strip()
    return fields


def extract_pdf_links(html: str, base_url: str) -> list[str]:
    hrefs = re.findall(r'href=["\']([^"\']+\.pdf(?:\?[^"\']*)?)["\']', html, flags=re.I)
    links = [urllib.parse.urljoin(base_url, href) for href in hrefs]
    return list(dict.fromkeys(links))


def extract_pdf_text(pdf_path: Path) -> str:
    try:
        import pdfplumber

        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return "\n\n".join(page for page in pages if page.strip()).strip()
    except Exception:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(pdf_path))
            return "\n\n".join((page.extract_text() or "") for page in reader.pages).strip()
        except Exception as exc:
            return f"[text extraction failed: {exc}]"


def write_document(
    *,
    url: str,
    title: str,
    category: str,
    folder: Path,
    source_name: str,
    document_type: str,
    extra: dict[str, object],
) -> dict[str, object]:
    folder.mkdir(parents=True, exist_ok=True)
    slug = slugify(title)
    pdf_path = folder / f"{slug}.pdf"
    text_path = folder / f"{slug}.txt"
    row: dict[str, object] = {
        "title": title,
        "document_type": document_type,
        "category": category,
        "jurisdiction": "India",
        "source_name": source_name,
        "source_url": url,
        "local_pdf_path": str(pdf_path.relative_to(DATA_DIR)),
        "local_text_path": str(text_path.relative_to(DATA_DIR)),
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "fetch_status": "pending",
        **extra,
    }

    try:
        if pdf_path.exists() and text_path.exists() and pdf_path.stat().st_size > 0 and text_path.stat().st_size > 0:
            row["fetch_status"] = "ok"
            row["bytes"] = pdf_path.stat().st_size
            row["text_chars"] = text_path.stat().st_size
            row["notes"] = "Reused existing local PDF/text."
            return row

        data, content_type = fetch_bytes(url, timeout=120)
        pdf_offset = data.find(b"%PDF")
        if pdf_offset == -1 or pdf_offset > 4096:
            row["fetch_status"] = "skipped_non_pdf"
            row["notes"] = f"Expected PDF but got content type {content_type!r}."
            return row
        if pdf_offset > 0:
            data = data[pdf_offset:]
        pdf_path.write_bytes(data)
        extracted_text = extract_pdf_text(pdf_path)
        text_path.write_text(extracted_text + "\n", encoding="utf-8")
        row["fetch_status"] = "ok" if extracted_text and not extracted_text.startswith("[text extraction failed") else "pdf_ok_text_failed"
        row["bytes"] = len(data)
        row["text_chars"] = len(extracted_text)
    except Exception as exc:
        row["fetch_status"] = "error"
        row["notes"] = str(exc)
    return row


def write_context_files(manifest_rows: list[dict[str, object]]) -> None:
    context_dir = DATA_DIR / "context"
    context_dir.mkdir(parents=True, exist_ok=True)
    (context_dir / "legal_taxonomy.json").write_text(
        json.dumps(TAXONOMY, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    sources = """# Legal Corpus Sources

This starter corpus is built for RabbitHole Courtroom RAG experiments.

## Used

- India Code: official Indian statute portal. Central Acts are browsed from `https://www.indiacode.nic.in/handle/123456789/1362/browse?type=shorttitle`, and PDFs are fetched from direct India Code bitstream links.
- Supreme Court of India direct PDFs: selected landmark judgments are fetched from `https://api.sci.gov.in/...` direct PDF URLs.

## Not Bulk Scraped

- eCourts Judgments (`https://judgments.ecourts.gov.in/`) is official, but search is CAPTCHA-gated. This corpus does not bypass that CAPTCHA.

## Notes

- This is a starter balanced corpus, not a complete database of Indian law.
- `context/manifest.jsonl` is the source of truth for provenance and local file paths.
"""
    (context_dir / "sources.md").write_text(sources, encoding="utf-8")

    manifest_path = context_dir / "manifest.jsonl"
    with manifest_path.open("w", encoding="utf-8") as handle:
        for row in manifest_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    precedent_rows = [
        row
        for row in manifest_rows
        if row.get("document_type") == "case" and row.get("is_precedent") is True
    ]
    precedent_path = DATA_DIR / "precedents" / "landmark_index.jsonl"
    precedent_path.parent.mkdir(parents=True, exist_ok=True)
    with precedent_path.open("w", encoding="utf-8") as handle:
        for row in precedent_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def fetch_laws(delay: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    acts = discover_central_acts(delay)
    for target in LAW_TARGETS:
        print(f"Fetching law target: {target.title}", flush=True)
        match = find_law_match(target, acts)
        if not match:
            rows.append({
                "title": target.title,
                "document_type": "law",
                "category": target.category,
                "jurisdiction": "India",
                "source_name": "India Code",
                "source_url": "",
                "local_pdf_path": "",
                "local_text_path": "",
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "fetch_status": "not_found_in_browse",
                "notes": target.notes or f"No Central Act browse match for {target.match!r}.",
            })
            continue

        time.sleep(delay)
        html = fetch_text(match["url"])
        details = parse_act_details(html)
        pdf_links = extract_pdf_links(html, match["url"])
        if not pdf_links:
            rows.append({
                "title": match["title"],
                "document_type": "law",
                "category": target.category,
                "jurisdiction": "India",
                "source_name": "India Code",
                "source_url": match["url"],
                "local_pdf_path": "",
                "local_text_path": "",
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "fetch_status": "missing_pdf_link",
                "notes": "India Code item page found, but no PDF link was parsed.",
                **details,
            })
            continue

        row = write_document(
            url=pdf_links[0],
            title=match["title"],
            category=target.category,
            folder=DATA_DIR / "laws" / target.category,
            source_name="India Code",
            document_type="law",
            extra={
                "item_url": match["url"],
                "target_title": target.title,
                **details,
            },
        )
        rows.append(row)
        time.sleep(delay)
    return rows


def fetch_cases(delay: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target in CASE_TARGETS:
        print(f"Fetching case target: {target.title}", flush=True)
        row = write_document(
            url=target.url,
            title=target.title,
            category=target.category,
            folder=DATA_DIR / "cases" / target.category,
            source_name=target.court,
            document_type="case",
            extra={
                "court": target.court,
                "year": target.year,
                "is_precedent": True,
                "principle": target.principle,
                "notes": target.notes,
            },
        )
        rows.append(row)
        time.sleep(delay)
    return rows


def validate_manifest(rows: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("fetch_status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
        if status in {"ok", "pdf_ok_text_failed"}:
            for key in ["local_pdf_path", "local_text_path"]:
                local_path = row.get(key)
                if local_path and not (DATA_DIR / str(local_path)).exists():
                    row["fetch_status"] = "validation_missing_local_file"
                    row["notes"] = f"Missing local file referenced by {key}: {local_path}"
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delay", type=float, default=0.25, help="Delay between source requests in seconds.")
    parser.add_argument("--laws-only", action="store_true", help="Only fetch laws.")
    parser.add_argument("--cases-only", action="store_true", help="Only fetch cases.")
    args = parser.parse_args()

    if args.laws_only and args.cases_only:
        raise SystemExit("--laws-only and --cases-only cannot both be set")

    for folder in ["laws", "cases", "precedents", "context", "incentives"]:
        (DATA_DIR / folder).mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    if not args.cases_only:
        rows.extend(fetch_laws(args.delay))
    if not args.laws_only:
        rows.extend(fetch_cases(args.delay))

    counts = validate_manifest(rows)
    write_context_files(rows)
    print(json.dumps({"data_dir": str(DATA_DIR), "documents": len(rows), "statuses": counts}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
