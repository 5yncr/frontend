import platform
import subprocess
from os import path

from flask import flash
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)  # create the application instance
app.config.from_object(__name__)  # load config from this file , frontend.py

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    TEMPLATES_AUTO_RELOAD=True,
))
app.config.from_envvar('SYNCR_SETTINGS', silent=True)

# Backend Access Functions

# Global Variables
curr_action = ''


def send_message(message):
    # Sends given message to backend
    # Wait for a response or until TIMEOUT
    # If error_message is not None, display error_message
    # Else display success_message
    response = {
        'drop_id': message.get('drop_id'),
        'file_name': message.get('file_name'),
        'file_path': message.get('file_path'),
        'action': message.get('action'),
        'message': "Generic Message For " + message.get('action'),
    }
    return response


def open_file_location(file_path):
    # Placeholder until backend communication is set-up
    file_path = path.dirname(path.abspath(__file__))

    op_sys = platform.system()
    if op_sys == 'Windows':
        subprocess.Popen(['explorer', file_path])
    if op_sys == 'Linux':
        subprocess.Popen(['xdg-open', file_path])
    if op_sys == 'Darwin':
        subprocess.Popen(['open', file_path])


@app.route('/remove_file/<drop_id>/<file_name>')
def remove_file(drop_id, file_name):
    # Remove file at specified location from drop info

    set_curr_action('remove file')

    message = {
        'drop_id': drop_id,
        'file_name': file_name,
        'action': 'rf',
    }
    response = send_message(message)
    # TODO: Remove file name after proper communication is set up
    return show_drops(
        response.get('drop_id'),
        response.get('message') + " " + response.get("file_name"),
    )


def get_owned_drops():
    # Placeholder until backend communication is set-up
    # TODO: validate data structure
    return [{'name': 'O_Drop_1'}, {'name': 'O_Drop_2'}]


def get_subscribed_drops():
    # Placeholder until backend communication is set-up
    # TODO: validate data structure
    return [{'name': 'S_Drop_1'}, {'name': 'S_Drop_2'}, {'name': 'S_Drop_3'}]


def get_selected_drop(drop_id):
    # Placeholder until backend communication is set-up
    # TODO: validate data structure

    # if drop does not exist -> return default drop display

    return {
        'name': drop_id, 'files': [
            {'name': 'FileOne', 'type': 'text', 'occr': 'once'},
            {'name': 'FileTwo', 'type': 'image', 'occr': 'many'},
            {'name': 'FileThree', 'type': 'video', 'occr': 'once'},
            {'name': 'FileFour', 'type': 'text', 'occr': 'once'},
            {'name': 'Folder', 'type': 'folder', 'occr': 'many'},
        ], 'permission': get_permission(drop_id),
    }


@app.route('/get_conflicting_files/<drop_id>')
def get_conflicting_files(drop_id):
    # eventually will be used to retrieve files of conflicting drops

    set_curr_action('get conflicting files')

    message = {
        'drop_id': drop_id,
        'action':  'get_c_f',
    }

    # TODO: Retrieve conflicting files names from backend.
    response = send_message(message)

    return show_drops(
        response.get('drop_id'),
        response.get('message') + " of drop " + response.get('drop_id'),
    )


def get_permission(drop_id):
    # returns the permission type of the drop ID
    owned_drops = get_owned_drops()

    for drop in owned_drops:
        if drop['name'] == drop_id:
            return "owned"

    return "subscribed"


def get_drop_id(file_path):
    # retrieves the drop_id from a given file path
    reached_slash = False
    drop_string = ''

    for letter in file_path:
        if not reached_slash:
            if letter == '/':
                reached_slash = True
            else:
                drop_string = drop_string + letter

    return drop_string


def get_file_name(file_path):
    # retrieves the file name from a given path
    file_name = ''

    for letter in file_path:
        if letter == '/':
            file_name = ''
        else:
            file_name = file_name + letter

    return file_name


def set_curr_action(action_update):
    # sets the global variable to a given value
    global curr_action
    curr_action = action_update


# TODO: Get file name from path so that app.route doesnt have file_name.
@app.route('/decline_conflict_file/<file_path>/<file_name>')
def decline_conflict_file(file_path, file_name):
    # if a file is in conflict with master
    # declining changes leaves file on master the same
    # backend communication: remove conflict file

    set_curr_action('current conflicts')

    message = {
        'drop_id': get_drop_id(file_path),
        'file_path': file_path,
        'file_name': file_name,
        'action': 'd_c_f',
    }

    # TODO: Communicate to do nothing to the master file on backend
    response = send_message(message)

    return show_drops(
        response.get('drop_id'),
        response.get('message') + " of file " + response.get('file_name'),
    )


# TODO: Get file name from path so that app.route doesnt have file_name.
@app.route('/accept_conflict_file/<file_path>/<file_name>')
def accept_conflict_file(file_path, file_name):
    # if a file is in conflict with file in master
    # accepting changes modifies master file
    # backend communication: change master file

    set_curr_action('current conflicts')

    message = {
        'drop_id': get_drop_id(file_path),
        'file_path': file_path,
        'file_name': file_name,
        'action': 'a_c_f',
    }

    # TODO: Backend will modify master file with changes
    response = send_message(message)

    return show_drops(
        response.get('drop_id'),
        response.get('message') + " of file " + response.get('file_name'),
    )


# TODO: Get file name from path so that app.route doesnt have file_name.
@app.route('/accept_changes/<file_path>/<file_name>')
def accept_changes(file_path, file_name):
    # Accepts the proposed changes of a file
    # backend: modify the master file with proposed changes

    set_curr_action('view pending changes')

    message = {
        'drop_id': get_drop_id(file_path),
        'file_path': file_path,
        'file_name': file_name,
        'action': 'a_c',
    }

    # TODO: Backend will modify master file with changes
    response = send_message(message)

    return show_drops(
        response.get('drop_id'),
        response.get('message') + " of file " + response.get('file_name'),
    )


# TODO: Get file name from path so that app.route doesnt have file_name.
@app.route('/decline_changes/<file_path>/<file_name>')
def decline_changes(file_path, file_name):
    # Declines the proposed changes of a file
    # backend: discard changes, keep master file

    set_curr_action('view pending changes')

    message = {
        'drop_id': get_drop_id(file_path),
        'file_path': file_path,
        'file_name': file_name,
        'action': 'd_c',
    }

    # TODO: Backend will keep master file unchanged
    response = send_message(message)

    return show_drops(
        response.get('drop_id'),
        response.get('message') + " of file " + response.get('file_name'),
    )


@app.route('/view_conflicts/<drop_id>')
def view_conflicts(drop_id):
    # if no drop is selected
        # do nothing
    # else
        # retrieve files from all conflicting drops
        # display said files in body of page

    set_curr_action('current conflicts')

    message = {
        'drop_id': drop_id,
        'action':  'v_c',
    }

    # TODO: Setup communication to retrieve conflicting files.
    response = send_message(message)

    # TODO: Get global variable setup for selected button (HTML)
    return show_drops(
        response.get('drop_id'),
        response.get('message') + " of drop " + response.get('drop_id'),
    )


@app.route('/add_file/<drop_id>')
def add_file(drop_id):
    # if no drop is selected
        # do nothing
    # else
        # communicate change to backend.
        # open finder / windows equivalent to choose file.

    set_curr_action('add file')

    return show_drops(drop_id, "file added")


@app.route('/share_drop/<drop_id>')
def share_drop(drop_id):
    # if no drop is selected
        # do nothing
    # else
        # communicate with backend to retrieve public key
        # display public key in the body of the page

    set_curr_action('share drop')

    return show_drops(drop_id, "drop shared")


@app.route('/view_pending_changes/<drop_id>')
def view_pending_changes(drop_id):
    # if no drop is selected
        # do nothing
    # else
        # display pending file changes on body of page
        # should provide options to review/accept pending changes

    set_curr_action('view pending changes')

    message = {
        'drop_id': drop_id,
        'action': 'v_p_c',
    }

    # TODO: Setup communication to retrieve files with changes.
    response = send_message(message)

    return show_drops(
        response.get('drop_id'),
        response.get('message') + " of drop " + response.get('drop_id'),
    )


@app.route('/view_owners/<drop_id>')
def view_owners(drop_id):
    # if no drop is selected
        # do nothing
    # else
        # communicate with backend to retrieve owners
        # display owners on body of page
        # give user option to remove owners if primary owner

    set_curr_action('view owners')

    return show_drops(drop_id, "list of owners")


@app.route('/whitelist/<drop_id>')
def whitelist(drop_id):
    # if no drop is selected
        # do nothing
    # else
        # display prompt on page to whitelist node
        # prompt should communicate with backend

    set_curr_action('whitelist')

    return show_drops(drop_id, "node whitelisted")


@app.route('/delete_drop/<drop_id>')
def delete_drop(drop_id):
    # if no drop is selected
        # do nothing
    # else
        # communicate deletion to backend.
        # backend should delete drop?

    set_curr_action('delete drop')

    message = {
        'drop_id': drop_id,
        'action': 'd_drop',
    }

    # TODO: Setup backend communication to remove drop
    response = send_message(message)

    return show_drops(
        response.get('drop_id'),
        response.get('message') + " of drop " + response.get('drop_id'),
    )


@app.route('/unsubscribe/<drop_id>')
def unsubscribe(drop_id):
    # if no drop is selected
        # Do nothing
    # else
        # communicate change to backend

    set_curr_action('unsubscribe')

    return show_drops(None, "unsubscribed")


# Request a change to the selected drop
@app.route('/request_change/<drop_id>')
def request_change(drop_id):
    # if no drop is seleted
        # Do nothing
    # else
        # communicate change to backend

    set_curr_action('request change')

    return show_drops(drop_id, "change requested")


@app.route('/')
def startup():
    return show_drops(None, None)


@app.route('/<drop_id>', methods=['GET', 'POST'])
def show_drops(drop_id=None, message=None):
    owned_drops = get_owned_drops()
    subscribed_drops = get_subscribed_drops()
    selected_drop = []

    if drop_id is not None:
        selected_drop = get_selected_drop(drop_id)

    performed_action = []  # REMOVE WHEN BACKEND COMMUNICATION IS ADDED

    if message is not None:
        performed_action = {'description': message}
        flash(message)

    # File Actions
    if request.method == 'POST':
        if request.form.get('type') == 'open_file':
            open_file_location('PUT PROPER LOCATION HERE')

    return render_template(
        'show_drops.html', selected=selected_drop, subscribed=subscribed_drops,
        owned=owned_drops, action=performed_action, selec_act=curr_action,
    )


@app.route('/initialize', methods=['GET', 'POST'])
def initialize():
    return startup()
    # if request.method == 'POST':
    #    session['logged_in'] = True
    #    flash('You were logged in')
    #    return redirect(url_for('show_drops'))
    # return render_template('initialize.html')
