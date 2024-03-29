function matchStart(params, data) {
    // If there are no search terms, return all of the data
    if ($.trim(params.term) === '') {
      return data;
    }

    // Skip if there is no 'text' to compare
    if (typeof data.text === 'undefined') {
      return null;
    }

    // Check if the data begins with the search term
    if (data.text.toUpperCase().startsWith(params.term.toUpperCase())) {
      return data;
    }

    // Return `null` if the term should not be displayed
    return null;
}

$(document).ready(function() {
    $('#player').select2({
        matcher: matchStart,
        placeholder: "Select a player",
        allowClear: true,
        width: '100%'
    });
});
