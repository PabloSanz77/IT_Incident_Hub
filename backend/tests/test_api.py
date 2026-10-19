from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, Base, get_db

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

def override_get_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_and_filter_incident():
    payload = {
        "title": "Impresora sin conexión",
        "description": "La impresora del área de ventas no responde",
        "category": "Hardware",
        "priority": "ALTA",
        "reporter": "Usuario de prueba",
    }
    response = client.post("/incidents", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "NUEVO"
    incident_id = response.json()["id"]

    filtered = client.get("/incidents", params={"priority": "ALTA"})
    assert filtered.status_code == 200
    assert any(item["id"] == incident_id for item in filtered.json())

def test_update_status_and_comment():
    created = client.post("/incidents", json={
        "title": "Error de red", "description": "No hay conectividad",
        "category": "Redes", "priority": "CRITICA", "reporter": "Pruebas"
    }).json()
    incident_id = created["id"]

    updated = client.patch(f"/incidents/{incident_id}", json={
        "technician": "Técnico Demo", "status": "EN_PROCESO"
    })
    assert updated.status_code == 200
    assert updated.json()["status"] == "EN_PROCESO"

    comment = client.post(f"/incidents/{incident_id}/comments", json={
        "author": "Técnico Demo", "body": "Se inicia el diagnóstico"
    })
    assert comment.status_code == 201
    assert comment.json()["incident_id"] == incident_id
