function make_favorites(url_add, url_remove){
  var csrftoken = $.cookie('csrftoken'); //  'Rz5JVkEFtiNpJvNFH3spA9tmk7BfWihx';
  $(function() {
    $('.star').click(function() {
      var id = $(this).attr('object_id');
      var target_model = $(this).attr('target_model');
      var state = $(this).hasClass('favorite');
      console.log(id + target_model + state);
      if (state == true) {
        var url = url_remove;//'{% url 'favs:remove' %}';
      } else if (state == false) {
        var url = url_add;//'{% url 'favs:add' %}';
      }
      console.log($(this).attr("class"));
      $("a[object_id='" +id + "']").toggleClass('favorite');      
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
          console.log(data);
          if (data.status == 'added') { 
            //$(this).toggleClass('favorite');
            console.log('we added');
          } else if (data.data = 'removed') {
            //$(this).toggleClass('favorite');
            console.log('we removed');
          }
        }
      });
    });
  });
};