var myVar = setInterval(myTimer, 1000);

// Store the previous values for fields that should be updated
var previousValues = {
    mute: null,
    blend: null,
    frequency: null,
    rdsps: null,
    rdsrt: null
};

function myTimer() {
    $.getJSON("/status", function (data) {
        $.each(data, function (key, val) {
            // Check if the value has changed
            if (val !== previousValues[key]) {

                if (key == "mute" || key == "blend") {
                    var checkbox = document.getElementsByName(key);
                    checkbox[0].checked = (val === "Enabled");
                }

                if (key == "frequency") {
                    var span = document.getElementById('frequency-span');
                    var input = document.getElementById('aligned-name');
                    span.innerHTML = val;
                    input.value = val;
                }

                if (key == "rdsps") {
                    var rdspsSpan = document.getElementById('rdsps');
                    rdspsSpan.innerHTML = val;
                }

                if (key == "rdsrt") {
                    var rdsrtSpan = document.getElementById('rdsrt');
                    rdsrtSpan.innerHTML = val;
                }

                // Update the previous value
                previousValues[key] = val;
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