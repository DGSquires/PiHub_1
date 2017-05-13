# Defines routes used for node control module
from flask import render_template, redirect, request, url_for, session, flash
from flask_login import login_required
from . import control
from .. import db
from ..models import User, Association, Node, Permissions
from .forms import AddNode, AddNodeUsers
from networking import socket_client
from config import Privileges


@control.route('/access', methods=['GET', 'POST'])
@login_required
def access():
    form = request.form
    if request.method == 'POST':
        print(form)
        node_info = db.session.query(Node).filter_by(id=form['id']).first()
        user = User.query.filter_by(email=session['email']).first()
        association = Association.query.filter_by(user_id=user.id, node_id=node_info.id).first()
        if association.can(Privileges.CONTROL_ACCESS):
            (success, new_state) = socket_client(form['is_open'], node_info.ip_address)
            print('Transmission success: ' + str(success) + ' | New node state: '+str(new_state))
            if success:
                if new_state == 'True':
                    node_info.is_open = True
                if new_state =='False':
                    node_info.is_open = False
                db.session.commit()
                flash('Access request successful')
            if success is False:
                flash('Access request could not be completed')
        if association.can(0x03) is not True:
            flash('You are not authorised to make this action')
    return render_template('control/access.html',
                           node_data=node_list())

def node_list():
    user = User.query.filter_by(email=session['email']).first()         # Returns User ID from email of current session user
    node_id_list = [i.node_id for i in Association.query.filter_by(user_id=user.id).all()]  # Returns list of Node IDs that user has access to
    node_data = Node.query.filter(Node.id.in_(node_id_list)).all()      # Returns dictionary containing individual Node data
    return node_data


@control.route('/add_node', methods=['GET', 'POST'])
@login_required
def add_node():
    form = AddNode()
    if form.validate_on_submit():
        node = Node(name=form.name.data,                                    # Builds node object from form config
                    ip_address=form.ip_address.data)
        db.session.add(node)
        db.session.commit()
        session['node_name'] = form.name.data
        return redirect(url_for('.add_node_users'))
    return render_template('control/add_node.html', form=form)


@control.route('/add_node_users', methods=['GET', 'POST'])
@login_required
def add_node_users():
    form = AddNodeUsers()
    print(session['node_name'])
    if form.validate_on_submit():
        node_name = session['node_name']                               # Calls node name from session dictionary
        node = Node.query.filter_by(name=node_name).first()               # Return the node object form dictionary
        user = User.query.filter_by(email=form.email.data).first()        # Returns user object from User table
        try:
            permissions = Permissions.permission_dict[form.role.data]   # Build permissions binary
        except KeyError:
            return redirect(url_for('.add_node_users'))                 # Refresh page for failed role type
        association = Association(user_id=user.id, node_id=node.id, permissions=permissions)        # Builds association object from Association table
        if form.iterate.data is False:                                 # Returns False when add additional users button is not pressed
            db.session.add(association)
            db.session.commit()
            session.pop('node_name', None)                              # Deletes the node linked to this session
            return redirect(url_for('.access'))                 # Redirects to ./control/access page
        db.session.add(association)
        db.session.commit()
        return redirect(url_for('.add_node_users'))
    return render_template('control/add_node_users.html', form=form)                    # Builds add_note.html page
