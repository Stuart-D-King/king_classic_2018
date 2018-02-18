import pandas as pd
import numpy as np
import sys
import pickle
import pdb
from pymongo import MongoClient
from collections import defaultdict


# def main():
#     client = MongoClient()
#     # Access/Initiate Database
#     db = client['kc_2018']
#     # Access/Initiate Table
#     tbl = db['scores']
#
#     tbl.insert({'item': 'card', 'qty' : 15})



class Player(object):

    def __init__(self, name, skins=True):
        self.name = name
        self.skins = skins
        self.scores = dict()
        self.courses = ["Talking Stick - O'odham",
                        'Talking Stick - Piipaash',
                        'Wildfire - Palmer',
                        'Wildfire - Faldo',
                        "Whirlwind - Devil's Claw",
                        'Whirlwind - Cattail']
        for course in self.courses:
            self.create_scoredcard(course)


    def create_scorecard(self, course):
        self.scores[course] = dict((x,0) for x in range(1,19))


    def post_score(self, course, hole, score):
        # if course in self.scores.keys():
        #     self.scores[course][hole] = score
        # else:
        #     self.create_scorecard(course)
        #     self.scores[course][hole] = score

        self.scores[course][hole] = score


    def show_scorecard(self, course):
        # if course in self.scores.keys():
        #     print(self.scores[course])
        # else:
        #     self.create_scorecard(course)
        #     print(self.scores[course])

        print(self.scores[course])


    def calc_course_score(self, course):
        score = sum(self.scores[course].values())
        print('Player: {}, Course: {}, Score: {}'.format(self.name, course, score))
        return score


    def calc_total_score(self):
        total = 0
        for course in self.scores.keys():
            total += sum(self.scores[course].values())

        print('Player: {}, Total Score: {}'.format(self.name, total))
        return total



class PlayGolf(object):

    def __init__(self, name, skins, init=False):
        # self.golfers = [('Stuart King', True),
        #                 ('Alex King', True),
        #                 ('Jerry King', True),
        #                 ('Reggie Sherrill', True),
        #                 ('Chet Cheek', False),
        #                 ('Jeff Veness', False),
        #                 ('Bobby Jovanov', True),
        #                 ('Zach Taylor', True),
        #                 ('Andy Tapper', True),
        #                 ('Ben Donahue', False),
        #                 ('Pete Nash', False),
        #                 ('Mathias Jackson', False),
        #                 ('Paul Hoover', False),
        #                 ('Ryan Veness', False),
        #                 ('Chris Marsh', True),
        #                 ('Josh Duckett', True)]

        # self.courses = ["Talking Stick - O'odham",
        #                 'Talking Stick - Piipaash',
        #                 'Wildfire - Palmer',
        #                 'Wildfire - Faldo',
        #                 "Whirlwind - Devil's Claw",
        #                 'Whirlwind - Cattail']

        if init:
            self.players = dict()
            for name, skins in self.golfers:
                self.create_player(name, skins)
        else:
            self.players = self.load()

        self.names = list(self.players.keys())
        self.team1 = ['Stuart', 'Zach', 'Chet']
        self.team2 = ['Alex', 'Jeff', 'Reggie']
        self.team3 = ['Jerry', 'Bobby', 'Scott']
        self.teams = [self.team1, self.team2, self.team3]


    def create_player(self, name, skins):
        if name not in self.players.keys():
            self.players[name] = Player(name, skins)


    def load(self):
        with open('players.pkl', 'rb') as f:
            players = pickle.load(f)
        return players


    def save(self):
        with open('players.pkl', 'wb') as f:
            pickle.dump(self.players, f, protocol=pickle.HIGHEST_PROTOCOL)


    def add_score(self, player, course, hole, score):
        self.players[player].post_score(course, hole, score)
        self.save()


    def show_team_score(self, team, course):
        team_score = team.calc_team_score(course)
        return 'Team: {}, Score: {}'.format(team.keys())


    def leaderboard(self):
        scores = []
        for player in self.players.values():
            scores.append(player.calc_course_score())
            # total = 0
            # for course in player.keys():
            #     total += sum(player[course].values())
            # scores.append(total)

        results = list(zip(self.names, scores))
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

        for order, (name, total) in enumerate(sorted_results):
            print('{}. {}, Score: {}'.format(order+1, name, total))


    def calc_skins(self, course):
        print('Skins for {}'.format(course))
        print('------------')
        pot = len(self.names) * 10
        cols = [str(x) for x in range(1, 19)]

        scores = []
        for player in self.players.values():
            scores.append(list(player.scores[course].values()))

        df = pd.DataFrame(data=scores, index=self.names, columns=cols)
        low_scores = df.min(axis=0)
        skins = []
        for hole, low_score in zip(range(1, 19), low_scores):
            if any(df[str(hole)] == 0):
                print('ERROR! Someone recorded an impossible score')
                continue

            scores = list(df[str(hole)].values)
            if scores.count(low_score) == 1:
                skins.append(df[str(hole)].idxmin())

        results = []
        for name in self.names:
            results.append((name, skins.count(name)))

        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

        total_skins = sum(n for _, n in sorted_results)
        skin_value = pot / total_skins

        final_results = [(name, skins * skin_value) for name, skins in sorted_results]

        for name, winnings in final_results:
            print('Player: {}, Skins: {}, Winnings: ${}'.format(name, int(winnings/skin_value), int(winnings)))

    def calc_team_scores(self, players, course, verbose=False):
        team = defaultdict(list)
        names = []
        for player in players:
            names.append(player.name)
            for course, score in player.scores.items():
                team[course].append(list(score.values()))

        cols = [str(x) for x in range(1, 19)]
        scores = list(team.values())[0]

        df = pd.DataFrame(data=scores, index=names, columns=cols)
        combined_scores = list(df.nsmallest(2,'1').sum(axis=0).values)
        low_scores = list(df.nsmallest(1,'1').sum(axis=0).values)

        if verbose:
            print('Team Scores:\n------------')
            for hole, (c_score, l_score) in enumerate(zip(combined_scores, low_scores)):
                print('Hole: {}, Combined Score: {}, Low Score: {}'.format(hole+1, c_score, l_score))

        return combined_scores, low_scores

    def calc_team_results(self, course):
        pot = len(self.names) * 10

        combined_team_scores = []
        low_team_scores = []
        for team in self.teams:
            combined_scores, low_scores = calc_team_scores(team, course)
            combined_team_scores.append(combined_scores)
            low_team_scores.append(low_scores)

        dct = dict((x,0) for x in range(1,4))
        cols = [str(x) for x in range(1, 19)]
        idx = list(range(1,4))

        df_combined = pd.DataFrame(data=combined_team_scores, index=idx, columns=cols)
        df_low = pd.DataFrame(data=low_team_scores, index=idx, columns=cols)

        combined_low = df_combined.min(axis=0)
        low_low = df_low.min(axis=0)

        for hole, (c_low, l_low) in enumerate(zip(combined_low, low_low)):
            c_scores = list(df_combined[str(hole+1)].values)
            l_scores = list(df_low[str(hole+1)].values)

            if c_scores.count(c_low) == 1:
                winner = df_combined[str(hole+1)].idxmin()
                dct[winner] += 1

            if l_scores.count(l_low) == 1:
                winner = df_low[str(hole+1)].idxmin()
                dct[winner] += 1


        results = [(key, value) for key, value in dct.items()]
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)

        points = [n for _, n in sorted_results]
        max_points = max(points)
        min_points = min(points)
        if points.count(max_points) == 1 and points[1] != points[2]:
            first_place_winnings = pot * (2/3)
            second_place_winnings = pot * (1/3)
            first_team, first_points = results[0]
            second_team, second_points = results[1]
            print('First place: Team {}, Point total: {}, Winnings: ${}'.format(first_team, first_points, first_place_winnings))
            print('Second place: Team {}, Point total: {}, Winnings: ${}'.format(second_team, second_points, second_place_winnings)))

        if points.count(max_points) == 1 and points[1] == points[2]:
            first_place_winnings = pot * (2/3)
            second_place_winnings = 0
            first_team, first_points = results[0]
            second_team1, second_points1 = results[1]
            second_team2, second_points2 = results[2]
            print('First place: Team {}, Point total: {}, Winnings: ${}'.format(first_team, first_points, first_place_winnings))
            print('Second place tie between Teams {} and {} with {} points - No payout'.format(second_team1, second_team2, second_points))

        if points.count(max_points) == 2:
            first_place_winnings = pot * (1/2)
            second_place_winnings = pot * (1/2)
            first_team1, first_points1 = results[0]
            first_team2, first_points2 = results[1]
            print('First place (tie): Teams {} and {}, Point total: {}, Winnings per team: ${}'.format(first_team1, first_team2, first_points1, first_place_winnings))


    def player_scorecard(self, player, course):
        dct = self.players[player].show_scorecard(course)
        print('Course: {}'.fromat(course))
        print('------------')
        for hole, score in dct.items():
            print('Hole: {}, Score: {}'.format(hole, score))


if __name__ == '__main__':

    # if len(sys.argv) > 1:
    #     if sys.argv[1] == "init":
    #         golf = PlayGolf(True)
    # else:
        # golf = PlayGolf()

    stuart = Player('Stuart', True)
    stuart.post_score('Talking Stick - Piipaash', 1, 5)
    stuart.post_score('Talking Stick - Piipaash', 2, 4)
    stuart.post_score('Talking Stick - Piipaash', 3, 5)

    stuart.show_scorecard('Talking Stick - Piipaash')
    tsp_stu = stuart.calc_course_score('Talking Stick - Piipaash')
    total_stu = stuart.calc_total_score()

    alex = Player('Alex', True)
    alex.post_score('Talking Stick - Piipaash', 1, 4)
    alex.post_score('Talking Stick - Piipaash', 2, 4)
    alex.post_score('Talking Stick - Piipaash', 3, 3)

    jerry = Player('Jerry', True)
    jerry.post_score('Talking Stick - Piipaash', 1, 6)
    jerry.post_score('Talking Stick - Piipaash', 2, 5)
    jerry.post_score('Talking Stick - Piipaash', 3, 4)

    group1 = [stuart, alex, jerry]
    team1 = Team(group1)
    t1_combined, t1_low = team1.calc_team_scores('Talking Stick - Piipaash')

    # golf.add_score("Stuart", "Talking Stick - Piipaash", 1, 5)
    # golf.add_score("Stuart", "Talking Stick - Piipaash", 2, 3)
    # golf.add_score("Stuart", "Talking Stick - Piipaash", 3, 4)
    #
    # golf.add_score("Alex", "Talking Stick - Piipaash", 1, 4)
    # golf.add_score("Alex", "Talking Stick - Piipaash", 2, 4)
    # golf.add_score("Alex", "Talking Stick - Piipaash", 3, 4)
    #
    # golf.add_score("Jerry", "Talking Stick - Piipaash", 1, 4)
    # golf.add_score("Jerry", "Talking Stick - Piipaash", 2, 5)
    # golf.add_score("Jerry", "Talking Stick - Piipaash", 3, 3)

    # golf.calc_skins("Talking Stick - Piipaash")
    # golf.leaderboard()
