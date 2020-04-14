from flask import Blueprint, request, render_template, jsonify, abort, current_app
# dealing with error
from psiturk.experiment_errors import ExperimentError

# Database setup
from psiturk.db import db_session, init_db
from psiturk.models import Participant
# dealing with json like reading from database
from json import dumps, loads

# explore the Blueprint
custom_code = Blueprint('custom_code', __name__, template_folder='templates', static_folder='static')

#----------------------------------------------
# example computing bonus
#----------------------------------------------

@custom_code.route('/compute_bonus', methods=['GET'])
def compute_bonus():
    # check that user provided the correct keys
    # errors will not be that gracefull here if being
    # accessed by the Javascrip client
    if not 'uniqueId' in request.args:
        # i don't like returning HTML to JSON requests...  maybe should change this
        raise ExperimentError('improper_inputs')
    uniqueId = request.args['uniqueId']

    try:
        # lookup user in database
        user = Participant.query.\
            filter(Participant.uniqueid == uniqueId).\
            one()
        user_data = loads(user.datastring)  # load datastring from JSON

        for record in user_data['data']:  # for line in data file
            trial = record['trialdata']
            if trial['phase'] == 'Points Collected':
                bonus = float(trial['Total Points']) / 10. * 0.01  # payout one cent per trial, for now
                    
        user.bonus = bonus
        db_session.add(user)
        db_session.commit()
        resp = {"bonusComputed": "success"}
        return jsonify(**resp)
    except:
        abort(404)  # again, bad to display HTML, but...
