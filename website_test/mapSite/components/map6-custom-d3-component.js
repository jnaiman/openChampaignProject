const React = require('react');
const D3Component = require('idyll-d3-component');
const d3 = require('d3');

// JPN: had to add the following
const topojson = require('topojson-client'); // Need this for map
const d3tip = require('d3-tip');

//const size = 600;
//const width = 600;
//const height= 600;

var margin = {top: 0, right: 0, bottom: 0, left: 0},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
var format = d3.format(",");


class Map6CustomD3Component extends D3Component {
    
    initialize(node, props) {
	const svg = this.svg = d3.select(node).append('svg')
	svg.attr("width", width)
            .attr("height", height)
            .append('g')
            .attr('class', 'map');


	// Set tooltips
	//var tip = d3tip() // JPN: had to change here d3.tip -> d3tip
        //    .attr('class', 'd3-tip')
        //    .offset([-10, 0])
        //    .html(function(d) {
//		return "<strong>Country: </strong><span class='details'>" + d.properties.name + "<br></span>" + "<strong>Corgis Born: </strong><span class='details'>" + format(d.population) +"</span>";
//            })
	
	
	var color = d3.scaleThreshold()
	    .domain([0,
		     1,
		     5,
		     10,
		     25,
		     50,
		     100,
		     300,
		     1000,
		     1200])
	    .range(["rgb(0,0,0)",
		    "rgb(1,1,1)",
		    "rgb(3,19,43)",
		    "rgb(8,48,107)",
		    "rgb(8,81,156)",
		    "rgb(33,113,181)",
		    "rgb(66,146,198)",
		    "rgb(107,174,214)",
		    "rgb(158,202,225)",
		    "rgb(198,219,239)"
		   ]);


	//var path = d3.geoPath();
		
	var projection = d3.geoEquirectangular()
            .scale(180000)
            .translate( [width / 4, height*3/4])
	    .center([-88.33330288929228,40.061894153130176]);
	var path = d3.geoPath().projection(projection);
	
	//svg.call(tip);

	d3.queue() // JPN: had to change queue -> d3.queue()
	//.defer(d3.json, "https://raw.githubusercontent.com/jdamiani27/Data-Visualization-and-D3/master/lesson4/world_countries.json")
	    .defer(d3.json,"https://raw.githubusercontent.com/jnaiman/openChampaignProject/master/data/map_data/City_Council_Districts_topojson_2.json")
	    .defer(d3.json, "https://raw.githubusercontent.com/jnaiman/corgWebsiteBuild/master/data/corgiData_countries.json")
	    .await(ready);

	function ready(error, data, population) {
	    if (error) throw error;
	    var corgPopulationById = {};

	    // neg to pos
	    //data.objects.City_Council_Districts.forEach( function(d) { d; });
	    //data.objects.City_Council_Districts.forEach( function(d) {console.log(d);} );
	    
	    svg.append("g")
		//.attr("class", "countries")
		.selectAll("path")
		.data(data.objects.City_Council_Districts)
		.enter().append("path")
		.attr("d", path)
		//.style("fill", 'red')
		//.style('stroke', 'red');
		//.style('stroke-width', 1.5)
		//.style("opacity",0.8);
	
	    // tooltips
	//	.style("stroke","white")
	//	.style('stroke-width', 0.3)
	//	.on('mouseover',function(d){
	//	    tip.show(d, this); 
	//	    d3.select(this)
	//		.style("opacity", 1)
	//		.style("stroke","white")
	//		.style("stroke-width",3);
	//	})
	//	.on('mouseout', function(d){
	//	    tip.hide(d);
	//	    
	//	    d3.select(this)
	//		.style("opacity", 0.8)
	//		.style("stroke","black")
	//		.style("stroke-width",0.3);
	//	});
	    
	    svg.append("path")
		//.datum(topojson.mesh(data.objects.City_Council_Districts, function(a, b) { return a !== b; }))
	        //.datum(topojson.mesh(data, data.objects.City_Council_Districts, (a, b) => a !== b))
	        .datum(topojson.mesh(data,data.objects.City_Council_Districts))
		.attr("d", path)
	    	.style("fill", 'blue')
		.style('stroke', 'red');

	}
    
    }
}



module.exports = Map6CustomD3Component;
