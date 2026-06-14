"""Test settings: SQLite in-memory, fast hashing, no external services."""
from .settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Disable Pillow file storage for tests (images not needed)
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Silence logging noise during tests
import logging
logging.disable(logging.CRITICAL)
