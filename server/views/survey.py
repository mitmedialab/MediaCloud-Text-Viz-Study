import os
import logging
import json
import datetime
import random
from flask import render_template, jsonify, request, make_response

from server import app, db_session, base_dir
from server.models.user import User, VizType

logger = logging.getLogger(__name__)

cookie_names = {
    'tutorial': 'USER_COOKIE',
    'viz': 'VIZ_TOKEN',
    'feedback': 'FEEDBACK_TOKEN',
    'thanks': 'THANKS_TOKEN'
}

def get_user_from_cookie(req, name):
    user_id = req.cookies[name].split('_')[4]
    return db_session.query(User).filter(User.id == user_id).first()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'step' not in request.form:
        logger.debug('Request to homepage')
        return render_template('index.html')

    logger.debug(request.form['step'])

    # Step 1: Consent Form
    if request.form['step'] == 'consent':
        logger.debug('Request to consent page')
        return render_template('consent.html', step='consent')

    # Step 2: Tutorial Video
    if request.form['step'] == 'tutorial':
        logger.debug('Request to tutorial page')

        # Check for existing cookie
        if 'USER_COOKIE' in request.cookies:
            current_user = get_user_from_cookie(request, 'USER_COOKIE')
            return render_template('tutorial.html', step='tutorial', viz_type=current_user.viz_type)

        # Create new user and save to database
        new_user = User()
        db_session.add(new_user)
        db_session.commit()

        # Update new user's cookie and ip address
        user_id = new_user.id
        new_user.cookie = 'MC_TEXT_VIZ_USER_{}'.format(user_id)
        # TODO: double-check this is correct address...?
        # print 'IP ADDRESS'
        # print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
        # print(request.headers.get('X-Forwarded-For', request.remote_addr))
        # print(request.headers.get('X-Real-IP'))
        new_user.ip_address = request.remote_addr

        # Select and save visualization type
        viz_types = map(lambda x: x.name, list(VizType))
        viz_type = viz_types[user_id % len(viz_types)]
        new_user.viz_type = viz_type
        db_session.commit()

        resp = make_response(render_template('tutorial.html', step='tutorial', viz_type=viz_type))
        resp.set_cookie(cookie_names['tutorial'], new_user.cookie)
        return resp

    # Step 3: Visualization
    if request.form['step'] == 'viz':
        logger.debug('Request to visualization page')

        # check for reload
        if cookie_names['viz'] in request.cookies:
            return render_template('error.html')

        # Get info for current user
        current_user = get_user_from_cookie(request, 'USER_COOKIE')
        viz_type = current_user.viz_type

        # save start time
        current_user.start_time = str(datetime.datetime.now())
        db_session.commit()

        resp = make_response(render_template('viz.html', step='viz', viz_type=viz_type))
        resp.set_cookie(cookie_names['viz'], 'true')
        return resp

    # Step 4: Feedback
    if request.form['step'] == 'feedback':
        logger.debug('Request to feedback page')

        # check for reload
        if cookie_names['feedback'] in request.cookies:
            return render_template('error.html')

        # save response from previous page (viz)
        save_viz_response(request)

        resp = make_response(render_template('feedback.html', step='feedback'))
        resp.set_cookie(cookie_names['feedback'], 'true')
        return resp

    # Step 5: Thank you
    if request.form['step'] == 'thanks':
        logger.debug('Request to thank-you page')

        # check for reload
        if cookie_names['thanks'] in request.cookies:
            return render_template('error.html')

        # Save feedback to database
        current_user = get_user_from_cookie(request, 'USER_COOKIE')
        current_user.feedback = request.form['general_feedback']
        db_session.commit()

        resp = make_response(render_template('thanks.html'))
        resp.set_cookie(cookie_names['thanks'], 'true')
        return resp

def save_viz_response(request):
    current_user = get_user_from_cookie(request, 'USER_COOKIE')
    current_user.theme1 = request.form['theme1']
    current_user.theme1_word1 = request.form['theme1_word1']
    current_user.theme1_word2 = request.form['theme1_word2']
    current_user.theme1_word3 = request.form['theme1_word3']
    current_user.theme2 = request.form['theme2']
    current_user.theme2_word1 = request.form['theme2_word1']
    current_user.theme2_word2 = request.form['theme2_word2']
    current_user.theme2_word3 = request.form['theme2_word3']
    current_user.end_time = str(datetime.datetime.now())

    db_session.commit()


@app.route('/vizTutorialData.json', methods=['GET'])
def vizTutorialData():
    logger.debug('Request to tutorial visualization data')

    file_path = os.path.join(base_dir, 'server/static/vizTutorialData.json')
    with open(file_path) as viz_data:
        results = json.load(viz_data)

    return jsonify(results)


@app.route('/vizData.json', methods=['GET'])
def vizData():
    logger.debug('Request to visualization data')

    file_path = os.path.join(base_dir, 'server/static/vizData.json')
    with open(file_path) as viz_data:
        results = json.load(viz_data)

    return jsonify(results)
