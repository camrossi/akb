// console.log("Hello Console");

// // let btn = document.createElement("button");
// // btn.innerText("Click here for new square");
// // document.body.appendChild(btn);

// let btn = document.createElement("button");
// btn.innerHTML = "Click Me";
// document.body.appendChild(btn);
// let i = 0;
// btn.onclick = function () {
//   console.log("button was clicked " + i + " time(s)");
//   btn.innerHTML = "Click Me " + i;

//   // const newSquare =
//   // 	document.createElement("user-node", { name: "hi1" });
//   const newSquare = new Node(i);
//   document.body.appendChild(newSquare);
//   i++;
// };

// document.addEventListener("mousedown", (e) => {
//   if (e.target) window.targetElement = e.target;
// });
// document.addEventListener("mousemove", (e) => {
//   // Currently pressed down on some element
//   const { targetElement } = window;
//   if (
//     targetElement &&
//     (targetElement.classList.contains("square") ||
//       targetElement.tagName === "USER-NODE")
//   ) {
//     console.dir(e, { depth: 100 });
//     targetElement.style.position = "absolute";
//     targetElement.style.left = `${e.x - 50}px`;
//     targetElement.style.top = `${e.y - 50}px`;
//   }
// });
// document.addEventListener("mouseup", (e) => {
//   window.targetElement = null;
// });

// // document.addEventListener('onclick', e => {

// //     // console.log('test')

// //     // e.target.style.color = 'blue'
// //     // if (!window.firstElement) return window.firstElement = e.target
// //     // if (!window.secondElement) return window.secondElement = e.target

// //     // TO-DO Draw a line between both

// // })
const pages = [
  // ["", "required"],
  ["login", "required"],
  ["l3out", "required"],
  ["vcenterlogin", "required"],
  ["vctemplate", "not required"],
  ["vcenter", "required"],
  ["calico_nodes", "required"],
  ["cluster", "required"],
  ["cluster_network", "required"],
  ["create", "required"],
];

const template = document.createElement("template");
// template.classList.add("square");
template.innerHTML = `
        <div></div>
`;
	//     <div style="width: 95%; height: 150px; background-color: green; border-style: solid; margin: auto">
    //     <div id="status-bar-container"></div>
    //     <h3
    //       style="justify-content: center; 
	// 	font-family: Arial, Helvetica, sans-serif; 
	// 	text-align: center;  
	// 	padding: 20px 0;"
    //     ></h3>
    //   </div>;

class StatusBar extends HTMLElement {
  constructor(name) {
      super();
    
    const containerDiv = document.createElement("div");
    containerDiv.classList.add("pagination")
    containerDiv.style =
        "width: 95%; height: 20px; background-color: white; border-style: solid; border-width: thin; margin: auto; display:flex; justify-content: space-evenly";
    
    const currentPage = pageNumber(getPageName());
    let index = 0;
    for (const page of pages) {
      const pageName = page[0];
      const child = document.createElement("a");
      if (pageName !== "") {
        child.innerText = pageName;
        child.href = pageName
      } else {
        child.innerText = "pick fabric";
        child.href = ""
      } 
      if (currentPage > index) {
        child.style.color = "green";
      } else if (currentPage === index) {
        child.style.color = "yellow";
      } else {
        child.style.color = "grey";
      }
      containerDiv.appendChild(child);
      index++;
    }
    console.log(containerDiv)
      
    // document.querySelector("status-bar-container")
    template.content.appendChild(containerDiv)
    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(template.content.cloneNode(true));

    // console.log(this.shadowRoot.querySelector("status-bar-container"));
    // console.log(document.getElementById("status-bar-container"));
  }
}

function getPageName() {
  const path = window.location.pathname;
  const page = path.split("/").pop();
  console.log(page);
  return page;
}

function pageNumber(pageName) {
  let index = 0;
  for (const arr of pages) {
    if (arr[0] === pageName) {
      return index;
    }
    index++;
  }
  return -1;
}

function changePage(futurePage, currentPage) {
  if (typeof (currentPage) === "string")
    currentPage = pageNumber(currentPage);
  if (typeof futurePage === "string")
    futurePage = pageNumber(futurePage);
  if (typeof (currentPage) === "number" && typeof (futurePage) === "number") {
    // if the page user wants to switch to is before the current page, that is always allowed
    if (futurePage < currentPage) return futurePage;
    // this is if the page user wants to switch to is the create page, or the last page
    else if (futurePage === pages.length - 1) return futurePage;
    // this is if the page user wants to switch to is after the current page but not the create page
    else {
      return currentPage;
    }
  }
  else
    console.log("currentPage or futurePage or both of them do not have number values")
  return currentPage;
}

window.customElements.define("status-bar", StatusBar);
