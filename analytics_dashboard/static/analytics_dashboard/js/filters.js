function updateGraphs() {
    const filter = document.getElementById('timeFilter').value;

    // Reload the page with selected filter as a query parameter
    window.location.href = `?filter=${filter}`;
}
