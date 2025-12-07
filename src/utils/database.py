"""
Database Layer for Anubis Intelligence Platform
Consolidated database management with SQLAlchemy ORM
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
    desc,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from config import DATABASE_DIR, config
from src.utils.validators import logger

Base = declarative_base()


class ReportMetadata(Base):
    """ORM model for report metadata"""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    classification = Column(String(50), nullable=False)
    tlp_level = Column(String(10), nullable=False)
    title = Column(String(255), nullable=False)
    author = Column(String(200), nullable=False)
    organization = Column(String(255), nullable=False)
    target_name = Column(String(255), nullable=True)
    target_alias = Column(String(255), nullable=True)
    status = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)
    redaction_count = Column(Integer, default=0)
    page_count = Column(Integer, default=1)
    file_path = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=True)
    version = Column(Integer, default=1)
    is_encrypted = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accessed_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    archived = Column(Integer, default=0)
    custom_metadata = Column(JSON, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "report_id": self.report_id,
            "classification": self.classification,
            "tlp_level": self.tlp_level,
            "title": self.title,
            "author": self.author,
            "organization": self.organization,
            "target_name": self.target_name,
            "target_alias": self.target_alias,
            "status": self.status,
            "summary": self.summary,
            "redaction_count": self.redaction_count,
            "page_count": self.page_count,
            "file_path": self.file_path,
            "version": self.version,
            "is_encrypted": bool(self.is_encrypted),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "archived": bool(self.archived),
            "custom_metadata": self.custom_metadata,
        }


class ReportVersion(Base):
    """ORM model for report versioning"""

    __tablename__ = "report_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(100), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)
    change_summary = Column(Text, nullable=True)
    modified_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "report_id": self.report_id,
            "version": self.version,
            "change_summary": self.change_summary,
            "modified_by": self.modified_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(Base):
    """ORM model for audit logging"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(100), nullable=True, index=True)
    event_type = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    user = Column(String(200), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "report_id": self.report_id,
            "event_type": self.event_type,
            "action": self.action,
            "user": self.user,
            "details": self.details,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DatabaseManager:
    """Main database manager for Anubis Intelligence Platform"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = config.database.sqlite_path

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=config.database.echo_sql,
            connect_args={"check_same_thread": False},
        )

        self.SessionLocal = sessionmaker(bind=self.engine)
        self._init_database()

    def _init_database(self) -> None:
        try:
            Base.metadata.create_all(self.engine)
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def get_session(self) -> Session:
        return self.SessionLocal()

    def create_report(
        self,
        report_id: str,
        classification: str,
        tlp_level: str,
        title: str,
        author: str,
        organization: str,
        target_name: str = None,
        target_alias: str = None,
        status: str = None,
        summary: str = None,
        data: Dict[str, Any] = None,
        redaction_count: int = 0,
        page_count: int = 1,
        file_path: str = None,
        file_hash: str = None,
        is_encrypted: bool = False,
        custom_metadata: Dict[str, Any] = None,
    ) -> Optional[ReportMetadata]:
        session = self.get_session()
        try:
            existing = (
                session.query(ReportMetadata).filter_by(report_id=report_id).first()
            )
            if existing:
                logger.warning(f"Report already exists: {report_id}")
                # Return a detached copy with the ID
                session.expunge(existing)
                return existing

            report = ReportMetadata(
                report_id=report_id,
                classification=classification,
                tlp_level=tlp_level,
                title=title,
                author=author,
                organization=organization,
                target_name=target_name,
                target_alias=target_alias,
                status=status,
                summary=summary,
                data=data,
                redaction_count=redaction_count,
                page_count=page_count,
                file_path=file_path,
                file_hash=file_hash,
                is_encrypted=1 if is_encrypted else 0,
                custom_metadata=custom_metadata,
            )

            session.add(report)
            session.commit()
            # Expunge the object so it's detached from the session
            session.expunge(report)
            logger.info(f"Report created: {report_id}")
            return report

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create report: {e}")
            return None
        finally:
            session.close()

    def get_report(self, report_id: str) -> Optional[ReportMetadata]:
        session = self.get_session()
        try:
            report = (
                session.query(ReportMetadata).filter_by(report_id=report_id).first()
            )
            if report:
                report.accessed_at = datetime.utcnow()
                session.commit()
            return report
        except Exception as e:
            logger.error(f"Failed to retrieve report: {e}")
            return None
        finally:
            session.close()

    def list_reports(
        self,
        classification: str = None,
        author: str = None,
        target_name: str = None,
        archived: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ReportMetadata]:
        session = self.get_session()
        try:
            query = session.query(ReportMetadata)

            if classification:
                query = query.filter_by(classification=classification)
            if author:
                query = query.filter_by(author=author)
            if target_name:
                query = query.filter(
                    ReportMetadata.target_name.ilike(f"%{target_name}%")
                )

            query = query.filter_by(archived=1 if archived else 0)
            reports = (
                query.order_by(desc(ReportMetadata.created_at))
                .limit(limit)
                .offset(offset)
                .all()
            )

            return reports

        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return []
        finally:
            session.close()

    def update_report(self, report_id: str, **kwargs) -> Optional[ReportMetadata]:
        session = self.get_session()
        try:
            report = (
                session.query(ReportMetadata).filter_by(report_id=report_id).first()
            )

            if not report:
                logger.warning(f"Report not found: {report_id}")
                return None

            allowed_fields = {
                "title",
                "summary",
                "status",
                "page_count",
                "redaction_count",
                "is_encrypted",
                "custom_metadata",
                "author",
                "organization",
                "target_name",
                "target_alias",
                "file_path",
                "file_hash",
                "version",
                "data",
            }

            for key, value in kwargs.items():
                if key not in allowed_fields:
                    continue

                if key == "is_encrypted":
                    setattr(report, key, 1 if value else 0)
                    continue

                if key in ("custom_metadata", "data"):
                    existing = getattr(report, key) or {}
                    if isinstance(existing, dict) and isinstance(value, dict):
                        merged = {**existing, **value}
                        setattr(report, key, merged)
                    else:
                        setattr(report, key, value)
                    continue

                setattr(report, key, value)

            report.updated_at = datetime.utcnow()
            session.commit()
            logger.info(f"Report updated: {report_id}")
            return report

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update report: {e}")
            return None
        finally:
            session.close()

    def search_reports(self, query_text: str, limit: int = 50) -> List[ReportMetadata]:
        session = self.get_session()
        try:
            reports = (
                session.query(ReportMetadata)
                .filter(
                    (ReportMetadata.title.ilike(f"%{query_text}%"))
                    | (ReportMetadata.summary.ilike(f"%{query_text}%"))
                    | (ReportMetadata.target_name.ilike(f"%{query_text}%"))
                )
                .order_by(desc(ReportMetadata.created_at))
                .limit(limit)
                .all()
            )
            return reports
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
        finally:
            session.close()

    def get_statistics(self) -> Dict[str, Any]:
        session = self.get_session()
        try:
            total_reports = session.query(ReportMetadata).count()
            archived_reports = (
                session.query(ReportMetadata).filter_by(archived=1).count()
            )
            encrypted_reports = (
                session.query(ReportMetadata).filter_by(is_encrypted=1).count()
            )

            classifications = {}
            for record in session.query(
                ReportMetadata.classification, ReportMetadata.__table__.c.id
            ).all():
                classification = record[0]
                classifications[classification] = (
                    classifications.get(classification, 0) + 1
                )

            return {
                "total_reports": total_reports,
                "archived_reports": archived_reports,
                "active_reports": total_reports - archived_reports,
                "encrypted_reports": encrypted_reports,
                "by_classification": classifications,
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
        finally:
            session.close()

    def archive_report(self, report_id: str) -> bool:
        session = self.get_session()
        try:
            report = (
                session.query(ReportMetadata).filter_by(report_id=report_id).first()
            )
            if not report:
                logger.warning(f"Report not found: {report_id}")
                return False

            report.archived = 1
            report.archived_at = datetime.utcnow()
            session.commit()
            logger.info(f"Report archived: {report_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to archive report: {e}")
            return False
        finally:
            session.close()

    def delete_report(self, report_id: str) -> bool:
        session = self.get_session()
        try:
            report = (
                session.query(ReportMetadata).filter_by(report_id=report_id).first()
            )
            if not report:
                logger.warning(f"Report not found: {report_id}")
                return False

            session.delete(report)
            session.commit()
            logger.warning(f"Report deleted: {report_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete report: {e}")
            return False
        finally:
            session.close()

    def create_version(
        self,
        report_id: str,
        version: int,
        data: Dict[str, Any],
        change_summary: str = "",
        modified_by: str = "SYSTEM",
    ) -> Optional[ReportVersion]:
        """Create a version record for a report"""
        session = self.get_session()
        try:
            version_record = ReportVersion(
                report_id=report_id,
                version=version,
                data=data,
                change_summary=change_summary,
                modified_by=modified_by,
            )
            session.add(version_record)
            session.commit()
            session.expunge(version_record)
            logger.info(f"Version created for {report_id}: v{version}")
            return version_record
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create version: {e}")
            return None
        finally:
            session.close()

    def log_audit_event(
        self,
        event_type: str,
        action: str,
        user: str = "SYSTEM",
        report_id: str = None,
        details: Dict[str, Any] = None,
    ) -> Optional[AuditLog]:
        """Log an audit event"""
        session = self.get_session()
        try:
            audit_log = AuditLog(
                event_type=event_type,
                action=action,
                user=user,
                report_id=report_id,
                details=details or {},
            )
            session.add(audit_log)
            session.commit()
            session.expunge(audit_log)
            logger.info(f"Audit logged: {event_type}/{action}")
            return audit_log
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log audit event: {e}")
            return None
        finally:
            session.close()


db = DatabaseManager()
