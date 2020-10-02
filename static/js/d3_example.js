var margin = { top: 10, right: 10, bottom: 20, left: 30 };
width = 400 - margin.left - margin.right,
height = 400 - margin.top - margin.bottom,
generalTextColor = '#cacaca',
rightPanelTextColor = '#cacaca';
var parseDate = d3.timeParse("%Y-%m-%d");

//Define initial axis values for scatter chart
var xVal = 'Goals',
yVal = 'xG'

d3.json("/data").then(function(records) {

    records.forEach(function(d) {
        d['DateParse'] = parseDate(d['DateParse']);
    });
    //building form chart
d3.json("/formData").then(function(formData) {

    var [squadA, squadB] = formData[0].Match.split(' vs. ') // Get selected squad names

    //split data for the lines in the form chart
    var lineOne = formData.filter(function(d) {return d.Squad == squadA})
    var lineTwo = formData.filter(function(d) {return d.Squad == squadB})

    //nest main dataset by player
    var nested = d3.nest()
                    .key(function(d) {return d.Player})
                    .rollup(function(player) {
                        return player.map(function(c) {
                            return {"Gls": +c.Gls,'Min':+c.Min, "xG": +c.xG,'Ast': +c.Ast,'xA':+c.xA, 'DateParse': c.DateParse, "Squad": c.Squad,"P_color": c.P_color, "S_color":c.S_color}
                        });
                    })
                    .entries(records)

    //function to sum up stats in the nested data (currently has one entry per date)
    function sumStatsScatter(node) {
        if (node.value) {
            node.values = node.value;
            delete node.value;
        }
        node.Goals = node.values.reduce(function(r,v){
            return r + (v.value? sumStats(v) : v.Gls);
        },0);
        node.xG = node.values.reduce(function(r,v){
            return r + (v.value? sumStats(v) : v.xG);
        },0);
        node.xA = node.values.reduce(function(r,v){
            return r + (v.value? sumStats(v) : v.xA);
        },0);
        node.Ast = node.values.reduce(function(r,v){
            return r + (v.value? sumStats(v) : v.Ast);
        },0);
        node.Min = node.values.reduce(function(r,v){
            return r + (v.value? sumStats(v) : v.Min);
        },0);
        return node.Goals, node.xG,node.Ast, node.xA,node.Min
    }    
    nested.forEach(function(node) {
        sumStatsScatter(node)
    })    

    nested = nested.filter(function(d) {return d.Min > 89}) // removes potential outliers from scatter plot 

    //define svg for scatter plot
    var svgScatter = d3.select("#scatter-chart").append("svg")
                .attr("id","svg-")
                .attr("preserveAspectRatio", "xMinYMin meet")
                .attr("viewBox", "0 0 472 472")
                
    //Find max value from x and y axes for scatter plot. I want the axes to have the same scale
    var scatterDomMax = d3.max(nested,function(d){return (d[xVal] / (d.Min/90))})*1.1 > d3.max(nested,function(d){return (d[yVal]/(d.Min/90))})*1.1 ? 
                        d3.max(nested,function(d){return (d[xVal] / (d.Min/90))})*1.1 : d3.max(nested,function(d){return (d[yVal]/(d.Min/90))})*1.1;
    //define x scale
    var xScale = d3.scaleLinear()
                .domain([0,scatterDomMax])
                .range([margin.left, 400]);

    var xAxis = svgScatter.append("g")
    .call(d3.axisBottom(xScale))
    .attr("class","x-axis")
    .attr("transform", "translate(0," + (400) + ")");    

    //x label
    svgScatter.append("text")
        .attr("class","scatterLabels")
        .style("text-anchor", "end")
        .attr("x", 405)
        .attr("y", 395)
        .style("font-size","24px")
        .style("fill",generalTextColor)
        .text(xVal + '/90').lower();

    //define y axis
    var yScale = d3.scaleLinear()
        .domain([0,scatterDomMax])
        .range([400,0])

    var yAxis=svgScatter.append("g")
        .call(d3.axisLeft(yScale))
        .attr("class","y-axis")
        .attr("transform", "translate(" + margin.left + ",0)")
        
    //y label
    svgScatter.append("text")
        .attr("class","scatterLabels")
        .attr("transform", "rotate(-90)")
        .attr("y", margin.right + 18)
        .attr("dy", "1em")
        .style("text-anchor", "end")
        .style("font-size","24px")
        .style("fill",generalTextColor)
        .text(yVal + '/90').lower();
    
    var tooltip = d3.select("body").append("div")	
                    .attr("id", "tooltip")				
                    .style("opacity", 0);

    //add dots to the scatter chart
    var dots = svgScatter.selectAll('circle')
        .data(nested)
        .enter()
        .append('circle')
        .attr("cx", function (d) { return xScale(d[xVal]/(d.Min/90)); })
        .attr("cy", function (d) { return yScale(d[yVal]/(d.Min/90)); })
        .attr("r", function(d) {return 6})
        .attr("class","testing")
        .style("stroke", function(d) {return (d.values[0].Squad == squadA) ? d.values[0].S_color: 
        (d.values[0].Squad == squadB) ? d.values[0].S_color :"#362D2D"}) //assign color based on the selected squad
        .style("stroke-width", "2px")
        .style("fill", function(d) {return (d.values[0].Squad == squadA) ? d.values[0].P_color: 
        (d.values[0].Squad == squadB) ? d.values[0].P_color :"#362D2D"})
        .on("mouseover", function(d) {		
            tooltip.transition()		
                .duration(200)		
                .style("opacity", .9)

            tooltip.html('<div style="width: 83%;height: 100%;padding-top: 0.5%; float:left"><table style="width:100%;"> <tr> ' +
                '<th colspan="3" style="border-right: 1px solid black">' +  d.key + '</th><th colspan="3" style="border-left: 1px solid black">' + d.values[0].Squad + '</th><th colspan=2>' +
                '<tr><td>Goals:</td><td>' + Math.round((d.Goals + Number.EPSILON) * 100) / 100 +
                '</td><td>xG:</td><td>' + Math.round((d.xG + Number.EPSILON) * 100) / 100 + 
                '</td><td>Apps:</td><td>' + d.values.length +
                '</td></tr><tr></td><td>Assists:</td><td>' + d.Ast + 
                '</td><td>xA:</td><td>' + Math.round((d.xA + Number.EPSILON) * 100) / 100 +
                '</td><td>Mins:</td><td>' + d.Min + 
                '</td></tr></table></div>')
                .style("left", 0 + "px")	
                .style("left", (d3.event.pageX + 10) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            })	       				
        .on("mouseout", function(d) {		
            tooltip.transition()		
                .duration(500)		
                .style("opacity", 0);	
        });

    //build points chart
    formData.forEach(function(d) {
        d.DateParse = parseDate(d.DateParse);
    });

    var formHeight = height - 70,
        formWidth = width * 2 - margin.left - margin.right

    var svgForm = d3.select("#dc-form-chart").append("svg")
        .attr("class","svgForm")
        .attr("preserveAspectRatio", "xMinYMin meet")
        .attr("viewBox", "0 0 750 400")
        .append("g")
        .attr("transform","translate(" + margin.left + "," + margin.top + ")");

    // set the ranges
    var x = d3.scaleTime().range([0, formWidth]);
    var y = d3.scaleLinear().range([formHeight, 0]);

    // define the 1st line
    var valueline = d3.line()
        .x(function(d) { return x(d.DateParse); })
        .y(function(d) { return y(d.rank); });

    // define the 2nd line
    var valueline2 = d3.line()
        .x(function(d) { return x(d.DateParse); })
        .y(function(d) { return y(d.rank); });

      // Scale the range of the data
        x.domain(d3.extent(formData, function(d) { return d.DateParse; }));
        y.domain([20,1]); // PL rankings are from 1:20

        // Add the valueline path.
        svgForm.append("path")
            .data([lineOne])
            .attr("class", "line")
            .style("stroke", function(d) {return d[0].P_color})
            .style("fill","none")
            .attr("d", valueline);

        // Add the valueline2 path.
        svgForm.append("path")
            .data([lineTwo])
            .attr("class", "line")
            .style("stroke", function(d) {return d[0].P_color})
            .style("fill","none")
            .attr("d", valueline2);

        // Add the X Axis
        svgForm.append("g")
            .attr("transform", "translate(0," + formHeight + ")")
            .call(d3.axisBottom(x)).attr('form-x');

        // Add the Y Axis
        svgForm.append("g")
            .call(d3.axisLeft(y)).attr('form-y');

        // Define the div for the tooltip
        var formToolDiv = d3.select("body").append("div")	
        .attr("class", "formTooltip")				
        .style("opacity", 0);

        // Add dots
        var myCircle = svgForm.append('g')
        .attr("class","dots")
        .selectAll("circle")
        .data(formData)
        .enter()
        .append("circle")
            .attr("cx", function (d) { return x(d.DateParse); } )
            .attr("cy", function (d) { return y(d.rank); } )
            .attr("r", 4)
            .style("fill", function (d) {if (d.Points == 3) return 'green'
                                        else if (d.Points == 0) return 'red'
                                        else return 'yellow'})
            .style("opacity", 0.7)
            .on("mouseover", function(d) {		
                formToolDiv.transition()		
                    .duration(200)		
                    .style("opacity", .9);		
                    formToolDiv	.html(d.matchup.replace(d.Squad,'').replace(' vs. ','') + ' (' + d.HA + ')'  +"<br/>"  +
                                        d.score_H + '-' + d.score_A)	
                    .style("left", (d3.event.pageX) + "px")		
                    .style("top", (d3.event.pageY - 28) + "px");	
                })					
            .on("mouseout", function(d) {		
                formToolDiv.transition()		
                    .duration(500)		
                    .style("opacity", 0);	
            });

        // Set idleTimeOut to null
        var idleTimeout
        function idled() { idleTimeout = null; }
        // Function that is triggered when brushing is performed
        var extent = [0, 10000]

        //Update function
    function updateChart(xVal,yVal) {
        width = 400 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom

        extent = d3.event.selection //used to find the selected date range

        if(!extent){
            extent = [0, 10000] //if no date range selected, take all available
            }

        var dataFilter = records.filter(function(d) {return d.DateParse >= x.invert(extent[0]) & d.DateParse <= x.invert(extent[1])})

        //nesting stuff
        var nestedFilter = d3.nest()
        .key(function(d) {return d.Player})
        .rollup(function(player) {
            return player.map(function(c) {
                return {"Gls": +c.Gls,'Min':+c.Min,"xG": +c.xG,'Ast': +c.Ast,'xA':+c.xA, 'DateParse': c.DateParse, "Squad": c.Squad,"P_color": c.P_color, "S_color":c.S_color}
            });
        })
        .entries(dataFilter)

        nestedFilter.forEach(function(node) {
            sumStatsScatter(node)
        })    
        nestedFilter = nestedFilter.filter(function(d) {return d.Min > 89})
        var scatterDomMax = d3.max(nestedFilter,function(d){return (d[xVal] / (d.Min/90))})*1.1 > d3.max(nestedFilter,function(d){return (d[yVal]/(d.Min/90))})*1.1 ? 
                            d3.max(nestedFilter,function(d){return (d[xVal] / (d.Min/90))})*1.1 : d3.max(nestedFilter,function(d){return (d[yVal]/(d.Min/90))})*1.1
        //define x scale
        var xScale = d3.scaleLinear()
            .domain([0,scatterDomMax])
            .range([margin.left, 400]);

        var xAxis = svgScatter.selectAll("g.x-axis")
            .transition().duration(500)
            .call(d3.axisBottom(xScale))

            //define y axis
        var yScale = d3.scaleLinear()
            .domain([0,scatterDomMax])
            .range([400,0])

        var yAxis=svgScatter.selectAll("g.y-axis")
            .transition().duration(500)
            .call(d3.axisLeft(yScale))

        //x label
        svgScatter.selectAll(".scatterLabels").remove();

        svgScatter.append("text")
            .attr("class","scatterLabels")
            .style("text-anchor", "end")
            .attr("x", 405)
            .attr("y", 395)
            .style("font-size","24px")
            .style("fill",generalTextColor)
            .text(xVal + '/90').lower();

        //y label
        svgScatter.append("text")
            .attr("class","scatterLabels")
            .attr("transform", "rotate(-90)")
            .attr("y", margin.right + 18)
            .attr("dy", "1em")
            .style("text-anchor", "end")
            .style("font-size","24px")
            .style("fill",generalTextColor)
            .text(yVal + '/90').lower();

        var updatedDots = d3.select("#scatter-chart").select("#svg-").selectAll("circle").data(nestedFilter);

        updatedDots.enter().append("circle");
        updatedDots.exit().remove();

        var tooltip = d3.select("#tooltip").style("opacity",0);

        updatedDots
            .transition()
            .duration(1000)
            .attr("cx", function (d) { return xScale(d[xVal]/ (d.Min/90)); })
            .attr("cy", function (d) { return yScale(d[yVal]/(d.Min/90)); })
            .attr("r", function(d) {return 6})
            .style("stroke", function(d) {return (d.values[0].Squad == squadA) ? d.values[0].S_color: 
                                            (d.values[0].Squad == squadB) ? d.values[0].S_color :"#362D2D"})
            .style("stroke-width", "2px")
            .style("fill", function(d) {return (d.values[0].Squad == squadA) ? d.values[0].P_color: 
                                            (d.values[0].Squad == squadB) ? d.values[0].P_color :"#362D2D"});
        updatedDots.on("mouseover", function(d) {		
            tooltip.transition()		
                .duration(200)		
                .style("opacity", .9)

            tooltip.html('<div style="width: 83%;height: 100%;padding-top: 0.5%; float:left"><table style="width:100%;"> <tr> ' +
                '<th colspan="3" style="border-right: 1px solid black">' +  d.key + '</th><th colspan="3" style="border-left: 1px solid black">' + d.values[0].Squad + '</th><th colspan=2>' +
                '<tr><td>Goals:</td><td>' + Math.round((d.Goals + Number.EPSILON) * 100) / 100 +
                '</td><td>xG:</td><td>' + Math.round((d.xG + Number.EPSILON) * 100) / 100 + 
                '</td><td>Apps:</td><td>' + d.values.length +
                '</td></tr><tr></td><td>Assists:</td><td>' + d.Ast + 
                '</td><td>xA:</td><td>' + Math.round((d.xA + Number.EPSILON) * 100) / 100 +
                '</td><td>Mins:</td><td>' + d.Min + 
                '</td></tr></table></div>')
                .style("left", 0 + "px")	
                .style("left", (d3.event.pageX + 10) + "px")		
                .style("top", (d3.event.pageY - 28) + "px");	
            })	       				
        .on("mouseout", function(d) {		
            tooltip.transition()		
                .duration(500)		
                .style("opacity", 0);	
        });
  }
  //end of update function
    
    // Calling updates
    svgForm.append("g").attr("class", "brush")
    .call( d3.brushX()                 // Add the brush feature using the d3.brush function
      .extent( [ [0,0], [formWidth,formHeight] ] ) // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
      .on("end", updateAll) // Each time the brush selection changes, trigger the 'updateChart' function
    ).lower();

    function updateAll() {
          updateChart(xVal,yVal);
          updateChart(xVal,yVal);
    }

    //Update scatter axes on button click
    d3.select("#goalscoringBtn")
    .on("click", function() {
      xVal = 'Goals'
      yVal = 'xG'
      updateChart(xVal,yVal)
    });

    d3.select("#creatingBtn")
    .on("click", function() {
      xVal = 'Ast'
      yVal = 'xA'
      updateChart(xVal,yVal)
    });
    //End of update calls

})//team data end
})//data end




