# Hackathon Submission Answers

## QUESTION 1: Problem Statement
**Data Readiness & Standardisation**

## QUESTION 2: Problem & Affected (Max 100 words)
Indian government portals host data in inconsistent formats (PDFs, non-standard CSVs) with missing or poor metadata. This fragmentation makes high-value public data undiscoverable and unusable for AI applications. The primary groups affected are researchers, policymakers, and AI startups who spend 80% of their time cleaning data instead of analyzing it. Our specifically addresses the "AI-readiness gap" by automating the conversion of these unstructured/semi-structured files into a unified, machine-readable schema.

## QUESTION 3: Proposed Solution (Max 100 words)
We built the **AIKosh Harmonizer**, an intelligent pipeline that turns disparate files (PDF, CSV, Excel) into standardized JSON metadata.
*   **Core Idea**: A dual-engine system using Computer Vision for PDFs and Large Language Models (Gemini) for semantic harmonization of structured data.
*   **Key Components**: FastAPI Backend, PDF Layout Parsing Engine, LLM Synthesizer, and a React-based Dashboard.
*   **Differentiation**: unlike regex-based scrapers, our solution uses Context-Aware AI to infer missing metadata (e.g., deducing "Ministry of Health" from a "Vaccination" dataset) and enforces strict IDMO schema compliance.

## QUESTION 4: Social Impact (Max 100 words)
**Primary Beneficiaries**: Citizens, Data Journalists, MSMEs, and Government Decision Makers.
**Impact**:
1.  **Transparency**: Makes hidden government data searchable and accessible to citizens.
2.  **Efficiency**: Reduces data pre-processing time for startups from weeks to minutes.
3.  **Policy**: Enables cross-ministry analytics (e.g., correlating health data with rainfall) by standardizing the underlying metadata layer, leading to better evidenced-based governance.

## QUESTION 5: Data Sources (Max 100 words)
Our solution is designed to ingest:
1.  **Open Government Data (OGD) Portals**: CSV and Excel datasets (Public Records).
2.  **Ministry Annual Reports**: PDF documents containing statistical tables (Public Records).
3.  **State Data Portals**: Legacy formats.
**Nature**: All data processed is Open Government Data.
**Licensing**: We strictly adhere to the **Open Government Data License (OGDL)** and do not store proprietary data.

## QUESTION 6: Open Source & Repository (Max 100 words)
**Repository**: [Insert Your GitHub Link Here]
**License**: We explicitly confirm this solution is released under the **MIT License**.
**Reusability**:
*   **Modular**: Developers can swap the LLM provider (Gemini/OpenAI) in `synthesizer.py`.
*   **Extensible**: The schema validation logic is decoupled, allowing adoption for other standards.
*   **Dockerized**: We provide a containerized setup for instant deployment by other teams.

## QUESTION 7: Artefacts (Max 100 words)
We are submitting:
1.  **Source Code**: Full GitHub repository with backend and frontend code.
2.  **Demo Video**: A walkthrough of extracting metadata from a raw PDF and a CSV.
3.  **Documentation**: A comprehensive `README.md` for zero-knowledge setup.
4.  **DataSet Samples**: A folder of `Input_Raw` vs `Output_Standardized` JSONs to prove fidelity.

## QUESTION 8: Future Development (Max 100 words)
**Mentorship Phase**:
*   **Milestone 1**: Integrate Bhashini API for multilingual metadata (Hindi/Tamil support).
*   **Milestone 2**: Add an "API Connector" to fetch live data from OGD APIs periodically.
**Scaling**: We plan to deploy this as a microservice on the **AIKosh Platform**, allowing it to serve as the "Ingestion Gatekeeper" for all new government uploads, ensuring 100% standardized data entering the national ecosystem from Day 1.
