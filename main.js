var repeater;
function getStatus(){
  let url = 'http://192.168.1.40:8080/status.json';


  fetch(url)
  .then(res => res.json())
  .then(out => {
    var server = out.server;
    var target1 = out.target["1"];
    var target2 = out.target["2"];

    if (server == 1) {
      document.getElementById('server-running').className = "active";
    }
    else if (server == 2) {
      document.getElementById('server-connected').className = "active";
      document.getElementById('server-running').className = "active";
    }
    else if (server == 3) {
      document.getElementById('server-connected').className = "waiting";
      document.getElementById('server-running').className = "active";
    }
    else {
      document.getElementById('server-connected').className = "not-active";
      document.getElementById('server-running').className = "not-active";
    }

    if (target1 == 1) {
      console.log('target1 on')
      document.getElementById('target-1-running').className = "active";
      document.getElementById('target-1-connected').className = "active";
    }
    else {
      console.log('target1 off')
      document.getElementById('target-1-running').className = "not-active";
      document.getElementById('target-1-connected').className = "not-active";
    }

    if (target2 == 1) {
      document.getElementById('target-2-running').className = "active";
      document.getElementById('target-2-connected').className = "active";
    }
    else {
      document.getElementById('target-2-running').className = "not-active";
      document.getElementById('target-2-connected').className = "not-active";
    }
    }

  )
  .catch(err => {throw err});
repeater = setTimeout(getStatus, 1000);
}
