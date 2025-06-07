import pytest
from datetime import datetime, timedelta
from app import create_app
from models import db, Client, Parking, ClientParking


@pytest.fixture
def app():
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True
    })

    with app.app_context():
        db.create_all()

        client = Client(
            name='Test',
            surname='User',
            credit_card='1234567812345678',
            car_number='A123AA123'
        )

        db.session.add(client)

        parking = Parking(
            address='Test address',
            opened=True,
            count_places=10,
            count_available_places=10
        )
        db.session.add(parking)

        time_in = datetime.now() - timedelta(hours=2)
        time_out = datetime.now() - timedelta(hours=1)
        completed_log = ClientParking(
            client_id=1,
            parking_id=1,
            time_in=time_in,
            time_out=time_out
        )
        db.session.add(completed_log)

        active_log = ClientParking(
            client_id=1,
            parking_id=1,
            time_in=datetime.now()
        )
        db.session.add(active_log)

        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session
        
