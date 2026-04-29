# Railway Deploy Guide

## 1. Create the project on Railway

1. Go to [railway.app](https://railway.app) → **New Project**
2. Choose **Deploy from GitHub repo** → select `sgc`
3. Railway will detect the `railway.toml` automatically

---

## 2. Add PostgreSQL

Inside the project → **+ New** → **Database** → **PostgreSQL**

Railway injects `DATABASE_URL` automatically into all services in the project.

---

## 3. Add a Volume (for media files)

Inside the **sgc service** → **Volumes** tab → **Add Volume**

- Mount path: `/app/media`

---

## 4. Set environment variables

Inside the **sgc service** → **Variables** tab, add:

| Variable | Value |
|---|---|
| `SECRET_KEY` | Generate: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourapp.up.railway.app` (update after first deploy) |
| `MEDIA_ROOT` | `/app/media` |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` | Your Google OAuth client ID |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` | Your **new** Google OAuth secret (rotate it) |

`DATABASE_URL` is already injected by the PostgreSQL plugin — do not add it manually.

---

## 5. Deploy

Push to `main` (or click **Deploy** in Railway). Railway runs automatically:

```
uv sync
python manage.py collectstatic --no-input
python manage.py migrate --no-input
gunicorn app.wsgi:application --bind 0.0.0.0:$PORT --workers 2
```

---

## 6. Update ALLOWED_HOSTS

After the first deploy, Railway assigns a domain like `sgc-production.up.railway.app`.

Update the `ALLOWED_HOSTS` variable to that domain, then redeploy.

To use a custom domain: **Settings** → **Networking** → **Custom Domain**.

---

## 7. Update Google OAuth redirect URIs

Go to [Google Cloud Console](https://console.cloud.google.com) → your OAuth app → **Authorized redirect URIs**

Add:
```
https://yourapp.up.railway.app/oauth/complete/google-oauth2/
```

Remove the old PythonAnywhere URI.

---

## 8. Migrate existing media files from PythonAnywhere

```bash
# On PythonAnywhere console — create a tarball
tar -czf media_backup.tar.gz media/

# Locally — download it
scp youruser@ssh.pythonanywhere.com:~/sgc/media_backup.tar.gz .

# Use Railway CLI to upload
npm install -g @railway/cli
railway login
railway link        # link to your project
railway run bash    # open a shell on the running container
# inside the container: extract the tarball into /app/media
```

---

## 9. Cancel PythonAnywhere

Once the app is working on Railway and media files are migrated, cancel your PythonAnywhere subscription.

---

## Useful Railway CLI commands

```bash
railway logs          # tail live logs
railway run bash      # shell into the running container
railway run python manage.py createsuperuser
railway run python manage.py shell
```
