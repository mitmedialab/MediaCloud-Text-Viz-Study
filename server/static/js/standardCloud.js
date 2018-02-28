var generateStandardCloud = function(options, wordList) {
  // calculate absolute position for nice spacing/centering
  var svgWidth = $(options.cloudDomId).width();
  var svgRect = document.getElementById('standard').getBoundingClientRect();

  const allSum = d3.sum(wordList, d => parseInt(d.count, 10));
  wordList.forEach((d, idx) => { wordList[idx].tfnorm = d.count / allSum; });

  var fullExtent = d3.extent(wordList, d => d.tfnorm)
  var colorScale = d3.scaleLinear()
                     .domain(fullExtent)
                     .range([options.minColor, options.maxColor]);

  var fontScale = d3.scaleLinear()
                    .domain(fullExtent)
                    .range([options.minFontSize, options.maxFontSize]);
  // create wordcloud
  d3.layout.cloud()
    .size([svgWidth, options.height])
    .words(wordList)
    .rotate(function(d) { return 0; })
    .random(() => 0.8) // keeps layout the same everytime
    .text(function(d) { return d.text; })
    .font('Arial')
    .fontSize(d => fontScale(d.tfnorm))
    .on('end', (wordsAsData) => {
      d3.select(options.cloudDomId)
        // note: width set inline in viz.html
        .attr('height', options.height)
        .append('g')
        .attr('transform', `translate(${svgRect.x + (svgWidth / 8)}, ${(svgRect.x / 2) + (options.height / 8)})`)
        .selectAll('text')
        .data(wordsAsData)
        .enter()
          .append('text')
            .attr('font-family', 'Lato')
            .attr('id', d => d.text)
            .attr('font-size', d => fontScale(d.tfnorm) + 'px')
            .attr('fill', d => colorScale(d.tfnorm))
            .attr('text-anchor', 'middle')
            .attr('transform', d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
            .text(d => d.text)
            .on('mouseover', function(d) {
              d3.select(this).transition().duration(200)
                             .attr('fill', '#0000ff')
                             .attr('font-weight', 'bold');
              // moves element to front
              d3.select(this).raise();
            })
            .on('mouseout', function(d) {
              // return everything back to normal
              d3.select(this).transition().duration(100)
                             .attr('fill', colorScale(d.tfnorm))
                             .attr('font-weight', 'normal');
            });
    })
    .start();
};
