mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

admin:
	python3 manage.py createsuperuser

email:
	python3 manage.py sendtestemail

celery:
