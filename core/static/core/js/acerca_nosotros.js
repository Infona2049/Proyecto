document.addEventListener("DOMContentLoaded", () => {
  // Dropdown de usuario
  const dropdownToggle = document.querySelector(".usuario");
  const dropdownMenu = document.querySelector(".dropdown-usuario");

  if (dropdownToggle && dropdownMenu) {
    dropdownToggle.addEventListener("click", (e) => { 
      e.stopPropagation();
      dropdownMenu.classList.toggle("visible");
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".usuario-container")) {
        dropdownMenu.classList.remove("visible");
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        dropdownMenu.classList.remove("visible");
      }
    });
  }

  // Dropdown configuración (engranaje)
  const configToggle = document.querySelector(".config-toggle");
  const configMenu = document.querySelector(".dropdown-config");

  if (configToggle && configMenu) {
    configToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      configMenu.style.display = configMenu.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".config-container")) {
        configMenu.style.display = "none";
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        configMenu.style.display = "none";
      }
    });

    const idiomaButtons = document.querySelectorAll(".config-option");

    idiomaButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        idiomaButtons.forEach(b => {
          b.classList.remove("active");
          const icon = b.querySelector("i");
          if (icon) icon.className = "fi fi-rs-circle";
        });

        btn.classList.add("active");
        const icon = btn.querySelector("i");
        if (icon) icon.className = "fi fi-rs-circle-dot";
      });
    });
  }

  // Submenú "Registro empresa"
  const toggle = document.querySelector(".submenu-titulo");
  const submenu = document.querySelector(".submenu");

  if (toggle && submenu) {
    toggle.addEventListener("click", (e) => {
      e.preventDefault();
      submenu.style.display = submenu.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".submenu-container")) {
        submenu.style.display = "none";
      }
    });
  }
});
