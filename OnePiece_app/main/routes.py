from flask import Blueprint, request, jsonify
from datetime import date, datetime
from flask_login import login_required, current_user
from OnePiece_app.models import Affiliation, Character, User, CharacterWithDevilFruit, CharacterWithHaki
from OnePiece_app.main.forms import AffiliationForm, CharactersForm
from OnePiece_app import db

main = Blueprint("main", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_affiliations = Affiliation.query.all()
    all_haki_characters = Character.query.filter(Character.haki != 'No').all()
    all_devilfruit_characters = Character.query.filter(Character.devil_fruit != 'No').all()
    return jsonify({
        "all_affiliations": [affiliation.serialize() for affiliation in all_affiliations],
        "all_haki_characters": [character.serialize() for character in all_haki_characters],
        "all_devilfruit_characters": [character.serialize() for character in all_devilfruit_characters]
    })

@main.route('/new_affiliation', methods=['POST'])
@login_required
def new_affiliation():
    data = request.get_json()
    form = AffiliationForm(data=data)
    if form.validate():
        new_affiliation = Affiliation(
            title=form.title.data,
            created_by_id=current_user.id
        )
        db.session.add(new_affiliation)
        db.session.commit()

        return jsonify({"message": "New affiliation was created successfully.", "id": new_affiliation.id}), 201
    return jsonify({"error": "Invalid data provided."}), 400

@main.route('/new_character', methods=['POST'])
@login_required
def new_character():
    data = request.get_json()
    form = CharactersForm(data=data)
    if form.validate():
        new_character = Character(
            name=form.name.data,
            category=form.category.data,
            affiliation=form.affiliation.data,
            devil_fruit=form.devil_fruit.data,
            haki=form.haki.data,
            created_by_id=current_user.id
        )
        db.session.add(new_character)
        db.session.commit()

        return jsonify({"message": "New character was created successfully.", "id": new_character.id}), 201
    return jsonify({"error": "Invalid data provided."}), 400

@main.route('/affiliation/<int:affiliation_id>', methods=['GET', 'PUT'])
@login_required
def affiliation_detail(affiliation_id):
    affiliation = Affiliation.query.get(affiliation_id)
    if not affiliation:
        return jsonify({"error": "Affiliation not found."}), 404

    if request.method == 'PUT':
        data = request.get_json()
        form = AffiliationForm(data=data)
        if form.validate():
            affiliation.title = form.title.data
            db.session.commit()

            return jsonify({"message": "Affiliation was updated successfully."}), 200
        return jsonify({"error": "Invalid data provided."}), 400

    return jsonify(affiliation.serialize())

@main.route('/characters/<int:character_id>', methods=['GET', 'PUT'])
@login_required
def character_detail(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found."}), 404

    if request.method == 'PUT':
        data = request.get_json()
        form = CharactersForm(data=data)
        if form.validate():
            character.name = form.name.data
            character.category = form.category.data
            character.affiliation = form.affiliation.data
            db.session.commit()

            return jsonify({"message": "Character was updated successfully."}), 200
        return jsonify({"error": "Invalid data provided."}), 400

    return jsonify(character.serialize())

@main.route('/add_to_favorite_character_list/<int:character_id>', methods=['POST'])
@login_required
def add_to_favorite_characters_list(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found."}), 404

    if character in current_user.favorite_characters_list_items:
        return jsonify({"message": "Character already in favorite characters list."}), 200

    current_user.favorite_characters_list_items.append(character)
    db.session.commit()
    return jsonify({"message": "Character added to favorite characters list successfully."}), 200

@main.route('/delete_from_favorite_characters_list/<int:character_id>', methods=['POST'])
@login_required
def delete_from_favorite_characters_list(character_id):
    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found."}), 404

    if character in current_user.favorite_characters_list_items:
        current_user.favorite_characters_list_items.remove(character)
        db.session.commit()
        return jsonify({"message": "Character removed from favorite characters list successfully."}), 200

    return jsonify({"message": "Character not in favorite characters list."}), 200

@main.route('/favorite_characters_list')
@login_required
def favorite_characters_list():
    user_characters_list = current_user.favorite_characters_list_items
    return jsonify({"favorite_characters_list": [character.serialize() for character in user_characters_list]})
