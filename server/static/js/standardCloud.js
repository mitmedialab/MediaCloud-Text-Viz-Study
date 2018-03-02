var generateStandardCloud = function(options, wordList) {
  // calculate absolute position for nice spacing/centering
  var svgWidth = $(options.cloudDomId).width();
  console.log('svgWidth');
  console.log(svgWidth);
  var svgRect = document.getElementById('standard').getBoundingClientRect();
  console.log('svgRect');
  console.log(svgRect);

  const allSum = d3.sum(wordList, function(d) { return parseInt(d.count, 10) });
  wordList.forEach(function(d, idx) { wordList[idx].tfnorm = d.count / allSum; });

  var fullExtent = d3.extent(wordList, function(d) { return d.tfnorm })
  var colorScale = d3.scaleLinear()
                     .domain(fullExtent)
                     .range([options.minColor, options.maxColor]);

  var fontScale = d3.scaleLinear()
                    .domain(fullExtent)
                    .range([options.minFontSize, options.maxFontSize]);
  var translationString = 'translate(' + (svgRect.left + (svgWidth / 8)) + ',' + ((svgRect.left / 2) + (options.height / 8)) + ')';
  console.log(svgRect.left);
  console.log(svgRect.x);
  console.log(svgWidth);
  console.log(options.height);
  console.log(translationString);
  // create wordcloud
  d3.layout.cloud()
    .size([svgWidth, options.height])
    .words(wordList)
    .rotate(function(d) { return 0; })
    .random(function() { return 0.8; }) // keeps layout the same everytime
    .text(function(d) { return d.text; })
    .font('Arial')
    .fontSize(function(d) { return fontScale(d.tfnorm) })
    .on('end', function(wordsAsData) {
      d3.select(options.cloudDomId)
        // note: width set inline in viz.html
        .attr('height', options.height)
        .append('g')
        // for some reason the translation here is not happening...
        .attr('transform', translationString)
        // .attr('transform', `translate(${svgRect.x + (svgWidth / 8)}, ${(svgRect.x / 2) + (options.height / 8)})`)
        .selectAll('text')
        .data(wordsAsData)
        .enter()
          .append('text')
            .attr('font-family', 'Lato')
            .attr('id', function(d) { return d.text })
            .attr('font-size', function(d) { return fontScale(d.tfnorm) + 'px' })
            .attr('fill', function(d) { return colorScale(d.tfnorm) })
            .attr('text-anchor', 'middle')
            .attr('transform', function(d) { return 'translate(' + d.x + ', ' + d.y + ')rotate(' + d.rotate + ')'; })
            .text(function(d) { return d.text })
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
