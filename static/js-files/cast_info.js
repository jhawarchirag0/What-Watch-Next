function setData(id){
    actor_details = JSON.parse({{ cast_json | tojson }})
    console.log(typeof(actor_details));
    let m = JSON.stringify(actor_details);
    console.log(m);
    if (id==0){
        alert("m")}
    // localStorage.setItem("a",id);
    
    // console.log(m);
};


