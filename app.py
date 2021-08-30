import os
import numpy as np
import pandas as pd
from numpy import load
from flask import Flask, request, jsonify, render_template, json
import tmdbsimple as tmdb
import requests
from tmdbv3api import TMDb, Movie
from importlib import reload

app=Flask(__name__)
new_df,indices,new_df2 = None,None,None
final_cosine_sim=None
m_id = None
actor1,actor2,actor3,actor4,director=None,None,None,None,None


@app.before_first_request
def before_first_request_func():
    file = 'dataset/tmdb_processed.csv'
    df2 = pd.read_csv(file)
    df2 = df2.fillna("")
    global new_df,indices,new_df2
    new_df2 = df2.iloc[:25000]
    new_df = new_df2.iloc[:10][["title", "overview", "vote_average", "poster_path"]].to_dict("list")
    new_df = json.dumps(new_df)
    indices = pd.DataFrame()
    indices["index"] = new_df2.index
    indices["title"] = new_df2['title']
    # load numpy array from npy file
    global final_cosine_sim
    final_cosine_sim = load('dataset/final_cosine_sim_15k.npy')
    print("Loaded Weights")



@app.route('/')
def home():
    try:
        tmdb = TMDb()
        tmdb.api_key = '036791174fdd67b8996bc53ad1a686f2'
        tmdb.language = 'en'
        tmdb.debug = True

        movie = Movie()
        popularr = movie.popular()
        popular=popularr[:7]

        final_popular={}
        for i in range(len(popular)):
            l=[]
            z=popular[i]['id']
            m = movie.details(z)
            l.append(m.title)
            l.append(m.overview[:140])
            l.append('https://image.tmdb.org/t/p/original//'+m.poster_path)
            final_popular[i]=l

        url="https://api.themoviedb.org/3/movie/upcoming?api_key=036791174fdd67b8996bc53ad1a686f2&language=en-US&page=1"
        
        info = requests.get(url)

        json_edit = info.json()
        a=json_edit['results']
        new_release={}
        for i in range(7):
            x= a[i]['original_title']
            y='https://image.tmdb.org/t/p/original/'+a[i]['backdrop_path']
            z=a[i]['overview'][:140]
            new_release[i]=[x,y,z]


        # for top_rated movie
        link="https://api.themoviedb.org/3/tv/top_rated?api_key=036791174fdd67b8996bc53ad1a686f2&language=en-US&page=1"
        details = requests.get(link)
        json_details = details.json()
        
        return render_template('index1.html',final_popular=final_popular,new_release=new_release,json_details=json_details)
    except Exception as e:
        print(e)
        return render_template('error_catch.html',e="Something went Wrong! " + str(e))


@app.route('/search',methods=['POST'])
def search():
    try:
        global actor1,actor2,actor3,actor4,director
        movie_name = request.form["movie_name"]
        print("Recieved request for movie: " + movie_name)
        tmdb.API_KEY = "036791174fdd67b8996bc53ad1a686f2"
        concat_link = "http://api.themoviedb.org/3/search/movie?query="+movie_name+"&api_key=036791174fdd67b8996bc53ad1a686f2&language=en-US"
        info = requests.get(concat_link)
        if info == None:
            print("Results not fetched")
        else:
            print("Results fetched")
        info = info.json()
        search_df = pd.DataFrame(info['results'])
        search_df = search_df.to_dict(orient='records')[0]
        id2 = search_df.copy()
        search_df['backdrop_path'] = "https://image.tmdb.org/t/p/original" + search_df['backdrop_path']
        movie_id = id2['id']

        gen = requests.get('https://api.themoviedb.org/3/genre/movie/list?api_key=036791174fdd67b8996bc53ad1a686f2&language=en-US')
        genre_list = gen.json()

        genres_list = []
        genre = id2['genre_ids']
        for i in genre_list['genres']:
            if(i['id'] in genre):
                genres_list.append(i['name'])

        movie = tmdb.Movies(movie_id)
        response = movie.info()
        dict1 = {'title': id2['original_title'],'overview': id2['overview'],'rating': id2['vote_average'],'release date': id2['release_date']}
        print("Movie Name: ", dict1['title'], "Movie id: ", movie_id)

        global m_id
        m_id = id2['original_title']
        recom_df2 = get_recommendations().to_dict('list')
        recom_df2 = recom_df2['id']
        recom_df = pd.DataFrame()
        for ele in recom_df2:
            print("Getting data for Movie id:", ele)
            re_movie = tmdb.Movies(ele)
            ##Temproary
            temp = str(re_movie.info())
            for i in range(len(temp)):
                print(temp[i], end="")
            ##
            re_response = re_movie.info()
            temp = str(re_response)
            for i in range(len(temp)):
                print(temp[i])
            print(re_response)
            if re_response['backdrop_path']!=None:
                re_response['backdrop_path'] = "https://image.tmdb.org/t/p/original" + re_response['backdrop_path']
            else:
                re_response['backdrop_path'] = ""
            recom_df = recom_df.append(re_response, ignore_index=True)
        recom_df = recom_df.to_dict('list')
        print("Recommendation Movies: ", recom_df)
        get_recom = json.dumps(recom_df)
        # get_recom = new_df

        cast = movie.credits()['cast']
        cast_df = pd.DataFrame(cast)
        cast_df = cast_df[cast_df['known_for_department']=='Acting']
        cast_df = cast_df.iloc[:4]
        bday = []
        pob = []
        bio = []
        for i in range(cast_df.shape[0]):
            concat_2 = "http://api.themoviedb.org/3/person/"+str(cast_df.iloc[i]["id"])+"?api_key=036791174fdd67b8996bc53ad1a686f2&language=en-US"
            abc = requests.get(concat_2)
            actor_info = abc.json()
            bday.append(actor_info['birthday'])
            pob.append(actor_info['place_of_birth'])
            bio_t = actor_info['biography'].split(".")[:2]
            bio.append(".".join(bio_t))
        cast_df["Bday"] = bday
        cast_df["Place_of_birth"] = pob
        cast_df["Bio"] = bio
        print(pd.DataFrame(cast_df))

        cast_json = cast_df.to_dict("list")
        cast_json = json.dumps(cast_json)

        # bio of actor
        # print(cast_json)

        crew = movie.credits()['crew']
        crew_df = pd.DataFrame(crew)
        crew_df = crew_df[crew_df['job']=='Director']
        crew_df = crew_df.iloc[:1]
        bday = []
        pob = []
        bio = []
        for i in range(crew_df.shape[0]):
            concat_2 = "http://api.themoviedb.org/3/person/"+str(crew_df.iloc[i]["id"])+"?api_key=036791174fdd67b8996bc53ad1a686f2&language=en-US"
            abc = requests.get(concat_2)
            crew_info = abc.json()
            bday.append(crew_info['birthday'])
            pob.append(crew_info['place_of_birth'])
            bio_t = crew_info['biography'].split(".")[:2]
            bio.append(".".join(bio_t))
        crew_df["Bday"] = bday
        crew_df["Place_of_birth"] = pob
        crew_df["Bio"] = bio
        print()
        print(crew_df)
        
        crew_json = crew_df.to_dict("list")
        crew_json = json.dumps(crew_json)


        actors = []
        x=0
        for i in cast:
            if(i['known_for_department']=='Acting' and x<4):
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
            concat_2 = "http://api.themoviedb.org/3/person/"+str(actors[i][3])+"?api_key=036791174fdd67b8996bc53ad1a686f2&language=en-US"
            abc = requests.get(concat_2)
            actor_info = abc.json()
            actors[i].append(actor_info['birthday'])
            actors[i].append(actor_info['place_of_birth'])
            actors[i].append(actor_info['biography'])
        # print(actors[0])
        
        concat_3 = "http://api.themoviedb.org/3/person/"+str(director[2])+"?api_key=036791174fdd67b8996bc53ad1a686f2&language=en-US"
        abc = requests.get(concat_3)
        director_info = abc.json()
        director.append(director_info['birthday'])
        director.append(director_info['place_of_birth'])
        director.append(director_info['biography'])

        # #movie_info:

        movie_title = dict1['title']
        movie_overview = dict1['overview']
        movie_rating = dict1['rating']
        movie_release_date = dict1['release date']
        movie_genres = genres_list
        movie_image = "https://image.tmdb.org/t/p/original"+id2['backdrop_path']

        #Actors_info:
        # if cast_df.iloc[0]>0:
        actor1_name = actors[0][0]
        actor1_character = actors[0][1]
        actor1_image = actors[0][2]
        actor1_bdate = actors[0][4]
        actor1_birthplace = actors[0][5]
        actor1_biography = actors[0][6]
        
        actor2_name = actors[1][0]
        actor2_character = actors[1][1]
        actor2_image = actors[1][2]
        actor2_bdate = actors[1][4]
        actor2_birthplace = actors[1][5]
        actor2_biography = actors[1][6]

        actor3_name = actors[2][0]
        actor3_character = actors[2][1]
        actor3_image = actors[2][2]
        actor3_bdate = actors[2][4]
        actor3_birthplace = actors[2][5]
        actor3_biography = actors[2][6]

        actor4_name = actors[3][0]
        actor4_character = actors[3][1]
        actor4_image = actors[3][2]  
        actor4_bdate = actors[3][4]
        actor4_birthplace = actors[3][5]
        actor4_biography = actors[3][6]
    
        #director_info:
        director_name = director[0]
        director_character = "Director"
        director_image = director[1]
        director_bdate = director[3]
        director_birthplace = director[4]
        director_biography = director[5]
                    
        movie = [movie_title,movie_overview,movie_rating,movie_release_date,movie_genres,movie_image]
        director = [director_name,director_character,director_image,director_bdate,director_birthplace,director_biography]
        actor1 = [actor1_name,actor1_character,actor1_image,actor1_bdate,actor1_birthplace, actor1_biography]
        actor2 = [actor2_name,actor2_character,actor2_image,actor2_bdate,actor2_birthplace, actor2_biography]
        actor3 = [actor3_name,actor3_character,actor3_image,actor3_bdate,actor3_birthplace, actor3_biography]
        actor4 = [actor4_name,actor4_character,actor4_image,actor4_bdate,actor4_birthplace, actor4_biography]
        print("Actor 1 details: ", actor1)

        return render_template('results.html',movien=[movie,director,actor1,actor2,actor3,director,actor4],get_recom=get_recom, cast_json= cast_json, crew_json=crew_json)
    except Exception as e:
        # e='The movie that you have entered is not stored in our database'
        print(e)    
        return render_template('error_catch.html',e="Something went wrong! " + str(e))


@app.route('/cast1')
def cast1():
    return render_template('cast_info.html')

def get_recommendations():
    idx = indices[indices["title"] == m_id]["index"].to_list()[0]
    final_sim = np.array(final_cosine_sim[idx])
    sim_scores = list(enumerate(final_sim))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    print("Recommendation Movies Id: ", movie_indices)
    return new_df2[['id']].iloc[movie_indices]

    
if __name__=="__main__":
    app.run(debug=True)