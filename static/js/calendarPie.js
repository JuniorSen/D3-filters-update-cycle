//Month days map
monthDays = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

function calendarPie(data) {
    meta = Object.entries(data).slice(0,1)[0][1];
    panelId = meta['panelId']
    data = Object.entries(data).slice(1,).map(entry => entry[1]);        
    dates = Object.entries(data).map(entry => d3.timeParse("%Y-%m-%d")(entry[1]['ActivityDate']));
    values =  Object.entries(data).map(entry => (entry[1]['locations']));
    pieData = values[2];
    var margin = {top:40, left:20}

    var pie = d3.pie().value(function(d) {
                return d.proportion;});
    var catCol = d3.scaleOrdinal().domain(d3.range(5)).range(d3.schemeCategory10);    

    const X = dates;
    var margin = {top: 170, right: 30, bottom: 30, left: 180}
    var curDay = X[0].getDay();
    const availableDates = X.map(entry => entry.getDate());
    const totalDays = monthDays[X[0].getMonth()+1];
    const Y = Object.entries(data).map(entry => (entry[1]['locations'][0]['proportion']));
    const I = d3.range(totalDays);
    var xind = 0;
    const Month = 11;
    const Year = 2021;
    const yFormat = '';
    const cellSize = 50;
    const radius = cellSize/2-2;
    const colors = d3.scaleLinear().domain([d3.min(Y),d3.max(Y)]).range(["paleturquoise", "dodgerblue"]);
    // // Compute a color scale. This assumes a diverging color scheme where the pivot
    // // is zero, and we want symmetric difference around zero.
    // const max = d3.quantile(Y, 0.9975, Math.abs);
    const formatDay = i => "MTWTFSS"[i];

    var svg = d3.select(panelId)
                .append("svg")
                .attr("width", cellSize*15+margin.left+100)
                .attr("height", cellSize*(Math.ceil(X.length/7)+4)+margin.top+100)
                .append("g")
                .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
    for(var day of d3.range(7)) {
      svg.append("rect")
      .datum(ind+1)
      .attr("x", day*cellSize+1)
      .attr("y", 1)
      .attr("height", radius*2)
      .attr("width", radius*2)
      .attr("stroke","black")
      .attr("stroke-width","1px")
      .attr("rx",radius/2)
      .attr("ry",radius/2)
      .attr("fill","#FFD700")

      svg.append("text")
          .attr("x", day*cellSize+1+radius)
          .attr("y", 1+radius)
          .text(formatDay(day))
          .attr("alignment-baseline","middle")
          .attr("text-anchor","middle")
          .style("font-size",String(cellSize/3)+"px")
    }
    
    points = d3.range(d3.min(Y),d3.max(Y),0.001).reverse();
    sampleHeight = Math.ceil(X.length/7)*cellSize


    console.log(I,"I")
    for(var ind of I) {
        pieData = values[ind];
        // console.log(values,ind,pieData,ind);
        if(!(typeof pieData === 'undefined') && Object.keys(pieData).length != 0) {
                svg.selectAll('g')
                        .data(pie(pieData))
                        .enter()
                        .append("path")
                        .attr('d', d3.arc()
                                .innerRadius(0)
                                .outerRadius(radius))
                        .attr('fill', function(d){return(catCol(d.index))})
                        .attr("stroke", "black")
                        .attr('transform',"translate("+(curDay%7*cellSize+radius+1)+"+"+((Math.floor(curDay/7)+1)*cellSize+radius+1)+")")
                        .style("stroke-width", "1px")
                        .style("opacity", 0.7)
        }
        else {
                svg.append("circle")
                .attr("r",radius)
                .attr('fill', "grey")
                .attr("cx",curDay%7*cellSize+radius+1)
                .attr("cy",(Math.floor(curDay/7)+1)*cellSize+radius+1)
                .style("stroke-width", "1px")
                .style("opacity", 0.7)
        }
        svg.append("text")
                .attr("x", curDay%7*cellSize+1)
                .attr("y", (Math.floor(curDay/7)+1)*cellSize+radius/3)
                .text(ind+1)
                .attr("alignment-baseline","mathematical")
                .attr("text-anchor","middle")
                .style("font-size",String(cellSize/5)+"px")
                .style("color","white");
        curDay += 1;
    }
    
  }