.PHONY: install test coverage sample-data dev-backend dev-frontend docker-up docker-down

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

sample-data:
	python scripts/generate_sample_data.py

test:
	cd backend && pytest -v

coverage:
	cd backend && pytest --cov=app --cov-report=term-missing

dev-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v
