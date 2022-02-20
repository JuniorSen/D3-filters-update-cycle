var formatAsInteger = d3.format(",");

function d3Line(data){
    var margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;
    var svg = d3.select("#surveyData")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

    for(var ind of Object.keys(data)) {
        data[ind].ActivityDate = d3.timeParse("%d/%m/%Y")(data[ind].ActivityDate);
    }

    // Add X axis --> it is a date format
    var x = d3.scaleTime()
        .domain(d3.extent(data, function(d) { return d.ActivityDate; }))
        .range([ 0, width ]);
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

//https://code.tutsplus.com/tutorials/building-a-multi-line-chart-using-d3js-part-2--cms-22973
//The code from below till end could be put in loop to draw multiple linegraphs
    // Add Y axis
    var y = d3.scaleLinear()
        .domain(d3.extent(data, function(d) {return d['mood']}))
        .range([ height, 0 ]);
    svg.append("g")
        .call(d3.axisLeft(y));

    // // Add the line
    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", function(d, j) {
            return "hsl(" + Math.random() * 360 + ",100%,50%)";
        })
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
        .x(function(d) { return x(d.ActivityDate) })
        .y(function(d) { return y(d.mood)}))

}