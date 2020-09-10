const api1 = '/data';
const api2 = '/data2';
let url_id;


function goBtnHandler(e) {
   
    let url = $('#url').val();

    if (url == "") {
        $('.loading').show();
        $("#loadingblock > strong").text("URL is compulsory")
        return false;
    }

    if (!url.match(new RegExp(/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi))) {
        $('.loading').show();
        $("#loadingblock > strong").text("Please enter a valid URL")
        return false;
    }

    $.ajax({
        type: 'POST',
        url: api1,
        data: JSON.stringify({
            url: $('#url').val()
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        beforeSend: function(xhr) {
            $('#url').prop("disabled", true);
            $("#clearBtn1").prop("disabled", true);
            $("#clearBtn2").prop("disabled", true);
            $(".loading").hide();
            $("#questionBlock").hide();
            console.log({
                "url": $('#url').val()
            });
        },
        success: function(result) {
            if (result.status == 0) {
                $('.loading').show();
                $("#loadingblock > strong").text("Sorry, the server could not parse the input");
                $('#url').prop("disabled", false);
                $("#clearBtn1").prop("disabled", false);
                $("#clearBtn2").prop("disabled", false);
                $('#url').focus();
                return;
            }
            $('#url_id').val(result.id);
            url_id = result.id;
            console.log('Got', result);
            $('#questionBlock').show();
            $("#url").prop("disabled", false);
            $("#clearBtn1").prop("disabled", false);
            $("#clearBtn2").prop("disabled", false);
            $(".question").val("");
            $(".answer").remove("*");
            $("#goBtn").hide();
        },
        timeout: 500000,
        error: function(jqXHR, textStatus, error) {
            $('.loading').show();
            $("#loadingblock > strong").text("Invalid request");
            $('#url').prop("disabled", false);
            console.log('error');
        }
    });

    setTimeout(function() {
        $("#question").focus();
    }, 20);

    return false;
}

function submitHandler(e) {
    var url = $("#url").val();
    var q1 = $("#question").val();
    console.log(url_id);

    if (url == "" || q1 == "") {
        $('.loading').show();
        $("#loadingblock > strong").text("URL and question are compulsory")
        return false;
    }

    if (!url.match(new RegExp(/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi))) {
        $('.loading').show();
        $("#loadingblock > strong").text("Please enter a valid URL")
        return false;
    }


    let formData = new FormData(document.getElementById('mainForm'));
    console.log(JSON.stringify(Object.fromEntries(formData)));
    $.ajax({
        type: 'POST',
        url: api2,
        data: JSON.stringify(Object.fromEntries(formData)),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        beforeSend: function(xhr) {
            console.log(JSON.stringify(Object.fromEntries(formData)));
            $("#submitblock").hide();
            $(".loading").show();
            $("#loadingblock > strong").text("Your data is being processed. Please wait.");
            $(".answer").hide();
            $("#url").prop("disabled", true);
            $("#question").prop("disabled", true);
            $("#clearBtn1").prop("disabled", true);
            $("#clearBtn2").prop("disabled", true);
            $(".answer").remove();
        },
        success: function(result) {
            console.log(result);
            $('.answer').show();
            $("#submitblock").show();
            $(".loading").hide();
            $("#url").prop("disabled", false);
            $("#question").prop("disabled", false);
            $("#clearBtn1").prop("disabled", false);
            $("#clearBtn2").prop("disabled", false);
            for (let ans of result.data) {
                try {
                    ans.confidence = ans.confidence;
                    answer = ans.answer[0].toUpperCase() + ans.answer.substr(1);
                    let t = '<h5><b>' + answer + '</b></h5><p>Confidence: ' + ans.confidence + '</p>';
                    $('<div class="alert alert-info answer">' + t + '</div>').appendTo($('#questionBlock'));
                }
                catch (err) {
                    console.log(err);
                    let t = '<h5><b>' + ans.answer + '</b></h5><p>Confidence: ' + ans.confidence + '</p>';
                    $('<div class="alert alert-info answer">' + t + '</div>').appendTo($('#questionBlock'));
                }
                   
            }

            $("#question").focus();
        },
        timeout: 500000,
        error: function(jqXHR, textStatus, error) {
            console.log(textStatus, error);
            $("#submitblock").show();
            $(".answer").hide();
            $("#url").prop("disabled", false);
            $("#question").prop("disabled", false);
            $("#clearBtn1").prop("disabled", false);
            $("#clearBtn2").prop("disabled", false);
            $("#loadingblock > strong").text("Currently the test server is down. Please try again after sometime. Sorry for inconvenience.")
            $("#submitBtn").val("Try Again")
        }
    });

    return false;
}

function clearAll(e) {
    $(".loading").hide();
    $("#url").val("");
    $("#questionBlock").hide();
    $('#question').val('');
    $('.answer').remove('*');
    $("#url").focus();
    $("#goBtn").show();
}

function clearResults(e) {
    $(".loading").hide();
    $('#question').val('').focus();
    $('.answer').remove('*');
}

$('document').ready(function() {
    // $("#url").focus();
    // $('.loading').hide();
    // $("#submitblock").show();
    // $(".answer").hide();
    // $('#questionBlock').hide();

    clearAll();

    $("#goBtn").click(goBtnHandler);
    $('#url').keypress(function(e) {
        let key = e.which;
        if (key == 13) {
            $("#goBtn").click();
        }
    });
    $("#submitBtn").click(submitHandler);
    $("#question").keypress(function(e) {
        let = key = e.which;
        if (key == 13) {
            $("#submitBtn").click();
        }
    });

    $('#clearBtn1').click(clearAll);
    $('#clearBtn2').click(clearResults);
});
