const React = require('react');
const D3Component = require('idyll-d3-component');
const d3 = require('d3');
const topojson = require('topojson-client'); // Need this for map



class Map5CustomD3Component extends D3Component {

    initialize(node, props) {

	var svg = d3.select(node).append('svg');
	
        var width = node.getBoundingClientRect().width;
        var height = width;
	
	svg.attr('viewBox', `0 0 ${width} ${height}`)
	    .style('width', '80%')
	    .style('height', 'auto');
	
	
	var width = node.getBoundingClientRect().width;
	var height = width;
	


	//var projection 
	var path = d3.geoPath().projection(projection);

	
	d3.json("https://raw.githubusercontent.com/jnaiman/openChampaignProject/master/data/map_data/City_Council_Districts_topojson_s.json", function(error, us) {
	    if (error) throw error;

	    console.log(us.objects.City_Council_Districts)

	    svg.append("g")
		.attr("class", "states")
		.selectAll("path")
		.data(topojson.feature(us, us.objects.City_Council_Districts).features)
		.enter().append("path")
		.attr("d", path);
	    
	    svg.append("path")
		.attr("class", "state-borders")
		.attr("d", path(topojson.mesh(us, us.objects.City_Council_Districts, function(a, b) { return a !== b; })));
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

module.exports = Map5CustomD3Component;
