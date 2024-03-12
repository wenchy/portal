{% for func_name, func in tab['forms'].items() %}

{% if func['layout'] == '6-column' %}
    <div class="col-xs-12 col-sm-12 col-md-12 item">
{% elif func['layout'] == '4-column' %}
    <div class="col-xs-12 col-sm-12 col-md-8 item">
{% else %}
   <div class="col-xs-6 col-sm-6 col-md-4 item">
{% end %}

    <div class="panel panel-{{ func['theme'] }}" {% if 'tip' in func %} data-toggle="tooltip" data-placement="top" title="{{ func['tip'] }}" {% end %}>
        <div class="panel-heading">
            <h3 class="panel-title text-center" >{% if 'title' in func %} {{ func['title'] }} {% else %} {{ func_name }} {% end %}</h3>
        </div>
        <div class="panel-body">
            <form class="form-horizontal"
                {% if 'target' in func %}
                    target="{{ func['target'] }}"
                {% else %}
                    target="_self"
                {% end %}

                {% if 'method' in func %}
                    method="{{ func['method'] }}"
                {% else %}
                    method="post"
                {% end %}

                {% if 'enctype' in func %}
                    enctype="{{ func['enctype'] }}"
                {% end %}

                action="/{{ venv_name }}{{ form_action }}"

                {% if 'popup' in func %}
                    popup="{{ func['popup'] }}"
                {% end %}
            >
                <input type="hidden" name="_module" value="{{ tab['module_name'] }}" />
                <input type="hidden" name="_func" value="{{ func_name }}" />
                <input type="hidden" name="_type" value=""> 

                {% for arg_name, arg in func['args'].items() %}
                    {% if arg_name in ["_jsoneditor_content"] %}
                        <input type="hidden" name="{{ arg_name }}" value="" />
                     {% elif arg_name in ["_ctx"] %}
                        <input type="hidden" name="_uid" value="" />
                        <input type="hidden" name="_zone" value="" />
                    {% else %}

                        {% if func['layout'] == '6-column' %}
                            <div class="col-sm-2">
                            {% set form_group_class='form_group_margin' %}
                            {% set label_class='control-label' %}
                            {% set input_class='' %}
                        {% elif func['layout'] == '4-column' %}
                            <div class="col-sm-3">
                            {% set form_group_class='form_group_margin' %}
                            {% set label_class='control-label' %}
                            {% set input_class='' %}
                        {% elif func['layout'] == '2-column' %}
                            <div class="col-sm-6">
                            {% set form_group_class='form_group_margin' %}
                            {% set label_class='control-label' %}
                            {% set input_class='' %}
                        {% else %}
                            {% set form_group_class='' %}
                            {% set label_class='col-sm-4 control-label' %}
                            {% set input_class='col-sm-8' %}
                        {% end %}

                        {% if arg['input'] == 'datetime' %}
                            <div class="{{ form_group_class }} form-group form-group-sm has-feedback" {% if 'tip' in arg %} data-toggle="tooltip" data-placement="top" title="{{ arg['tip'] }}" {% end %}>
                                <label class="{{ label_class }}">{{ arg['desc'] }}</label>
                                <div class="{{ input_class }}">
                                    <span class="glyphicon glyphicon-calendar form-control-feedback" aria-hidden="true"></span>
                                    <input name="{{ arg_name }}" type="text" class="form-control input-sm datetimepicker" {{ arg['status'] }}>
                                </div>
                            </div>
                        {% elif arg['input'] == 'select' %}
                            <div class="{{ form_group_class }} form-group form-group-sm {% if 'submit' in func and func['submit'] == arg_name %} hidden {% end %}" {% if 'tip' in arg %} data-toggle="tooltip" data-placement="top" title="{{ arg['tip'] }}" {% end %}>
                                <label class="{{ label_class }}">{{ arg['desc'] }}</label>
                                <div class="{{ input_class }}">
                                    <select name="{{ arg_name }}" class="form-control input-sm" {{ arg['status'] }}>
                                        {% for value,desc in arg['options'].items() %} 
                                            <option value="{{ value }}">{{ desc }}</option>
                                        {% end %}
                                    </select>
                                </div>
                            </div>
                        {% elif arg['input'] == 'textarea' %} 
                            <div class="{{ form_group_class }} form-group form-group-sm" {% if 'tip' in arg %} data-toggle="tooltip" data-placement="top" title="{{ arg['tip'] }}" {% end %}>
                                <label class="{{ label_class }}">{{ arg['desc'] }}</label>
                                <div class="{{ input_class }}">
                                    <textarea name="{{ arg_name }}" {% if 'placeholder' in arg %} placeholder="{{ arg['placeholder'] }}" {% end %} type="text" class="form-control input-sm" rows="5" {{ arg['status'] }}>{{ arg['default'] }}</textarea>
                                </div>
                            </div>
                        {% elif arg['input'] == 'file' %}    
                            <div class="{{ form_group_class }} form-group form-group-sm" {% if 'tip' in arg %} data-toggle="tooltip" data-placement="top" title="{{ arg['tip'] }}" {% end %}>
                                <label class="{{ label_class }}">{{ arg['desc'] }}</label>
                                <div class="{{ input_class }}">
                                    <input name="{{ arg_name }}" type="file" class="form-control input-sm" {{ arg['status'] }}></input>
                                </div>
                            </div>
                        {% else %}
                            <div class="{{ form_group_class }} form-group form-group-sm" {% if 'tip' in arg %} data-toggle="tooltip" data-placement="top" title="{{ arg['tip'] }}" {% end %}>
                                <label class="{{ label_class }}">{{ arg['desc'] }}</label>
                                <div class="{{ input_class }}">
                                    {% if 'datalist' in arg %}
                                        <input name="{{ arg_name }}" list="{{ func_name + '_' + arg_name }}_datalist" value="{{ arg['default'] }}"  {% if 'placeholder' in arg %} placeholder="{{ arg['placeholder'] }}" {% end %} type="text" class="form-control input-sm" {{ arg['status'] }}>
                                        <datalist id="{{ func_name + '_' + arg_name }}_datalist">
                                            {% for value,desc in arg['datalist'].items() %} 
                                                <option value="{{ value }}">{{ desc }}</option>
                                            {% end %}
                                        </datalist>
                                    {% else %}
                                        <input name="{{ arg_name }}" value="{{ arg['default'] }}" {% if 'placeholder' in arg %} placeholder="{{ arg['placeholder'] }}" {% end %} type="text" class="form-control input-sm" {{ arg['status'] }}>
                                    {% end %}
                                </div>
                            </div>
                        {% end %}

                        {% if func['layout'] != '1-column' %}
                            </div>
                        {% end %}

                    {% end %}
                {% end %}

                <!-- submit -->
                <div style="padding: 3px 0"></div>
               
                {% if 'submit' in func and 'options' in func['args'][func['submit']] %}
                <div class="text-right">
                    {% for value,desc in func['args'][func['submit']]['options'].items() %}
                        <button type="button" arg_name="{{ func['submit'] }}" class="btn btn-default btn-sm submit-btn" arg_value="{{ value }}">&nbsp;{{ desc }}&nbsp;</button>
                    {% end %}
                </div>
                {% else %}
                <div class="form-group">
                    <div class="col-sm-offset-4 col-sm-8">
                        <button type="submit" class="btn btn-default btn-sm submit-btn">&nbsp;提 交&nbsp;</button>
                    </div>
                </div>
                {% end %}
            </form>
        </div>
    </div>
</div>
{% end %}
