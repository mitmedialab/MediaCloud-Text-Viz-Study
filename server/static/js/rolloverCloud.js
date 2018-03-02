var generateRolloverCloud = function(options, wordList) {
  const COS_SIM_THRESHOLD = 0.95;

  // calculate absolute position for nice spacing/centering
  var svgWidth = $(options.cloudDomId).width();
  var svgRect = document.getElementById('rollover').getBoundingClientRect();

  // add in tf normalization
  const allSum = d3.sum(wordList, function(d) { return parseInt(d.count, 10); });
  wordList.forEach(function(d, idx) { wordList[idx].tfnorm = d.count / allSum; });

  var fullExtent = d3.extent(wordList, function(d) { return d.tfnorm; })
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
    .padding(1)
    .rotate(function() { return 0; })
    .random(function() { return 0.8; }) // keeps layout the same everytime
    .text(function(d) { return d.text; })
    .font('Arial')
    .fontSize(function(d) { return fontScale(d.tfnorm); })
    .on('end', function(wordsAsData) {
      d3.select(options.cloudDomId)
        // note: width set inline in viz.html
        .attr('height', options.height)
        .append('g')
        .attr('transform', 'translate(' + (svgRect.x + (svgWidth / 8)) + ', ' + ((svgRect.x / 2) + (options.height / 8)) + ')')
        // .attr('transform', `translate(${svgRect.x + (svgWidth / 8)}, ${(svgRect.x / 2) + (options.height / 8)})`)
        .selectAll('text')
        .data(wordsAsData)
        .enter()
          .append('text')
            .attr('font-family', 'Lato')
            .attr('id', function(d) { return d.text; })
            .attr('font-size', function(d) { return fontScale(d.tfnorm) + 'px'; })
            .attr('fill', function(d) { return colorScale(d.tfnorm); })
            .attr('text-anchor', 'middle')
            .attr('transform', function(d) { return 'translate(' + d.x + ', ' + d.y + ')rotate(' + d.rotate + ')'; })
            .text(function(d) { return d.text; })
            .on('mouseover', function(d) {
              d3.select(this).transition().duration(200)
                             .attr('fill', '#0000ff')
                             .attr('font-size', fontScale(d.tfnorm)*1.5)
                             .attr('font-weight', 'bold');
              d3.select(this).raise();

              // different color scale for every corresponding similarity list
              var simColorScale = d3.scaleLinear()
                                    .domain([COS_SIM_THRESHOLD, 1.0])
                                    .range(['#acb5f9', '#0000ff']);

              wordList.forEach(function(word) {
                var sim = d.similar.find(function(x) { return x.text === word.text; });
                if (sim) {
                  // highlight similar words
                  d3.select('#' + word.text).transition().duration(200)
                                            .attr('fill', simColorScale(sim.score))
                                            .attr('font-size', fontScale(word.tfnorm) * 1.5)
                                            .attr('font-weight', 'bold')
                                            .attr('pointer-events', 'none');
                  // moves element to front
                  d3.select('#' + word.text).raise();
                } else {
                  // fade out all other words
                  if (word.text !== d.text) {
                    d3.select('#' + word.text).transition().duration(200)
                                              .attr('fill', '#cecece')
                                              .attr('font-size', fontScale(word.tfnorm))
                                              .attr('pointer-events', 'none');
                  }
                }
              });
            })
            .on('mouseout', function(d) {
              // return everything back to normal
              wordList.forEach(function(word) {
                d3.select('#' + word.text).transition().duration(100)
                                          .attr('fill', colorScale(word.tfnorm))
                                          .attr('font-size', fontScale(word.tfnorm))
                                          .attr('font-weight', 'normal')
                                          .attr('pointer-events', 'auto');
              });
            });
    })
    .start();
};
