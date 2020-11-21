<!DOCTYPE html>
<html lang="zh">

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title>portal({{deployed_venv['desc']}})</title>
    <!-- Bootstrap -->
    <link href="/{{ venv_name }}/static/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <!-- Date Range Picker -->
    <link href="/{{ venv_name }}/static/daterangepicker/daterangepicker.css" rel="stylesheet">
    <!-- jsoneditor -->
    <link href="/{{ venv_name }}/static/jsoneditor/jsoneditor.min.css" rel="stylesheet">
    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
    <!-- select2 -->
    <!-- <link href="/{{ venv_name }}/static/css/select2.min.css" rel="stylesheet"> -->
    <!-- quill editor -->
    <link href="/{{ venv_name }}/static/quill/quill.snow.css" rel="stylesheet">
    <link href="/{{ venv_name }}/static/quill/quill.bubble.css" rel="stylesheet">
    <link href="/{{ venv_name }}/static/css/index.css" rel="stylesheet">
</head>

<body>

    <div id="menu_container" class="container">
        <nav class="navbar navbar-inverse navbar-fixed-top">
            <div class="container">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="/{{ venv_name }}/" data-toggle="tooltip" data-placement="bottom" title="【_VERSION_】Deployed by _DEPLOYER_">
                        portal&nbsp;{{deployed_venv['desc']}}({{ venv_name }})<br>
                        <span id="username" class="badge">{{ username }}</span>
                    </a>
                    <span class="visible-xs" style="height: 50px; padding: 6px 15px">
                        <button type="button" class="btn btn-default" style="color: #fff; background-color: transparent; border-color: #333; font-size: 18px" data-toggle="offcanvas">
                            <span class="glyphicon glyphicon-list" aria-hidden="true"></span>
                        </button>
                    </span>
                </div>
                <div id="navbar" class="collapse navbar-collapse">
                    <div class="navbar-form navbar-left">
                        <!--  <select class="form-control" name="SERVER_TYPE" id="env_id" onchange="OnClickSetEnvID(true)">
                        </select> -->
                        <div class="form-group">
                            <select class="form-control" name="g_type" id="g_type" onChange="updateAccountType()">
                                <option value="0" >IOS</option>
                                <option value="1" selected="selected">安卓</option>
                            </select>

                            {% if venv_name == 'idc' %}
                               <!--  IDC区太多了，支持输入 -->
                                <input list="zonelist" class="form-control" name="g_env" id="g_env" onChange="updateEnvAddr()" type="text"  placeholder="zoneid" value="0" data-toggle="tooltip" data-placement="bottom" title="请输入zoneid">
                                <datalist id="zonelist">
                                    {% for zone_id, zone_conf in zones.items() %}
                                        <option value="{{ zone_id }}">{{ zone_conf['desc'] }}</option>
                                    {% end %}
                                </datalist>
                            {% else %}
                                <!--  开发测试等区数量有限，使用select，方便操作 -->
                                <select class="form-control" name="g_env" id="g_env" onChange="updateEnvAddr()">
                                    {% for zone_id, zone_conf in zones.items() %}
                                        <option value="{{ zone_id }}">{{ zone_conf['desc'] }}</option>
                                    {% end %}
                                </select>
                            {% end %}

                            <input list="uidlist" class="form-control" name="g_uid" id="g_uid" onChange="updateUID()" type="text"  placeholder="uid" value="0" data-toggle="tooltip" data-placement="bottom" title="请输入ruid">
                            <datalist id="uidlist"></datalist>
                        </div>
                    </div>
                    <ul class="nav navbar-nav">
                        <li role="presentation" class="dropdown">
                            <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">
                            环境<span class="caret"></span>
                            </a>
                            <ul class="dropdown-menu">
                                {% for desc, envs in venvs.items() %}
                                    <li class="dropdown-submenu">
                                        <a href="#">{{ desc }}</a>
                                        <ul class="dropdown-menu">
                                            {% for name, conf in envs.items() %}
                                                <li><a href="{{ conf['domain'] }}/{{ conf['path'] }}/" target="_blank">{{ conf['desc'] }}({{ name }})</a></li>
                                            {% end %}
                                        </ul>
                                    </li>
                                {% end %}
                            </ul>
                        </li>
                        <li role="presentation" class="dropdown">
                            <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">
                            高级<span class="caret"></span>
                            </a>
                            <ul class="dropdown-menu">
                                <li>
                                    <a href="#" data-toggle="collapse" data-target="#BatchPanel" aria-expanded="false" aria-controls="BatchPanel" >
                                        批处理
                                        <span class="glyphicon glyphicon-list-alt" aria-hidden="false" title="batch process"></span>
                                    </a>
                                </li>
                                <li role="separator" class="divider"></li>
                                <li>
                                    <a href="#" data-toggle="collapse" data-target="#ChatPanel" aria-expanded="false" aria-controls="ChatPanel">
                                        聊天室
                                        <span class="glyphicon glyphicon-comment" aria-hidden="false" title="chat room"></span>
                                    </a>
                                </li>
                            </ul>
                        </li>
                        <li role="presentation" class="dropdown">
                            <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">
                            更多<span class="caret"></span>
                            </a>
                            <ul class="dropdown-menu">
                                <li><a href="/{{ venv_name }}/admin/list" target="_blank">高级功能</a></li>
                                <li><a href="/{{ venv_name }}/excel/list" target="_blank">策划配置</a></li>
                                <li class="dropdown-submenu">
                                    <a href="#">Prometheus</a>
                                    <ul class="dropdown-menu">
                                        <li><a href="#" target="_blank">dev</a></li>
                                        <li><a href="#" target="_blank">test</a></li>
                                        <li><a href="#" target="_blank">idc</a></li>
                                    </ul>
                                </li>
                            </ul>
                        </li>
                    </ul>
                    <form id="fuzzy-search" class="navbar-form form-inline navbar-right">
                        <div class="form-group has-feedback">
                            <div class="input-group">
                                <input id="search-keyword" name="search_input" data-provide="typeahead" type="text" value="" class="form-control" autocomplete="off" placeholder="Search...">
                            </div>
                        </div>
                    </form>
                </div>
                <!--/.nav-collapse -->
            </div>
        </nav>
    </div>
