## Report Assistant Backend

### Usefully commands
`python manage.py startapp <app_name>`

### Migrate all your changes

`python manage.py makemigrations`

`python manage.py migrate`

### Runserver

`python manage.py createsuperuser`


### Create a superuser account to log in to the admin panel
`python manage.py createsuperuser`

### Check todo list for production
`python manage.py check --deploy`

### I18N
`django-admin makemessages -l en`
`django-admin makemessages -l hu`

Majd a http://localhost:8000/en/rosetta/ szerkeszük meg az új szövegek fordítását
