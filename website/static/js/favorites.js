function make_favorites(url_add, url_remove){
	var csrftoken = $.cookie('csrftoken');
	$(function() {
		$('.fa').click(function() {
			var id = $(this).attr('object_id');
			var target_model = $(this).attr('target_model');
			var state = $(this).hasClass('fa-star');
			// console.log(id + target_model + state);
			if (state === true) {
				var url = url_remove;
			} else if (state === false) {
				var url = url_add;
			}
			if (state){
				$("a[object_id='" +id + "'][target_model='" + target_model + "']").removeClass('fa-star');
				$("a[object_id='" +id + "'][target_model='" + target_model + "']").addClass('fa-star-o');
			} else {
				$("a[object_id='" +id + "'][target_model='" + target_model + "']").removeClass('fa-star-o');
				$("a[object_id='" +id + "'][target_model='" + target_model + "']").addClass('fa-star');
			}
			// TODO move this to Jquery ?
			$.ajax({
				url: url,
				type: 'post',
				data : {
					target_model : target_model,
					target_object_id: id,
					csrfmiddlewaretoken :  csrftoken
				},
				dataType: 'json',
				success : function(data) {
				}
			});
		});
	});
}
