# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import re
from typing import List, Optional
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """
    Optimizes verbose search descriptions into multiple specific, focused search queries.
    Converts natural language descriptions into Boolean search queries suitable for academic databases.
    """

    def __init__(self):
        self.keyword_extractors = {
            "domain_terms": r"\b(?:AI|artificial intelligence|deep learning|machine learning|computer vision|NLP|" +
                           r"augmented reality|AR|mixed reality|MR|virtual reality|VR|neural network|transformer|" +
                           r"blockchain|quantum|IoT|cloud|edge computing|5G|6G)\b",
            "time_keywords": r"\b(?:2024|2025|2023|2022|2021|recent|latest|current|historical|timeline|evolution)\b",
            "application_keywords": r"\b(?:medical|healthcare|education|business|retail|entertainment|gaming|" +
                                  r"manufacturing|transportation|agriculture|finance|security)\b",
            "technical_keywords": r"\b(?:algorithm|architecture|framework|model|method|approach|technique|" +
                                 r"implementation|design|protocol|standard|optimization)\b"
        }

    def optimize_description(self, description: str) -> List[str]:
        """
        Convert a verbose description into multiple focused search queries.

        Args:
            description: Original verbose search description

        Returns:
            List of optimized search queries
        """
        if not description or len(description.strip()) < 5:
            return []

        # Check if description already contains structured queries
        if self._is_already_structured(description):
            return self._extract_existing_queries(description)

        # Otherwise, generate optimized queries
        return self._generate_queries_from_description(description)

    def _is_already_structured(self, description: str) -> bool:
        """Check if description already has numbered queries or Boolean operators."""
        has_numbered = bool(re.search(r"\d+\.\s*['\"]?(?:search|query|find)", description, re.IGNORECASE))
        has_boolean = bool(re.search(r"\b(?:AND|OR|NOT)\b", description))
        return has_numbered or has_boolean

    def _extract_existing_queries(self, description: str) -> List[str]:
        """Extract structured queries from description."""
        queries = []

        # Try to extract numbered queries
        numbered_queries = re.findall(
            r'\d+\.\s*["\']?([^"\'\n]+?)["\']?(?:(?=\d+\.)|$)',
            description,
            re.MULTILINE | re.IGNORECASE
        )

        if numbered_queries:
            queries = [q.strip() for q in numbered_queries if q.strip() and len(q.strip()) > 5]

        # If no numbered queries, try to split by common delimiters
        if not queries:
            for delimiter in [';', '|', '\n\n']:
                parts = description.split(delimiter)
                if len(parts) > 1:
                    queries = [p.strip() for p in parts if p.strip() and len(p.strip()) > 5]
                    break

        return queries[:5]  # Limit to 5 queries

    def _generate_queries_from_description(self, description: str) -> List[str]:
        """Generate optimized queries from verbose description."""
        queries = []

        # Extract key domain terms
        domain_terms = self._extract_terms(description, "domain_terms")
        tech_terms = self._extract_terms(description, "technical_keywords")
        app_terms = self._extract_terms(description, "application_keywords")
        time_terms = self._extract_terms(description, "time_keywords")

        # Generate Query 1: Core concept (domain terms + technical approach)
        if domain_terms or tech_terms:
            q1 = self._build_query(
                required_terms=domain_terms[:2],
                optional_terms=tech_terms[:2],
                exclude_terms=[]
            )
            if q1:
                queries.append(q1)

        # Generate Query 2: Application-focused (domain + application + time)
        if domain_terms and app_terms:
            q2 = self._build_query(
                required_terms=domain_terms[:1],
                optional_terms=app_terms[:2],
                time_filter=time_terms[0] if time_terms else None
            )
            if q2:
                queries.append(q2)

        # Generate Query 3: Technical depth (technical terms + methodology)
        if tech_terms:
            q3 = self._build_query(
                required_terms=tech_terms[:2],
                optional_terms=domain_terms[:1],
                exclude_terms=[]
            )
            if q3:
                queries.append(q3)

        # Generate Query 4: Specific focus if multiple domain/app terms exist
        if len(domain_terms) > 1 or len(app_terms) > 1:
            remaining_domain = domain_terms[1:] if len(domain_terms) > 1 else []
            remaining_app = app_terms[1:] if len(app_terms) > 1 else []

            q4 = self._build_query(
                required_terms=remaining_domain or remaining_app,
                optional_terms=[],
                time_filter=time_terms[0] if time_terms else None
            )
            if q4:
                queries.append(q4)

        # If no queries generated, create a fallback generic query
        if not queries:
            # Extract any substantial noun phrases
            words = description.split()
            important_words = [w.lower() for w in words
                             if len(w) > 4 and not w.lower() in ['search', 'collect', 'gather', 'information']]
            if important_words:
                q_fallback = " AND ".join(important_words[:3])
                queries.append(q_fallback)

        # Limit to 5 queries maximum and remove duplicates
        queries = list(dict.fromkeys(queries))  # Remove duplicates while preserving order
        return queries[:5]

    def _extract_terms(self, text: str, term_type: str, limit: int = 5) -> List[str]:
        """Extract specific types of terms from text."""
        if term_type not in self.keyword_extractors:
            return []

        pattern = self.keyword_extractors[term_type]
        matches = re.findall(pattern, text, re.IGNORECASE)
        # Normalize and deduplicate
        terms = list(dict.fromkeys([m.lower() for m in matches]))
        return terms[:limit]

    def _build_query(self, required_terms: List[str], optional_terms: List[str] = None,
                     exclude_terms: List[str] = None, time_filter: str = None) -> str:
        """
        Build a Boolean search query from terms.

        Args:
            required_terms: Terms that MUST be in results (joined with AND)
            optional_terms: Terms that MAY be in results (joined with OR)
            exclude_terms: Terms to exclude
            time_filter: Optional time range filter

        Returns:
            Formatted Boolean search query
        """
        if not required_terms:
            return ""

        # Build required part
        required_part = " AND ".join(f'"{term}"' if " " in term else term
                                    for term in required_terms)

        # Build optional part
        optional_part = ""
        if optional_terms:
            optional_str = " OR ".join(f'"{term}"' if " " in term else term
                                      for term in optional_terms)
            optional_part = f" AND ({optional_str})"

        # Build exclusion part
        exclude_part = ""
        if exclude_terms:
            exclude_str = " AND NOT ".join(exclude_terms)
            exclude_part = f" AND NOT {exclude_str}"

        # Combine parts
        query = required_part + optional_part + exclude_part

        # Add time filter if provided
        if time_filter:
            # Only add year ranges, not subjective terms like "recent"
            if re.search(r"\d{4}", time_filter):
                year_match = re.search(r"(\d{4})[-–]?(\d{4})?", time_filter)
                if year_match:
                    query += f" {year_match.group(0)}"

        return query.strip()


# Create global optimizer instance
_optimizer = QueryOptimizer()


@tool
def optimize_search_queries(description: str) -> str:
    """
    Convert verbose search descriptions into multiple specific search queries.

    This tool analyzes a lengthy description of what to search for and converts it into
    2-5 concise, Boolean-formatted queries suitable for academic search engines like arXiv.

    Args:
        description: The verbose description of what to search for (can be a full sentence or paragraph)

    Returns:
        JSON string containing:
        - queries: List of optimized search queries
        - explanation: Brief explanation of the query strategy

    Example:
        Input: "Search academic databases (arXiv, IEEE Xplore, ACM Digital Library) for information 
                related to AI glasses. Gather historical data such as timeline of development, early 
                pioneers, and foundational work."

        Output: {
            "queries": [
                "\"AI glasses\" OR \"augmented reality glasses\" AND computer vision",
                "smart glasses OR head-mounted display AND applications",
                "wearable display AND optical design OR micro-display technology"
            ],
            "explanation": "Query 1 focuses on core concept with technical approach. Query 2 explores applications. Query 3 dives into technical components."
        }
    """
    try:
        optimized_queries = _optimizer.optimize_description(description)

        if not optimized_queries:
            return json.dumps({
                "queries": [],
                "explanation": "Unable to extract meaningful search queries from the provided description.",
                "error": "No valid queries could be generated"
            })

        # Create explanation
        explanations = []
        if len(optimized_queries) > 0:
            explanations.append("Query 1: Core concept with primary technical focus")
        if len(optimized_queries) > 1:
            explanations.append("Query 2: Application-domain specific search")
        if len(optimized_queries) > 2:
            explanations.append("Query 3: Technical depth and methodology focus")
        if len(optimized_queries) > 3:
            explanations.append("Query 4: Extended coverage of related domains")
        if len(optimized_queries) > 4:
            explanations.append("Query 5: Additional refinement or alternative perspectives")

        return json.dumps({
            "queries": optimized_queries,
            "explanation": " | ".join(explanations),
            "count": len(optimized_queries)
        }, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Error optimizing search queries: {str(e)}")
        return json.dumps({
            "queries": [],
            "explanation": f"Error during query optimization: {str(e)}",
            "error": str(e)
        })


if __name__ == "__main__":
    # Test examples
    test_descriptions = [
        "Search academic databases (arXiv, IEEE Xplore, ACM Digital Library) for information related to AI glasses. Gather historical data such as timeline of development, early pioneers, and foundational work. Also collect current data including latest technological advances, market situation, and recent product launches.",
        "Find information about machine learning approaches in medical imaging, including deep learning techniques, convolutional neural networks, and their applications in diagnosis and treatment planning.",
        "Research quantum computing and its applications in cryptography, including quantum algorithms, post-quantum cryptography, and security implications.",
    ]

    optimizer = QueryOptimizer()
    for desc in test_descriptions:
        print(f"\nOriginal: {desc[:80]}...")
        queries = optimizer.optimize_description(desc)
        print(f"Optimized Queries:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
