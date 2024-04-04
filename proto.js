// proto

function draw_dir(data) {
    d = draw_slices(d3.select("g.main"), data)
    proto._slice_rects = d.rectEnter
    proto._slice_texts = d.textEnter
    this._main_translate_container = d.container
    d.rectEnter
    	.on("mouseover", function(d, i) {
	    d3.select(this).attr("fill", proto.highlight_color)
	})
        .on("mouseout", function(d, i) {
	    d3.selectAll(".slice-rect").attr("fill", proto.background_color)
	})
    d.textEnter
    	.on("mouseover", function(d, i) {
	    d3.select(this.parentNode).select("rect").attr("fill", proto.highlight_color)
    	})
    return d
}

function draw_scratch(data) {
    clear_main()
    render_content(data)
    render_frame_tick()
}

function draw_machines(data) {
    clear_main()
    render_content(data, d3.treemapDice)
    render_frame_tick()
}

function draw_lab(data) {
    draw_machines(data)
}

function draw_network(data) {
    draw_machines(data)
}

function draw_samples(data) {
    draw_machines(data)
}

function draw_progress(data) {
    draw_machines(data)
}

function draw_codeview(data) {
    draw_machines(data)
}

function draw_veingraph(data) {
    dim = wxh()
    // d3.tree().size([dim.height, dim.width])
    // root = d3.hierarchy(treeData, function(d) { return d.children; });
    const root = d3.hierarchy(data)
    const links = root.links()
    const nodes = root.descendants()
    
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(0).strength(1))
        .force("charge", d3.forceManyBody().strength(-50))
        .force("x", d3.forceX())
        .force("y", d3.forceY())
    
    const svg = d3.create("svg")
	    .attr("viewBox", [-dim.width / 2, -dim.height / 2, dim.width, dim.height]);
    
    const link = svg.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .selectAll("line")
        .data(links)
        .join("line")

    const drag = simulation => {
	
	function dragstarted(event, d) {
	    if (!event.active) simulation.alphaTarget(0.3).restart();
	    d.fx = d.x;
	    d.fy = d.y;
	}
	
	function dragged(event, d) {
	    d.fx = event.x;
	    d.fy = event.y;
	}
	
	function dragended(event, d) {
	    if (!event.active) simulation.alphaTarget(0);
	    d.fx = null;
	    d.fy = null;
	}
	
	return d3.drag()
	    .on("start", dragstarted)
	    .on("drag", dragged)
	    .on("end", dragended);
    }    
    const node = svg.append("g")
        .attr("fill", "#fff")
        .attr("stroke", "#000")
        .attr("stroke-width", 1.5)
        .selectAll("circle")
        .data(nodes)
        .join("circle")
        .attr("fill", d => d.children ? null : "#000")
        .attr("stroke", d => d.children ? null : "#fff")
        .attr("r", 3.5)
        .call(drag(simulation))
    
    node.append("title")
	.text(d => d.data.name)
    
    simulation.on("tick", () => {
	link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y)
	
	node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
    })
}
//
//function draw_morphlab(data) {
//    draw_dir(data)
//}
//
//function scratch() {
//    update_menu("scratch")
//    clear_main()
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            draw_scratch(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", "scratch", true)
//    xh.send()
//}
//
//function machines() {
//    update_menu("machines")
//    clear_main()
//    xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            draw_machines(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", "machines", true)
//    xh.send()
//}
//
//function stacklab() {}
//
//function lab() {
//    update_menu("lab")
//    clear_main()
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            draw_lab(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", "lab", true)
//    xh.send()
//}
//
//
//function network() {
//    update_menu("network")
//    clear_main()
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            draw_network(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", "network", true)
//    xh.send()
//}
//
//function samples() {
//    update_menu("samples")
//    clear_main()
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            draw_samples(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", "samples", true)
//    xh.send()
//}
//
//function progress() {
//    update_menu("progress")
//    clear_main()
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            draw_progress(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", "progress", true)
//    xh.send()
//}
//
//function codeview() {
//    update_menu("codeview")
//    clear_main()
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            draw_codeview(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", "codeview", true)
//    xh.send()
//}
//
//function veingraph() {
//    update_menu("veingraph")
//    clear_main()
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            draw_veingraph(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", "veingraph", true)
//    xh.send()
//}
//
//function morphlab() {
//    update_menu("morphlab")
//    clear_main()
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            draw_morphlab(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", "morphlab", true)
//    xh.send()
//}
//
//function transition_menu(menu, menu_fn) {
//    init_menu(menu)
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            menu_fn.apply(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", menu, true)
//    xh.send()
//    return false
//}
//
//function transition(menu) {
//    update_menu(menu)
//    clear_main()
//    var xh = new XMLHttpRequest()
//    xh.onreadystatechange = function() {
//        if(this.readyState == 4 && this.status == 200) {
//            window["draw_"+menu].apply(JSON.parse(this.responseText))
//            render_frame_tick()
//        }
//    }
//    xh.open("GET", menu, true)
//    xh.send()
//    init_menu(menu)
//}

function clear_main() {
    d3.selectAll("g.main > *").remove()
}
