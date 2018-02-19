var generateWord2vecCloud = function(options, wordList) {
  const COS_SIM_THRESHOLD = 0.95;
  const MOUSEOVER_TRANSITION_TIME = 400;
  const svgContainerHeight = options.height;

  var svgContainerWidth = $('#svg-container').width();

  // add in tf normalization
  const allSum = d3.sum(wordList, d => parseInt(d.count, 10));
  wordList.forEach((d, idx) => { wordList[idx].tfnorm = d.count / allSum; });

  // scales
  var fullExtent = d3.extent(wordList, d => d.tfnorm)
  var colorScale = d3.scaleLinear()
                     .domain(fullExtent)
                     .range([options.minColor, options.maxColor]);
  var fontScale = d3.scaleLinear()
                    .domain(fullExtent)
                    .range([options.minFontSize, options.maxFontSize]);

  const margin = 75;

  // NOTE: probs a neater way to do this...
  const minX = d3.min(wordList, d => d[options.xProperty]);
  const minY = d3.min(wordList, d => d[options.yProperty]);
  const maxX = d3.max(wordList, d => d[options.xProperty]);
  const maxY = d3.max(wordList, d => d[options.yProperty]);
  const globalMaxAbs = Math.max(Math.abs(Math.max(minX, minY)), Math.abs(Math.max(maxX, maxY)));

  // make scales completely symmetric and centered around 0
  const xScale = d3.scaleLinear()
    .domain([-globalMaxAbs, globalMaxAbs])
    .range([margin, options.width - margin]);
  const yScale = d3.scaleLinear()
    .domain([-globalMaxAbs, globalMaxAbs])
    .range([options.height - margin, margin]);

  var centerOffsetX = (svgContainerWidth / 2) - xScale(0);
  var centerOffsetY = (yScale(0) - (svgContainerHeight / 2));

  // create cloud
  d3.select(options.cloudDomId)
    .attr('width', options.width)
    .attr('height', options.height)
    .attr('transform', `translate(${centerOffsetX},${-centerOffsetY})`);

  // draw circle
  var circle = d3.arc()
      .innerRadius(0)
      .outerRadius(xScale(globalMaxAbs)*.55)
      .startAngle(0)
      .endAngle(2*Math.PI);
  d3.select(options.cloudDomId).append("path")
      .attr('d', circle)
      .attr('fill', '#f9f9f9')
      .attr('transform', `translate(${xScale(0)},${yScale(0)})`);

  // draw arc 'tooltip'
  var arc = d3.arc()
    .innerRadius(0)
    .outerRadius(xScale(globalMaxAbs)*.55)
    .startAngle(0)
    .endAngle(Math.acos(COS_SIM_THRESHOLD) * 2);
  d3.select(options.cloudDomId).append("path")
    .attr('d', arc)
    .attr('id', 'arc')
    .attr('fill', '#efefef')
    .attr('transform', `translate(${xScale(0)},${yScale(0)})`)
    .style('opacity', 0);

  // Add circle at origin
  d3.select(options.cloudDomId).append('circle')
    .attr("cx", xScale(0))
    .attr("cy", yScale(0))
    .attr("r", 5)
    .style("fill", 'black');

  // axis lines for visual debugging
  // d3.select(options.cloudDomId).append('svg:line')
  //   .attr('x1', xScale(0))
  //   .attr('y1', yScale(0))
  //   .attr('x2', xScale(0))
  //   .attr('y2', yScale(globalMaxAbs))
  //   .style('stroke', '#cfcfd1');
  // d3.select(options.cloudDomId).append('svg:line')
  //   .attr('x1', xScale(0))
  //   .attr('y1', yScale(0))
  //   .attr('x2', xScale(globalMaxAbs))
  //   .attr('y2', yScale(0))
  //   .style('stroke', '#cfcfd1');
  // d3.select(options.cloudDomId).append('svg:line')
  //   .attr('x1', xScale(0))
  //   .attr('y1', yScale(0))
  //   .attr('x2', xScale(0))
  //   .attr('y2', yScale(-globalMaxAbs))
  //   .style('stroke', '#cfcfd1');
  //   d3.select(options.cloudDomId).append('svg:line')
  //     .attr('x1', xScale(0))
  //     .attr('y1', yScale(0))
  //     .attr('x2', xScale(-globalMaxAbs))
  //     .attr('y2', yScale(0))
  //     .style('stroke', '#cfcfd1');

  // Add Text Labels
  const sizeRange = { min: options.minFontSize, max: options.maxFontSize };

  const sortedWords = wordList.sort((a, b) => a.count - b.count); // important to sort so z order is right

  const text = d3.select(options.cloudDomId).selectAll('text')
    .data(sortedWords)
    .enter()
      .append('text')
        .attr('text-anchor', 'middle')
        .text(d => d.text)
        .attr('font-family', 'Lato')
        .attr('id', d => d.text)
        .attr('x', d => xScale(d[options.xProperty]))
        .attr('y', d => yScale(d[options.yProperty]))
        .attr('fill', d => colorScale(d.tfnorm))
        .attr('font-size', (d) => {
          //const fs = fontSizeComputer(d, fullExtent, sizeRange);
          return `${fontScale(d.tfnorm)}px`;
        })
        .on('mouseover', function(d) {
          /* rotate and show arc tooltip */
          // calculate angle from (x, y) coordinates
          var offset = Math.acos(COS_SIM_THRESHOLD) * (180 / Math.PI);
          var currentAngle = Math.atan(Math.abs(d[options.yProperty] / d[options.xProperty])) * (180 / Math.PI);
          // 1st quadrant
          if (d[options.xProperty] > 0 && d[options.yProperty] > 0) {
            currentAngle = 90. - currentAngle - offset;
          }
          // second quadrant
          else if (d[options.xProperty] > 0 && d[options.yProperty] < 0) {
            currentAngle = 90. + currentAngle - offset;
          }
          // third quadrant
          else if (d[options.xProperty] < 0 && d[options.yProperty] < 0) {
            currentAngle = -90. - currentAngle - offset;
          }
          // fourth quadrant
          else if (d[options.xProperty] < 0 && d[options.yProperty] > 0) {
            currentAngle = -90. + currentAngle - offset;
          }
          d3.select('#arc')
            .attr('transform', `translate(${xScale(0)},${yScale(0)}) rotate(${currentAngle})`);
          d3.select('#arc')//.transition().duration(MOUSEOVER_TRANSITION_TIME)
            .style('opacity', 1);

          d3.select(this).transition().duration(MOUSEOVER_TRANSITION_TIME)
                         .attr('fill', '#0000ff')
                         .attr('font-size', fontScale(d.tfnorm))
                         .attr('font-weight', 'bold');
          // moves element to front
          d3.select(this).raise();

          // word vector line for debugging
          // d3.select(options.cloudDomId).append('svg:line')
          //   .attr('id', `${d.text}-line`)
          //   .attr('x1', xScale(0))
          //   .attr('y1', yScale(0))
          //   .attr('x2', xScale(d[options.xProperty]))
          //   .attr('y2', yScale(d[options.yProperty]))
          //   .style('stroke', '#cfcfd1')

          // different color scale for every corresponding similarity list
          var simColorScale = d3.scaleLinear()
                                .domain([COS_SIM_THRESHOLD, 1.0])
                                .range(['#acb5f9', '#0000ff']);
          wordList.forEach(function(word) {
            var sim = d.similar.find(x => x.text === word.text);
            if (sim && sim.text !== d.text) {
              // highlight similar words
              d3.select(`#${word.text}`).transition().duration(MOUSEOVER_TRANSITION_TIME)
                                        .attr('fill', simColorScale(sim.score))
                                        .attr('font-size', fontScale(word.tfnorm))
                                        .attr('font-weight', 'bold')
                                        .attr('pointer-events', 'none');
              // moves element to front
              d3.select(`#${word.text}`).raise();
              // d3.select(options.cloudDomId)
              //   .append('svg:line')
              //   .attr('id', `${word.text}-line`)
              //   .attr('x1', xScale(0))
              //   .attr('y1', yScale(0))
              //   .attr('x2', xScale(word[options.xProperty]))
              //   .attr('y2', yScale(word[options.yProperty]))
              //   .style('stroke', '#cfcfd1')
            } else {
              // fade out all other words
              if (word.text !== d.text) {
                d3.select(`#${word.text}`).transition().duration(MOUSEOVER_TRANSITION_TIME)
                                          .attr('fill', '#e2e2e2')
                                          .attr('pointer-events', 'none');
              }
            }
          });
        })
        .on('mouseout', function(d) {
          //reset and hide arc tooltip
          d3.select('#arc')
            .style('opacity', 0)
            .attr('transform', `translate(${xScale(0)},${yScale(0)}) rotate(${0})`);

          // return everything back to normal
          wordList.forEach(function(word) {
            d3.select(`#${word.text}`).transition().duration(100)
              .attr('fill', colorScale(word.tfnorm))
              .attr('font-size', fontScale(word.tfnorm))
              .attr('font-weight', 'normal')
              .attr('pointer-events', 'auto');
          });
        });
};
