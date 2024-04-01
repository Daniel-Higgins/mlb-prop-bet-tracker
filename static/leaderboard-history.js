$(document).ready(function() {
    console.log("Leaderboard script is running");
    // Populate the leaderboard as before
    // ...

    // Populate player selection dropdown
    var players = ['Higgins', 'Volz', 'Eddie', 'Mark', 'Danny D'];
    var playerSelect = $('#playerSelect');
    players.forEach(function(player) {
        playerSelect.append(`<option value="${player}">${player}</option>`);
    });

    // Function to fetch and display a player's betting history
    // Function to fetch and display a player's betting history
    function fetchPlayerHistory(player) {
        $.getJSON(`/player_history/${player}`, function(data) {
            var tableBody = $('#playerHistoryTable tbody');
            tableBody.empty(); // Clear existing data
            data.forEach(function(bet) {
                var newRow = `<tr>
                                <td>${bet.datePlaced}</td>
                                <td>${bet.outcome}</td>
                                <td>${bet.typeOfBet}</td>
                                <td>${bet.playerBetOn}</td>
                                <td>${bet.odds}</td>
                                <td>${bet.book}</td>
                              </tr>`;
                tableBody.append(newRow);
            });
        });
    }


    // Event handler for player selection
    $('#playerSelect').change(function() {
        var selectedPlayer = $(this).val();
        if (selectedPlayer) {
            fetchPlayerHistory(selectedPlayer);
        } else {
            $('#playerHistoryTable tbody').empty(); // Clear the table if no player is selected
        }
    });
});
