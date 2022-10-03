import { apiAppToken } from "./secret.js";

//  Variables
const apiBaseUrl = "https://data.cityofnewyork.us/resource/4kpn-sezh.json";
const $searchResultsList = $("#search-results-list");
const $boroughSearchForm = $("#search-by-borough-form");
const $boroughSearchBtn = $("#borough-search-button");
const $advancedSearchBtn = $("#advance-search-button");
const $advancedSearchForm = $("#advanced-search-form");
const $basicSearchBtn = $("#basic-search-button");
const $advancedSubmitBtn = $("#advanced-submit-button");
const $similarLocationsBtn = $("#similar-locations-button");

// Add the visual elements to the page
const addToPage = (facilityObj) => {
  const newLi = document.createElement("li");
  newLi.innerHTML = `<a href="/facilities/${facilityObj.facility_pk}">${facilityObj.facilityname}</a> ${facilityObj.address}`;

  $searchResultsList.append(newLi);
};

//  Advanced search initiator
$advancedSearchBtn.on("click", function () {
  $searchResultsList.html("");
  $boroughSearchForm.hide();
  $advancedSearchForm.show();
});

//  Basic search initiator
$basicSearchBtn.on("click", function () {
  $searchResultsList.html("");
  $advancedSearchForm.hide();
  $boroughSearchForm.show();
});

//  Basic search (by borough) handler
$boroughSearchBtn.on("click", async function (event) {
  event.preventDefault();
  $searchResultsList.html("");
  const borough = $("#borough-input").val();

  const results = await $.ajax({
    url: apiBaseUrl,
    type: "GET",
    data: {
      $limit: 500,
      $$app_token: apiAppToken,
      borough: borough,
    },
  });

  for (let result in results) {
    addToPage(results[result]);
  }
});

//  Advanced search handler
$advancedSubmitBtn.on("click", async function (event) {
  event.preventDefault();
  $searchResultsList.html("");

  const zipCode = $("#zip-code-input").val();
  const $maleCondoms = $("#male-condoms-input");
  const $femaleCondoms = $("#female-condoms-input");
  const $lubricant = $("#lubricant-input");
  const $openNow = $("#open-now-input");

  const data = { $limit: 500, $$app_token: apiAppToken };

  //  Adjust search criteria for data request based on user input
  if (zipCode != "") {
    data.zipcode = zipCode;
  }

  if ($maleCondoms.prop("checked")) {
    data.condoms_male = "true";
  }

  if ($femaleCondoms.prop("checked")) {
    data.fc2_female_insertive_condoms = "true";
  }

  if ($lubricant.prop("checked")) {
    data.lubricant = "true";
  }

  const results = await $.ajax({
    url: apiBaseUrl,
    type: "GET",
    data: data,
  });

  for (let result in results) {
    //  Filter if "open now" is selected in the search form
    if ($openNow.prop("checked")) {
      const date = new Date();
      const day = date.getDay();
      const hour = date.getHours();
      const minutes = date.getMinutes();

      checkDayAndTime(results[result], day, hour, minutes);
    } else {
      addToPage(results[result]);
    }
  }
});

//  Helper function that compares each location to the current day and time, if currently open, add site to page
const checkDayAndTime = (facilityObj, day, hour, minutes) => {
  const dayToCheck = weekday[day];
  const timeStr = facilityObj[dayToCheck];

  //  Immediately filter out locations that are not open on the current day
  if (timeStr != undefined) {
    //  Split time string into two separate strings, open and close
    const timeArray = timeStr.split(" - ");
    const openTime = timeArray[0];
    const closeTime = timeArray[1];

    //  Get arrays from the individual time strings for comparison
    let open = getTime(openTime);
    let close = getTime(closeTime);

    //  Handle locations that close after midnight (adjust time to show additional open hours)
    if (close[0] < open[0]) {
      close[0] = close[0] + 24;
    }

    //  Handle locations that are open now
    if (open[0] <= hour && hour < close[0]) {
      addToPage(facilityObj);
    }

    //  Handle locations closing within the hour
    else if (hour == close[0] && minutes < close[1]) {
      addToPage(facilityObj);
    }
  }
};

//  Lookup array for day of the week
const weekday = [
  "sunday",
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
];

//  Helper function to turn time string into array of hours and minutes
const getTime = (time) => {
  const timeModArray = time.split(" ");
  const hhmmStr = timeModArray[0];
  const hmArray = hhmmStr.split(":");
  const mod = timeModArray[1];
  let hour = "";

  if (mod == "AM") {
    hour = parseInt(hmArray[0]);
  } else if (mod == "PM") {
    hour = parseInt(hmArray[0]) + 12;
  }

  const mins = parseInt(hmArray[1]);

  return [hour, mins];
};
