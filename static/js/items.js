function new_item_submit() {
    var name = $('#new-name').val();
    var price = $('#new-price').val();
    var type = $('#new-type').val();
    var sale_self = true;
    var will_take_back = true;
    if ($('#new-sale-self-no').prop('checked')) {
        sale_self = false;
    }
    if ($('#new-take-back-no').prop('checked')) {
        will_take_back = false;
    }
    var post_data = {
        'name' : name,
        'type' : parseInt(type),
        'sale_self' : sale_self,
        'will_take_back' : will_take_back,
        'price' : price
    };
    $('#new-item-submit').prop('disabled', true);
    $.ajax({
        url : '/item',
        type : 'POST',
        data : JSON.stringify(post_data),
        dataType : 'json',
        success: function (data) {
            $('#new-item-submit').prop('disabled', false);
            $('#new-error').hide();
            window.location.href = '/items';
        },
        error: function (xhr) {
            var data = JSON.parse(xhr.responseText);
            var status = data['status'];
            $('#new-error').html('提交时发生错误，请稍后再试。');
            $('#new-error').show();
            $('#new-item-submit').prop('disabled', false);
        }
    });
    return false;
}

$(document).ready(function () {
    $('#form-new-item').submit(new_item_submit);
});