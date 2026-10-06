# External system integration boundary

## ULII
ULII is the Uganda Judiciary's public legal-information service and provides judgments, legislation, gazettes and other public legal material. It is also an end-user interface for ECCMIS. The platform must treat ULII as an external research source, not copy its database into A1OS. ULII's terms prohibit scraping and bulk downloading, so the first production integration is controlled deep-link/search assistance and citation capture rather than scraping.

Official source: https://ulii.org/

## ECCMIS
ECCMIS is the Uganda Judiciary's electronic court case management system covering case lifecycle functions including electronic filing, service and related court processes. A1OS remains the firm's internal system of record and must not impersonate or replace ECCMIS. Court actions should be represented as external references, filing metadata, receipts and status evidence until an authorized integration/API is available.

Official source: https://www.judiciary.go.ug/data/smenu/143/1/About%20ECCMIS.html

## Integration rules
1. Never store external credentials in the frontend.
2. Never automate court submissions without an explicit authorized connector and governed approval.
3. Preserve source URL, retrieval time and citation metadata for research records.
4. Keep internal matter confidentiality separate from public legal research.
5. AI may assist research and drafting; it cannot represent a court filing as submitted unless the external system confirms it.
