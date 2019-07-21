"use strict";

fetch("sales.json").then(r=>r.text()).then(r=>{
	// Note: access to sales and s _contents_ doesn't violate constness (may be confusing)
	const sales = JSON.parse(r);
	for (const s of sales.weekly) s[0] = new Date(s[0]).getTime();
	Highcharts.chart('chart', {
		title: { text: document.querySelector("h1").innerText },
		chart: { type: "column" },
		colors: ['#6CF', '#39F', '#06C', '#036', '#000'],
		xAxis: { type: "datetime" },
		yAxis: { title: { text: "€" }},
		series: [{ name: "Weekly sales", data: sales.weekly }],
	});
});
