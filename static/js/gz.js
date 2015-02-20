// useful function to see if an array contains an object
Array.prototype.contains = function(obj) {
	var i = this.length;
	while (i--) {
		if (this[i] == obj) {
			return true;
		}
	}
	return false;
};

// set up the margins and such
var W = parseInt(d3.select('#tree').style('width'))
var margin = {top: 1, right: 1, bottom: 1, left: 1},
    width = W - margin.left - margin.right,
	height = .5*W - margin.top - margin.bottom;

// Re-draw when window size is changed
var current_gal;
function resize_window() {
    val = parseInt(d3.select('#tree').style('width'))
    if (val!=W){
        W=val;
        width = W - margin.left - margin.right;
        height = .5*W - margin.top - margin.bottom;
        updateData(current_gal);
    }
};

// wait for re-size event to be over before re-drawing
var doit;
window.onresize = function() {
    clearTimeout(doit);
    doit = setTimeout(resize_window, 100);
};

// Hook up buttons
d3.select("#random_gal").on("click",function() {
    updateData('random');
});

d3.select("#galaxies").on("change", function() {
	updateData(this.value);
});

d3.select("#file_upload").on("change", function() {
    var file = d3.event.target.files[0];
    if (file) {
        var reader = new FileReader();
        reader.onloadend = function(evt) {
            var dataText = evt.target.result;
            upload_me(dataText);
        };
        reader.readAsText(file);
    };
});

// what version of galaxy zoo are we working with
// set to 2 by default
var zoo = "2";
var upload = false;
var image_offset;
set_zoo();
d3.selectAll("#zoo_buttons > label").on("click", function() {
    val=d3.select(this).select("input").property("value");
    if (val=="0") {
        d3.select("#search_button_cell").attr("style","display: none;");
        d3.select("#upload_dd_cell").attr("style","display: block;");
        upload = true;
        document.getElementById("file_upload").click();
        //upload_me("/static/data/test.csv");
    }
    else if (upload || zoo!=val) {
        d3.select("#upload_dd_cell").attr("style","display: none;");
        d3.select("#search_button_cell").attr("style","display: block;");
        upload = false;
        zoo = val;
        set_zoo();
    }
})

// what color theme to use
// default light
var color_theme="light"
d3.selectAll("#color_buttons > label").on("click", function() {
    val=d3.select(this).select("input").property("value");
    if (color_theme!=val) {
        color_theme = val;
        d3.select("#css").attr("href","/static/css/"+color_theme+"_style.css");
    }
})

// funciton to handle an uploaded file
function upload_me(dataText) {
    // parse data stream
    var data = [];
    d3.csv.parse(dataText, function(row) {
        data.push(row);
    });
    var max_size = data.length
    // populate the dropdown list
    ug=d3.select("#upload_galaxy").selectAll("option").data(data, function(d, i) { return  i+1+": "+d.value+" "+d.table; });
    ug.enter()
        .append("option")
        .attr("value", function(d, i) { return i; })
        .attr("search", function(d) { return d.value; })
        .attr("table", function(d) { return d.table; })
        .text(function(d, i) {
            idx=i+1;
            return "   "+idx+": "+d.value+" "+d.table;
        });
    ug.exit().remove();
    $('.selectpicker').selectpicker('refresh');
    // hook up 'previous' button
    d3.select("#dd_previous").on("click", function() {
        current=parseInt(d3.select("ul.dropdown-menu.selectpicker").select("li.selected").attr("data-original-index"))
        if (current>0) {
            dd_now=current-1;
            d3.select("#upload_galaxy").property("value", dd_now)
            dd_change(d3.select("#upload_galaxy").select('option[value="'+dd_now+'"]'));
        };
    });
    // hook up 'next' button
    d3.select("#dd_next").on("click", function() {
        current=parseInt(d3.select("ul.dropdown-menu.selectpicker").select("li.selected").attr("data-original-index"))
        if (current<max_size-1) {
            dd_now=current+1;
            d3.select("#upload_galaxy").property("value", dd_now)
            dd_change(d3.select("#upload_galaxy").select('option[value="'+dd_now+'"]'));
        };
    });
    // this controls changed due to clicking on the lsit
    d3.select("ul.dropdown-menu.selectpicker").selectAll('li').on("click", function() {
        current=parseInt(d3.select(this).attr("data-original-index"));
        if (current != dd_now) {
            dd_now=current;
            dd_change(d3.select("#upload_galaxy").select('option[value="'+current+'"]'));
        }
    });
    // function to update node tree based on selected option
    function dd_change(selected_option) {
        $('.selectpicker').selectpicker('render');
        val = selected_option.attr("table").substr(2)
        if (zoo != val) {
            zoo = val;
            set_zoo(selected_option.attr("search"));
        }
        else {
            updateData(selected_option.attr("search"));
        };
    };
    // load first option from the list
    var dd_now = 0
    dd_change(d3.select("#upload_galaxy").select('option[value="0"]'));
};

function set_zoo(search) {
    switch (zoo) {
    case "1":
        break;
    default:
        d3.select("#weight_raw").attr("class","btn btn-primary active");
	    d3.select("#weight_weighted_lab").attr("class","btn btn-primary disabled");
    }
    // read in file that maps the answer_id to the 
    // image offset in workflow.png and providing a useful
    // mouse over message
    d3.json("/static/config/zoo"+zoo+"_offset.json", function(d){
	    image_offset = d;
	    updateData(search||'random');
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
	$.getJSON($SCRIPT_ROOT + '/_get_path', {
        table: "gz"+zoo,
	    argv: gal_id
	}, function(d) {
	    json_callback(d.result)
	});

    // now that the basics are set up read in the json file
    var Total_value
    var current_gal
    var metadata
    function json_callback(answers) { 
	    // draw the galaxy image
	    $(".galaxy-image").attr("src", answers.image_url);
	    // Add text for RA and DEC
	    d3.select("#ra_dec")
	        .text("RA: " + parseFloat(answers.ra).toFixed(3) + ", DEC:" + parseFloat(answers.dec).toFixed(3))

        metadata = answers.metadata;
        current_gal = answers.gal_name;
        // make sure reset button returns same object
        function reset_data(){
	        updateData(current_gal);
        }
        d3.select("#reset_button").on("click", reset_data)
        
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
            // add the yes/no image if needed
	        oimage.append("image")
	            .attr("xlink:href", "/static/images/workflow.png")
	            .attr("x", -50)
	            .attr("y", function(d) { 
		            if (d.name) {
		                return image_offset[d.name][2] ? -image_offset[d.name][2]*100-50 : 100;
		            } else {
		                return 100;
		            }
	            })
	            .attr("clip-path", function(d) { return "url(#myClip" + d.name + ")"; })
	            .attr("width", 100)
	            .attr("height", 4900)
	            .attr("opacity", .35);
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
	        .attr("class", function(d) { return d.answer_id ? "gnode" : "gnode metadata-thumbnail"; })
	        .call(force.drag)
	        .on("click", function(d) { return d.answer_id ? click(d) : metadata_thumbnail(d); });

        // format the shadow-box for metadata
        function metadata_thumbnail(d) {
	        $('.modal-body').empty();
            var title = current_gal;
            var metastring = JSON.stringify(metadata,null,2);
            // remove quotes
            metastring = metastring.replace(/\"([^(\")"]+)\"/g,"$1");
            metastring = metastring.replace(/[,]+/g, "")
            $('.modal-title').html(title);
            $('.modal-body').html('<pre class="modal-data">'+metastring+'</pre>');
	        $('#myModal').modal({show:true});
        };       
        
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


