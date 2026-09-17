(() => {
    const sidebar = document.getElementById("sidebar");
    const toggle = document.getElementById("menuToggle");
    const overlay = document.getElementById("sidebarOverlay");

    const setSidebar = (open) => {
        if (!sidebar || !toggle) return;
        sidebar.classList.toggle("is-open", open);
        document.body.classList.toggle("nav-open", open);
        toggle.setAttribute("aria-expanded", String(open));
    };

    toggle?.addEventListener("click", () => {
        setSidebar(!sidebar.classList.contains("is-open"));
    });
    overlay?.addEventListener("click", () => setSidebar(false));
    window.addEventListener("keydown", (event) => {
        if (event.key === "Escape") setSidebar(false);
    });

    document.querySelectorAll(".message-close").forEach((button) => {
        button.addEventListener("click", () => button.closest(".message")?.remove());
    });

    window.setTimeout(() => {
        document.querySelectorAll(".message").forEach((message) => {
            message.classList.add("is-leaving");
            window.setTimeout(() => message.remove(), 250);
        });
    }, 6000);
})();

