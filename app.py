from flask import Flask, request, jsonify
from datetime import datetime
from models import db, Client, Parking, ClientParking


def create_app(config=None):
    app = Flask(__name__)

    app.config.update({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///parking.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    if config is not None:
        app.config.update(config)

    db.init_app(app)

    @app.route('/clients', methods=['GET'])
    def get_clients():
        clients = Client.query.all()
        return jsonify([{
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        } for client in clients])

    @app.route('/clients/<int:client_id>', methods=['GET'])
    def get_client(client_id):
        client = Client.query.get_or_404(client_id)
        return jsonify({
            'id': client.id,
            'name': client.name,
            'surname': client.surname,
            'credit_card': client.credit_card,
            'car_number': client.car_number
        })
    
    @app.route('/clients', methods=['POST'])
    def create_client():
        data = request.get_json()

        if not all(key in data for key in ['name', 'surname', 'car_number']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        client = Client(
            name=data['name'],
            surname=data['surname'],
            credit_card=data.get('credit_card'),
            car_number=data['car_number']
        )

        db.session.add(client)
        db.session.commit()

        return jsonify({'id': client.id}), 201
    
    @app.route('/parkings', methods=['POST'])
    def create_parking():
        data = request.get_json()

        if not all(key in data for key in ['address', 'count_places']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        parking = Parking(
            address=data['address'],
            opened=data.get('opened', True),
            count_places=data['count_places'],
            count_available_places=data['count_places']
        )

        db.session.add(parking)
        db.session.commit()

        return jsonify({'id': parking.id}), 201
    
    @app.route('/client_parkings', methods=['POST'])
    def enter_parking():
        data = request.get_json()

        if not all(key in data for key in ['client_id', 'parking_id']):
            return jsonify({'error': 'client_id and parking_id are required'}), 400
        
        client = Client.query.get_or_404(data['client_id'])
        parking = Parking.query.get_or_404(data['parking_id'])

        if not client.credit_card:
            return jsonify({'error': 'Client has no credit card'}), 400

        if not parking.opened:
            return jsonify({'error': 'Parking is closed'}), 400
        
        if parking.count_available_places <= 0:
            return jsonify({'error': 'No available places'}), 400
        
        existing_log = ClientParking.query.filter_by(
            client_id=client.id,
            parking_id=parking.id,
            time_out=None
        ).first()

        if existing_log:
            return jsonify({'error': 'Client is already on this parking'}), 400
        
        log = ClientParking(
            client_id=client.id,
            parking_id=parking.id,
            time_in=datetime.now()
        )

        parking.count_available_places -= 1

        db.session.add(log)
        db.session.commit()

        return jsonify({
            'id': log.id,
            'message': 'Client entered parking successfully',
            'available_places': parking.count_available_places
        }), 201
    
    @app.route('/client_parkings', methods=['PUT'])
    def exit_parking():
        data = request.get_json()

        if not all(key in data for key in ['client_id', 'parking_id']):
            return jsonify({'error': 'client_id and parking_id are required'}), 400
        
        client = Client.query.get_or_404(data['client_id'])
        parking = Parking.query.get_or_404(data['parking_id'])

        if not client.credit_card:
            return jsonify({'error': 'Client has no credit card'}), 400

        log = ClientParking.query.filter_by(
            client_id=client.id,
            parking_id=parking.id,
            time_out=None
        ).first()

        if not log:
            return jsonify({'error': 'No active parking record found'}), 404
        
        log.time_out = datetime.now()
        parking.count_available_places += 1

        db.session.commit()

        return jsonify({
            'message': 'Client exited parking successfully',
            'available_places': parking.count_available_places
        }), 200
    
    return app
