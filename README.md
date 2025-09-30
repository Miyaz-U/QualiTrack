QualiTrack
Overview

The QualiTrack is a utility project designed as a replacement for JIRA in handling user stories and defects within software testing. It also allows uploading Excel files containing data, which are automatically processed and updated in the database.

Features

Manage user stories and defects efficiently.

Upload Excel files to update data directly in the system.

Separate views for test cases, defects, and efforts.

Built using Django, Pandas, and NumPy.

Installation

Clone the repository:

git clone https://github.com/your-username/QualiTrack.git

cd QualiTrack


Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows


Install dependencies:

pip install -r requirements.txt


Run database migrations:

python manage.py migrate


Start the development server:

python manage.py runserver

Usage

Access the app in your browser at: http://127.0.0.1:8000/

Navigate through User Stories, Defects, Efforts, and Test Cases.

Upload Excel files to auto-update records.

Requirements

Python 3.8+

Django

Pandas

NumPy

License

This project is for educational and demonstration purposes.
