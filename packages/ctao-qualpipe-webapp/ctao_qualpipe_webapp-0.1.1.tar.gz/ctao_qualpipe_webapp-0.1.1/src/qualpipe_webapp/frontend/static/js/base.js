// to avoid eventListener duplications
const resizeListeners = {};

function adjustContentPadding() {
  const body = document.querySelector("body");
  const wrapper = document.querySelector("div#wrapper");
  const sidebarWrapper = document.querySelector("div#sidebar-wrapper");
  const pageContentWrapper = document.querySelector("div#page-content-wrapper");
  const pageContentWrapperChild = document.querySelector(
    "div#page-content-wrapper div"
  );
  const navbar1 = document.querySelector(".first-nav.navbar.fixed-top");
  const footer = document.querySelector(".footer.fixed-bottom");
  const navbar2 = document.querySelector(".second-nav.navbar");
  const navbarToggler = document.querySelector("#navbarToggler");
  const navbarToggler2 = document.querySelector("#navbarToggler2");

  navbarToggler.style.maxHeight =
    window.innerHeight - navbar1.offsetHeight - footer.offsetHeight + "px";

  if (navbar2 === null) {
    body.style.paddingTop = navbar1.offsetHeight + "px";
    wrapper.style.minHeight =
      window.innerHeight - navbar1.offsetHeight - footer.offsetHeight + "px";
  } else {
    body.style.paddingTop = navbar1.offsetHeight + navbar2.offsetHeight + "px";
    wrapper.style.minHeight =
      window.innerHeight -
      navbar1.offsetHeight -
      navbar2.offsetHeight -
      footer.offsetHeight +
      "px";
    navbarToggler2.style.maxHeight = wrapper.style.minHeight;
  }
  sidebarWrapper.style.maxHeight = wrapper.style.minHeight;
  pageContentWrapper.style.maxHeight = wrapper.style.minHeight;
  pageContentWrapperChild.style.paddingBottom = footer.offsetHeight + "px";
}

// Adjust at any reload and resizing
window.addEventListener("DOMContentLoaded", adjustContentPadding);
window.addEventListener("resize", adjustContentPadding);
