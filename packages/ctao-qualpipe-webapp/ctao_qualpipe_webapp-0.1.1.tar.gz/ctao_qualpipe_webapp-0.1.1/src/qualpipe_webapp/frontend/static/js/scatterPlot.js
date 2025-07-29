// NOSONAR
function scatterPlot(id, data, metadata) {
  // NOSONAR

  // Check if data are arrays
  if (
    data &&
    !Array.isArray(data) &&
    typeof data === "object" &&
    Array.isArray(data.x) &&
    Array.isArray(data.y)
  ) {
    const length = data.x.length;
    const arr = [];
    for (let i = 0; i < length; i++) {
      arr.push({
        x: data.x[i],
        y: data.y[i],
        xerr: data.xerr ? data.xerr[i] : undefined,
        yerr: data.yerr ? data.yerr[i] : undefined,
      });
    }
    data = arr;
  }

  // Remove any precedent SVG element
  d3.select("#" + id)
    .selectAll("svg")
    .remove();

  d3.select("#" + id + " h5").remove(); // Remove placeholder title

  // clean div element if previous error was shown
  d3.select("#" + id).text("");

  // Dynamically retrieve container sizes
  const container = document.getElementById(id);
  const boundingRect = container.getBoundingClientRect();
  let width = boundingRect.width;
  let height = boundingRect.height;

  // // Margins
  const margin = { top: 30, right: 15, bottom: 45, left: 50 };
  width = width - margin.left - margin.right;
  height = height - margin.top - margin.bottom;

  // Append the svg object to the body of the page
  const svg = d3
    .select("#" + id)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // If no data, return message
  if (!data || data.length === 0) {
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", height / 2)
      .attr("text-anchor", "middle")
      .attr("font-size", 18)
      .attr("fill", "#888")
      .text("No data found for this plot.");
    badgeCriteriaNone(id);
    return;
  }

  const metadata_default = {
    title: "Scatter Plot",
    xLabel: "X axis",
    yLabel: "Y axis",
    xUnit: "a.u.",
    yUnit: "a.u.",
  };

  // set the ranges
  const x = d3.scaleLinear().range([0, width]);
  const y = d3.scaleLinear().range([height, 0]);

  // define the line
  const valueline = d3
    .line()
    .x(function (d) {
      return x(d.x);
    })
    .y(function (d) {
      return y(d.y);
    });

  // title
  svg
    .append("text")
    .attr("x", width / 2)
    .attr("y", -margin.top / 3)
    .attr("class", "scatterPlot-title")
    .text(metadata.title ? metadata.title : metadata_default.title);

  // format the data
  data.forEach(function (d) {
    d.x = +d.x;
    d.y = +d.y;
    if (d.xerr !== undefined) d.xerr = +d.xerr;
    if (d.yerr !== undefined) d.yerr = +d.yerr;
  });

  // Determine xMin and xMax
  let xMin, xMax, yMin, yMax;

  xMin = Number.isFinite(metadata.xMin)
    ? metadata.xMin
    : d3.min(data, (d) => (d.xerr !== undefined ? d.x - d.xerr : d.x));

  xMax = Number.isFinite(metadata.xMax)
    ? metadata.xMax
    : d3.max(data, (d) => (d.xerr !== undefined ? d.x + d.xerr : d.x));

  yMin = Number.isFinite(metadata.yMin)
    ? metadata.yMin
    : d3.min(data, (d) => (d.yerr !== undefined ? d.y - d.yerr : d.y));

  yMax = Number.isFinite(metadata.yMax)
    ? metadata.yMax
    : d3.max(data, (d) => (d.yerr !== undefined ? d.y + d.yerr : d.y));

  x.domain([xMin, xMax]);
  y.domain([yMin, yMax]);

  // Add the valueline path.
  svg
    .append("path")
    .data([data])
    .attr("class", "scatterPlot-line ")
    .attr("d", valueline);

  // Add a circle marker for each data point
  svg
    .selectAll(".scatterPlot-point")
    .data(data)
    .enter()
    .append("circle")
    .attr("class", "scatterPlot-point")
    .attr("cx", (d) => x(d.x))
    .attr("cy", (d) => y(d.y))
    .attr("r", 4); // marker radius

  // Add vertical error bars (yerr)
  svg
    .selectAll(".scatterPlot-yerror")
    .data(data.filter((d) => d.yerr !== undefined))
    .enter()
    .append("line")
    .attr("class", "scatterPlot-yerror")
    .attr("x1", (d) => x(d.x))
    .attr("x2", (d) => x(d.x))
    .attr("y1", (d) => y(d.y - d.yerr))
    .attr("y2", (d) => y(d.y + d.yerr));

  // Add horizontal error bars (xerr)
  svg
    .selectAll(".scatterPlot-xerror")
    .data(data.filter((d) => d.xerr !== undefined))
    .enter()
    .append("line")
    .attr("class", "scatterPlot-xerror")
    .attr("y1", (d) => y(d.y))
    .attr("y2", (d) => y(d.y))
    .attr("x1", (d) => x(d.x - d.xerr))
    .attr("x2", (d) => x(d.x + d.xerr))
    .attr("stroke", "#333")
    .attr("stroke-width", 1);

  plotCriteria(svg, width, height, y, metadata, id);

  // Add the X Axis
  let xLabelText;
  if (metadata.xLabel) {
    if (metadata.xUnit) {
      xLabelText = `${metadata.xLabel} [${metadata.xUnit}]`;
    } else {
      xLabelText = metadata.xLabel;
    }
  } else {
    xLabelText = `${metadata_default.xLabel} [${metadata_default.xUnit}]`;
  }

  svg
    .append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x))
    .append("text")
    .attr("y", (margin.bottom * 3) / 4)
    .attr("x", width / 2)
    .attr("class", "scatterPlot-xlabel")
    .attr("fill", "#000")
    .text(xLabelText);

  // Add the Y Axis
  let yLabelText;
  if (metadata.yLabel) {
    if (metadata.yUnit) {
      yLabelText = `${metadata.yLabel} [${metadata.yUnit}]`;
    } else {
      yLabelText = metadata.yLabel;
    }
  } else {
    yLabelText = `${metadata_default.yLabel} [${metadata_default.yUnit}]`;
  }

  svg
    .append("g")
    .call(d3.axisLeft(y))
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", (-margin.left * 2) / 3)
    .attr("class", "scatterPlot-ylabel")
    .attr("fill", "#000")
    .text(yLabelText);
}
