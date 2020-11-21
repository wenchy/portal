/*
 *   File name: pro_index.js
 *  Created on: 2017-02-10
 * Modified on:
 *      Author: wenchyzhu
 *     Version: v0.1
 *       Brief: LuckyFish后台测试工具Pro版
 *
 */
$(document).ready(function() {
    // 广告通知栏5秒后自动消失
    // setTimeout('$("div.advertisement").hide("slow")', 5000);

    //popover
    $('[data-toggle="popover"]').popover()

    // tooltip
    $(function() {
        $('[data-toggle="tooltip"]').tooltip()
    })
});

/**************************************************************/
/************************ 以下为自定义函数 ********************/
/**************************************************************/

// autocomplete
function InitTypeaHead() {
    var search_keys = new Array();
    var i = 0;
    $("div.item .panel-title").each(function() {
        search_keys[i++] = $(this).text();
    });
    $(":input[name='search_input']").typeahead({
        hint: true,
        source: search_keys,
        /*本地数据*/
        items: 10,
        highlight: true,
        minLength: 1,
        afterSelect: function() {
            $("#fuzzy-search").submit();
        }
    });
}

// Fuzzy Search (简单的模糊搜索)
// 参考: https://github.com/bevacqua/fuzzysearch/blob/master/index.js
function FuzzySearch(needle, haystack) {
    var hlen = haystack.length;
    var nlen = needle.length;
    if (nlen > hlen) {
        return false;
    }
    if (nlen === hlen) {
        return needle === haystack;
    }
    outer: for (var i = 0, j = 0; i < nlen; i++) {
        var nch = needle.charCodeAt(i);
        while (j < hlen) {
            if (haystack.charCodeAt(j++) === nch) {
                continue outer;
            }
        }
        return false;
    }
    return true;
}