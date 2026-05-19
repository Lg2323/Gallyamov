document.addEventListener("DOMContentLoaded", () => {
    initRevealAnimations();
    initSliders();
    initDialogs();
    initVenuePicker();
    initToasts();
});

function initRevealAnimations() {
    const items = document.querySelectorAll("[data-reveal]");

    if (!("IntersectionObserver" in window)) {
        items.forEach((item) => item.classList.add("is-visible"));
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.12 }
    );

    items.forEach((item) => observer.observe(item));
}

function initSliders() {
    const sliders = document.querySelectorAll("[data-slider]");

    sliders.forEach((slider) => {
        const track = slider.querySelector(".slider-card__track");
        const slides = slider.querySelectorAll(".slide");
        const prevButton = slider.querySelector("[data-slider-prev]");
        const nextButton = slider.querySelector("[data-slider-next]");

        if (!track || slides.length === 0) {
            return;
        }

        let currentIndex = 0;
        let intervalId = null;

        const render = () => {
            track.style.transform = `translateX(-${currentIndex * 100}%)`;
        };

        const moveNext = () => {
            currentIndex = (currentIndex + 1) % slides.length;
            render();
        };

        const movePrev = () => {
            currentIndex = (currentIndex - 1 + slides.length) % slides.length;
            render();
        };

        const start = () => {
            intervalId = window.setInterval(moveNext, 3000);
        };

        const stop = () => {
            if (intervalId) {
                window.clearInterval(intervalId);
            }
        };

        prevButton?.addEventListener("click", () => {
            stop();
            movePrev();
            start();
        });

        nextButton?.addEventListener("click", () => {
            stop();
            moveNext();
            start();
        });

        slider.addEventListener("mouseenter", stop);
        slider.addEventListener("mouseleave", start);

        render();
        start();
    });
}

function initDialogs() {
    const openButtons = document.querySelectorAll("[data-open-dialog]");
    const closeButtons = document.querySelectorAll("[data-close-dialog]");

    openButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.getAttribute("data-open-dialog");
            const dialog = document.getElementById(targetId);

            if (dialog && typeof dialog.showModal === "function") {
                dialog.showModal();
            }
        });
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const dialog = button.closest("dialog");
            dialog?.close();
        });
    });

    document.querySelectorAll("dialog").forEach((dialog) => {
        dialog.addEventListener("click", (event) => {
            const bounds = dialog.getBoundingClientRect();
            const isInDialog =
                bounds.top <= event.clientY &&
                event.clientY <= bounds.top + bounds.height &&
                bounds.left <= event.clientX &&
                event.clientX <= bounds.left + bounds.width;

            if (!isInDialog) {
                dialog.close();
            }
        });
    });
}

function initVenuePicker() {
    const venueSelect = document.getElementById("id_venue");
    const venueButtons = document.querySelectorAll("[data-select-venue]");

    if (!venueSelect || venueButtons.length === 0) {
        return;
    }

    venueButtons.forEach((button) => {
        button.addEventListener("click", () => {
            venueSelect.value = button.getAttribute("data-select-venue");
            venueSelect.dispatchEvent(new Event("change"));
            venueSelect.scrollIntoView({ behavior: "smooth", block: "center" });
            venueSelect.focus();
        });
    });
}

function initToasts() {
    document.querySelectorAll("[data-toast]").forEach((toast) => {
        window.setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(20px)";
            window.setTimeout(() => toast.remove(), 300);
        }, 3800);
    });
}
