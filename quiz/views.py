import random, json

from django.shortcuts import render
from django.http import HttpResponse

from .utils import lookup
from .models import Team, Conference, Division

players = [{"name": "Giannis Antetokounmpo", "id": 20}, {"name": "Stephen Curry", "id": 124}, {"name": "Luka Doncic", "id": 963}, {"name": "LeBron James", "id": 265}, {"name": "Kawhi Leonard", "id": 314}]

# Create your views here.
def index(request):
    # Get the name of all teams
    teams = Team.objects.order_by("fullName")
    context = {
        "teams": teams,
        "players": players
    }
    return render(request, "index.html", context)
    

def team_quiz(request):   
    # Get team information
    team = Team.objects.get(id=request.POST["quiz-team"])
    divName = str(team.div)
    
    # Get list of Divisions, except for the chosen team's division
    divisions = Division.objects.exclude(name=divName).values_list("name", flat=True)

    # Contact API for quiz data
    quiz_type = "team"
    teamId = request.POST["quiz-team"]
    dataset = lookup(quiz_type, teamId)

    # check that lookup returned data
    if not dataset:
        return render(request, "apology.html")    
    
    # remove players that only played in summer leagues etc. and randomise players
    players = dataset["api"]["players"]
    players = [
        player for player in players if
        "standard" in player["leagues"] and player["affiliation"] != ""
    ]
    players = random.sample(players, len(players))

    # define questions
    # TODO: exclude incorrect answers from picking the same value as the correct answer by chance
    questions = [
    {
        "question": f"What division do the {team.fullName} play in?",
        "answers": {
        "a": f"{divisions[2].capitalize()}",
        "b": f"{divName.capitalize()}",
        "c": f"{divisions[1].capitalize()}"
        },
        "correctAnswer": "b"
    }, 
    {
        "question": f"What jersey number does {players[0]['firstName']} {players[0]['lastName']} wear?",
        "answers": {
        "a": f"{players[0]['leagues']['standard']['jersey']}",
        "b": f"{players[1]['leagues']['standard']['jersey']}",
        "c": f"{players[2]['leagues']['standard']['jersey']}"
        },
        "correctAnswer": "a"
    },
    {
        "question": f"How many years has {players[1]['firstName']} {players[1]['lastName']} been in the league?",
        "answers": {
        "a": f"{random.randint(0,7)}", # TODO: decent chance of being same number as correct answer
        "b": f"{players[1]['yearsPro']}",
        "c": f"{random.randint(8,16)}"  # TODO: decent chance of being the same as a/b, add in code to exclude options
        },
        "correctAnswer": "b"
    },
    {
        "question": f"Where did {players[2]['firstName']} {players[2]['lastName']} play before he entered the NBA?",
        "answers": {
        "a": f"{players[3]['affiliation'].rpartition('/')[0]}",
        "b": f"{players[1]['affiliation'].rpartition('/')[0]}",
        "c": f"{players[2]['affiliation'].rpartition('/')[0]}",
        },
        "correctAnswer": "c"
    },
    {
        "question": f"What year was {players[3]['firstName']} {players[3]['lastName']} born?",
        "answers": {
        "a": f"{players[3]['dateOfBirth'][0:4]}",
        "b": f"{players[4]['dateOfBirth'][0:4]}",
        "c": f"{players[2]['dateOfBirth'][0:4]}"
        },
        "correctAnswer": "a"
    },
    {
        "question": f"How tall is {players[4]['firstName']} {players[4]['lastName']}?",
        "answers": {
        "a": f"{players[5]['heightInMeters']} m",
        "b": f"{players[3]['heightInMeters']} m",
        "c": f"{players[4]['heightInMeters']} m"
        },
        "correctAnswer": "c"
    },
    {
        "question": f"How much does {players[5]['firstName']} {players[5]['lastName']} weigh?",
        "answers": {
        "a": f"{players[5]['weightInKilograms']} kg",
        "b": f"{players[6]['weightInKilograms']} kg",
        "c": f"{players[4]['weightInKilograms']} kg"
        },
        "correctAnswer": "a"
    }
    ]
    # randomise questions
    questionList = random.sample(questions, len(questions))
    correct_answers = []
    for question in questionList:
        correct_answers.append(question["correctAnswer"])
    
    return render(request, "quiz.html", {
        "quiz_type": quiz_type,
        "questionList": questionList,
        "title": team.fullName,
        "team": team,
        "correct_answers": json.dumps(correct_answers)
    })


def player_quiz(request):
    print(f"request is {request.POST}")
    # Contact API for quiz data
    quiz_type = "player"
    playerId = request.POST["quiz-player"]
    dataset = lookup(quiz_type, playerId)

    # check that lookup returned data
    if not dataset:
        return render(request, "apology.html")    

    # extract player info from dataset
    player = dataset["api"]["players"][0]
    colleges = ["Duke", "Kentucky", "Louisiana State University", "North Carolina"]
    countries = ["USA", "Australia", "Lithuania"]
    
    # remove options if they are the same as the actual answer
    if player['collegeName'] in colleges:
        colleges.remove(player['collegeName'])
    
    if player['country'] in countries:
        countries.remove(player['country'])
        

    # define questions
    # TODO: exclude incorrect answers from picking the same value as the correct answer by chance
    questions = [
    {
        "question": f"What country is {player['firstName']} from?",
        "answers": {
        "a": f"{player['country']}",
        "b": f"{countries.pop(random.randint(0, len(countries) - 1))}",
        "c": f"{countries.pop(random.randint(0, len(countries) - 1))}"
        },
        "correctAnswer": "a"
    },
    {
        "question": f"How tall is {player['firstName']}?",
        "answers": {
        "a": f"{round(float(player['heightInMeters']) * 1.1, 2)}m",
        "b": f"{round(float(player['heightInMeters']) * 0.9, 2)}m",
        "c": f"{player['heightInMeters']}m"
        },
        "correctAnswer": "c"
    },
    {
        "question": f"What number does {player['firstName']} wear?",
        "answers": {
        "a": f"{int(player['leagues']['standard']['jersey']) + 5}",
        "b": f"{abs(int(player['leagues']['standard']['jersey']) - 3)}",
        "c": f"{player['leagues']['standard']['jersey']}"
        },
        "correctAnswer": "c"
    },
    {
        "question": f"What year did {player['firstName']} start playing in the NBA?",
        "answers": {
        "a": f"{player['startNba']}",
        "b": f"{int(player['startNba']) + 1}",
        "c": f"{int(player['startNba']) - 1}"
        },
        "correctAnswer": "a"
    },
    {
        "question": f"What does {player['firstName']} weigh?",
        "answers": {
        "a": f"{player['weightInKilograms']}kg",
        "b": f"{round(float(player['weightInKilograms']) * 1.1, 1)}kg",
        "c": f"{round(float(player['weightInKilograms']) * 0.9, 1)}kg"
        },
        "correctAnswer": "a"
    },
    {
        "question": f"Where did {player['firstName']} play before the NBA?",
        "answers": {
        "a": f"{colleges.pop(random.randint(0, len(colleges) - 1))}",
        "b": f"{player['collegeName']}",
        "c": f"{colleges.pop(random.randint(0, len(colleges) - 1))}"
        },
        "correctAnswer": "b"
    },
    {
        "question": f"What year was {player['firstName']} born?",
        "answers": {
        "a": f"{player['dateOfBirth'][0:4]}",
        "b": f"{int(player['dateOfBirth'][0:4]) + 2}",
        "c": f"{int(player['dateOfBirth'][0:4]) - 1}"
        },
        "correctAnswer": "a"
    },

    
    ]
    # randomise questions
    questionList = random.sample(questions, len(questions))
    correct_answers = []
    for question in questionList:
        correct_answers.append(question["correctAnswer"])
    
    return render(request, "quiz.html", {
        "quiz_type": quiz_type,
        "questionList": questionList,
        "title": f"{player['firstName']} {player['lastName']}",
        "player": player,
        "correct_answers": json.dumps(correct_answers)
    })

