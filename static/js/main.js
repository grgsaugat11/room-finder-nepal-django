document.addEventListener('DOMContentLoaded', function () {
    const provinceSelect = document.getElementById('province-select');
    const districtSelect = document.getElementById('district-select');

    if (!provinceSelect || !districtSelect) {
        return;
    }

    function loadDistricts(provinceId, selectedDistrictId = '') {
        districtSelect.innerHTML = '<option value="">Loading...</option>';

        if (!provinceId) {
            districtSelect.innerHTML = '<option value="">All Districts</option>';
            return;
        }

        fetch(`/ajax/load-districts/?province_id=${provinceId}`)
            .then(response => response.json())
            .then(data => {
                districtSelect.innerHTML = '<option value="">All Districts</option>';

                data.districts.forEach(district => {
                    const option = document.createElement('option');
                    option.value = district.id;
                    option.textContent = district.name;

                    if (String(district.id) === String(selectedDistrictId)) {
                        option.selected = true;
                    }

                    districtSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error loading districts:', error);
                districtSelect.innerHTML = '<option value="">All Districts</option>';
            });
    }

    provinceSelect.addEventListener('change', function () {
        loadDistricts(this.value);
    });

    if (provinceSelect.value) {
        loadDistricts(provinceSelect.value, selectedDistrict);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const passwordButtons = document.querySelectorAll('.password-toggle');

    passwordButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const wrapper = button.closest('.password-field');
            const input = wrapper.querySelector('input');

            if (!input) return;

            if (input.type === 'password') {
                input.type = 'text';
                button.textContent = '🙈';
                button.setAttribute('aria-label', 'Hide password');
            } else {
                input.type = 'password';
                button.textContent = '👁';
                button.setAttribute('aria-label', 'Show password');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const confirmElements = document.querySelectorAll('[data-confirm]');

    confirmElements.forEach(function (element) {
        element.addEventListener('click', function (event) {
            const message = element.getAttribute('data-confirm') || 'Are you sure you want to do this?';

            if (!confirm(message)) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('profile-modal');
    const openBtn = document.querySelector('.profile-modal-open');
    const closeBtn = document.querySelector('.profile-modal-close');

    if (!modal || !openBtn || !closeBtn) return;

    openBtn.addEventListener('click', function () {
        modal.classList.add('show');
    });

    closeBtn.addEventListener('click', function () {
        modal.classList.remove('show');
    });

    modal.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.classList.remove('show');
        }
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            modal.classList.remove('show');
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const uploadWrappers = document.querySelectorAll('.file-upload-wrapper');

    uploadWrappers.forEach(function (wrapper) {
        const input = wrapper.querySelector('input[type="file"]');
        const fileNameText = wrapper.querySelector('.selected-file-name');
        const previewBox = wrapper.querySelector('.selected-image-preview');

        if (!input || !fileNameText) return;

        input.addEventListener('change', function () {
            const files = Array.from(input.files);

            if (files.length === 0) {
                fileNameText.textContent = input.multiple ? 'No files selected' : 'No file selected';
                wrapper.classList.remove('file-selected');

                if (previewBox) {
                    previewBox.innerHTML = '';
                }

                return;
            }

            wrapper.classList.add('file-selected');

            if (files.length === 1) {
                fileNameText.textContent = `Selected: ${files[0].name}`;
            } else {
                fileNameText.textContent = `${files.length} files selected`;
            }

            if (!previewBox) return;

            previewBox.innerHTML = '';

            files.slice(0, 4).forEach(function (file) {
                if (!file.type.startsWith('image/')) return;

                const reader = new FileReader();

                reader.onload = function (event) {
                    const img = document.createElement('img');
                    img.src = event.target.result;
                    img.alt = file.name;
                    previewBox.appendChild(img);
                };

                reader.readAsDataURL(file);
            });

            if (files.length > 4) {
                const moreText = document.createElement('span');
                moreText.className = 'more-files-count';
                moreText.textContent = `+${files.length - 4} more`;
                previewBox.appendChild(moreText);
            }
        });
    });
});