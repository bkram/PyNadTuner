var myVar = setInterval(myTimer, 1000);
let items = "";
function myTimer() {
    document.getElementsByName("frequency").placeholder = "Type name here..";
    $.getJSON("/status", function (data) {
        var items = [];
        $.each(data, function (key, val) {
            // console.log(key + " " + val)
            $('#' + key).html(val)
        });
    });
}

function tune(step) {
    fetch("/tune?step=" + step);
}
