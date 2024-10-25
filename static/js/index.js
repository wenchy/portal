$(document).ready(function () {
    var cur_env_id = window.location.pathname.split("/")[1];
    // refresh page at five clock on everyday.
    setInterval(function () {
        var now = moment();
        if (now.hour() == 5) {
            location.reload(true);
        }
    }, 30 * 60 * 1000);

    UpdateUidDatalist();

    // $(".pinned").pin();
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
    InitTypeaHead();
    var jsoneditor_options = {
        mode: 'tree',
        modes: ['code', 'form', 'text', 'tree', 'view'], // allowed modes
    };
    var jsoneditorDict = {}
    $("div.jsoneditor").each(function () {
        // jsoneditor need convert jQuery object to JavaScript object
        jsoneditorDict[$(this).attr("id")] = new JSONEditor($(this).get(0), jsoneditor_options);
    });

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

    // common form submit: ajax
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
            operation = "Submit";
        } else {
            operation = operation.trim().replace(" ", "");
        }
        var operation_desc = "[" + operation + "] " + title;
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

        var outerThis = this;
        // checkbox
        var $checkboxList = $(this).find("div.checkbox");
        $checkboxList.each(function () {
            var $checkbox = $(this);
            if ($checkbox.length > 0) {
                // process if checkbox exists
                console.log("get checkbox id: " + $checkbox.attr("id"))
                checkboxId = $checkbox.attr("id")
                checkboxSubId = checkboxId + "-sub"
                let args = [];
                $(this).find(":input[name='" + checkboxSubId + "']:checked").each(function () {
                    console.log("box val: " + $(this).val())
                    args.push($(this).val());
                });
                console.log("get checkbox args: " + args.join(','))
                $(this).find(":input[name='" + checkboxSubId + "']").remove();
                $(outerThis).find(":input[name='" + checkboxId + "']").val(args);
            }
        })
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
                $result_panel.append("Action" + batchProcessTip + ": " + operation_desc + "\n\n");
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
                    if (confirm('Unauthorized, please refresh webpage.')) {
                        location.reload(true);
                    }
                }
                $log_panel.prepend($result_panel.text());
                console.log(XMLHttpRequest);
            },
            complete: function (jqXHR, textStatus) {
                // Hide loading img
                $("#commonResultPanel img").hide();
                // Scroll down to bottom for showing the result status.
                $result_panel.scrollTop($('div#commonResultPanel pre')[0].scrollHeight);

                // prepend to log panel
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
    var array = new Array();
    if (typeof (Cookies.get(cookiekey)) != 'undefined') {
        array = Cookies.getJSON(cookiekey);
        // console.log(array);
    }
    return array;
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
        // local data
        items: 10,
        highlight: true,
        minLength: 1,
        afterSelect: function (item) {
            console.log(item);
            $("#fuzzy-search").submit();
        }
    });
}

// Fuzzy Search
// Refer to https://github.com/bevacqua/fuzzysearch/blob/master/index.js
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

// Cascading grid layout
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
