# CLAUDE.md

## Proyecto

face-net-api — API FastAPI (async) para gestión de exámenes con supervisión (evidencias de cámara/pantalla). PostgreSQL + SQLAlchemy 2.0 async + Alembic. Gestión de dependencias con `uv`.

## Comandos

```bash
uv run fastapi dev            # servidor de desarrollo (http://localhost:8000)
uv run alembic upgrade head   # aplicar migraciones
uv run alembic revision --autogenerate -m "msg"  # nueva migración
```

## Arquitectura: modular

Cada módulo de dominio vive en `src/app/modules/<modulo>/` y contiene sus propias capas:

```
src/
└── app/
    ├── common/                     # código compartido entre módulos
    │   ├── database/
    │   │   ├── session.py          # engine y async_sessionmaker
    │   │   └── dependencies/
    │   │       └── get_async_session.py
    │   ├── model/
    │   │   └── base_model.py       # Base declarativa (SQLAlchemy)
    │   └── setting/
    │       └── base_setting.py     # settings (pydantic-settings, lee .env)
    │
    └── modules/
        └── <modulo>/               # p. ej. user, person, role, auth, exam,
            │                       #        question, exam_attempt, evidence
            ├── __init__.py
            ├── controller/         # paquete: routers FastAPI
            │   ├── __init__.py
            │   └── <modulo>_controller.py
            ├── service/            # paquete: lógica de negocio
            │   ├── __init__.py
            │   └── <modulo>_service.py
            ├── repository/         # paquete: acceso a datos (SQLAlchemy)
            │   ├── __init__.py
            │   └── <modulo>_repository.py
            ├── model/              # paquete: modelos ORM (tablas)
            │   ├── __init__.py
            │   └── <modulo>_model.py
            └── dto/                # paquete: schemas Pydantic
                ├── __init__.py
                └── <modulo>_dto.py
```

Punto de entrada: `main.py` (raíz) — crea `FastAPI()` e incluye los routers de cada módulo.

### Responsabilidad de cada capa

- **controller**: define `APIRouter`, valida entrada vía DTOs, delega al service. Sin lógica de negocio ni queries.
- **service**: reglas de negocio, validaciones de dominio, transacciones. No conoce HTTP.
- **repository**: única capa que ejecuta queries. Recibe `AsyncSession`, devuelve modelos ORM.
- **model**: clases SQLAlchemy que heredan de `Base` (`common/model/base_model.py`).
- **dto**: Pydantic `BaseModel`; separar DTOs de creación, actualización y respuesta (p. ej. `UserCreate`, `UserUpdate`, `UserResponse`).

### Reglas

- Flujo de dependencias: controller → service → repository. Nunca saltar capas ni invertir la dirección.
- Un módulo puede usar services de otro módulo, pero no sus repositories.
- Todo async: endpoints, services y repositories usan `async def` y `AsyncSession`.
- La sesión de BD se inyecta con `Depends(get_async_session)` en el controller y se propaga hacia abajo.
- Los modelos ORM nunca salen del API: los controllers responden siempre DTOs.

## Base de datos

- Esquemas PostgreSQL: `core` (user, person, role, user_role, Document) y `academic` (exam, question, answer_option, exam_attempt, attempt_answer, evidence).
- Fuente de verdad del diseño: `db.dbml`. Mantenerlo sincronizado con los modelos.
- Migraciones en `migrations/versions/`; nuevos modelos deben importarse en `migrations/env.py` para autogenerate.
- Config de conexión: `DATABASE_URL` en `.env` (ver `.env.example`).
