document.querySelectorAll(
    ".evg-overlay,.evg-popup,#lgpd,#house-ad-link,.house-ad-link"
).forEach((e) => e.remove());

// Remove any element with a class that starts with styles__Container-sc-
document.querySelectorAll("[class^='styles__Container-sc-']").forEach((e) => e.remove());
