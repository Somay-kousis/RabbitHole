# Legal Corpus Sources

This starter corpus is built for RabbitHole Courtroom RAG experiments.

## Used

- India Code: official Indian statute portal. Central Acts are browsed from `https://www.indiacode.nic.in/handle/123456789/1362/browse?type=shorttitle`, and PDFs are fetched from direct India Code bitstream links.
- Supreme Court of India direct PDFs: selected landmark judgments are fetched from `https://api.sci.gov.in/...` direct PDF URLs.

## Not Bulk Scraped

- eCourts Judgments (`https://judgments.ecourts.gov.in/`) is official, but search is CAPTCHA-gated. This corpus does not bypass that CAPTCHA.

## Notes

- This is a starter balanced corpus, not a complete database of Indian law.
- `context/manifest.jsonl` is the source of truth for provenance and local file paths.
