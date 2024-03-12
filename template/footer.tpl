<!-- 执行结果 -->
    <div id="BatchPanel" class="panel panel-info collapse">
        <div class="panel-heading">
            <h3 class="panel-title text-center">
                批量处理
                <span class="glyphicon glyphicon-list-alt" aria-hidden="false"></span>
            </h3>
        </div>
        <div id="BatchPanelBody" class="panel-body">
            <form id="batchProcessForm">
                <div class="form-group" data-toggle="tooltip" data-placement="left" title="" data-original-title="每行一个uid">
                    <label for="uids">长uid列表</label>
                    <textarea name="__uidlist__" class="form-control" rows="5" id="uids"></textarea>
                </div>
                <div class="checkbox">
                    <label>
                        <input type="checkbox" id="batchProcessCheck"> 确定进行批量处理
                    </label>
                </div>
            </form>
        </div>
    </div>

    <div id="commonResultPanel" class="panel panel-default">
        <div id="commonResultMsg" class="panel-body collapse in">
            <pre class="pre-result"></pre>
        </div>
        <div id="commonResultControl" class="panel-footer">
            <h3 class="panel-title text-center">
                <span id="resize-result-panel" class="glyphicon glyphicon-resize-full" aria-hidden="false" title="resize"></span>
                &nbsp;&nbsp;&nbsp;&nbsp;

                <img src="/{{ venv_name }}/static/img/loading-green.gif" style="width: 16px; height: 16px; display: none" alt="loading">
                执行结果

                &nbsp;&nbsp;&nbsp;&nbsp;
                <span class="glyphicon glyphicon-fullscreen" aria-hidden="false" title="show log" data-toggle="modal" data-target="#commonResultModal"></span>
            
                &nbsp;&nbsp;&nbsp;&nbsp;
                <span class="glyphicon glyphicon-resize-vertical pull-right" aria-hidden="false" title="hide/show" data-toggle="collapse" data-target="#commonResultMsg" aria-expanded="false" aria-controls="commonResultMsg"></span>
            </h3>
        </div>
    </div>
    <!-- 执行结果历史记录 -->
    <div class="modal fade" id="commonResultModal" tabindex="-1" role="dialog">
        <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
                <div class="modal-header text-center">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title" ><span class="glyphicon glyphicon-comment" aria-hidden="false"></span>
                    执行结果日志</h4>
                </div>
                <div class="modal-body">
                    <pre class="pre-result"></pre>
                </div>
                <!-- <div class="modal-footer">
                    <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary">Save changes</button>
                </div> -->
            </div>
        </div>
    </div>
    
    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="/{{ venv_name }}/static/js/jquery-1.12.4.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/{{ venv_name }}/static/bootstrap/js/bootstrap.min.js"></script>
    <!-- Cascading grid layout library -->
    <script src="/{{ venv_name }}/static/js/masonry.pkgd.min.js"></script>
    <!-- Detect when images have been loaded. -->
    <script src="/{{ venv_name }}/static/js/imagesloaded.pkgd.min.js"></script>
    <!-- Parse, validate, manipulate, and display dates in JavaScript. -->
    <script src="/{{ venv_name }}/static/js/moment.min.js"></script>
     <!-- js-cookie -->
    <script src="/{{ venv_name }}/static/js/js.cookie.js"></script>
    <script src="/{{ venv_name }}/static/jquery.cookie.js"></script>
    <!-- Include Date Range Picker -->
    <script src="/{{ venv_name }}/static/daterangepicker/daterangepicker.js"></script>
    <!-- Include typeahead -->
    <script src="/{{ venv_name }}/static/bootstrap/js/typeahead.min.js"></script>
    <!-- Include jsoneditor -->
    <script src="/{{ venv_name }}/static/jsoneditor/jsoneditor.min.js"></script>
    <!-- My Customization -->
    <script src="/{{ venv_name }}/static/js/index.js"></script>
    <script>
        function updateUID() {
            save_cookie()
            $("[name=_uid]").val($('#g_uid').val())
        }

        function updateZone() {
            save_cookie()
            $("[name=_zone]").val($('#g_zone').val())
        }

        function updateAccountType() {
            save_cookie()
            $("[name=_type]").val($('#g_type').val())
        }


        function save_cookie() {
            $.cookie("g_uid", $("#g_uid").val())
            $.cookie("g_zone", $("#g_zone").val())
            $.cookie("g_type", $("#g_type").val())
        }

        function load_cookie() {
            var g_uid = $.cookie("g_uid")
            if (g_uid) {
                $("#g_uid").val(g_uid)
            }
            var g_zone = $.cookie("g_zone")
            if (g_zone) {
                $("#g_zone").val(g_zone)
            }

            var g_type = $.cookie("g_type")
            if (g_type) {
                $("#g_type").val(g_type)
            }
        }
        function load_params() {
            var g_uid = getParameterByName('uid'); 
            var g_zone = getParameterByName('zone');
            var g_type = getParameterByName('type');

            if (g_uid && g_zone && g_type) {
                $("#g_uid").val(g_uid)
                $("#g_zone").val(g_zone)
                $("#g_type").val(g_type)
            }
        }

        // var foo = getParameterByName('foo'); // "lorem"
        // var bar = getParameterByName('bar'); // "" (present with empty value)
        // var baz = getParameterByName('baz'); // "" (present with no value)
        // var qux = getParameterByName('qux'); // null (absent)
        function getParameterByName(name, url) {
            if (!url) url = window.location.href;
            name = name.replace(/[\[\]]/g, "\\$&");
            var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
                results = regex.exec(url);
            if (!results) return null;
            if (!results[2]) return '';
            return decodeURIComponent(results[2].replace(/\+/g, " "));
        }

        $(document).ready(function() {
            load_cookie()
            load_params()
            updateUID()
            updateZone()
            updateAccountType()
        });
    </script>
    
</body>

</html>