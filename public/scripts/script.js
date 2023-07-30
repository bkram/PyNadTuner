var myVar = setInterval(myTimer, 1000);
let items = "";
function myTimer() {
    $.getJSON("/status", function (data) {
        var items = [];
        $.each(data, function (key, val) {
            $('#' + key).html(val)
            if (key == "mute") {
                var mute = document.getElementsByName('mute');
                if (val == "Enabled") {
                    var mute = document.getElementsByName('mute');
                    mute[0].checked = 'True';
                }
                else {
                    mute[0].checked = '';
                }
            }
            if (key == "blend") {
                var mute = document.getElementsByName('blend');
                if (val == "Enabled") {
                    var mute = document.getElementsByName('blend');
                    mute[0].checked = 'True';
                }
                else {
                    mute[0].checked = '';
                }
            }

        });
    });

}

function tune(step) {
    fetch("/tune?step=" + step);
}

function set_mute() {
    var mute = document.getElementsByName('mute');

    if (mute[0].checked) {
        fetch("/mute?mute=on")
    }
    else {
        fetch("/mute?mute=off")
    }

}

function set_blend() {
    var blend = document.getElementsByName('blend');

    if (blend[0].checked) {
        fetch("/blend?blend=on")
    }
    else {
        fetch("/blend?blend=off")
    }

}