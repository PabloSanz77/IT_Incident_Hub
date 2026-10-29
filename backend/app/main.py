import logging
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text, create_engine, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("incident_hub")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./incident_hub.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class Status(str, Enum):
    NUEVO = "NUEVO"
    ASIGNADO = "ASIGNADO"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"
    CERRADO = "CERRADO"

class Priority(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"

class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    priority: Mapped[Priority] = mapped_column(SAEnum(Priority), default=Priority.MEDIA, nullable=False)
    reporter: Mapped[str] = mapped_column(String(120), nullable=False)
    technician: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[Status] = mapped_column(SAEnum(Status), default=Status.NUEVO, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    comments: Mapped[list["IncidentComment"]] = relationship(back_populates="incident", cascade="all, delete-orphan")

class IncidentComment(Base):
    __tablename__ = "incident_comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id"), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    incident: Mapped[Incident] = relationship(back_populates="comments")

class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=3)
    category: str = Field(min_length=2, max_length=80)
    priority: Priority = Priority.MEDIA
    reporter: str = Field(min_length=2, max_length=120)

class IncidentUpdate(BaseModel):
    technician: str | None = None
    status: Status | None = None
    priority: Priority | None = None

class CommentCreate(BaseModel):
    author: str = Field(min_length=2, max_length=120)
    body: str = Field(min_length=1, max_length=2000)

class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    incident_id: int
    author: str
    body: str
    created_at: datetime

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    category: str
    priority: Priority
    reporter: str
    technician: str | None
    status: Status
    created_at: datetime

app = FastAPI(title="IT Incident Hub API", version="0.1.0", description="API inicial para gestión de incidentes TI")
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in origins], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok", "service": "incident-hub-api"}

@app.post("/incidents", response_model=IncidentOut, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    try:
        item = Incident(**payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)

        logger.info("Incidente creado correctamente: ID=%s", item.id)
        return item

    except Exception:
        db.rollback()
        logger.exception("Error al crear un incidente")
        raise HTTPException(
            status_code=500,
            detail="Error interno al crear el incidente",
        )


@app.get("/incidents", response_model=list[IncidentOut])
def list_incidents(
    status: Status | None = None,
    priority: Priority | None = None,
    category: str | None = None,
    technician: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Incident).order_by(Incident.created_at.desc())
    if status:
        stmt = stmt.where(Incident.status == status)
    if priority:
        stmt = stmt.where(Incident.priority == priority)
    if category:
        stmt = stmt.where(Incident.category.ilike(f"%{category}%"))
    if technician:
        stmt = stmt.where(Incident.technician.ilike(f"%{technician}%"))
    return list(db.scalars(stmt).all())

@app.get("/incidents/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    item = db.get(Incident, incident_id)
    if not item:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return item

@app.patch("/incidents/{incident_id}", response_model=IncidentOut)
def update_incident(incident_id: int, payload: IncidentUpdate, db: Session = Depends(get_db)):
    item = db.get(Incident, incident_id)
    if not item:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

@app.post("/incidents/{incident_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(incident_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    item = db.get(Incident, incident_id)
    if not item:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    comment = IncidentComment(incident_id=incident_id, **payload.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@app.get("/incidents/{incident_id}/comments", response_model=list[CommentOut])
def list_comments(incident_id: int, db: Session = Depends(get_db)):
    if not db.get(Incident, incident_id):
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    return list(db.scalars(select(IncidentComment).where(IncidentComment.incident_id == incident_id).order_by(IncidentComment.created_at)).all())

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Incident)) or 0
    open_count = db.scalar(select(func.count()).select_from(Incident).where(Incident.status.in_([Status.NUEVO, Status.ASIGNADO, Status.EN_PROCESO]))) or 0
    closed_count = db.scalar(select(func.count()).select_from(Incident).where(Incident.status == Status.CERRADO)) or 0
    critical_count = db.scalar(select(func.count()).select_from(Incident).where(Incident.priority == Priority.CRITICA)) or 0
    categories = db.execute(select(Incident.category, func.count()).group_by(Incident.category)).all()
    technicians = db.execute(select(Incident.technician, func.count()).where(Incident.technician.is_not(None)).group_by(Incident.technician)).all()
    return {
        "total": total, "open": open_count, "closed": closed_count, "critical": critical_count,
        "by_category": [{"category": c, "count": n} for c, n in categories],
        "by_technician": [{"technician": t, "count": n} for t, n in technicians],
    }
