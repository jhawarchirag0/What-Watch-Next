import numpy as np
from flask import Flask, request, jsonify, render_template
import os
import tmdbsimple as tmdb
import requests

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/search',methods=['POST'])
# def search():
#     return render_template('search-results.html')

@app.route('/search',methods=['POST'])
def search():

    # return the data from the API 
    # data is like images, information about the movie, etc.
    movie_name = request.form["movie_name"]
    tmdb.API_KEY = "4d437864b2f333cb0fc07c9b104397c6"
    concat_link = "http://api.themoviedb.org/3/search/movie?query="+movie_name+"&api_key=4d437864b2f333cb0fc07c9b104397c6&language=en-US"
    info = requests.get(concat_link)
    json_edit = info.json()
    id1 = json_edit['results']
    id2 = id1[0]
    movie_id = id2['id']
    gen = requests.get('https://api.themoviedb.org/3/genre/movie/list?api_key=4d437864b2f333cb0fc07c9b104397c6&language=en-US')

    genre_list = gen.json()
    genres_list = []
    genre = id2['genre_ids']
    for i in genre_list['genres']:
        if(i['id'] in genre):
            genres_list.append(i['name'])
    movie = tmdb.Movies(movie_id)
    response = movie.info()
    dict1 = {'title': id2['original_title'],'overview': id2['overview'],'rating': id2['vote_average'],'release date': id2['release_date']}
    cast = movie.credits()['cast']
    crew = movie.credits()['crew']
    actors = []
    x=0
    for i in cast:
        if(i['known_for_department']=='Acting' and x<3):
            xyz = "https://image.tmdb.org/t/p/original"+i['profile_path']
            act1 = [i['name'],i['character'],xyz,i['id']]
            actors.append(act1)
            x+=1
    director=[]
    for i in crew:
        if(i['job']=='Director'):
            director.append(i['name'])
            xyz = "https://image.tmdb.org/t/p/original"+i['profile_path']
            director.append(xyz)
            director.append(i['id'])
            break    

    for i in range(len(actors)):
        concat_2 = "http://api.themoviedb.org/3/person/"+str(actors[i][3])+"?api_key=4d437864b2f333cb0fc07c9b104397c6&language=en-US"
    abc = requests.get(concat_2)
    actor_info = abc.json()
    actors[i].append(actor_info['birthday'])
    actors[i].append(actor_info['place_of_birth'])
    actors[i].append(actor_info['biography'])
    concat_3 = "http://api.themoviedb.org/3/person/"+str(director[2])+"?api_key=4d437864b2f333cb0fc07c9b104397c6&language=en-US"
    abc = requests.get(concat_3)
    director_info = abc.json()
    director.append(director_info['birthday'])
    director.append(director_info['place_of_birth'])
    director.append(director_info['biography'])

    #movie_info:

    movie_title = dict1['title']
    movie_overview = dict1['overview']
    movie_rating = dict1['rating']
    movie_release_date = dict1['release date']
    movie_genres = genres_list
    movie_image = "https://image.tmdb.org/t/p/original"+id2['backdrop_path']

    #Actors_info:

    # actor1_name = actors[0][0]
    # actor1_character = actors[0][1]
    # actor1_image = actors[0][2]
    # actor1_bdate = actors[0][4]
    # actor1_birthplace = actors[0][5]
    # actor1_biography = actors[0][6]

    # actor2_name = actors[1][0]
    # actor2_character = actors[1][1]
    # actor2_image = actors[1][2]
    # actor2_bdate = actors[1][4]
    # actor2_birthplace = actors[1][5]
    # actor2_biography = actors[1][6]

    # actor3_name = actors[2][0]
    # actor3_character = actors[2][1]
    # actor3_image = actors[2][2]   
    # actor3_bdate = actors[2][4]
    # actor3_birthplace = actors[2][5]
    # actor3_biography = actors[2][6]

    #director_info:

    director_name = director[0]
    director_character = "Director"
    director_image = director[1]
    director_bdate = director[3]
    director_birthplace = director[4]
    director_biography = director[5]
                
    movie = [movie_title,movie_overview,movie_rating,movie_release_date,movie_genres,movie_image]
    director = [director_name,director_character,director_image,director_bdate,director_birthplace,director_biography]
    # actor1 = [actor1_name,actor1_character,actor1_image,actor1_bdate,actor1_birthplace,actor1_biography]
    # actor2 = [actor2_name,actor2_character,actor2_image,actor2_bdate,actor2_birthplace,actor2_biography]
    # actor3 = [actor3_name,actor3_character,actor3_image,actor3_bdate,actor3_birthplace,actor3_biography]
    
    return render_template('search-results.html',movien=movie)


if __name__=="__main__":
    app.run(debug=True)