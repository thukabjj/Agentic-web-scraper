#!/usr/bin/env python3
"""
Evidence Analysis Adapter for Deep Research

This adapter provides intelligent evidence extraction, analysis, and cross-referencing
capabilities using LLM integration.
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.domain.models import (Citation, ContentType, Evidence, EvidenceType,
                                PageContent)
from core.domain.ports import EvidenceAnalysisPort, LLMPort


class EvidenceAnalysisAdapter(EvidenceAnalysisPort):
    """
    Adapter for analyzing and validating evidence using LLM capabilities
    """

    def __init__(self, llm_adapter: LLMPort):
        self.llm_adapter = llm_adapter

    async def extract_evidence(
        self,
        content: PageContent,
        research_context: str
    ) -> List[Evidence]:
        """
        Extract relevant evidence from page content using LLM analysis

        Args:
            content: Page content to analyze
            research_context: Research question or context

        Returns:
            List of extracted evidence pieces
        """
        # Create prompt for evidence extraction
        prompt = f"""
        Analyze the following content and extract key pieces of evidence relevant to
        the research question: "{research_context}"

        Content from {content.url}:
        {content.content[:4000]}...

        Please extract evidence in the following JSON format:
        {{
            "evidence_pieces": [
                {{
                    "content": "Direct quote or paraphrased evidence",
                    "evidence_type": "primary|secondary|supporting",
                    "relevance_score": 0.8,
                    "confidence_score": 0.9,
                    "excerpt": "Relevant excerpt from the source",
                    "tags": ["tag1", "tag2"]
                }}
            ]
        }}

        Focus on factual claims, data points, expert opinions, and research findings.
        Exclude opinions, advertisements, or irrelevant content.
        """

        try:
            # Get LLM analysis
            response = await self._get_llm_completion(prompt)

            # Parse the response
            evidence_data = self._parse_evidence_response(response)

            # Convert to Evidence objects
            evidence_list = []
            for item in evidence_data.get("evidence_pieces", []):
                citation = Citation(
                    url=content.url,
                    title=content.title or "Untitled",
                    excerpt=item.get("excerpt", item.get("content", "")[:200]),
                    timestamp=content.timestamp,
                    source_type=self._determine_source_type(content.url),
                    page_content_id=content.url  # Using URL as ID for now
                )

                evidence = Evidence(
                    content=item.get("content", ""),
                    evidence_type=self._parse_evidence_type(item.get("evidence_type", "supporting")),
                    citation=citation,
                    relevance_score=float(item.get("relevance_score", 0.5)),
                    confidence_score=float(item.get("confidence_score", 0.5)),
                    tags=item.get("tags", [])
                )

                evidence_list.append(evidence)

            return evidence_list

        except Exception as e:
            # Fallback to simple extraction
            return await self._fallback_evidence_extraction(content, research_context)

    async def cross_reference_evidence(
        self,
        evidence_list: List[Evidence],
        threshold: float = 0.7
    ) -> Dict[str, List[Evidence]]:
        """
        Cross-reference evidence to find supporting and contradicting claims

        Args:
            evidence_list: List of evidence to cross-reference
            threshold: Similarity threshold for grouping evidence

        Returns:
            Dictionary grouping evidence by similar claims
        """
        if len(evidence_list) < 2:
            return {}

        # Create prompt for cross-referencing
        evidence_summaries = []
        for i, evidence in enumerate(evidence_list):
            evidence_summaries.append(f"Evidence {i+1}: {evidence.content[:200]}...")

        prompt = f"""
        Analyze these {len(evidence_list)} pieces of evidence and identify:
        1. Similar claims that support each other
        2. Contradictory claims
        3. Related topics or themes

        Evidence to analyze:
        {chr(10).join(evidence_summaries)}

        Return JSON format:
        {{
            "similar_groups": [
                {{
                    "theme": "Description of similar theme",
                    "evidence_indices": [0, 2, 4],
                    "similarity_score": 0.85
                }}
            ],
            "contradictions": [
                {{
                    "evidence_a": 0,
                    "evidence_b": 3,
                    "contradiction_type": "direct_contradiction|partial_contradiction",
                    "description": "Brief description of contradiction"
                }}
            ]
        }}
        """

        try:
            response = await self._get_llm_completion(prompt)
            analysis = self._parse_json_response(response)

            # Group evidence by similar claims
            grouped_evidence = {}

            for group in analysis.get("similar_groups", []):
                theme = group.get("theme", "Unknown theme")
                indices = group.get("evidence_indices", [])

                grouped_evidence[theme] = [
                    evidence_list[i] for i in indices
                    if 0 <= i < len(evidence_list)
                ]

            # Add contradictions as separate groups
            for contradiction in analysis.get("contradictions", []):
                desc = contradiction.get("description", "Contradiction detected")
                idx_a = contradiction.get("evidence_a", -1)
                idx_b = contradiction.get("evidence_b", -1)

                if 0 <= idx_a < len(evidence_list) and 0 <= idx_b < len(evidence_list):
                    key = f"CONTRADICTION: {desc}"
                    grouped_evidence[key] = [evidence_list[idx_a], evidence_list[idx_b]]

            return grouped_evidence

        except Exception:
            # Fallback to simple similarity matching
            return await self._fallback_cross_reference(evidence_list, threshold)

    async def evaluate_evidence_quality(
        self,
        evidence: Evidence
    ) -> float:
        """
        Evaluate the quality and reliability of evidence

        Args:
            evidence: Evidence to evaluate

        Returns:
            Quality score between 0.0 and 1.0
        """
        prompt = f"""
        Evaluate the quality and reliability of this evidence on a scale of 0.0 to 1.0:

        Evidence: {evidence.content}
        Source: {evidence.citation.url}
        Source Type: {evidence.citation.source_type}

        Consider factors:
        - Factual accuracy and specificity
        - Source authority and credibility
        - Recency and relevance
        - Supporting data or references
        - Potential bias or opinion vs fact

        Respond with just the numerical score (e.g., 0.85):
        """

        try:
            response = await self._get_llm_completion(prompt)
            score = float(response.strip())
            return max(0.0, min(1.0, score))
        except Exception:
            # Fallback scoring based on source type and other factors
            return self._fallback_quality_scoring(evidence)

    async def detect_contradictions(
        self,
        evidence_list: List[Evidence]
    ) -> List[Dict[str, Any]]:
        """
        Detect contradictory evidence within a list

        Args:
            evidence_list: List of evidence to check for contradictions

        Returns:
            List of detected contradictions
        """
        if len(evidence_list) < 2:
            return []

        contradictions = []

        # Compare each pair of evidence
        for i in range(len(evidence_list)):
            for j in range(i + 1, len(evidence_list)):
                evidence_a = evidence_list[i]
                evidence_b = evidence_list[j]

                prompt = f"""
                Analyze these two pieces of evidence and determine if they contradict each other:

                Evidence A: {evidence_a.content}
                Source A: {evidence_a.citation.url}

                Evidence B: {evidence_b.content}
                Source B: {evidence_b.citation.url}

                Return JSON:
                {{
                    "is_contradiction": true/false,
                    "contradiction_type": "direct|partial|contextual|none",
                    "description": "Brief explanation of contradiction or why not contradictory",
                    "confidence": 0.85
                }}
                """

                try:
                    response = await self._get_llm_completion(prompt)
                    analysis = self._parse_json_response(response)

                    if analysis.get("is_contradiction", False):
                        contradictions.append({
                            "evidence_a_index": i,
                            "evidence_b_index": j,
                            "evidence_a": evidence_a,
                            "evidence_b": evidence_b,
                            "contradiction_type": analysis.get("contradiction_type", "unknown"),
                            "description": analysis.get("description", "Contradiction detected"),
                            "confidence": float(analysis.get("confidence", 0.5))
                        })

                except Exception:
                    continue  # Skip this pair if analysis fails

        return contradictions

    async def _get_llm_completion(self, prompt: str) -> str:
        """Get completion from LLM adapter"""
        # For now, we'll use a simple approach - in a real implementation,
        # you might want to add specific methods to the LLM adapter
        try:
            # Simulate LLM call - replace with actual implementation
            return await self.llm_adapter.clean_content(prompt, ContentType.TEXT)
        except Exception:
            return "{}"

    def _parse_evidence_response(self, response: str) -> Dict:
        """Parse LLM response for evidence extraction"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return {"evidence_pieces": []}
        except json.JSONDecodeError:
            return {"evidence_pieces": []}

    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON response from LLM"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {}
        except json.JSONDecodeError:
            return {}

    def _parse_evidence_type(self, type_str: str) -> EvidenceType:
        """Parse evidence type from string"""
        type_map = {
            "primary": EvidenceType.PRIMARY,
            "secondary": EvidenceType.SECONDARY,
            "supporting": EvidenceType.SUPPORTING,
            "contradicting": EvidenceType.CONTRADICTING
        }
        return type_map.get(type_str.lower(), EvidenceType.SUPPORTING)

    def _determine_source_type(self, url: str) -> str:
        """Determine source type from URL"""
        url_lower = url.lower()

        if any(domain in url_lower for domain in ['.edu', 'scholar.google', 'pubmed', 'arxiv']):
            return "academic"
        elif any(domain in url_lower for domain in ['github.com', 'docs.', 'documentation']):
            return "documentation"
        elif any(domain in url_lower for domain in ['news', 'reuters', 'bbc', 'cnn']):
            return "news"
        else:
            return "web"

    async def _fallback_evidence_extraction(
        self,
        content: PageContent,
        research_context: str
    ) -> List[Evidence]:
        """Fallback evidence extraction using simple heuristics"""
        evidence_list = []

        # Simple content chunking
        paragraphs = content.content.split('\n\n')

        for paragraph in paragraphs[:5]:  # Limit to first 5 paragraphs
            if len(paragraph.strip()) > 100:  # Minimum length
                citation = Citation(
                    url=content.url,
                    title=content.title or "Untitled",
                    excerpt=paragraph[:200],
                    timestamp=content.timestamp,
                    source_type=self._determine_source_type(content.url)
                )

                evidence = Evidence(
                    content=paragraph.strip(),
                    evidence_type=EvidenceType.SUPPORTING,
                    citation=citation,
                    relevance_score=0.5,
                    confidence_score=0.5
                )

                evidence_list.append(evidence)

        return evidence_list

    async def _fallback_cross_reference(
        self,
        evidence_list: List[Evidence],
        threshold: float
    ) -> Dict[str, List[Evidence]]:
        """Fallback cross-referencing using simple similarity"""
        # Simple keyword-based grouping
        groups = {}

        for evidence in evidence_list:
            # Extract keywords from content
            words = evidence.content.lower().split()
            keywords = [w for w in words if len(w) > 4][:5]  # Top 5 keywords

            key = f"Topic: {', '.join(keywords[:2])}"
            if key not in groups:
                groups[key] = []
            groups[key].append(evidence)

        return groups

    def _fallback_quality_scoring(self, evidence: Evidence) -> float:
        """Fallback quality scoring using simple heuristics"""
        score = 0.5  # Base score

        # Source type factor
        source_scores = {
            "academic": 0.9,
            "documentation": 0.8,
            "news": 0.7,
            "web": 0.5
        }
        score = source_scores.get(evidence.citation.source_type, 0.5)

        # Content length factor
        if len(evidence.content) > 200:
            score += 0.1

        # Recency factor (within last year)
        if evidence.citation.timestamp:
            days_old = (datetime.now() - evidence.citation.timestamp).days
            if days_old < 365:
                score += 0.1

        return min(1.0, score)
