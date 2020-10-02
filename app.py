from flask import Flask, render_template,request, session
import pandas as pd

app = Flask(__name__) #create app instance
app.secret_key = 'example' #store this in an environment variable for live apps.
filepath = 'input/'
#read in data
player_df = pd.read_csv(filepath + 'data.csv')
team_df = pd.read_csv(filepath + 'teams_data.csv')

#homepage
@app.route("/", methods = ['GET','POST'])
def H2H():
    #set default form values
    if request.form.get("squadA_select") == None:
        Squad_a = 'Manchester City'
    else:
        Squad_a =request.form.get("squadA_select")
    if request.form.get("squadB_select") == None:
        Squad_b = 'Arsenal'
    else:
        Squad_b =request.form.get("squadB_select")

    #get list of teams and selected teams to feed into html template
    squads = pd.read_csv(filepath + 'squad_list.csv')
    squad_list_a = list(squads.Squad)
    squad_list_b = list(squads.Squad)
    Match = Squad_a +  ' vs. ' + Squad_b
    session['Squad_a'] = Squad_a
    session['Squad_b'] = Squad_b
    session['Match'] = Match
    return render_template("index.html",Squad_a = Squad_a, Squad_b = Squad_b,squad_list_a=squad_list_a, squad_list_b=squad_list_b , Match = Match)

@app.route("/data")
def get_data():
    Squad_a, Squad_b, Match = [session.get('Squad_a', None),session.get('Squad_b', None), session.get('Match', None)]

    df = player_df[(player_df.Squad == Squad_a) | (player_df.Squad == Squad_b)]
    df['Match'] = Match
    return df.to_json(orient='records')

@app.route("/formData")
def get_team_data():
    Squad_a, Squad_b, Match = [session.get('Squad_a', None),session.get('Squad_b', None), session.get('Match', None)]

    df = team_df[(team_df.Squad == Squad_a) | (team_df.Squad == Squad_b)]
    df['Match'] = Match

    return df.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True)