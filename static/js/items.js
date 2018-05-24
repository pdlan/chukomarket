var new_item = {
    name: '',
    price: '',
    type: '0',
    will_take_back: 'true',
    sale_self: 'true',
    error: '',
    disable_button: false,
    agree_eula: false
};

var edit_item = {
    name: '',
    price: '',
    type: '0',
    will_take_back: 'true',
    sale_self: 'true',
    error: '',
    disable_button: false
};

var delete_item = {
    id: '',
    error: '',
    disable_button: false
}

function new_item_submit() {
    var post_data = {
        name : new_item.name,
        type : new_item.type,
        sale_self: new_item.sale_self == 'true',
        will_take_back : new_item.will_take_back == 'true',
        price : new_item.price,
    };
    new_item.disable_button = true;
    $.ajax({
        url : '/item',
        type : 'POST',
        data : JSON.stringify(post_data),
        dataType : 'json',
        success: function (data) {
            post_data.id = data.id;
            items.push(post_data);
            $('#modal-new-item').modal('hide');
            new_item.name = '';
            new_item.price = '';
            new_item.type = '0';
            new_item.will_take_back = 'true';
            new_item.sale_self = 'true';
            new_item.error = '';
            new_item.disable_button = false;
            new_item.agree_eula = false;
        },
        error: function (xhr) {
            var data = JSON.parse(xhr.responseText);
            var status = data['status'];
            new_item.error = '提交时发生错误，请稍后再试。';
            new_item.disable_button = false;
        }
    });
}

function edit_item_submit() {
    var post_data = {
        name: edit_item.name,
        type: edit_item.type,
        sale_self: edit_item.sale_self == 'true',
        will_take_back: edit_item.will_take_back == 'true',
        price: edit_item.price
    };
    edit_item.disable_button = true;
    $.ajax({
        url : '/item/' + edit_item.id,
        type : 'PUT',
        data : JSON.stringify(post_data),
        dataType : 'json',
        success: function (data) {
            edit_item.disable_button = false;
            edit_item.error = '';
            for (var i = 0; i < items.length; ++i) {
                if (items[i].id === edit_item.id) {
                    items[i].name = edit_item.name;
                    items[i].price = edit_item.price;
                    items[i].type = edit_item.type;
                    items[i].will_take_back = edit_item.will_take_back;
                    items[i].sale_self = edit_item.sale_self;
                    break;
                }
            }
            $('#modal-edit-item').modal('hide');
        },
        error: function (xhr) {
            var data = JSON.parse(xhr.responseText);
            var status = data.status;
            edit_item.error = '提交时发生错误，请稍后再试。';
            edit_item.disable_button = false;
        }
    });
}

function delete_item_submit() {
    delete_item.disable_button = true;
    $.ajax({
        url : '/item/' + delete_item.id,
        type : 'DELETE',
        success: function (data) {
            delete_item.disable_button = false;
            delete_item.error = '';
            for (var i = 0; i < items.length; ++i) {
                if (items[i].id === delete_item.id) {
                    items.splice(i, 1);
                    break;
                }
            }
            $('#modal-delete-item').modal('hide');
        },
        error: function (xhr) {
            var data = JSON.parse(xhr.responseText);
            var status = data.status;
            delete_item.error = '删除时发生错误，请稍后再试。';
            delete_item.disable_button = false;
        }
    });
}

function on_click_edit(id) {
    for (var i = 0; i < items.length; ++i) {
        if (items[i].id === id) {
            edit_item.id = id;
            edit_item.name = items[i].name;
            edit_item.price = items[i].price;
            edit_item.type = items[i].type;
            edit_item.will_take_back = items[i].will_take_back;
            edit_item.sale_self = items[i].sale_self;
            break;
        }
    }
    $('#modal-edit-item').modal('show');
}

function on_click_delete(id) {
    delete_item.id = id;
    $('#modal-delete-item').modal('show');
}

var app = new Vue({
    el: '#app',
    data: {
        items: items,
        new_item: new_item,
        edit_item: edit_item,
        delete_item: delete_item
    },
    methods : {
        on_click_edit: on_click_edit,
        on_click_delete: on_click_delete,
        new_item_submit: new_item_submit,
        edit_item_submit: edit_item_submit,
        delete_item_submit: delete_item_submit,
        type_name: function(i) {
            return ['书籍', '日用品', '电子设备', '其他'][i]
        }
    }
});