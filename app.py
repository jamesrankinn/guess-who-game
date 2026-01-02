from flask import Flask, render_template, request, jsonify
from game_logic import CategoryManager
import random
import os

app = Flask(__name__)

# Make categories path absolute (based on where app.py lives)
CATEGORIES_PATH = os.path.join(app.root_path, "categories")
category_manager = CategoryManager(folder_path=CATEGORIES_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_categories', methods=['GET'])
def get_categories():
    categories = category_manager.get_available_categories()
    return jsonify(categories)

@app.route('/setup_game', methods=['POST'])
def setup_game():
    data = request.get_json(force=True)  # force=True helps if content-type is weird
    player_names = data.get('players', [])
    selected_category = data.get('category', '')

    if not isinstance(player_names, list) or len(player_names) < 3:
        return jsonify({"error": "Need at least 3 players."}), 400

    if not selected_category:
        return jsonify({"error": "No category selected."}), 400

    word_list = category_manager.get_words_from_category(selected_category)
    if not word_list:
        return jsonify({"error": "Category is empty or missing."}), 400

    # Pick secret
    target_word = random.choice(word_list)

    # Shuffle copy of players so we don't mutate input list unexpectedly
    shuffled_players = player_names[:]
    random.shuffle(shuffled_players)

    # Pick imposter + starter
    imposter_name = random.choice(shuffled_players)
    starter_name = random.choice(shuffled_players)

    game_data = []
    for player in shuffled_players:
        if player == imposter_name:
            role = "IMPOSTER"
            secret = "You are the Imposter"
        else:
            role = "CIVILIAN"
            secret = target_word

        game_data.append({
            "player": player,
            "role": role,
            "secret_word": secret
        })

    return jsonify({
        "queue": game_data,
        "starter": starter_name
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)

