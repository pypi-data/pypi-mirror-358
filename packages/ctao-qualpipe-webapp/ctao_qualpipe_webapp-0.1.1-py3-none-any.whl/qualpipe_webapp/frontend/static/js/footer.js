document.addEventListener("DOMContentLoaded", function () {
  // sidebar
  const selectSite = document.getElementById("which-Site");
  const selectTelID = document.getElementById("which-Tel-ID");
  // footer
  const footerSite = document.getElementById("footer-site");
  const footerTelID = document.getElementById("footer-tel-id");
  const footerDate = document.getElementById("footer-date");

  // Update selected value
  selectSite.addEventListener("change", function () {
    footerSite.textContent = selectSite.value;
    footerTelID.textContent = selectTelID.value;
  });
  selectTelID.addEventListener("change", function () {
    footerSite.textContent = selectSite.value;
    footerTelID.textContent = selectTelID.value;
  });

  $("#date-picker").on("changeDate", function (e) {
    const selectedDate = $("#date-picker").val();
    footerDate.textContent = selectedDate;
  });
});
