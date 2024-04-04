// core

var proto = { x: 25, y: 50, cx:0, cy: 0,
	      console_height: 50,
	      console_height_up: 260,
	      console_height_down: 50,
	      console_party: true,
	      input_height: 20,
	      menu_width: 90,
	      menu_height: 30,
	      menu_padding: 4,
	      menu_value: 2,
	      button_height: 20,
	      button_width: 100,
	      button_top_padding: 13,
	      button_left_padding: 50,
	      slice_padding: 2,
	      slice_left_padding: 5,
	      slice_height: 20,
	      slice_height_min:17,
	      text_left_padding: 5,
	      text_top_padding: 15,
	      text_height: 10,
	      label_top_padding: 15,
	      label_left_padding: 5,
	      foreground_color: "black",
	      background_color: "white",
	      highlight_color: "rgb(122,0,0)",
	      background_grid_base: 4,
	      duration: 5}

var margin = { top: 0, right: 12,
	           left: 0, bottom: 54}

network_drop_down_list = ["view", "add", "ping"]
view_drop_down_list = ["code", "storm", "rain"]
sample_drop_down_list = ["view", "add"]
jobs_drop_down_list = ["view", "add", "halt"]

var menu_data = {name: "menu", children: [
                      {name:"targets", children: [],
                       click: (d) => targets_button_handler(d.data.name, menu_button)},
                      {name:"view", children: [],
					   click: (d) => view_button_handler(d.data.name, menu_button)},
					  {name:"network", children: [],
					   click: (d) => network_button_handler(d.data.name, menu_button)},
					  {name:"sample", children: [],
					   click: (d) => sample_button_handler(d.data.name, menu_button)},
					  {name:"jobs", children: [],
					   click: (d) => jobs_button_handler(d.data.name, menu_button)}
					  ]}

menu_dict = {'targets': targets_button_handler,
             'network': network_button_handler,
             'view': view_button_handler,
             'sample': sample_button_handler,
             'jobs': jobs_button_handler}

// general items
project_menu_list = ["view", "stats", "+sample", "testcase", "coverage"]
targets_menu_list = ["upload"]
sample_menu_list = ["view", "debug", "libdislocator", "rabid werewolf", "+dict"]
machine_menu_list = ["power", "ssh", "install", "sleep", "version", "start", "stop"]

project_config_menu_list = ["player", "fuzzer", "templates", "dictionary", "seed corpus", "engine"]
targets_config_menu_list = []
sample_config_menu_list = []
machine_config_menu_list = []

function wxh() {
    d = document,
    e = d.documentElement,
    g = d.getElementsByTagName('body')[0],
    x = window.innerWidth || e.clientWidth || g.clientWidth
    y = window.innerHeight|| e.clientHeight|| g.clientHeight
    x = window.innerWidth
    y = window.innerHeight
    width = x-margin.right
    height = y-margin.top-margin.bottom
    return {width: width, height: height}
}

function init_menu(menu) {
    this._menu_dicemap = d3.treemap()
        .tile(d3.treemapDice)
        .padding(proto.menu_padding)
    this._menu_current = menu_data
    d3.select("g.menu").attr("height", proto.menu_height)
    update_menu(menu)
}

function update_menu(menu) {
    this._menu_name = menu
    d3.selectAll("g.menu > *").remove()
    this._menu_hierarchy = d3.hierarchy(this._menu_current)
    	.sum((d) => d.value || proto.menu_value)
    this._menu_dicemap(this._menu_hierarchy)
    this._menu_items = this._menu_hierarchy.descendants().splice(1)
}

function render_menu_tick() {
    dim = wxh()
    if (this._menu_items == undefined) {
	    update_menu(this._menu_current)
    }
    this._menu_dicemap.size([dim.width*1.2,proto.menu_height])(this._menu_hierarchy)
    items = d3.select("g.menu")
        .selectAll(".menu-items")
        .data(this._menu_items)
    items.exit().remove()
    
    container_enter = items.enter()
        .append("a")
            .each(function(d, i) {
            d3.select(this).classed("menu-items menu-"+d.data.name, true)
        })
        .style("cursor", "pointer")
        .style("user-select", "none")
        .on("contextmenu", function(d, i) {
            console.log("menu right click")
            d3.event.preventDefault()
        })
    container_enter
        .append("rect")
        .style("stroke", "rgba(0,0,0,.6)")
    	.style("fill", "white")
    	.classed("menu-rect", true)
    container_enter
        .append("text")
    	.text(function(d) { return d.data.name })
    	.attr("font-size", "12px")
    	.attr("fill", "red")
        .classed("menu-text", true)
        .style("text-overflow", "ellipsis")
    	.style("overflow", "hidden")
    	.style("white-space", "nowrap")
    container_update = items.merge(container_enter)
        .on("click", (d) => {
            console.log('menu button clicked '+d.data.name)
            if (d.data.click !== undefined) {
                eval(d.data.click)
            }
            d3.event.stopPropagation()
            return false;
        })
    d3.selectAll(".menu-rect")
        .attr('x', function (d) { return d.x0; })
    	.attr('y', function (d) { return d.y0; })
    	.attr('width', function (d) { return d.data.width || d.x1 - d.x0; })
    	.attr('height', function (d) { return d.y1 - d.y0; })
    d3.selectAll(".menu-text")
        .attr("x", function(d){ return d.x0+proto.text_left_padding-(8*(d.data.name.length/2))+((d.x1-d.x0)/2)})
    	.attr("y", function(d){ return d.y0+proto.text_top_padding})
    	// .attr('textLength', function (d) { return (d.x1-d.x0)/1.7 })
    
    rects_update = items.merge(container_enter)
    	.attr('x', function (d) { return d.x0; })
    	.attr('y', function (d) { return d.y0; })
    	.attr('width', function (d) { return d.data.width || d.x1 - d.x0; })
    	.attr('height', function (d) { return d.y1 - d.y0; })
    texts_update = items.merge(container_enter)
        .attr("x", function(d){ return d.x0+proto.text_left_padding-(8*(d.data.name.length/2))+((d.x1-d.x0)/2)})
    	.attr("y", function(d){ return d.y0+proto.text_top_padding})
    return container_enter
}

function draw_lines(cnt, data) {
    logs = cnt.selectAll("text")
	.data(data)
    logsEnter = logs.enter()
	.append("text")
	.text((d) => d.name)
    	.each(function(d, i) { d.id=i++ })
    	.attr("font-size", "12px")
	.classed("log-text", "true")
    logsUpdate = logsEnter.merge(logs)
    	.attr("x", proto.label_left_padding)
    	.attr("y", function(d){ return proto.cy+d.id*proto.slice_height+proto.label_top_padding })
    logsExit = logs.exit().remove()
    return logsEnter
}

function draw_slices(cnt, data) {
    slices = cnt.selectAll("g")
	.data(data)
    sliceContainer = slices.enter()
    	.append("g")
	.classed("slice-g", true)
    	.each(function(d, i) { d.id=i++ })
    rectEnter = sliceContainer.append("rect")
    	.attr("fill", "white")
	.attr("stroke", "rgba(1,1,1,.7)")
	.attr("width", function(d) {return d.name.length*10})
	.attr("height", proto.slice_height-2)
	.classed("slice-rect", true)
    	.on("mouseover", function(d, i) {
	    d3.select(this).attr("stroke", proto.highlight_color)
	})
	.on("mouseout", function(d) {
	    d3.selectAll(".slice-rect").attr("stroke", "white")
	})
    textEnter = sliceContainer.append("text")
    	.attr("font-size", "12px")
	.attr("width", function(d) {return d.name.length*10})
	.attr("height", proto.slice_height)
	.text((d) => d.name)
    	.classed("slice-text", true)
    rectUpdate = rectEnter.merge(slices)
    textUpdate = textEnter.merge(slices)
    	.attr("x", proto.text_left_padding)
    	.attr("y", proto.label_top_padding-2)
    exit = slices.exit().remove()
    return {container: sliceContainer, rectEnter: rectEnter, textEnter: textEnter}
}

function collapse_children(d) {
    if(d.children) {
        d.__children = d.children
        d._children = []
        d.__children.forEach(collapse_children)
        d.children = null
    }
}

function render_content(data, layout) {
    dim = wxh()
    register_console_messages(data.console)
    this._data = data
    this._root_dicemap = d3.treemap()
        .size([dim.width-proto.button_width, dim.height-4*proto.menu_height])
	.padding(2)
    
    if (layout != undefined) { // if specified apply layout
	    this._root_dicemap.tile(layout)
    }

    this._root_hierarchy = d3.hierarchy(this._data, function(d) {return d.children})
        .sum((d) => d.value || proto.menu_value)
	    .sort(function(a, b) {return a.data.name.length - b.data.name.length})
    this._root_hierarchy.children.forEach(collapse_children)
    this._root_dicemap(this._root_hierarchy)
    this._root_items = this._root_hierarchy.descendants().splice(1)
    render_content_tick()
}

function render_profile(data, layout) {
    register_console_messages(data.console)
    dim = wxh()
    this._data = data
    this._root_dicemap = d3.treemap()
        .size([dim.width-proto.button_width, dim.height-4*proto.menu_height])
	    .padding(2)
    if (layout != undefined) {
	this._root_dicemap.tile(layout)
    }

    this._root_hierarchy = d3.hierarchy(this._data, function(d) {return d.children})
    	.sum((d) => d.value || proto.menu_value)
	    .sort(function(a, b) {return a.data.name.length - b.data.name.length})
    this._root_hierarchy.children.forEach(collapse_children)
    this._root_dicemap(this._root_hierarchy)
    this._root_items = this._root_hierarchy.descendants().splice(1)
    render_content_tick()    
}

function render_content_tick() {
    i=0
    node = d3.selectAll("g.main")
	.selectAll("g.root-item")
	.data(this._root_items)
    nodeEnter = node.enter()
	    .append("g")
	    .attr("class", "root-item")
    	.each(function(d) {if (d.id == undefined) {d.id = ++i}})
	    .on("click", click)
    this._root_translate_container = nodeEnter
    nodeEnter.append("rect")
	    .attr("class", "node")
	    .style("fill", "white")
	    .attr("stroke", "black")
	    .attr("cursor", "pointer")
    nodeEnter.append("text")
	    .attr("dy", ".15em")
	    .attr("font-size", "12px")
	    .text((d) => d.data.name)
	    .attr("x", 5)
	    .attr("y", (d) => proto.button_top_padding)
	    .attr("cursor", "pointer")
    	.attr("fill", "red")
    nodeUpdate = nodeEnter.merge(node)
        .attr("transform", (d) => "translate("+(d.x0+proto.x)+","+(d.y0+proto.y)+")")
    	.transition()
	    .duration(proto.duration)

    nodeUpdate.select("rect.text")
        .attr("x", (d) => 5)
        .attr("y", (d) => proto.button_top_padding)
    nodeUpdate.select("rect.node")
        .attr("height", (d) => proto.button_height)
        .attr("width", (d) => proto.button_width)
    nodeExit = node.exit().transition()
        .duration(proto.duration)
        .attr("transform", "translate(0,0)")
        .remove()
    nodeExit.select("rect")
        .attr("height", 0)
        .attr("width", 0)
    	.attr("x", 0)
    	.attr("y", 0)
    nodeExit.select("text")
        .style("fill-opacity", 1e-6)
        .attr("stroke", "rgba(0,0,0,0)")
    	.attr("x", 0)
    	.attr("y", 0)
}

function click(d) {
    if (d._children != undefined && d._children.length != 0) {
    	d._children = []
    } else {
    	d._children = d.__children
    }
    pop_menu(d)
    d3.event.stopPropagation()
    render_content_tick()
}

function xhr_button(button, variable) {
    var xh = new XMLHttpRequest()
    console.log(button)
    xh.onreadystatechange = function() {
    	if(this.readyState == 4 && this.status == 200) {
    	    render_frame_tick()
    	    render_content(JSON.parse(this.responseText))
    	}
    }
    xh.open("GET", button+'/'+variable, true)
    xh.setRequestHeader("Content-Type", "application/x-www-form-urlencoded")
    return xh
}

function process_button(prefix, menu_button) {
    d3.event.stopPropagation()
    x = xhr_button(prefix, menu_button.data.name)
    x.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200) {
            // init_core()
            render_frame_tick()
            render_content(JSON.parse(this.responseText))
        }
    }
    x.send()
}

function process_menu_button(prefix, menu_button) {
    d3.event.stopPropagation()
    x = xhr_button(prefix, menu_button.data.name)
    x.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200) {
            // init_core()
            render_frame_tick()
            render_content(JSON.parse(this.responseText))
        }
    }
    x.send()
}

 function project_button_handler(prefix, menu_button) {
    console.log("project button handler "+prefix+" "+menu_button.data.name)
    clear_main()
    // update project menu
    this._menu_current.children[0].name = menu_button.data.name
    update_menu(this._menu_current)

    if (project_menu_list.includes(prefix)) {
        process_button(prefix, menu_button)
    } else {
        console.log("invalid command "+prefix)
    }
    render_frame_tick()
    return false;
}

function targets_button_handler(prefix, menu_button) {
    console.log("target button handler "+prefix+" "+menu_button.data.name)
    if (targets_menu_list.includes(prefix)) {
        process_button(prefix, menu_button)
    } else {
        console.log("invalid command "+prefix)
    }
    render_frame_tick()
    return false;
}

function network_button_handler(prefix, menu_button) {
    return function(d) {
        d3.event.stopPropagation()
        if (machine_menu.includes(d.data.name)) {
            x = xhr_button(prefix, d.data.name)
            x.send("cmd="+d.data.name+"&host="+d.parent.data.name)
        }
        click(d.parent)
    }
}

function view_button_handler(prefix, menu_button) {
    console.log("view button handler "+prefix+" "+menu_button.data.name)
    if (view_drop_down_list.includes(prefix)) {
        process_button(prefix, menu_button)
    } else {
        console.log("invalid command "+prefix)
    }
    render_frame_tick()
    return false;
}

function sample_button_handler(prefix, menu_button) {
    console.log("sample button handler "+prefix+" "+menu_button.data.name)

    if (sample_menu_list.includes(prefix)) {
        process_button(prefix, menu_button)
    } else {
        console.log("invalid command "+prefix)
    }
    render_frame_tick()
    return false;
}

function jobs_button_handler(prefix, menu_button) {
    d3.event.stopPropagation()
    if (jobs_drop_down_list.includes(d.data.name)) {
        x = xhr_button(prefix, d.data.name)
        x.send("target="+d.parent.data.name)
    }
    click(d.parent)
}

function pop_menu(menu_button) {
    console.log(menu_button)
    i=0
    node = d3.select("g.main")
        .selectAll("g.button")
        .data(menu_button._children, (d) => d.children)
    nenter = node.enter()
        .append("g")
        .attr("class", "button")
        .on("click", (d) => project_button_handler(d.data.name, menu_button))
    this._option_translate_container = nenter
    nenter.append("rect")
    	.attr("class", "node")
        .style("fill", "red")
        .attr("stroke", "black")
        .attr("cursor", "pointer")
    nenter.append("text")
        .attr("dy", ".15em")
        .attr("font-size", "12px")
        .text((d) => d.data.name)
        .attr("x", 5)
        .attr("y", (d) => proto.button_top_padding)
        .attr("cursor", "pointer")
        .on("click", (d) => project_button_handler(d.data.name, menu_button))

    update = nenter.merge(node)
        .each(function(d) {
            if (d.id == undefined) { d.id = ++i }
            d.x0 = menu_button.x0+20
            d.y0 = menu_button.y0+(d.id*proto.button_height)
        })
        .attr("transform", (d) => "translate("+(proto.x+d.x0)+","+(proto.y+d.y0)+")")
    	.transition()
	    .duration(proto.duration)
    update.select("rect.text")
        .attr("x", (d) => 5)
        .attr("y", (d) => proto.button_top_padding)

    update.select("rect.node")
        .attr("height", proto.button_height)
        .attr("width", proto.button_width)
    exit = node.exit().transition()
        .duration(proto.duration)
        .remove()
    exit.select("rect")
        .attr("height", 0)
        .attr("width", 0)
    exit.select("text")
        .style("fill-opacity", 1e-6)
        .attr("stroke", "rgba(0,0,0,0)")
}

function render_frame_tick(){
    dim = wxh()
    width = dim.width
    height = dim.height
    d3.select("svg").attr("width", width).attr("height", height)
    d3.selectAll(".rs-width").attr("width", width)
    d3.select("g.main").attr("height", height-proto.menu_height-proto.console_height)
    d3.select(".commandline").attr("size", x/9+5)
    height -= proto.console_height
    d3.select("g.output").attr("transform","translate(0,"+height+")")
    d3.select(".rs-width").attr("width", width)
    render_menu_tick()
    
    d3.selectAll("g.root-item").attr("transform", (d) => "translate("+(proto.x+d.x0)+","+(proto.y+d.y0)+")")
    d3.selectAll("g.button").attr("transform", (d) => "translate("+(proto.x+d.x0)+","+(proto.y+d.y0)+")")
    draw_background_grid()
}

function init_core() {
    dim = wxh()
    width = dim.width,
    height = dim.height
    svg = d3.select("body")
        .append("svg")
        .attr("width", width)
        .attr("height", height)

    svg.append("g").classed("rs-width menu", true)
    svg.append("g").classed("rs-width main", true)
    svg.append("g").classed("rs-width output", true)
        .append("rect")
        .attr("height", proto.console_height)
        .style("stroke", "black")
        .style("fill", "rgba(0,0,0,.5)")
        .classed("rs-width log", true)
    d3.select("body")
        .append("input")
        .classed("commandline", true)
        .attr("height", proto.input_height)
        .attr("maxlength", 2048)
        .attr("name", "q")
        .attr("type", "text")
        .on("keyup", function() {
            var keyCode = d3.event.keyCode || d3.event.which
            if (keyCode === 13) {
                d3.event.preventDefault()
                return false
            }
        })
        .on("keypress", function(e) {
            var keyCode = d3.event.keyCode || d3.event.which;
            if (keyCode === 13) {
                d3.event.preventDefault()
                crlf(document.getElementsByClassName("commandline")[0].value)
                document.getElementsByClassName("commandline")[0].value = ""
                return false
            }
        });

    init_menu("scratch")
    init_console()
    install_handlers()
    return svg
}

function install_handlers() {
    d3.select("g.output").call(d3.zoom)
    	.on("wheel.zoom", log_scroll)
    svg.on("wheel.zoom", pan)
    d3.select(window).on('resize', render_handler)
    d3.select("svg").call(d3.drag().on("start", drag_fn))
}

function init_console() {
    proto._console_data = []
}

function register_console_messages(messages) {
    if (messages)
	for(message of messages) crlf(message)
}

function crlf(mesg) {
    proto._console_data.push({name: mesg})
    d3.select("g.output").on("click", function() {
        dim = wxh()
        if (proto.console_party) {
            proto.console_party = false
            proto.console_height = dim.height/2
        } else {
            proto.console_party = true
            proto.console_height = proto.console_height_down
        }
        d3.select(this).attr("height", proto.console_height)
        d3.select(".log").attr("height", proto.console_height)
        d3.event.stopPropagation()
        render_frame_tick()
    })
    return draw_lines(d3.select("g.output"), proto._console_data)
    	.style("stroke", "white")
        .on("mouseover", function(d, i) {
            d3.select(this).attr("stroke", proto.highlight_color)
        })
        .on("mouseout", function(d, i) {
            d3.selectAll("log-text").attr("stroke", "white")
        })
}

function log_scroll() {
    d3.event.stopPropagation()
    proto.cy += d3.event.wheelDelta/10
    // if (proto.cy <= 0) proto.cy = 0

    if (proto.cy <= (1-proto._console_data.length)*proto.slice_height) {
        proto.cy = (1-proto._console_data.length)*proto.slice_height
    } else if (proto.cy >= proto.console_height-proto.slice_height) {
        proto.cy = proto.console_height-proto.slice_height
    }
    d3.selectAll(".log-text")
        .attr("y", (d) => proto.cy+d.id*proto.slice_height+proto.label_top_padding)
    render_frame_tick()
}

function draw_background_grid() {
    base = proto.background_grid_base
    grid = base*20
    base = base+"px "+base+"px"
    grid = grid+"px "+grid+"px"
    background_size = [base, base, grid, grid, grid, grid, grid, grid, base].join(", ")
    d3.select("body").style("background-size", background_size)
}

function drag_fn() {
    d3.event.on("drag", dragged).on("end", ended)
    function dragged(event, d) {
	proto.x += d3.event.dx/1.5
	proto.y += d3.event.dy/1.5
	d3.select("body").style("background-position-x", proto.x+"px")
	d3.select("body").style("background-position-y", proto.y+"px")
	render_handler()
    }
    function ended() {
	// console.log("drag ended")
    }
}

function render_handler() {
    render_frame_tick()
    render_menu_tick()
}

function pan() {
    proto.y -= d3.event.wheelDelta/7
    render_frame_tick()
    d3.event.stopPropagation()
}
