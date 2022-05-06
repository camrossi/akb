const pages = [
  ["", "required"],
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
    // containerDiv.classList.add("pagination")
    containerDiv.style =
        "width: 100%; height: 75px; font-size: 16px; background-color: white; border-style: solid; border-width: thin; margin: auto; display:flex; justify-content: space-evenly";
    
    const currentPage = pageNumber(getPageName());
    let index = 0;
    for (const page of pages) {
      const pageName = page[0];
      const child = document.createElement("a");
      child.style = "display: flex; justify-content: space-around;";
      
      if (pageName !== "") {
        child.innerText = pageName;
        // child.href = pageName;
      } else {
        child.innerText = "pick fabric";
        // child.href = "";
      } 
      const iconContainer = document.createElement("div");
      iconContainer.style = "display: flex; justify-content: space-around;";
      const childIcon = document.createElement("img");
      childIcon.style="margins: auto;"
      if (
        currentPage > index &&
        (parseInt(sessionStorage.getItem("skipToCreate")) === -1 ||
          currentPage < parseInt(sessionStorage.getItem("skipToCreate")))
      ) {
        child.style.color = "green";
        childIcon.src =
          "../../../../static/images/done_FILL0_wght400_GRAD0_opsz48.svg";
      } else if (currentPage < index) {
        child.style.color = "grey";
        childIcon.src =
          "../../../../static/images/minimize_FILL0_wght400_GRAD0_opsz48.svg";
      } else if (currentPage === index) {
        child.style.color = "orange";
        childIcon.src =
          "../../../../static/images/pending_FILL0_wght400_GRAD0_opsz48.svg";
      } else {
        child.style.color = "grey";
        childIcon.src =
          "../../../../static/images/minimize_FILL0_wght400_GRAD0_opsz48.svg";
      }
      const nameAndIcon = document.createElement("div");
      // const icon = document.createElement("div");

      nameAndIcon.appendChild(child);
      iconContainer.appendChild(childIcon);
      nameAndIcon.appendChild(iconContainer);
      nameAndIcon.setAttribute("indexNumber", index)
      nameAndIcon.setAttribute("onclick", "changePage(parseInt(this.getAttribute('indexNumber')))");
      containerDiv.appendChild(nameAndIcon);
      index++;
    }
    // console.log(containerDiv)
    // const nameAndIcon = document.createElement("div");
      
    // document.querySelector("status-bar-container")
    // console.log(containerDiv);
    if (pageNumber <= parseInt(sessionStorage.getItem("skipToCreate")))
      sessionStorage.setItem("skipToCreate", -1);
    template.content.removeChild(template.content.firstElementChild)
    template.content.appendChild(containerDiv);
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

function pageNumberToName(pageNumber) {
  return pages[pageNumber];
}
function skipToCreate() {
  if (sessionStorage.getItem("skipToCreate") === null)
    sessionStorage.setItem("skipToCreate", -1);
}
skipToCreate();


function changePage(futurePage, currentPage) {
  if (currentPage === undefined)
    currentPage = getPageName();
  if (typeof (currentPage) === "string")
    currentPage = pageNumber(currentPage);
  if (typeof futurePage === "string")
    futurePage = pageNumber(futurePage);
  console.log("current page: " + currentPage);
  console.log("future page: " + futurePage);
  
  if (typeof (currentPage) === "number" && typeof (futurePage) === "number" && futurePage >= 0) {
    // if the page user wants to switch to is before the current page, that is always allowed
    if (futurePage < currentPage) {
      // window.location.href = window.location.href
      // User is on the create page
      if (currentPage === pages.length - 1) {
        if (futurePage <= parseInt(sessionStorage.getItem("skipToCreate"))) {
          console.log("go to future page: " + futurePage);
          window.location.href =
            window.location.origin + "/" + pages[futurePage][0];
          if (futurePage <= skipToCreate)
            sessionStorage.setItem("skipToCreate", -1);
          return futurePage;
        }
        else {
          return currentPage;
        }
      }
      // User is currently not on the create page
      else {
        console.log("go to future page: " + futurePage);
        window.location.href =
          window.location.origin + "/" + pages[futurePage][0];
        if (futurePage <= skipToCreate)
          sessionStorage.setItem("skipToCreate", -1);
        return futurePage;
      }
    }

    // this is if the page user wants to switch to is the create page, or the last page
    else if (futurePage === pages.length - 1) {
      console.log("go to create page: " + futurePage);
      sessionStorage.setItem("skipToCreate", currentPage);
      window.location.href = window.location.origin + "/" + pages[futurePage][0];
      return futurePage;
    }

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
