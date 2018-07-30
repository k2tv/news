function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault()

        var signature = $("#signature").val()
        var nick_name = $("#nick_name").val()
        var gender = $(".gender:checked").val()

        if (!nick_name) {
            alert('请输入昵称')
            return
        }
        if (!gender) {
            alert('请选择性别')
        }

        // TODO 修改用户信息接口
        $.post('/user/user_base_info',{
            'signature':signature,
            'nick_name':nick_name,
            'gender':gender,
            'csrf_token':$('#csrf_token').val(),
        },function (data) {
            var name = data.nick_name;
            $('.user_center_name',window.parent.document).html(name)
            $('#nick_name',window.parent.document).html(name)
        })
    })
})