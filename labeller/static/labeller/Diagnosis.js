class Diagnosis { 
	constructor(name, abbreviation) {
		this.name = name;
		this.abbreviation = abbreviation;
	}




	asString() {
		return (`${this.name} (${this.abbreviation})`)	
	}

	isDiagnosisChoiseEquivalent(choice_name) {
		if (this.asString() == choice_name || 
			this.asString().replaceAll(' ', '%20') == choice_name) {
			return true;
		}
		else {
			return false;
		}
	}

	static getNameFromChosenDiagnosis(chosen_diagnosis){
		return chosen_diagnosis.substr(0, chosen_diagnosis.indexOf('(')-1)
	}

	
	// static getAbbreviationFromChosenDiagnosis(chosen_diagnosis){
	// 	return chosen_diagnosis.substr(chosen_diagnosis.indexOf('(')+1, chosen_diagnosis.indexOf(')'))
	// }
	static getSlideDiangosisDiv(slide_pk, dx_pk, dx_text){
		var newDiv = `<div class="p-2 diagnosis_div_slide_${slide_pk}" id="diagnosis_div_${slide_pk}_${dx_pk}">`
		newDiv += dx_text 
		newDiv += '<button id="delete_diagnosis_'+slide_pk+'_'+dx_pk+'" class="'+ slide_pk + ' ' + dx_pk + ' btn p-0">'
		newDiv += '<i class="bi-trash"></i> </button></div>'
		return newDiv;
	}


	static addDiagnosisToSlideAJAX(slide_pk, diagnosis_pk, dx_text) {
		// var diagnosis = new Diagnosis(chosen_diagnosis)
		$.post("/add_diagnosis_to_slide/", {'slide_pk': slide_pk, 'diagnosis_pk': diagnosis_pk},
			function(json){
				if(json['success']==true) {
					if( $(`.diagnosis_div_slide_${slide_pk}`).length ==0 ) {
						$('#dx_title_'+slide_pk).html('<b>Diagnoses:</b> ');
					}
					$('#slide_info_row_'+slide_pk).append(Diagnosis.getSlideDiangosisDiv(slide_pk, diagnosis_pk, dx_text))
					$('#delete_diagnosis_'+slide_pk+'_'+dx_pk).on('click', Diagnosis.removeDiagnosisFromSlideClickHandler);	
				}	  
				// TO DO Add functionality to delete a diagnosis
				
		});
	}


	static removeDiagnosisFromSlideClickHandler(e) {
		// console.log('delete clicked!')
		var classes_as_array = this.classList.value.split(' ');
		var slide_pk = classes_as_array[0];
		var diagnosis_pk = classes_as_array[1]; 
		Diagnosis.removeDiagnosisFromSlideAJAX(diagnosis_pk, slide_pk)
		
	}						

	static removeDiagnosisFromSlideAJAX(diagnosis_pk, slide_pk) {
		$.post("/remove_diagnosis_from_slide/", {'slide_pk': slide_pk, 'diagnosis_pk': diagnosis_pk},
			function(json){
				if(json['success']==true) {
					$('#diagnosis_div_'+slide_pk+'_'+diagnosis_pk).remove();
					if( $(`.diagnosis_div_slide_${slide_pk}`).length ==0 ) {
						$('#dx_title_'+slide_pk).text('Diagnosis: None');
					}
				}
		});
	}


	// ******************** Add Notes *******************

	static getSlideNoteDiv(slide_sid, note_text) {
		var noteDiv = `<div class="p-2 note_div_slide_${slide_sid}" id="note_div_${slide_sid}">`;
		noteDiv += note_text;
		noteDiv += '<button id="delete_note_'+slide_sid+'" class="'+slide_sid+' ' +'btn p-0">';
		noteDiv += '<i class="bi-trash"></i></button></div>';
		return noteDiv;
	}

	static addNoteToSlideAJAX(slide_sid, slide_note) {
		console.log('entering ADDNOTETOSLIDEAJAX');
		$.post("/add_note_to_slide/", {'slide_sid': slide_sid}, function(json) {

			if(json['success'] == true) {

				$('#slide_notes_row_'+slide_sid).append(Diagnosis.getSlideNoteDiv(slide_sid, slide_note));
				// Aboce ID Does note exist. Also - because there can only be 1 note per slide - this makes even LESS sense....
				
				$('#delete_note_'+slide_sid).on('click', Diagnosis.removeNoteFromSlideClickHandler);
			};
		});
	};

	// static removeNoteFromSlideClickHandler(e) {
	// 	var classes_as_array = this.classList.value.split(' ');
	// 	var slide_pk = classes_as_array[0];
	// 	Diagnosis.removeNoteFromSlideClickHandler(slide_pk);
	// };

}