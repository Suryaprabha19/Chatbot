document.getElementById('predictionForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const quantity_sold = document.getElementById('quantity_sold').value;
    const discount = document.getElementById('discount').value;
    const profit = document.getElementById('profit').value;
    const launch_month = document.getElementById('launch_month').value;
    const rating = document.getElementById('rating').value;

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            quantity_sold: quantity_sold,
            discount: discount,
            profit: profit,
            launch_month: launch_month,
            rating: rating,
        }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').innerText = 'Predicted Sales Amount: ' + data.prediction;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
