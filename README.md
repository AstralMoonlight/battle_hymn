source venv/Scripts/activate
python -m venv venv

pip freeze > requirements.txt
pip install -r requirements.txt
