$(function () {
    $('.widget-input-integer').each(function () {
        var widget = $(this);
        var options = {
            allowMinus: false
        };

        if(widget.data('allowMinus'))
            options.allowMinus = true;

        widget.find('input').inputmask('integer', options);
    });
});