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
                calculateParlayOdds(); // Recalculate parlay odds after table update
            }
        });
    }

    $("#yes-button").click(function() {
        submitBetOutcome("yes");
    });

    $("#no-button").click(function() {
        submitBetOutcome("no");
    });

    calculateParlayOdds(); // Initial calculation on page load
});

$(document).ready(function() {
    $("td[data-utc-time]").each(function() {
        var utcTime = $(this).attr("data-utc-time");
        var localTime = new Date(utcTime + ' UTC').toLocaleString();
        $(this).text(localTime);
    });
});

function calculateParlayOdds() {
    let odds = [];
    $("#bet-outcome-form .table tbody tr").each(function() {
        const oddsValue = $(this).find('td:eq(4)').text(); // Assuming the 5th column contains the odds
        odds.push(parseInt(oddsValue));
    });

    if (odds.length < 2) {
        $("#parlay-odds-value").text("Need at least 2 bets for a parlay");
        $("#win-amount").text("N/A");  // Update the win amount text
        return;
    }

    let decimal = 1;
    odds.forEach(function(odd) {
        decimal *= convertD(odd);
    });

    decimal = (decimal * 100) - 100;
    let parlayOdds = Math.floor(decimal);
    $("#parlay-odds-value").text(parlayOdds);

    // Calculate the win amount for a $20 bet
    let winAmount = (parlayOdds / 100) * 20;
    $("#win-amount").text(winAmount.toFixed(2));  // Update the win amount text
}

function convertD(a) {
    let dec = 0.0;
    if (a > 0) {
        dec = (a / 100) + 1;
    } else {
        dec = 1 - (100 / a);
    }
    return dec;
}
