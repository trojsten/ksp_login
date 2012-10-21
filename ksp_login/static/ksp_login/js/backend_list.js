(function($)
{
    // First, load the CSS only used with JavaScript-enabled browsers.
    var css = document.createElement("link");
    css.setAttribute("rel", "stylesheet");
    css.setAttribute("type", "text/css");
    css.setAttribute("href", STATIC_URL + "ksp_login/css/js_only.css");
    document.getElementsByTagName("head")[0].appendChild(css);

    var simple_provider_action = function()
    {
        $(this).siblings('form').submit();
    };

    var clear_selected_input_provider = function()
    {
        $('div.ksp_login_selected_input_provider').hide('fast', function()
        {
            $(this).remove();
        });
        $('.ksp_login_selected_provider_button')
            .removeClass('ksp_login_selected_provider_button');
    };

    var input_provider_action = function()
    {
        var myself = $(this);
        if (myself.hasClass('ksp_login_selected_provider_button'))
        {
            clear_selected_input_provider();
            return;
        }
        clear_selected_input_provider();
        myself.addClass('ksp_login_selected_provider_button');
        var new_form = myself.siblings('form').clone().wrap('<div />').parent();
        new_form.addClass('ksp_login_selected_input_provider');
        new_form.hide();
        var backend_list = myself.closest('.ksp_login_provider_list');
        backend_list.after(new_form);
        new_form.show('fast');
    };

    $('.ksp_login_provider_list > .provider_simple > img')
        .on('click', simple_provider_action);
    $('.ksp_login_provider_list > .provider_with_input > img')
        .on('click', input_provider_action);
})(ksp_login.jQuery);
