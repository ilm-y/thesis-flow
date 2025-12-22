# Paper Analysis Guide

## Overview

This guide provides detailed instructions for extracting and structuring metadata from academic papers in a standardized format for deep-mining research analysis.

## Extraction Methodology

### Phase 1: Locating and Accessing Papers

1. **Paper Source Identification**
   - Search academic databases: arXiv, IEEE Xplore, ACM Digital Library, PubMed
   - Use DOI or direct URL when provided by user
   - Prioritize peer-reviewed publications
   - Note publication year and venue for temporal analysis

2. **Access and Content Retrieval**
   - Download full-text PDF when available
   - Extract text using OCR if necessary
   - Preserve formatting and section structure
   - Note any access restrictions or paywalls

### Phase 2: Metadata Extraction

#### 2.1 Bibliographic Information
```
Title: [Exact paper title]
Authors: [All authors in order, with affiliations if available]
Publication Year: [Year of publication]
Venue: [Journal name, conference acronym, or publisher]
DOI: [Digital Object Identifier if available]
URL: [Direct link to paper or abstract]
Citation Count: [Number of times cited, if available from Google Scholar or Semantic Scholar]
```

#### 2.2 Abstract and Keywords
- **Abstract**: Full paper abstract (typically 150-300 words)
- **Keywords**: Extract or identify research keywords and topics
- **Research Field**: Primary discipline (AI, ML, NLP, Computer Vision, etc.)

#### 2.3 Methodology and Approach
- **Problem Statement**: What problem does this paper address?
- **Research Question**: Core research question(s)
- **Methodology**: Research approach (empirical, theoretical, applied, etc.)
- **Type of Paper**: (original research, survey, case study, benchmark, etc.)

#### 2.4 Technical Details
- **Datasets Used**: Names and sources of datasets
- **Baseline Methods**: Existing approaches compared against
- **Proposed Method**: Novel approach or contribution
- **Complexity Analysis**: Computational or conceptual complexity if mentioned

#### 2.5 Results and Findings
- **Performance Metrics**: Quantitative results (accuracy, F1, BLEU, etc.)
- **Baseline Comparisons**: How does proposed method compare to existing work?
- **Key Findings**: Most important results
- **Tables and Figures**: Locate key result tables

#### 2.6 Scope and Limitations
- **Limitations Acknowledged**: Acknowledged limitations by authors
- **Scope Boundaries**: What the paper does NOT address
- **Future Work**: Suggested directions mentioned by authors
- **Generalizability**: Applicability to other domains/tasks

### Phase 3: Information Synthesis

Organize extracted information into structured JSON or markdown format:

```json
{
  "metadata": {
    "title": "Paper Title",
    "authors": ["Author 1", "Author 2"],
    "year": 2024,
    "venue": "NeurIPS 2024",
    "doi": "10.xxxx/xxxx.xxxx"
  },
  "research_scope": {
    "problem_statement": "...",
    "research_questions": ["RQ1: ...", "RQ2: ..."],
    "methodology": "...",
    "paper_type": "original_research"
  },
  "technical_scope": {
    "datasets": ["Dataset 1", "Dataset 2"],
    "baselines": ["Method A", "Method B"],
    "proposed_method": "Novel approach description",
    "complexity": "O(n log n) or equivalent"
  },
  "results": {
    "primary_metrics": {
      "accuracy": "95.2%",
      "f1_score": "0.948"
    },
    "key_findings": ["Finding 1", "Finding 2"]
  },
  "scope_limitations": {
    "acknowledged_limitations": ["Limitation 1", "Limitation 2"],
    "future_work": ["Direction 1", "Direction 2"]
  }
}
```

## Quality Assurance Checklist

- [ ] All bibliographic information is accurate and complete
- [ ] Abstract accurately reflects paper content
- [ ] Keywords represent the main research topics
- [ ] Problem statement is clearly articulated
- [ ] All numeric results are transcribed accurately
- [ ] Limitations are honestly reported
- [ ] Paper type is correctly identified
- [ ] All sources (datasets, baselines) are properly cited
- [ ] Venue information is correct (journal/conference name and year)

## Special Cases

### Survey and Review Papers
- Focus on coverage breadth and categorization schemes
- Note how many papers/works are reviewed
- Extract key research trends identified
- Document research gaps highlighted

### Technical Reports and Whitepapers
- Identify the organization/author
- Note publication status (official, preliminary, internal)
- Extract technical specifications with full detail
- Document assumed audience expertise level

### Pre-prints (arXiv, etc.)
- Note pre-print status and associated published version if available
- Record submission date and revision history if relevant
- Flag if paper has been subsequently published with modifications

## Output Format Standards

All extracted information should:
1. Use consistent field names across all papers
2. Include confidence levels for uncertain information
3. Preserve direct quotes for methodology and findings
4. Include section references for all extracted information
5. Be ready for cross-paper synthesis and comparison
