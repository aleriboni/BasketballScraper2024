def map_event_type(description):
        mapping = {
            'substitution': 'sub',
            'falli di squadra': 'foul',
            'fallo commesso': 'foul',
            'palla contesa': 'jump ball',
            'palla persa': 'turnover',
            'palle perse di squadra': 'turnover',
            'rimbalzo difensivo': 'rebound',
            'rimbalzi difensivi di squadra': 'rebound',
            'rimbalzo offensivo': 'rebound',
            'rimbalzi offensivi di squadra': 'rebound',
            'tiro libero sbagliato': 'free throw',
            'tiro libero segnato': 'free throw',
            '2 punti sbagliato': 'miss',
            '2 punti segnato': 'shot',
            '3 punti sbagliato': 'miss',
            '3 punti segnato': 'shot',
            'inizio tempo': 'start of period',
            'fine tempo': 'end of period',
            'time out': 'timeout',
        }

        if description.lower() in mapping:
            return mapping[description.lower()]
        else:
            return None

def map_points(description):
    mapping = {
        'tiro libero sbagliato': 0,
        'tiro libero segnato': 1,
        '2 punti sbagliato': 0,
        '2 punti segnato': 2,
        '3 punti sbagliato': 0,
        '3 punti segnato': 3,

    }

    if description.lower() in mapping:
        return mapping[description.lower()]
    else:
        return None

def map_reason(descriptions):
    mapping = {
        '3 secondi': '3 second violation',
        '5 secondi': '5 second violation',
        '8 secondi': '8 second violation',
        'antisportivo': 'flagrant foul',
        'antisportivo su tiro': 'shooting flagrant foul',
        'doppio': 'double dribble turnover',
        'doppio palleggio': 'discontinue dribble turnover',
        'espulsione': 'ejection',
        'fuori dal campo': 'out of bounds lost ball turnover',
        'infrazione di campo': 'backcourt',
        'offensivo': 'offensive foul',
        'palleggio': 'lost ball',
        'passaggio sbagliato': 'bad pass',
        'passi': 'traveling',
        'personale': 'personal foul',
        'tecnico': 'techincal foul',
        'tecnico allenatore': 'coach technical foul',
        'tiro': 'shooting foul',
        'violazione 24sec': 'shot clock violation',
    }
    for description in descriptions:
        if description and description.lower() in mapping:
            return mapping[description.lower()]
    return ''

def map_type(entry):

    mapping_description = {
        'palla contesa': 'jump ball',
        # 'palla persa': 'turnover',
        # 'palle perse di squadra': 'TOV',
        'rimbalzo difensivo': 'rebound defensive',
        'rimbalzi difensivi di squadra': 'team rebound',
        'rimbalzo offensivo': 'rebound offensive',
        'rimbalzi offensivi di squadra': 'team rebound',

        'inizio tempo': 'start of period',
        'fine tempo': 'end of period',
        'time out': 'timeout: regular',
    }

    mapping_flags = {
        '3 secondi': '3 second violation',
        '5 secondi': '5 second violation',
        '8 secondi': '8 second violation',
        'antisportivo': 'flagrant foul',
        'antisportivo su tiro': 'shooting flagrant foul',
        'doppio': 'double dribble turnover',
        'doppio palleggio': 'discontinue dribble turnover',
        'espulsione': 'ejection',
        'fuori dal campo': 'out of bounds lost ball turnover',
        'infrazione di campo': 'backcourt',
        'offensivo': 'offensive foul',
        'palleggio': 'lost ball',
        'passaggio sbagliato': 'bad pass',
        'passi': 'traveling',
        'personale': 'personal foul',
        'tecnico': 'techincal foul',
        'tecnico allenatore': 'coach technical foul',
        'tiro': 'shooting foul',
        'violazione 24sec': 'shot clock violation',
        # 'alley-oop': 'ALLEY-OOP',
        'altro': None,
        'appoggio a canestro': 'Layup',
        'arresto e tiro': 'Pullup',
        'da penetrazione': 'Driving',
        'gancio': 'Hook Shot',
        'giro e tiro': 'Turnaround shot',
        'schiacciata': 'Dunk',
        'stoppata': None,
        'tiro in corsa': 'Floating Jump Shot',
        'tiro in fadeaway': 'Fadeaway Jumper',
        'tiro in sospensione': 'Jump Shot',
        'tiro in step back': 'Step Back Jump Shot',
    }

    if entry['description'].lower() in mapping_description:
        return mapping_description[entry['description'].lower()]

    if entry['description'].lower() in ['tiro libero segnato', 'tiro libero sbagliato']:
        return f'Free Throw {entry["num"]} of {entry["outof"]}'

    for el in [entry['action_1_qualifier_description'], entry['action_2_qualifier_description']]:
        if el and el.lower() == 'alley-oop':
            if entry['dunk']:
                return 'Alley Oop Dunk'
            else:
                return 'Alley Oop Layup'

    for description in [entry['action_1_qualifier_description'], entry['action_2_qualifier_description']]:
        if description and description.lower() in mapping_flags:
            return mapping_flags[description.lower()]

    return ''

def map_phase(code):
    mapping = {
        'andata': 'Regular Season',
        'ritorno': 'Regular Season',
        'seconda fase': 'Clock Round',
        'ottavi': 'Playoffs',
        'quarti': 'Playoffs',
        'quarti di finale': 'Playoffs',
        'semifinali': 'Playoffs',
        'finale': 'Playoffs',
        'finali': 'Playoffs',
        'girone a': 'Regular Season',
        'girone b': 'Regular Season',
        'girone c': 'Regular Season',
        'girone d': 'Regular Season',
        'Finale 3°/4° Posto': 'Playoffs',
    }

    if code.lower() in mapping:
        return mapping[code.lower()]
    else:
        print(f"{code} not recognized in allowed values")
        return None