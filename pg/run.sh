docker stop postgrespy_pg
docker rm postgrespy_pg
source ../.env
docker run -d -p 5440:5432 --restart=unless-stopped --name postgrespy_pg -e POSTGRES_USER=$POSTGRES_USER -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD registry.gitlab.com/dvnguyen/postgrespy/pg
sleep 10
docker logs postgrespy_pg
