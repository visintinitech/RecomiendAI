from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Item, Rating
from app.recommender import CollaborativeRecommender
from app.cache import cache_with_ttl
from app.events import EventPublisher
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

recommender = None
event_publisher = None

@api_bp.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    data = request.get_json()
    if not data or 'name' not in data or 'description' not in data:
        return jsonify({'error': 'Faltan campos'}), 400

    item = Item(name=data['name'], description=data['description'], category=data.get('category'))
    db.session.add(item)
    db.session.commit()
    recommender.refresh()
    logger.info('Item creado por usuario %s', get_jwt_identity())
    return jsonify({'id': item.id, 'name': item.name}), 201

@api_bp.route('/users/<int:user_id>/rate', methods=['POST'])
@jwt_required()
def rate_item(user_id):
    current_user = int(get_jwt_identity())
    if current_user != user_id:
        return jsonify({'error': 'No autorizado'}), 403

    data = request.get_json()
    if not data or 'item_id' not in data or 'score' not in data:
        return jsonify({'error': 'Faltan item_id o score'}), 400

    if not (1 <= data['score'] <= 5):
        return jsonify({'error': 'Score debe estar entre 1 y 5'}), 400

    item = Item.query.get(data['item_id'])
    if not item:
        return jsonify({'error': 'Ítem no encontrado'}), 404

    rating = Rating.query.filter_by(user_id=user_id, item_id=data['item_id']).first()
    if rating:
        rating.score = data['score']
    else:
        rating = Rating(user_id=user_id, item_id=data['item_id'], score=data['score'])
        db.session.add(rating)
    db.session.commit()

    recommender.refresh()
    event_publisher.publish_rating_update(user_id)
    return jsonify({'message': 'Valoración registrada'}), 200

@api_bp.route('/users/<int:user_id>/recommendations', methods=['GET'])
@jwt_required()
@cache_with_ttl(ttl_seconds=300)
def get_recommendations(user_id):
    current_user = int(get_jwt_identity())
    if current_user != user_id:
        return jsonify({'error': 'No autorizado'}), 403

    n = min(request.args.get('n', 5, type=int), 20)
    recommended_ids = recommender.recommend_for_user(user_id, top_n=n)

    items_map = {item.id: item for item in Item.query.filter(Item.id.in_(recommended_ids)).all()}
    result = [{
        'id': item_id,
        'name': items_map[item_id].name,
        'description': items_map[item_id].description,
        'category': items_map[item_id].category
    } for item_id in recommended_ids if item_id in items_map]

    return jsonify({'user_id': user_id, 'recommendations': result}), 200

@api_bp.route('/items/<int:item_id>/similar', methods=['GET'])
@jwt_required()
def get_similar(item_id):
    # Este endpoint solo devuelve ítems similares por contenido (no implementado en colaborativo)
    return jsonify({'error': 'No implementado'}), 501

@api_bp.route('/users/<int:user_id>/ratings', methods=['GET'])
@jwt_required()
def get_user_ratings(user_id):
    current_user = int(get_jwt_identity())
    if current_user != user_id:
        return jsonify({'error': 'No autorizado'}), 403

    ratings = Rating.query.filter_by(user_id=user_id).all()
    result = [{
        'item_id': r.item_id,
        'score': r.score,
        'timestamp': r.timestamp.isoformat()
    } for r in ratings]
    return jsonify({'user_id': user_id, 'ratings': result}), 200
