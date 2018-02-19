import os
import logging
import json
import datetime
from flask import render_template, jsonify, request

from server import app, db_session, base_dir
from server.models.user import User, Response, VizType

logger = logging.getLogger(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'step' not in request.form:
        logger.debug('Request to homepage')
        return render_template('index.html')

    print(request.form['step'])

    # Step 1: Consent Form
    if request.form['step'] == 'consent':
        logger.debug('Request to consent page')
        return render_template('consent.html', step='consent')

    # Step 2: Tutorial Video
    if request.form['step'] == 'tutorial':
        logger.debug('Request to tutorial page')
        # Create new user and save to database
        new_user = User(consent=True)
        db_session.add(new_user)
        db_session.commit()
        info = {"user_id": new_user.id}
        return render_template('tutorial.html', info=json.dumps(info), step='tutorial')

    # Step 3: Visualization 1
    if request.form['step'] == 'viz1':
        logger.debug('Request to visualization page')
        info = json.loads(request.form['info'])
        # TODO: Randomize and/or serialize order of viz types
        current_user_id = info['user_id']
        viz_types = map(lambda x: x.name, list(VizType))
        # info[viz_type] = viz_types[current_user_id % len(viz_types)]
        info['viz_order'] = viz_types
        # update info for next viz
        info['viz_type'] = info['viz_order'][0]
        info['start_time'] = str(datetime.datetime.now())
        return render_template('viz.html', info=json.dumps(info), step='viz1')

    # Step 4: Visualization 2
    if request.form['step'] == 'viz2':
        logger.debug('Request to visualization page')
        save_viz_response(request) # save response from previous page (viz 1)
        # update info for next viz
        info = json.loads(request.form['info'])
        info['viz_type'] = info['viz_order'][1]
        info['start_time'] = str(datetime.datetime.now())
        return render_template('viz.html', info=json.dumps(info), step='viz2')

    # Step 5: Visualization 3
    if request.form['step'] == 'viz3':
        logger.debug('Request to visualization page')
        save_viz_response(request) # save response from previous page (viz 2)
        # update info for next viz
        info = json.loads(request.form['info'])
        info['viz_type'] = info['viz_order'][2]
        info['start_time'] = str(datetime.datetime.now())
        return render_template('viz.html', info=json.dumps(info), step='viz3')

    # Step 6: Feedback
    if request.form['step'] == 'feedback':
        logger.debug('Request to feedback page')
        save_viz_response(request) # save response from previous page (viz 3)
        info = json.loads(request.form['info'])
        info = {'user_id': info['user_id']}
        return render_template('feedback.html', info=json.dumps(info), step='feedback')

    # Step 7: Thank you
    if request.form['step'] == 'thanks':
        logger.debug('Request to thank-you page')
        # Save feedback to database
        feedback = request.form['general_feedback']
        current_user_id = json.loads(request.form['info'])['user_id']
        current_user = db_session.query(User).filter(User.id == current_user_id).first()
        current_user.feedback = feedback
        db_session.commit()
        return render_template('thanks.html', data=json.dumps(str(current_user)))

def save_viz_response(request):
    # Retrieve responses
    theme1 = request.form['theme1']
    theme1_word1 = request.form['theme1_word1']
    theme1_word2 = request.form['theme1_word2']
    theme1_word3 = request.form['theme1_word3']
    theme2 = request.form['theme2']
    theme2_word1 = request.form['theme2_word1']
    theme2_word2 = request.form['theme2_word2']
    theme2_word3 = request.form['theme2_word3']
    info = json.loads(request.form['info'])
    viz_type = info['viz_type']
    current_user_id = info['user_id']
    start_time = info['start_time']
    end_time = str(datetime.datetime.now())

    # Add to database
    current_user = db_session.query(User).filter(User.id == current_user_id).first()
    user_response = Response(theme1=theme1, theme1_word1=theme1_word1, theme1_word2=theme1_word2, theme1_word3=theme1_word3,
                             theme2=theme2, theme2_word1=theme2_word1, theme2_word2=theme2_word2, theme2_word3=theme2_word3,
                             viz_type=viz_type, start_time=start_time, end_time=end_time)

    current_user.responses.append(user_response)
    db_session.commit()


@app.route('/vizData.json', methods=['GET'])
def vizData():
    logger.debug('Request to visualization data')

    file_path = os.path.join(base_dir, 'server/static/vizData.json')
    with open(file_path) as viz_data:
        results = json.load(viz_data)

    return jsonify(results)
