# Milestone 3C Source Selection Report

**Project:** Pharmacy Patient Assistant

**Purpose:** Research authoritative medication-information sources suitable for a Nigerian community pharmacy assistant.

**Checked date:** 2026-11-02

**Scope:** Research only. No clinical or medication documents were downloaded, ingested, indexed, or introduced into the application runtime. No application code, secrets, configuration, or frontend files were modified.

## Executive summary

The first source collection should be led by Nigerian primary sources. Use the National Agency for Food and Drug Administration and Control (NAFDAC) for Nigerian product-registration resources, recalls, safety alerts, blacklists, pharmacovigilance and post-market surveillance. Use the Pharmacy Council of Nigeria (PCN) for pharmacy practice, registration, premises, licensing and professional-regulatory matters. Use the Federal Ministry of Health and Social Welfare (FMoHSW) for national policy, programmes and public-health context. These sources are the most directly relevant to Nigerian community pharmacy practice, but each page or document still needs an item-level currency and permission check.

WHO, EMA, FDA, manufacturer product information, Martindale and MedlinePlus should be treated as question-specific supplementary sources. They are not substitutes for Nigerian law, NAFDAC-approved local product information, current PCN requirements, local protocols, a prescriber, or the responsible pharmacist. International sources can differ from Nigeria in registration, formulation, strength, indications, warnings, availability and professional requirements.

The research confirmed that permission to **read** a source is different from permission to **download**, **extract**, **index internally**, **redistribute**, **reproduce in user-facing answers**, or **use for automated access or model training**. Public accessibility, a download link, government status, a robots.txt file, or attribution alone does not establish all of those permissions. Except where a specific licence or official machine-readable service clearly supports the activity, the project should use a link-first, human-reviewed workflow and obtain written permission before systematic ingestion.

A question-dependent hierarchy is safer than a universal institutional ranking. The applicable source should be selected by question type, jurisdiction, exact product identity and currentness. Conflicts should be documented and escalated rather than silently resolved by the assistant.

## Research methodology

The research covered eight source groups: NAFDAC; FMoHSW; PCN; WHO; EMA and the EU product-information framework; FDA; manufacturer-issued product information; and recognised medicines-information references. For each group, a small number of official pages were opened and assessed for information type, authority, Nigerian relevance, version evidence, update frequency, copyright or licensing statements, automated-extraction or indexing permission, attribution requirements, limitations and a recommendation.

The exercise used official primary websites wherever possible. It did not scrape sites, download documents, ingest document contents, or test automated access. Where an explicit licence or machine-readable service was not verified, the report records the permission as unknown rather than assuming that use is allowed.

The checked date is recorded as **2026-11-02 as supplied for this exercise**. This report does not independently validate future page state, legal status, licence terms, or continuing availability after that date.

## Source evaluation table

| Source group | Organisation and official website | Information provided | Authority and Nigerian relevance | Version and update evidence | Copyright / licensing / automated use | Attribution | Limitations and risks | Recommendation |
|---|---|---|---|---|---|---|---|---|
| **NAFDAC** | National Agency for Food and Drug Administration and Control, Nigeria. [NAFDAC](https://nafdac.gov.ng/), [Drugs](https://nafdac.gov.ng/drugs/), [Recalls and Safety Alerts](https://nafdac.gov.ng/category/recalls-and-alerts/) | Regulatory mandate; drug-registration resources; Greenbook; pharmacovigilance; post-market surveillance; NAPAR; recalls; safety alerts; blacklists; public notices. | **High and direct** for Nigerian regulated-product oversight. NAFDAC describes its statutory role in regulating drugs and other regulated products. | The alerts page displayed a currency statement as of 15 October 2026 and the site contains dated 2026 alerts. No universal version history or fixed update schedule was verified. | No explicit open licence or reuse permission was verified. [Robots.txt](https://nafdac.gov.ng/robots.txt) is a technical crawler directive, not consent to scrape, extract, download, index or reproduce. | Attribute NAFDAC, the exact page or entry, URL and check date. Attribution does not create permission. | A registration entry or alert does not by itself establish product quality, authenticity, clinical appropriateness, storage conditions or supply-chain legality. Individual linked documents may have separate rights. | **Suitable as the primary Nigerian regulatory source**, used read-only and item-by-item. Written permission is needed before automated or systematic collection. |
| **FMoHSW** | Federal Ministry of Health and Social Welfare. [About](https://health.gov.ng/about-us/), [Departments](https://health.gov.ng/departments/), [Publications](https://health.gov.ng/publications/), [Policy documents](https://health.gov.ng/policy-documents-2/) | Ministry mandate; national health policies; Food and Drugs Services context; public-health programmes; manuals, guides, reports, advisories and policy documents. | **High as a primary government source for its own policies and programmes.** It is not necessarily the controlling source for medicines regulation, dispensing rules or professional practice. | Some entries show dates or editions; the FAQ page showed a May 2025 update. No complete supersession register or site-wide schedule was verified. | The pages displayed a copyright footer. No open licence, text-extraction permission or automated-indexing permission was verified. A “Download” link does not itself establish reproduction rights. | Attribute the ministry, exact publication or page, URL and check date. Attribution does not replace permission. | The checked homepage contained an unrelated promotional paragraph, so consequential claims should be checked on the exact page and corroborated. Older or undated policy material may no longer be current. | **Conditionally suitable** for policy and public-health context, with currentness checks and pharmacist/regulatory review. |
| **PCN** | Pharmacy Council of Nigeria. [PCN](https://pcn.gov.ng/), [About](https://pcn.gov.ng/about-pharmacy-council-nigeria/), [Publications](https://pcn.gov.ng/about-pharmacy-council-nigeria/publications/) | Pharmacy education, training and practice oversight; pharmacist and technician registration; PPMV matters; inspection; licensing; ethics; notices and bulletins. | **High and direct** for Nigerian pharmacy practice and professional regulation. PCN identifies itself as the federal pharmacy regulator established under the Pharmacy Council of Nigeria Act 2022. | The publications area showed dated 2026 bulletins, but the annual-licensing page displayed a 2024 instruction. No complete document history was verified. | No explicit open licence or automated-use permission was found. Public links indicate access to listed publications but not blanket rights to extract, index or reproduce them. | Attribute PCN, exact page or publication, URL and check date. | Time-sensitive registration and licensing instructions can change. The evaluated 2024 annual-licensing instruction must not be treated as current without confirmation from PCN or the relevant state/zonal office. | **Suitable as the primary Nigerian pharmacy-regulatory source**, with direct confirmation for current operational requirements. |
| **WHO** | World Health Organization. [WHO](https://www.who.int/), [Nigeria](https://www.who.int/countries/nga), [Guidelines](https://www.who.int/publications/who-guidelines), [Terms](https://www.who.int/about/policies/terms-of-use) | International clinical and public-health guidance; country context; publications; evidence-based recommendations. | **High international authority**, with direct Nigeria country context. WHO guidance is not automatically Nigerian law or local clinical policy. | Product-specific publication dates apply. The guidelines planning list stated that it is updated in June and December. No universal schedule applies to all pages. | WHO website terms permit limited research/private-study extracts under conditions. Some publications use CC BY-NC-SA 3.0 IGO. Third-party material may have separate rights. No blanket permission for scraping, bulk extraction or internal indexing was verified. | Acknowledge WHO and link the page. For licensed publications, retain required title, year, licence and attribution. Do not use the logo or imply endorsement. | Guidance can be scoped to a population or setting, superseded, or unsuitable for Nigerian law and local availability. | **Conditionally suitable** for general evidence and international context, after Nigerian applicability review. |
| **EMA / EU product information** | European Medicines Agency. [Product information](https://www.ema.europa.eu/en/glossary-terms/product-information), [SmPC](https://www.ema.europa.eu/en/glossary-terms/summary-product-characteristics), [Medicine data](https://www.ema.europa.eu/en/medicines/download-medicine-data), [Legal notice](https://www.ema.europa.eu/en/about-us/about-website/legal-notice) | EU-approved SmPC, package leaflet and labelling; public assessment reports; safety and post-authorisation information; machine-readable medicine tables and JSON. | **Very high for EU centrally authorised medicines and the EU framework.** It does not establish Nigerian registration, local formulation, availability or Nigerian law. | EMA states that downloadable data tables update overnight. Product information changes through variations and pharmacovigilance. Document-level revision dates must be retained. | EMA permits reproduction/distribution of EMA-owned material with acknowledgement, subject to exclusions. EMA expressly supports automated use of published JSON/data tables, not blanket ingestion of every page, PDF, image or third-party document. | Acknowledge EMA and include the URL and access month/year. Do not use the logo without permission. | EU product information may differ from Nigerian product information. EMA warns that online material may be incomplete or not fully current and that adopted text controls where relevant. | **Conditionally suitable** as a secondary product-information reference and for the published machine-readable datasets within their stated scope. |
| **FDA** | U.S. Food and Drug Administration. [Prescribing information](https://www.fda.gov/drugs/fdas-labeling-resources-human-prescription-drugs/prescribing-information-resources), [Patient labeling](https://www.fda.gov/drugs/fdas-labeling-resources-human-prescription-drugs/patient-labeling-resources), [Label repository](https://labels.fda.gov/), [Website policies](https://www.fda.gov/about-fda/about-website/website-policies) | U.S. Prescribing Information; Medication Guides; patient labeling; approval and label databases. | **High for U.S. FDA-approved labeling**, but not Nigerian authorization or local dispensing requirements. | FDA says PI holders should review PI at least annually and update it when new information makes it inaccurate. The label repository warns that displayed company-submitted labels may be reformatted, unverified and not identical to currently approved or distributed labeling. | Ordinary FDA website text and graphics are generally public domain unless otherwise noted. This does not establish rights for manufacturer-submitted labels, attachments, logos or every document, nor blanket automated-ingestion permission. | FDA says attribution is appreciated but not required; link to the original, record copy date and avoid implying FDA endorsement. | U.S. labels can differ materially from Nigerian products. Patient labeling is not available for every medicine. | **Conditionally suitable** for U.S. label context, always cross-checked against NAFDAC and local product information. |
| **Manufacturer product information** | A manufacturer portal was evaluated as an example: [Sanofi India product information](https://www.sanofi.com/en/india/our-science/for-healthcare-professionals/product-information) and [terms](https://www.sanofi.com/en/terms-of-use). | Manufacturer-issued abbreviated/full prescribing information and leaflets; medical-information, adverse-event and product-complaint contacts. | **Primary for the manufacturer’s own published material**, but the evaluated portal was India-specific and not evidence of Nigerian authorization. | Sanofi stated that scientific information is continually updated, but the evaluated page did not expose a universal revision history. Exact document dates must be checked. | No open licence or permission for automated extraction, indexing or substantial reproduction was verified. | Attribute the manufacturer, exact product/document, URL and check date. Link rather than reproduce substantial text. | Product, strength, formulation, warning, language and authorization can differ by market. Manufacturer information is not a substitute for NAFDAC-approved local information or pharmacist judgement. | **Conditionally suitable**, only after matching the exact Nigerian product and checking rights. |
| **BNF, Martindale and MedlinePlus** | [BNF](https://bnf.nice.org.uk/), [BNF EULA](https://bnf.nice.org.uk/eula/), [Martindale](https://www.pharmaceuticalpress.com/martindaleonline/), [MedicinesComplete FAQ](https://www.pharmaceuticalpress.com/medicines-complete-faq/), [MedlinePlus](https://medlineplus.gov/about/general/aboutmedlineplus/), [MedlinePlus web services](https://medlineplus.gov/about/developers/webservices/) | BNF: UK prescribing and dispensing reference. Martindale: evaluated international medicine and product information. MedlinePlus: patient-readable health and medicine information and an XML health-topic service. | **Useful supplementary references**, not Nigerian regulatory authorities. BNF is UK-focused; Martindale is licensed; MedlinePlus is U.S.-oriented and includes mixed public-domain and licensed material. | BNF print is updated March and September with monthly online updates. Martindale/MicinesComplete reports monthly updates. MedlinePlus has source-specific review schedules and a daily Tuesday-Saturday health-topic service update. | BNF free NICE terms exclude users outside the UK and prohibit scraping, data mining, AI training and database ingestion. Martindale prohibits scraping/text mining and offers separate licensing. MedlinePlus supports its XML health-topic service under stated conditions, but much of its content is copyrighted or licensed. | BNF and Martindale require publisher notices and licensing compliance. MedlinePlus public-domain content requests NLM/MedlinePlus attribution; the service requires source identification and no endorsement. | None of these sources replaces Nigerian law, local product information or pharmacist judgement. Access and reuse rights vary within each source. | **Conditionally suitable as supplementary references only.** Use BNF or Martindale only under a valid licence; use MedlinePlus selectively and within its content and web-service terms. |

## Licensing and copyright assessment

The following permissions must be treated as separate decisions for every specific page or document:

1. **Permission to read:** A page is publicly accessible or a user has lawful subscription access.
2. **Permission to download:** The site provides a download or a user is authorised to save a copy under its terms.
3. **Permission to extract text or data:** A licence or service term allows copying, parsing or text/data mining.
4. **Permission to index internally:** The licence permits storing content or metadata in an internal retrieval system.
5. **Permission to reproduce in user-facing answers:** The licence permits quotation, paraphrase, redistribution or derivative presentation in the intended product.

The research verified some narrow permissions but not a general permission across all sources. EMA’s published JSON/data tables are the clearest candidate for automated use, within the stated scope and with acknowledgement. MedlinePlus provides a free XML health-topic service with attribution, caching and rate-limit conditions, but the service does not make all MedlinePlus content public domain. WHO publication licences can permit non-commercial reuse of specific CC-licensed works, subject to licence terms and third-party exclusions. FDA ordinary website content is generally public domain unless otherwise noted, but FDA policy does not automatically settle the rights in manufacturer-submitted labels or attachments.

NAFDAC, FMoHSW and PCN pages were publicly readable, but no explicit open licence or automated-ingestion permission was verified in the reviewed pages. Robots.txt is not a licence. A government website, public notice or download button does not by itself authorise systematic extraction, internal indexing, redistribution or model training. Manufacturer portals and paid references require the most caution: no open licence was verified for the evaluated manufacturer portal, BNF has strong geographic and anti-scraping restrictions, and Martindale offers a separate data-licensing route.

Until an item-specific permission is documented, the safe project default is: retain source metadata and a link; write a short human-reviewed summary; do not store substantial document text; do not bulk-download or scrape; do not train a model on the content; and do not reproduce long passages in the user-facing assistant.

## Recommended source hierarchy

There should not be one universal hierarchy. The controlling source depends on the question.

### Nigerian regulatory status, recalls and alerts

Start with the exact current NAFDAC database entry, recall, safety alert, blacklist or official notice. Match the product, strength, formulation, batch or other identifier as applicable. A result should be treated as a trigger for pharmacist review, not as a complete clinical or quality assessment.

### Pharmacy registration, premises and professional practice

Start with the exact current PCN publication or notice. Confirm time-sensitive requirements directly with PCN or the relevant state or zonal office. Do not rely on the evaluated annual-licensing page’s displayed 2024 instruction without confirmation.

### National policy and public-health context

Use the relevant FMoHSW policy or publication. If the question affects dispensing, professional practice, product regulation or patient care, identify the responsible regulator or current legal instrument rather than treating a general ministry page as controlling.

### Exact product information

First identify the active ingredient, strength, dosage form, manufacturer, market and document revision. Use current Nigerian-approved local product information when available. An EMA, FDA or manufacturer document may supplement the answer only after confirming that it matches the product and jurisdiction. International approval does not prove Nigerian registration, availability or local labelling.

### International evidence and general guidance

Use the current WHO publication within its stated scope, then assess Nigerian applicability. WHO authority does not make a recommendation legally binding in Nigeria.

### Patient-readable background

MedlinePlus may provide general patient-readable background, but its U.S. context and mixed licensing must be considered. It does not replace local counselling or approved local product information.

### Conflicting or outdated information

When sources conflict, do not silently choose the most convenient source. Record the exact sources, dates, jurisdictions and product identifiers. Prefer the competent Nigerian primary source for a Nigerian regulatory question, the exact current product information for product details, and the source expressly governing the question or jurisdiction. If the conflict could affect treatment, dispensing, safety, legal compliance or a high-risk patient group, abstain and escalate to the responsible pharmacist, prescriber, regulator or legal adviser.

## Proposed initial source collection

The first implementation should be small and metadata-first. It should not begin with a large document corpus.

| Proposed source | Why it is needed | Information contribution | Licensing status at this stage | Pharmacist review needed |
|---|---|---|---|---|
| NAFDAC Drugs, Recalls and Safety Alerts, plus a specific current entry when needed | Essential Nigerian source for product-status checks, recalls, safety alerts, blacklists and pharmacovigilance. | Product-regulatory metadata, current alerts and post-market-surveillance signals. | Public reading confirmed. No general permission for automated extraction, bulk download, internal indexing or substantial reproduction verified. | Confirm exact product and current entry; decide whether quarantine, reporting, patient notification or referral is needed. |
| PCN About, publications, registration, licensing and contact pages | Essential for pharmacy-practice oversight and current registration/licensing pathways. | Regulatory and professional-practice context, current notices and contact routes. | Public reading and offered publication links visible. No general extraction, indexing or reproduction licence verified. | Determine which requirement applies; confirm current instructions with PCN or state/zonal office. |
| FMoHSW relevant policy or publication page | Provides national policy and public-health context. | Policy categories, Food and Drugs Services context, public-health programmes and official publications. | Copyright footer observed; no verified open licence or automated-use permission. | Determine whether the material is contextual or controls the specific question. |
| One question-specific WHO publication or Nigeria page | Provides international evidence or country context when Nigerian material does not answer the broader question. | General guidance, definitions, country data and international recommendations. | Permission depends on the exact page/publication. Specific CC BY-NC-SA works may permit non-commercial reuse; no blanket automated permission. | Assess population, setting, Nigerian applicability and currentness. |
| One exact local product-information document, selected only after product identification | Product counselling requires exact product and revision, not a generic source. | Approved use, dose, warnings, contraindications, adverse effects, storage and patient instructions as applicable. | Must be checked document-by-document. No document should be downloaded or ingested before rights and local authority are confirmed. | Match active ingredient, strength, form, manufacturer, Nigerian authorization and pack/leaflet. |

For each entry, initially retain only: source name; exact URL; page or document title; jurisdiction; content type; checked date; visible publication or revision date; permitted use as actually stated; and a short human-written summary. This keeps the first implementation reviewable and reduces licensing exposure.

## Nigerian-context findings

NAFDAC is the key source for Nigerian regulated-product information, including registration resources, alerts, recalls, blacklists, pharmacovigilance and post-market surveillance. A NAFDAC result should still be interpreted with the exact product and context, and it does not by itself establish clinical suitability or product authenticity.

PCN is the key source for Nigerian pharmacy education, training, practice oversight, registration, licensing and premises-related matters. Operational pages can lag behind current requirements, so the assistant should direct time-sensitive questions to the current PCN channel rather than presenting a stale page as definitive.

FMoHSW is important for national policy and public-health context, but a ministry page should not automatically outrank NAFDAC for product regulation or PCN for professional practice. The checked FMoHSW site also showed a content-integrity concern in the form of unrelated promotional text on the homepage. That is a reason to corroborate consequential information on the exact official page and with the responsible authority.

International recommendations may differ from Nigerian regulatory requirements, local product availability, formulations, strengths, approved indications, warnings, language and dispensing practice. The assistant should identify the jurisdiction of every source and make that visible whenever an international source is used.

The following could not currently be verified from the research exercise: a universal NAFDAC or PCN document-versioning system; a complete superseded-document archive; blanket automated-access permissions; document-level licensing for every linked PDF, image, database or third-party asset; the current legal effect of every linked regulation; and whether a particular international or manufacturer document matches a Nigerian product.

## Risks and limitations

- Pages, documents, databases, terms and links can change after the checked date. Store item-level publication, revision, effective, archive and access dates.
- No source in this report is a diagnosis, prescribing authorisation, dispensing decision, legal opinion or substitute for a pharmacist, prescriber, regulator or emergency service.
- A public page, download button, open API, JSON file, XML feed or robots.txt signal grants only the rights expressly stated for that item and service.
- Third-party material, images, PDFs, manufacturer submissions, logos and database rights may differ from the rights of the hosting organisation.
- BNF’s free NICE terms materially restrict use outside the UK and prohibit scraping, data mining, AI training and database ingestion. Martindale requires licensing for system integration. MedlinePlus has mixed public-domain and licensed content.
- International sources may be clinically informative but legally or operationally inapplicable to Nigeria.
- The evaluated FMoHSW homepage and PCN licensing page demonstrate why page currency and content integrity need active review.
- No universal source ranking, retention policy, update schedule or comprehensive permission statement was verified.

## Recommendations for Milestone 3D

1. Create a source register with source name, exact URL, title, jurisdiction, content type, checked date, publication or revision date, permitted use, and an escalation owner.
2. Define question-routing rules: NAFDAC for Nigerian product and alert status; PCN for pharmacy regulation and licensing; FMoHSW for policy context; WHO for international guidance; and exact local product information for medicine counselling.
3. Have the supervising pharmacist review routing rules, escalation triggers, alert handling and the boundary between information support and professional decisions.
4. Require exact product, strength, dosage form, manufacturer, jurisdiction and document date before product-information answers are considered.
5. Pilot short attributed answers that link to live sources and state uncertainty. Do not copy substantial text.
6. Before any download, extraction, internal index, API integration, model training, reproduction, commercial use or patient-facing publication, obtain written legal or information-governance review of the specific licence.
7. Retain only the minimum metadata and synthetic test data needed for the prototype. Do not introduce patient-identifying information.
8. Recheck time-sensitive alerts, recalls and licensing instructions immediately before relying on them.

## Decisions requiring pharmacist or legal review

- Which questions the assistant may answer independently and which must be escalated to the responsible pharmacist, prescriber, NAFDAC, PCN, a state/zonal office or emergency services.
- How a specific NAFDAC registration, recall, blacklist or alert should affect stock, dispensing, patient communication and reporting.
- Whether a PCN registration, annual licence, premises, inspection, staffing or PPMV requirement is current and applicable.
- Whether an international or manufacturer document matches the Nigerian product and whether local approved labelling must control.
- Patient-specific dose, interaction, contraindication, pregnancy, paediatric, renal/hepatic, antimicrobial, emergency and referral decisions.
- How conflicts between NAFDAC, PCN, FMoHSW, WHO, product information and international regulators will be handled.
- Whether each proposed source may be downloaded, extracted, cached, internally indexed, redistributed, adapted, used for model training or commercially used.
- Whether any API, JSON/XML service or bulk workflow is covered by explicit terms. EMA published JSON and the MedlinePlus health-topic XML service have specific conditions, but neither authorizes unrelated content ingestion.
- Whether BNF or Martindale access is lawfully licensed for the Nigerian workplace and whether a specific MedlinePlus item is public-domain or licensed third-party content.
- Any legal interpretation concerning the NAFDAC Act, PCN Act, copyright, database rights, privacy, confidentiality, professional liability or patient-data retention.

## Conclusion

Milestone 3C supports a cautious, Nigerian-first source strategy rather than immediate document ingestion. The smallest defensible starting set is a metadata register linking to current NAFDAC, PCN and FMoHSW pages, supplemented only when needed by a question-specific WHO source and an exact, locally matched product-information document. The assistant should remain link-first and pharmacist-reviewed until licensing, currentness, conflict handling and clinical governance are approved.

## References

[1]: https://nafdac.gov.ng/ "NAFDAC official website"
[2]: https://nafdac.gov.ng/drugs/ "NAFDAC Drugs resources"
[3]: https://nafdac.gov.ng/category/recalls-and-alerts/ "NAFDAC Recalls and Safety Alerts"
[4]: https://nafdac.gov.ng/robots.txt "NAFDAC robots.txt"
[5]: https://health.gov.ng/about-us/ "Federal Ministry of Health and Social Welfare About Us"
[6]: https://health.gov.ng/departments/ "Federal Ministry of Health and Social Welfare Departments"
[7]: https://health.gov.ng/publications/ "Federal Ministry of Health and Social Welfare Publications"
[8]: https://health.gov.ng/policy-documents-2/ "Federal Ministry of Health and Social Welfare Policy Documents"
[9]: https://health.gov.ng/faqs/ "Federal Ministry of Health and Social Welfare FAQs"
[10]: https://pcn.gov.ng/ "Pharmacy Council of Nigeria official website"
[11]: https://pcn.gov.ng/about-pharmacy-council-nigeria/ "PCN About the Council"
[12]: https://pcn.gov.ng/about-pharmacy-council-nigeria/publications/ "PCN Publications"
[13]: https://pcn.gov.ng/registrations/pharmacist/ "PCN Pharmacists registration"
[14]: https://pcn.gov.ng/registrations/annual-licensing/ "PCN Annual licensing"
[15]: https://www.who.int/ "World Health Organization official website"
[16]: https://www.who.int/countries/nga "WHO Nigeria country page"
[17]: https://www.who.int/publications/who-guidelines "WHO Guidelines"
[18]: https://www.who.int/about/policies/terms-of-use "WHO Terms of Use"
[19]: https://www.who.int/about/policies/publishing-policies/copyright "WHO Copyright and licensing"
[20]: https://www.ema.europa.eu/en/glossary-terms/product-information "EMA Product information"
[21]: https://www.ema.europa.eu/en/glossary-terms/summary-product-characteristics "EMA Summary of Product Characteristics"
[22]: https://www.ema.europa.eu/en/medicines/download-medicine-data "EMA Download medicine data"
[23]: https://www.ema.europa.eu/en/about-us/about-website/legal-notice "EMA Legal notice"
[24]: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02001L0083-20220101 "EU Directive 2001/83/EC consolidated text"
[25]: https://www.fda.gov/drugs/fdas-labeling-resources-human-prescription-drugs/prescribing-information-resources "FDA Prescribing Information resources"
[26]: https://www.fda.gov/drugs/fdas-labeling-resources-human-prescription-drugs/patient-labeling-resources "FDA Patient labeling resources"
[27]: https://labels.fda.gov/ "FDA Online Label Repository"
[28]: https://www.fda.gov/drugs/development-approval-process-drugs/drug-approvals-and-databases "FDA Drug approvals and databases"
[29]: https://www.fda.gov/about-fda/about-website/website-policies "FDA Website Policies"
[30]: https://www.sanofi.com/en/india/our-science/for-healthcare-professionals/product-information "Sanofi India Product Information"
[31]: https://www.sanofi.com/en/terms-of-use "Sanofi Terms of Use"
[32]: https://bnf.nice.org.uk/ "British National Formulary"
[33]: https://bnf.nice.org.uk/eula/ "BNF NICE End User Licence Agreement"
[34]: https://bnf.nice.org.uk/about/preface/ "BNF Preface"
[35]: https://bnf.nice.org.uk/about/publication-information/ "BNF Publication Information"
[36]: https://www.pharmaceuticalpress.com/martindaleonline/ "Martindale Online"
[37]: https://www.pharmaceuticalpress.com/content/martindale-the-complete-drug-reference/ "Martindale: The Complete Drug Reference"
[38]: https://www.pharmaceuticalpress.com/terms-and-conditions/ "Pharmaceutical Press Terms and Conditions"
[39]: https://www.pharmaceuticalpress.com/data-licensing/content/ "Pharmaceutical Press Data Licensing"
[40]: https://www.pharmaceuticalpress.com/medicines-complete-faq/ "MedicinesComplete FAQ"
[41]: https://medlineplus.gov/about/general/aboutmedlineplus/ "About MedlinePlus"
[42]: https://medlineplus.gov/about/using/usingcontent/ "Using MedlinePlus Content"
[43]: https://medlineplus.gov/about/general/reviewandupdate/ "MedlinePlus Review and Update"
[44]: https://medlineplus.gov/about/developers/webservices/ "MedlinePlus Web Services"
