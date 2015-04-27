function make_favorites(url_add, url_remove){
  var csrftoken = $.cookie('csrftoken');
  $(function() {
    $('.star').click(function() {
      var id = $(this).attr('object_id');
      var target_model = $(this).attr('target_model');
      var state = $(this).hasClass('favorite');
      // console.log(id + target_model + state);
      if (state === true) {
        var url = url_remove;
      } else if (state === false) {
        var url = url_add;
      }
      $("a[object_id='" +id + "'][target_model='" + target_model + "']").toggleClass('favorite');
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
