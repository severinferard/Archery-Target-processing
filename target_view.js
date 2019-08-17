function draw(target_num){
    var c=document.getElementById('myCanvas');
    var ctx=c.getContext('2d');
    ctx.canvas.width  = window.innerWidth;
    ctx.canvas.height = window.innerHeight*0.7;

    fetch('http://192.168.1.40:8080/data.json')
    .then(res => res.json())
    .then(out => {
      var impacts = out.target[target_num];
      console.log("impacts", impacts);

      var center_x = window.innerWidth/2
      var center_y = ctx.canvas.height/2
      var r_max = window.innerHeight/3

      ctx.beginPath();
      ctx.arc(center_x, center_y,  r_max, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.fillStyle = "blue";
      ctx.fill();

      ctx.beginPath();
      ctx.arc(center_x, center_y,  5 *r_max/6, 0, 2 * Math.PI);
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(center_x, center_y,  4 *r_max/6, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.fillStyle = "red";
      ctx.fill();

      ctx.beginPath();
      ctx.arc(center_x, center_y,  3 *r_max/6, 0, 2 * Math.PI);
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(center_x, center_y,  2 *r_max/6, 0, 2 * Math.PI);
      ctx.stroke();
      ctx.fillStyle = "yellow";
      ctx.fill();

      ctx.beginPath();
      ctx.arc(center_x, center_y,  1 *r_max/6, 0, 2 * Math.PI);
      ctx.stroke();

      var score_board = []
      for (i = 0; i < impacts.length; i++) {
        var ratio = impacts[i][0];
        var angle = impacts[i][1];
        var point = impacts[i][2];
        console.log(ratio, angle, point);

        x = r_max * ratio * Math.cos(angle) + center_x;
        y = r_max * ratio * Math.sin(angle) + center_y;
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fillStyle = "black";
        ctx.fill();

        score_board.push(point);
        console.log("score_board", score_board);
      }
      for (i = 0; i <6; i++) {
        var id = "score-" + (i+1).toString()
        console.log("id", id)
        var score = score_board[i]
        if (score !== undefined) {
          document.getElementById(id).innerHTML = score;
        }

      }

      if (score_board.length > 6) {
        var first_score_board = score_board.slice(0, 6)
      }
      else {
        var first_score_board = score_board
      }
      console.log("first", first_score_board)
      document.getElementById("score-total").innerHTML = first_score_board.reduce((a, b) => a + b, 0);






    })
    .catch(err => {throw err});
};


function calibrate() {

  fetch('http://192.168.1.40:8080/calibrate')
  .then(res => res.json())
  .then(out => {
  })
  .catch(err => {throw err});
};
