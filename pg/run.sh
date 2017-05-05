docker stop postgrespy_pg
docker rm postgrespy_pg
docker run -d -p 5440:5432 --name postgrespy_pg -e POSTGRES_USER=$POSTGRES_USER -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD registry.gitlab.com/dvnguyen/postgrespy/pg
