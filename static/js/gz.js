// useful function to see if an array contains an object
Array.prototype.contains = function(obj) {
	var i = this.length;
	while (i--) {
		if (this[i] == obj) {
			return true;
		}
	}
	return false;
}

// set if the site should use the local json files of the full database
var local_files = false;

// set up the margins and such
var margin = {top: 1, right: 1, bottom: 1, left: 1},
	width = 1080 - margin.left - margin.right,
	height = 550 - margin.top - margin.bottom;

if (local_files){
    var header = d3.select("#header")
	.append("select")
	.attr("id","galaxies")
	.selectAll("option");
} else {
    var header = d3.select("#header")
	.append("input")
	.attr("id","galaxies")
	.attr("type","text");
    var header_button = d3.select("#header")
	.append("button")
	.attr("type","button")
	.text("Random")
	.attr("id","random_gal")
	.on("click", random_gal)
}

// what version of galaxy zoo are we working with
// set to 2 by default
var zoo = 2;
var json_list;
var image_offset;
set_zoo();
d3.select("#zoo_1").on("change", function() { 
    zoo = 1; 
    set_zoo();
})
d3.select("#zoo_2").on("change", function() { 
    zoo = 2; 
    set_zoo();
})
d3.select("#zoo_3").on("change", function() { 
    zoo = 3; 
    set_zoo();
})
d3.select("#zoo_4").on("change", function() { 
    zoo = 4; 
    set_zoo();
})

d3.select("#light").on("change", function() {
    d3.select("#css").attr("href","/static/css/style.css");
})
d3.select("#dark").on("change", function() {
    d3.select("#css").attr("href","/static/css/style_dark.css");
})


function set_zoo() {
    if (zoo == 1) {
	json_list = [];
	d3.select("#zoo_1").property("checked",1);
    } else if (zoo == 3) {
	json_list = ['10000189', '10000215', '10000235', '10000249', '10000278',
		     '10000325', '10000327', '10000331', '10000395', '10000416',
		     '10000449', '10000457', '10000493', '10000504', '10000514',
		     '10000519', '10002860', '10002902', '10002932', '10002937',
		     '10003019', '10003051', '10003061', '10003080', '10003149',
		     '10003153', '10003216', '10003361', '10003374', '10003386',
		     '10003398', '10003402', '10003408', '10003442', '10003476',
		     '10003488', '10003513', '10003528', '10003533', '10003534',
		     '10003544', '10003559', '10003585', '10003685', '10003695',
		     '10003703', '10003711', '10003719', '10003722', '10003727',
		     '10003733', '10003750', '10003751', '10003782', '10003785',
		     '10003801', '10003811', '10003846', '10003850', '10003853',
		     '10003879', '10003909', '10003975', '10003977', '10004038',
		     '10004047', '10004054', '10004065', '10004083', '10004086',
		     '10004092', '10004094', '10004097', '10004100', '10004109',
		     '10004113', '10004118', '10004144', '10004146', '10004153',
		     '10004160', '10004163', '10004168', '10010723', '10010732',
		     '10010804', '10010828', '10010842', '10010870', '10010872',
		     '10010879', '10010933', '10010938', '10010981', '10010992',
		     '10011013', '10011019', '10011026', '10011028', '10011054',
		     '10011090', '10011094', '10011123', '10011132', '10011144',
		     '10011152', '10011164', '10011183', '10011220', '10011247',
		     '10011295', '10011298', '10011325']
    
	//9614 removed from the list since it does not have an image url
	d3.select("#zoo_3").property("checked",1);
	d3.select("#weight_raw").property("checked",1);
	d3.select("#weight_weighted").property("disabled",1);
	d3.select("#weight_bias").property("disabled",1);
    } else if (zoo == 2) {
	json_list = ['588017703996096547', '587738569780428805', '587735695913320507', '587742775634624545', 
		     '587732769983889439', '588017725475782665', '588017702391578633', '588297864730181658', 
		     '588017704545812500', '588017566564155399', '588298663573454909', '587726014001512533', 
		     '587739098063044622', '587742615095935051', '588009371227258884', '587733410447491082', 
		     '587724648188543033', '587739720286863441', '588017704536244309', '587738947748626521', 
		     '588017704542404685', '587731869633871916', '587742191517433893', '588017111295197219', 
		     '587726015088623663', '587731512078893077', '587735696987193397', '587734893290848319', 
		     '588017110759243821', '588017569236910086', '587738067813924971', '587738569776955447', 
		     '587736586036117538', '588017565490085907', '588017724937076758', '587722982832013381', 
		     '588007004186476581', '588010360698961934', '587739505005297793', '587735348038467644', 
		     '588017948813492313', '587722982831423597', '587732482744975451', '587728879794782218', 
		     '587741828582604849', '587737827291693069', '588011218064769056', '588017948822863950', 
		     '587739131878703149', '588010878226399343', '588017565490741294', '588017704007172105', 
		     '588017949895819327', '587735349112799302', '587738946132770821', '587732576700399634', 
		     '588017728153059441', '587729776369991770', '587735349112340576', '587729159500988440', 
		     '587738410330292307', '588017703470628953', '587736584961982478', '588017725473947655', 
		     '588017729224900665', '588017112366841905', '587739158191145031', '587735348564787262', 
		     '587726031180660845', '588017719573086223', '588298664117076044', '587726032266526801', 
		     '587742062688796700', '587737808501932038', '587729159502299191', '587742864209084513', 
		     '587726014532354067', '588017704006975536', '588017726012129401', '588017702398328858', 
		     '587739099129380912', '587736941444530242', '587732582056525908', '588017605758550042', 
		     '588017978901528612', '587725474420097049', '587726014532550731', '588017565483859979', 
		     '588017703482032232', '587735344799350868', '587741722823819271', '588017569236910085', 
		     '587731870707089488', '588848899380084803', '587735696440623158'];
	d3.select("#zoo_2").property("checked",1);
	d3.select("#weight_raw").property("checked",1);
	d3.select("#weight_weighted").property("disabled",1);
	d3.select("#weight_bias").property("disabled",1);
    } else if (zoo == 4) {
	json_list = [];
	d3.select("#zoo_4").property("checked",1);
    }

    if (local_files){
	header = header.data(json_list, function(d) { return d; });

	header.enter()
	    .append("option")
	    .attr("value", function(d) { return d; })
	    .text(function(d) { return d; });
	
	header.exit().remove();
    }

    // read in file that maps the answer_id to the 
    // image offset in workflow.png and providing a useful
    // mouse over message
    d3.json("/static/config/zoo"+zoo+"_offset.json", function(d){ 
	image_offset = d;
	run_default();
    });
};

d3.select("#galaxies")
	.on("change", function() {
	    updateData(this.value);
	});
//load the first item of the list by default
function run_default() {
    if (local_files) {
	updateData(json_list[0]);
    } else {
	random_gal();
    }
};

// random galaxy
function random_gal() {
    $.getJSON($SCRIPT_ROOT + '/_get_random', {
        table: "gz"+zoo,
    }, function(d) {
	updateData(d.result.gal_name)
    });
};

// function that takes in a galaxy id and makes the node tree
function updateData(gal_id){
    // clear the page
    d3.selectAll("svg").remove();

    // hook up call-bakcs for the slider bars and reset button
    d3.select("#slider_charge").on("input", function() { update_charge(+this.value); })
    d3.select("#slider_strength").on("input", function() { update_strength(+this.value); })
    d3.select("#slider_friction").on("input", function() { update_friction(+this.value); })
    d3.select("#reset_button").on("click", reset_data)

    function update_charge(new_val){
	d3.select("#slider_charge_value").text(new_val);
	d3.select("#slider_charge").property("value", new_val);
	force.charge(function(n) {return -1 * new_val * 1700 * n.value});
	force.stop();
	force.start();
    }

    function update_strength(new_val){
	d3.select("#slider_strength_value").text(new_val);
	d3.select("#slider_strength").property("value", new_val);
	force.linkStrength(new_val);
	force.stop();
	force.start();
    }

    function update_friction(new_val){
	d3.select("#slider_friction_value").text(new_val);
	d3.select("#slider_friction").property("value", new_val);
	// use 1-new_val to make 0 frictionless instead of 1!
	force.friction(1-new_val);
	force.stop();
	force.start();
    }

    function reset_data(){
	updateData(gal_id);
    }

    // add the draw window
    var svg = d3.select("#body").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
      .append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // create the node tree object
    var force = d3.layout.force()
	.size([width, height]);

    // update the sliders to default values
    update_charge(2.5);
    update_strength(1);
    update_friction(0.35);

    if (local_files) {
	file_name="/static/data/"+gal_id+".json";
	d3.json(file_name, json_callback);
    } else {
	$.getJSON($SCRIPT_ROOT + '/_get_path', {
            table: "gz"+zoo,
	    argv: gal_id
	}, function(d) {
	    json_callback(d.result)
	});
    }

    // now that the basics are set up read in the json file
    var Total_value
    function json_callback(answers) { 
	// draw the galaxy image
	$(".galaxy-image").attr("src", answers.image_url);
	// Add text for RA and DEC
	d3.select("#ra_dec")
	    .text("RA: " + parseFloat(answers.ra).toFixed(3) + ", DEC:" + parseFloat(answers.dec).toFixed(3))
	// make sure dropdown list matches this id (useful for refresh)
	d3.select("#galaxies").property("value",answers.gal_name)
	root = answers;
	// make sure to minpulate data *before* the update loop
	// add a list of source and target Links to each node
	root.nodes.forEach(function(node) {
	    node.sourceLinks = [];
	    // _sourceLinks will be used to toggle links on and off
	    node._sourceLinks = [];
	    node.targetLinks = [];
	});
	root.links.forEach(function(link, i) {
	    // give each link a unique id
	    link.link_id = i;
	    link.is_max = false;
	    var source = link.source,
		target = link.target;
	    if (typeof source === "number") source = link.source = root.nodes[link.source];
	    if (typeof target === "number") target = link.target = root.nodes[link.target];
	    source.sourceLinks.push(link);
	    target.targetLinks.push(link);
	});
	// Get the number of votes for each node
	root.nodes.forEach(function(node) {
	    node.value = Math.max(
		d3.sum(node.sourceLinks, function(L) {return L.value}),
		d3.sum(node.targetLinks, function(L) {return L.value})
	    );
	});
	var max_nodes=[root.nodes[0]]
	function max_path(node) {
	    if (node.sourceLinks.length>0) {
		link_values=[]
		node.sourceLinks.forEach(function(d) { link_values.push(d.value); });
		idx_max = link_values.indexOf(Math.max.apply(Math, link_values));
		node.sourceLinks[idx_max].is_max = true;
		max_nodes.push(node.sourceLinks[idx_max].target)
		max_path(node.sourceLinks[idx_max].target);
	    }
	};
	// Find the links along the max vote path
	max_path(root.nodes[0]);
	
	// Normalize votes by total number
	Total_value=root.nodes[0].value
	root.nodes.forEach(function(node, i) {
	    node.value /= Total_value;
	    // set the radius such that 9 full sized nodes could fit
	    node.radius = (1-2*.07) * width * Math.sqrt(node.value) / 18;
	    node.node_id = i;
	});     
	// get the x position for each node
	computeNodeBreadths(root);
	// find how deep the tree goes and set the linkDistance to match 
	max_level = d3.max(root.nodes, function(d) {return d.fixed_level; });
	force.linkDistance(.8*width/(max_level + 1));
	
	// good starting points
	root.nodes.forEach(function(d , i) {
	    d.x = d.fixed_x;
	    // find if smooth or spiral is voted the most
	    // and put that group on top
	    if (root.nodes[1].value > root.nodes[2].value) { 
		j = 1;
	    } else {
		j = -1;
	    }
	    // set the y position such that higher vote values
	    // are on top, and (to a lesser extent) the groups
	    // stay together
	    d.y = (1 - d.value + j * d.group/10) * height/2;
	});
	// fix the first node so it does not move
	root.nodes[0].radius = .07 * width
	root.nodes[0].x = root.nodes[0].radius;
	root.nodes[0].y = height/2;
	root.nodes[0].fixed = true;
	// Add breadcrumb trail for max_path
	// Breadcrumb dimensions: width, height, spacing, width of tip/tail.
	var b = { h: 20, s: 3, t: 15 };
	b['w'] = (width-b.t-3*(max_nodes.length-1))/max_nodes.length;
	// Generate a string that describes the points of a breadcrumb polygon.
	var max_height = 1;
	function wrap(text, width) {
	    text.each(function() {
		var text = d3.select(this),
		    words = text.text().split(/\s+/).reverse(),
		    word,
		    line = [],
		    lineNumber = 0,
		    lineHeight = 1.1, // ems
		    y = text.attr("y"),
		    x = text.attr("x"),
		    dy = parseFloat(text.attr("dy")),
		    tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");
		while (word = words.pop()) {
		    line.push(word);
		    tspan.text(line.join(" "));
		    if (tspan.node().getComputedTextLength() > width) {
			line.pop();
			tspan.text(line.join(" "));
			line = [word];
			tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
			if (lineNumber+1 > max_height) {
			    max_height = lineNumber+1;
			}
		    }
		}
	    });
	}
	function breadcrumbPoints(d, i) {
	    var points = [];
	    points.push("0,0");
	    points.push(b.w + ",0");
	    points.push(b.w + b.t + "," + (b.h / 2));
	    points.push(b.w + "," + b.h);
	    points.push("0," + b.h);
	    if (i > 0) { // Leftmost breadcrumb; don't include 6th vertex.
		points.push(b.t + "," + (b.h / 2));
	    }
	    return points.join(" ");
	}
	var trail = d3.select("#sequence").append("svg:svg")
	    .attr("width", width)
	    .attr("height", b.h)
	    .attr("id", "trail");
	var g_bc = d3.select("#trail")
	    .selectAll("g")
	    .data(max_nodes, function(d) { return d.node_id; });
	var g_bc_entering = g_bc.enter().append("svg:g");
	g_bc_entering.append("svg:text")
	    .attr("class", "breadcrumb_text")
	    .attr("x", (b.w + b.t) / 2)
	    .attr("y", 0 )
	    .attr("dy", "1em")
	    .attr("text-anchor", "middle")
	    .text(function(d) { return image_offset[d.answer_id][0] + ": " + Math.round(d.value*Total_value); });
	g_bc.selectAll("text")
	    .call(wrap, b.w-2*b.t);
	b['h'] = 20 * max_height;
	g_bc_entering.insert("svg:polygon","text")
	    .attr("class", "breadcrumb")
	    .attr("points", breadcrumbPoints);
	trail.attr("height",b.h);
	g_bc.attr("transform", function(d, i) {
	    return "translate(" + i * (b.w + b.s) + ", 0)";
	});
	g_bc.exit().remove();
	// run the call-back function to update positions
	update(root.nodes, root.links);
    };
    
    // make the links long nice by using diagonal
    // swap x and y so the curve goes the propper way
    var diagonal = d3.svg.diagonal()
	.source(function(d) { return {"x":d.source.y, "y":d.source.x}; })
	.target(function(d) { return {"x":d.target.y, "y":d.target.x}; })
	.projection(function(d) {return [d.y, d.x]; });

    // select the link and gnode objects
    var link = svg.selectAll(".link"),
	gnode = svg.selectAll(".gnode");

    var first_draw = true;

    // create the update function to draw the tree
    function update(nodes_in, links_in) {
	// Set data as node ids
	var n_odd_nodes = root.odd_list.length
	
	if (first_draw & n_odd_nodes > 0) {
	    // place for the "odd" answers to go
	    first_draw = false;
	    var odd_answers1 = d3.select("#odd").append("svg")
		.attr("width",width + margin.left + margin.right)
		.attr("height",(width-2*.07)/9 + margin.top + margin.bottom)

	    var odd_answers = odd_answers1.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	    var onode = odd_answers.selectAll(".onode");

	    root.odd_list.forEach(function(d) {
		value = d.value / Total_value;
		d.radius = width * (1-2*.07) * Math.sqrt(value) / 18
	    });
	    
	    onode = onode.data(root.odd_list, function(d) { return d.name });
	    // Exit old nodes
	    onode.exit().remove();
	    
	    var oenter = onode.enter().append("g")
		.attr("class","onode")
		
	    var oimage = oenter.append("g")
		.attr("transform", function(d) { return "scale(" + d.radius/50 + ")" });

	    odd_answers1.attr("height",2*Math.ceil(root.odd_list[0].radius) + margin.top + margin.bottom);
	    oenter.attr("transform", function(d,i) {
		return 'translate(' + [width*(i+.5)/n_odd_nodes, Math.ceil(root.odd_list[0].radius)] + ')'; 
		});
	    oimage.append("defs")
		.append("clipPath")
		.attr("id", function(d) { return "myClip" + d.name; })
		.append("circle")
		.attr("cx", 0)
		.attr("cy", 0)
		.attr("r", 50);
	    // add a black circle in the background
	    oimage.append("circle")
		.attr("color", "black")
		.attr("cx", 0)
		.attr("cy", 0)
		.attr("r", 50);
	    oimage.append("image")
		.attr("xlink:href", "/static/images/workflow.png")
		.attr("x", -50)
		.attr("y", function(d) { return -image_offset[d.name][1]*100-50; })
		.attr("clip-path", function(d) { return "url(#myClip" + d.name + ")"; })
		.attr("width", 100)
		.attr("height", 4900);
	    oenter.append("title")
		.text(function(d) { return image_offset[d.name][0] + ": " + d.value; });
	}
	// add the nodes and links to the tree
	force
	    .nodes(nodes_in)
	    .links(links_in)
	    .on("tick", tick);

	// set the data for the links (with unique ids)
	link = link.data(links_in, function(d) { return d.link_id; });
	
	// add a path object to each link
	link.enter().insert("path", ".gnode")
            .attr("class", function(d) { return d.is_max ? "link_max" : "link"; })
	    .attr("d", diagonal)
            .style("stroke-width", function(d) { return .5 * width * Math.sqrt(d.value/Total_value) / 18; });

	link.append("title")
	    .text(function(d) { return d.value; })
    
	// Exit any old links
	link.exit().remove();

	// set the data for the nodes (with unique ids)
	gnode = gnode.data(nodes_in, function(d) { return d.node_id; });

	// Exit any old nodes
	gnode.exit().remove();
      
	// add a group to the node to translate it
	var genter = gnode.enter().append("g")
	    .attr("class","gnode")
	    .call(force.drag)
	    .on("click", click);

	// add a group to the node to scale it
	// with this scaling the image (with r=50px) will have the propper radius
	var gimage = genter.append("g")
	    .attr("transform", function(d) { return d.answer_id ? "scale(" + d.radius/50 + ")" : "scale(" + d.radius/100 + ")"; })

	// add a clipPath for a circle to corp the node image
	gimage.append("defs")
	    .append("clipPath")
	    .attr("id", function(d) { return "myClip" + d.node_id; })
	    .append("circle")
	    .attr("cx", 0)
	    .attr("cy", 0)
	    .attr("r", function(d) { return d.answer_id ? 45 : 100; });

	// add a black circle in the background
	gimage.append("circle")
	    .attr("color", "black")
	    .attr("cx", 0)
	    .attr("cy", 0)
	    .attr("r", function(d) { return d.answer_id ? 45 : 100; });

	// add the inital image to the node
	gimage.append("image")
	    .attr("xlink:href", function(d) { return d.answer_id ? "/static/images/workflow.png" : root.image_url})
	    .attr("x", function(d) { return d.answer_id ? -50: -100; })
	    .attr("y", function(d) { return d.answer_id ? -image_offset[d.answer_id][1]*100-50 : -100; })
	    .attr("clip-path", function(d) { return "url(#myClip" + d.node_id + ")"; })
	    .attr("width", function(d) { return d.answer_id ? 100: 200; })
	    .attr("height", function(d) { return d.answer_id ? 4900: 200; });
	
	// add the yes/no image if needed
	gimage.append("image")
	    .attr("xlink:href", "/static/images/workflow.png")
	    .attr("x", -50)
	    .attr("y", function(d) { 
		if (d.answer_id) {
		    return image_offset[d.answer_id][2] ? -image_offset[d.answer_id][2]*100-50 : 100;
		} else {
		    return 100;
		}
	    })
	    .attr("clip-path", function(d) { return "url(#myClip" + d.node_id + ")"; })
	    .attr("width", 100)
	    .attr("height", 4900)
	    .attr("opacity", .35);

	// add the mouse over text
	var mouse_over = genter.append("title")
	    .text(function(d) { return image_offset[d.answer_id][0] + ": " + Math.round(d.value*Total_value); })
    
	// start the nodes moving
	force.start();
	//for (var i = 500; i > 0; --i) force.tick();
	//force.stop();
   
	d3.select("#weight_raw").on("change", function() { set_weight(0); })
	d3.select("#weight_weighted").on("change", function() { set_weight(1); })
	d3.select("#weight_bias").on("change", function() { set_weight(2); })

	// call-back to swap weighting
	function set_weight(idx) {
	    root.nodes.forEach(function(n) {
		n.radius = n._radius[idx];
		n.value = n._values[idx];
		gimage.attr("transform", function(d) { return d.answer_id ? "scale(" + d.radius/50 + ")" : "scale(" + d.radius/100 + ")"; });
		link.style("stroke-width", function(d) { return .5 * Math.min(d.target.radius, d.source.radius); });
		mouse_over.text(function(d) { return image_offset[d.answer_id][0] + ": " + d.votes[idx]; })
	    });
	    update_charge(d3.select("#slider_charge").property("value"));
	}

	// call-back to set how the nodes will move
	function tick(e) {
	    // make sure the force gets smaller as the simulation runs
	    var ky = 10 * e.alpha;
	   
	    root.nodes.forEach(function(d, i) {
		// fix the x value at the depth of the node
		// and add in the radius of the first node
		i!=0 ? d.x = d.fixed_x + root.nodes[0].radius+50 : d.x = d.fixed_x + root.nodes[0].radius;
		// move low prob nodes down
		// and keep the groups together (to a lesser extent)
		if (root.nodes[1].value > root.nodes[2].value) { 
		    j = 1;
		} else {
		    j = -1;
		}
		// the amount to move the node
		delta_y = (3 * d.value - j * .3 * d.group + .3) * ky;
		// store the old position in case something goes wrong
		// the collision detection can casue NaNs and I am not sure why
		d.y_old = d.y;
		// check to make sure the node is not outside the plot area
		// if it is change the direction of the push
		if ((d.y-d.radius<0 && delta_y>0) || (d.y+d.radius>height && delta_y<0)) {
		    delta_y *= -1
		}
		d.y -= delta_y;
	    });

	    // Also do collision detection after a few itterations
	    if (e.alpha<0.05) {
		var q=d3.geom.quadtree(root.nodes),
		    i=0,
		    n=root.nodes.length;
		while (++i < n) q.visit(collide(root.nodes[i]));
	    }
	    
	    // if the new position is NaN use the previous position
	    // this prevents links for disappearing
	    root.nodes.forEach( function(d) {
		if (isNaN(d.y)) { d.y = d.y_old; }
	    });
	    
	    // Translate the node group to the new position
	    gnode.attr("transform", function(d) {
		return 'translate(' + [d.x, d.y] + ')'; 
	    });    
	    link.attr("d",diagonal);
	};
	// the collision detection code
	// found this online and I am not sure how it works
	function collide(node) {
	    var r = node.radius,
		nx1 = node.x - r,
		nx2 = node.x + r,
		ny1 = node.y - r,
		ny2 = node.y + r;
	    return function(quad, x1, y1, x2, y2) {
		if (quad.point && (quad.point !== node)) {
		    var x = node.x - quad.point.x,
			y = node.y - quad.point.y,
			l = Math.sqrt(x * x + y * y),
			r = 0.9*(node.radius + quad.point.radius);
		    if (l < r) {
			l = (l - r) / l * .5;
			//node.x -= x *= l;
			node.y -= y *= l;
			//quad.point.x += x;
			quad.point.y += y;
		    }
		}
		return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
	    };
	}
    };
    // Find the x positions for each node
    function computeNodeBreadths(root) {
	var remainingNodes = root.nodes,
	    nextNodes,
	    x = 0;
	
	while (remainingNodes.length) {
	    nextNodes = [];
	    remainingNodes.forEach(function(node) {
		node.fixed_x = x;
		node.sourceLinks.forEach(function(link) {
		    if (nextNodes.indexOf(link.target) < 0) {
			nextNodes.push(link.target);
		    }
		});
	    });
	    remainingNodes = nextNodes;
	    ++x;
	}	  
	moveSinksRight(x);
	// don't scale to the full width or the nodes go off the page
	scaleNodeBreadths(.87 * (width-50) / (x - 1));
    };
    
    function moveSinksRight(x) {
	root.nodes.forEach(function(node) {
	    if (!node.sourceLinks.length) {
		node.fixed_x = x - 1;
	    }
	});
    };
    
    function scaleNodeBreadths(kx) {
	root.nodes.forEach(function(node) {
	    node.fixed_level = node.fixed_x;
	    node.fixed_x *= kx;
	});
    };

    // call-back to collapse/expand nodes
    function click(d) {
	if (d3.event.defaultPrevented) return;
	if (d.sourceLinks.length>0) {
	    d._sourceLinks=d.sourceLinks;
	    d.sourceLinks=[];
	} else {
	    d.sourceLinks=d._sourceLinks
	    d._sourceLinks=[];
	}
	// find what nodes and links are still around
	var current_nodes = [];
	var current_links = [];
	function recurse(node) {
	    if (!current_nodes.contains(node)) { current_nodes.push(node) };
	    if (node.sourceLinks.length>0) {
		node.sourceLinks.forEach(function(link) {
		    if (!current_links.contains(link)) { current_links.push(link) };
		    recurse(link.target);
		});
	    }
	};
	recurse(root.nodes[0]);
	// update the nodes
	update(current_nodes, current_links);
    };
};


