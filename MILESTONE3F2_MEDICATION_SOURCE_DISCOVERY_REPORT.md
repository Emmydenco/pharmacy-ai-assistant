# Milestone 3F.2 — Medication Knowledge Source Discovery

**Research date:** 5–6 November 2026  
**Project:** Pharmacy Patient Assistant, initially targeting community pharmacies in Nigeria  
**Status:** Research and documentation only. No medication content was ingested, no source was approved, no source-registry permission was changed, and no application code was modified.

## Executive summary

This review compared RxNorm/RxNav, DailyMed/SPL, openFDA drug-label data, WHO Essential Medicines List and related publications, EMA medicine data, MedlinePlus, and NHS dm+d. The sources divide into three different roles:

- **Terminology and identity:** RxNorm/RxNav and NHS dm+d are useful for normalized names, identifiers, products, ingredients, strengths, dosage forms, and relationships. They are not substitutes for patient-facing clinical monographs.
- **Clinical or regulatory product information:** DailyMed, openFDA label records, MedlinePlus drug information, and EMA product information can contain indications, warnings, adverse reactions, and other clinical content, but much of that content is manufacturer-submitted, third-party licensed, jurisdiction-specific, or not clearly reusable for all requested activities.
- **International reference guidance:** WHO’s Essential Medicines List is highly authoritative for prioritization and international context, but it is not a Nigerian product-information source and WHO’s normal publication licence is non-commercial.

**No candidate is approved for immediate full clinical ingestion.** The strongest candidates for a staged strategy are: (1) **NHS dm+d** for terminology and product identity, subject to confirming that the exact TRUD release and any included third-party components remain within the Open Government Licence; (2) **RxNorm/RxNav** for international terminology, subject to the UMLS/RxNorm licence and source-restriction review; and (3) **openFDA metadata-only fields** for public-domain metadata where the individual field is clearly outside the manufacturer-submitted label text. These sources do not establish Nigerian registration or Nigerian-approved patient information.

The first source for any real ingestion should therefore be selected only after a source-specific approval record identifies exact datasets or documents, rights for extraction/transformation/storage/indexing/RAG/summaries/user-facing reproduction, jurisdictional limitations, attribution requirements, and a pharmacist review plan. Until then, the application should remain on synthetic fixtures.

## Sources investigated and decision categories

The decision categories are: **A — suitable for controlled ingestion; B — suitable for metadata and linking only; C — permission or licensing unresolved; D — unsuitable for this project.** The category is scoped to the intended use, not to whether a source is technically accessible.

| Candidate | Category | Main role | Main reason |
|---|---:|---|---|
| RxNorm/RxNav | C, potentially A for a scoped terminology subset | Medication identity and terminology | NLM-created normalized names and codes are public domain, but full releases also contain proprietary source data and require a free UMLS licence. |
| DailyMed/SPL | C | US label discovery and product-information linking | API and downloads are technically strong, but record-level rights vary and label content may be supplied by private labelers. |
| openFDA drug-label API | B for carefully selected metadata; C for label text | Metadata, identifier discovery, and links | openFDA is generally CC0, but third-party label works may be excluded and the API warns that submitted label content is not verified by FDA. |
| WHO Essential Medicines List/publications | C for non-commercial, resource-specific use | International prioritization and reference context | Individual publications must be checked; the normal CC BY-NC-SA 3.0 IGO licence does not grant commercial use. |
| EMA medicine data/product information | A for EMA-owned material after record-level check; C for third-party material | EU regulatory metadata and product-information links | EMA permits commercial and non-commercial reproduction of EMA-owned material with attribution, but excludes third-party content and carries jurisdictional limits. |
| MedlinePlus | B for public-domain summaries and linking; C/D for drug monographs | Patient-oriented health information and links | Public-domain sections may be reused with attribution, but ASHP drug monographs and other licensed content cannot be ingested without a separate licence. |
| NHS dm+d | A for an exact OGL-covered release after confirmation; not a clinical monograph | UK medicines and devices terminology | TRUD identifies the item as covered by the Open Government Licence, which allows commercial reuse, adaptation, and redistribution with attribution. UK scope remains a limitation. |
| NAFDAC Greenbook | C | Nigerian regulatory lookup | Prior Milestone 3F research found official access but no sufficiently clear published permission for extraction, internal indexing, AI retrieval, or redistribution. It remains a verification/linking candidate, not an approved ingestion source. |

## Official documentation examined

The review used official publisher documentation and licence pages rather than search snippets. The prior project reports were also used for the already completed NAFDAC and openFDA assessments.

1. NLM RxNorm files and release documentation, including current monthly and weekly release availability, RRF format, and the separate prescribable-content release.[1]
2. NLM RxNorm Terms of Service, including public-domain status of NLM-created normalized names and codes, proprietary source restrictions, attribution, redistribution freshness, and non-endorsement terms.[2]
3. NLM RxNav API documentation, including GET-based access, API-key behavior, caching, rate-limit guidance, and monthly update relationship.[3]
4. DailyMed REST API and SPL download documentation.[4] [5]
5. WHO copyright and licensing policy plus the WHO Model List of Essential Medicines description.[6] [7]
6. EMA medicine-data downloads, JSON data documentation, and legal notice.[8] [9] [10]
7. MedlinePlus content-use policy and Web Service documentation.[11] [12]
8. NHSBSA/TRUD dm+d licence page, NHS dm+d scope page, and the Open Government Licence v3 text.[13] [14] [15]
9. openFDA Terms of Service and drug-label API documentation.[16] [17]
10. `MILESTONE3C_SOURCE_SELECTION_REPORT.md` and `MILESTONE3F1_OPENFDA_SOURCE_VERIFICATION_REPORT.md` for the project’s earlier NAFDAC and openFDA conclusions.

## Licensing and permission findings

The following matrix uses **Verified**, **Unresolved**, or **Not appropriate**. “Verified” means the cited official documentation supports that activity for the identified content class. It does not mean that every document or record in the source has the same rights.

| Source/content class | Viewing | Linking | Downloading | Extraction | Transformation | Internal storage/indexing | AI retrieval/summaries | User-facing reproduction | Redistribution/commercial use |
|---|---|---|---|---|---|---|---|---|---|
| RxNorm NLM-created normalized names/codes | Verified | Verified | Generally verified | Generally verified | Generally verified | Generally verified with attribution and current-version notice | Plausible for this public-domain subset; source-specific review still required | Plausible with attribution and no NLM endorsement | Public-domain subset is broadly reusable; full release and proprietary source components remain licence-controlled |
| Full RxNorm release | Verified | Verified | Verified after UMLS licence | Unresolved by source component | Unresolved by source component | Unresolved by source component | Unresolved by source component | Unresolved by source component | UMLS licence and source restrictions apply; do not assume commercial redistribution |
| RxNav API responses | Verified | Verified | API retrieval verified | Unresolved by response/source component | Unresolved by response/source component | Caching is contemplated, but rights remain source-dependent | Unresolved for proprietary source responses | Attribution requested; no endorsement | Rate limits and terms apply; API access is not blanket content licensing |
| DailyMed SPL records | Verified | Verified | Technically verified | Unresolved at record/content level | Unresolved at record/content level | Unresolved at record/content level | Unresolved | Unresolved | Do not assume commercial reuse or redistribution of label text; labeler and third-party rights must be checked |
| openFDA CC0-covered material | Verified | Verified | Verified | Verified | Verified | Verified | Technically possible, subject to content class and terms | Verified subject to warnings/attribution practice | Commercial use is allowed for CC0-covered content |
| openFDA third-party label works | Verified | Verified | API access only does not settle reuse | Unresolved | Unresolved | Unresolved | Unresolved | Unresolved | Third-party rights may apply and are expressly excluded from the general CC0 statement |
| WHO publication explicitly under CC BY-NC-SA 3.0 IGO | Verified | Verified | Verified | Verified for licensed work | Verified with ShareAlike and attribution | Non-commercial use only | Non-commercial use may be possible if the specific work permits it | Non-commercial with attribution and disclaimers | Commercial use requires permission; third-party credited material may require separate permission |
| EMA-owned material | Verified | Verified | Verified | Verified | Generally verified | Generally verified | Technically feasible, but summaries must preserve provenance and disclaimers | Commercial and non-commercial reproduction permitted with source acknowledgement | Commercial reuse permitted for EMA-owned material; third-party content excluded |
| MedlinePlus public-domain sections | Verified | Verified | Verified | Verified | Generally verified | Generally verified with attribution | Plausible for public-domain sections, not for licensed sections | Permitted with attribution and no endorsement implication | Public-domain sections may be reused; licensed drug monographs cannot be ingested without direct licence |
| MedlinePlus licensed drug monographs | Verified | Single direct links permitted | Not sufficient for reuse | Not permitted without licence | Not permitted without licence | Not permitted without licence | Not permitted without licence | Direct linking permitted; reproduction unresolved/not permitted | Separate licence from the rights holder required |
| NHS dm+d exact OGL-covered release | Verified | Verified | Verified after TRUD account/subscription | Verified under OGL | Verified | Verified | Technically compatible, subject to attribution and third-party exclusions | Verified under OGL with attribution and non-endorsement | OGL permits commercial and non-commercial use, adaptation, and redistribution; third-party rights remain excluded |
| NAFDAC Greenbook | Verified | Verified | Technically accessible | Unresolved | Unresolved | Unresolved | Unresolved | Unresolved | Permission remains unresolved; no ingestion approval |

This matrix is a project governance assessment, not legal advice. A future approval must preserve the exact licence text and source snapshot used for the decision.

## Candidate assessments

### 1. RxNorm and RxNav

RxNorm provides normalized clinical-drug names and codes such as RxCUI, with relationships useful for ingredient, strength, dose-form, and product normalization. The release files are pipe-delimited RRF files, and NLM publishes full monthly releases, weekly updates, and a separate current prescribable-content release.[1] RxNav exposes HTTP GET APIs for RxNorm, prescribable RxNorm, RxTerms, and drug-class resources. NLM documents caching and says the APIs are updated following monthly releases.[3]

The rights boundary is important. NLM states that the normalized names and codes created by NLM are public domain, but the full RxNorm dataset also includes proprietary data from terminology providers. A free UMLS licence is required for full releases, and source-specific restrictions may apply.[2] NLM requests attribution, prohibits implying endorsement, and requires republishers to keep distributed data current or clearly say that it may not be current.[2]

RxNorm is strong for medication identity and terminology. It is not a complete patient-information source: it does not by itself supply the full counselling, warnings, contraindications, adverse-reaction, storage, or locally approved-label content required for a pharmacy assistant. It also does not establish Nigerian registration, Nigerian brand availability, or NAFDAC status. It is best treated as a terminology layer, not the primary clinical knowledge base.

**Assessment:** C overall until the exact RxNorm subset and UMLS/source restrictions are documented. A limited NLM-created terminology subset may become suitable for controlled ingestion after governance review.

### 2. DailyMed and SPL

DailyMed provides a versioned REST API with XML or JSON responses and resources for SPLs, set IDs, drug names, NDCs, RxCUIs, UNII codes, histories, media, and packaging. It also provides ZIP and PDF downloads for current and historical SPL versions.[4] Bulk daily, weekly, monthly, and full-release downloads are available.[5]

This is technically attractive for provenance because records have set IDs, version history, active/archived status, and update headers. However, DailyMed label records are not automatically a reusable corpus. SPL content is submitted by labelers, and the project’s previous openFDA assessment identified the same core issue for manufacturer-submitted label text: a government-hosted record may contain content whose copyright or reuse terms are held by a private party. The official pages reviewed here did not establish blanket permission for extraction, transformation, internal indexing, AI summaries, and commercial redistribution of every label.

DailyMed records are also primarily US-regulatory information. A DailyMed label does not establish Nigerian approval, local packaging, local brand availability, or Nigerian prescribing practice.

**Assessment:** C. Suitable for discovery and linking while record-level rights are unresolved. Do not bulk-download or ingest label text in this project yet.

### 3. openFDA

openFDA generally makes its own platform materials and public-domain data available under CC0, while warning that some data may not be public domain, including copyrightable works supplied by private entities.[16] The drug-label API specifically returns manufacturer and distributor submissions in SPL-derived JSON. openFDA annotates and reformats the records, updates the dataset weekly, and warns that the content has not been altered or verified by FDA and may not match the currently distributed or approved label.[17]

The new finding is that an **openFDA metadata-only integration** could still have value without treating the label body as reusable clinical evidence. Candidate fields should be divided into: (a) clearly public-domain/API metadata and identifiers; (b) harmonized or platform-added fields whose provenance is documented; and (c) manufacturer-submitted label sections, which remain rights- and reliability-sensitive. The first two classes could support search, identifier discovery, and links. They should not be used to imply Nigerian regulatory status or clinical approval.

**Assessment:** B for carefully selected metadata and linking; C for label-text ingestion until record-level rights and verification boundaries are resolved.

### 4. WHO Essential Medicines List and publications

WHO describes the Model List of Essential Medicines as a guide that countries or regional authorities can adapt to local priorities and treatment guidelines. It is updated every two years and focuses on population health needs, evidence, safety, cost-effectiveness, dosage forms, quality, and availability.[7]

WHO’s normal publication licence is CC BY-NC-SA 3.0 IGO. It allows copying, distribution, translation, and adaptation for non-commercial purposes with attribution and ShareAlike, but commercial uses require permission. WHO also warns that publications can contain third-party material requiring separate permission.[6] The exact licence notice for each EML edition or medicine publication must therefore be captured before ingestion.

WHO is highly valuable for international prioritization and terminology around essential medicines. It does not establish Nigerian registration, local brands, product labels, or local clinical policy. It is better as a supplementary reference or future non-commercial research source than as the sole patient-facing medicine corpus.

**Assessment:** C for the project’s potential future commercial use; possibly controlled non-commercial use for specific editions after licence and third-party checks.

### 5. EMA medicine data and product information

EMA publishes medicine tables and JSON data for medicines, procedures, documents, product information, safety communications, shortages, and related regulatory material. Its pages state that the medicine data tables are updated overnight, while the general JSON files update twice daily. The files include stable-looking fields such as medicine names, product numbers, document types, first-published dates, last-updated dates, reference numbers, and document URLs.[8] [9]

EMA’s legal notice says EMA-owned webpages and documents may be reproduced and distributed for non-commercial and commercial purposes with acknowledgement. It expressly excludes third-party content and some photographs or other material not owned by EMA.[10] It also states that the website is informational, may not be complete or current, and that online documents may not reproduce an officially adopted text precisely.

EMA offers strong provenance and update mechanics for EMA-owned metadata and documents. Its coverage is European and does not establish Nigerian regulatory status. Product information may also contain third-party or rights-sensitive content, so an exact document-level rights classification is required.

**Assessment:** A for a narrow, EMA-owned metadata subset after record-level confirmation; C for mixed document collections and third-party product-information content.

### 6. MedlinePlus

MedlinePlus states that some content is public domain and some content is copyrighted and licensed specifically for MedlinePlus. Public-domain sections include health-topic summaries, medical-test information, and selected government-produced material. MedlinePlus permits reproduction, redistribution, and linking of the public-domain content with attribution.[11]

The same page identifies ASHP drug monographs and other materials as copyrighted. It says users may make single direct links, but may not ingest or brand the copyrighted content in an EHR, patient portal, or other health IT system without licensing the content from the information vendor.[11] This is a direct blocker for using the drug-monograph section as an unlicensed RAG corpus.

The MedlinePlus Web Service is free, does not require registration or licensing, returns XML topic data, updates daily Tuesday–Saturday, and requires no more than 85 requests per minute per IP. NLM recommends caching results for 12–24 hours.[12] These terms support a linking or carefully scoped public-domain integration, not blanket extraction of drug information.

MedlinePlus is US-oriented and does not establish Nigerian product status. Its public-domain health-topic summaries may be useful for general health education, but they are not a sufficient primary medication-label source.

**Assessment:** B for public-domain sections and linking; C/D for licensed drug monographs without a direct licence.

### 7. NHS dm+d

The NHSBSA describes dm+d as the recognized NHS standard for identifying and communicating medicinal-product and medical-device information in patient care. The data is maintained from manufacturer and supplier product information, and NHSBSA publishes updates on a regular weekly cycle.[14]

The TRUD page identifies the dm+d item as covered by the Open Government Licence. OGL v3 grants a worldwide, royalty-free, perpetual, non-exclusive right to copy, publish, distribute, transmit, adapt, and exploit the information commercially and non-commercially, subject to attribution. It excludes third-party rights, personal data, trademarks, and other rights not licensed by the provider.[13] [15]

This makes dm+d the clearest candidate for a controlled terminology ingestion, provided the project records the exact TRUD release, confirms that the release is the OGL-covered item, preserves attribution, and excludes components not licensed by NHSBSA. dm+d is not a clinical monograph. It can support product identity, names, ingredients, strengths, dose forms, and relationships, but it does not by itself provide patient counselling, indications, contraindications, warnings, adverse reactions, or Nigerian-approved information.

**Assessment:** A for the exact OGL-covered terminology release after source-governance approval; not a sufficient primary clinical-information source.

### 8. NAFDAC Greenbook

The earlier Milestone 3F assessment reviewed NAFDAC’s official Drugs page, Greenbook site, privacy material, and a product document. It found an important Nigerian relevance advantage: NAFDAC is the natural source for Nigerian regulatory status. It did not find a clear, general licence authorizing download, extraction, transformation, internal indexing, AI retrieval, summaries, and user-facing reproduction of Greenbook documents. The selected product document also contained rights language requiring caution.

**Assessment:** C. Use only for manual verification or links until NAFDAC permission is obtained or a clearly applicable licence is published.

## Medication information coverage and pharmaceutical suitability

| Candidate | Generic/ingredient | Brand/product | Strength/dose form/route | Indications/warnings/adverse reactions | Storage/counselling | Nigerian regulatory facts |
|---|---:|---:|---:|---:|---:|---:|
| RxNorm/RxNav | Strong | Partial | Strong | Limited | Limited | No |
| DailyMed/SPL | Strong | Strong | Strong | Strong but labeler-submitted and US-oriented | Often present, record-specific | No |
| openFDA | Strong | Strong | Strong | Present in records but unverified/reformatted submissions | Record-specific | No |
| WHO EML | Strong at essential-medicine level | Limited | Some dosage-form information | Guideline/reference context, not product monographs | Limited | No |
| EMA | Strong | Strong for EU-authorised products | Strong for covered products | Strong in selected product documents | Often present, document-specific | No |
| MedlinePlus | Generic and patient-topic coverage | Limited | Limited/record-specific | Some patient-facing information; licensed drug monographs restricted | Some | No |
| NHS dm+d | Strong | Strong for UK products | Strong | Minimal clinical narrative | Minimal | No |
| NAFDAC Greenbook | Potentially strong for Nigerian registered products | Strong for listed products | Record-specific | Product-document dependent | Record-specific | Potentially yes, subject to official record and permission |

No candidate alone supplies every required field. A responsible system needs a layered source strategy and must never merge foreign regulatory facts into Nigerian advice without explicit jurisdiction labels.

## Nigerian relevance

A medicine appearing in a US, UK, EU, or international database does not establish NAFDAC registration, local availability, Nigerian brand identity, local package instructions, or Nigerian clinical practice. WHO guidance is not automatically a Nigerian guideline. A foreign label is not Nigerian-approved patient information.

The most important missing layer is a permission-cleared Nigerian regulatory/product source. NAFDAC Greenbook is the obvious candidate for regulatory verification, but its reuse permission remains unresolved under the prior assessment. The project should therefore treat NAFDAC as a future regulatory verification or linking source until written permission or a clear licence is obtained.

RxNorm, NHS dm+d, and openFDA metadata can still support normalization and cross-source matching. They should not be used to infer that a normalized product is stocked in Nigeria or approved locally. A later inventory integration should be pharmacy-owned synthetic or authorized inventory data, separate from public medicine knowledge.

## Technical feasibility

All candidates can be represented in the existing governed architecture because the current models already support source identity, approval status, version/publication metadata, provenance, page or section references, citations, freshness, and source revalidation. No connector is recommended in this milestone.

- **RxNorm/RxNav:** RRF downloads and JSON/XML APIs; stable RxCUI identifiers; monthly full releases and weekly updates; API keys improve rate limits and unlock certain licensed-source functions; moderate integration complexity.
- **DailyMed:** Versioned JSON/XML REST API, set IDs, histories, ZIP/PDF download URLs, active/archived status, and media/packaging resources; technically strong but rights and content classification are complex.
- **openFDA:** JSON API, harmonized identifiers, weekly updates, query and pagination mechanisms; low-to-moderate integration complexity; clinical content needs an explicit unverified-submission flag.
- **WHO:** Publications and online EML resources; machine-readable and licence availability vary by resource; moderate complexity and substantial rights review per edition.
- **EMA:** XLS and JSON downloads, twice-daily JSON updates, document URLs, product numbers, and update fields; moderate complexity; strong provenance for EMA-owned metadata.
- **MedlinePlus:** XML web service and XML files; daily updates Tuesday–Saturday; 85 requests per minute per IP; low technical complexity but mixed content rights.
- **NHS dm+d:** TRUD account/subscription, downloadable releases, OGL-labelled item, recurring releases, and structured terminology; moderate integration complexity; UK-only scope.
- **NAFDAC:** Web interfaces and product documents are technically discoverable, but permission, stable access, and extraction terms remain unresolved.

## Comparative evaluation

Scores are from 1 to 5. For **integration complexity**, 5 means easier/lower complexity. A high technical score does not override unresolved rights.

| Source | Permission clarity | Commercial use | Coverage | Authority | Nigerian relevance | Technical access | Updates | Provenance | Integration simplicity | Sustainability |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RxNorm/RxNav | 3 | 2 | 3 | 5 | 2 | 5 | 5 | 5 | 4 | 5 |
| DailyMed/SPL | 2 | 2 | 5 | 4 | 2 | 5 | 5 | 5 | 3 | 4 |
| openFDA metadata | 4 | 4 | 3 | 4 | 2 | 5 | 4 | 4 | 4 | 4 |
| WHO EML/publications | 3 | 1 | 3 | 5 | 3 | 3 | 3 | 4 | 3 | 4 |
| EMA-owned data | 4 | 4 | 4 | 5 | 2 | 4 | 5 | 5 | 4 | 5 |
| MedlinePlus public-domain subset | 4 | 4 | 3 | 5 | 2 | 4 | 4 | 4 | 4 | 5 |
| NHS dm+d | 5 | 5 | 3 | 4 | 2 | 4 | 5 | 5 | 4 | 5 |
| NAFDAC Greenbook | 1 | 1 | 4 | 5 | 5 | 2 | 3 | 4 | 2 | 3 |

**Score interpretation:** NHS dm+d scores highest on the specific OGL-covered terminology item because its licence explicitly permits commercial reuse, adaptation, and redistribution with attribution. RxNorm scores highly on authority, identifiers, provenance, and updates, but lower on commercial permission because the full release contains proprietary source material and requires UMLS/source-restriction review. openFDA metadata scores well for technical and public-domain characteristics only when the selected fields are separated from third-party label text. NAFDAC scores highly for Nigerian relevance but lowest for permission clarity and technical sustainability because the prior permission assessment is unresolved.

## Recommended source strategy

### Primary clinical-information source

**Do not select a primary clinical-information corpus yet.** The current evidence does not establish blanket, commercially reusable, record-level rights for DailyMed, openFDA label text, MedlinePlus drug monographs, WHO publications, or mixed EMA product-information documents. The next source should be chosen only after a document-level permission review. A written permission request to NAFDAC for a limited, named Greenbook document would be the most locally relevant path, but it is not yet a source approval.

### Supplementary medication terminology source

The preferred initial terminology candidates are **NHS dm+d** and **RxNorm**, with different roles:

1. NHS dm+d is the clearest commercial-reuse candidate for a controlled terminology subset under OGL, subject to confirming the exact release and excluding third-party components. It is UK-focused.
2. RxNorm is the stronger internationally recognized normalization layer for RxCUI-based matching, but full-release ingestion requires UMLS licensing and source-specific review. Use only a clearly permissioned subset or an approved API usage pattern.

A terminology layer should be kept separate from clinical evidence. It can map names and identifiers; it cannot support counselling claims by itself.

### Nigerian regulatory source

**NAFDAC Greenbook** should remain the target regulatory source for Nigerian registration and product identity, but only for linking/manual verification until a clear reuse permission is obtained. Do not copy or index its product text yet.

### Optional international reference sources

- Use WHO EML as a non-commercial or link-only international prioritization reference unless commercial permission is obtained for the exact edition.
- Use EMA-owned metadata or documents when the exact record is confirmed as EMA-owned and attribution/disclaimer requirements are preserved.
- Use openFDA metadata for identifier discovery and links, not as a blanket licence for manufacturer-submitted label text.
- Use MedlinePlus public-domain summaries and direct links, excluding licensed ASHP drug monographs unless separately licensed.

## Proposed first source for ingestion

**Proposed first controlled ingestion candidate: an exact NHS dm+d terminology release covered by the TRUD Open Government Licence, not clinical monograph text.** This is a proposal for Milestone 3F.3 review, not an approval.

The first ingestion should be limited to fields necessary for terminology and product identity, such as source identifiers, product/ingredient names, strengths, dose forms, and relationships. It should preserve the TRUD item identity, release date, licence URL, attribution, publisher, and an explicit statement that the dataset is UK-oriented and does not establish Nigerian registration or availability.

Before ingestion, Milestone 3F.3 must verify:

1. The exact release is the OGL-covered item, not a linked third-party component.
2. The project may download, extract, transform, store, index, retrieve, summarize, and reproduce the selected fields.
3. The required attribution is retained in every derived chunk and user-facing citation.
4. Third-party trademarks, logos, personal data, and excluded rights are not ingested.
5. The terminology source is not treated as evidence for indications, warnings, adverse reactions, dosing advice, or Nigerian regulatory facts.
6. A pharmacist reviews the intended field mapping and test queries before any runtime use.

If the governance review does not approve this exact source snapshot, the project remains synthetic-only.

## Unresolved permission questions

1. For RxNorm, which exact NLM-created and source-contributed fields will be used, and do the UMLS Source Restriction Levels permit internal storage, RAG, summaries, commercial use, and user-facing reproduction?
2. For DailyMed and openFDA, can rights holders confirm reuse of the specific label records selected for a non-commercial prototype and a possible future commercial product?
3. For WHO EML and publications, what licence is attached to each exact edition or file, and does it permit the intended transformations and AI-generated summaries? If not, can commercial permission be obtained?
4. For EMA, which exact records are EMA-owned, and which contain third-party documents, images, translations, or rights-sensitive attachments?
5. For MedlinePlus, can the project obtain a direct licence for ASHP drug monographs, or should it be restricted to public-domain summaries and links?
6. For NHS dm+d, do the exact TRUD files contain any third-party rights or non-OGL components, and what account/subscription terms apply to persistent automated downloads?
7. For NAFDAC Greenbook, can NAFDAC provide written permission for downloading, extraction, internal indexing, RAG, summaries, and user-facing reproduction of named records?
8. What Nigerian pharmacist or regulator review is required before any international source can be used to answer medication-use questions in a Nigerian pharmacy context?
9. What source-update and withdrawal process will be used when a product is withdrawn, a label changes, or a licence changes?

## Risks and limitations

This report is not legal advice and does not establish clinical validation or regulatory compliance. “Public,” “free API,” and “government-hosted” do not mean that every attached document, label, image, translation, or third-party field is reusable.

The major clinical risk is jurisdictional mismatch. Foreign product labels and terminology can be accurate for their jurisdiction while being unsuitable as Nigerian-approved patient information. A safe design must show source jurisdiction, date, document version, and permission status, and must abstain when local status or evidence is missing.

The major data-governance risk is mixed rights within a single API or bulk download. Source approval must be field- or record-specific, not merely domain-specific. It must also be rechecked before final answers, because records, licences, and source status can change.

The major technical risk is conflating terminology with clinical evidence. RxNorm, dm+d, and metadata APIs can improve retrieval and matching but cannot by themselves support patient-facing medication claims.

## Recommendations for Milestone 3F.3

1. Do not ingest real medication content yet and keep the current knowledge base synthetic-only.
2. Perform a formal approval review for one exact NHS dm+d OGL-covered terminology release as the first candidate.
3. In parallel, request written NAFDAC permission for a narrowly named Greenbook record set or obtain a clearly applicable official licence.
4. Define separate source classes in the registry: terminology, regulatory status, clinical label, patient education, and international guidance.
5. Add field-level and record-level rights metadata to the source approval record, including permitted activities and jurisdiction.
6. Build a pharmacist-reviewed evaluation set using synthetic or de-identified prompts; do not use real patient data.
7. Treat openFDA/DailyMed/MedlinePlus clinical text as link-only or unresolved until the exact record rights are documented.
8. When one source is formally approved, ingest one small, reversible, version-pinned sample and test provenance, abstention, withdrawal, and citation behavior before expanding.
9. Do not make a live Cloudflare request or change provider configuration as part of source approval.

## References

[1]: https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html "NLM RxNorm Files"
[2]: https://www.nlm.nih.gov/research/umls/rxnorm/docs/termsofservice.html "NLM RxNorm Terms of Service"
[3]: https://lhncbc.nlm.nih.gov/RxNav/APIs/ "NLM RxNav APIs"
[4]: https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm "DailyMed Application Development Support: Web Services"
[5]: https://dailymed.nlm.nih.gov/dailymed/spl-resources.cfm "DailyMed SPL Resources"
[6]: https://www.who.int/about/policies/publishing/copyright "WHO Copyright, Licensing and Permissions"
[7]: https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.02 "WHO Model List of Essential Medicines — 23rd list, 2023"
[8]: https://www.ema.europa.eu/en/medicines/download-medicine-data "EMA Download Medicine Data"
[9]: https://www.ema.europa.eu/en/about-us/about-website/download-website-data-json-data-format "EMA Download Website Data in JSON Data Format"
[10]: https://www.ema.europa.eu/en/about-us/about-website/legal-notice "EMA Legal Notice"
[11]: https://medlineplus.gov/about/using/usingcontent/ "MedlinePlus Linking to and Using Content"
[12]: https://medlineplus.gov/about/developers/webservices/ "MedlinePlus Web Service"
[13]: https://isd.digital.nhs.uk/trud/users/guest/filters/0/categories/6/items/24/licences "NHSBSA dm+d TRUD Licence"
[14]: https://www.nhsbsa.nhs.uk/manufacturers-and-suppliers/medicines-data-and-dmd "NHSBSA Medicines Data and dm+d"
[15]: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/ "Open Government Licence v3.0"
[16]: https://open.fda.gov/terms/ "openFDA Terms of Service"
[17]: https://open.fda.gov/apis/drug/label/ "openFDA Drug Product Labeling API"
