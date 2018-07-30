function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $('.pic_info').submit(function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            url:'/user/user_pic_info',
            type:'post',
            dataType:'json',
            success:function (data) {
                // var res = data.res;
                window.parent.location.href = '/user/'
            }
        });
    });

});