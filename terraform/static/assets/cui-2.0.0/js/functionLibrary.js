const tags = [
  ["input", "text"],
  ["textarea"],
  ["input", "list"],
  ["select"],
  // ["span", "checkbox__input"],
  // ["input", "checkbox"],
];
function saveInput() {
  var inputs, index;
  const path = window.location.pathname;
  const page = path.split("/").pop();
  console.log(page);
  for (const tag of tags) {
    // collects all the elements in the HTML with the given tag
    inputs = document.getElementsByTagName(tag[0]);
    // iterate through all of 
    for (index = 0; index < inputs.length; ++index) {
      const currentElem = inputs[index];
      if (
        tag.length === 1 ||
        !(
          tag[0] === "input" &&
          tag[1] === "checkbox" &&
          currentElem.tagName === "INPUT" &&
          currentElem.type === "checkbox"
        )
        // && tag[1] === currentElem.type
      ) {
        // console.log(currentElem)
        if (tag.length === 1 || (tag.length > 1 && tag[1] === currentElem.type))
          sessionStorage.setItem(page + " " + currentElem.id, currentElem.value);
      } else if (
        tag[0] === "input" &&
        tag[1] === "checkbox" &&
        currentElem.tagName === "INPUT" &&
        currentElem.type === "checkbox"
      ) {
        // if (currentElem.
        // console.log(currentElem);
        // console.log(currentElem.checked);
        sessionStorage.setItem(
          page + " " + currentElem.id,
          currentElem.checked
        );

        //   console.log(currentElem.tagName)
      }
    }
  }
  // console.log("Saved inputs locally.");
}
function loadInput() {
  var inputs, index;
  // console.log(JSON.stringify(sessionStorage, null, 2));

  const path = window.location.pathname;
  const page = path.split("/").pop();
  // console.log(page);
  // console.log("load attempt")
  for (const tag of tags) {
    inputs = document.getElementsByTagName(tag[0]);
    for (index = 0; index < inputs.length; ++index) {
      const currentElem = inputs[index];
      if (
        tag.length === 1 ||
        !(
          tag[0] === "input" &&
          tag[1] === "checkbox" &&
          currentElem.tagName === "INPUT" &&
          currentElem.type === "checkbox"
        )
      ) {
        // console.log(currentElem);
        if (
          sessionStorage.getItem(page + " " + currentElem.id) !== null &&
          (tag.length === 1 || (tag.length > 1 && tag[1] === currentElem.type))
        ) {
          currentElem.value = sessionStorage.getItem(
            page + " " + currentElem.id
          );
        }
      } else if (
        tag[0] === "input" &&
        tag[1] === "checkbox" &&
        currentElem.tagName === "INPUT" &&
        currentElem.type === "checkbox"
      ) {
        if (sessionStorage.getItem(page + " " + currentElem.id) === "true")
          currentElem.click();
      }
    }
  }
  // console.log("Loaded saved inputs from local storage.");
}

function loadInputLimit(limitArr) {
  var inputs, index;
  console.log(JSON.stringify(sessionStorage, null, 2));

  const path = window.location.pathname;
  const page = path.split("/").pop();
  console.log(page);
  // console.log("load attempt")
  for (const tag of limitArr) {
    inputs = document.getElementsByTagName(tag[0]);
    for (index = 0; index < inputs.length; ++index) {
      const currentElem = inputs[index];
      if (
        tag.length === 1 ||
        !(
          tag[0] === "input" &&
          tag[1] === "checkbox" &&
          currentElem.tagName === "INPUT" &&
          currentElem.type === "checkbox"
        )
      ) {
        console.log(currentElem);
        if (
          sessionStorage.getItem(page + " " + currentElem.id) !== null &&
          (tag.length === 1 || (tag.length > 1 && tag[1] === currentElem.type))
        ) {
          const retrieved = sessionStorage.getItem(page + " " + currentElem.id);
          currentElem.value = retrieved;
          console.log(retrieved);
        }
      } else if (
        tag[0] === "input" &&
        tag[1] === "checkbox" &&
        currentElem.tagName === "INPUT" &&
        currentElem.type === "checkbox"
      ) {
        if (sessionStorage.getItem(page + " " + currentElem.id) === "true")
          currentElem.click();
      }
    }
  }
  // console.log("Loaded saved inputs from local storage.");
}

let previousBottom = 0;
let previousIframeSrc = "";
let savedBottom = 0;
function autoScroll(input) {
  const frame = document
    .querySelector("iframe")
    .contentWindow.document.querySelector("html");
  const iframeSrc = document.querySelector("iframe").getAttribute("src");
  const bottom = frame.scrollHeight - 564;
  const currentHeight = frame.scrollTop;

  if (savedBottom !== 0) {
    if (savedBottom !== bottom) {
      previousBottom = 0;
      savedBottom = 0;
    }
  }
  else {
    if (iframeSrc !== previousIframeSrc) {
      console.log("iframe src: " + iframeSrc);
      console.log("previous iframe src: " + previousIframeSrc);
      console.log("changed iframe src");
      // previousBottom = 0;
      previousIframeSrc = iframeSrc;
      savedBottom = bottom;
      // endAutoScroll();
      // startAutoScroll();
    }

    if (currentHeight >= previousBottom - 1 || input !== undefined) {
      frame.scrollTo(0, bottom);
      console.log("Previous Bottom: " + previousBottom);
      console.log("frame.scrollTop: " + currentHeight);
      console.log("autoScrolled");
      previousBottom = bottom;
    } else if (currentHeight < previousBottom - 1) {
      console.log("Previous Bottom: " + previousBottom);
      console.log("frame.scrollTop: " + currentHeight);
      console.log("Cursor moved so will not autoscroll");
    }
  }  
}

let autoScrollTimer = null;
function startAutoScroll() {
  autoScrollTimer = setInterval(() => {
    autoScroll();
  }, 200)
}

function endAutoScroll() {
  if (autoScrollTimer !== null)
    clearInterval(autoScrollTimer);
}

let autoScrollBool = true;
function toggleAutoScroll() {
  autoScrollBool = !autoScrollBool;
  const autoScrollButton = document.getElementById("autoScrollToggle");
  // console.log(autoScrollButton);
  if (autoScrollBool) {
    autoScrollButton.value = "Stop Autoscroll";
    previousBottom = 0;
    // previousIframeSrc = "";
    startAutoScroll();
  } else {
    autoScrollButton.value = "Start Autoscroll";
    endAutoScroll();
  }
}
