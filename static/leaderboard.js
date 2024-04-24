$(document).ready(function() {
    console.log("Leaderboard script is running");
    $.getJSON('/leaderboard_data', function(data) {
        var tableBody = $('#leaderboardTable tbody');
        tableBody.empty(); // Clear existing data
        data.forEach(function(row) {
            var profilePicHtml = row.profilePicUrl ?
                                 `<img src="${row.profilePicUrl}" alt="Profile Pic" style="width:30px; height:30px;">` :
                                 '<img src="https://mlb-app-stuff.s3.amazonaws.com/user-stuff/avatar/default-avatar.png" alt="Profile Pic" style="width:30px; height:30px;">';
            var newRow = `<tr>
                            <td>${profilePicHtml} ${row.bettorName}</td>
                            <td>${row.numberOfBets}</td>
                            <td>${row.wins}</td>
                            <td>${row.losses}</td>
                            <td>${row.currentStreak}</td>
                            <td>${row.longestStreak}</td>
                            <td>${row.mostBetPlayer}</td>
                            <td>${row.avgOdds.toFixed(1)}</td>
                            <td>${row.mostUsedBook}</td>
                          </tr>`;
            tableBody.append(newRow);
        });
    });
});
