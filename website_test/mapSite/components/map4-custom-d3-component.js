const React = require('react');
const D3Component = require('idyll-d3-component');
const d3 = require('d3');
const topojson = require('topojson-client'); // Need this for map

//var mapurl = "https://d3js.org/us-10m.v1.json";
var width  = 300;
var height = 400;


class Map4CustomD3Component extends D3Component {

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
	
	//var projection = d3.geoMercator()
        //    .center([80,25])
        //    .translate([w/2, h/2])
        //    .scale(800);

//	var path = d3.geoPath();
	
	
	d3.json("https://raw.githubusercontent.com/jnaiman/openChampaignProject/master/data/map_data/City_Council_Districts_topojson.json", function(error, us) {
	    if (error) throw error;

	    //console.log(us.objects.City_Council_Districts)
	    //console.log(us)

	    var center = d3.geoCentroid(us.transform.translate);
	    var scale  = 150;
	    var offset = [width/2, height/2];
	    var projection = d3.geoMercator().scale(scale).center(center)
		.translate(offset);

	    //console.log(center, scale, offset);
	    
	    // create the path
	    var path = d3.geoPath().projection(projection);

	    //console.log('here');
	    //console.log(us.bbox);
	    
	    // using the path determine the bounds of the current map and use 
	    // these to determine better values for the scale and translation
	    //var bounds  = path.bounds(us);
	    var bounds = us.bbox;
	    //console.log(bounds[0]);
	    var hscale  = scale*width  / (bounds[0] - bounds[2]);
	    //console.log(hscale);
	    var vscale  = scale*height / (bounds[1] - bounds[3]);
	    var scale   = (hscale < vscale) ? hscale : vscale;
	    var offset  = [width - (bounds[2] + bounds[0])/2,
                           height - (bounds[3] + bounds[1])/2];

	    console.log(hscale, vscale, scale,offset);
	    // new projection
	    // HERE: this at least prints something but it looks all wrong
	    projection = d3.geoMercator().center(us.transform.translate)
		.scale(500000).translate(us.transform.translate);
	    path = path.projection(projection);

	    
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

module.exports = Map4CustomD3Component;
