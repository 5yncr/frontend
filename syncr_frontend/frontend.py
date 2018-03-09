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
    """
    Retrieves conflicting files from a drop.
    :param drop_id: ID of drop with conflicting files.
    :return: list of conflicting files
    """
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
    """
    Returns the permission type of the drop ID.
    :param drop_id: The ID of a given drop.
    :return: The permission type of the drop.
    """
    owned_drops = get_owned_drops()

    for drop in owned_drops:
        if drop['name'] == drop_id:
            return "owned"

    return "subscribed"


def get_drop_id(file_path):
    """
    Gets drop id from file path
    :param file_path: File path that contains drop ID
    :return: drop ID
    """

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
    """
    Gets file name from file path
    :param file_path: File path that contains file name
    :return: file name
    """

    file_name = ''

    for letter in file_path:
        if letter == '/':
            file_name = ''
        else:
            file_name = file_name + letter

    return file_name


def set_curr_action(action_update):
    """
    Sets the global variable to the current pressed
    button
    :param action_update: name of action
    :return: none
    """

    global curr_action
    curr_action = action_update


def get_file_versions(file_path):
    """
    Retrieves available versions of a file
    :param file_path: Path of conflicted file
    :return: list of versions for particular file
    """
    # TODO: link with backend to retrieve file version info.

    return {
        'versions': [
            {'name': 'Version 1', 'timestamp': 'ts1', 'owner': 'o1'},
            {'name': 'Version 2', 'timestamp': 'ts2', 'owner': 'o2'},
            {'name': 'Version 3', 'timestamp': 'ts3', 'owner': 'o3'},
            {'name': 'Version 4', 'timestamp': 'ts4', 'owner': 'o4'},
        ],
    }


# TODO: Get file name from path so that file_name isn't parameter.
@app.route('/decline_conflict_file/<file_path>/<file_name>')
def decline_conflict_file(file_path, file_name):
    """
    Sends 'decline conflict file' command to backend
    :param file_path: path of the declined file
    :param file_name: name of the declined file
    :return: message sent back to frontend
    """

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


# TODO: Get file name from path so that file_name isn't parameter.
@app.route('/accept_conflict_file/<file_path>/<file_name>')
def accept_conflict_file(file_path, file_name):
    """
    Sends 'accept conflict file' command to backend
    :param file_path: path of the accepted file
    :param file_name: name of the accepted file
    :return: message sent back to frontend
    """

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


# TODO: Get file name from path so that file_name isn't parameter.
@app.route('/accept_changes/<file_path>/<file_name>')
def accept_changes(file_path, file_name):
    """
    Sends 'accept changes' command to backend
    :param file_path: path of file with accepted changes
    :param file_name: name of file with accepted changes
    :return: message sent back to frontend
    """

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


# TODO: Get file name from path so that file_name isn't parameter.
@app.route('/decline_changes/<file_path>/<file_name>')
def decline_changes(file_path, file_name):
    """
    Sends 'decline changes' command to backend
    :param file_path: path of file with declined changes
    :param file_name: name of file with declined changes
    :return: message sent back to frontend
    """

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
    """
    Sends 'view conflicts' command to backend
    :param drop_id: name of drop with possible conflicts
    :return: list of conflicted files sent to frontend
    """

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
    """
    Sends 'view pending changes' command to backend
    :param drop_id: name of drop with pending changes
    :return: list of files in drop with proposed changes
    """

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
    """
    Sends the 'delete drop' message to backend
    :param drop_id: name of the drop to be deleted
    :return: drop is removed from backend and frontend
    """

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

    file_versions = get_file_versions('')  # REMOVE WHEN BACKEND IS ADDED

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
        versions=file_versions,
    )


@app.route('/initialize', methods=['GET', 'POST'])
def initialize():
    return startup()
    # if request.method == 'POST':
    #    session['logged_in'] = True
    #    flash('You were logged in')
    #    return redirect(url_for('show_drops'))
    # return render_template('initialize.html')
