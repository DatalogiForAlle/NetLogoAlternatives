var FreeCanvas = function(canvas_width, canvas_height) {
    var canvas_tag = "<canvas width ='" + canvas_width + "' height='" + canvas_height + "' ";
    canvas_tag += "style='border:1px dotted'></canvas>"

    var canvas = $(canvas_tag)[0];
    $("#elements").append(canvas);
    var context = canvas.getContext("2d");

    this.render = function(data) {
	context.fillStyle = "#000000";
	context.fillRect(0,0,canvas_width,canvas_height);
	console.log(data[0].length)
	for(i=0;i<data[0].length;i++){
	    context.fillStyle = data[0][i].Color;
	    context.fillRect(data[0][i].x-5, data[0][i].y-5, 10, 10);
	}
    };

    this.reset = function() {
	context.clearRect(0,0,canvas_width,canvas_height);
    };
};
