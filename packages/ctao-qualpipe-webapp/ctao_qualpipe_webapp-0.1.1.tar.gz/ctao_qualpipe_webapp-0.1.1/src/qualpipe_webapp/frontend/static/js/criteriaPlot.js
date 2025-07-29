const allowedCriterion = [
  "TelescopeRangeCriterion",
  "RangeCriterion",
  "TelescopeThresholdCriterion",
  "ThresholdCriterion",
];

function plotCriteria(svg, width, height, y, metadata, id) {
  if (!isValidCriteriaReport(metadata)) {
    console.warn(
      "Invalid criteria report for plot " + id + ". Skipping criteria plot."
    );
    badgeCriteriaNone(id);
    return;
  }
  // If metadata are valid and complete, do the plotting for any allowed criterion present
  for (const criterion of allowedCriterion) {
    if (metadata.criteriaReport.hasOwnProperty(criterion)) {
      const config = metadata.criteriaReport[criterion].config[criterion];
      switch (criterion) {
        case "TelescopeRangeCriterion":
          plotRange(
            config.min_value[0][2],
            config.max_value[0][2],
            svg,
            width,
            y
          );
          break;
        case "RangeCriterion":
          plotRange(config.min_value, config.max_value, svg, width, y);
          break;
        case "TelescopeThresholdCriterion":
          plotThreshold(
            config.above,
            config.threshold[0][2],
            svg,
            width,
            height,
            y
          );
          break;
        case "ThresholdCriterion":
          plotThreshold(config.above, config.threshold, svg, width, height, y);
          break;
      }
      updateBadgeCriteria(id, metadata, criterion);
      // Only one criterion should be present, so break after handling
      break;
    }
  }
}

function plotRange(minVal, maxVal, svg, width, y) {
  // Color region between two lines
  svg
    .append("rect")
    .attr("x", 0)
    .attr("y", y(maxVal))
    .attr("width", width)
    .attr("height", y(minVal) - y(maxVal))
    .attr("fill", "#28a745")
    .attr("opacity", 0.15);

  // Min horizontal line
  svg
    .append("line")
    .attr("x1", 0)
    .attr("x2", width)
    .attr("y1", y(minVal))
    .attr("y2", y(minVal))
    .attr("stroke", "#28a745")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "4,2");

  // Max horizontal line
  svg
    .append("line")
    .attr("x1", 0)
    .attr("x2", width)
    .attr("y1", y(maxVal))
    .attr("y2", y(maxVal))
    .attr("stroke", "#28a745")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "4,2");
}

function plotThreshold(above, threshold, svg, width, height, y) {
  if (above) {
    // Color above threshold
    svg
      .append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", width)
      .attr("height", y(threshold))
      .attr("fill", "#28a745")
      .attr("opacity", 0.15);
  } else {
    // Color below threshold
    svg
      .append("rect")
      .attr("x", 0)
      .attr("y", y(threshold))
      .attr("width", width)
      .attr("height", height - y(threshold))
      .attr("fill", "#28a745")
      .attr("opacity", 0.15);
  }
  // Horizontal threshold line
  svg
    .append("line")
    .attr("x1", 0)
    .attr("x2", width)
    .attr("y1", y(threshold))
    .attr("y2", y(threshold))
    .attr("stroke", "#28a745")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "4,2");
}

// --> TBD add call to function inside to update also color of table
function updateBadgeCriteria(id, metadata, criterion) {
  // Update criteria badge color upon criteria result
  const badgerElem = document.getElementById(id).parentElement;
  if (metadata.criteriaReport[criterion].result) {
    updateBadgeClass(badgerElem, "badger-success");
  } else {
    updateBadgeClass(badgerElem, "badger-danger");
  }
}

function badgeCriteriaNone(id) {
  // If 'criteriaReport' is not valid or incomplete, we put NONE in the badge
  const badgerElem = document.getElementById(id).parentElement;
  console.log("Badge set to NONE for plot: " + id + ".");
  updateBadgeClass(badgerElem, "badger-null");
}

function updateBadgeClass(elem, newClass) {
  const validClasses = ["badger-success", "badger-danger", "badger-null"];
  if (!elem || !validClasses.includes(newClass)) return;

  validClasses.forEach((cls) => elem.classList.remove(cls));
  elem.classList.add(newClass);

  const badgeText = {
    "badger-success": "CRITERIA: OK",
    "badger-danger": "CRITERIA: FAIL",
    "badger-null": "CRITERIA: NONE",
  };
  elem.setAttribute("data-badger-right", badgeText[newClass]);
}

// sonarjs/cognitive-complexity
// NOSONAR
function isValidCriteriaReport(metadata) {
  // NOSONAR

  // Check 'metadata' and 'criteriaReport'
  if (metadata && typeof metadata === "object") {
    if (
      typeof metadata?.criteriaReport === "object" &&
      metadata.criteriaReport !== null
    ) {
      // Get the first (and only) key in criteriaReport
      const outerKey = Object.keys(metadata.criteriaReport)[0];
      if (!allowedCriterion.includes(outerKey)) {
        console.warn(
          "Unknown or missing 'criteria' in criteriaReport:",
          outerKey
        );
        return false;
      }
      const outerObj = metadata.criteriaReport[outerKey];
      // Check 'config'
      if (typeof outerObj?.config === "object" && outerObj.config !== null) {
        const innerKey = Object.keys(outerObj.config)[0];
        if (innerKey !== outerKey) {
          console.warn(
            "CriteriaReport key and config key do not match, respectively:",
            outerKey,
            "and",
            innerKey
          );
          return false;
        } else {
          if (
            outerObj.config[outerKey] &&
            typeof outerObj.config[outerKey] === "object"
          ) {
            if (outerKey === "ThresholdCriterion") {
              if (
                !(
                  typeof outerObj.config[outerKey].above === "boolean" &&
                  typeof outerObj.config[outerKey].threshold === "number"
                )
              ) {
                console.warn(
                  "Missing or incomplete 'config." + outerKey + "' object."
                );
                return false;
              }
            } else if (outerKey === "TelescopeThresholdCriterion") {
              if (
                !(
                  typeof outerObj.config[outerKey].above === "boolean" &&
                  Array.isArray(outerObj.config[outerKey].threshold) &&
                  Array.isArray(outerObj.config[outerKey].threshold[0]) &&
                  outerObj.config[outerKey].threshold[0].length >= 3 &&
                  typeof outerObj.config[outerKey].threshold[0][0] ===
                    "string" &&
                  typeof outerObj.config[outerKey].threshold[0][1] ===
                    "string" &&
                  typeof outerObj.config[outerKey].threshold[0][2] === "number"
                )
              ) {
                console.warn(
                  "Invalid or missing '" + outerKey + "' required parameters."
                );
                return false;
              }
            } else if (outerKey === "RangeCriterion") {
              if (
                !(
                  typeof outerObj.config[outerKey].max_value === "number" &&
                  typeof outerObj.config[outerKey].min_value === "number"
                )
              ) {
                console.warn(
                  "Invalid or missing '" + outerKey + "' required parameters."
                );
                return false;
              }
            } else if (outerKey === "TelescopeRangeCriterion") {
              if (
                !(
                  Array.isArray(outerObj.config[outerKey].max_value) &&
                  Array.isArray(outerObj.config[outerKey].max_value[0]) &&
                  outerObj.config[outerKey].max_value[0].length == 3 &&
                  typeof outerObj.config[outerKey].max_value[0][0] ===
                    "string" &&
                  typeof outerObj.config[outerKey].max_value[0][1] ===
                    "string" &&
                  typeof outerObj.config[outerKey].max_value[0][2] ===
                    "number" &&
                  Array.isArray(outerObj.config[outerKey].min_value) &&
                  Array.isArray(outerObj.config[outerKey].min_value[0]) &&
                  outerObj.config[outerKey].min_value[0].length == 3 &&
                  typeof outerObj.config[outerKey].min_value[0][0] ===
                    "string" &&
                  typeof outerObj.config[outerKey].min_value[0][1] ===
                    "string" &&
                  typeof outerObj.config[outerKey].min_value[0][2] === "number"
                )
              ) {
                console.warn(
                  "Invalid or missing '" + outerKey + "' required parameters."
                );
                return false;
              }
            }
          } else {
            console.warn(
              "Invalid or missing 'config." + outerKey + "' object."
            );
            return false;
          }
        }
      } else {
        console.warn("Invalid or missing 'config' for '" + outerKey + "'");
        return false;
      }
      if (typeof outerObj?.result !== "boolean") {
        console.warn("Invalid or missing criteria result");
        return false;
      }
    } else {
      console.warn("Missing 'criteriaReport'");
      return false;
    }
  } else {
    console.warn("Invalid metadata");
    return false;
  }
  return true;
}
