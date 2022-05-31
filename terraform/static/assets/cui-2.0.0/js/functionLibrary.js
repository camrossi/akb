const tags = [
  ["input", "text"],
  ["textarea"],
  ["input", "list"],
  ["select"],
  // ["span", "checkbox__input"],
  // ["input", "checkbox"],
];
function getPageName() {
  const path = window.location.pathname;
  const page = path.split("/").pop();
  console.log(page);
  return page;
}

function saveInput() {
  var inputs, index;
  const page = getPageName();
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
  saveLoopBackAddresses();
  // console.log("Saved inputs locally.");
}
function saveLoopBackAddresses() {
  if (page !== "fabric") return;
  const saved = [];
  const page = getPageName();
  const loopBacksToSave = ["loopback_ipv4", "loopback_ipv6"];
  for (const loopBack of loopBacksToSave) {
      const grandParentElem = document.getElementById(loopBack);
      if (grandParentElem !== null && grandParentElem !== undefined) {
        for (const child of grandParentElem.children) {
          saved.push(child.children[0].innerText);
        }
        sessionStorage.setItem(
          page + " " + grandParentElem.id,
          JSON.stringify(saved)
        );
    }
  }
}

function loadLoopBackAddresses() {
  const page = getPageName();
  if (page !== "fabric")
    return;
  const loopBacksToSave = ["loopback_ipv4", "loopback_ipv6"];

  for (const loopBack of loopBacksToSave) {
    const grandParentElem = document.getElementById(loopBack);
    if (grandParentElem !== null && grandParentElem !== undefined) {
      console.log(sessionStorage.getItem(page + " " + grandParentElem.id));
      const addressArr = JSON.parse(sessionStorage.getItem(page + " " + grandParentElem.id));
      // console.log(addressArr);
      for (const address of addressArr) {
        // saved.push(child.children[0].innerText);
        let elem = undefined;
        if (loopBack === "loopback_ipv4") {
          elem = document.getElementById("input_lo_ipv4");
          elem.value = address;
          input_lo_ipv4_enter();
        }
        else {
          elem = document.getElementById("input_lo_ipv6");
          elem.value = address;
          input_lo_ipv6_enter();
        }
        elem.value = "";
      }
    }
  }
}

  function input_lo_ipv4_enter() {
    var count_lo = $("#loopback_ipv4").children().length;
    if (count_lo >= 2) {
      $("#form_loopback_alert").show();
      $("#form_loopback").addClass("form-group--error");
      return false;
    }

    var lo_ipv4_addrs = $("#loopback_ipv4").data("lo_ipv4_addrs");
    if (lo_ipv4_addrs == null) {
      lo_ipv4_addrs = [];
      $("#loopback_ipv4").data("lo_ipv4_addrs", lo_ipv4_addrs);
    }

    var ipv4_addr = $("#input_lo_ipv4").val();
    var lo_label = $(
      '<span class="label label--info label--raised base-margin-left"></span>'
    );
    lo_label.append($("<span><span>").text(ipv4_addr));
    lo_label.append('<span class="icon-close"></span>');

    console.log(lo_label);
    var label_ipv4 = $(lo_label).appendTo("#loopback_ipv4");
    label_ipv4.data("ipv4", ipv4_addr);
    lo_ipv4_addrs.push(ipv4_addr);
    $("#loopback_ipv4").data("lo_ipv4_addrs", lo_ipv4_addrs);
    $(this).val("");
  }
  
  function input_lo_ipv6_enter() {
      var count_lo = $("#loopback_ipv6").children().length;
      if (count_lo >= 2) {
        $("#form_loopbackv6_alert").show();
        $("#form_loopbackv6").addClass("form-group--error");
        return false;
      }

      var lo_ipv6_addrs = $("#loopback_ipv6").data("lo_ipv6_addrs");
      if (lo_ipv6_addrs == null) {
        lo_ipv6_addrs = [];
        $("#loopback_ipv6").data("lo_ipv6_addrs", lo_ipv6_addrs);
      }

      var ipv6_addr = $("#input_lo_ipv6").val();
      var lo_label = $(
        '<span class="label label--info label--raised base-margin-left"></span>'
      );
      lo_label.append($("<span></span>").text(ipv6_addr));
      lo_label.append($('<span class="icon-close"></span>'));
      var label_ipv6 = $(lo_label).appendTo("#loopback_ipv6");
      label_ipv6.data("ipv6", ipv6_addr);
      lo_ipv6_addrs.push(ipv6_addr);
      $("#loopback_ipv6").data("lo_ipv6_addrs", lo_ipv6_addrs);
      $(this).val("");
  }

function loadInput() {
  var inputs, index;
  // console.log(JSON.stringify(sessionStorage, null, 2));

  const page = getPageName();
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
  loadLoopBackAddresses();
  // console.log("Loaded saved inputs from local storage.");
}

function loadInputLimit(limitArr) {
  var inputs, index;
  console.log(JSON.stringify(sessionStorage, null, 2));

  const page = getPageName();
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

function loadInputVCenter() {
  // console.log(JSON.stringify(sessionStorage, null, 2))
  const dcElem = document.getElementById("dc");

  const path = window.location.pathname;
  const page = path.split("/").pop();

  // load in the vCenter DC Name
  const retrievedVal = sessionStorage.getItem(page + " " + "dc");
  if (retrievedVal !== null && retrievedVal !== "") {
    dcElem.value = retrievedVal;
    dcElem.form.requestSubmit();
    console.log("if condition ran");
  } else console.log("No saved value for vCenter DC Name");
}

function loadListenerCreator() {
      console.log("turbo:load fired");
      loadInputVCenter();

      const dummyC = document.getElementById('dummy_container')

      const observer = new MutationObserver((mutationsList, observered) => {
         console.log('Mutation observer body is being ran!')
         loadInput();
         observer.disconnect();

         document.removeEventListener('turbo:load', null)

      })
      observer.observe(dummyC, { attributes: true, childList: true, subtree: true })
}
