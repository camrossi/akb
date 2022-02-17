const tags = [
  ["input", "text"],
  ["textarea"],
  ["input", "list"],
  ["select"],
    // ["span", "checkbox__input"],
  ["input", "checkbox"]
];
function saveInput() {
  var inputs, index;
  
    for (const tag of tags) {
        inputs = document.getElementsByTagName(tag[0]);
        for (index = 0; index < inputs.length; ++index) {
          currentElem = inputs[index];
          if (tag.length === 1 || !(tag[0] === "input" && tag[1] === "checkbox" && currentElem.tagName === "INPUT" && currentElem.type === "checkbox")) {
            // console.log(currentElem)
            sessionStorage.setItem(currentElem.id, currentElem.value);
          }
          else if (
            tag[0] === "input" &&
            tag[1] === "checkbox" &&
            currentElem.tagName === "INPUT" &&
            currentElem.type === "checkbox"
          ) {
            // if (currentElem.
              console.log(currentElem);
              console.log(currentElem.checked);
                sessionStorage.setItem(currentElem.id, currentElem.checked);

            //   console.log(currentElem.tagName)
          }
        }
  }
  console.log("saved");
}
function loadInput() {
    var inputs, index;
    // console.log("load attempt")
    for (const tag of tags) {
      inputs = document.getElementsByTagName(tag[0]);
      for (index = 0; index < inputs.length; ++index) {
        currentElem = inputs[index];
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
              if (sessionStorage.getItem(currentElem.id) !== null) {
                  currentElem.value = sessionStorage.getItem(currentElem.id);
              }
          }
          else if (
              tag[0] === "input" &&
              tag[1] === "checkbox" &&
              currentElem.tagName === "INPUT" &&
              currentElem.type === "checkbox"
          ) {
              if (sessionStorage.getItem(currentElem.id) === "true")
                currentElem.click();
          }

      }
    }
  console.log("loaded");
}

