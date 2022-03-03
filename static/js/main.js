queue()
    .defer(d3.json, surveyVizUrl)
    .defer(d3.json, sigLocP1Url)
    .await(ready);
    // .defer(d3.json, P1surveyURL)
    // .defer(d3.json, P2surveyURL)

function ready(error, a1, a2) {
    // console.log(attributes);
    d3TimeLine(a1[0]);
    d3TimeLine(a1[1]);
    p1Calendar(a2);
}