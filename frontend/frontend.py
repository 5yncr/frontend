from flask import Flask
from flask import render_template

app = Flask(__name__)  # create the application instance
app.config.from_object(__name__)  # load config from this file , frontend.py

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    TEMPLATES_AUTO_RELOAD=True,
))
app.config.from_envvar('SYNCR_SETTINGS', silent=True)

# Backend Access Functions


def get_owned_drops():
    return [{'name': 'O_Drop_1'}, {'name': 'O_Drop_2'}]


def get_subscribed_drops():
    return [{'name': 'S_Drop_1'}, {'name': 'S_Drop_2'}, {'name': 'S_Drop_3'}]


def get_selected_drop(drop_id):
    return [drop_id]


@app.route('/')
def startup():
    return show_drops(None)


@app.route('/<drop_id>')
def show_drops(drop_id=None):
    owned_drops = get_owned_drops()
    subscribed_drops = get_subscribed_drops()
    selected_drop = []
    if drop_id is not None:
        selected_drop = get_selected_drop(drop_id)
    return render_template(
        'show_drops.html', selected=selected_drop,
        subscribed=subscribed_drops, owned=owned_drops,
    )


@app.route('/initialize', methods=['GET', 'POST'])
def initialize():
    return startup()
    # if request.method == 'POST':
    #    session['logged_in'] = True
    #    flash('You were logged in')
    #    return redirect(url_for('show_drops'))
    # return render_template('initialize.html')
