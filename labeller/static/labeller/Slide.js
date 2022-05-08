class Slide { 

	constructor(slide_pk) {
		this.pk = String(slide_pk);
	}

	static getNewULForSlide(id, sid, slide_name){

	}

	static getULForSlide(id, sid, slide_name) {
		var cellSummary = new CellSummary('sid', sid);
		//$('#slide_info_row').append(cellSummary.getULForSlide());
	
		var slide_path = '/label_slide/'+sid+ '/';
		var ul = '<ul id="slide_list_' + sid + '" class="slide_list slide_list_box">';
		ul = ul + '<li class="slide_id">ID: '+ id +'</li>';
		ul = ul + '<li class="slide_sid">SID: '+ sid +'</li>';
		ul = ul + '<li class="label_btn"><a class="slide_label_btn" href= "'+ slide_path+'">Label</a></li>';
		ul = ul + '<li class="slide_name" id="slide_name_' +sid+ '">Name: ' +slide_name+ '</li>';
		ul = ul + '<li><button type="button" id="slide_info_'+sid+'" class="slide_info">Info</li>';
		ul = ul + '<li id="cell_total_'+sid+'"></li></ul>';
		//ul = ul + '<div id="bigtable_' +sid+ '" class="bigtable">' +createBigTable(sid)+ '</div>';
		ul = ul + '<div id="bigtable_' +sid+ '" class="bigtable">' +cellSummary.createBigTable(sid)+ '</div>';
		//ul = ul + '<li class="slide_label_btn" id="slide"'+sid+'">Show Slide Info</li></ul>';
		return ul;
	}
	
	static infoButtonOnClick(sid) {

		$('#slide_info_'+sid).on('click', function() {
		  var $this = $(this);
		  var sid = $(this).attr('id').slice('slide_info_'.length);
	
		  if ($this.hasClass("clicked_once")) {
			$this.removeClass("clicked_once");
			// $this.removeClass('slide_info_down');
			$('#bigtable_' +sid).slideUp().removeClass("bigtable_box");
			$('#slide_list_' +sid).addClass('slide_list_box');
			$('#cell_total_'+sid).fadeOut();
	
		  } else {
	
			$.get('/get_all_cells_in_slide/', {'sid':sid}, function(json) { 
	
			  console.log('lets get them cells!');
			  //console.log(json);
			  //console.log(json['all_cells_json']);
			  
			  var cells_json_reformat = $.parseJSON(json['cells_json'].replace(/&quot;/ig,'"'));
			  $this.addClass("clicked_once");
			//   $this.addClass('slide_info_down');
			  $('#slide_list_' +sid).removeClass("slide_list_box");
			  $('#bigtable_' +sid).slideDown().addClass("bigtable_box");
			  $('#cell_total_'+sid).html('Total: ' + cells_json_reformat.length).fadeIn();
	
			  Slide.UpdateCountsOnPage(json['cells_json'], json['celltypes_json'], sid);
	
			});      
		  };
		});
	}

	static UpdateCountsOnPage(cells_json, celltypes_json, sid) {
		// var cells_json_reformat = $.parseJSON(cells_json.replace(/&quot;/ig, '"'));
		var cells = Cell.LoadCellsFromJson(cells_json, celltypes_json);
		var counts = CellCounter.countCells(cells);
		console.log('counts', counts)

		for (var key in Cell.classLabelDict) {
			CellCounter.replaceOldCountWithNewCount(`.class_table_td.count_${key}.${sid}`, counts[key]);
		};
	};
}	