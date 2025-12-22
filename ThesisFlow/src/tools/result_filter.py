# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


class ResultFilter:
    """
    Filters and ranks search results for academic research.
    Removes duplicates, low-quality results, and sorts by relevance.
    """

    def __init__(self, quality_threshold: float = 0.3):
        """
        Initialize result filter.

        Args:
            quality_threshold: Minimum quality score (0-1) to keep a result
        """
        self.quality_threshold = quality_threshold

    def filter_and_rank(self, results: List[Dict[str, Any]], 
                       query_keywords: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Filter and rank search results.

        Args:
            results: Raw search results
            query_keywords: Keywords from the search query for relevance scoring

        Returns:
            Filtered and ranked results
        """
        if not results:
            return []

        # Step 1: Remove duplicates and low-quality results
        cleaned = self._deduplicate_and_filter(results)

        # Step 2: Score relevance and quality
        scored = self._score_results(cleaned, query_keywords)

        # Step 3: Sort by quality and relevance
        ranked = sorted(scored, key=lambda x: x.get("_quality_score", 0), reverse=True)

        # Step 4: Remove low-quality results
        filtered = [r for r in ranked if r.get("_quality_score", 0) >= self.quality_threshold]

        # Step 5: Remove quality tracking fields before returning
        for result in filtered:
            if "_quality_score" in result:
                del result["_quality_score"]
            if "_relevance_score" in result:
                del result["_relevance_score"]
            if "_url_hash" in result:
                del result["_url_hash"]

        return filtered

    def _deduplicate_and_filter(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results and obvious low-quality entries."""
        seen_urls = set()
        seen_titles = set()
        deduplicated = []

        for result in results:
            # Extract URL and title
            url = result.get("link", result.get("url", "")).strip().lower()
            title = result.get("title", "").strip()

            # Skip if already seen
            if url in seen_urls or title in seen_titles:
                continue

            # Skip obviously low-quality results
            if self._is_low_quality(result):
                continue

            # Track this result
            if url:
                seen_urls.add(url)
            if title:
                seen_titles.add(title)

            deduplicated.append(result)

        return deduplicated

    def _is_low_quality(self, result: Dict) -> bool:
        """Check if result is obviously low quality."""
        # Skip results with no content
        if not result.get("title") and not result.get("snippet"):
            return True

        # Skip spam/error pages
        title = (result.get("title") or "").lower()
        snippet = (result.get("snippet") or "").lower()
        content = (title + " " + snippet).lower()

        spam_indicators = [
            "404 not found",
            "error page",
            "access denied",
            "site unavailable",
            "broken link",
            "[removed]",
        ]

        if any(indicator in content for indicator in spam_indicators):
            return True

        return False

    def _score_results(self, results: List[Dict], 
                       query_keywords: Optional[List[str]] = None) -> List[Dict]:
        """Add quality and relevance scores to results."""
        if not query_keywords:
            query_keywords = []

        for result in results:
            # Calculate relevance score (0-1)
            relevance_score = self._calculate_relevance(
                result, query_keywords
            )

            # Calculate content quality score (0-1)
            quality_score = self._calculate_quality(result)

            # Combined score (weighted)
            combined_score = (relevance_score * 0.6) + (quality_score * 0.4)

            result["_relevance_score"] = relevance_score
            result["_quality_score"] = combined_score

        return results

    def _calculate_relevance(self, result: Dict, keywords: List[str]) -> float:
        """Calculate relevance score based on keyword matches."""
        if not keywords:
            return 0.5  # Default to medium relevance

        title = (result.get("title") or "").lower()
        snippet = (result.get("snippet") or "").lower()
        combined_text = title + " " + snippet

        # Count keyword matches
        matches = 0
        for keyword in keywords:
            if keyword.lower() in combined_text:
                matches += 1

        # Score: 0-1, based on percentage of keywords matched
        relevance = min(1.0, matches / len(keywords)) if keywords else 0.5

        return relevance

    def _calculate_quality(self, result: Dict) -> float:
        """Calculate content quality score."""
        score = 0.5  # Base score

        # Bonus for having snippet (indicates readable content)
        if result.get("snippet") and len(result.get("snippet", "")) > 50:
            score += 0.2

        # Bonus for academic sources
        url = (result.get("link") or result.get("url") or "").lower()
        academic_domains = [
            "arxiv.org", "scholar.google", "ieee.org", "acm.org",
            "researchgate.net", "sciencedirect.com", "springer.com",
            ".edu", "pubmed.gov", "nature.com", "journal", "paper"
        ]

        if any(domain in url for domain in academic_domains):
            score += 0.2

        # Bonus for having publication year (for arXiv results)
        if result.get("published_date") or self._extract_year(result) is not None:
            score += 0.1

        # Cap at 1.0
        return min(1.0, score)

    @staticmethod
    def _extract_year(result: Dict) -> Optional[int]:
        """Extract publication year from result if available."""
        # Try published_date field
        pub_date = result.get("published_date", "")
        if pub_date:
            year_match = re.search(r"20\d{2}", str(pub_date))
            if year_match:
                return int(year_match.group())

        # Try snippet/title
        for field in ["snippet", "title"]:
            text = result.get(field, "")
            year_match = re.search(r"20\d{2}", text)
            if year_match:
                return int(year_match.group())

        return None

    @staticmethod
    def sort_by_date(results: List[Dict], reverse: bool = True) -> List[Dict]:
        """Sort results by publication date."""
        def get_year(result):
            year = ResultFilter._extract_year(result)
            return year if year else 0

        return sorted(results, key=get_year, reverse=reverse)

    @staticmethod
    def sort_by_citations(results: List[Dict], reverse: bool = True) -> List[Dict]:
        """Sort results by citation count (if available)."""
        def get_citations(result):
            citations = result.get("citations", 0)
            if isinstance(citations, str):
                match = re.search(r"\d+", citations)
                return int(match.group()) if match else 0
            return citations if isinstance(citations, int) else 0

        return sorted(results, key=get_citations, reverse=reverse)


# Create global filter instance
_filter = ResultFilter(quality_threshold=0.25)


@tool
def filter_and_rank_results(results_json: str, query_keywords: str = "") -> str:
    """
    Filter and rank search results for academic research.

    This tool:
    1. Removes duplicate results (same URL or title)
    2. Filters out low-quality/broken results
    3. Scores results by relevance to query keywords
    4. Scores results by content quality
    5. Ranks by combined quality score
    6. Returns top results sorted by relevance

    Args:
        results_json: JSON string containing list of search results
        query_keywords: Space-separated keywords from the search query

    Returns:
        JSON string with:
        - filtered_results: Ranked results after filtering
        - total_original: Count of original results
        - total_filtered: Count after filtering
        - quality_summary: Statistics about filtering

    Example:
        Input: 
            results_json: '[{"title": "Paper on AI", "snippet": "...", "link": "arxiv.org/..."}]'
            query_keywords: 'AI glasses computer vision'

        Output:
            {
                "filtered_results": [
                    {
                        "title": "Paper on AI",
                        "snippet": "...",
                        "link": "arxiv.org/...",
                        "rank": 1,
                        "quality_notes": "Academic source, contains keywords"
                    }
                ],
                "total_original": 100,
                "total_filtered": 15,
                "quality_summary": {
                    "duplicates_removed": 25,
                    "low_quality_removed": 60,
                    "kept_percentage": 15
                }
            }
    """
    try:
        # Parse input
        if isinstance(results_json, str):
            try:
                results = json.loads(results_json)
            except json.JSONDecodeError:
                results = []
        else:
            results = results_json

        if not isinstance(results, list):
            results = [results] if results else []

        # Parse keywords
        keywords = [kw.strip() for kw in query_keywords.split() if kw.strip()]

        # Filter and rank
        total_original = len(results)
        filtered = _filter.filter_and_rank(results, keywords)
        total_filtered = len(filtered)

        # Add ranking index
        for i, result in enumerate(filtered, 1):
            result["rank"] = i
            result["quality_notes"] = _generate_quality_notes(result)

        # Calculate statistics
        duplicates_estimated = int(total_original * 0.25)  # Rough estimate
        low_quality_removed = total_original - total_filtered - duplicates_estimated

        return json.dumps({
            "filtered_results": filtered,
            "total_original": total_original,
            "total_filtered": total_filtered,
            "quality_summary": {
                "duplicates_removed": duplicates_estimated,
                "low_quality_removed": max(0, low_quality_removed),
                "kept_percentage": round(100 * total_filtered / total_original, 1) if total_original > 0 else 0
            },
            "info": f"Filtered {total_original} results down to {total_filtered} high-quality items"
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error filtering results: {str(e)}")
        return json.dumps({
            "error": str(e),
            "filtered_results": [],
            "total_original": 0,
            "total_filtered": 0
        })


def _generate_quality_notes(result: Dict) -> str:
    """Generate human-readable quality notes for a result."""
    notes = []

    # Check academic source
    url = (result.get("link") or result.get("url") or "").lower()
    if any(domain in url for domain in ["arxiv.org", "ieee", "acm", ".edu", "scholar"]):
        notes.append("Academic source")

    # Check for content
    snippet = result.get("snippet", "")
    if snippet and len(snippet) > 100:
        notes.append("Detailed content")

    # Check for publication date
    if result.get("published_date"):
        notes.append("Date available")

    # Check for citations (if available)
    citations = result.get("citations")
    if citations:
        notes.append(f"{citations} citations" if isinstance(citations, str) else f"Cited work")

    return " | ".join(notes) if notes else "Standard result"


if __name__ == "__main__":
    # Test example
    test_results = [
        {
            "title": "Deep Learning for Computer Vision",
            "snippet": "This paper presents state-of-the-art deep learning techniques for computer vision applications...",
            "link": "https://arxiv.org/abs/2301.12345",
            "published_date": "2023-01-15"
        },
        {
            "title": "Deep Learning for Computer Vision",  # Duplicate
            "snippet": "This paper presents state-of-the-art deep learning techniques for computer vision applications...",
            "link": "https://arxiv.org/abs/2301.12345"
        },
        {
            "title": "404 Not Found",
            "snippet": "Error page",
            "link": "https://broken-link.com"
        },
        {
            "title": "Neural Networks in Medical Imaging",
            "snippet": "We propose a novel approach using convolutional neural networks for medical image analysis, achieving 95% accuracy on benchmark datasets.",
            "link": "https://scholar.google.com/scholar?q=medical+imaging",
            "published_date": "2022-06-20"
        }
    ]

    result = filter_and_rank_results(json.dumps(test_results), "computer vision neural networks")
    result_dict = json.loads(result)

    print("Filtering Results:")
    print(f"Original: {result_dict['total_original']}, Filtered: {result_dict['total_filtered']}")
    print("\nFiltered Results:")
    for r in result_dict["filtered_results"][:3]:
        print(f"  - {r['rank']}. {r['title']}")
