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

function setFiles(files) {
  const fileTransfer = new DataTransfer();
  [...files].forEach((file) => fileTransfer.items.add(file));
  input.files = fileTransfer.files;
  showFiles(input.files);
}

input.addEventListener('change', () => showFiles(input.files));
document.addEventListener('paste', (event) => {
  const imageItem = [...event.clipboardData.items].find((item) => item.type.startsWith('image/'));
  if (!imageItem) return;

  event.preventDefault();
  const image = imageItem.getAsFile();
  if (image) {
    setFiles([new File([image], `pasted-image.${image.type.split('/')[1] || 'png'}`, { type: image.type })]);
    dropzone.classList.add('has-paste');
    window.setTimeout(() => dropzone.classList.remove('has-paste'), 900);
  }
});
['dragenter', 'dragover'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropzone.classList.add('is-dragging');
}));
['dragleave', 'drop'].forEach((eventName) => dropzone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropzone.classList.remove('is-dragging');
}));
dropzone.addEventListener('drop', (event) => {
  setFiles(event.dataTransfer.files);
});
threshold.addEventListener('input', () => { thresholdValue.textContent = threshold.value; });
border.addEventListener('input', () => { borderValue.textContent = `${border.value} px`; });
