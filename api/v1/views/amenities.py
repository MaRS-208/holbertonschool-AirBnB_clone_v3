#!/usr/bin/python3
""" API redirections """
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
    """ retrieves a list of all amenities objects """
    ret_list = []
    for obj in storage.all(Amenity).values():
        ret_list.append(obj.to_dict())
    return jsonify(ret_list)


# Get by id
@app_views.route('/amenities/<amenity_id>',
                 methods=['GET'],
                 strict_slashes=False)
def amenities_get(amenity_id):
    """ retrieves a specific amenity object based on id """
    obj = storage.get(Amenity, amenity_id)
    if (obj):
        return jsonify(obj.to_dict())
    else:
        abort(404)


# Delete by id
@app_views.route('/amenities/<amenity_id>',
                 methods=['DELETE'],
                 strict_slashes=False)
def amenities_del(amenity_id):
    """ delete linked amenity object """
    obj = storage.get(Amenity, amenity_id)
    if obj is not None:
        storage.delete(obj)
        storage.save()
        return {}
    else:
        abort(404)


# Create new
@app_views.route('/amenities/',
                 methods=['POST'],
                 strict_slashes=False)
def amenities_new():
    """ creates new amenity """
    obj_JSON = request.get_json()
    if obj_JSON is None:
        abort(400, "Not a JSON")
    elif 'name' not in obj_JSON.keys():
        abort(400, description="Missing name")

    obj_JSON = request.get_json()
    new_obj = Amenity(**obj_JSON)

    storage.new(new_obj)
    storage.save()
    return jsonify(storage.get(new_obj.__class__, new_obj.id).to_dict()), 201


# Update
@app_views.route('/amenities/<amenity_id>',
                 methods=['PUT'],
                 strict_slashes=False)
def amenities_put(amenity_id):
    """ Handles PUT request. Updates Amenity obj with status 200
    else 400 """
    ignore_keys = ['id', 'created_at', 'updated_at']
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
