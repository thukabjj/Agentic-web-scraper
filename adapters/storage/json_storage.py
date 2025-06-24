#!/usr/bin/env python3
"""
JSON-based storage adapter for persisting crawl data
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from core.domain.models import (Citation, CrawlSession, Evidence, PageContent,
                                ResearchProject, ResearchStage)
from core.domain.ports import StorageAdapterPort


class JsonStorageAdapter(StorageAdapterPort):
    """JSON file-based storage implementation"""

    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

        # Create subdirectories
        self.sessions_path = self.base_path / "sessions"
        self.content_path = self.base_path / "content"
        self.sessions_path.mkdir(exist_ok=True)
        self.content_path.mkdir(exist_ok=True)

    async def save_session(self, session: CrawlSession) -> None:
        """Save crawl session to JSON file"""
        try:
            session_data = {
                "session_id": session.session_id,
                "name": session.name,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "pages_crawled": session.pages_crawled,
                "targets": [
                    {
                        "url": target.url,
                        "content_type": target.content_type.value,
                        "max_depth": target.max_depth,
                        "follow_external": target.follow_external
                    }
                    for target in session.targets
                ]
            }

            session_file = self.sessions_path / f"{session.session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            print(f"Failed to save session {session.session_id}: {e}")

    async def load_session(self, session_id: str) -> Optional[CrawlSession]:
        """Load crawl session from JSON file"""
        try:
            session_file = self.sessions_path / f"{session_id}.json"
            if not session_file.exists():
                return None

            with open(session_file, 'r') as f:
                data = json.load(f)

            # Convert back to session object
            from core.domain.models import (ContentType, CrawlStatus,
                                            CrawlTarget)

            targets = [
                CrawlTarget(
                    url=target["url"],
                    content_type=ContentType(target["content_type"]),
                    max_depth=target.get("max_depth", 1),
                    follow_external=target.get("follow_external", False)
                )
                for target in data.get("targets", [])
            ]

            session = CrawlSession(
                session_id=data["session_id"],
                name=data["name"],
                targets=targets,
                status=CrawlStatus(data["status"]),
                pages_crawled=data.get("pages_crawled", 0)
            )

            # Set created_at if available
            if "created_at" in data:
                session.created_at = datetime.fromisoformat(data["created_at"])

            return session

        except Exception as e:
            print(f"Failed to load session {session_id}: {e}")
            return None

    async def save_content(self, content: PageContent) -> None:
        """Save page content to JSON file"""
        try:
            content_data = {
                "url": content.url,
                "content": content.content,
                "content_type": content.content_type.value,
                "timestamp": content.timestamp.isoformat(),
                "title": content.title,
                "status_code": content.status_code,
                "headers": content.headers
            }

            # Create filename from URL hash
            import hashlib
            url_hash = hashlib.md5(content.url.encode()).hexdigest()[:8]
            content_file = self.content_path / f"content_{url_hash}.json"

            with open(content_file, 'w') as f:
                json.dump(content_data, f, indent=2)

        except Exception as e:
            print(f"Failed to save content for {content.url}: {e}")

    async def export_to_file(self, data: Any, filepath: str) -> None:
        """Export data to file"""
        try:
            file_path = Path(filepath)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w') as f:
                if isinstance(data, (dict, list)):
                    json.dump(data, f, indent=2, default=str)
                else:
                    f.write(str(data))

        except Exception as e:
            print(f"Failed to export to {filepath}: {e}")

    # Research-specific storage methods
    async def save_research_project(self, project: "ResearchProject") -> None:
        """Save research project to JSON file"""
        try:
            from core.domain.models import ResearchProject

            project_data = {
                "project_id": project.project_id,
                "title": project.title,
                "research_question": project.research_question,
                "description": project.description,
                "status": project.status.value,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "confidence_level": project.confidence_level,
                "findings": project.findings,
                "conclusions": project.conclusions,
                "tags": project.tags,
                "related_projects": project.related_projects,
                "stages": [
                    {
                        "stage_id": stage.stage_id,
                        "stage_type": stage.stage_type.value,
                        "description": stage.description,
                        "status": stage.status.value,
                        "queries": stage.queries,
                        "created_at": stage.created_at.isoformat(),
                        "completed_at": stage.completed_at.isoformat() if stage.completed_at else None,
                        "next_stages": stage.next_stages,
                        "targets": [
                            {
                                "url": target.url,
                                "content_type": target.content_type.value,
                                "max_depth": target.max_depth,
                                "follow_external": target.follow_external
                            }
                            for target in stage.targets
                        ],
                        "evidence_collected": [
                            {
                                "content": evidence.content,
                                "evidence_type": evidence.evidence_type.value,
                                "relevance_score": evidence.relevance_score,
                                "confidence_score": evidence.confidence_score,
                                "extracted_at": evidence.extracted_at.isoformat(),
                                "tags": evidence.tags,
                                "citation": {
                                    "url": evidence.citation.url,
                                    "title": evidence.citation.title,
                                    "excerpt": evidence.citation.excerpt,
                                    "timestamp": evidence.citation.timestamp.isoformat(),
                                    "source_type": evidence.citation.source_type,
                                    "reliability_score": evidence.citation.reliability_score,
                                    "page_content_id": evidence.citation.page_content_id
                                }
                            }
                            for evidence in stage.evidence_collected
                        ]
                    }
                    for stage in project.stages
                ],
                "all_evidence": [
                    {
                        "content": evidence.content,
                        "evidence_type": evidence.evidence_type.value,
                        "relevance_score": evidence.relevance_score,
                        "confidence_score": evidence.confidence_score,
                        "extracted_at": evidence.extracted_at.isoformat(),
                        "tags": evidence.tags,
                        "citation": {
                            "url": evidence.citation.url,
                            "title": evidence.citation.title,
                            "excerpt": evidence.citation.excerpt,
                            "timestamp": evidence.citation.timestamp.isoformat(),
                            "source_type": evidence.citation.source_type,
                            "reliability_score": evidence.citation.reliability_score,
                            "page_content_id": evidence.citation.page_content_id
                        }
                    }
                    for evidence in project.all_evidence
                ]
            }

            project_file = self.sessions_path / f"research_{project.project_id}.json"
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)

        except Exception as e:
            print(f"Failed to save research project {project.project_id}: {e}")

    async def load_research_project(self, project_id: str) -> Optional["ResearchProject"]:
        """Load research project by ID"""
        try:
            from datetime import datetime

            from core.domain.models import (Citation, ContentType, CrawlTarget,
                                            Evidence, EvidenceType,
                                            ResearchProject, ResearchStage,
                                            ResearchStageType, ResearchStatus)

            project_file = self.sessions_path / f"research_{project_id}.json"
            if not project_file.exists():
                return None

            with open(project_file, 'r') as f:
                data = json.load(f)

            # Reconstruct stages
            stages = []
            for stage_data in data.get("stages", []):
                # Reconstruct targets
                targets = []
                for target_data in stage_data.get("targets", []):
                    target = CrawlTarget(
                        url=target_data["url"],
                        content_type=ContentType(target_data["content_type"]),
                        max_depth=target_data.get("max_depth", 1),
                        follow_external=target_data.get("follow_external", False)
                    )
                    targets.append(target)

                # Reconstruct evidence
                evidence_collected = []
                for evidence_data in stage_data.get("evidence_collected", []):
                    citation = Citation(
                        url=evidence_data["citation"]["url"],
                        title=evidence_data["citation"]["title"],
                        excerpt=evidence_data["citation"]["excerpt"],
                        timestamp=datetime.fromisoformat(evidence_data["citation"]["timestamp"]),
                        source_type=evidence_data["citation"]["source_type"],
                        reliability_score=evidence_data["citation"]["reliability_score"],
                        page_content_id=evidence_data["citation"].get("page_content_id")
                    )

                    evidence = Evidence(
                        content=evidence_data["content"],
                        evidence_type=EvidenceType(evidence_data["evidence_type"]),
                        citation=citation,
                        relevance_score=evidence_data["relevance_score"],
                        confidence_score=evidence_data["confidence_score"],
                        extracted_at=datetime.fromisoformat(evidence_data["extracted_at"]),
                        tags=evidence_data.get("tags", [])
                    )
                    evidence_collected.append(evidence)

                stage = ResearchStage(
                    stage_id=stage_data["stage_id"],
                    stage_type=ResearchStageType(stage_data["stage_type"]),
                    description=stage_data["description"],
                    status=ResearchStatus(stage_data["status"]),
                    queries=stage_data.get("queries", []),
                    targets=targets,
                    evidence_collected=evidence_collected,
                    created_at=datetime.fromisoformat(stage_data["created_at"]),
                    completed_at=datetime.fromisoformat(stage_data["completed_at"]) if stage_data.get("completed_at") else None,
                    next_stages=stage_data.get("next_stages", [])
                )
                stages.append(stage)

            # Reconstruct all evidence
            all_evidence = []
            for evidence_data in data.get("all_evidence", []):
                citation = Citation(
                    url=evidence_data["citation"]["url"],
                    title=evidence_data["citation"]["title"],
                    excerpt=evidence_data["citation"]["excerpt"],
                    timestamp=datetime.fromisoformat(evidence_data["citation"]["timestamp"]),
                    source_type=evidence_data["citation"]["source_type"],
                    reliability_score=evidence_data["citation"]["reliability_score"],
                    page_content_id=evidence_data["citation"].get("page_content_id")
                )

                evidence = Evidence(
                    content=evidence_data["content"],
                    evidence_type=EvidenceType(evidence_data["evidence_type"]),
                    citation=citation,
                    relevance_score=evidence_data["relevance_score"],
                    confidence_score=evidence_data["confidence_score"],
                    extracted_at=datetime.fromisoformat(evidence_data["extracted_at"]),
                    tags=evidence_data.get("tags", [])
                )
                all_evidence.append(evidence)

            # Create project
            project = ResearchProject(
                project_id=data["project_id"],
                title=data["title"],
                research_question=data["research_question"],
                description=data["description"],
                status=ResearchStatus(data["status"]),
                stages=stages,
                all_evidence=all_evidence,
                findings=data.get("findings", ""),
                conclusions=data.get("conclusions", ""),
                confidence_level=data.get("confidence_level", 0.0),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                tags=data.get("tags", []),
                related_projects=data.get("related_projects", [])
            )

            return project

        except Exception as e:
            print(f"Failed to load research project {project_id}: {e}")
            return None

    async def list_research_projects(self) -> List["ResearchProject"]:
        """List all research projects"""
        projects = []

        try:
            for project_file in self.sessions_path.glob("research_*.json"):
                project_id = project_file.stem.replace("research_", "")
                project = await self.load_research_project(project_id)
                if project:
                    projects.append(project)
        except Exception as e:
            print(f"Failed to list research projects: {e}")

        return projects

    async def delete_research_project(self, project_id: str) -> bool:
        """Delete a research project"""
        try:
            project_file = self.sessions_path / f"research_{project_id}.json"
            if project_file.exists():
                project_file.unlink()
                return True
            return False
        except Exception as e:
            print(f"Failed to delete research project {project_id}: {e}")
            return False

    def get_storage_info(self) -> dict:
        """Get storage directory information"""
        try:
            session_count = len(list(self.sessions_path.glob("*.json")))
            content_count = len(list(self.content_path.glob("*.json")))

            return {
                "base_path": str(self.base_path),
                "sessions_count": session_count,
                "content_count": content_count
            }
        except Exception:
            return {"base_path": str(self.base_path), "error": "Cannot read storage info"}
