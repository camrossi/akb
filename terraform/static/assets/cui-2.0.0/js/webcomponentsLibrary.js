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
      containerDiv.style =
          "width: 95%; height: 150px; background-color: white; border-style: solid; margin: auto; display:flex; justify-content: space-evenly";
      for (const page of pages) {
        const pageName = page[0];
        const child = document.createElement("div");

        if (pageName !== "") {
          child.innerText = pageName;
        } else {
          child.innerText = "Pick Fabric";
        } 
        containerDiv.appendChild(child);
      }
      console.log(containerDiv)
      
          // document.querySelector("status-bar-container")
          template.content.appendChild(containerDiv)
    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    // this.shadowRoot.querySelector("h3").innerText = this.getAttribute("name");

    // this.shadowRoot.querySelector("h3").innerText = "Node" + " " + name;
      console.log(this.shadowRoot.querySelector("status-bar-container"));
      console.log(document.getElementById("status-bar-container"));
    // 		this.innerHTML = `
    // 	    <div
    //       style="width: 100px; height: 100px; background-color: green; border-style: solid;"
    //     >
    // 		<h3 style="justify-content: center;"></h3>
    // 		</div>
    // `;
  }
}

window.customElements.define("status-bar", StatusBar);
