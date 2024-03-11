up:
	@docker-compose up

down:
	@docker-compose down

upd:
	@docker-compose up -d

exec-%:
	@docker exec -it $* bash

