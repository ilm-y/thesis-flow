# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


class QualityAssessment:
    """
    Assesses the quality and relevance of academic papers.
    Scores papers based on multiple quality dimensions.
    """

    # Quality scoring weights
    WEIGHTS = {
        "recency": 0.15,           # Recent papers are more valuable
        "citations": 0.20,         # Citation count indicates influence
        "venue_quality": 0.20,     # arXiv, IEEE, ACM, etc. are high quality
        "content_depth": 0.15,     # Length and detail of abstract
        "methodology_clarity": 0.15,  # How clearly methods are presented
        "relevance": 0.15          # Match to research keywords
    }

    def __init__(self):
        self.current_year = datetime.now().year

    def assess_papers(self, papers: List[Dict[str, Any]], 
                     keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Assess quality of multiple papers.

        Args:
            papers: List of paper records
            keywords: Keywords for relevance scoring

        Returns:
            Papers with quality scores added
        """
        if not papers:
            return []

        if keywords is None:
            keywords = []

        # Score each paper
        scored_papers = []
        for paper in papers:
            score = self._score_paper(paper, keywords)
            paper_with_score = paper.copy()
            paper_with_score["quality_score"] = score
            paper_with_score["quality_rating"] = self._score_to_rating(score)
            scored_papers.append(paper_with_score)

        return scored_papers

    def _score_paper(self, paper: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate overall quality score for a paper (0-100)."""
        score = 0.0

        # Recency score
        recency_score = self._score_recency(paper)
        score += recency_score * self.WEIGHTS["recency"]

        # Citation score
        citation_score = self._score_citations(paper)
        score += citation_score * self.WEIGHTS["citations"]

        # Venue quality score
        venue_score = self._score_venue(paper)
        score += venue_score * self.WEIGHTS["venue_quality"]

        # Content depth score
        depth_score = self._score_content_depth(paper)
        score += depth_score * self.WEIGHTS["content_depth"]

        # Methodology clarity score
        method_score = self._score_methodology(paper)
        score += method_score * self.WEIGHTS["methodology_clarity"]

        # Relevance score
        relevance_score = self._score_relevance(paper, keywords)
        score += relevance_score * self.WEIGHTS["relevance"]

        return min(100.0, score)  # Cap at 100

    def _score_recency(self, paper: Dict) -> float:
        """Score based on publication year (higher = more recent)."""
        year = self._extract_year(paper)

        if year is None:
            return 50.0  # Unknown year = medium score

        # Calculate age in years
        age = self.current_year - year

        # Scoring: 0-5 years old = high score, >10 years = low score
        if age <= 2:
            return 100.0
        elif age <= 5:
            return 80.0
        elif age <= 8:
            return 60.0
        elif age <= 10:
            return 40.0
        else:
            return 20.0

    def _score_citations(self, paper: Dict) -> float:
        """Score based on citation count."""
        citations = self._extract_citations(paper)

        if citations is None:
            return 50.0  # Unknown = medium

        # Scoring based on citation count
        if citations >= 1000:
            return 100.0
        elif citations >= 500:
            return 90.0
        elif citations >= 100:
            return 80.0
        elif citations >= 50:
            return 70.0
        elif citations >= 20:
            return 60.0
        elif citations >= 10:
            return 50.0
        elif citations >= 5:
            return 40.0
        elif citations > 0:
            return 30.0
        else:
            return 20.0  # No citations yet

    def _score_venue(self, paper: Dict) -> float:
        """Score based on publication venue."""
        url = (paper.get("link") or paper.get("url") or "").lower()
        title = (paper.get("title") or "").lower()
        venue = (paper.get("venue") or paper.get("conference") or "").lower()
        combined = url + " " + title + " " + venue

        # Tier 1: Top academic venues
        tier1_venues = [
            "arxiv", "nature", "science", "ieee", "acm", 
            "cvpr", "iccv", "eccv", "neurips", "icml", "iclr",
            "aistats", "uai", "ijcai", "aaai", "sigmod", "vldb"
        ]

        # Tier 2: Reputable academic venues
        tier2_venues = [
            "springer", "elsevier", "wiley", "acm digital",
            "journal", "conference", "proceedings", ".edu",
            "researchgate", "scholar.google"
        ]

        # Tier 3: Other sources
        tier3_venues = [
            "medium", "blog", "github", "reddit", ".com"
        ]

        # Score based on venue tier
        for venue in tier1_venues:
            if venue in combined:
                return 100.0

        for venue in tier2_venues:
            if venue in combined:
                return 80.0

        for venue in tier3_venues:
            if venue in combined:
                return 40.0

        # Default for unknown venue
        if url:
            return 60.0
        return 50.0

    def _score_content_depth(self, paper: Dict) -> float:
        """Score based on content depth (length of abstract/snippet)."""
        # Check for full abstract
        abstract = paper.get("abstract", paper.get("snippet", ""))

        if not abstract:
            return 20.0

        # Score by length
        length = len(abstract)
        if length >= 500:
            return 100.0
        elif length >= 300:
            return 80.0
        elif length >= 150:
            return 60.0
        elif length >= 50:
            return 40.0
        else:
            return 20.0

    def _score_methodology(self, paper: Dict) -> float:
        """Score based on methodology clarity."""
        abstract = (paper.get("abstract") or paper.get("snippet") or "").lower()
        title = (paper.get("title") or "").lower()
        combined = abstract + " " + title

        # Check for methodology indicators
        methodology_indicators = [
            "propose", "propose", "present", "introduce", "develop",
            "method", "approach", "algorithm", "model", "framework",
            "experiment", "empirical", "evaluation", "benchmark",
            "dataset", "result", "findings", "analysis"
        ]

        indicator_count = sum(1 for indicator in methodology_indicators 
                            if indicator in combined)

        # Score based on indicator count
        if indicator_count >= 8:
            return 100.0
        elif indicator_count >= 6:
            return 80.0
        elif indicator_count >= 4:
            return 60.0
        elif indicator_count >= 2:
            return 40.0
        else:
            return 20.0

    def _score_relevance(self, paper: Dict, keywords: List[str]) -> float:
        """Score based on keyword relevance."""
        if not keywords:
            return 50.0

        title = (paper.get("title") or "").lower()
        abstract = (paper.get("abstract") or paper.get("snippet") or "").lower()
        combined = title + " " + abstract

        # Count keyword matches
        matches = 0
        for keyword in keywords:
            if keyword.lower() in combined:
                matches += 1

        # Score based on match percentage
        if keywords:
            match_percentage = matches / len(keywords)
            return min(100.0, match_percentage * 100)
        return 50.0

    @staticmethod
    def _score_to_rating(score: float) -> str:
        """Convert numerical score to star rating."""
        if score >= 90:
            return "★★★★★ (Excellent)"
        elif score >= 75:
            return "★★★★☆ (Very Good)"
        elif score >= 60:
            return "★★★☆☆ (Good)"
        elif score >= 45:
            return "★★☆☆☆ (Fair)"
        else:
            return "★☆☆☆☆ (Poor)"

    @staticmethod
    def _extract_year(paper: Dict) -> Optional[int]:
        """Extract publication year from paper."""
        # Try year field
        if "year" in paper and isinstance(paper["year"], int):
            return paper["year"]

        # Try published_date
        pub_date = paper.get("published_date", "")
        if pub_date:
            match = re.search(r"20\d{2}", str(pub_date))
            if match:
                return int(match.group())

        # Try title/snippet
        for field in ["title", "snippet", "abstract"]:
            text = paper.get(field, "")
            match = re.search(r"20\d{2}", text)
            if match:
                return int(match.group())

        return None

    @staticmethod
    def _extract_citations(paper: Dict) -> Optional[int]:
        """Extract citation count from paper."""
        citations = paper.get("citations")

        if isinstance(citations, int):
            return citations

        if isinstance(citations, str):
            match = re.search(r"(\d+)", citations)
            if match:
                return int(match.group(1))

        return None


# Create global assessor instance
_assessor = QualityAssessment()


@tool
def assess_paper_quality(papers_json: str, query_keywords: str = "") -> str:
    """
    Assess the quality and relevance of academic papers.

    This tool scores papers on multiple dimensions:
    1. **Recency** (15%): How recent the publication (0-5 years = high score)
    2. **Citations** (20%): Impact measured by citation count
    3. **Venue Quality** (20%): Publication venue prestige (arXiv, IEEE, ACM > others)
    4. **Content Depth** (15%): Length and detail of abstract
    5. **Methodology** (15%): Clarity of research approach
    6. **Relevance** (15%): Match to search keywords

    Args:
        papers_json: JSON string containing list of papers to assess
        query_keywords: Space-separated keywords for relevance scoring

    Returns:
        JSON string with:
        - assessed_papers: Papers ranked by quality score (0-100)
        - scoring_breakdown: Explanation of scoring methodology
        - top_papers: Top N papers recommended for reading
        - quality_distribution: Summary of quality scores

    Example:
        Input:
            papers_json: '[{"title": "AI Glasses Vision", "snippet": "...", "link": "arxiv.org/..."}]'
            query_keywords: 'AI glasses augmented reality'

        Output:
            {
                "assessed_papers": [
                    {
                        "title": "AI Glasses Vision",
                        "quality_score": 82,
                        "quality_rating": "★★★★☆ (Very Good)",
                        "scoring_notes": "Recent work (2024), from arXiv, 120 citations, high relevance"
                    }
                ],
                "top_papers": ["Paper 1", "Paper 2"],
                "quality_distribution": {
                    "excellent": 2,
                    "very_good": 5,
                    "good": 3,
                    "fair": 2,
                    "poor": 1
                }
            }
    """
    try:
        # Parse input
        if isinstance(papers_json, str):
            try:
                papers = json.loads(papers_json)
            except json.JSONDecodeError:
                papers = []
        else:
            papers = papers_json

        if not isinstance(papers, list):
            papers = [papers] if papers else []

        # Parse keywords
        keywords = [kw.strip() for kw in query_keywords.split() if kw.strip()]

        # Assess papers
        assessed = _assessor.assess_papers(papers, keywords)

        # Sort by quality score
        assessed_sorted = sorted(assessed, key=lambda x: x.get("quality_score", 0), reverse=True)

        # Calculate distribution
        distribution = {
            "excellent": sum(1 for p in assessed if p.get("quality_score", 0) >= 90),
            "very_good": sum(1 for p in assessed if 75 <= p.get("quality_score", 0) < 90),
            "good": sum(1 for p in assessed if 60 <= p.get("quality_score", 0) < 75),
            "fair": sum(1 for p in assessed if 45 <= p.get("quality_score", 0) < 60),
            "poor": sum(1 for p in assessed if p.get("quality_score", 0) < 45)
        }

        # Get top papers
        top_papers = [p.get("title", "Unknown") for p in assessed_sorted[:5]]

        # Add scoring notes to each paper
        for paper in assessed_sorted:
            notes = _generate_scoring_notes(paper)
            paper["scoring_notes"] = notes

        return json.dumps({
            "assessed_papers": assessed_sorted,
            "top_papers": top_papers,
            "quality_distribution": distribution,
            "scoring_breakdown": {
                "recency": "15% - How recent (0-5 years = higher score)",
                "citations": "20% - Citation count (indicates influence)",
                "venue": "20% - Publication venue (arXiv/IEEE/ACM = high)",
                "depth": "15% - Abstract/content length",
                "methodology": "15% - Clarity of research approach",
                "relevance": "15% - Match to keywords"
            },
            "total_assessed": len(assessed),
            "average_score": round(sum(p.get("quality_score", 0) for p in assessed) / len(assessed), 1) if assessed else 0
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error assessing paper quality: {str(e)}")
        return json.dumps({
            "error": str(e),
            "assessed_papers": [],
            "total_assessed": 0
        })


def _generate_scoring_notes(paper: Dict) -> str:
    """Generate human-readable scoring explanation for a paper."""
    notes = []

    score = paper.get("quality_score", 0)

    # Check recency
    year = QualityAssessment._extract_year(paper)
    if year:
        age = 2024 - year
        if age <= 2:
            notes.append("Recent work")
        elif age <= 5:
            notes.append(f"{age}y old")
        else:
            notes.append(f"Older ({age}y)")

    # Check venue
    url = (paper.get("link") or paper.get("url") or "").lower()
    if "arxiv" in url:
        notes.append("arXiv")
    elif any(domain in url for domain in ["ieee", "acm", "springer"]):
        notes.append("Premium venue")
    elif ".edu" in url:
        notes.append("Academic source")

    # Check citations
    citations = QualityAssessment._extract_citations(paper)
    if citations and citations > 0:
        if citations >= 100:
            notes.append(f"Highly cited ({citations})")
        elif citations >= 10:
            notes.append(f"Cited ({citations}x)")

    # Check content
    abstract = paper.get("abstract", paper.get("snippet", ""))
    if abstract and len(abstract) > 300:
        notes.append("Detailed")

    return " | ".join(notes) if notes else "Standard paper"


if __name__ == "__main__":
    # Test example
    test_papers = [
        {
            "title": "Deep Learning for Computer Vision: A 2024 Review",
            "snippet": "This comprehensive review covers recent advances in deep learning applications to computer vision, including CNN architectures, transformers, and vision models.",
            "link": "https://arxiv.org/abs/2401.12345",
            "published_date": "2024-01-15",
            "citations": 250
        },
        {
            "title": "Classical Computer Vision Methods",
            "snippet": "Survey of early computer vision techniques.",
            "link": "https://example.edu/papers/cv",
            "published_date": "2010-06-20",
            "citations": 5
        }
    ]

    result = assess_paper_quality(json.dumps(test_papers), "computer vision deep learning")
    result_dict = json.loads(result)

    print("Paper Quality Assessment:")
    print(f"Total Assessed: {result_dict['total_assessed']}")
    print(f"Average Score: {result_dict['average_score']}/100")
    print("\nTop Papers:")
    for paper in result_dict["assessed_papers"][:2]:
        print(f"  - {paper['title']}: {paper['quality_rating']} ({paper['quality_score']})")
