function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
    console.log('12311231231');
}


$(function () {
    console.log('1231');
    $('.pass_info').submit(function (e) {
        console.log('2222');
        e.preventDefault();
         console.log('221231232');
        var passwd_old = $('#passwd_old').val();
        var passwd_new = $('#passwd_new').val();
        var passwd_new_re = $('#passwd_new_re').val();
        var tip = $('.error_tip');
        if(passwd_old.length<6){
            tip.html('旧密码错误');
            tip.show();
            return
        }
        if(!passwd_new || !passwd_new_re){
            tip.html('请输入新密码');
            tip.show();
            return
        }
        if(passwd_new<6 || passwd_new_re<6){
            tip.html('新密码最少需要6位数');
            tip.show();
            return
        }
        if(passwd_new != passwd_new_re){
            tip.html('新密码不一致');
            tip.show();
            return
        }
        $.post('/user/user_pass_info',{
            'passwd_old':passwd_old,
            'passwd_new':passwd_new,
            'csrf_token':$('#csrf_token').val()
        },function (data) {
            var res = data.res;
            if(res==2){
                tip.html('旧密码错误')
            }else {
                 tip.html('修改成功')
                window.parent.location.href = '/'
            }
            tip.show();
        })
    })
})