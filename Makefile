run-docker-compose:
	docker-compose down 
	docker-compose up --build -d
	docker-compose logs -f

run-app:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-app-dev: 
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --debug

run-app-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --debug