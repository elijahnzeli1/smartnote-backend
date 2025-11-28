#!/bin/bash
# Script to create migrations for chat models

cd /home/nthukunzeli/SmartNoteAPI/backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Create migrations
python manage.py makemigrations notes

# Apply migrations
python manage.py migrate

echo "Migrations created and applied successfully!"
