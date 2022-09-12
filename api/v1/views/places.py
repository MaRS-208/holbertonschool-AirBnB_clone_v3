#!/usr/bin/python3
"""Create a new view for Place object that\
handles all default RESTFul API actions"""

from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.place import Place
from models.city import City
from werkzeug.exceptions import BadRequest


# Status
@app_views.route('/places/status')
def places_status():
    """ returns status OK if app is working """
    return jsonify({"Status": "OK"})


# All
@app_views.route('/places', strict_slashes=False)
def places_all():
    """ retrieves a list of all states objects """
    ret_list = []
    for obj in storage.all(Place).values():
        ret_list.append(obj.to_dict())
    return jsonify(ret_list)


# Get by id
@app_views.route('/places/<place_id>',
                 methods=['GET'],
                 strict_slashes=False)
def places_get(place_id):
    """ retrieves a specific state object based on id """
    obj = storage.get(Place, place_id)
    if (obj):
        return jsonify(obj.to_dict())
    else:
        abort(404)

# Get places by city_id
@app_views.route('/cities/<city_id>/places',
                 methods=['GET'],
                 strict_slashes=False)
def places_by_city(state_id):
    """ retrieves all cities object based on partent state_id """
    ret_list = []
    if storage.get(City, city_id) is None:
        abort(404)
    for obj in storage.all(Place).values():
        if obj.city_id == city_id:
            ret_list.append(obj.to_dict())
    return jsonify(ret_list)

# Delete by id
@app_views.route('/places/<place_id>',
                 methods=['DELETE'],
                 strict_slashes=False)
def places_del(place_id):
    """ delete linked state object """
    obj = storage.get(Place, place_id)
    if obj is not None:
        storage.delete(obj)
        storage.save()
        return {}
    else:
        abort(404)


# Create new
@app_views.route('/cities/<city_id>/places/',
                 methods=['POST'],
                 strict_slashes=False)
def places_new(city_id):
    if storage.get(City, city_id) is None:
        abort(404)
    obj_JSON = request.get_json()
    if obj_JSON is None:
        abort(400, "Not a JSON")
    elif 'name' not in obj_JSON.keys():
        abort(400, description="Missing name")
    elif 'user_id' not in obj_JSON.keys():
        abort(400, description="Missing user_id")

    obj_JSON = request.get_json()
    new_obj = Place(**obj_JSON)

    storage.new(new_obj)
    storage.save()
    return jsonify(storage.get(new_obj.__class__, new_obj.id).to_dict())


# Update
@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def places_put(place_id):
    """ Handles PUT request. Updates a Place obj with status 200, else 400 """
    ignore_keys = ['id', 'created_at', 'updated_at', 'user_id', 'city_id']
    obj = storage.get(Place, place_id)
    attrs = request.get_json(force=True, silent=True)
    if not obj:
        abort(404)
    if attrs is None:
        abort(400, "Not a JSON")
    else:
        for key, value in attrs.items():
            if key in ignore_keys:
                continue
            setattr(obj, key, value)
        storage.save()
        return jsonify(obj.to_dict()), 200
