
function show_available_target(){
  let url = 'http://192.168.1.40:8080/status.json';


  fetch(url)
  .then(res => res.json())
  .then(out => {
    var server = out.server;
    var list_items = [];

    var node = document.createElement("LI");

    for (i = 1; i < 3; i++){
      console.log(out.target[i])
      if (out.target[i] > 0) {
        var node = document.createElement("LI");
        var textnode = document.createTextNode("Target " + i);
        node.appendChild(textnode);
        document.getElementById("target-list").appendChild(node);
      }
    }
    liAll = document.querySelectorAll('#target-list > li');
    liAll.forEach(function(elt) {
      txt = elt.textContent;
      link = document.createElement('a');
      atxt = document.createTextNode(txt);
      link.appendChild(atxt);
      link.setAttribute('href',txt.slice(0, 6).toLowerCase() + txt.slice(7, 9) +'.html');
      elt.appendChild(link);
      elt.firstChild.remove();
});
    }
  )
  .catch(err => {throw err});
}
