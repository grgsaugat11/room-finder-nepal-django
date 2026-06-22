document.addEventListener('DOMContentLoaded', function () {
    const filterPairs = [
        {
            province: document.getElementById('id_province'),
            district: document.getElementById('id_district'),
            emptyText: '---------'
        },
        {
            province: document.getElementById('province-select'),
            district: document.getElementById('district-select'),
            emptyText: 'All Districts'
        }
    ];

    filterPairs.forEach(function (pair) {
        if (!pair.province || !pair.district) return;

        const selectedDistrict = pair.district.dataset.selected || pair.district.value || '';

        function loadDistricts(provinceId, keepSelectedDistrict = '') {
            const url = '/ajax/load-districts/?province_id=' + encodeURIComponent(provinceId || '');

            fetch(url)
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    pair.district.innerHTML = '';

                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.textContent = pair.emptyText;
                    pair.district.appendChild(defaultOption);

                    data.districts.forEach(function (district) {
                        const option = document.createElement('option');
                        option.value = district.id;
                        option.textContent = provinceId || !district.province
                            ? district.name
                            : district.name + ' — ' + district.province;

                        if (String(district.id) === String(keepSelectedDistrict)) {
                            option.selected = true;
                        }

                        pair.district.appendChild(option);
                    });
                });
        }

        pair.province.addEventListener('change', function () {
            loadDistricts(this.value);
        });

        loadDistricts(pair.province.value, selectedDistrict);
    });
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
        if (wrapper.classList.contains('property-images-upload')) return;

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

document.addEventListener('DOMContentLoaded', function () {
    const toastMessages = document.querySelectorAll('.toast-message');

    toastMessages.forEach(function (toast) {
        let duration = 3000;

        if (toast.classList.contains('error')) {
            duration = 7000;
        }

        if (toast.classList.contains('warning')) {
            duration = 5000;
        }

        const progress = toast.querySelector('.toast-progress');

        if (progress) {
            progress.style.animationDuration = duration + 'ms';
        }

        const removeToast = function () {
            toast.classList.add('toast-hide');

            setTimeout(function () {
                toast.remove();
            }, 300);
        };

        const timer = setTimeout(removeToast, duration);

        const closeBtn = toast.querySelector('.toast-close');

        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                clearTimeout(timer);
                removeToast();
            });
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const mainNav = document.getElementById('main-nav');

    if (!hamburgerBtn || !mainNav) {
        return;
    }

    hamburgerBtn.addEventListener('click', function () {
        hamburgerBtn.classList.toggle('active');
        mainNav.classList.toggle('show');
    });

    mainNav.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
            hamburgerBtn.classList.remove('active');
            mainNav.classList.remove('show');
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const uploadBox = document.querySelector('.property-images-upload');
    if (!uploadBox) return;

    const imageInput = uploadBox.querySelector('input[type="file"]');
    const fileNameText = uploadBox.querySelector('.selected-file-name');
    const previewBox = uploadBox.querySelector('.property-image-preview-grid');

    if (!imageInput || !previewBox) return;

    const maxImages = 15;
    let selectedImages = [];

    imageInput.multiple = true;

    uploadBox.addEventListener('click', function (event) {
        if (event.target.closest('.property-image-remove-btn')) return;
        if (event.target.closest('.property-image-preview-card')) return;

        imageInput.click();
    });

    previewBox.addEventListener('click', function (event) {
        const removeBtn = event.target.closest('.property-image-remove-btn');

        if (!removeBtn) return;

        event.preventDefault();
        event.stopPropagation();

        const index = Number(removeBtn.dataset.index);

        selectedImages.splice(index, 1);
        syncInputFiles();
        renderSelectedImages();
    }, true);

    imageInput.addEventListener('change', function () {
        Array.from(imageInput.files).forEach(function (file) {
            const exists = selectedImages.some(function (oldFile) {
                return oldFile.name === file.name &&
                    oldFile.size === file.size &&
                    oldFile.lastModified === file.lastModified;
            });

            if (!exists && selectedImages.length < maxImages) {
                selectedImages.push(file);
            }
        });

        syncInputFiles();
        renderSelectedImages();
    });

    function syncInputFiles() {
        const dataTransfer = new DataTransfer();

        selectedImages.forEach(function (file) {
            dataTransfer.items.add(file);
        });

        imageInput.files = dataTransfer.files;
    }

    function renderSelectedImages() {
        previewBox.innerHTML = '';

        if (fileNameText) {
            fileNameText.textContent = selectedImages.length
                ? selectedImages.length + ' files selected'
                : 'No files selected';
        }

        selectedImages.forEach(function (file, index) {
            const reader = new FileReader();

            reader.onload = function (event) {
                const card = document.createElement('div');
                card.className = 'property-image-preview-card';

                const img = document.createElement('img');
                img.src = event.target.result;
                img.alt = file.name;

                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'property-image-remove-btn';
                removeBtn.dataset.index = index;
                removeBtn.textContent = '×';

                card.appendChild(img);
                card.appendChild(removeBtn);
                previewBox.appendChild(card);
            };

            reader.readAsDataURL(file);
        });
    }
});