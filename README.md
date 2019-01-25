PyPMS is a PMS (Property Management System) for the hotel Hotel Panorama, Grasse France

Manual User:
git clone https://github.com/XuanShine/PyPMS
cd PyPMS
virtualenv -p python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
pytest  # launch tests
python manage.py runserver

then go to http://127.0.0.1:8000/home.html