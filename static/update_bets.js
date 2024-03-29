// update_bets.js
$(document).ready(function() {
    function submitBetOutcome(outcome) {
        $("#bet-outcome").val(outcome);
        $.ajax({
            type: "POST",
            url: $("#bet-outcome-form").attr("action"),
            data: $("#bet-outcome-form").serialize(),
            success: function(data) {
                // Refresh the table content
                var newTbody = $("<table>").html(data).find("tbody");
                $(".table-responsive .table tbody").replaceWith(newTbody);
            }
        });
    }

    $("#yes-button").click(function() {
        submitBetOutcome("yes");
    });

    $("#no-button").click(function() {
        submitBetOutcome("no");
    });
});
