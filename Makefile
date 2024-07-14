run:
	@docker compose up --build

stop:
	@echo "stopping docker conatiner"
	@docker compose down

clean: stop
	@echo "Removing docker containers and volumes"
	@docker volume rm -f pg_cluster_master_data pg_cluster_replica_data
	@echo "Run 'make docker-run' to start again"