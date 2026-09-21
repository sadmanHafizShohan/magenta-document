const input = document.querySelector('#files');
const dropzone = document.querySelector('#dropzone');
const fileList = document.querySelector('#file-list');
const threshold = document.querySelector('#threshold');
const thresholdValue = document.querySelector('#threshold-value');
const border = document.querySelector('#border');
const borderValue = document.querySelector('#border-value');

function showFiles(files) {
  fileList.innerHTML = '';
  [...files].forEach((file) => {
    const row = document.createElement('div');
    row.className = 'file-row';
    row.innerHTML = `<span class="file-dot"></span><span>${file.name}</span><small>${(file.size / 1024 / 1024).toFixed(2)} MB</small>`;
    fileList.appendChild(row);
  });
}

input.addEventListener('change', () => showFiles(input.files));
['dragenter', 'dragover'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropzone.classList.add('is-dragging');
}));
['dragleave', 'drop'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropzone.classList.remove('is-dragging');
}));
dropzone.addEventListener('drop', (event) => {
  input.files = event.dataTransfer.files;
  showFiles(input.files);
});
threshold.addEventListener('input', () => { thresholdValue.textContent = threshold.value; });
border.addEventListener('input', () => { borderValue.textContent = `${border.value} px`; });
