from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from flask_login import current_user
from ..models import User, Node, Association
from . import api
from .errors import forbidden, bad_request


# Requests Needed
# 1.1 GET all node info
# 1.2 GET specific node info
# 2.1 PUT change access state
# 3. change node access state - PUT
# 4. add user to node - POST

# Simple Test Case
@api.route('/users', methods=['GET'])
def get_users():
    print('Hello')
    return jsonify({'hello':'hi'})

# 1.1 Get all node info
@api.route('/get_nodes/')
def get_nodes():
    nodes = Node.query.all()
    return jsonify([node.to_json() for node in nodes])

# 1.2 Get node info from given node id & user id
@api.route('/get_node/<int:id>')
def get_node(id):
    user_id = g.current_user.id
    association = Association.query.filter_by(node_id=id, user_id=user_id).scalar()
    if association is None:
        return forbidden('Access info denied')
    node = Node.query.get_or_404(id)
    return jsonify(node.to_json())

# 2.1 Change node access state
@api.route('/access_node/<int:id>', methods=['PUT'])
def access_node(id):
    user_id = g.current_user.id
    association = Association.query.filter_by(node_id=id, user_id=user_id).first()
    if association is None:
        return forbidden('Access info denied')
    node = Node.query.get_or_404(id)
    request_data = request.get_json()
    if isinstance(request_data['is_open'], bool):
        node.is_open = request_data['is_open']
        db.session.commit()
        return jsonify(node.to_json())
    return bad_request('Invalid access request')

# 3.1 Add user to node from given node id & two user ids
@api.route('/connection/add', methods=['POST'])
def connection_add():
    user_id = g.current_user.id
    request_data = request.get_json()
    association = Association.query.filter_by(node_id=request_data['node_id'],
                                              user_id=user_id).first()
    if association is None:
        return forbidden('Access info denied')
    user = User.query.filter_by(email=request_data['email']).first()
    new_association = Association(user_id=user.id,
                                  node_id=request_data['node_id'],
                                  permissions='STANDARD')
    db.session.add(new_association)
    db.session.commit()
    return jsonify({'request': 'success'})

# 3.2 Remove user from node with given node id & user id
@api.route('/connection/remove', methods=['DELETE'])
def connection_remove():
    user_id = g.current_user.id
    request_data = request.get_json()
    association = Association.query.filter_by(node_id=request_data['node_id'],
                                              user_id=user_id).first()
    if association is None:
        return forbidden('Access info denied')
    user = User.query.filter_by(email=request_data['email']).first()
    delete_association = Association.query.filter_by(user_id=user.id,
                                     node_id=request_data['node_id']).delete()
    db.session.commit()
    return jsonify({'request': 'success'})



