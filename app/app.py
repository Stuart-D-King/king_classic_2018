import numpy as np
import pandas as pd
from pymongo import MongoClient
from king_classic import PlayGolf, Player
from flask import Flask, request, redirect, url_for, render_template
import pdb

app = Flask(__name__)
golf = PlayGolf('2018')


# home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# past results
@app.route('/past_results', methods=['GET'])
def past_results():
    return render_template('past_results.html')


# add a player
@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        f_name = request.form['first_name']
        l_name = request.form['last_name']
        skins = request.form['in_skins']
        golf.add_player(f_name + ' ' + l_name, skins)
        return redirect(url_for('add_player'))

    return render_template('add_player.html')


# enter scores
@app.route('/enter_scores', methods=['GET', 'POST'])
def enter_scores():
    players = golf.coll.distinct('name')
    players.append('None')
    holes = [x for x in range(1,19)][::-1]
    scores = [x for x in range(1,11)][::-1]
    scores.append('None')
    if request.method == 'POST':
        course = request.form['course']
        hole = int(request.form['hole'])
        golfers = [request.form['player1'], request.form['player2'], request.form['player3'], request.form['player4']]
        g_scores = [int(request.form['score1']), int(request.form['score2']), int(request.form['score3']), int(request.form['score4'])]
        gns = list(zip(golfers, g_scores))
        for golfer, score in gns:
            golf.add_score(golfer, course, hole, score)
        # return render_template('enter_scores.html', players=players, holes=holes, scores=scores)
        return redirect(url_for('enter_scores'))

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
        course = request.form['skins_course']
        skins_df = golf.calc_skins(course)
        return render_template('skins.html', skins_df=skins_df.to_html(index=False))
        # return redirect(url_for('skins'))

    return render_template('skins.html')


# scorecard page
@app.route('/scorecard', methods=['GET', 'POST'])
def scorecard():
    players = golf.coll.distinct('name')
    if request.method == 'POST':
        course = request.form['scorecard_course']
        golfers = request.form.getlist('golfers')
        scorecard_df = golf.player_scorecards(golfers, course)
        return render_template('scorecard.html', players=players, scorecard_df=scorecard_df.to_html())

    return render_template('scorecard.html', players=players)


# teams page
@app.route('/team_standings', methods=['GET', 'POST'])
def team_standings():
    return render_template('team_standings.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8105, threaded=True)
