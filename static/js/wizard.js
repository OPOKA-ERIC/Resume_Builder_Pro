// Resume Builder Pro - Wizard Step Validation
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form[data-wizard-step]');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        let valid = true;
        const firstInvalid = form.querySelector('[required]');

        form.querySelectorAll('[required]').forEach(function (field) {
            field.classList.remove('is-invalid');
            if (!field.value.trim()) {
                valid = false;
                field.classList.add('is-invalid');
            }
        });

        if (!valid) {
            e.preventDefault();
            if (firstInvalid) {
                firstInvalid.focus();
            }
            const toast = document.getElementById('validationToast');
            if (toast) {
                const bsToast = bootstrap.Toast.getOrCreateInstance(toast);
                bsToast.show();
            }
        }
    });

    form.querySelectorAll('input, textarea, select').forEach(function (field) {
        field.addEventListener('input', function () {
            this.classList.remove('is-invalid');
        });
    });
});
