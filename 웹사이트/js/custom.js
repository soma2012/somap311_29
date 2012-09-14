jQuery.noConflict()(function($){
var $container = $('#articles');
		
if($container.length) {
		
		// initialize isotope

     $container.isotope({
      itemSelector : '.block',
      masonry : {
        //columnWidth : 120
        columnWidth : 1,
		gutterWidth: 1,
      },
      masonryHorizontal : {
        rowHeight: 120
      },
      cellsByRow : {
        columnWidth : 240,
        rowHeight : 240
      },
      cellsByColumn : {
        columnWidth : 240,
        rowHeight : 240
      }});
	  
	 
		// filter items when filter link is clicked
		$('#filters button').click(function(){
		  var selector = $(this).attr('data-filter');
		  $container.isotope({ filter: selector,
		  getSortData : function( $elem ) {
            return $elem.attr('article-date');
          }});
		  $(this).removeClass('btn-info').addClass('btn-success').siblings().removeClass('btn-success').addClass('btn-info');
		  return false;
		});
		
}});



