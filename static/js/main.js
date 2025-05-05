document.addEventListener('DOMContentLoaded', () => {
  const fileInput  = document.getElementById('fileInput');
  const processBtn = document.getElementById('processBtn');
  const outputDiv  = document.getElementById('output');

  processBtn.addEventListener('click', () => {
    const file = fileInput.files[0];
    if (!file) {
      return alert('Пожалуйста, выберите изображение.');
    }

    const form = new FormData();
    form.append('file', file);

    fetch('/process-image', { method: 'POST', body: form })
      .then(res => res.json())
      .then(data => {
        if (data.error) throw data.error;
        outputDiv.innerHTML = `
          <h5>Найдено судов: <strong>${data.count}</strong></h5>
          <img src="${data.image}" alt="Результат детекции">
        `;
      })
      .catch(err => {
        console.error(err);
        alert('Ошибка при обработке изображения.');
      });
  });
});
