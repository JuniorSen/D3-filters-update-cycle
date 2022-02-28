queue()
	.defer(d3.json, P1surveyURL)
    .defer(d3.json, P2surveyURL)
    .await(ready);

function ready(error, attributes1, attributes2) {
    d3TimeLine(attributes1);
    d3TimeLine(attributes2);
}