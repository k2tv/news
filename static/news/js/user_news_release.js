function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    $(".release_form").submit(function (e) {
        e.preventDefault();
        var tip = $('.error_tip2');
        if($('#title').val().length<=0){
            tip.html('标题不能为空');
            tip.show();
            return
        }
        if($('#summary').val().length<=0){
            tip.html('摘要不能为空');
            tip.show();
            return
        }

        if(tinymce.activeEditor.getContent().length<=0){
            tip.html('内容不能为空');
            tip.show();
            return
        }else {
            if($('#rich_content').val().length<=0){
            tip.html('确认提交？提交后无法修改');
            tip.show();
            return
        }
        }

        $(this).ajaxSubmit({
            url:'/user/user_news_release',
            type:'post',
            dataType:'json',
            success:function (data) {
                // TODO 发布完毕之后需要选中我的发布新闻
                // 选中索引为6的左边单菜单
                window.parent.fnChangeMenu(6);
                // 滚动到顶部
                window.parent.scrollTo(0, 0)
            }
        })
    })
});