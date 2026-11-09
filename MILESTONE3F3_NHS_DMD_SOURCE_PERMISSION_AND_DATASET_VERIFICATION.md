# Milestone 3F.3 — NHS dm+d Source Permission and Dataset Verification

**Research checked:** 6 November 2026  
**Project:** Pharmacy Patient Assistant, initially targeting community pharmacies in Nigeria  
**Scope:** Research-only source-permission and dataset verification  
**Status:** No application code changed. No source was approved in the registry. No runtime knowledge-base content was added. No bulk release was downloaded or ingested. No live Cloudflare request was made.

## Executive summary

The exact candidate reviewed is the NHSBSA/TRUD item **“dm+d in a vendor-neutral format,” TRUD item number 24, pack 6 / subpack 24, Release 11.0.0, Week 45, released 2 November 2026**. The public TRUD item page explicitly states that releases of this item are covered by the **Open Government Licence for TRUD**. The Open Government Licence v3 permits copying, publishing, distributing, transmitting, adapting, and commercial or non-commercial exploitation, subject to attribution and exclusions.[1] [2]

This is strong evidence that the identified TRUD item is intended for reuse under OGL. It is not enough to approve the entire release file without further inspection. OGL excludes personal data, third-party rights that the information provider is not authorised to license, logos and other excluded intellectual-property rights. The public pages reviewed do not expose the exact Release 11.0.0 archive manifest, checksums, internal file list, or field-level rights declarations. Because this milestone prohibits bulk downloading, those questions remain unresolved.

**Final classification: C — PERMISSION OR DATASET COVERAGE UNRESOLVED.** The proposed source is not approved for ingestion in this milestone. A later Milestone 3G may request approval for a narrowly defined field subset only after obtaining the exact release through the authorised TRUD process, verifying its manifest and excluded components, and completing pharmacist/source-governance review.

The appropriate internal source class is **TERMINOLOGY / PRODUCT-IDENTITY SOURCE**, not **CLINICAL-MEDICATION-EVIDENCE SOURCE**. NHS dm+d provides identifiers, descriptions, product structures, and related operational information for the NHS. NHS documentation explicitly says that dm+d is not a decision-support system.[3] It must not be used as evidence for indications, contraindications, warnings, adverse effects, dosing or treatment recommendations, counselling claims, patient-specific advice, or Nigerian regulatory status.

## 1. Exact candidate release

| Field | Verified value | Evidence and limitation |
|---|---|---|
| Dataset name | NHSBSA dm+d — “dm+d in a vendor-neutral format” | Official TRUD release and licence pages.[4] [5] |
| TRUD item number | **24** | The official releases URL contains `/subpack/24/releases`; the licence URL contains `/items/24/licences`.[4] [5] |
| TRUD pack/subpack | Pack **6**, subpack **24** | Reflected in the official TRUD release URL.[4] |
| Exact release | **Release 11.0.0** | Official TRUD release list.[4] |
| Week | **Week 45** | Official TRUD release list.[4] |
| Release date | **2 November 2026** | The official release listing/search result identifies Release 11.0.0 as released on 2 November 2026. The public extracted release page exposes the release name and week but not the date in its text output; the NHSBSA schedule page confirms the weekly release mechanism.[4] [6] |
| Release identifier | **11.0.0 / Week 45** | This is the public release identifier. A machine download ID or archive filename is not exposed on the public release page without an authenticated release listing response. |
| Download/resource identifier | **TRUD item 24**; authenticated API resource would be the item-24 release file | The TRUD API documentation states that item numbers identify resources and that the release-list response supplies the archive filename, download URL, checksum, signature, and size. No API key was used here.[7] |
| File format | XML dm+d release; the weekly subpack also includes the dm+d TRUD release schedule and an AMPP-to-GTIN mapping file | Official NHSBSA release page.[6] |
| Publisher/maintainer | NHS Business Services Authority, with support from NHS England on behalf of DHSC | Official NHSBSA overview.[8] |
| Source jurisdiction | United Kingdom, specifically NHS medicines terminology used across NHS systems | Official NHS description and standard scope.[3] [8] |
| Official source URL | `https://isd.digital.nhs.uk/trud/user/guest/group/0/pack/6/subpack/24/releases` | Official release list.[4] |
| Official licence URL | `https://isd.digital.nhs.uk/trud/users/guest/filters/0/categories/6/items/24/licences` | Official item licence page.[5] |
| General licence text | `https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/` | Official OGL v3 text.[2] |
| Documentation check date | **6 November 2026** | This report’s research date. |

The exact archive filename, SHA-256 checksum, signed manifest, and internal XML file list are intentionally not recorded as verified values because obtaining them requires the authenticated TRUD release-list API or a release download. This report does not invent those identifiers.

## 2. Official sources examined

The following official sources were read on 6 November 2026:

1. NHS TRUD release list for item 24, which identifies Release 11.0.0 and Week 45.[4]
2. NHS TRUD item-licence page for item 24, which attaches the Open Government Licence for TRUD to the releases of this item and requires an open TRUD account to use the content.[5]
3. NHSBSA “Release of dm+d files,” which describes the weekly dm+d subpack, XML format, the TRUD release schedule, and the AMPP-to-GTIN mapping.[6]
4. NHSBSA dm+d overview, which describes the publisher, weekly refresh, product scope, identifiers, suppliers, pricing, availability, SNOMED CT, BNF, and GTIN-related content.[8]
5. NHS Digital dm+d overview, which describes the vocabulary, identifiers, seven concept classes, raw XML distribution through TRUD, and the explicit statement that dm+d is not a decision-support system.[3]
6. NHS TRUD “Using the API,” which documents authenticated release listing, download links, checksums, signatures, account/API-key requirements, and automated-download timing guidance.[7]
7. Open Government Licence v3, which defines reuse rights, attribution, commercial use, adaptation, redistribution, non-endorsement, warranty limitations, and exclusions.[2]
8. NHSBSA dm+d implementation guidance, used to verify the meaning of VTM, VMP, VMPP, AMP, AMPP, identifiers, strengths, forms, routes, and relationships.[9]

## 3. Licence verification

### What is established

The TRUD item page names the item **NHSBSA dm+d — dm+d in a vendor-neutral format** and lists **Open Government Licence for TRUD** under “Licences applied to this item.” It states that the content within releases of items having this licence may be used under the OGL terms. The same page says users must have an open TRUD account to use the content and recommends recording how and where the content is used so that updated content can be managed.[5]

OGL v3 grants a worldwide, royalty-free, perpetual, non-exclusive licence for information expressly made available under the licence. It allows copying, publishing, distributing, transmitting, adapting, and commercial or non-commercial exploitation.[2] It requires acknowledgement of the source and, where possible, a link to the licence. If no provider-specific attribution statement is supplied, the default statement is: “Contains public sector information licensed under the Open Government Licence v3.0.”[2]

### What remains unresolved

The licence page establishes the licence attached to the **TRUD item**, but it does not expose the contents of the exact Release 11.0.0 archive. The following questions therefore remain unresolved without the authorised release file and its metadata:

- Whether every file in Release 11.0.0 is entirely covered by the OGL item licence.
- Whether any linked or embedded SNOMED CT, BNF, GTIN, trademark, logo, personal-data, or other third-party component is subject to separate rights.
- Whether the proposed derived fields can be isolated without copying excluded content.
- Whether the AMPP-to-GTIN mapping file has any additional rights or provider-specific restrictions.
- Whether a future derived product may redistribute the selected records in the proposed user-facing format while preserving all required attributions and exclusions.

These are not claims that excluded material is present. They are verification gaps created by the no-download boundary.

### Licence conclusions by question

| Question | Classification | Official basis and limitation |
|---|---|---|
| Is the exact TRUD item assigned an explicit licence? | **VERIFIED** | The item-24 licence page explicitly assigns the Open Government Licence for TRUD to releases of the item.[5] |
| Is Release 11.0.0 itself identified? | **VERIFIED** | The public release page identifies Release 11.0.0, Week 45; the release date is 2 November 2026.[4] |
| Is the entire archive file covered without exclusions? | **UNRESOLVED** | The item page assigns OGL to releases, but OGL excludes third-party rights and other listed categories. The archive manifest was not inspected.[2] [5] |
| Are derivatives permitted? | **VERIFIED in principle** | OGL permits adaptation and technically necessary format changes, subject to exclusions and attribution.[2] |
| Is commercial use permitted? | **VERIFIED in principle** | OGL expressly permits commercial and non-commercial exploitation of covered information.[2] |
| Is redistribution permitted? | **VERIFIED in principle** | OGL permits copying, publishing, distributing, and transmitting covered information, subject to attribution and exclusions.[2] |
| Are attribution and non-endorsement requirements known? | **VERIFIED** | OGL requires acknowledgement and prohibits suggesting official endorsement.[2] |
| Are third-party and excluded components cleared? | **UNRESOLVED** | OGL excludes rights the provider is not authorised to license, plus personal data, logos, trademarks, and other rights. Exact release contents were not inspected.[2] |
| Is a TRUD account required? | **VERIFIED** | The item licence page says an open TRUD account is required; the API also requires an account API key for automated downloads.[5] [7] |

## 4. Permission matrix for intended activities

The matrix applies only to the exact candidate item and proposed field subset. “Verified” means the official terms support the activity for covered content. It is not blanket approval of every record, file, or component.

| Intended activity | Classification | Basis |
|---|---|---|
| Downloading Release 11.0.0 | **VERIFIED, operationally conditional** | TRUD exposes release downloads to subscribed account holders and provides an authenticated API for release files. The item requires an open account. The project has not downloaded the release in this milestone.[5] [7] |
| Extracting selected terminology fields | **VERIFIED in principle, field coverage unresolved** | OGL permits adaptation and reuse of covered information. Exact archive contents and excluded components still require inspection.[2] |
| Transforming/normalizing selected fields | **VERIFIED in principle, field coverage unresolved** | OGL permits adapting covered information; attribution and exclusions continue to apply.[2] |
| Storing derived records internally | **VERIFIED in principle, field coverage unresolved** | Storage is a practical form of copying/use permitted for covered information under OGL; this is not an approval of excluded components.[2] |
| Indexing records for retrieval | **VERIFIED in principle, field coverage unresolved** | OGL permits adaptation and inclusion in an application; the exact selected fields must be confirmed as covered.[2] |
| Using records in a RAG pipeline | **VERIFIED in principle, field coverage unresolved** | RAG is an internal application use of derived covered information, but it must retain provenance, attribution, jurisdiction, and exclusions. OGL does not establish clinical appropriateness.[2] |
| Generating summaries or derived responses | **VERIFIED in principle, field coverage unresolved** | Adaptation and application use are permitted for covered information; outputs must not imply NHS endorsement and must not turn terminology into clinical advice.[2] |
| Displaying derived terminology to users | **VERIFIED in principle, field coverage unresolved** | OGL permits publication and distribution of covered information with attribution; user-facing display must clearly state UK scope and terminology-only role.[2] |
| Redistributing derived terminology | **VERIFIED in principle, field coverage unresolved** | OGL permits distribution and transmission of covered information; exact record and third-party exclusions must be checked first.[2] |
| Commercial use | **VERIFIED in principle, field coverage unresolved** | OGL expressly permits commercial exploitation of covered information; excluded components and any separate terms remain outside that permission.[2] |

Because the exact file contents were not inspected, every “in principle” classification remains conditional and does not approve ingestion. The source remains **C** until the field-level and archive-level checks are completed.

## 5. Proposed field-level assessment

The first useful subset should be deliberately small and terminology-focused. It should not include pricing, reimbursement, clinical decision-support flags, or narrative product information unless a later review shows a specific need and rights basis.

| Proposed field | Meaning | Required for terminology use case? | Licence status | Third-party risk | Store/index? | Direct user display? |
|---|---|---:|---|---|---:|---|
| VTM identifier and description | Virtual Therapeutic Moiety: ingredient or combination-level therapeutic concept and its name | Yes for generic/ingredient normalization | OGL coverage of exact field **UNRESOLVED until release inspection** | Low-to-medium; exact source provenance needed | Yes, if verified | Yes, with source/jurisdiction label |
| VMP identifier and description | Virtual Medicinal Product: generic product concept including form and strength | Yes | **UNRESOLVED until release inspection** | Low-to-medium | Yes, if verified | Yes, as terminology only |
| VMPP identifier and description | Virtual Medicinal Product Pack: generic product pack concept and pack size | Optional for first slice; useful for pack normalization | **UNRESOLVED until release inspection** | Low-to-medium | Prefer defer in first slice unless required | Only when needed to explain identity |
| AMP identifier and description | Actual Medicinal Product: actual branded/manufactured product concept | Yes for product-name matching, but UK-specific | **UNRESOLVED until release inspection** | Medium because supplier-provided product information may be represented | Yes only after field review | Yes with “UK terminology; not Nigerian approval” |
| AMPP identifier and description | Actual Medicinal Product Pack: actual pack-level product | Optional for first slice | **UNRESOLVED until release inspection** | Medium | Defer unless pack lookup is required | Prefer not in first user-facing slice |
| Product-to-ingredient relationship | Links products to VTM/ingredient concepts | Yes | **UNRESOLVED until release inspection** | Low-to-medium | Yes, if verified | Usually indirect; show normalized ingredient name rather than raw relationship |
| Product-to-strength relationship | Represents strength and numerator/denominator units | Yes for identity normalization; not a dose recommendation | **UNRESOLVED until release inspection** | Low-to-medium | Yes, if verified | Display only as product identity, never as patient-specific dosing advice |
| Form identifier/description | Dose form such as tablet or solution | Yes | **UNRESOLVED until release inspection** | Low | Yes, if verified | Yes as identity metadata |
| Route identifier/description | Route associated with the product where present | Useful but not essential for first slice | **UNRESOLVED until release inspection** | Low-to-medium | Defer unless exact semantics are confirmed | Do not display as advice without pharmacist review |
| Product identifier/code system | Persistent concept identifier and code system | Yes for provenance and deduplication | **UNRESOLVED until release inspection** | Low | Yes | Usually show as provenance, not as a patient-facing code |
| Release/version metadata | Release number, week, release date, publisher, licence URL | Yes for reproducibility | **VERIFIED for release metadata; archive details pending** | Low | Yes on every record/chunk | Show source date/version when relevant |
| AMPP-to-GTIN mapping | Link between packs and global trade-item identifiers | No for first terminology slice | **UNRESOLVED** | Medium; supplier/identifier rights and scope need review | No initially | No |
| Price/reimbursement/availability fields | NHS reimbursement, price, availability, tariff-related data | No; out of scope and jurisdiction-specific | **UNRESOLVED for proposed use** | Medium-to-high | No | No |

### Fields explicitly excluded

The first ingestion must exclude all information that could be mistaken for clinical evidence or Nigerian regulatory evidence. In particular, do not ingest or index indications, contraindications, warnings, adverse effects, dosing instructions, treatment recommendations, storage or counselling claims, patient-specific recommendations, NAFDAC status, or Nigerian availability. The source documentation does not make dm+d a clinical monograph or decision-support system.[3]

## 6. Terminology is not clinical evidence

NHS dm+d should be registered, if ever approved, as:

> **Source type:** TERMINOLOGY / PRODUCT-IDENTITY SOURCE

It must not be registered as:

> **Source type:** CLINICAL-MEDICATION-EVIDENCE SOURCE

The source can help answer questions such as “What normalized product or ingredient identity is associated with this UK dm+d code?” It cannot establish:

- indications;
- contraindications;
- warnings;
- adverse effects;
- dosing recommendations;
- treatment recommendations;
- patient-specific medication advice;
- storage or counselling claims; or
- Nigerian regulatory status.

In the existing governed architecture, this distinction should be represented by a source-type value and by permitted-evidence capabilities. A future `SourceRecord` should allow terminology sources to be retrievable for identity and normalization tasks while preventing their passages from satisfying clinical-evidence requirements. Any clinical chat route should continue to require an evidence bundle whose source class supports the requested factual claim. This report does not add or approve that record.

## 7. Third-party and excluded-content assessment

The OGL exclusions matter even though the exact TRUD item is OGL-labelled. OGL does not cover personal data, third-party rights the information provider is not authorised to license, logos, crests, Royal Arms, military insignia, patents, trademarks, design rights, or identity documents.[2]

The public NHS pages describe dm+d as containing or linking to information such as Drug Tariff reimbursement, product availability, pricing, SNOMED CT, BNF, and GTINs.[8] The presence of these categories does not prove that each field has identical rights. The proposed first slice should therefore avoid supplementary files and fields that are not necessary for product identity until the archive manifest and field provenance are reviewed.

The most important unresolved component questions are:

1. Does Release 11.0.0 contain only the item-24 dm+d XML and its stated mapping/schedule files, or does it bundle material with separate rights?
2. Are SNOMED CT identifiers or descriptions included in the exact file, and if so, under what component-specific terms?
3. Are BNF, GTIN, pricing, reimbursement, and availability fields covered by the same item-level OGL permission for the proposed derived use?
4. Are manufacturer/supplier names, product descriptions, trademarks, or logos present, and if so, are they covered or excluded?
5. Does the archive contain any personal data or other fields unnecessary for terminology normalization?

## 8. TRUD access and update terms

### Account and subscription

The item-24 licence page states that users must have an open TRUD account to use the content. The TRUD API documentation states that automated release listing and downloads are available to account holders for items to which they are subscribed. An account API key is generated from the account credentials, and the documentation warns that the key must remain private.[5] [7]

No project TRUD account, API key, or credential was requested or configured in this milestone. No credential was printed, stored, or exposed.

### Automated downloads

TRUD documents two API endpoints: one lists releases and one downloads a release file using a URL from the release-list response. The response can provide an archive filename, release date, file size, SHA-256 checksum, signature file, and public-key information.[7] This is sufficient for a future version-pinned connector design, but the connector is intentionally out of scope here.

TRUD recommends running automation on weekdays between 08:00–18:00 or 00:00–06:00 UK time to avoid planned maintenance. This is an operational recommendation, not a licence restriction.[7]

### Update frequency and versioning

NHSBSA states that dm+d is refreshed weekly.[8] The TRUD release list identifies releases by a version-like release number and week number. Release 11.0.0 is the current candidate examined here, released 2 November 2026.[4] NHSBSA’s release schedule describes the TRUD release ID, extraction date, distribution date, and week number.[6]

Older releases remain visible in the public release list, including Releases 10.3.0 through 4.3.0, which supports reproducibility through release pinning.[4] The future ingestion should pin both the public release number/week/date and the authenticated archive filename plus SHA-256 checksum returned by TRUD. A release should never be referenced only as “latest dm+d.”

### Redistribution and credentials

The OGL permits redistribution of covered information with attribution. The TRUD account/API key is a separate access credential and must never be redistributed. The future connector should keep credentials server-side, use a protected secret mechanism, avoid writing keys into source files or logs, and store only the non-secret release metadata needed for provenance.

## 9. Nigerian jurisdiction limitations

NHS dm+d is a UK NHS terminology standard. It does not establish:

- NAFDAC registration;
- Nigerian product availability;
- Nigerian brand availability;
- Nigerian-approved package labelling;
- Nigerian prescribing or dispensing practice; or
- Nigerian treatment guidelines.

The fact that a product appears in dm+d means that it is represented in a UK NHS terminology context. It does not establish that the same product, strength, dosage form, brand, pack, or regulatory status exists in Nigeria.

Every future derived record should permanently carry at least:

- `source_jurisdiction = United Kingdom`;
- `source_type = terminology_product_identity`;
- `publisher = NHS Business Services Authority`;
- `supporting_body = NHS England / DHSC context where applicable`;
- `dataset_name = NHSBSA dm+d — dm+d in a vendor-neutral format`;
- `trud_item_number = 24`;
- `release = 11.0.0`;
- `release_week = 45`;
- `release_date = 2026-11-02`;
- `licence = Open Government Licence for TRUD / OGL v3.0`;
- `licence_url` pointing to the exact item licence and OGL text;
- attribution text required by OGL;
- `verification_date = 2026-11-06`;
- a statement that the record does not establish Nigerian approval, availability, or clinical practice; and
- the exact archive filename and SHA-256 checksum once obtained through TRUD.

## 10. Governance mapping

The following is a recommendation only. It does not create or approve a `SourceRecord`.

| Governance field | Recommended value |
|---|---|
| `source_id` | A stable project identifier such as `nhsbsa-dmd-trud-item-24-r11.0.0`; assign only after approval |
| `source_type` | `terminology_product_identity` |
| `jurisdiction` | `United Kingdom` |
| `publisher` | `NHS Business Services Authority` |
| `supporting_authority` | `NHS England / Department of Health and Social Care context` |
| `licence` | `Open Government Licence for TRUD; OGL v3.0` |
| `licence_url` | Exact TRUD item-24 licence page and OGL v3 URL |
| `permitted_activities` | Conditionally: download, selected-field extraction, normalization, internal storage, indexing, RAG for identity-only retrieval, summaries of terminology-only content, user display, redistribution, commercial use — only for verified covered fields |
| `excluded_activities` | Clinical advice, dose recommendations, clinical claims, Nigerian regulatory claims, copying excluded third-party components, use of logos/trademarks without rights, and any activity outside OGL or TRUD terms |
| `release/version` | `Release 11.0.0; Week 45` |
| `release_date` | `2026-11-02` |
| `verification_date` | `2026-11-06` |
| `trud_item_number` | `24` |
| `attribution_text` | `Contains public sector information licensed under the Open Government Licence v3.0.` unless a provider-specific statement is supplied |
| `update_cadence` | Weekly, with release and week identifiers |
| `source_authority` | High for UK terminology identity; not clinical-authority evidence and not Nigerian regulatory authority |
| `pharmacist_review_status` | `not_reviewed` |
| `archive_sha256` | Required before approval; not available without authenticated release metadata |
| `third_party_review_status` | `unresolved` |
| `approval_status` | `not_approved` |

## 11. Proposed Milestone 3G small-ingestion scope

This proposal is conditional and must not be executed until Milestone 3G approves the exact release and fields.

### Candidate scope

- **Exact source:** TRUD item 24, Release 11.0.0, Week 45, released 2 November 2026.
- **First fields:** one identifier and description for a small set of VTM, VMP, and AMP concepts; selected product-to-ingredient and product-to-strength relationships; form where required for identity normalization; release/provenance metadata.
- **Deferred fields:** VMPP/AMPP pack detail, routes, GTIN mappings, price, reimbursement, availability, BNF/ATC mappings, supplementary files, and any field whose rights or semantics are not confirmed.
- **Approximate size:** no more than **100 syntheticly selected real records** in the first reversible sample, chosen after release inspection. The exact count and selection rule must be recorded before ingestion; no record was downloaded or selected here.

### Version pinning and provenance

Before ingestion, record the authenticated TRUD archive filename, release name, release date, archive SHA-256 checksum, release-list response, and licence page snapshot. Every derived record and chunk should retain the TRUD item number, release/week/date, source jurisdiction, source class, licence URL, attribution, original concept identifier, source XML path or element reference, and extraction timestamp.

### Licence metadata on chunks

Derived chunks should carry a structured citation to the exact source record, not just a homepage URL. They should include the licence name and URL, required attribution, `source_type=terminology_product_identity`, `jurisdiction=United Kingdom`, and the warning that the record does not establish Nigerian regulatory or clinical facts.

### Reversibility

Ingestion should be isolated under one source ID and release ID. Removal should be possible by deleting or deactivating all chunks, citations, and index entries carrying that source/release identity, then verifying that no retrieval result can return them. No existing synthetic fixtures should be overwritten.

### Required tests

Milestone 3G should test:

1. exact-release and checksum pinning;
2. XML provenance and field mapping;
3. identifier, ingredient, product, strength, and form retrieval;
4. stale-release and withdrawn-source abstention;
5. a clinical question about an NHS dm+d-only record, which must abstain;
6. a Nigerian regulatory question, which must abstain or escalate;
7. citation identity and licence-attribution preservation;
8. exclusion of price, reimbursement, availability, and unverified third-party fields;
9. complete source/release rollback; and
10. pharmacist review of representative terminology mappings.

## 12. Risks and unresolved questions

1. **Archive coverage:** The item-level OGL statement is explicit, but the exact Release 11.0.0 archive contents and any excluded components were not inspected.
2. **Mixed vocabulary rights:** SNOMED CT, BNF, GTIN, trademark, or supplier-related fields may carry separate rights or usage constraints. The first slice should avoid them until verified.
3. **UK-only semantics:** Product identity and availability fields may be meaningful only in the NHS/UK context.
4. **Clinical overreach:** dm+d descriptions and relationships can be mistaken for treatment evidence. The provider boundary must reject clinical claims unsupported by an approved clinical source.
5. **Operational access:** TRUD requires an account and subscription. Automated downloads require a private API key, scheduled responsibly and stored only as a protected secret.
6. **Change management:** Weekly releases can change identifiers, descriptions, availability, and relationships. “Latest” is not reproducible; every release must be pinned and revalidated.
7. **No Nigerian regulatory evidence:** A separate permission-cleared Nigerian source remains necessary for NAFDAC status or local product information.
8. **Licence changes:** Source permissions and third-party exclusions should be rechecked at each new release and before any publication or model use.

## 13. Final classification

### **C — PERMISSION OR DATASET COVERAGE UNRESOLVED**

The exact candidate has a strong, official item-level OGL basis and appears technically suitable for a small terminology ingestion. However, the exact Release 11.0.0 archive and its component-level rights were not inspected, and this milestone prohibits downloading it. It would be unsafe to classify the full release as A based only on the item page and general OGL text.

The proposed future scope may become approvable only after the exact release manifest and selected fields are reviewed. This is not an approval, and no `SourceRecord` has been created or changed.

## 14. Recommendation

Proceed to Milestone 3G only as a **permission-gated, reversible terminology experiment**, not as clinical knowledge ingestion. Obtain Release 11.0.0 through an authorized TRUD account, record the authenticated archive metadata and checksum, inspect the XML and manifest, exclude supplementary or third-party material unless separately cleared, and request pharmacist/source-governance approval for a small VTM/VMP/AMP terminology subset.

If the archive inspection confirms that the selected fields are covered by the item-level OGL and contain no excluded material, the exact release and exact fields can be approved narrowly. If not, keep the source at classification C and continue using synthetic fixtures. In either case, NHS dm+d must never be presented as Nigerian regulatory evidence or as a clinical medication-information source.

## References

[1]: https://isd.digital.nhs.uk/trud/users/guest/filters/0/categories/6/items/24/licences "NHS TRUD Item 24 Licence Page"
[2]: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ "Open Government Licence v3.0"
[3]: https://digital.nhs.uk/services/terminology-and-classifications/dm-d "NHS Digital dm+d Overview"
[4]: https://isd.digital.nhs.uk/trud/user/guest/group/0/pack/6/subpack/24/releases "NHS TRUD Item 24 Releases"
[5]: https://isd.digital.nhs.uk/trud/user/guest/group/0/pack/6/subpack/24/licences "NHS TRUD Item 24 Licence Listing"
[6]: https://www.nhsbsa.nhs.uk/pharmacies-gp-practices-and-appliance-contractors/nhs-dictionary-medicines-and-devices-dmd/release-dmd-files "NHSBSA Release of dm+d Files"
[7]: https://isd.digital.nhs.uk/trud/users/guest/filters/0/api "NHS TRUD Using the API"
[8]: https://www.nhsbsa.nhs.uk/pharmacies-gp-practices-and-appliance-contractors/nhs-dictionary-medicines-and-devices-dmd "NHSBSA NHS Dictionary of Medicines and Devices"
[9]: https://www.nhsbsa.nhs.uk/sites/default/files/2020-11/dm%2Bd%20Implementation%20Guide%20%28Primary%20Care%29%20v2.0.pdf "NHSBSA dm+d Implementation Guide — Primary Care"
