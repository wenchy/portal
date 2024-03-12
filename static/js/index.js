$(document).ready(function () {
    var cur_env_id = window.location.pathname.split("/")[1];
    // refresh page at five clock on everyday.
    setInterval(function () {
        var now = moment();
        if (now.hour() == 5) {
            location.reload(true);
        }
    }, 30 * 60 * 1000);

    var ad_visible = false;
    if (moment().isBefore('2018-06-01 01:00:00', 'day') || cur_env_id == "idc") {
        $("div.advertisement").removeClass("hidden");
        ad_visible = true;
    }
    if (ad_visible) {
        $("div.advertisement").fadeIn("slow").delay(10 * 1000).fadeOut("slow");
    }

    UpdateUidDatalist();

    // $(".pinned").pin();
    // popover
    $('[data-toggle="popover"]').popover()

    // offcanvas
    $('[data-toggle="offcanvas"]').click(function () {
        $('.row-offcanvas').toggleClass('active')
    });

    // tooltip
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

    // Cascading grid layout
    var $container = $('.masonry-container');
    $container.imagesLoaded(function () {
        $container.masonry({
            columnWidth: '.item',
            itemSelector: '.item'
        });
        // // 等待masonry初始化完后
        // // 初始时就刷新最近最常使用(MRU)的功能卡片
        // MRURefresh()
    });

    // Reinitialize masonry inside each panel after the relative tab link is clicked -
    $('a[data-toggle=tab]').each(function () {
        var $this = $(this);
        $this.on('shown.bs.tab', function () {
            $container.imagesLoaded(function () {
                $container.masonry({
                    columnWidth: '.item',
                    itemSelector: '.item'
                });
            });

        }); //end shown
    }); //end each

    // Firstly Update Date Range Picker
    UpdateTimePicker();
    // auto uin, 自动填写号码
    AutoUin();
    // 初始化typeahead, 搜索自动补全autocomplete
    InitTypeaHead();
    // 初始化jsoneditor
    var jsoneditor_options = {
        mode: 'tree',
        modes: ['code', 'form', 'text', 'tree', 'view'], // allowed modes
    };
    var jsoneditorDict = {}
    $("div.jsoneditor").each(function () {
        // jsoneditor need convert jQuery object to JavaScript object
        jsoneditorDict[$(this).attr("id")] = new JSONEditor($(this).get(0), jsoneditor_options);
    });

    // 功能卡片模糊搜索
    $("form#fuzzy-search").submit(function (e) {
        // // First: clear search result html
        // $("div#search_result>div.row").html('');
        // var search_input = $.trim($(this).find(":input[name='search_input']").val());
        // $(".original-card-tabpanel div.item .panel-title").each(function() {
        //     if (FuzzySearch(search_input, $(this).text())) {
        //         $("div#search_result div.masonry-container").append($(this).parents("div.item").prop("outerHTML"));
        //     }
        // });
        // $("div#search_result div.masonry-container>div.item").each(function() {
        //     $(this).attr("style", '');
        // });
        // // tab: trigger click, 切换到"搜索结果"tab
        // $("#search-tab").click();
        // $("div#search_result div.masonry-container").masonry('reloadItems');
        // $("div#search_result div.masonry-container").masonry('layout');

        // UpdateTimePicker();

        $("div.item .panel-title").each(function () {
            $card = $(this).parents("div.panel");
            if ($(this).text().trim() == $("form#fuzzy-search").find(":input[name='search_input']").val().trim()) {
                var tab_id = $(this).parents("div.tab-pane").attr("id");
                console.log("fuzzysearch： " + tab_id);
                $("div#sidebar a." + tab_id).click();
                $('html, body').animate({
                    scrollTop: $(this).offset().top - 70 // substract top fixed navigation height（70px）
                }, 100);
                // set
                $card.find("div.panel-heading").css({ "background-color": "#b40703", "border-color": "#b40703" });
                $card.fadeOut("slow")
                    .fadeIn("slow")
                    .delay(10000) // delay 10 seconds
                    .queue(function (next) {
                        $(this).find("div.panel-heading").css({ "background-color": "#337ab7", "border-color": "#337ab7" });
                        console.log("fuzzysearch: reset card head background-color");
                        next();
                    });
                return;
            }
        });

        console.log("fuzzysearch done.");
        return false;
    });

    // 通用表单提交处理: ajax
    $("#tab_body").on("submit", "form", function () {
        var formTarget = $(this).attr("target");
        if (formTarget == "_blank") {
            $(this).submit();
            return;
        }

        var isBatchProcess = $("#batchProcessForm #batchProcessCheck").is(':checked')
        var popup = $(this).attr("popup");
        var title = $(this).parent().siblings(".panel-heading").children(".panel-title").text().trim();
        var operation = $(this).data('operation');
        if (operation == undefined) {
            operation = "提交";
        } else {
            operation = operation.trim().replace(" ", "");
        }
        var operation_desc = "[" + operation + "]" + title;
        var batchProcessConfirm = ""
        var batchProcessTip = ""
        if (isBatchProcess) {
            batchProcessConfirm = '(批量处理)'
            batchProcessTip = '<font color="PURPLE"><b>(批量处理)</b></font>'
            popup = "confirm"
        }
        switch (popup) {
            case "confirm":
                if (!confirm('您确定' + batchProcessConfirm + '：' + operation_desc + '？')) {
                    console.log("form submit canceled: " + title);
                    return false;
                }
                break;

            case "alert":
                alert('注意！您将执行操作: ' + operation_desc + '！')
                break;

            case "prompt":
                let env_id = prompt('注意！您将执行操作：' + operation_desc + '！\n请输入当前环境ID：', "")
                if (env_id == null) {
                    console.log("user cancel prompt: " + operation_desc);
                    return false;
                } else {
                    if (env_id != cur_env_id) {
                        alert('输入错误！当前环境ID是：' + cur_env_id)
                        return false;
                    }
                }
                break;

            default:
                console.log("unknown popup: " + popup);
                break;
        }
        var httpUrl = $(this).attr("action");
        var httpMethod = $(this).attr("method");

        var last_response_len = false;
        var $result_panel = $("#commonResultPanel pre");
        var $log_panel = $('#commonResultModal pre')
        var jsoneditor;
        var $jsoneditors = $(this).parents("div.tab-pane").find("div.jsoneditor");
        var isEditorForm = false;
        if ($jsoneditors.length > 0) {
            // 如果有jsoneditor，则进行如下处理
            jsoneditor = jsoneditorDict[$jsoneditors.attr("id")];
            console.log("before jsoneditor-content: " + $jsoneditors.attr("id") + ", content: " + jsoneditor.getText())
            // 加入jsoneditor的content参数
            $(this).find(":input[name='_jsoneditor_content']").val(jsoneditor.getText());
            isEditorForm = true;
        }
        var formData = $(this).serialize();

        var ajax_cache = true;
        var ajax_contentType = 'application/x-www-form-urlencoded; charset=UTF-8';
        var ajax_processData = true;

        if ($(this).attr("enctype") == "multipart/form-data" || isBatchProcess) {

            formData = new FormData(this);

            var batch_data = $('#batchProcessForm').serializeArray();
            $.each(batch_data, function (key, input) {
                formData.append(input.name, input.value);
            });

            // set Ajax options for uploading file
            httpMethod = 'POST';
            ajax_cache = false;
            ajax_contentType = false;
            ajax_processData = false;

            // Display the key/value pairs
            for (var pair of formData.entries()) {
                console.log(pair[0] + ', ' + pair[1]);
            }
        }

        console.log("formData: " + formData);

        $.ajax({
            url: httpUrl,
            type: httpMethod,
            data: formData,
            dataType: "text",
            cache: ajax_cache,
            contentType: ajax_contentType,
            processData: ajax_processData,
            beforeSend: function (jqXHR, settings) {
                // Show loading img
                $("#commonResultPanel img").show();
                // Firstly clear
                $result_panel.text("");
                $result_panel.append("\n【任务" + batchProcessTip + "：" + operation_desc + "】\n\n");
                // $result_panel.append("\n*****任务开始*****\n");　　　
            },
            success: function (data, name) {
                if (isEditorForm) {
                    try {
                        var jsoneditor_content = JSON.parse(data);
                        console.log(jsoneditor_content);
                        jsoneditor.set(jsoneditor_content);
                    }
                    catch (err) {
                        console.log('json parse exception: ' + err);
                    }
                }
                CookieSetInsert("uidset", $("#g_uid").val());
            },
            error: function (jqXHR, textStatus, errorThrown) {
                $result_panel.append("\n" + "AJAX failed");
                $result_panel.append("\nTextStatus: " + textStatus);
                $result_panel.append("\nErrorThrown: " + errorThrown);
                if (errorThrown.trim() == "Unauthorized") {
                    // 未鉴权，刷新页面让用户进行鉴权
                    if (confirm('您的OA鉴权已过期！请刷新页面，重新鉴权。')) {
                        location.reload(true);
                    }
                }
                $log_panel.prepend($result_panel.text());
                console.log(XMLHttpRequest);
            },
            complete: function (jqXHR, textStatus) {
                // Hide loading img
                $("#commonResultPanel img").hide();
                // $result_panel.append("\n*****任务结束*****\n");　
                // 滚动条自动滚动到底部，方便查看结果状态
                $result_panel.scrollTop($('div#commonResultPanel pre')[0].scrollHeight);

                // 计入操作日志
                $log_panel.prepend($result_panel.text());
                $log_panel.prepend("\n==============================" +
                    "\nAction: " + batchProcessTip + "：" + operation_desc +
                    "\n  Time: " + moment().format('YYYY-MM-DD HH:mm:ss') +
                    "\n   URL: " + httpUrl + "?" + formData + "\n");
            },
            xhrFields: {
                onprogress: function (e) {
                    var this_response, response = e.currentTarget.response;
                    if (last_response_len === false) {
                        this_response = response;
                        last_response_len = response.length;
                    } else {
                        this_response = response.substring(last_response_len);
                        last_response_len = response.length;
                    }
                    //console.log(this_response);
                    $result_panel.append(this_response);
                    $result_panel.scrollTop($('div#commonResultPanel pre')[0].scrollHeight);
                }
            }
        });

        // Cookies
        ProcessCookies(title);
        return false;
    });

    var click_timer;

    function SetClickTimer($submit_btn, seconds) {
        click_timer = setInterval(function () {
            $submit_btn.click()
        }, seconds * 1000);
    }

    function ClearClickTimer(click_timer) {
        clearInterval(click_timer);
    }

    // hook when submit form
    $("#tab_body").on("mousedown", ".submit-btn", function (e) {
        switch (e.which) {
            case 1:
                // left click
                console.log("left click")
                ClearClickTimer(click_timer);
                break;
            case 2:
                // middle click
                console.log("middle click")
                SetClickTimer($(this), 2);
                break;
            case 3:
                // right click
                console.log("right click")
                break;
        }
    });
    
    // refer: https://github.com/filebrowser/filebrowser 
    $("#filebrowser").click(function () {
        let env = $("#g_env").val();
        let url = $(this).attr("href") + "?_env=" + env;
        window.open(url, "_blank");
    });

    // multi submit form
    $("#tab_body").on("click", '.submit-btn[type="button"]', function (e) {
        // data setter
        $(this).parents("form").data('operation', $(this).text());
        var selector_str = "select[name='" + $(this).attr("arg_name") + "']";
        $(this).parents("form").find(selector_str).val($(this).attr("arg_value"));
        console.log(selector_str + "  " + $(this).attr("arg_value") + " " + $(this).parents("form").find(selector_str).val());
        $(this).parents("form").submit();
    });

    $("#mru-tab").click(function () {
        // 刷新最近最常使用(MRU)的功能卡片
        MRURefresh();
    });

    $("#resize-result-panel").click(function () {
        if ($("#commonResultMsg").width() != "300") {
            $("#commonResultMsg").width("300px");
            $("#commonResultMsg pre").width("290px");

            $("#commonResultMsg").height("240px");
            $("#commonResultMsg pre").height("240px");

        } else {
            $("#commonResultMsg").width("900px");
            $("#commonResultMsg pre").width("890px");

            $("#commonResultMsg").height("500px");
            $("#commonResultMsg pre").height("500px");
        }
    });
});

/**************************************************************/
/************************ 以下为自定义函数 ********************/
/**************************************************************/

// Cookies
function ProcessCookies(key_str) {
    // 最近最常使用(MRU: Most Recently Used)
    var mru = new Array();
    if (typeof (Cookies.get('mru')) == 'undefined') {
        //Cookies.set('mru', 'cookie test', { expires: 30, path: '/' });
        console.log("First in, Welcome! This site will write cookies for your MRU experience.");
    } else {
        mru = Cookies.getJSON('mru');
        // console.log(mru);
    }
    var is_found = false;
    var mru_index = 0;
    $.each(mru,
        function (index, value) {
            mru_index = index;
            // console.log(mru_index);
            // console.log(value.key);
            // console.log(value.value);
            if (value.key == key_str) {
                is_found = true;
                return false;
            }
        }
    );
    if (is_found) {
        mru[mru_index].value += 1;
    } else {
        if (mru.length == 0) {
            mru[mru_index] = { 'key': key_str, 'value': 1 };
        } else {
            mru[mru_index + 1] = { 'key': key_str, 'value': 1 };
        }
    }
    //按照value排序: 由大到小
    var sorted_mru = mru.sort(
        function (a, b) {
            if (a.value < b.value) return 1;
            if (a.value > b.value) return -1;
            return 0;
        }
    );
    // cookie expire: 30天
    Cookies.set('mru', sorted_mru, { expires: 30, path: '/' });
    // console.log(Cookies.get('mru'));
}

// 最近最常使用
function MRURefresh() {
    var mru = new Array();
    if (typeof (Cookies.get('mru')) == 'undefined') {
        //Cookies.set('mru', 'cookie test', { expires: 30, path: '/' });
        console.log("First in, Welcome! This site will write cookies for your MRU experience.");
    } else {
        $("div#most_recently_used div.row").html('');
        //标签id重复问题待解决, 先屏蔽掉此功能
        return;
        mru = Cookies.getJSON('mru');
        // 最近最常使用: 设置最多显示10个功能卡片
        for (var i = 0; i < mru.length && i < 10; i++) {
            $(".original-card-tabpanel div.item .panel-title").each(function () {
                if (mru[i].key == $(this).text()) {
                    $new_node = $("div#most_recently_used div.masonry-container").append($(this).parents("div.item").prop("outerHTML"));
                    //console.log($new_node.html());
                    $new_node.children(".panel-title h3").append("<span class='badge'>" + mru[i].value + "</span>");
                    //console.log($new_node.children(".panel-title").html());
                    return false;
                }
            });
        }

        $("div#most_recently_used div.masonry-container div.item").each(function () {
            $(this).attr("style", '');
        });
        $("div#most_recently_used div.masonry-container").masonry('reloadItems');
        $("div#most_recently_used div.masonry-container").masonry('layout');
        UpdateTimePicker();
    }
}

function UpdateUidDatalist() {
    // uid datalist
    $("#uidlist").text("");
    var uidset = CookieSetGet("uidset");
    for (i = 0; i < uidset.length; i++) {
        let option = '<option value="' + uidset[i] + '">';
        $("#uidlist").append(option);
    }
}

function CookieSetInsert(cookiekey, element) {
    var array = new Array();
    if (typeof (Cookies.get(cookiekey)) != 'undefined') {
        array = Cookies.getJSON(cookiekey);
        console.log(array);
    }
    var found = false;
    $.each(array,
        function (index, value) {
            if (value == element) {
                found = true;
                return false;
            }
        }
    );
    if (!found) {
        if (array.length == 0) {
            array[0] = element;
        } else {
            array[array.length] = element;
        }
        // cookie expire: 30天
        Cookies.set(cookiekey, array, { expires: 30, path: '/' });
        console.log(Cookies.get(cookiekey));
        UpdateUidDatalist()
    }
}

function CookieSetGet(cookiekey) {
    // 最近最常使用(MRU: Most Recently Used)
    var array = new Array();
    if (typeof (Cookies.get(cookiekey)) != 'undefined') {
        array = Cookies.getJSON(cookiekey);
        // console.log(array);
    }
    return array;
}


// 号码自动填写
function AutoUin() {
    // auto uin
    $("#tab_body").on("change", ":input[name='uin']", function () {
        if ($("input#auto-uin").prop("checked")) {
            var uin = $(this).val().trim();
            $(':input[name="uin"]').each(function () {
                $(this).val(uin);
            });
            $(':input[name="player_id"]').each(function () {
                $(this).val(uin);
            });
        }
    });
    $("#tab_body").on("change", ":input[name='player_id']", function () {
        if ($("input#auto-uin").prop("checked")) {
            var player_id = $(this).val().trim();
            $(':input[name="player_id"]').each(function () {
                $(this).val(player_id);
            });
            $(':input[name="uin"]').each(function () {
                $(this).val(player_id);
            });
        }
    });
}

function UpdateTimePicker() {
    // Date Range Picker
    $('input.datetimepicker').daterangepicker({
        timePicker24Hour: true,
        singleDatePicker: true,
        timePicker: true,
        showDropdowns: true,
        timePickerSeconds: true,
        autoApply: true,
        autoUpdateInput: true,
        startDate: moment(),
        // timePickerIncrement: 30,
        locale: {
            format: 'YYYY-MM-DD HH:mm:ss'
        }
    });
}
// autocomplete
function InitTypeaHead() {
    var search_keys = new Array();
    var i = 0;
    $("div.item .panel-title").each(function () {
        search_keys[i++] = $(this).text().trim();
    });
    $(":input[name='search_input']").typeahead({
        hint: true,
        source: search_keys,
        /*本地数据*/
        items: 10,
        highlight: true,
        minLength: 1,
        afterSelect: function (item) {
            console.log(item);
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

// 重新动态流式布局
function RelayoutContainer($jquery_obj) {
    $jquery_obj.masonry('reloadItems');
    $jquery_obj.masonry('layout');
}

function GetQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null)
        return unescape(r[2]);
    return null;
}
