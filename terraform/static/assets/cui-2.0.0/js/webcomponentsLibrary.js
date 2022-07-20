let pages;
let ndfc = false;

var getUrlParameter = function getUrlParameter(sParam) {
  var sPageURL = window.location.search.substring(1),
    sURLVariables = sPageURL.split("&"),
    sParameterName,
    i;

  for (i = 0; i < sURLVariables.length; i++) {
    sParameterName = sURLVariables[i].split("=");

    if (sParameterName[0] === sParam) {
      return sParameterName[1] === undefined
        ? true
        : decodeURIComponent(sParameterName[1]);
    }
  }
  return "";
};

function addFabricToURL() {
  const fabric = getUrlParameter("fabric_type");
  if (fabric === "" || fabric === "aci")
    return "?fabric_type=aci";
  else if (fabric === "vxlan_evpn")
    return "?fabric_type=vxlan_evpn";
}

function pagesInitialization() {
  const fabric = getUrlParameter("fabric_type");
  console.log("deploy:", sessionStorage.getItem("deploy"))
  console.log("bare_metal:", sessionStorage.getItem("bare_metal"))
  if (fabric === "")
    ndfc = false;
  else if (fabric === "vxlan_evpn")
    ndfc = true;
  if (sessionStorage.getItem("deploy") === "true" && sessionStorage.getItem("bare_metal") === "true") {
    console.log("Deploy on ACI and Configure BareMetal Servers");
    pages = [
      ["", "required"],
      ["login", "required"],
      ["l3out", "required"],
      ["calico_nodes", "required"],
      ["cluster", "required"],
      ["cluster_network", "required"],
      ["create", "required"],
    ];
  }else if (sessionStorage.getItem("deploy") === "false") {
    console.log("Deploy on ACI NO Nodes");
    pages = [
      ["", "required"],
      ["login", "required"],
      ["l3out", "required"],
      ["cluster_network", "required"],
      ["create", "required"],
    ];
  } else if (ndfc) {
    pages = [
      ["", "required"],
      ["login", "required"],
      ["fabric", "required"],
      ["vcenterlogin", "required"],
      ["vctemplate", "not required"],
      ["vcenter", "required"],
      ["calico_nodes", "required"],
      ["cluster", "required"],
      ["cluster_network", "required"],
      ["create", "required"],
    ];
  } else {
    console.log("Deploy on ACI and VMs");
    pages = [
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
  }
}
pagesInitialization();

const template = document.createElement("template");
// template.classList.add("square");
template.innerHTML = `
        <div></div>
`;

class StatusBar extends HTMLElement {
  constructor() {
    super();
    
    const containerDiv = document.createElement("div");
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
        (sessionStorage.getItem("skipToCreate") === null ||
          parseInt(sessionStorage.getItem("skipToCreate")) === -1 ||
          index < parseInt(sessionStorage.getItem("skipToCreate")))
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
    
    if (currentPage <= parseInt(sessionStorage.getItem("skipToCreate")))
      sessionStorage.setItem("skipToCreate", -1);
    template.content.removeChild(template.content.firstElementChild)
    template.content.appendChild(containerDiv);
    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(template.content.cloneNode(true));
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
  
  if (typeof (currentPage) === "number" && typeof (futurePage) === "number" && futurePage >= 0 && futurePage !== currentPage) {
    // if the page user wants to switch to is before the current page, that is always allowed
    if (futurePage < currentPage) {
      // window.location.href = window.location.href
      // User is on the create page
      if (currentPage === pages.length - 1) {
        if (
          parseInt(sessionStorage.getItem("skipToCreate")) === -1 ||
          futurePage <= parseInt(sessionStorage.getItem("skipToCreate"))
        ) {
          console.log("go to future page: " + futurePage);
          window.location.href =
            window.location.origin +
            "/" +
            pages[futurePage][0] +
            addFabricToURL();
          if (futurePage <= skipToCreate)
            sessionStorage.setItem("skipToCreate", -1);
          return futurePage;
        } else {
          return currentPage;
        }
      }
      // User is currently not on the create page
      else {
        console.log("go to future page: " + futurePage);
        if (futurePage === 0)
          window.location.href = window.location.origin + "/" + pages[futurePage][0];
        else
          window.location.href =
            window.location.origin +
            "/" +
            pages[futurePage][0] +
            addFabricToURL();
        if (futurePage <= skipToCreate)
          sessionStorage.setItem("skipToCreate", -1);
        return futurePage;
      }
    }

    // this is if the page user wants to switch to is the create page, or the last page
    else if (futurePage === pages.length - 1) {
      console.log("go to create page: " + futurePage);
      sessionStorage.setItem("skipToCreate", currentPage);
      window.location.href =
        window.location.origin + "/" + pages[futurePage][0] + addFabricToURL();
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
