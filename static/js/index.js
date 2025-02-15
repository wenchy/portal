$(document).ready(function () {
    var curEnvName = window.location.pathname.split("/")[1];
    // refresh page at five clock on everyday.
    setInterval(function () {
        let now = moment();
        if (now.hour() == 5) {
            location.reload(true);
        }
    }, 30 * 60 * 1000);

    updateUidDatalist();
    loadEnvironFromCookie()
    loadEnvironFromQuerystring()
    updateUID()
    updateZone()
    updateType()

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
    let $container = $('.masonry-container');
    // Reinitialize masonry inside each panel after the relative tab link is clicked
    $('a[data-toggle=tab]').each(function () {
        $(this).on('shown.bs.tab', function () {
            $container.imagesLoaded(function () {
                $container.masonry({
                    columnWidth: '.item',
                    itemSelector: '.item',
                    percentPosition: true,
                    horizontalOrder: true,
                });
            });
        });
    });
    // Automatically click the first tab on page load
    $("a[data-toggle=tab]").first().click();

    // Firstly Update Date Range Picker
    updateDatetimePicker();
    initTypeaHead();
    // Refer to https://github.com/josdejong/jsoneditor
    // view mode: handle large JSON documents up to 500 MiB.
    let jsoneditorOptions = {
        modes: ['view', 'form', 'tree', 'code', 'text'],
        mode: 'tree'
    };
    var jsoneditorDict = {}
    $("div.jsoneditor").each(function () {
        // jsoneditor need convert jQuery object to JavaScript object
        jsoneditorDict[$(this).attr("id")] = new JSONEditor($(this).get(0), jsoneditorOptions);
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
                var tabId = $(this).parents("div.tab-pane").attr("id");
                // console.log("fuzzysearch： " + tab_id);
                $("div#sidebar a." + tabId).click();
                $('html, body').animate({
                    scrollTop: $(this).offset().top - 70 // substract top fixed navigation height（70px）
                }, 100);
                $panelHead = $card.find("div.panel-heading");
                // Store the original CSS
                let originalBgColor = $panelHead.css('background-color');
                // Set new background color
                $panelHead.css({ "background-color": "#800080" });
                $card.fadeOut("slow")
                    .slideDown("slow")
                    .delay(10000) // delay 10 seconds
                    .queue(function (next) {
                        $panelHead.css({ "background-color": originalBgColor });
                        next();
                    });
            }
        });
        return false;
    });

    // common form submit: ajax
    $("#tab_body").on("submit", "form", function () {
        var formTarget = $(this).attr("target");
        if (formTarget == "_blank") {
            // No need to submit to avoid infinite recursion
            return;
        }

        var isBatchProcess = $("#batch-process-form #batchProcessCheck").is(':checked')
        var popup = $(this).attr("popup");
        var title = $(this).parent().siblings(".panel-heading").children(".panel-title").text().trim();
        var operation = $(this).data('operation');
        if (operation == undefined) {
            operation = "Submit";
        } else {
            operation = operation.trim().replace(" ", "");
        }
        var operationDesc = "[" + operation + "] " + title;
        var batchProcessConfirm = ""
        var batchProcessTip = ""
        if (isBatchProcess) {
            batchProcessConfirm = '(batch)'
            batchProcessTip = '<font color="red"><b>(batch)</b></font>'
            popup = "confirm"
        }
        switch (popup) {
            case "confirm":
                if (!confirm('Are you sure to run' + batchProcessConfirm + ': ' + operationDesc + '?')) {
                    console.log("form submit canceled: " + title);
                    return false;
                }
                break;

            case "alert":
                alert('Attention!\nYou will run action: ' + operationDesc + '!')
                break;

            case "prompt":
                let envName = prompt('Action: ' + operationDesc + '\nPlease input environment name:', "")
                if (envName == null) {
                    console.log("user cancel prompt: " + operationDesc);
                    return false;
                } else {
                    if (envName != curEnvName) {
                        alert('Wrong environment name.\nThe current is: ' + curEnvName)
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

        var lastResponseLen = false;
        var $resultPanel = $("#common-result-panel pre");
        var $logPanel = $('#commonResultModal pre')
        let jsoneditor = null;
        let $jsoneditors = $(this).parents("div.tab-pane").find("div.jsoneditor");
        if ($jsoneditors.length > 0) {
            jsoneditor = jsoneditorDict[$jsoneditors.attr("id")];
            console.log("before jsoneditor-content: " + $jsoneditors.attr("id") + ", content: " + jsoneditor.getText())
            // Set jsoneditor's content
            $(this).find('input[data-input-type="editor"]').val(jsoneditor.getText());
        }

        // NOTE: unchecked checkboxes will not included in the serialized string.
        var formData = $(this).serialize();

        var ajaxCache = true;
        var ajaxContentType = 'application/x-www-form-urlencoded; charset=UTF-8';
        var ajaxProcessData = true;

        if ($(this).attr("enctype") == "multipart/form-data" || isBatchProcess) {
            formData = new FormData(this);
            var batch_data = $('#batch-process-form').serializeArray();
            $.each(batch_data, function (key, input) {
                formData.append(input.name, input.value);
            });

            // set Ajax options for uploading file
            httpMethod = 'POST';
            ajaxCache = false;
            ajaxContentType = false;
            ajaxProcessData = false;

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
            cache: ajaxCache,
            contentType: ajaxContentType,
            processData: ajaxProcessData,
            beforeSend: function (jqXHR, settings) {
                // Show loading img
                $("#common-result-panel img").show();
                // Firstly clear
                $resultPanel.text("");
                $resultPanel.append("<strong>Action" + batchProcessTip + ": " + operationDesc + "</strong>\n\n");
            },
            success: function (data, name) {
                if (jsoneditor) {
                    try {
                        var content = JSON.parse(data);
                        // console.log(content);
                        jsoneditor.set(content);
                    } catch (err) {
                        console.log('json parse exception: ' + err);
                    }
                }
                cookieSetInsert("uidset", $("#environ-uid").val());
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(jqXHR)
                $resultPanel.append(`\n\n❌ <font color="red">${jqXHR.status} ${errorThrown}</font>`);
                if (jqXHR.status === 401) {
                    if (confirm('Unauthorized, please reload webpage.')) {
                        location.reload(true);
                    }
                }
            },
            complete: function (jqXHR, textStatus) {
                // Hide loading img
                $("#common-result-panel img").hide();
                // Scroll down to bottom for showing the result status.
                $resultPanel.scrollTop($('div#common-result-panel pre')[0].scrollHeight);

                // prepend to log panel
                // remove first title line to avoid duplicating (e.g.: Action: XXX)
                let content = $resultPanel.text().split("\n").slice(1).join("\n")
                $logPanel.prepend(content);
                $logPanel.prepend("\n******************************************************" +
                    "\nAction" + batchProcessTip + ": " + operationDesc +
                    "\n  Time: " + moment().format('YYYY-MM-DD HH:mm:ss') +
                    "\n   URL: " + httpUrl + "?" + formData + "\n");
            },
            xhrFields: {
                onprogress: function (e) {
                    var thisResponse, response = e.currentTarget.response;
                    if (lastResponseLen === false) {
                        thisResponse = response;
                        lastResponseLen = response.length;
                    } else {
                        thisResponse = response.substring(lastResponseLen);
                        lastResponseLen = response.length;
                    }
                    $resultPanel.append(thisResponse);
                    $resultPanel.scrollTop($('div#common-result-panel pre')[0].scrollHeight);
                }
            }
        });
        return false;
    });

    var clickTimer;
    function setClickTimer($submit_btn, seconds) {
        clickTimer = setInterval(function () {
            $submit_btn.click()
        }, seconds * 1000);
    }

    function clearClickTimer(clickTimer) {
        clearInterval(clickTimer);
    }

    // hook when submit form
    $("#tab_body").on("mousedown", ".submit-btn", function (e) {
        switch (e.which) {
            case 1:
                // left click
                console.log("left click")
                clearClickTimer(clickTimer);
                break;
            case 2:
                // middle click
                console.log("middle click")
                setClickTimer($(this), 2);
                break;
            case 3:
                // right click
                console.log("right click")
                break;
        }
    });

    // multi submit form
    $("#tab_body").on("click", '.submit-btn[type="button"]', function (e) {
        let form = $(this).parents("form");
        // data setter
        form.data('operation', $(this).text());
        let opcodeValue = $(this).attr("data-form-opcode")
        let opcodeSelector = "input[name='_opcode']";
        form.find(opcodeSelector).val(opcodeValue);
        console.log(opcodeSelector + "  " + opcodeValue + " " + form.find(opcodeSelector).val());

        let oldFormTarget = form.attr("target");

        // If button has attr "data-form-target", then use it and restore it finally.
        let dataFormTarget = $(this).attr("data-form-target");
        if (dataFormTarget != undefined && oldFormTarget != dataFormTarget) {
            form.attr("target", dataFormTarget);
        }
        // submit
        form.submit();
        // restore old form target
        if (oldFormTarget != dataFormTarget) {
            form.attr("target", oldFormTarget);
        }
    });

    $("#resize-result-panel").click(function () {
        if ($("#common-result-msg").width() != "300") {
            $("#common-result-msg").css({
                'width': '300px',
                'height': '240px'
            });
            $("#common-result-msg pre").css({
                'width': '290px',
                'height': '240px'
            });
        } else {
            $("#common-result-msg").css({
                'width': '900px',
                'height': '500px'
            });
            $("#common-result-msg pre").css({
                'width': '890px',
                'height': '500px'
            });
        }
    });
});

function updateUidDatalist() {
    // uid datalist
    $("#uidlist").text("");
    var uidset = CookieSetGet("uidset");
    for (i = 0; i < uidset.length; i++) {
        let option = '<option value="' + uidset[i] + '">';
        $("#uidlist").append(option);
    }
}

function cookieSetInsert(cookiekey, element) {
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
        // cookie expire: 30 days
        Cookies.set(cookiekey, array, { expires: 30, path: '/' });
        console.log(Cookies.get(cookiekey));
        updateUidDatalist()
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

function updateDatetimePicker() {
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
function initTypeaHead() {
    var searchKeys = new Array();
    var i = 0;
    $("div.item .panel-title").each(function () {
        searchKeys[i++] = $(this).text().trim();
    });
    $(":input[name='search_input']").typeahead({
        hint: true,
        source: searchKeys,
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
function fuzzySearch(needle, haystack) {
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

function updateUID() {
    saveEnvironToCookie()
    $("[name=_uid]").val($('#environ-uid').val())
}

function updateZone() {
    saveEnvironToCookie()
    $("[name=_zone]").val($('#environ-zone').val())
}

function updateType() {
    saveEnvironToCookie()
    $("[name=_type]").val($('#environ-type').val())
}


function saveEnvironToCookie() {
    $.cookie("environ-uid", $("#environ-uid").val())
    $.cookie("environ-zone", $("#environ-zone").val())
    $.cookie("environ-type", $("#environ-type").val())
}

function loadEnvironFromCookie() {
    var uid = $.cookie("environ-uid")
    if (uid) {
        $("#environ-uid").val(uid)
    }
    var zone = $.cookie("environ-zone")
    if (zone) {
        $("#environ-zone").val(zone)
    }
    var type = $.cookie("environ-type")
    if (type) {
        $("#environ-type").val(type)
    }
}
function loadEnvironFromQuerystring() {
    var uid = getValueFromQuerystring('uid');
    var zone = getValueFromQuerystring('zone');
    var type = getValueFromQuerystring('type');
    if (uid && zone && type) {
        $("#environ-uid").val(uid)
        $("#environ-zone").val(zone)
        $("#environ-type").val(type)
    }
}

function getValueFromQuerystring(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}
