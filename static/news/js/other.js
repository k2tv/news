// 解析url中的查询字符串
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

// news_collect
$(function(){

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
    })

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
    })

})
