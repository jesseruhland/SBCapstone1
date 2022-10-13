//  Variables
const apiBaseUrl = "/sites";
const $searchResultsList = $("#search-results-list");
const $similarLocationsList = $("#similar-locations-list");
const $boroughSearchForm = $("#search-by-borough-form");
const $boroughSearchBtn = $("#borough-search-button");
const $advancedSearchBtn = $("#advance-search-button");
const $advancedSearchForm = $("#advanced-search-form");
const $basicSearchBtn = $("#basic-search-button");
const $advancedSubmitBtn = $("#advanced-submit-button");
const $similarLocationsBtn = $("#similar-locations-button");
const $hideSimilarBtn = $("#hide-similar-button");
const $deleteCommentBtn = $(".delete-comment-button");
const $userUnFavBtn = $(".user-page-unfav-btn");
const $siteUnFavBtn = $("#site-page-unfav-btn");
const $siteFavBtn = $("#site-page-fav-btn");

// Add the visual elements to the page
const addToPage = (siteObj, location) => {
  const newLi = document.createElement("div");
  newLi.classList.add("col-12");
  if (location != $similarLocationsList) {
    newLi.classList.add("col-sm-6");
    newLi.classList.add("col-md-4");
  }
  newLi.innerHTML = `<div class="card mt-1"><div class="card-body"><h5 class="card-title">${
    siteObj.name
  }</h5><h6 class="card-subtitle mb-2 text-muted">${siteObj.borough}</h6><p>${
    siteObj.address
  }<br />${siteObj.phone || ""}</p><a href="/sites/${
    siteObj.id
  }">More Information</a></div>`;

  location.append(newLi);
};

//  Advanced search initiator
$advancedSearchBtn.on("click", function () {
  $searchResultsList.html("");
  $boroughSearchForm.addClass("d-none");
  $advancedSearchForm.removeClass("d-none");
});

//  Basic search initiator
$basicSearchBtn.on("click", function () {
  $searchResultsList.html("");
  $advancedSearchForm.addClass("d-none");
  $boroughSearchForm.removeClass("d-none");
});

//  Basic search (by borough) handler
$boroughSearchBtn.on("click", async function (event) {
  event.preventDefault();
  $searchResultsList.html("");
  const borough = $("#borough-input").val();

  const response = await $.ajax({
    url: apiBaseUrl,
    method: "GET",
    data: {
      borough: borough,
    },
  });

  results = JSON.parse(response);

  for (let result in results) {
    addToPage(results[result], $searchResultsList);
  }
});

//  Advanced search handler
$advancedSubmitBtn.on("click", async function (event) {
  event.preventDefault();
  $searchResultsList.html("");

  const $siteName = $("#site-name-input").val();
  const $zipCode = $("#zip-code-input").val();
  const $maleCondoms = $("#male-condoms-input");
  const $femaleCondoms = $("#female-condoms-input");
  const $lubricant = $("#lubricant-input");
  const $openNow = $("#open-now-input");

  const data = {};

  //  Adjust search criteria for data request based on user input

  if ($siteName != "") {
    data.site_name = $siteName;
  }

  if ($zipCode != "") {
    data.zip_code = $zipCode;
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

  const response = await $.ajax({
    url: apiBaseUrl,
    type: "GET",
    data: data,
  });

  results = JSON.parse(response);

  for (let result in results) {
    //  Filter if "open now" is selected in the search form
    if ($openNow.prop("checked")) {
      const date = new Date();
      const day = date.getDay();
      const hour = date.getHours();
      const minutes = date.getMinutes();

      checkDayAndTime(results[result], day, hour, minutes);
    } else {
      addToPage(results[result], $searchResultsList);
    }
  }
});

//  Helper function that compares each location to the current day and time, if currently open, add site to page
const checkDayAndTime = (siteObj, day, hour, minutes) => {
  const dayToCheck = weekday[day];
  const timeStr = siteObj[dayToCheck];

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
      addToPage(siteObj, $searchResultsList);
    }

    //  Handle locations closing within the hour
    else if (hour == close[0] && minutes < close[1]) {
      addToPage(siteObj, $searchResultsList);
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

// Similiar Location Handler:

$similarLocationsBtn.on("click", async function (event) {
  event.preventDefault();
  $similarLocationsList.html("");

  const $simZipCode = $("#similar-zip-code-input").val();
  const $simMaleCondoms = $("#similar-mc-input").val();
  const $simFemaleCondoms = $("#similar-fc-input").val();
  const $simLubricant = $("#similar-lubricant-input").val();

  const data = {};

  if ($simZipCode != "") {
    data.zip_code = $simZipCode;
  }

  if ($simMaleCondoms == "True") {
    data.condoms_male = "true";
  }

  if ($simFemaleCondoms == "True") {
    data.fc2_female_insertive_condoms = "true";
  }

  if ($simLubricant == "True") {
    data.lubricant = "true";
  }

  const response = await $.ajax({
    url: apiBaseUrl,
    type: "GET",
    data: data,
  });

  results = JSON.parse(response);

  for (let result in results) {
    addToPage(results[result], $similarLocationsList);
  }

  $similarLocationsBtn.addClass("d-none");
  $hideSimilarBtn.removeClass("d-none");

  $similarLocationsList.removeClass("d-none");
});

//  Hide Similar Results
$hideSimilarBtn.on("click", function () {
  $hideSimilarBtn.addClass("d-none");
  $similarLocationsBtn.removeClass("d-none");
  $similarLocationsList.addClass("d-none");
});

//  Send delete comment request without refreshing the page, update front end to sync with back end
$deleteCommentBtn.on("click", async function (event) {
  commentID = event.target.getAttribute("data-comment-id");

  const response = await $.ajax({
    url: `/comments/${commentID}/delete`,
    type: "POST",
  });

  event.target.parentElement.parentElement.parentElement.remove();
});

//  Send delete favorite request from USER DETAIL PAGE without refreshing the page, update front end to sync with back end
$userUnFavBtn.on("click", async function (event) {
  siteID = event.target.getAttribute("data-site-id");

  const response = await $.ajax({
    url: `/sites/${siteID}/favorite/delete`,
    type: "POST",
  });

  event.target.parentElement.parentElement.remove();
});

//  Send delete favorite request from SITE DETAIL PAGE without refreshing the page, update front end to sync with back end
$siteUnFavBtn.on("click", async function (event) {
  siteID = event.target.getAttribute("data-site-id");

  const response = await $.ajax({
    url: `/sites/${siteID}/favorite/delete`,
    type: "POST",
  });

  $siteUnFavBtn.addClass("d-none");
  $siteFavBtn.removeClass("d-none");
});

//  Send new favorite request from SITE DETAIL PAGE without refreshing the page, update front end to sync with back end
$siteFavBtn.on("click", async function (event) {
  siteID = event.target.getAttribute("data-site-id");

  const response = await $.ajax({
    url: `/sites/${siteID}/favorite`,
    type: "POST",
  });

  $siteFavBtn.addClass("d-none");
  $siteUnFavBtn.removeClass("d-none");
});
