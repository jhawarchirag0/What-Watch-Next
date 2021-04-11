var slideIndex = 0;
var x;

function init(){
  var i;
  for(i=0; i<x.length; i++){
    if(i!=slideIndex){
      x[i].style.display = "none";
    }
    else{
      x[i].style.display = "block"
    }
  }
}

window.onload = function() {
  x = document.getElementsByClassName("movie");
  console.log(x);
  init();
}

function nextImage(){
  slideIndex++;
  if( slideIndex>=x.length ){
    slideIndex = 0
  }
  var i;
  for(i=0; i<x.length; i++){
    if(i!=slideIndex){
      x[i].style.display = "none";
    }
    else{
      x[i].style.display = "block"
    }
  }
}

function prevImage(){
  slideIndex--;
  if( slideIndex<0 ){
    slideIndex = x.length - 1;
  }
  var i;
  for(i=0; i<x.length; i++){
    if(i!=slideIndex){
      x[i].style.display = "none";
    }
    else{
      x[i].style.display = "block"
    }
  }
}