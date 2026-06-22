document.addEventListener('DOMContentLoaded', function () {
    const provinceSelect = document.getElementById('province-select');
    const districtSelect = document.getElementById('district-select');

    if (!provinceSelect || !districtSelect) {
        return;
    }

    const selectedDistrict = districtSelect.dataset.selected || '';

    function loadDistricts(provinceId, selectedDistrictId = '') {
        districtSelect.innerHTML = '<option value="">Loading districts...</option>';

        let url = '/ajax/load-districts/';

        if (provinceId) {
            url += `?province_id=${provinceId}`;
        }

        fetch(url)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('Failed to load districts');
                }

                return response.json();
            })
            .then(function (data) {
                districtSelect.innerHTML = '<option value="">All Districts</option>';

                data.districts.forEach(function (district) {
                    const option = document.createElement('option');
                    option.value = district.id;

                    if (provinceId) {
                        option.textContent = district.name;
                    } else {
                        option.textContent = `${district.name} — ${district.province}`;
                    }

                    if (String(district.id) === String(selectedDistrictId)) {
                        option.selected = true;
                    }

                    districtSelect.appendChild(option);
                });
            })
            .catch(function (error) {
                console.error('District loading error:', error);
                districtSelect.innerHTML = '<option value="">Could not load districts</option>';
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

document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("propertyImages");
    const preview = document.getElementById("selectedImagePreview");
    const modal = document.getElementById("imagePreviewModal");
    const modalImg = document.getElementById("expandedImagePreview");
    const closeModal = document.getElementById("closeImagePreview");

    if (!input || !preview) return;

    let selectedFiles = [];

    input.addEventListener("change", function () {
        const newFiles = Array.from(input.files);

        newFiles.forEach(file => {
            const alreadyExists = selectedFiles.some(existingFile =>
                existingFile.name === file.name &&
                existingFile.size === file.size &&
                existingFile.lastModified === file.lastModified
            );

            if (!alreadyExists) {
                selectedFiles.push(file);
            }
        });

        updateInputFiles();
        renderPreview();
    });

    function updateInputFiles() {
        const dataTransfer = new DataTransfer();

        selectedFiles.forEach(file => {
            dataTransfer.items.add(file);
        });

        input.files = dataTransfer.files;
    }

    function renderPreview() {
        preview.innerHTML = "";

        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();

            reader.onload = function (event) {
                const item = document.createElement("div");
                item.className = "selected-image-item";

                const img = document.createElement("img");
                img.src = event.target.result;
                img.alt = file.name;

                img.addEventListener("click", function () {
                    modalImg.src = event.target.result;
                    modal.classList.add("show");
                });

                const removeBtn = document.createElement("button");
                removeBtn.type = "button";
                removeBtn.className = "remove-selected-image";
                removeBtn.innerHTML = "&times;";

                removeBtn.addEventListener("click", function () {
                    selectedFiles.splice(index, 1);
                    updateInputFiles();
                    renderPreview();
                });

                item.appendChild(img);
                item.appendChild(removeBtn);
                preview.appendChild(item);
            };

            reader.readAsDataURL(file);
        });
    }

    closeModal.addEventListener("click", function () {
        modal.classList.remove("show");
        modalImg.src = "";
    });

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.classList.remove("show");
            modalImg.src = "";
        }
    });
});