function plotAndCreateResizeListener(el, data, key) {
  return function resizeHandler() {
    // Reset standard axis color after possible alerts
    const plotContainer = document.getElementById(el.id);
    plotContainer.style.color = "black";
    scatterPlot(el.id, data[key].fetchedData, data[key].fetchedMetadata);
  };
}

function makePlot() {
  const dataPromise = requestData();

  dataPromise
    .then((data) => {
      if (!data) {
        const message = "No data received or data is invalid.";
        console.error(message);
        clearPlot(message);
        throw new Error(message);
      }
      console.log("Received data:", data);

      const plotElements = document.querySelectorAll('[id^="plot-"]');
      Array.from(plotElements).forEach((el) => {
        const key = el.id.replace(/^plot-/, "");
        if (data[key]) {
          if (
            !data[key].fetchedData ||
            !Array.isArray(data[key].fetchedData.x) ||
            !Array.isArray(data[key].fetchedData.y) ||
            data[key].fetchedData.x.length !== data[key].fetchedData.y.length ||
            !data[key].fetchedData.x.every(
              (val) => typeof val === "number" && !isNaN(val)
            ) ||
            !data[key].fetchedData.y.every(
              (val) => typeof val === "number" && !isNaN(val)
            )
          ) {
            const message = `Invalid data for key: ${key}`;
            clearPlot(message, el.id);
            throw new Error(message);
          }
          // Remove old listener if existing
          if (resizeListeners[el.id]) {
            window.removeEventListener("resize", resizeListeners[el.id]);
          }
          // Create and add the new listener
          const plotAndListen = plotAndCreateResizeListener(el, data, key);
          plotAndListen();
          resizeListeners[el.id] = plotAndListen;
          window.addEventListener("resize", plotAndListen);
        } else {
          const message = `No data found for key: ${key}`;
          clearPlot(message, el.id);
          throw new Error(message);
        }
      });
    })
    .catch((error) => {
      console.error("Error while requesting data:", error);
    });
}

function clearPlot(message = "", plotId = null) {
  function clearSinglePlot(container, id) {
    if (container) {
      container.innerHTML = message;
      container.style.color = "red";
      container.style.fontWeight = "bold";
      console.log(`Cleared plot container for ${id.replace(/^plot-/, "")}.`);
      badgeCriteriaNone(id);
    } else {
      console.warn(
        `No plot container found for key: ${id.replace(/^plot-/, "")}`
      );
    }
  }

  if (plotId === null) {
    const plotElements = document.querySelectorAll('[id^="plot-"]');
    Array.from(plotElements).forEach((el) => {
      clearSinglePlot(document.getElementById(el.id), el.id);
    });
  } else {
    clearSinglePlot(document.getElementById(plotId), plotId);
  }
}

function checkQueryParams(
  selectedTelType,
  selectedSite,
  selectedDate,
  selectedOB,
  selectedTelID
) {
  if (!isValidSite(selectedSite)) return false;
  if (!isValidDate(selectedDate)) return false;
  if (!isValidOB(selectedOB)) return false;
  if (!isValidTelType(selectedTelType)) return false;
  if (!isValidTelID(selectedTelID)) return false;

  // Clear missinInfo alert
  const missingInfo = document.getElementById("missingInfo");
  if (missingInfo) {
    missingInfo.textContent = "";
  }
  return true;
}

function missingInfo(text, error = false) {
  if (error) {
    console.error(text);
  } else {
    console.warn(text);
  }
  const missingInfo = document.getElementById("missingInfo");
  if (missingInfo) {
    missingInfo.textContent = text;
    missingInfo.style.background = "red";
  }
}

function isValidSite(site) {
  if (site !== "North" && site !== "South") {
    missingInfo("Site must be either 'North' or 'South'");
    return false;
  }
  return true;
}

function isValidDate(date) {
  if (!date || date === "Choose a date") {
    missingInfo("Please select a 'date' from the dropdown menu.");
    return false;
  }
  if (!date.match(/^\d{4}-\d{2}-\d{2}$/)) {
    missingInfo("Date must be in YYYY-MM-DD format", true);
    return false;
  }
  return true;
}

function isValidOB(ob) {
  if (!ob || ob === "choose date first") {
    missingInfo("Please first choose a 'date' from the dropdown menu.");
    return false;
  }
  if (ob === "No OBs available") {
    missingInfo(
      "No Observation Blocks available for the selected date. Please select an other 'date' from the dropdown menu."
    );
    return false;
  }
  if (ob === "Select an OB") {
    missingInfo("Please select an 'Observation Block' from the dropdown menu.");
    return false;
  }
  if (!/^\d+$/.test(ob)) {
    missingInfo("Observation Block must be a valid number", true);
    return false;
  }
  return true;
}

function isValidTelType(type) {
  if (!type || !["LST", "MST", "SST"].includes(type)) {
    missingInfo("Telescope type must be 'LST', 'MST', or 'SST'", true);
    return false;
  }
  return true;
}

function isValidTelID(id) {
  if (!id || id === "select a Tel ID") {
    missingInfo("Please, select a 'Telescope ID' from the dropdown menu.");
    return false;
  }
  if (!/^\d+$/.test(id)) {
    missingInfo("Telescope ID must be a valid number", true);
    return false;
  }
  return true;
}

async function requestData() {
  const path = window.location.pathname;
  const arrayElement = path.split("/").filter(Boolean)[0];
  const selectedTelType = arrayElement ? arrayElement.slice(0, -1) : "";
  const selectedSite = document.getElementById("which-Site").value;
  const selectedDate = $("#date-picker").val();
  const selectedOB = document.getElementById("which-OB").value;
  const selectedTelID = document.getElementById("which-Tel-ID").value;

  const validParameters = checkQueryParams(
    selectedTelType,
    selectedSite,
    selectedDate,
    selectedOB,
    selectedTelID
  );

  if (validParameters) {
    console.log("Query parameters are valid");
    try {
      const response = await fetch(
        `${API_URL}/v1/data?site=${selectedSite}&date=${selectedDate}&ob=${selectedOB}&telescope_type=${selectedTelType}&telescope_id=${selectedTelID}`
      );
      const data = await response.json();
      if (response.status === 404) {
        missingInfo("Requested data not found (404).", true);
        return;
      }
      return data;
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  } else {
    console.error("Invalid query parameters. Cannot request data.");
    return false;
  }
}
