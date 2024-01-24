import math
import mapping_utils
import requests
import json
from typing import Dict, List
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from datetime import timedelta

IN_SUB_STRING = 'Ingresso'
OUT_SUB_STRING = 'Uscita'

def retrieve_info(url: str, auth: str):

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
           'Authorization': auth,
           'accept': 'application/json'}
    
    session = requests.Session()
    retry = Retry(connect=10, backoff_factor=2)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode())
    return None
    
    
def retrieve_games(matches_2023: List[Dict]):

    games = []
    for day in matches_2023:
        for game in day:
            if game['home_final_score'] != 0 and game['visitor_final_score'] != 0:
                games.append({'game_id': game['id'],
                              'date': game['match_datetime'],
                              'data_set': "2023-2024 Regular Season"
                            })
    return games

def retrieve_starters(scores: Dict) -> Dict:

    home = []
    away = []
    for player in scores['ht']['rows']:
        if player['sf'] == '1':
            home.append(f'{player["player_name"]} {player["player_surname"]}'.title())
    for player in scores['vt']['rows']:
        if player['sf'] == '1':
            away.append(f'{player["player_name"]} {player["player_surname"]}'.title())
    return {'home': home, 'away':away}

def handle_substitutions(raw_actions, starters, game_id):

    actions = []

    home_team_players = set(starters['home'])
    away_team_players = set(starters['away'])

    players = {
        1: home_team_players,
        0: away_team_players
    }

    # count the number of in and out substitutions for each team, to check that they are the same
    sub_count = dict()
    for i in [0, 1]:
        sub_count[i] = dict()
        sub_count[i][IN_SUB_STRING] = 0
        sub_count[i][OUT_SUB_STRING] = 0

    for raw_action in raw_actions:
        if raw_action['description'] in [IN_SUB_STRING, OUT_SUB_STRING]:
            sub_count[raw_action['home_club']][raw_action['description']] += 1

    # check that the number of in and out subs is the same
    for team in [1, 0]:
        if sub_count[team][IN_SUB_STRING] != sub_count[team][OUT_SUB_STRING]:
            print(team)
            error = f'{game_id}, {team}, IN: {sub_count[team][IN_SUB_STRING]}, OUT: {sub_count[team][OUT_SUB_STRING]}'
            raise Exception(error)

    pending_subs = {
        0: {
            IN_SUB_STRING: set(),
            OUT_SUB_STRING: set()
        },
        1: {
            IN_SUB_STRING: set(),
            OUT_SUB_STRING: set()
        }
    }

    for raw_action in raw_actions:
    
        if raw_action['description'] not in [IN_SUB_STRING, OUT_SUB_STRING]:
            raw_action['home_players'] = home_team_players.copy()
            raw_action['away_players'] = away_team_players.copy()
            actions.append(raw_action)

        elif raw_action['description'] in [IN_SUB_STRING, OUT_SUB_STRING] and raw_action['player_name'] and raw_action['player_surname']:
            
            player = f'{raw_action["player_name"]} {raw_action["player_surname"]}'.title()

            # 1. se il tipo dell'azione è uscita controllare che non ci siano ingressi in attesa. Se ci sono sostituire, altrimenti inserire in lista
            # 2. se il tipo dell'azione è ingresso controllare che non ci siano uscite in attesa. Se ci sono sostituire, altrimenti inserire in lista

            type_to_look_for = OUT_SUB_STRING if raw_action['description'] == IN_SUB_STRING else IN_SUB_STRING

            # if there is a player waiting to conclude the substitution, we shall replace him
            # if the pending player is an out sub, we shall remove him from the list and add the entering player
            # if the pending player is an in sub, we shall remove the current player from the list and add the entering player
            if pending_subs[raw_action['home_club']][type_to_look_for]:

                if type_to_look_for == OUT_SUB_STRING:  # is not empty
                    player_to_be_removed = pending_subs[raw_action["home_club"]][type_to_look_for].pop()
                    player_to_be_inserted = player
                    # player_to_be_removed = self.players_cache[player_to_be_removed_str]

                else:
                    player_to_be_removed = player
                    player_to_be_inserted = pending_subs[raw_action["home_club"]][type_to_look_for].pop()
                    # player_to_be_inserted = self.players_cache[player_to_be_inserted_str]

                try:
                    players[raw_action['home_club']].remove(player_to_be_removed)
                    players[raw_action['home_club']].add(player_to_be_inserted)

                    # print(f'Sub IN {player_to_be_inserted} for {player_to_be_removed}. On court: {players[raw_action["home_club"]]}')

                except KeyError:
                    error = f'Key Error: could not make substitution {player_to_be_inserted} for {player_to_be_removed}. Game is {game_id}, action is {raw_action["action_id"]} and type is {raw_action["description"]}\nPlayers on court are {players[raw_action["home_club"]]}'
                    raise Exception()

                if len(players[raw_action['home_club']]) != 5:
                    error = f'Error with team {raw_action["team_name"]} in action {raw_action["action_id"]} during game {game_id}:\nthere are not 5 players on court!\nSub: {player_to_be_inserted} for {player_to_be_removed}\nOn court: {players[raw_action["home_club"]]}\nPending: {pending_subs[raw_action["home_club"]]}'
                    raise Exception()

                raw_action['player_in'] = player_to_be_inserted
                raw_action['player_out'] = player_to_be_removed
                raw_action['home_players'] = home_team_players.copy()
                raw_action['away_players'] = away_team_players.copy()
                raw_action['description'] = 'Substitution'

                actions.append(raw_action)

            else:
                pending_subs[raw_action['home_club']][raw_action['description']].add(player)

        else:
            continue

    return actions

def add_ft_count(raw_actions):

    player = None
    num = 0

    for raw_action in raw_actions:
        if raw_action['description'].lower() in {'tiro libero sbagliato', 'tiro libero segnato'}:
            player_ra = ' '.join([raw_action['player_name'], raw_action['player_surname']]).title()
            if player is None or player_ra != player:
                player = player_ra
                num = 1
                raw_action['num'] = num
            else:
                num += 1
                raw_action['num'] = num
        else:
            player = None
            num = 0

    player = None
    outof = 0

    for raw_action in raw_actions[::-1]:
        if raw_action['description'].lower() in {'tiro libero sbagliato', 'tiro libero segnato'}:
            player_ra = ' '.join([raw_action['player_name'], raw_action['player_surname']]).title()
            if player is None or player_ra != player:
                player = player_ra
                outof = raw_action['num']
                raw_action['outof'] = outof
            else:
                raw_action['outof'] = outof
        else:
            player = None
            outof = 0

    return raw_actions


def remove_substitutions(raw_actions):

    actions = []
    for raw_action in raw_actions:
        if raw_action['description'] not in [IN_SUB_STRING, OUT_SUB_STRING]:
            actions.append(raw_action)
    return actions


def create_actions(game, raw_actions: List[Dict], substitutions: bool = True) -> List[Dict]:

    actions = []
    home_score = 0
    away_score = 0

    action_start = timedelta(minutes=0)
    period_start = 1

    for raw_action in raw_actions:

        action = dict()

        action['game_id'] = game['game_id']

        action['data_set'] = game['data_set']
        action['date'] = game['date']

        if substitutions:
            ap_l = sorted(list(raw_action['away_players']))
            for i in range(len(raw_action['away_players'])):
                action[f"a{i + 1}"] = ap_l[i]

            # print(raw_action['away_players'])
            hp_l = sorted(list(raw_action['home_players']))
            for i in range(len(raw_action['home_players'])):
                action[f"h{i + 1}"] = hp_l[i]

        period = raw_action['period']
        action['period'] = period

        # score is in the format 22 - 18 (home - away)
        if raw_action['score']:
            home_score = int(raw_action['score'].split('-')[0])
            away_score = int(raw_action['score'].split('-')[1])

        action['home_score'] = home_score
        action['away_score'] = away_score

        # print(raw_action['minute'], raw_action['seconds'])

        elapsed_time = timedelta(minutes=raw_action['minute'], seconds=raw_action['seconds'])
        elapsed_hours, elapsed_remainder = divmod(elapsed_time.seconds, 3600)
        elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
        elapsed_str = f'{elapsed_minutes:02d}:{elapsed_seconds:02d}'

        period_minutes = 10 if raw_action['period'] <= 4 else 5
        time_duration = timedelta(minutes=period_minutes)

        remaining_time = time_duration - elapsed_time
        remaining_hours, remaining_remainder = divmod(remaining_time.seconds, 3600)
        remaining_minutes, remaining_seconds = divmod(remaining_remainder, 60)
        remaining_str = f'{remaining_minutes:02d}:{remaining_seconds:02d}'

        action['remaining_time'] = remaining_str
        action['elapsed_time'] = elapsed_str
        
        if period != period_start:
            action_start = timedelta(minutes=0)
            period_start = period
        play_length = elapsed_time - action_start
        play_length_hours, play_length_remainder = divmod(play_length.seconds, 3600)
        play_length_minutes, play_length_seconds = divmod(play_length_remainder, 60)
        play_length_str = f'{play_length_minutes:02d}:{play_length_seconds:02d}'
        action['play_length'] = play_length_str
        action_start = elapsed_time

        action['play_id'] = raw_action['action_id']

        action['team'] = raw_action['team_name']

        event_type = mapping_utils.map_event_type(raw_action['description'])

        if event_type is None and raw_action['description'].lower() == "assist":
            actions[-1]['assist'] = ' '.join(
                [raw_action['player_name'], raw_action['player_surname']]).title().strip()
            continue
        elif event_type is None and raw_action['description'].lower() == "stoppata":
            actions[-1]['block'] = ' '.join(
                [raw_action['player_name'], raw_action['player_surname']]).title().strip()
            continue
        elif event_type is None and raw_action['description'].lower() == "fallo subito":
            actions[-1]['opponent'] = ' '.join(
                [raw_action['player_name'], raw_action['player_surname']]).title().strip()
            continue
        elif event_type is None and raw_action['description'].lower() == "palla recuperata":
            actions[-1]['steal'] = ' '.join(
                [raw_action['player_name'], raw_action['player_surname']]).title().strip()
            continue
        elif event_type is None and raw_action['description'].lower() == "stoppata subita":
            continue

        action['event_type'] = event_type

        action['assist'] = ''

        if event_type == 'jump ball' and raw_action['home_club'] and raw_action['player_name'] and raw_action[
            'player_surname']:
            action['away'] = ''
            action['home'] = ' '.join([raw_action['player_name'], raw_action['player_surname']]).title().strip()
        elif event_type == 'jump ball' and not raw_action['home_club'] and raw_action['player_name'] and raw_action[
            'player_surname']:
            action['away'] = ' '.join([raw_action['player_name'], raw_action['player_surname']]).title().strip()
            action['home'] = ''
        else:
            action['away'] = ''
            action['home'] = ''

        action['block'] = ''

        if event_type == 'sub':
            action['entered'] = raw_action['player_in']
            action['left'] = raw_action['player_out']
        else:
            action['entered'] = ''
            action['left'] = ''

        if 'num' in raw_action:
            action['num'] = raw_action['num']
        else:
            action['num'] = None

        action['opponent'] = ''

        if 'outof' in raw_action:
            action['outof'] = raw_action['outof']
        else:
            action['outof'] = None

        if raw_action['player_name'] and raw_action['player_surname']:
            action['player'] = ' '.join([raw_action['player_name'], raw_action['player_surname']]).title().strip()
        else:
            action['player'] = ''

        points = mapping_utils.map_points(raw_action['description'])
        action['points'] = points

        action['possession'] = ''

        action['reason'] = mapping_utils.map_reason(
            [raw_action["action_1_qualifier_description"], raw_action["action_2_qualifier_description"]])

        if points is not None and points > 0:
            action['result'] = 'made'
        elif points is not None and points == 0:
            action['result'] = 'missed'
        else:
            action['result'] = ''

        action['steal'] = ''

        action['type'] = mapping_utils.map_type(raw_action)

        # original coordinates place the origin in the bottom left corner. The coordinate span is (0, 100) for both axis, so we shall divide by the number of feet of the size
        if raw_action['x'] and raw_action['y']:
            x = (raw_action['y'] - 50) * .15
            y = (raw_action['x'] - 50) * .28

            original_x = raw_action['x']
            original_y = raw_action['y']

            if x >= 0:
                x = -x
                y = -y
            # y += (14 - 1.575)

            converted_y = y
            converted_x = x

            converted_y = x
            converted_x = y

            # left side
            if raw_action['side'] == 0:  # and raw_action['side_area_zone'] == 'A':
                x_rim = 5.17

            else:
                x_rim = 91.86 - 5.17

            y_rim = 49.21 / 2
            shot_distance = math.sqrt((converted_x - x_rim) ** 2 + (converted_y - y_rim) ** 2)
        else:
            original_x = None
            original_y = None
            converted_x = None
            converted_y = None
            shot_distance = None

        action['shot_distance'] = shot_distance
        action['original_x'] = original_x
        action['original_y'] = original_y
        action['converted_x'] = converted_x
        action['converted_y'] = converted_y

        action['description'] = raw_action['description']

        actions.append(action)

    return actions