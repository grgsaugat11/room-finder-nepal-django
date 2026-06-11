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