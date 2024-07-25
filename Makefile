mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

admin:
	python3 manage.py createsuperuser

email:
	python3 manage.py sendtestemail

celery:
	celery -A core worker -l INFO

beat:
	celery -A root beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

dumpdata:
	python3 manage.py dumpdata --indent=2 apps.Category > categories.json

loaddata:
	python3 manage.py loaddata categories

ngrok:
	ngrok http 8000