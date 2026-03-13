// ResumeForge JavaScript
document.addEventListener("DOMContentLoaded", function() {
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll(".alert-dismissible").forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm before dangerous actions
    document.querySelectorAll("[data-confirm]").forEach(function(el) {
        el.addEventListener("click", function(e) {
            if (!confirm(el.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
});
