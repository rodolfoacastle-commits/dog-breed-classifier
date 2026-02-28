(function () {
  const form = document.getElementById('upload-form');
  const fileInput = document.getElementById('file-input');
  const submitBtn = document.getElementById('submit-btn');
  const loading = document.getElementById('loading');
  const resultContainer = document.getElementById('result');
  const uploadSection = document.getElementById('upload-section');

  function showLoading(show) {
    loading.classList.toggle('hidden', !show);
    submitBtn.disabled = show;
  }

  function showResult(html) {
    resultContainer.innerHTML = html;
    resultContainer.classList.add('visible');
    const tryAnother = resultContainer.querySelector('[data-try-another]');
    if (tryAnother) {
      tryAnother.addEventListener('click', function () {
        resultContainer.innerHTML = '';
        resultContainer.classList.remove('visible');
        fileInput.value = '';
      });
    }
  }

  function showError(message) {
    showResult(
      '<div class="result-card result-error">' +
        '<p class="error-message">' + escapeHtml(message) + '</p>' +
        '<button type="button" class="btn btn-secondary" data-try-another>Try another</button>' +
      '</div>'
    );
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function renderDog(data) {
    const breeds = data.breeds || [];
    const sweaters = data.sweaters || [];
    let breedsHtml = breeds.map(function (b) {
      const pct = Math.min(100, Math.max(0, b.percentage));
      return (
        '<div class="breed-item">' +
          '<div class="circular-progress" style="--pct: ' + pct + '" aria-label="' + escapeHtml(b.name) + ' ' + pct + '%">' +
            '<span class="circular-progress-value">' + pct + '%</span>' +
          '</div>' +
          '<span class="breed-name">' + escapeHtml(b.name) + '</span>' +
        '</div>'
      );
    }).join('');

    let sweatersHtml = '';
    if (sweaters.length) {
      sweatersHtml =
        '<section class="sweaters-section">' +
          '<h3>Recommended sweaters</h3>' +
          '<div class="sweaters-grid">' +
            sweaters.map(function (s) {
              return (
                '<a href="' + escapeHtml(s.product_url) + '" target="_blank" rel="noopener" class="sweater-card">' +
                  '<img src="' + escapeHtml(s.image_url) + '" alt="" width="200" height="200">' +
                  '<span class="sweater-name">' + escapeHtml(s.name) + '</span>' +
                  '<span class="sweater-price">' + escapeHtml(s.price) + '</span>' +
                '</a>'
              );
            }).join('') +
          '</div>' +
        '</section>';
    }

    const img = data.image
      ? '<img src="' + escapeHtml(data.image) + '" alt="Your upload" class="result-image">'
      : '';

    return (
      '<div class="result-card result-dog">' +
        img +
        '<h2>Top breeds</h2>' +
        '<div class="breeds-row">' + breedsHtml + '</div>' +
        sweatersHtml +
        '<button type="button" class="btn btn-secondary" data-try-another>Try another</button>' +
      '</div>'
    );
  }

  var barkAudio = null;

  function playBark() {
    var bark1 = new Audio('https://www.myinstants.com/media/sounds/dog-bark.mp3');
    bark1.volume = 0.7;
    bark1.play().catch(function () {});
    bark1.addEventListener('ended', function () {
      var bark2 = new Audio('https://www.myinstants.com/media/sounds/dog-bark.mp3');
      bark2.volume = 0.7;
      bark2.play().catch(function () {});
    });
  }

  function renderCat(data) {
    const message = data.message || 'No Cats Allowed!';
    var fallbackDataUrl = 'data:image/svg+xml,' + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">' +
      '<rect width="200" height="200" fill="#ddd6fe" rx="16" stroke="#7c3aed" stroke-width="3"/>' +
      '<text x="100" y="118" font-size="72" text-anchor="middle">🐕</text>' +
      '</svg>'
    );
    var gifUrl = 'https://media.giphy.com/media/26uf43dkw9ByWsjLi/giphy.gif';
    playBark();
    return (
      '<div class="result-card result-cat">' +
        '<div class="easter-egg-gif-wrap">' +
          '<img src="' + gifUrl + '" alt="No cats allowed" class="easter-egg-gif" onerror="this.onerror=null; this.src=\'' + fallbackDataUrl + '\';" />' +
        '</div>' +
        '<h2 class="easter-egg-title">' + escapeHtml(message) + '</h2>' +
        '<button type="button" class="btn btn-secondary" data-try-another>Try another</button>' +
      '</div>'
    );
  }

  function renderOther(data) {
    const message = data.message || "This doesn't look like a dog. Try uploading a photo of a dog for the best results.";
    const img = data.image
      ? '<img src="' + escapeHtml(data.image) + '" alt="Your upload" class="result-image">'
      : '';
    return (
      '<div class="result-card result-other">' +
        img +
        '<p class="result-message">' + escapeHtml(message) + '</p>' +
        '<button type="button" class="btn btn-secondary" data-try-another>Try another</button>' +
      '</div>'
    );
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!fileInput.files || !fileInput.files[0]) {
      showError('Please choose a file.');
      return;
    }

    const fd = new FormData();
    fd.append('file', fileInput.files[0]);

    showLoading(true);
    resultContainer.innerHTML = '';
    resultContainer.classList.remove('visible');

    fetch('/api/predict', {
      method: 'POST',
      body: fd,
    })
      .then(function (res) {
        return res.text().then(function (text) {
          var json;
          try {
            json = text ? JSON.parse(text) : {};
          } catch (e) {
            throw new Error(res.ok ? 'Invalid response from server.' : 'The server could not process your request. Try again or use a different image.');
          }
          if (!res.ok) {
            throw new Error(json.error || (res.status === 500 ? 'Something went wrong on our end. Please try again.' : 'Something went wrong.'));
          }
          return json;
        });
      })
      .then(function (json) {
        if (json.is_dog) {
          showResult(renderDog(json));
        } else if (json.is_cat) {
          showResult(renderCat(json));
        } else {
          showResult(renderOther(json));
        }
      })
      .catch(function (err) {
        showError(err.message || 'Upload failed. Please try again.');
      })
      .finally(function () {
        showLoading(false);
      });
  });
})();
