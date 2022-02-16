const tags = [["input", "text"], ["textarea"], ["input", "list"], ["select"]];
function saveInput() {
  var inputs, index;
  
    for (const tag of tags) {
        inputs = document.getElementsByTagName(tag[0]);
        for (index = 0; index < inputs.length; ++index) {
          currentElem = inputs[index];
          if (tag.length == 1 || currentElem.type === tag[1]) {
            console.log(currentElem)
            sessionStorage.setItem(currentElem.id, currentElem.value);
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
        if (tag.length == 1 || currentElem.type === tag[1]) {
          console.log(currentElem)
            if (sessionStorage.getItem(currentElem.id) !== null) {
                currentElem.value = sessionStorage.getItem(currentElem.id);
            }
        }
      }
    }
  console.log("loaded");
}

