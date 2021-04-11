recommended_movies = JSON.parse({{ get_recom | tojson }})
// poster_path

var no_of_movies = recommended_movies["title"].length;

for(var i=0; i<no_of_movies; i++){
    var movie_div = document.createElement("div");
    movie_div.className = "movie";
    
    var movie_name = document.createElement("H3");
    movie_name.className = "movie-name";
    var movie_name_text = document.createTextNode(recommended_movies["title"][i]);
    movie_name.appendChild(movie_name_text);

    var movie_info = document.createElement("div");
    movie_info.className = "movie-info";

    var movie_image = document.createElement("img");
    movie_image.src = "https://image.tmdb.org/t/p/original"+recommended_movies['profile_path'];
    movie_image.alt = recommended_movies["title"][i];
    movie_info.appendChild(movie_image);

    var info_hover = document.createElement("div");
    info_hover.className = "info-hover";

    var data = document.createElement("div")
    var data_p = document.createElement("p");
    var data_p_text = document.createTextNode(recommended_movies["overview"][i]);
    data_p.appendChild(data_p_text);
    data.appendChild(data_p);
    info_hover.appendChild(data)
}