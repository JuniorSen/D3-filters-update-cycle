queue()
	.defer(d3.json, surveyURL)
    .await(ready);

console.log(surveyURL)

function ready(error, attributes) {
    d3TimeLine(attributes);
}