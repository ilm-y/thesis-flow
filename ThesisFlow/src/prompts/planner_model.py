# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, Field


class StepType(str, Enum):
    RESEARCH = "research"
    PROCESSING = "processing"
    ANALYSIS = "analysis"


class AnalysisType(str, Enum):
    """Types of academic analysis supported by the researcher"""
    PAPER_ANALYSIS = "paper_analysis"
    CITATION_NETWORK = "citation_network"
    TECHNICAL_BREAKDOWN = "technical_breakdown"


# ============================================================
# Academic Paper Analysis Data Structures
# ============================================================

class PaperMetadata(BaseModel):
    """Structured extraction of academic paper metadata"""
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    abstract: str = Field(default="", description="Paper abstract/summary")
    publication_year: Optional[int] = Field(default=None, description="Year of publication")
    venue: str = Field(default="", description="Journal/conference name")
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier")
    keywords: List[str] = Field(default_factory=list, description="Research keywords")
    methodology: str = Field(default="", description="Research methodology overview")
    main_contributions: List[str] = Field(default_factory=list, description="Key contributions")
    datasets_used: List[str] = Field(default_factory=list, description="Datasets employed")
    limitations: List[str] = Field(default_factory=list, description="Acknowledged limitations")
    future_work: List[str] = Field(default_factory=list, description="Suggested future directions")


class Citation(BaseModel):
    """Citation reference model"""
    id: int = Field(..., description="Citation ID for tracking")
    title: str = Field(..., description="Cited work title")
    authors: List[str] = Field(default_factory=list, description="Citation authors")
    year: Optional[int] = Field(default=None, description="Publication year")
    citation_count: Optional[int] = Field(default=None, description="Number of times cited")
    relevance_score: Optional[float] = Field(default=None, description="Relevance to current paper (0-1)")
    url: str = Field(default="", description="Reference URL")


class CitationAnalysis(BaseModel):
    """Analysis of paper's citation network and relationships"""
    total_citations: int = Field(default=0, description="Total number of citations")
    citations: List[Citation] = Field(default_factory=list, description="Citation details")
    citation_networks: Dict[str, Any] = Field(default_factory=dict, description="Citation relationship map")
    key_authors: List[str] = Field(default_factory=list, description="Most cited authors in references")
    research_foundations: List[str] = Field(default_factory=list, description="Foundational works building to this paper")
    related_papers: List[str] = Field(default_factory=list, description="Related paper references")
    novelty_assessment: str = Field(default="", description="Assessment of novelty relative to citations")


class TechnicalComponent(BaseModel):
    """Technical component breakdown"""
    name: str = Field(..., description="Component name")
    description: str = Field(..., description="Component description")
    algorithm: Optional[str] = Field(default=None, description="Algorithm used")
    implementation_details: str = Field(default="", description="How it's implemented")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies on other components")
    complexity: Optional[str] = Field(default=None, description="Time/space complexity")
    validation: Optional[str] = Field(default=None, description="How component is validated")


class TechnicalBreakdown(BaseModel):
    """Step-by-step technical breakdown of paper's contributions"""
    problem_statement: str = Field(default="", description="The problem being solved")
    proposed_solution: str = Field(default="", description="Overview of solution")
    technical_components: List[TechnicalComponent] = Field(
        default_factory=list, 
        description="Individual technical components"
    )
    mathematical_foundation: str = Field(default="", description="Mathematical basis if applicable")
    experimental_setup: str = Field(default="", description="How experiments are structured")
    results_summary: str = Field(default="", description="Key experimental results")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance comparison metrics")
    implementation_guidance: str = Field(default="", description="How to implement the approach")


class InnovationNode(BaseModel):
    """Represents an innovation or key insight from the paper"""
    title: str = Field(..., description="Innovation title")
    description: str = Field(..., description="Innovation description")
    impact_level: str = Field(default="", description="'low', 'medium', 'high', or 'groundbreaking'")
    technical_novelty: str = Field(default="", description="What's technically novel")
    application_domains: List[str] = Field(default_factory=list, description="Applicable domains")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites/dependencies")
    limitations: List[str] = Field(default_factory=list, description="Known limitations")
    future_potential: str = Field(default="", description="Potential for future development")


class Step(BaseModel):
    need_search: bool = Field(..., description="Must be explicitly set for each step")
    title: str
    description: str = Field(..., description="Specify exactly what data to collect")
    step_type: StepType = Field(..., description="Indicates the nature of the step")
    analysis_type: Optional[AnalysisType] = Field(
        default=None, 
        description="Type of analysis for academic research: paper_analysis, citation_network, or technical_breakdown"
    )
    structured_output: Optional[Union[PaperMetadata, CitationAnalysis, TechnicalBreakdown]] = Field(
        default=None,
        description="Structured output from specialized analysis"
    )
    execution_res: Optional[str] = Field(
        default=None, description="The Step execution result"
    )


class Plan(BaseModel):
    locale: str = Field(
        ..., description="e.g. 'en-US' or 'zh-CN', based on the user's language"
    )
    has_enough_context: bool
    thought: str = Field(default="", description="Thinking process for the plan")
    title: str
    analysis_mode: Optional[str] = Field(
        default="traditional",
        description="'traditional' for web research or 'deep_mining' for academic literature analysis"
    )
    steps: List[Step] = Field(
        default_factory=list,
        description="Research & Processing steps to get more context",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "has_enough_context": False,
                    "thought": (
                        "To understand the current market trends in AI, we need to gather comprehensive information."
                    ),
                    "title": "AI Market Research Plan",
                    "analysis_mode": "traditional",
                    "steps": [
                        {
                            "need_search": True,
                            "title": "Current AI Market Analysis",
                            "description": (
                                "Collect data on market size, growth rates, major players, and investment trends in AI sector."
                            ),
                            "step_type": "research",
                        }
                    ],
                },
                {
                    "has_enough_context": False,
                    "thought": "Deep analysis of academic paper on transformer models",
                    "title": "Transformer Architecture Deep Dive",
                    "analysis_mode": "deep_mining",
                    "steps": [
                        {
                            "need_search": True,
                            "title": "Extract Paper Metadata",
                            "description": "Extract title, authors, abstract, methodology from paper",
                            "step_type": "research",
                            "analysis_type": "paper_analysis"
                        },
                        {
                            "need_search": True,
                            "title": "Analyze Citation Network",
                            "description": "Map paper's citations and research foundations",
                            "step_type": "research",
                            "analysis_type": "citation_network"
                        },
                        {
                            "need_search": False,
                            "title": "Technical Breakdown",
                            "description": "Decompose technical components and innovations",
                            "step_type": "processing",
                            "analysis_type": "technical_breakdown"
                        }
                    ],
                }
            ]
        }

