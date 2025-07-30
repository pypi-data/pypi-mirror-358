import { jsx as o, jsxs as c } from "react/jsx-runtime";
import { useState as l } from "react";
import { componentStore as n } from "routelit-client";
function m({ children: e, className: t = "" }) {
  return /* @__PURE__ */ o("div", { className: "root " + t, children: e });
}
function u({ isOpen: e, toggle: t }) {
  return /* @__PURE__ */ o("button", { className: "sidebar-toggle", onClick: t, children: e ? "x" : ">" });
}
function d({ defaultOpen: e, children: t, className: i, ...s }) {
  const [r, a] = l(e || !1);
  return /* @__PURE__ */ c("aside", { className: i, ...s, children: [
    /* @__PURE__ */ o("div", { className: `content ${r ? "" : "hidden"}`, children: t }),
    /* @__PURE__ */ o(u, { isOpen: r, toggle: () => a(!r) })
  ] });
}
function g({ children: e, ...t }) {
  return /* @__PURE__ */ o("main", { ...t, children: e });
}
n.register("root", m);
n.register("sidebar", d);
n.register("main", g);
n.forceUpdate();
console.log(" setup done routelit elements ", n);
export {
  g as Main,
  m as Root,
  d as Sidebar
};
