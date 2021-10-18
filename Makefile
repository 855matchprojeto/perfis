db-run:
	docker run --rm --name db_mc855_authenticator -p 5943:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=1234 -e POSTGRES_DB=postgres -d postgres

db-stop:
	docker stop postgres

db-shell:
	docker exec -it postgres psql -U postgres

