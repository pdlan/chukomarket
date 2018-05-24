function recv_submit() {
    var id = $('#id-recv').val();
    var post_data = {
        id: parseInt(id),
        action: 'receive'
    };
    $.ajax({
        url : '/admin',
        type : 'POST',
        data : JSON.stringify(post_data),
        dataType : 'json',
        success: function (data) {
            alert('接收成功');
            $('#id-recv').val('');
        },
        error: function (xhr) {
            alert('接收失败');
        }
    });
    return false;
}

function checkout_submit() {
    var id = $('#id-checkout').val();
    var post_data = {
        id: parseInt(id),
        action: 'checkout'
    };
    $.ajax({
        url : '/admin',
        type : 'POST',
        data : JSON.stringify(post_data),
        dataType : 'json',
        success: function (data) {
            alert('结账成功');
            $('#id-checkout').val('');
        },
        error: function (xhr) {
            alert('结账失败');
        }
    });
    return false;
}

$(document).ready(function () {
    $('#form-recv').submit(recv_submit);
    $('#form-checkout').submit(checkout_submit);
});