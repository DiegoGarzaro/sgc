## Initial Steps Django

1. Create venv:
```python
python -m venv venv
```

2. Activate venv:
```
source venv/bin/activate
```

3. Install Django (install requirements file):
```python
pip install -r requirements.txt
```

4. Verify if Django is installed successfully:
```
django-admin --version
```

5. Start new Django project:
```
django-admin startproject app .
```

6. Create database and all Django default app structure:
```python
python manage.py migrate
```

7. Create `superuser` to access Django administrator panel:
```python
python manage.py createsuperuser
```

8. Run application:
```python
python manage.py runserver
```

9. Everytime a new app is created, it's necessary to add it into `app/settings.py` in `INSTALLED_APPS`. To create a new app:
```python
python manage.py startapp brands
```

10. After changes is made in app models, enter the command below to replicate the model changes to the database:
```python
python manage.py makemigrations
```
