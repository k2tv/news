var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid');
        $('.menu li').each(function () {
            $(this).removeClass('active')
        });
        $(this).addClass('active');

        if (clickCid != currentCid) {
            // TODO 去加载新闻数据
            currentCid = clickCid;
            total_page = 1;
            cur_page = 1;
            updateNewsData(1, clickCid);
        }
    });

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100 && data_querying) {
            // TODO 判断页数，去更新新闻数据
            if (cur_page <= total_page) {
                cur_page++;
                console.log('cur_page'+cur_page)
                updateNewsData(2, currentCid, cur_page);
                data_querying = false;
            }
        }
    });

});

function updateNewsData(isOne, currentCid, cur_page) {
    // TODO 更新新闻数据
        $.get('/get_news_list_other_category', {'category_id': currentCid, 'page': cur_page}, function (data) {
            var list = data.news_list;
            var html_list = '';
            total_page = data.total_page;
            console.log(total_page)
            for (i = 0; i < list.length; i++) {
                html_list += '<li>\n' +
                    '            <a href="/detail/'+list[i].id+'.html" class="news_pic fl"><img src="' + list[i].pic + '" alt="'+ list[i].title + '"></a>\n' +
                    '            <a href="/detail/'+list[i].id+'.html" class="news_title fl">' + list[i].title + '</a>\n' +
                    '            <a href="/detail/'+list[i].id+'.html" class="news_detail fl">' + list[i].summary + '</a>\n' +
                    '            <div class="author_info fl">\n' +
                    '                <div class="author fl">\n' +
                    '                    <img src="../../static/news/images/avatar/' + list[i].avatar + '" width="20px" alt="author">\n' +
                    '                    <a href="/author/'+list[i].user_id+'.html">' + list[i].nick_name + '</a>\n' +
                    '                </div>\n' +
                    '                <div class="time fl">' + list[i].create_time + '</div>\n' +
                    '            </div>\n' +
                    '        </li>'
            }
            if (isOne == 1) {
                $('.list_con').html(html_list);
            } else {
                $('.list_con').append(html_list);
            }
            data_querying = true;
        })
}
