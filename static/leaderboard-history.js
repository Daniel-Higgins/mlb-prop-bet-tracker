$(document).ready(function() {
    console.log("Leaderboard script is running");

    var playerSelect = $('#playerSelect');

        // Fetch usernames and populate the dropdown
        function fetchUsernames() {
            $.getJSON('/get_usernames', function(usernames) {
                usernames.forEach(function(username) {
                    playerSelect.append(`<option value="${username}">${username}</option>`);
                });
            });
        }

    fetchUsernames();

    // Function to fetch and display a player's betting history
    function fetchPlayerHistory(player) {
        $.getJSON(`/player_history/${player}`, function(data) {
            var tableBody = $('#playerHistoryTable tbody');
            tableBody.empty(); // Clear existing data

            // Sort the data by date in descending order
            data.sort((a, b) => new Date(b.datePlaced) - new Date(a.datePlaced));

            // Append each sorted bet to the table
            data.forEach(function(bet) {
                var localDate = new Date(bet.datePlaced + ' UTC'); // Convert UTC to local date
                var newRow = `<tr>
                                <td>${localDate.toLocaleString()}</td> <!-- Display as local time -->
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


