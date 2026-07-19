# 🧠 RecomiendAI

Microservicio de recomendaciones colaborativas con autenticación JWT, caché Redis, PostgreSQL y tests.

## Características
- Registro/login con JWT
- Motor colaborativo (SVD con Surprise)
- Persistencia PostgreSQL + migraciones Alembic
- Caché en Redis (TTL 5 min)
- Invalidación de caché por eventos (Pub/Sub)
- Tests con pytest

## Instalación
1. Clonar, crear entorno virtual, instalar dependencias.
2. Levantar servicios con `docker-compose up -d`.
3. Configurar `.env`.
4. `flask db upgrade`
5. `python app.py`

## Endpoints principales
- `POST /auth/register` – crear usuario
- `POST /auth/login` – obtener token
- `POST /api/items` – crear ítem (requiere token)
- `POST /api/users/{id}/rate` – valorar ítem
- `GET /api/users/{id}/recommendations` – obtener recomendaciones

## Tests
`pytest tests/ -v --cov=app`
