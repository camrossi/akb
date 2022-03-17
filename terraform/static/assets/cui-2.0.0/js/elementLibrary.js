const bottomBarTemplate = document.createElement("template");
bottomBarTemplate.innerHTML = `
                <div class="container">
                    <footer class="footer footer--tertiary" id="_uidca388897">
                        <div class="footer__links">
                            <ul class="list list--inline" id="_uid08010aa3">
                                <li><a href="http://www.cisco.com/cisco/web/siteassets/contacts/index.html" target="_blank"
                                                                                                            id="_uidbb5636c3">Contacts</a></li>
                                <li><a href="https://secure.opinionlab.com/ccc01/o.asp?id=jBjOhqOJ" target="_blank"
                                                                                                    id="_uid92d9bfeb">Feedback</a></li>
                                <li><a href="https://www.cisco.com/c/en/us/about/help.html" target="_blank"
                                                                                            id="_uidcbd80f09">Help</a></li>
                                <li><a href="http://www.cisco.com/c/en/us/about/sitemap.html" target="_blank"
                                                                                              id="_uid134ab5bc">Site Map</a></li>
                                <li><a href="https://www.cisco.com/c/en/us/about/legal/terms-conditions.html" target="_blank"
                                                                                                              id="_uidf3e2c0a6">Terms &amp; Conditions</a></li>
                                <li><a href="https://www.cisco.com/c/en/us/about/legal/privacy-full.html" target="_blank"
                                                                                                          id="_uide8b9adf9">Privacy Statement</a></li>
                                <li><a href="https://www.cisco.com/c/en/us/about/legal/privacy-full.html#cookies" target="_blank"
                                                                                                                  id="_uid5580971c">Cookie Policy</a></li>
                                <li><a href="https://www.cisco.com/c/en/us/about/legal/trademarks.html" target="_blank"
                                                                                                        id="_uidbe7db422">Trademarks</a></li>
                            </ul>
                        </div>
                    </footer>
                </div>
                <link rel="stylesheet" type="text/css"
                    href="static/assets/cui-2.0.0/css/cui-standard.min.css">
                <link rel="stylesheet" type="text/css" href="static/assets/cui-2.0.0/css/frame.css">
                <link rel="stylesheet" type="text/css" href="static/assets/cui-2.0.0/css/style.css"></link>
`;

class BottomBar extends HTMLElement {
  constructor(name) {
    super();

    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(bottomBarTemplate.content.cloneNode(true));
  }
}

window.customElements.define("bottom-bar", BottomBar);

const topBarTemplate = document.createElement("template");
topBarTemplate.innerHTML = `
        <header class="header" id="_uid818d10e3">
            <div class="container">
               <div class="header-panels">
                  <div class="header-panel"><a href="http://www.cisco.com" target="_blank" class="header__logo"
                        id="_uid5a704e92"><span class="icon-cisco"></span></a>
                     <div class="header__title">Nexus Kubernetes Tools</div>
                  </div>
                  <div class="header-panel header-panel--right"><a data-hreftarget="_self" target="_self"
                        data-hreflink="https://aci-github.cisco.com/ddastoli/calico_aci/tree/pythonterraform"
                        href="https://aci-github.cisco.com/ddastoli/calico_aci/tree/pythonterraform"
                        data-hreftitle="Source Code" title="Source Code" class="header-item"
                        id="_uidb14b144f">GitHub</a><a data-hreftarget="_self" target="_self"
                        data-hreflink="https://aci-github.cisco.com/ddastoli/calico_aci/issues"
                        href="https://aci-github.cisco.com/ddastoli/calico_aci/issues" data-hreftitle="Open An Issue"
                        title="Open An Issue" class="header-item" id="_uid2e094e7e">Open An Issue</a></div>
               </div>
            </div>
        </header>
        <link rel="stylesheet" type="text/css"
            href="static/assets/cui-2.0.0/css/cui-standard.min.css">
        <link rel="stylesheet" type="text/css" href="static/assets/cui-2.0.0/css/frame.css">
        <link rel="stylesheet" type="text/css" href="static/assets/cui-2.0.0/css/style.css"></link>
`;

class TopBar extends HTMLElement {
  constructor(name) {
    super();

    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(topBarTemplate.content.cloneNode(true));
  }
}

window.customElements.define("top-bar", TopBar);

const nextPreviousTemplate = document.createElement("template");
nextPreviousTemplate.innerHTML = `
         <div class="container">
            <div class="navibox">
               <input id="submit" type="submit" value="Next" class="btn btn--wide" name="button" style="margin-left: 10px;" onclick="saveInput()">
               <input type="submit" value="Previous" class="btn btn--wide" name="button" style="margin-left: 0px" onclick="saveInput()">
            </div>
         </div>
        <link rel="stylesheet" type="text/css"
            href="static/assets/cui-2.0.0/css/cui-standard.min.css">
        <link rel="stylesheet" type="text/css" href="static/assets/cui-2.0.0/css/frame.css">
        <link rel="stylesheet" type="text/css" href="static/assets/cui-2.0.0/css/style.css"></link>
`;

class NextPrevious extends HTMLElement {
  constructor(name) {
    super();

    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(nextPreviousTemplate.content.cloneNode(true));
  }
}

window.customElements.define("next-previous", NextPrevious);
