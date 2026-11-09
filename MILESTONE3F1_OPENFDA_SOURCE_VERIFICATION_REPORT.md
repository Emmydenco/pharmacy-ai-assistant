# Milestone 3F.1 — openFDA Source Permission and Record Verification Report

## Research date

2026-11-05. This was a research-only assessment. No application code was modified, no source-registry approval state was changed, and no medication content was added to the project knowledge base.

## Official sources examined

The assessment used the following official sources:

- openFDA Terms of Service and Data Rights and Usage.[1]
- openFDA Data Licensing / CC0 explanation.[2]
- openFDA Structured Product Labeling dataset description.[3]
- openFDA Drug Labeling API overview.[4]
- openFDA API overview and response structure.[5]
- openFDA authentication and rate-limit documentation.[6]
- openFDA endpoint usage and query documentation.[7] [8]
- FDA Structured Product Labeling resources.[9]
- FDA website policies for copying and linking FDA-authored website content.[10]
- The official DailyMed record page for the selected SPL set ID.[11]

A single minimal openFDA API lookup was made with `limit=1` to identify a candidate record. The endpoint returned a full JSON record, including label sections, because the endpoint does not provide a field-selection parameter in the documented request used here. The response was not saved to the repository, was not copied into application files, was not indexed, and no clinical label wording is reproduced in this report. No further label-content request was made.

## Dataset permission assessment

### Viewing and linking

Viewing the openFDA documentation and API output is permitted subject to the openFDA terms. FDA website policy also says that people may link to FDA URLs and that FDA prefers linking to the current source rather than copying it.[10] Linking to the openFDA dataset and the exact DailyMed record is therefore the least-risk use identified in this assessment.

### Downloading, extracting, transforming, internal storage, and indexing

The openFDA terms state that, unless otherwise noted, openFDA content, data, documentation, code, and related materials are public domain under a CC0 1.0 dedication. The terms also expressly warn that some data may not be public domain, including copies of copyrightable works supplied to FDA by private entities. Those works may be available under fair use or regulatory directives, and the terms state that the relevant rights may be similarly limited.[1] [2]

The SPL documentation says that drug manufacturers and distributors submit the labeling to FDA and that the API returns data from those submissions.[3] The drug-label API documentation further states that the label text is reformatted for readability, has not been altered or verified by FDA, and may not be the currently distributed or identical approved labeling.[4]

Accordingly, the general CC0 statement is a strong basis for reuse of FDA-authored openFDA documentation and data fields where no exception applies. It is not sufficient by itself to establish that every field or embedded label passage can be extracted, transformed, stored, indexed, or reproduced. The terms require field- or record-level caution where private or third-party material is involved.

### AI-assisted retrieval and generated summaries

The openFDA terms allow copying, modifying, distributing, and performing public-domain material, but they do not convert privately supplied copyrighted works into unrestricted material. An internal retrieval index and AI-generated summary would be derivative uses of the record content. Those uses are acceptable only for content whose rights are established, with third-party exclusions respected. The openFDA API page also warns users not to rely on the data for medical-care decisions.[4] That warning is a safety and quality limitation, not a licence grant.

### User-facing reproduction and redistribution

FDA-authored public-domain metadata may be cited and reused with no mandatory attribution under the CC0 statement, although openFDA asks users to give proper credit and provides the suggested attribution “Data provided by the U.S. Food and Drug Administration.”[1] [2] For the selected label, user-facing reproduction of label text remains unresolved because the record contains manufacturer-submitted and branded material. The safest current approach is linking and retaining metadata only, not reproducing label passages.

### API conditions and limits

The official authentication page reports standard limits of 240 requests per minute and 1,000 requests per day per IP address without an API key, and 240 requests per minute and 120,000 requests per day per API key.[6] It also requires HTTPS and describes the `api_key` query parameter or Basic Auth alternative. The endpoint usage page says an API key is recommended for regular use and that a query normally returns one record unless `limit` is specified.[7] These two pages are slightly inconsistent about whether a key is strictly required; the operationally conservative choice is to use an official API key for regular service use, keep it server-side, and remain within documented limits.

The documented drug-label endpoint is `https://api.fda.gov/drug/label.json`. It supports field searches such as `search=field:term`, `limit`, and the documented query syntax. The maximum `limit` for one call is 1,000.[7] The API response contains `meta` and `results` sections, including a terms URL, licence URL, last-updated date, and result count.[5]

## Candidate medication record

The candidate was chosen as a technical record-verification example, not because it establishes Nigerian suitability:

- **Generic name:** ACETAMINOPHEN.
- **Brand name:** Pain Reliever Extra Strength.
- **Active ingredient and strength:** Acetaminophen 500 mg.
- **Dosage form:** DailyMed identifies the label as an acetaminophen tablet, coated; the OTC label presentation describes gelcaps. The exact product presentation must therefore be preserved rather than normalized casually.
- **Route:** ORAL.
- **Labeler:** Valu Merchandisers Company.
- **Set ID:** `0005aafa-08f8-4990-a54d-cc097195708f`.
- **SPL record ID:** `ee8e3aa2-8550-41c7-9911-0723b3fb2f87`.
- **Application / monograph identifier:** `M013`.
- **Product NDCs:** `63941-519-12` and `63941-519-15`.
- **Label revision/effective date:** `20260102` / January 2, 2026.
- **API record URL:** `https://api.fda.gov/drug/label.json?search=openfda.generic_name%3Aacetaminophen&limit=1`.
- **Exact record lookup URL for future verification:** `https://api.fda.gov/drug/label.json?search=set_id%3A0005aafa-08f8-4990-a54d-cc097195708f&limit=1`.
- **Original/record-level label URL:** `https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0005aafa-08f8-4990-a54d-cc097195708f`.
- **Record update date:** DailyMed reports January 2, 2026; the openFDA response metadata reported `last_updated` as 2026-11-05.
- **Jurisdiction:** United States FDA/DailyMed context.
- **Record retrieval date:** 2026-11-05.

The record identifiers are suitable for provenance: set ID identifies the label set, SPL record ID identifies the returned record, version and effective time identify the revision, and NDC/application fields identify the product context.

## Record-level rights assessment

The record is not FDA-authored clinical text in the ordinary sense. It is a Structured Product Labeling submission from a manufacturer or distributor, exposed through an FDA-maintained API and DailyMed interface. The selected record contains manufacturer product wording, branded references, pack-display content, and a reference to another trademark owner. The DailyMed page identifies the packager and provides links to PDF/XML label downloads, but it does not, on the page reviewed, grant a blanket licence for copying the full record into an AI index or reproducing its contents in a user-facing assistant.[11]

The general openFDA terms warn that privately supplied copyrightable works may be outside CC0.[1] [2] The drug-label documentation also warns that the API content is reformatted and unverified by FDA and may not be identical to currently approved or distributed labeling.[4] These facts prevent treating the candidate’s full label text as automatically reusable or as verified product information.

The candidate is therefore rejected for controlled label-text ingestion at this stage. The metadata-only elements needed to link to the record may be retained as a research note, but no clinical text should enter the internal index until the specific record’s rights and intended use are confirmed.

## Nigerian pharmacy relevance and limitations

This record is U.S.-jurisdiction product labeling. It does not establish:

- NAFDAC registration or authorization in Nigeria;
- Nigerian availability, formulation, strength, pack size, or labeling;
- Nigerian dispensing or pharmacy-practice requirements;
- Nigerian warnings, language, or approved patient information; or
- patient-specific suitability, diagnosis, dose selection, interaction management, or treatment advice.

A U.S. FDA label must not be presented as Nigerian-approved product information. Any future use would need an explicit jurisdiction label and a separate Nigerian source check. The prior Milestone 3C research identified NAFDAC as the primary source for Nigerian product-regulatory status, but NAFDAC Greenbook permissions remained unresolved in Milestone 3F. No claim about this product’s Nigerian registration is made here.

## Technical feasibility

The openFDA architecture is technically suitable for a narrow, metadata-first connector:

- **Endpoint:** `https://api.fda.gov/drug/label.json`.
- **Search:** `search=field:term`, with documented field syntax and date/range examples.
- **Identifiers:** `set_id`, record `id`, `effective_time`, `version`, application number, NDC, and harmonized `openfda` fields.
- **Response:** JSON with `meta` and `results`.
- **Pagination/volume controls:** `limit` and documented query controls; maximum one-call limit 1,000. A future connector should use the smallest possible limit and must not bulk crawl.
- **Update frequency:** Weekly for the drug-label API.[4]
- **API key:** Recommended for regular use; key must be server-side and never placed in frontend assets.
- **Rate limits:** 240 requests/minute and 120,000 requests/day per key under the standard limits.[6]
- **Error handling:** A future connector must treat non-2xx responses, rate limits, malformed JSON, missing result records, and changed schema as fail-closed ingestion errors. No such connector was implemented in this milestone.
- **Provenance:** The selected identifiers and revision fields are adequate for a proposed source-linked record, subject to rights approval and exact-record verification.

The API is technically feasible for one-record retrieval, but technical feasibility does not establish legal permission, Nigerian relevance, clinical accuracy, or production readiness.

## Proposed SourceRecord — not activated

The following is a proposed governance record only. It was **not** registered or approved in the application:

- **source_id:** `openfda-drug-labels-us-spl`
- **source_name:** openFDA Drug Product Labeling / Structured Product Labeling
- **publisher:** U.S. Food and Drug Administration (FDA), with labeling submissions from manufacturers/distributors
- **official_url:** `https://open.fda.gov/apis/drug/label/`
- **api_url:** `https://api.fda.gov/drug/label.json`
- **dataset:** Drug Product Labeling / SPL
- **jurisdiction:** United States; not Nigerian authorization evidence
- **authority level:** `primary` for FDA data publication and U.S. label context; not primary for Nigerian registration or local product information
- **linking:** `confirmed_permitted` for linking to official FDA/openFDA/DailyMed pages based on the cited official linking guidance, subject to current terms
- **downloading:** `permission_required` at record level because the dataset includes privately submitted or third-party material
- **extraction:** `permission_required`
- **internal indexing:** `permission_required` — deliberately not approved
- **reproduction:** `permission_required`
- **public accessibility:** `confirmed_permitted`
- **licence basis:** openFDA CC0 statement for material not otherwise noted; record-level exceptions remain applicable
- **attribution:** Credit FDA/openFDA and link to the exact record; do not imply FDA endorsement; preserve third-party notices and attribution if rights are later confirmed
- **verification date:** 2026-11-05
- **review status:** `draft`
- **unresolved issues:** record-level rights for manufacturer-submitted label text; third-party trademarks and embedded material; whether intended internal indexing and user-facing summaries are permitted; U.S. versus Nigerian applicability; currentness and exact-label matching

The distinction is explicit: the candidate may be suitable for **approved linking and metadata use**, but it is not **approved for internal indexing**.

## Final suitability classification

**Classification: C — Permission or rights remain unresolved.**

The candidate is technically suitable for a future controlled metadata/linking connector. Full label ingestion, internal indexing, RAG use, and user-facing reproduction should not proceed until the exact record’s rights and intended use are resolved. The record is not suitable as Nigerian-approved medication information.

## Recommendation for the next milestone

Do not ingest this candidate yet. The next step should be a human-reviewed rights decision for the exact record or a source-selection change to a dataset with explicit record-level reuse terms. If approved later, begin with metadata and a single short, pharmacist-reviewed passage only after recording the exact permission basis, then run the existing source registry, approval, provenance, retrieval, claim-support, and final source-governance tests. Do not weaken any safety boundary and do not imply clinical correctness.

Pharmacist review and legal/licensing review remain required. This report makes no claim of clinical validation, medical correctness, regulatory compliance, legal compliance, or production readiness.

## References

[1]: https://open.fda.gov/terms/ "openFDA Terms of Service"
[2]: https://open.fda.gov/license "openFDA Data Licensing"
[3]: https://open.fda.gov/data/spl/ "openFDA Structured Product Labeling dataset"
[4]: https://open.fda.gov/apis/drug/label/ "openFDA Drug Labeling API overview"
[5]: https://open.fda.gov/apis/ "About the openFDA API"
[6]: https://open.fda.gov/apis/authentication/ "openFDA API authentication and rate limits"
[7]: https://open.fda.gov/apis/drug/label/how-to-use-the-endpoint/ "How to use the openFDA Drug Labeling endpoint"
[8]: https://open.fda.gov/apis/drug/label/example-api-queries/ "openFDA Drug Labeling example queries"
[9]: https://www.fda.gov/industry/fda-data-standards-advisory-board/structured-product-labeling-resources "FDA Structured Product Labeling Resources"
[10]: https://www.fda.gov/about-fda/about-website/website-policies "FDA Website Policies"
[11]: https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0005aafa-08f8-4990-a54d-cc097195708f "DailyMed record for the selected SPL set ID"
