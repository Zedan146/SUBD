// Обработка фильтрации заказов
document.querySelectorAll('.filter-buttons .btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.filter-buttons .btn').forEach(b => {
            b.classList.remove('btn-active');
        });
        this.classList.add('btn-active');

        // Здесь будет логика фильтрации заказов
        console.log('Фильтруем заказы по:', this.textContent);
    });
});

// AJAX поиск клиентов
document.getElementById('id_client_search').addEventListener('input', function(e) {
    const query = e.target.value;
    if (query.length < 2) return;

    fetch(`/api/clients/?search=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const results = document.getElementById('client-results');
            results.innerHTML = '';

            if (data.length) {
                data.forEach(client => {
                    const item = document.createElement('div');
                    item.className = 'autocomplete-item';
                    item.textContent = `${client.surname} ${client.name} (${client.phone})`;
                    item.dataset.id = client.id;
                    item.addEventListener('click', () => {
                        document.getElementById('id_client').value = client.id;
                        document.getElementById('id_client_search').value =
                            `${client.surname} ${client.name}`;
                        results.style.display = 'none';
                    });
                    results.appendChild(item);
                });
                results.style.display = 'block';
            } else {
                results.style.display = 'none';
            }
        });
});

document.querySelectorAll('.order-content').forEach(link => {
    link.addEventListener('click', function(e) {
        // Дополнительные действия при клике, если нужно
        console.log('Переход к деталям заказа');
    });
});