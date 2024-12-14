hello:
	echo "Hello, World"

runserver:
	cd ./reportassistant && \
	poetry run manage.py makemigrations && \
	poetry run manage.py migrate && \
	poetry run python manage.py runserver


start_worker:
		cd ./reportassistant && \
		poetry run python manage.py db_worker

makemessages:
	cd ./reportassistant && \
	django-admin makemessages -l en  && \
	django-admin makemessages -l hu