queue()
	// .defer(d3.json, P1surveyURL)
    // .defer(d3.json, P2surveyURL)
    .defer(d3.json, surveyVizUrl)
    .await(ready);

function ready(error, attributes) {
    // console.log(attributes);
    d3TimeLine(attributes[0]);
    d3TimeLine(attributes[1]);
}