document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (searchInput && searchResults) {
        let searchTimeout;

        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length < 2) {
                searchResults.innerHTML = '';
                searchResults.style.display = 'none';
                return;
            }

            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });

        function performSearch(query) {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', `/ajax-search/?query=${encodeURIComponent(query)}`, true);

            xhr.onload = function () {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    displayResults(response.results);
                }
            };

            xhr.send();
        }

        function displayResults(results) {
            if (results.length === 0) {
                searchResults.innerHTML = `
                    <div class="alert alert-warning text-center">
                        <i class="bi bi-search"></i> ‘ильмы не найдены
                    </div>
                `;
                searchResults.style.display = 'block';
                return;
            }

            let html = '<div class="list-group">';
            results.forEach(movie => {
                html += `
                    <a href="/?query=${encodeURIComponent(movie.title)}" 
                       class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${movie.title}</h6>
                            <small class="text-success">${movie.rating}/10</small>
                        </div>
                        <p class="mb-1 small">
                            <i class="bi bi-person"></i> ${movie.director} Х 
                            <i class="bi bi-calendar"></i> ${movie.year} Х 
                            <i class="bi bi-tags"></i> ${movie.genre}
                        </p>
                    </a>
                `;
            });
            html += '</div>';

            searchResults.innerHTML = html;
            searchResults.style.display = 'block';
        }

        // —крываем результаты при клике вне области
        document.addEventListener('click', function (e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });

        // ќбработка Enter
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                const query = this.value.trim();
                if (query) {
                    window.location.href = `/?query=${encodeURIComponent(query)}`;
                }
            }
        });
    }
});