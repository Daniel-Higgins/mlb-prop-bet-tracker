$(document).ready(function() {
    console.log("Leaderboard script is running");
    $.getJSON('/leaderboard_data', function(data) {
        var tableBody = $('#leaderboardTable tbody');
        tableBody.empty(); // Clear existing data
        data.forEach(function(row) {
            var newRow = `<tr>
                            <td>${row.bettorName}</td>
                            <td>${row.numberOfBets}</td>
                            <td>${row.wins}</td>
                            <td>${row.losses}</td>
                            <td>${row.winStreak}</td> <!-- Display win streak -->
                            <td>${row.mostBetPlayer}</td>
                            <td>${row.avgOdds.toFixed(2)}</td>
                            <td>${row.mostUsedBook}</td>
                          </tr>`;
            tableBody.append(newRow);
        });
    });
});


