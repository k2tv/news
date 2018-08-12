function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    // 关注当前新闻作者
    $(".focus").click(function () {
        $.post('/follow',{
            'author_id':$('#author_id').val(),
            'csrf_token':$('#csrf_token').val()
        },function (data) {
            if(data.result==3){
                $('.focus').hide();
                $('.focused').show();
            }
        });
    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {
        $.post('/follow',{
            'author_id':$('#author_id').val(),
            'csrf_token':$('#csrf_token').val()
        },function (data) {
            if(data.result==3){
                $('.focus').show();
                $('.focused').hide();
            }
        });
    });
});