from flask import Blueprint, jsonify
from app import cg, mongo
from app.services.market_data_service import get_token_market_data

market_data_bp = Blueprint('market_data', __name__)

@market_data_bp.route('/token/<token_id>')
def get_token_data(token_id):
    try:
        market_data = get_token_market_data(token_id)
        return jsonify(market_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@market_data_bp.route('/trending')
def get_trending_tokens():
    try:
        trending = cg.get_search_trending()
        return jsonify(trending), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400 