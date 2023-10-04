#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess

def start_redis():
    try:
        # Start Redis server as a background process
        subprocess.Popen(["redis-server"])
        print("Started Redis Server.")
    except Exception as e:
        print(f"Could not start Redis Server: {e}")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salvusbackend.settings')

    # This makes it so that a redis-server should only start locally, if on production, there should already be one running
    # from django.conf import settings
    # if settings.DEBUG:
    #     start_redis()  # Only start Redis if DEBUG is True
    #     subprocess.Popen(["celery", "-A", "salvusbackend", "worker", "--loglevel=info"])

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
