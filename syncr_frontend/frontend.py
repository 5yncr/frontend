"""Main implementation of syncr's frontend."""
from os import path
from os import scandir

from flask import flash
from flask import Flask
from flask import render_template
from flask import request
from syncr_backend.constants import FrontendAction

from .communication import send_request

app = Flask(__name__)  # create the application instance
app.config.from_object(__name__)  # load config from this file , frontend.py

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    TEMPLATES_AUTO_RELOAD=True,
))
app.config.from_envvar('SYNCR_SETTINGS', silent=True)

# Global Variables
current_drop_path = ''
home_path = path.expanduser('~')[1:]

# Backend Access Functions


def send_message(message):
    """
    Send message to backend and wait for a response or until TIMEOUT.

    :param message: message sent to backend
    :return: response from server
    """
    message['action'] = str(message['action'])

    response = send_request(message)

    return response


def get_owned_subscribed_drops():
    """
    Get a tuple of owned drops and subscribed drops.

    :return: Gets a tuple of of dictionaries in format (owned drop dict,
        subscribed drop dict)
    """
    message = {
        'action': FrontendAction.GET_OWNED_SUBSCRIBED_DROPS,
    }

    response = send_message(message)

    return response.get('requested_drops_tuple')


# Return dictionary for selected drop
def get_selected_drop(drop_id):
    """
    Get a drop's infromation.

    :param drop_id: Selected drop
    :return: Dictionary for selected drop
    """
    message = {
        'drop_id': drop_id,
        'action': FrontendAction.GET_SELECTED_DROP,
    }

    response = send_message(message)

    drop = response.get('requested_drops')

    return drop


def get_pending_changes(drop_id):
    """Get information about a drop, including pending changes.

    :param drop_id: The drop id
    :return: Drop info, including pending changes
    """
    message = {
        'drop_id': drop_id,
        'action': FrontendAction.GET_PENDING_CHANGES,
    }

    response = send_message(message)

    drop = response.get('requested_drops')

    return drop


def is_in_drop_list(drop_id, drop_list):
    """
    Figure out if a drop is in a list of drops.

    TODO: remove me.

    :param drop_id: ID of the drop
    :param drop_list: List of drops
    :return: True if the given drop_id exists in the drop list
    """
    in_list = False

    for drop in drop_list:
        if drop.get('drop_id') == drop_id:
            in_list = True

    return in_list


def get_drop_id(file_path):
    """
    Get drop id from file path.

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
    Get file name from file path.

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


@app.route('/create_drop/<path:current_path>')
def create_drop(current_path):
    """
    Provide the UI with the prompt to create a drop.

    :param current_path: Where we are in the path lookup
    :return: response that triggers the UI prompt
    """
    return show_drop(
        None,
        None,
        current_path,
        'create_drop',
    )


@app.route('/subscribe_to_drop/<path:current_path>')
def subscribe_to_drop(current_path):
    """
    Provide the UI with the prompt to subscribe to a drop.

    :param current_path: The path to put the new drop
    :return: response that triggers the UI prompt
    """
    return show_drop(
        None,
        None,
        current_path,
        'subscribe_to_drop_directory',
    )


@app.route('/subscribe_to_drop_with_directory/<path:drop_path>')
def subscribe_to_drop_with_directory(drop_path):
    """
    Request user to provide drop code for a drop to subscribed to.

    And then save in that location

    :param drop_path: Where to save the drop
    :return: Dialog to get the drop id
    """
    return show_drop(
        None,
        None,
        drop_path,
        'subscribe_to_drop_name',
    )


@app.route('/initialize_drop/<path:drop_path>')
def initialize_drop(drop_path):
    """
    Create a drop from a path.

    :param drop_path: Where to initialize the drop from
    :return: Message sent back to frontend.
    """
    if drop_path is None:
        message = 'Cannot create drop. No directory was selected.'
    else:
        message = {
            'action': FrontendAction.INITIALIZE_DROP,
            'directory': '/' + drop_path,
        }

        response = send_message(message)
        message = response.get('message')

        if response.get('success'):
            return show_drop(
                response.get('drop_id'),
                message,
            )

    return show_drop(
        None,
        message,
    )


@app.route('/subscribe', methods=['POST'])
def input_drop_to_subscribe(drop_code=None, drop_path=None):
    """
    Subscribe to a drop.

    :param drop_code: Drop id
    :param drop_path: Where to put the drop
    :return: Show the drop
    """
    if drop_code is None:
        result = request.form.get('drop_to_subscribe_to')
        path = request.form['drop_path']
    else:
        result = drop_code
        path = drop_path

    message = {
        'action': FrontendAction.INPUT_DROP_TO_SUBSCRIBE_TO,
        'drop_id': result,
        'directory': '/' + path,
    }

    response = send_message(message)
    return show_drops(
        result,
        response.get('message'),
    )


@app.route('/share_drop/<drop_id>')
def share_drop(drop_id):
    """
    Display drop ID to user for sharing purposes.

    :param drop_id: Drop ID to be shared
    :return: Show drop page with drop_id at the top
    """
    download_code = "Download Code: " + drop_id

    return show_drop(drop_id, download_code)


@app.route('/view_owners/<drop_id>/add/', methods=['GET', 'POST'])
def add_owner(drop_id, owner_id=None):
    """
    Add an owner to specified drop.

    :param drop_id: ID of drop
    :param owner_id: ID of owner
    :return: Show the drop owners
    """
    if owner_id is None:
        if request.method == 'POST':
            if request.form.get('owner_id') is None:
                return view_owners(drop_id)

        new_owner_id = request.form.get('owner_id')
    else:
        new_owner_id = owner_id

    message = {
        'drop_id': drop_id,
        'owner_id': new_owner_id,
        'action': FrontendAction.ADD_OWNER,
    }

    response = send_message(message)
    message = response.get('message')

    if response.get('success'):
        message = 'Successfully added owner'
    else:
        message = 'Error adding new owner'

    return view_owners(drop_id, message)


@app.route('/view_owners/<drop_id>/remove/<owner_id>', methods=['POST'])
def remove_owner(drop_id, owner_id):
    """
    Remove an owner from specified drop.

    :param drop_id: ID of drop
    :param owner_id: ID of owner to remove from drop
    :return: Show the drop owners
    """
    message = {
        'drop_id': drop_id,
        'owner_id': owner_id,
        'action': FrontendAction.REMOVE_OWNER,
    }

    response = send_message(message)
    message = response.get('message')

    if response.get('success'):
        message = 'Successfully removed owner'
    else:
        message = 'Error removing owner'

    return view_owners(drop_id, message)


@app.route('/view_owners/<drop_id>')
def view_owners(drop_id, message=None):
    """
    Update current action to display list of owners.

    :param drop_id: ID of drop to view owners
    :param message: message from owner action if any
    :return: Show the drop owenrs
    """
    return show_drop(drop_id, message, None, 'owners')


@app.route('/delete_drop/<drop_id>')
def delete_drop(drop_id):
    """
    Send the 'delete drop' message to backend.

    :param drop_id: name of the drop to be deleted
    :return: drop is removed from backend and frontend
    :return: Main page if it succeeded
    """
    message = {
        'drop_id': drop_id,
        'action': FrontendAction.DELETE_DROP,
    }

    response = send_message(message)
    result = response.get('message')

    if response.get('success') is True:
        return show_drop(None, result, None, 'delete drop')
    else:
        return show_drop(drop_id, result, None, 'delete drop')


@app.route('/unsubscribe/<drop_id>')
def unsubscribe(drop_id):
    """
    Unsubscribe from drop.

    :param drop_id: ID of drop to be unsubscribed
    :return: UI and backend update to not have subscribed drop.
    """
    message = {
        'drop_id': drop_id,
        'action': FrontendAction.UNSUBSCRIBE,
    }

    response = send_message(message)
    result = response.get('message')

    if response.get('success') is True:
        return show_drop(None, result, None, 'unsubscribe')
    else:
        return show_drop(drop_id, result, None, 'unsubscribe')


@app.route('/new_version/<drop_id>')
def new_version(drop_id):
    """
    Tell backend to create new version from changed files for specified drop.

    :param drop_id: drop to create new version for
    :return: renders web page based off backend response
    """
    message = {
        'action': FrontendAction.NEW_VERSION,
        'drop_id': drop_id,
    }

    response = send_message(message)

    return show_drop(
        drop_id,
        response.get('message'),
    )


@app.route('/sync_update/<drop_id>')
def sync_update(drop_id):
    """
    Tell backend to sync updates from changed remote files.

    :param drop_id: drop to sync updates for
    :return: renders web page based off backend response
    """
    message = {
        'action': FrontendAction.SYNC_UPDATE,
        'drop_id': drop_id,
    }

    response = send_message(message)
    message = response.get('message')

    return show_drop(
        drop_id,
        message,
    )


@app.route('/get_ID/', defaults={'drop_id': None})
@app.route('/get_ID/drop/<drop_id>')
def get_node_id(drop_id=None):
    """
    Request current node id from backend.

    :param drop_id: id for currently viewed drop
    :return: node id view page
    """
    message = {
        'action': FrontendAction.GET_PUBLIC_KEY,
    }

    response = send_message(message)
    message = response.get('message')

    return show_drop(
        drop_id,
        message,
    )


@app.route('/')
def startup():
    """Show the main page.

    :return: The main page
    """
    return show_drop()


@app.route('/drop/<drop_id>', methods=['GET', 'POST'])
def show_drops(drop_id=None, message=None, current_path=None):
    """Show a drop with curr action as none.

    This causes show_drop to request pending changes as well.

    :param drop_id: The drop id
    :param message: Message to show
    :current_path: Current path in a subscribe/create action
    :return: View drop page
    """
    return show_drop(drop_id, message, current_path)


def show_drop(drop_id=None, message=None, current_path=None, curr_action=None):
    """
    Show a drop.

    :param drop_id: ID of current drop
    :param message: Message from a particular action
    :param current_path: current directory recognized
    :param curr_action: The action to do
    :return: renders web page based off of drop and action.
    """
    drop_tups = get_owned_subscribed_drops()
    if drop_tups is not None:
        owned_drops = drop_tups[0]
        subscribed_drops = drop_tups[1]
    else:
        owned_drops = []
        subscribed_drops = []

    selected_drop = []
    new_ver = None
    new_updates = None
    permission = None

    file_status = {}
    remote_file_status = {}
    added = []
    remote_added = []

    if drop_id is not None:

        if curr_action:
            selected_drop_info = get_selected_drop(drop_id) or {}
        else:
            selected_drop_info = get_pending_changes(drop_id) or {}
        selected_drop = selected_drop_info.get('drop')
        if selected_drop is not None:

            if is_in_drop_list(drop_id, owned_drops):
                permission = "owned"
            else:
                permission = "subscribed"

            # Check if new version can be created
            pending_changes = selected_drop_info.get('pending_changes', {})
            added = pending_changes.get('added', [])
            removed = pending_changes.get('removed', [])
            changed = pending_changes.get('changed', [])
            unchanged = pending_changes.get('unchanged', [])
            for f in removed:
                file_status[f] = 'removed'
            for f in changed:
                file_status[f] = 'changed'
            for f in unchanged:
                file_status[f] = 'unchanged'
            version_update = any([added, removed, changed])
            if version_update and is_in_drop_list(drop_id, owned_drops):
                new_ver = True
                flash('Local changes present. Select NEW VERSION.')

            # Check if new updates are available
            remote_pending_changes = selected_drop_info.get(
                'remote_pending_changes', {},
            )
            remote_added = remote_pending_changes.get('added', [])
            remote_removed = remote_pending_changes.get('removed', [])
            remote_changed = remote_pending_changes.get('changed', [])
            remote_unchanged = remote_pending_changes.get('unchanged', [])
            for f in remote_removed:
                remote_file_status[f] = 'removed'
            for f in remote_changed:
                remote_file_status[f] = 'changed'
            for f in remote_unchanged:
                remote_file_status[f] = 'unchanged'
            remote_update = any([remote_added, remote_removed, remote_changed])
            if remote_update:
                new_updates = True
                flash('Remote updates available. Select DOWNLOAD UPDATES.')

    if message is not None:
        flash(message)

    # Directory Stepping
    folders = []
    if current_path:
        try:
            with scandir('/' + current_path) as entries:
                for entry in entries:
                    if not entry.is_file() and entry.name[0] != '.':
                        folders.append(entry.name)
        except Exception as e:
            flash(e)
            folders = []
    else:
        current_path = home_path

    return render_template(
        'show_drops.html',
        selected=selected_drop,
        subscribed=subscribed_drops,
        owned=owned_drops,
        selec_act=curr_action,
        new_version=new_ver,
        new_updates=new_updates,
        permission=permission,
        directory=current_path,
        directory_folders=folders,
        file_status=file_status,
        remote_file_status=remote_file_status,
        added=added,
        remote_added=remote_added,
    )
