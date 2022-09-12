#!/usr/bin/python3
""" API redirections """
from models.place import Place
from models.amenity import Amenity
from werkzeug.exceptions import BadRequest
from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage


# Status
@app_views.route('/amenities/status')
def amenities_status():
    """ returns status OK if app is working """
    return jsonify({"Status": "OK"})


# All
@app_views.route('/amenities', strict_slashes=False)
def amenities_all():
    """ retrieves a list of all reviews objects """
    ret_list = []
    for obj in storage.all(Amenity).values():
        ret_list.append(obj.to_dict())
    return jsonify(ret_list)


# Get by id
@app_views.route('/amenities/<amenity_id>',
                 methods=['GET'],
                 strict_slashes=False)
def amenities_get(amenity_id):
    """ retrieves a specific review object based on id """
    obj = storage.get(Amenity, amenity_id)
    if (obj):
        return jsonify(obj.to_dict())
    else:
        abort(404)


# Get cities by state_id
@app_views.route('/places/<place_id>/amenities',
                 methods=['GET'],
                 strict_slashes=False)
def amenities_by_place(place_id):
    """ retrieves all reviews object based on partent place_id """
    ret_list = []
    if storage.get(Place, place_id) is None:
        abort(404)
    for obj in storage.all(Amenity).values():
        if obj.place_id == place_id:
            ret_list.append(obj.to_dict())
    return jsonify(ret_list)


# Delete by id
@app_views.route('/amenities/<amenity_id>',
                 methods=['DELETE'],
                 strict_slashes=False)
def amenities_del(amenity_id):
    """ delete linked review object """
    obj = storage.get(Amenity, amenity_id)
    if obj is not None:
        storage.delete(obj)
        storage.save()
        return {}
    else:
        abort(404)


# Create new
@app_views.route('places/<place_id>/amenities/',
                 methods=['POST'],
                 strict_slashes=False)
def amenities_new(place_id):
    if storage.get(Place, place_id) is None:
        abort(404)
    try:
        obj_JSON = request.get_json()
        new_obj = Amenities(**obj_JSON)
        if not obj_JSON.get('name'):
            abort(400, description="Missing name")
    except BadRequest:
        abort(400, description="Not a JSON")

    storage.new(new_obj)
    storage.save()
    return jsonify(storage.get(new_obj.__class__, new_obj.id).to_dict()), 201


# Update
@app_views.route('/amenities/<amenity_id>',
                 methods=['PUT'],
                 strict_slashes=False)
def amenities_put(amenity_id):
    """Handles PUT request. Updates Review obj with status 200, else 400"""
    ignore_keys = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
    obj = storage.get(Amenity, amenity_id)
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
