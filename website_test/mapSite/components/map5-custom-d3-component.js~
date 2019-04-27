const React = require('react');
const D3Component = require('idyll-d3-component');
const d3 = require('d3');
const topojson = require('topojson-client'); // Need this for map

//var mapurl = "https://d3js.org/us-10m.v1.json";


class Map2CustomD3Component extends D3Component {

    initialize(node, props) {

	var svg = d3.select(node).append('svg');
	//var svg = d3.select("svg");
	
        var width = node.getBoundingClientRect().width;
        var height = width;
	
	svg.attr('viewBox', `0 0 ${width} ${height}`)
	    .style('width', '80%')
	    .style('height', 'auto');
	
	
	var width = node.getBoundingClientRect().width;
	var height = width;
	


	var path = d3.geoPath();
	//var projection = d3.geoAlbers();
	//var path = d3.geoPath().projection(projection);

	
	d3.json("https://d3js.org/us-10m.v1.json", function(error, us) {
	    if (error) throw error;

	    console.log(us.objects.states)

	    svg.append("g")
		.attr("class", "states")
		.selectAll("path")
		.data(topojson.feature(us, us.objects.states).features)
		.enter().append("path")
		.attr("d", path);
	    
	    svg.append("path")
		.attr("class", "state-borders")
		.attr("d", path(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; })));
	});

    }
    
    update(props, oldProps) {
	//this.svg.selectAll('circle')
	//    .transition()
	//    .duration(750)
	//    .attr('cx', Math.random() * size)
	//    .attr('cy', Math.random() * size);
    }
}

module.exports = Map2CustomD3Component;
