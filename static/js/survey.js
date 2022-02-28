var formatAsInteger = d3.format(",");

function d3TimeLine(data){
    var margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;
    console.log("data",data)
    metadata = Object.entries(data).slice(0,1).map(entry => entry[1])[0];
    data = Object.entries(data).slice(1,).map(entry => entry[1]);
    console.log("data",Object.entries(data));
    for(var ind of Object.keys(data)) {
        data[ind].ActivityDate = d3.timeParse("%d/%m/%Y")(data[ind].ActivityDate);
    }
    console.log("Meta",metadata);
    var svg = d3.select(metadata['panelId'])
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
    
    // Add X axis --> it is a date format
    var x = d3.scaleTime()
        .domain(d3.extent(data, function(d) { return d.ActivityDate; }))
        .range([ 0, width ]);

    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

//https://code.tutsplus.com/tutorials/building-a-multi-line-chart-using-d3js-part-2--cms-22973

    var columns = Object.values(
                    Object.keys(metadata)
                        .filter(key => key[0]=='c')
                        .reduce((obj, key) => {
                            obj[key] = metadata[key];
                            return obj
                        }, {})
                    );
    
    console.log(columns, metadata['panelId']);
    var res = d3.min(data, function(d) {
        var minVal = Number.MAX_SAFE_INTEGER;
        var maxVal = Number.MIN_SAFE_INTEGER;
        for(var col of columns) {
            minVal = Math.min(minVal, d[col]);
            maxVal = Math.max(maxVal, d[col]);
        }
        return minVal;
    });
    allVal = [];
    for(var col of columns) {
        allVal = allVal.concat(data.map(function (d){return d[col]}));
    }

    // Add Y axis
    var y = d3.scaleLinear()
        .domain(d3.extent(allVal))
        .range([ height, 0 ]);
    svg.append("g")
        .call(d3.axisLeft(y));

    //d3 category10 scheme used to color categories
    var catCol = d3.scaleOrdinal().domain(columns).range(d3.schemeCategory10);
    // // Add the line

    var ind = 1;
    for(var col of columns) {
        //The code from below till has been put in loop to draw multiple linegraphs
        svg.append("path")
            .datum(data)
            .attr("fill", "none")
            .attr("stroke", catCol(col))
            .attr("stroke-width", 1.5)
            .attr("d", d3.line()
            .x(function(d) { return x(d.ActivityDate) })
            .y(function(d) { return y(d[col])}));
        svg.append("circle")
            .attr("cx",width-50)
            .attr("cy",20*ind)
            .attr("r",4)
            .style("fill", catCol(col));
        svg.append("text")
            .attr("x",width-40)
            .attr("y",20*ind+4) //+radius
            .text(col)
            .style("font-size","15px")
            .attr("alignment-baseline","middle");
        ind += 1;
    }
}