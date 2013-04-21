ksp_login.jQuery(function($)
{
    // First, load the CSS only used with JavaScript-enabled browsers.
    var css = document.createElement("link");
    css.setAttribute("rel", "stylesheet");
    css.setAttribute("type", "text/css");
    css.setAttribute("href", STATIC_URL + "ksp_login/css/js_only.css");
    document.getElementsByTagName("head")[0].appendChild(css);

    $('.ksp_login_provider_list').addClass('ksp_login_provider_list_js');

    var update_modal_size = function()
    {
        $(this).closest('.simplemodal-container').each(function()
        {
            var modal_box_div = $(this).find('#ksp_login_modal_box');
            var height = modal_box_div.height();
            var width = modal_box_div.width();
            $.modal.update(height, width);
            $('.simplemodal-wrap').css({overflow: 'hidden'});
        });
    }

    var show_element = function(elem, callback)
    {
        $(elem).slideDown({
            duration: 'fast',
            complete: callback,
            progress: update_modal_size,
        });
    };

    var hide_element = function(elem, callback)
    {
        $(elem).slideUp({
            duration: 'fast',
            complete: callback,
            progress: update_modal_size,
        });
    };

    var simple_provider_action = function()
    {
        $(this).siblings('form').submit();
    };

    var clear_selected_input_provider = function()
    {
        hide_element('div.ksp_login_selected_input_provider', function()
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
        show_element(new_form);
    };

    var more_options_click = function()
    {
        $('#ksp_login_modal_box').modal({
            overlayClose: true,
        })
        $('.simplemodal-wrap').css({overflow: 'hidden'});
        return false;
    }

    $(document).on('click',
                   '.ksp_login_provider_list > .provider_simple > img',
                   simple_provider_action);
    $(document).on('click',
                   '.ksp_login_provider_list > .provider_with_input > img',
                   input_provider_action);

    $('.ksp_login_more').on('click', more_options_click);
})
