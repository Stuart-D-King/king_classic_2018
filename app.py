import numpy as np
import pandas as pd
from pymongo import MongoClient
from king_classic import PlayGolf, Player
from flask import Flask, request, redirect, url_for, render_template
from collections import Counter
import pdb


app = Flask(__name__)
golf = PlayGolf('2018')


# home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# general info page
@app.route('/general_info', methods=['GET'])
def general_info():
    return render_template('general_info.html')


# locations map
@app.route('/past_locations', methods=['GET'])
def past_locations():
    return render_template('past_locations.html')


# past results page
@app.route('/past_results', methods=['GET'])
def past_results():
    return render_template('past_results.html')


# add a player page
@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        f_name = request.form['first_name'].capitalize()
        l_name = request.form['last_name'].capitalize()
        hdcp = int(request.form['hdcp'])
        skins = request.form['in_skins']
        if skins == 'True':
            skins = True
        else:
            skins = False
        full_name = f_name.strip() + ' ' + l_name.strip()
        full_name = full_name
        # pdb.set_trace()
        golf.add_player(full_name, hdcp, skins)
        msg = 'Player added successfully'
        return render_template('add_player.html', msg=msg)

    return render_template('add_player.html')


# enter scores page
@app.route('/enter_scores', methods=['GET', 'POST'])
def enter_scores():
    players = golf.coll.distinct('name')
    players.sort()
    # players.append('None')
    holes = [x for x in range(1,19)]
    scores = [x for x in range(1,11)]
    # scores.append('None')
    if request.method == 'POST':
        try:
            course = request.form['course']
            hole = int(request.form['hole'])

            golfers = [request.form['player1'], request.form['player2'], request.form['player3'], request.form['player4']]
            golfers = [golfer for golfer in golfers if golfer != 'None']

            g_scores = [request.form['score1'], request.form['score2'], request.form['score3'], request.form['score4']]
            g_scores = [int(score) for score in g_scores if score != "None"]

            if course == 'None' or hole == 0 or not g_scores or not golfers:
                msg = 'An error occured. Please ensure a course, hole, and at least one golfer and score are selected.'
                return render_template('enter_scores.html', players=players, holes=holes, scores=scores, msg=msg)

            if len([x for x, count in Counter(golfers).items() if count > 1]) >= 1:
                msg = 'The same golfer was selected twice. Please try again.'
                return render_template('enter_scores.html', players=players, holes=holes, scores=scores, msg=msg)

            gns = list(zip(golfers, g_scores))
            for golfer, score in gns:
                golf.add_score(golfer, course, hole, score)

            scorecard_df = golf.player_scorecards(golfers, course)
            msg = 'Scores entered successfully!'

            return render_template('enter_scores.html', players=players, holes=holes, scores=scores, msg=msg, scorecard_df=scorecard_df.to_html(), course=course)
        except:
            msg = 'An error occurred. Please try again.'
            return render_template('enter_scores.html', players=players, holes=holes, scores=scores, msg=msg)

    return render_template('enter_scores.html', players=players, holes=holes, scores=scores)


# leaderboard page
@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    leaderboard_df = golf.leaderboard()
    return render_template('leaderboard.html', leaderboard_df=leaderboard_df.to_html(index=False))


# skins page
@app.route('/skins', methods=['GET', 'POST'])
def skins():
    if request.method == 'POST':
        try:
            course = request.form['skins_course']
            if course == 'None':
                error_msg = 'Please select a course'
                return render_template('skins.html', error_msg=error_msg)
            # pdb.set_trace()
            skins_df = golf.calc_skins(course)

            return render_template('skins.html', skins_df=skins_df.to_html(index=False), c=course)

        except:
            no_skins_msg = 'No skins were won'
            return render_template('skins.html', no_skins_msg=no_skins_msg)

    return render_template('skins.html')


# scorecard page
@app.route('/scorecard', methods=['GET', 'POST'])
def scorecard():
    players = golf.coll.distinct('name')
    players.sort()
    if request.method == 'POST':
        course = request.form['scorecard_course']
        if course == 'None':
            msg = 'Please select a course'
            return render_template('scorecard.html', players=players, msg=msg)

        golfers = request.form.getlist('golfers')
        scorecard_df = golf.player_scorecards(golfers, course)
        return render_template('scorecard.html', players=players, scorecard_df=scorecard_df.to_html(), course=course)

    return render_template('scorecard.html', players=players)


# teams page
@app.route('/team_standings', methods=['GET', 'POST'])
def team_standings():
    return render_template('team_standings.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
