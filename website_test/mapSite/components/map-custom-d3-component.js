const React = require('react');
const D3Component = require('idyll-d3-component');
const d3 = require('d3');
//const topojson = require('topojson-client');

//var width = 900;
//var height = 600;
//var projection = d3.geo.mercator();
// DID DO: npm install --save d3-geo, but not sure if that did it
//var projection = d3.geoMercator();

//var mapurl = "http://enjalot.github.io/wwsd/data/world/world-110m.geojson";
//var mapurl = "https://raw.githubusercontent.com/cszang/dendrobox/master/data/world-110m2.json";
var mapurl = "https://d3js.org/us-10m.v1.json";


class MapCustomD3Component extends D3Component {

    initialize(node, props) {
	//const svg = this.svg = d3.select(node).append('svg');
    //const canvas = d3.select(node).append('canvas').node();
    //const context = canvas.getContext("2d");
    //const width = node.getBoundingClientRect().width;
    //const height = width * 0.9;
    //canvas.width = width;
    //canvas.height = height;



	var svg = d3.select(node).append('svg');

	var width = node.getBoundingClientRect().width;
	var height = width;

	var projection = d3.geoMercator()
	    .center([-81.369515, 28.538479])
	    .scale(400000)
	    .translate([width / 2, height / 2])
	
	var canvas = d3.select('body').append('canvas')
	    .attr('height', height)
	    .attr('width', width)
	
	var ctx = canvas.node().getContext('2d')

	var path = d3.geoPath()
	    .projection(projection)
	    .context(ctx)
	
    svg.attr('viewBox', `0 0 ${width} ${height}`)
      .style('width', '100%')
      .style('height', '100%');

	
	//svg.attr('width', width);
	//svg.attr('height', height);

	//var projection = d3.geoMercator()
	//var projection = d3.
	//    .scale(width / 2 / Math.PI)
	//    .translate([width / 2, height / 2]);
	//var path = d3.geoPath().projection(projection);
	
	//svg.attr('viewBox', `0 0 ${width} ${height}`)
	//    .style('width', '100%')
	//    .style('height', 'auto');

	

//    d3.json(mapurl, function(err, geojson) {
//      svg.append("path")
//        .attr("d", path(geojson))
//    });

	//var projection = d3.geoAlbersUsa().scale(500).translate([250,250]);
	//const context = DOM.context2d(width, height);

	//var path = d3.geoPath(projection);

//	d3.json("https://d3js.org/us-10m.v1.json", function(error, us) {
//  if (error) throw error;
//
//  svg.append("g")
//      .attr("class", "states")
//    .selectAll("path")
//    .data(topojson.feature(us, us.objects.states).features)
//    .enter().append("path")
//      .attr("d", path);
//
//  svg.append("path")
//      .attr("class", "state-borders")
//      .attr("d", path(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; })));
//});

	  

    }
    
    update(props, oldProps) {
	//this.svg.selectAll('circle')
	//    .transition()
	//    .duration(750)
	//    .attr('cx', Math.random() * size)
	//    .attr('cy', Math.random() * size);
    }
}

module.exports = MapCustomD3Component;
