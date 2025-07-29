const API_URL = "http://localhost:8000"; // backend URL

// NOSONAR
$(document).ready(function () {
  // NOSONAR

  // Set up event listeners for mouse enter/leave sidebar
  const SIDEBAR_EL = document.getElementById("wrapper");
  initMenu();

  document
    .getElementById("sidebar-wrapper")
    .addEventListener("mouseenter", function () {
      SIDEBAR_EL.classList.remove("collapsed");
    });
  document
    .getElementById("sidebar-wrapper")
    .addEventListener("mouseleave", function () {
      SIDEBAR_EL.classList.add("collapsed");
    });

  // Datepicker initialization
  $("#date-picker").datepicker({
    format: "yyyy-mm-dd",
    autoclose: true,
    todayHighlight: true,
    todayBtn: true,
    clearBtn: true,
    calendarWeeks: true,
    orientation: "right",
  });

  $("#date-picker").on("show", function () {
    // Wait until datepicker is actually in the DOM
    setTimeout(function () {
      const datepickerDiv = document.querySelector(
        ".datepicker.datepicker-dropdown"
      );
      if (datepickerDiv) {
        datepickerDiv.addEventListener("mouseenter", function () {
          SIDEBAR_EL.classList.remove("collapsed");
        });
        datepickerDiv.addEventListener("mouseleave", function () {
          SIDEBAR_EL.classList.add("collapsed");
        });
      }
    }, 0);
  });

  let dateOBs = {};

  // Fetch the OB-Date mapping from the JSON file
  // This is used to populate the OB dropdown based on the selected date
  $.getJSON(`${API_URL}/v1/ob_date_map`, function (data) {
    dateOBs = data;
  }).fail(function () {
    console.error("Failed to load /data/v1/ob_date_map.json");
  });

  const path = window.location.pathname; // e.g. "/LSTs/pointings/123"
  const arrayElement = path.split("/").filter(Boolean)[0];

  const validTelTypes = ["LSTs", "MSTs", "SSTs"];
  const isTelescopeElement = validTelTypes.includes(arrayElement);

  // sidebar elements
  const selectSite = document.getElementById("which-Site");
  // footer elements
  const footerSite = document.getElementById("footer-site");
  const footerDate = document.getElementById("footer-date");
  // Set up starting value
  footerSite.textContent = selectSite.value;

  if (isTelescopeElement) {
    // sidebar elements
    const selectTelID = document.getElementById("which-Tel-ID");
    // footer elements
    const footerTelType = document.getElementById("footer-tel-type");
    const footerTelID = document.getElementById("footer-tel-id");
    // Set up starting value
    footerTelID.textContent = selectTelID.value;
    footerTelType.textContent = arrayElement;

    selectSite.addEventListener("change", function () {
      // Remove current options
      selectTelID.innerHTML = "";
      const option = document.createElement("option");
      option.value = "select a Tel ID";
      option.textContent = "select a Tel ID";
      option.disabled = true;
      option.selected = true;
      selectTelID.appendChild(option);

      if (selectSite.value === "North") {
        if (arrayElement === "LSTs") {
          for (let i = 1; i <= 4; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = i;
            selectTelID.appendChild(option);
          }
        } else if (arrayElement === "MSTs") {
          for (let i = 5; i <= 59; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = i;
            selectTelID.appendChild(option);
          }
        }
      } else if (selectSite.value === "South") {
        if (arrayElement === "LSTs") {
          for (let i = 1; i <= 4; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = i;
            selectTelID.appendChild(option);
          }
        } else if (arrayElement === "MSTs") {
          for (let i = 5; i <= 29; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = i;
            selectTelID.appendChild(option);
          }
          for (let i = 100; i <= 130; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = i;
            selectTelID.appendChild(option);
          }
        } else if (arrayElement === "SSTs") {
          for (let i = 30; i <= 99; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = i;
            selectTelID.appendChild(option);
          }
          for (let i = 131; i <= 179; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = i;
            selectTelID.appendChild(option);
          }
        }
      }
      footerSite.textContent = selectSite.value;
    });

    selectTelID.addEventListener("change", function () {
      footerTelID.textContent = selectTelID.value;
      footerTelID.style.color = ""; // Remove any inline color style (including red)
    });
  }

  $("#date-picker").on("changeDate", function (e) {
    const selectedDate = $("#date-picker").val();
    footerDate.textContent = selectedDate;
    footerDate.style.color = ""; // Remove any inline color style (including red)

    // If we remove the OB the following part should be revised
    if (isTelescopeElement) {
      // sidebar elements
      const selectOB = document.getElementById("which-OB");
      // footer elements
      const footerOB = document.getElementById("footer-ob");
      // Clear old options
      selectOB.innerHTML = "";

      const obs = dateOBs[selectedDate] || [];

      if (obs.length === 0) {
        const option = document.createElement("option");
        option.value = "No OBs available";
        option.textContent = "No OBs available";
        option.disabled = true;
        option.selected = true;
        selectOB.appendChild(option);
        footerOB.textContent = selectOB.value;
      } else {
        const option = document.createElement("option");
        option.value = "Select an OB";
        option.textContent = "Select an OB";
        option.disabled = true;
        option.selected = true;
        selectOB.appendChild(option);
        obs.forEach((ob) => {
          const option = document.createElement("option");
          option.value = `${ob}`;
          option.textContent = `${ob}`;
          selectOB.appendChild(option);
        });
        footerOB.textContent = option.value;
      }
      footerOB.style.color = "red";

      selectOB.addEventListener("change", function () {
        footerOB.textContent = selectOB.value;
        footerOB.style.color = ""; // Remove any inline color style (including red)
      });
    }
  });

  // Initial Trigger to set up starting 'Site' values
  selectSite.dispatchEvent(new Event("change"));
});

function initMenu() {
  $("#menu ul").hide();
  $("#menu ul").children(".current").parent().show();
  $("#menu li a").click(function () {
    let checkElement = $(this).next();
    if (checkElement.is("ul") && checkElement.is(":visible")) {
      return false;
    }
    if (checkElement.is("ul") && !checkElement.is(":visible")) {
      $("#menu ul:visible").slideUp("normal");
      checkElement.slideDown("normal");
      return false;
    }
  });
}
