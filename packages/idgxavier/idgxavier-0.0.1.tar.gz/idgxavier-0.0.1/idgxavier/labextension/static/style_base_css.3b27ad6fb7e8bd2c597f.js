"use strict";
(self["webpackChunk_xavier_idgxavier"] = self["webpackChunk_xavier_idgxavier"] || []).push([["style_base_css"],{

/***/ "./node_modules/css-loader/dist/cjs.js!./style/Cell.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/Cell.css ***!
  \**************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.cell {
  width: 100%;
  /*height: 100%;*/ /* why there's no effect? */
  vertical-align: middle;
  /* padding-left: 5px; */
  /* padding-right: 5px; */
  font-weight: normal;
}

.cell::-webkit-scrollbar {
  display: none;
}

.cell.xavier-cell-empty {
  color: #aaaaaa !important;
}

.text-bold {
  font-weight: bold;
}`, "",{"version":3,"sources":["webpack://./style/Cell.css"],"names":[],"mappings":"AAAA;EACE,WAAW;EACX,gBAAgB,EAAE,2BAA2B;EAC7C,sBAAsB;EACtB,uBAAuB;EACvB,wBAAwB;EACxB,mBAAmB;AACrB;;AAEA;EACE,aAAa;AACf;;AAEA;EACE,yBAAyB;AAC3B;;AAEA;EACE,iBAAiB;AACnB","sourcesContent":[".cell {\r\n  width: 100%;\r\n  /*height: 100%;*/ /* why there's no effect? */\r\n  vertical-align: middle;\r\n  /* padding-left: 5px; */\r\n  /* padding-right: 5px; */\r\n  font-weight: normal;\r\n}\r\n\r\n.cell::-webkit-scrollbar {\r\n  display: none;\r\n}\r\n\r\n.cell.xavier-cell-empty {\r\n  color: #aaaaaa !important;\r\n}\r\n\r\n.text-bold {\r\n  font-weight: bold;\r\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/SidePanel/DetailView.css":
/*!******************************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/SidePanel/DetailView.css ***!
  \******************************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.xavier-ss-wrapper {
  display: block;
  position: relative;
  width: 100%;
  height: calc(100% - 30px);
  overflow: auto;
}

.xavier-dvt-name.xavier-st-text {
  width: 100px;
}

.xavier-cc-float-right {
  position: sticky; /* Let it horizontally fixed but vertically not fixed */
  /* right: 10px; */ /* the right is not fixed */
  opacity: 0.9;
  /* box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3); */
  background-color: white;
  z-index: 1000;
}`, "",{"version":3,"sources":["webpack://./style/SidePanel/DetailView.css"],"names":[],"mappings":"AAAA;EACE,cAAc;EACd,kBAAkB;EAClB,WAAW;EACX,yBAAyB;EACzB,cAAc;AAChB;;AAEA;EACE,YAAY;AACd;;AAEA;EACE,gBAAgB,EAAE,uDAAuD;EACzE,iBAAiB,EAAE,2BAA2B;EAC9C,YAAY;EACZ,gDAAgD;EAChD,uBAAuB;EACvB,aAAa;AACf","sourcesContent":[".xavier-ss-wrapper {\r\n  display: block;\r\n  position: relative;\r\n  width: 100%;\r\n  height: calc(100% - 30px);\r\n  overflow: auto;\r\n}\r\n\r\n.xavier-dvt-name.xavier-st-text {\r\n  width: 100px;\r\n}\r\n\r\n.xavier-cc-float-right {\r\n  position: sticky; /* Let it horizontally fixed but vertically not fixed */\r\n  /* right: 10px; */ /* the right is not fixed */\r\n  opacity: 0.9;\r\n  /* box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3); */\r\n  background-color: white;\r\n  z-index: 1000;\r\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/SidePanel/Icons.css":
/*!*************************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/SidePanel/Icons.css ***!
  \*************************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.xavier-mdt-icon-wrapper {
  display: inline-block;
  width: var(--xavier-icon-width);
  height: 100%;
  text-align: center;
  vertical-align: top;
  line-height: calc(100% + 15px); /* Maybe hard code */
  cursor: pointer;
}

.xavier-mdt-icon-wrapper:hover {
  background-color: var(--jp-layout-color2);
}

.xavier-mdt-icon-wrapper.xavier-mdt-icon-placeholder {
  cursor: default;
}

.xavier-mdt-icon-wrapper.xavier-mdt-icon-placeholder:hover {
  background-color: transparent;
}`, "",{"version":3,"sources":["webpack://./style/SidePanel/Icons.css"],"names":[],"mappings":"AAAA;EACE,qBAAqB;EACrB,+BAA+B;EAC/B,YAAY;EACZ,kBAAkB;EAClB,mBAAmB;EACnB,8BAA8B,EAAE,oBAAoB;EACpD,eAAe;AACjB;;AAEA;EACE,yCAAyC;AAC3C;;AAEA;EACE,eAAe;AACjB;;AAEA;EACE,6BAA6B;AAC/B","sourcesContent":[".xavier-mdt-icon-wrapper {\r\n  display: inline-block;\r\n  width: var(--xavier-icon-width);\r\n  height: 100%;\r\n  text-align: center;\r\n  vertical-align: top;\r\n  line-height: calc(100% + 15px); /* Maybe hard code */\r\n  cursor: pointer;\r\n}\r\n\r\n.xavier-mdt-icon-wrapper:hover {\r\n  background-color: var(--jp-layout-color2);\r\n}\r\n\r\n.xavier-mdt-icon-wrapper.xavier-mdt-icon-placeholder {\r\n  cursor: default;\r\n}\r\n\r\n.xavier-mdt-icon-wrapper.xavier-mdt-icon-placeholder:hover {\r\n  background-color: transparent;\r\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/SidePanel/MetadataView.css":
/*!********************************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/SidePanel/MetadataView.css ***!
  \********************************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.xavier-metadata-view {
  display: block;
  width: 100%;
  height: 100%; /* Leave space for xavier-sidepanel-view-title */
  overflow-x: hidden;
  overflow-y: auto;
}

/* mv == metadata view, df = dataframe */
.xavier-mv-df-list {
  display: block;
  width: 100%;
  height: calc(100% - 20px);
}

.xavier-mv-df {
  display: block;
  width: 100%;
}

/* mdt = mv-df-title */
.xavier-mdt-wrapper {
  display: block;
  width: 100%;
  height: 25px;
}

.xavier-mdt-name-wrapper {
  display: inline-block;
  width: 100%;
  /* width: calc(100% - 63px); */
  height: 100%;
  vertical-align: top;
  cursor: pointer;
}

.xavier-mdt-name-wrapper:hover {
  background-color: var(--jp-layout-color2);
}

.xavier-mdt-name {
  display: inline-block;
  width: calc(60% - 10px); /* leave the space for xavier-mdt-shape */
  height: 100%;
  padding-left: 5px;
  padding-right: 5px;
  color: #000;
  font-weight: 700;
  font-size: var(--xavier-df-font-size);
  line-height: calc(100% + 10px); /* Maybe hard code */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.xavier-mdt-shape {
  display: inline-block;
  width: 40%; /* Correspond to .xavier-mdt-name */
  height: 100%;
  color: #000;
  font-size: var(--xavier-df-font-size);
  line-height: calc(100% + 10px); /* Maybe hard code */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.xavier-mv-col {
  display: block;
  width: 100%;
  padding-left: 10px;
}

.xavier-mv-itemlist-wrapper {
  display: block;
  width: 100%;
  /* min-height: 50px; */
}

.xavier-mv-cate {
  display: block;
  width: calc(100% - 10px);
  height: var(--xavier-cate-item-height);
  padding-left: 10px;
}

.xavier-mct-name.xavier-mv-cate-value {
  overflow: hidden;
  font-size: var(--xavier-value-font-size);
  width: 85%;
  padding-left: 10px;
  padding-right: 10px;
  /* padding-left: 0; */
}

.xavier-mv-search-bar {
  display: block;
  width: 100%;
  /* width: calc(100% - 5px - var(--xavier-scrollbar-width));  */
  /* consider the margin-left and the scrollbar width */
  /* margin-left: 5px; */
  /* margin-top: 5px; */
}

.xavier-mv-search-input {
  width: 100%;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
  outline: none;
  font-size: var(--xavier-value-font-size);
}

.xavier-mv-num-search-input {
  width: calc(50% - 5px - var(--xavier-scrollbar-width)); 
}

.xavier-mv-num-search-mid {
  display: inline-block;
  width: 7%;
  text-align: center;
  font-size: var(--xavier-value-font-size);
}

.xavier-mv-search-input:focus {
  border-color: #66afe9;
  box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 4px rgba(102, 175, 233, .6);
}

.xavier-mv-search-container {
  position: absolute;
  top: 60px;
  width: 180px;
  /* width: 100%; */
  z-index: 1;
}

.xavier-mv-cate-list {
  display: block;
  width: 100%;
  max-height: calc(var(--xavier-cate-item-height) * 9.5);
  overflow-x: hidden;
  overflow-y: auto;
  background-color: white;
}

/* mct = mv-col-title */
.xavier-mct-wrapper {
  display: block;
  width: 100%;
  height: 25px;
}

.xavier-mct-name-wrapper {
  display: inline-block;
  /* width: calc(100% - 21px); */
  height: 100%;
  vertical-align: top;
  cursor: pointer;
}

.xavier-mct-name-wrapper:hover {
  background-color: var(--jp-layout-color2);
}

.xavier-mct-name {
  display: inline-block;
  width: calc(55% - 10px); /* leave the space for xavier-mct-histogram */
  height: 100%;
  padding-left: 5px;
  padding-right: 5px;
  color: #000;
  font-weight: normal;
  /* font-size: 14px; */ /* Default is 13px */
  line-height: calc(100% + 10px); /* Maybe hard code */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.xavier-mct-histogram {
  display: inline-flex;
  position: relative;
  width: calc(45% - 10px); /* leave the space for xavier-mct-name */
  height: 100%;
  /* margin-right: 10px; */
  background: #f5f5f5;
  align-items: flex-end;
}

.xavier-mct-histogram.xavier-mv-cate-hist {
  width: calc(30% - 15px);
}

.xavier-mct-histogram-rect {
  display: block;
  height: 100%;
  background-color: #b5e1f7; /*#EDF7FA too light*/
}

.xavier-mct-histogram-text {
  font-size: 10px; /*hard code */
  display: inline-block;
  position: absolute;
  width: calc(100% - 10px);
  height: 100%;
  color: black;
  right: 10px;
  flex-shrink: 1;
  text-align: right;
  line-height: calc(100% + 10px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.xavier-mct-histogram-text.xavier-mv-cate-str {
  font-size: var(--xavier-value-font-size);
}

.xavier-mct-histogram-bar {
  display: inline-block;
}`, "",{"version":3,"sources":["webpack://./style/SidePanel/MetadataView.css"],"names":[],"mappings":"AAAA;EACE,cAAc;EACd,WAAW;EACX,YAAY,EAAE,gDAAgD;EAC9D,kBAAkB;EAClB,gBAAgB;AAClB;;AAEA,wCAAwC;AACxC;EACE,cAAc;EACd,WAAW;EACX,yBAAyB;AAC3B;;AAEA;EACE,cAAc;EACd,WAAW;AACb;;AAEA,sBAAsB;AACtB;EACE,cAAc;EACd,WAAW;EACX,YAAY;AACd;;AAEA;EACE,qBAAqB;EACrB,WAAW;EACX,8BAA8B;EAC9B,YAAY;EACZ,mBAAmB;EACnB,eAAe;AACjB;;AAEA;EACE,yCAAyC;AAC3C;;AAEA;EACE,qBAAqB;EACrB,uBAAuB,EAAE,yCAAyC;EAClE,YAAY;EACZ,iBAAiB;EACjB,kBAAkB;EAClB,WAAW;EACX,gBAAgB;EAChB,qCAAqC;EACrC,8BAA8B,EAAE,oBAAoB;EACpD,gBAAgB;EAChB,uBAAuB;EACvB,mBAAmB;AACrB;;AAEA;EACE,qBAAqB;EACrB,UAAU,EAAE,mCAAmC;EAC/C,YAAY;EACZ,WAAW;EACX,qCAAqC;EACrC,8BAA8B,EAAE,oBAAoB;EACpD,gBAAgB;EAChB,uBAAuB;EACvB,mBAAmB;AACrB;;AAEA;EACE,cAAc;EACd,WAAW;EACX,kBAAkB;AACpB;;AAEA;EACE,cAAc;EACd,WAAW;EACX,sBAAsB;AACxB;;AAEA;EACE,cAAc;EACd,wBAAwB;EACxB,sCAAsC;EACtC,kBAAkB;AACpB;;AAEA;EACE,gBAAgB;EAChB,wCAAwC;EACxC,UAAU;EACV,kBAAkB;EAClB,mBAAmB;EACnB,qBAAqB;AACvB;;AAEA;EACE,cAAc;EACd,WAAW;EACX,8DAA8D;EAC9D,qDAAqD;EACrD,sBAAsB;EACtB,qBAAqB;AACvB;;AAEA;EACE,WAAW;EACX,YAAY;EACZ,sBAAsB;EACtB,kBAAkB;EAClB,sBAAsB;EACtB,aAAa;EACb,wCAAwC;AAC1C;;AAEA;EACE,sDAAsD;AACxD;;AAEA;EACE,qBAAqB;EACrB,SAAS;EACT,kBAAkB;EAClB,wCAAwC;AAC1C;;AAEA;EACE,qBAAqB;EACrB,6EAA6E;AAC/E;;AAEA;EACE,kBAAkB;EAClB,SAAS;EACT,YAAY;EACZ,iBAAiB;EACjB,UAAU;AACZ;;AAEA;EACE,cAAc;EACd,WAAW;EACX,sDAAsD;EACtD,kBAAkB;EAClB,gBAAgB;EAChB,uBAAuB;AACzB;;AAEA,uBAAuB;AACvB;EACE,cAAc;EACd,WAAW;EACX,YAAY;AACd;;AAEA;EACE,qBAAqB;EACrB,8BAA8B;EAC9B,YAAY;EACZ,mBAAmB;EACnB,eAAe;AACjB;;AAEA;EACE,yCAAyC;AAC3C;;AAEA;EACE,qBAAqB;EACrB,uBAAuB,EAAE,6CAA6C;EACtE,YAAY;EACZ,iBAAiB;EACjB,kBAAkB;EAClB,WAAW;EACX,mBAAmB;EACnB,qBAAqB,EAAE,oBAAoB;EAC3C,8BAA8B,EAAE,oBAAoB;EACpD,gBAAgB;EAChB,uBAAuB;EACvB,mBAAmB;AACrB;;AAEA;EACE,oBAAoB;EACpB,kBAAkB;EAClB,uBAAuB,EAAE,wCAAwC;EACjE,YAAY;EACZ,wBAAwB;EACxB,mBAAmB;EACnB,qBAAqB;AACvB;;AAEA;EACE,uBAAuB;AACzB;;AAEA;EACE,cAAc;EACd,YAAY;EACZ,yBAAyB,EAAE,oBAAoB;AACjD;;AAEA;EACE,eAAe,EAAE,aAAa;EAC9B,qBAAqB;EACrB,kBAAkB;EAClB,wBAAwB;EACxB,YAAY;EACZ,YAAY;EACZ,WAAW;EACX,cAAc;EACd,iBAAiB;EACjB,8BAA8B;EAC9B,gBAAgB;EAChB,uBAAuB;EACvB,mBAAmB;AACrB;;AAEA;EACE,wCAAwC;AAC1C;;AAEA;EACE,qBAAqB;AACvB","sourcesContent":[".xavier-metadata-view {\r\n  display: block;\r\n  width: 100%;\r\n  height: 100%; /* Leave space for xavier-sidepanel-view-title */\r\n  overflow-x: hidden;\r\n  overflow-y: auto;\r\n}\r\n\r\n/* mv == metadata view, df = dataframe */\r\n.xavier-mv-df-list {\r\n  display: block;\r\n  width: 100%;\r\n  height: calc(100% - 20px);\r\n}\r\n\r\n.xavier-mv-df {\r\n  display: block;\r\n  width: 100%;\r\n}\r\n\r\n/* mdt = mv-df-title */\r\n.xavier-mdt-wrapper {\r\n  display: block;\r\n  width: 100%;\r\n  height: 25px;\r\n}\r\n\r\n.xavier-mdt-name-wrapper {\r\n  display: inline-block;\r\n  width: 100%;\r\n  /* width: calc(100% - 63px); */\r\n  height: 100%;\r\n  vertical-align: top;\r\n  cursor: pointer;\r\n}\r\n\r\n.xavier-mdt-name-wrapper:hover {\r\n  background-color: var(--jp-layout-color2);\r\n}\r\n\r\n.xavier-mdt-name {\r\n  display: inline-block;\r\n  width: calc(60% - 10px); /* leave the space for xavier-mdt-shape */\r\n  height: 100%;\r\n  padding-left: 5px;\r\n  padding-right: 5px;\r\n  color: #000;\r\n  font-weight: 700;\r\n  font-size: var(--xavier-df-font-size);\r\n  line-height: calc(100% + 10px); /* Maybe hard code */\r\n  overflow: hidden;\r\n  text-overflow: ellipsis;\r\n  white-space: nowrap;\r\n}\r\n\r\n.xavier-mdt-shape {\r\n  display: inline-block;\r\n  width: 40%; /* Correspond to .xavier-mdt-name */\r\n  height: 100%;\r\n  color: #000;\r\n  font-size: var(--xavier-df-font-size);\r\n  line-height: calc(100% + 10px); /* Maybe hard code */\r\n  overflow: hidden;\r\n  text-overflow: ellipsis;\r\n  white-space: nowrap;\r\n}\r\n\r\n.xavier-mv-col {\r\n  display: block;\r\n  width: 100%;\r\n  padding-left: 10px;\r\n}\r\n\r\n.xavier-mv-itemlist-wrapper {\r\n  display: block;\r\n  width: 100%;\r\n  /* min-height: 50px; */\r\n}\r\n\r\n.xavier-mv-cate {\r\n  display: block;\r\n  width: calc(100% - 10px);\r\n  height: var(--xavier-cate-item-height);\r\n  padding-left: 10px;\r\n}\r\n\r\n.xavier-mct-name.xavier-mv-cate-value {\r\n  overflow: hidden;\r\n  font-size: var(--xavier-value-font-size);\r\n  width: 85%;\r\n  padding-left: 10px;\r\n  padding-right: 10px;\r\n  /* padding-left: 0; */\r\n}\r\n\r\n.xavier-mv-search-bar {\r\n  display: block;\r\n  width: 100%;\r\n  /* width: calc(100% - 5px - var(--xavier-scrollbar-width));  */\r\n  /* consider the margin-left and the scrollbar width */\r\n  /* margin-left: 5px; */\r\n  /* margin-top: 5px; */\r\n}\r\n\r\n.xavier-mv-search-input {\r\n  width: 100%;\r\n  padding: 5px;\r\n  border: 1px solid #ccc;\r\n  border-radius: 3px;\r\n  box-sizing: border-box;\r\n  outline: none;\r\n  font-size: var(--xavier-value-font-size);\r\n}\r\n\r\n.xavier-mv-num-search-input {\r\n  width: calc(50% - 5px - var(--xavier-scrollbar-width)); \r\n}\r\n\r\n.xavier-mv-num-search-mid {\r\n  display: inline-block;\r\n  width: 7%;\r\n  text-align: center;\r\n  font-size: var(--xavier-value-font-size);\r\n}\r\n\r\n.xavier-mv-search-input:focus {\r\n  border-color: #66afe9;\r\n  box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 4px rgba(102, 175, 233, .6);\r\n}\r\n\r\n.xavier-mv-search-container {\r\n  position: absolute;\r\n  top: 60px;\r\n  width: 180px;\r\n  /* width: 100%; */\r\n  z-index: 1;\r\n}\r\n\r\n.xavier-mv-cate-list {\r\n  display: block;\r\n  width: 100%;\r\n  max-height: calc(var(--xavier-cate-item-height) * 9.5);\r\n  overflow-x: hidden;\r\n  overflow-y: auto;\r\n  background-color: white;\r\n}\r\n\r\n/* mct = mv-col-title */\r\n.xavier-mct-wrapper {\r\n  display: block;\r\n  width: 100%;\r\n  height: 25px;\r\n}\r\n\r\n.xavier-mct-name-wrapper {\r\n  display: inline-block;\r\n  /* width: calc(100% - 21px); */\r\n  height: 100%;\r\n  vertical-align: top;\r\n  cursor: pointer;\r\n}\r\n\r\n.xavier-mct-name-wrapper:hover {\r\n  background-color: var(--jp-layout-color2);\r\n}\r\n\r\n.xavier-mct-name {\r\n  display: inline-block;\r\n  width: calc(55% - 10px); /* leave the space for xavier-mct-histogram */\r\n  height: 100%;\r\n  padding-left: 5px;\r\n  padding-right: 5px;\r\n  color: #000;\r\n  font-weight: normal;\r\n  /* font-size: 14px; */ /* Default is 13px */\r\n  line-height: calc(100% + 10px); /* Maybe hard code */\r\n  overflow: hidden;\r\n  text-overflow: ellipsis;\r\n  white-space: nowrap;\r\n}\r\n\r\n.xavier-mct-histogram {\r\n  display: inline-flex;\r\n  position: relative;\r\n  width: calc(45% - 10px); /* leave the space for xavier-mct-name */\r\n  height: 100%;\r\n  /* margin-right: 10px; */\r\n  background: #f5f5f5;\r\n  align-items: flex-end;\r\n}\r\n\r\n.xavier-mct-histogram.xavier-mv-cate-hist {\r\n  width: calc(30% - 15px);\r\n}\r\n\r\n.xavier-mct-histogram-rect {\r\n  display: block;\r\n  height: 100%;\r\n  background-color: #b5e1f7; /*#EDF7FA too light*/\r\n}\r\n\r\n.xavier-mct-histogram-text {\r\n  font-size: 10px; /*hard code */\r\n  display: inline-block;\r\n  position: absolute;\r\n  width: calc(100% - 10px);\r\n  height: 100%;\r\n  color: black;\r\n  right: 10px;\r\n  flex-shrink: 1;\r\n  text-align: right;\r\n  line-height: calc(100% + 10px);\r\n  overflow: hidden;\r\n  text-overflow: ellipsis;\r\n  white-space: nowrap;\r\n}\r\n\r\n.xavier-mct-histogram-text.xavier-mv-cate-str {\r\n  font-size: var(--xavier-value-font-size);\r\n}\r\n\r\n.xavier-mct-histogram-bar {\r\n  display: inline-block;\r\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/SidePanel/SidePanel.css":
/*!*****************************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/SidePanel/SidePanel.css ***!
  \*****************************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_MetadataView_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! -!../../node_modules/css-loader/dist/cjs.js!./MetadataView.css */ "./node_modules/css-loader/dist/cjs.js!./style/SidePanel/MetadataView.css");
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_DetailView_css__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! -!../../node_modules/css-loader/dist/cjs.js!./DetailView.css */ "./node_modules/css-loader/dist/cjs.js!./style/SidePanel/DetailView.css");
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_Icons_css__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! -!../../node_modules/css-loader/dist/cjs.js!./Icons.css */ "./node_modules/css-loader/dist/cjs.js!./style/SidePanel/Icons.css");
// Imports





var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_MetadataView_css__WEBPACK_IMPORTED_MODULE_2__["default"]);
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_DetailView_css__WEBPACK_IMPORTED_MODULE_3__["default"]);
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_Icons_css__WEBPACK_IMPORTED_MODULE_4__["default"]);
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.xavier-sidepanel {
  min-width: 400px;
}

.xavier-sidepanel-react {
  background: var(--jp-layout-color1);
  color: var(--jp-ui-font-color1);

  /* This is needed so that all font sizing of children done in ems is
   * relative to this base size */
  font-size: var(--jp-ui-font-size1);

  overflow: hidden;
  min-width: 450px;
  width: 450px;
  padding: 10px;
}

.xavier-sidepanel-fullview {
  display: block;
  width: 100%;
  height: 100%;
}

.xavier-sidepanel-view-title {
  display: block;
  width: 100%;
  height: 20px;
  margin-top: 5px;
  margin-bottom: 5px;
}

/* sti == sidepanel-title-icon */
.xavier-sti-wrapper {
  display: inline-block;
  width: var(--xavier-icon-width);
  height: 100%;
  vertical-align: top;
  margin: 0 5px;
}

/* st == sidepanel-title */
.xavier-st-text {
  display: inline-block;
  width: calc(100% - var(--xavier-icon-width) - 10px - 102px); /* margin of xavier-sti-wrapper and border of xavier-st-btn */
  height: 100%;
  vertical-align: top;
  color: #777;
  font-weight: 700;
  font-size: 15px;
  overflow: hidden;
}

.xavier-st-btn {
  display: inline-block;
  width: 100px;
  height: 100%;
  vertical-align: top;
  line-height: calc(100% + 10px); /* Maybe hard code */
  text-align: center;
  cursor: pointer;
  border-width: 1px;
  border-radius: 1px;
  border-style: solid;
}

.xavier-st-btn:hover {
  color: #1890ff;
}`, "",{"version":3,"sources":["webpack://./style/SidePanel/SidePanel.css"],"names":[],"mappings":"AAIA;EACE,gBAAgB;AAClB;;AAEA;EACE,mCAAmC;EACnC,+BAA+B;;EAE/B;iCAC+B;EAC/B,kCAAkC;;EAElC,gBAAgB;EAChB,gBAAgB;EAChB,YAAY;EACZ,aAAa;AACf;;AAEA;EACE,cAAc;EACd,WAAW;EACX,YAAY;AACd;;AAEA;EACE,cAAc;EACd,WAAW;EACX,YAAY;EACZ,eAAe;EACf,kBAAkB;AACpB;;AAEA,gCAAgC;AAChC;EACE,qBAAqB;EACrB,+BAA+B;EAC/B,YAAY;EACZ,mBAAmB;EACnB,aAAa;AACf;;AAEA,0BAA0B;AAC1B;EACE,qBAAqB;EACrB,2DAA2D,EAAE,6DAA6D;EAC1H,YAAY;EACZ,mBAAmB;EACnB,WAAW;EACX,gBAAgB;EAChB,eAAe;EACf,gBAAgB;AAClB;;AAEA;EACE,qBAAqB;EACrB,YAAY;EACZ,YAAY;EACZ,mBAAmB;EACnB,8BAA8B,EAAE,oBAAoB;EACpD,kBAAkB;EAClB,eAAe;EACf,iBAAiB;EACjB,kBAAkB;EAClB,mBAAmB;AACrB;;AAEA;EACE,cAAc;AAChB","sourcesContent":["@import url('./MetadataView.css');\r\n@import url('./DetailView.css');\r\n@import url('./Icons.css');\r\n\r\n.xavier-sidepanel {\r\n  min-width: 400px;\r\n}\r\n\r\n.xavier-sidepanel-react {\r\n  background: var(--jp-layout-color1);\r\n  color: var(--jp-ui-font-color1);\r\n\r\n  /* This is needed so that all font sizing of children done in ems is\r\n   * relative to this base size */\r\n  font-size: var(--jp-ui-font-size1);\r\n\r\n  overflow: hidden;\r\n  min-width: 450px;\r\n  width: 450px;\r\n  padding: 10px;\r\n}\r\n\r\n.xavier-sidepanel-fullview {\r\n  display: block;\r\n  width: 100%;\r\n  height: 100%;\r\n}\r\n\r\n.xavier-sidepanel-view-title {\r\n  display: block;\r\n  width: 100%;\r\n  height: 20px;\r\n  margin-top: 5px;\r\n  margin-bottom: 5px;\r\n}\r\n\r\n/* sti == sidepanel-title-icon */\r\n.xavier-sti-wrapper {\r\n  display: inline-block;\r\n  width: var(--xavier-icon-width);\r\n  height: 100%;\r\n  vertical-align: top;\r\n  margin: 0 5px;\r\n}\r\n\r\n/* st == sidepanel-title */\r\n.xavier-st-text {\r\n  display: inline-block;\r\n  width: calc(100% - var(--xavier-icon-width) - 10px - 102px); /* margin of xavier-sti-wrapper and border of xavier-st-btn */\r\n  height: 100%;\r\n  vertical-align: top;\r\n  color: #777;\r\n  font-weight: 700;\r\n  font-size: 15px;\r\n  overflow: hidden;\r\n}\r\n\r\n.xavier-st-btn {\r\n  display: inline-block;\r\n  width: 100px;\r\n  height: 100%;\r\n  vertical-align: top;\r\n  line-height: calc(100% + 10px); /* Maybe hard code */\r\n  text-align: center;\r\n  cursor: pointer;\r\n  border-width: 1px;\r\n  border-radius: 1px;\r\n  border-style: solid;\r\n}\r\n\r\n.xavier-st-btn:hover {\r\n  color: #1890ff;\r\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/SpreadSheet.css":
/*!*********************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/SpreadSheet.css ***!
  \*********************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.spreadsheet {
  text-align: left;
}

.xavier-mv-table-wrapper {
  /* min-height: 120px; */
  width: 100%;
}

.xavier-mv-header-cell {
  display: flex; 
  justify-content: center;
  align-items: center;
  height: 100%;
}

.xavier-mv-confirm-btn {
  margin-top: 5px;
  height: 30px;
  width: 100%;
  background-color: #dedede;
  border: none;
  cursor: pointer;
}

.row {
  width: auto;
  display: table-row;
}

.cell-container {
  position: relative;
  padding-left: 5px;
  padding-right: 5px;
  display: table-cell;
  /* height: 100%; */
}

.cell-container-header {
 cursor: pointer; 
}

.cell-container::-webkit-scrollbar {
  display: none; /* Chrome Safari */
}

.xavier-sample-row-btn {
  /* margin-bottom: 10px; */
  position: sticky;
  left: 0;
  height: 30px;
  width: 100%;
  background-color:#f1f1f1;
  border: none;
  cursor: pointer;
}`, "",{"version":3,"sources":["webpack://./style/SpreadSheet.css"],"names":[],"mappings":"AAAA;EACE,gBAAgB;AAClB;;AAEA;EACE,uBAAuB;EACvB,WAAW;AACb;;AAEA;EACE,aAAa;EACb,uBAAuB;EACvB,mBAAmB;EACnB,YAAY;AACd;;AAEA;EACE,eAAe;EACf,YAAY;EACZ,WAAW;EACX,yBAAyB;EACzB,YAAY;EACZ,eAAe;AACjB;;AAEA;EACE,WAAW;EACX,kBAAkB;AACpB;;AAEA;EACE,kBAAkB;EAClB,iBAAiB;EACjB,kBAAkB;EAClB,mBAAmB;EACnB,kBAAkB;AACpB;;AAEA;CACC,eAAe;AAChB;;AAEA;EACE,aAAa,EAAE,kBAAkB;AACnC;;AAEA;EACE,yBAAyB;EACzB,gBAAgB;EAChB,OAAO;EACP,YAAY;EACZ,WAAW;EACX,wBAAwB;EACxB,YAAY;EACZ,eAAe;AACjB","sourcesContent":[".spreadsheet {\r\n  text-align: left;\r\n}\r\n\r\n.xavier-mv-table-wrapper {\r\n  /* min-height: 120px; */\r\n  width: 100%;\r\n}\r\n\r\n.xavier-mv-header-cell {\r\n  display: flex; \r\n  justify-content: center;\r\n  align-items: center;\r\n  height: 100%;\r\n}\r\n\r\n.xavier-mv-confirm-btn {\r\n  margin-top: 5px;\r\n  height: 30px;\r\n  width: 100%;\r\n  background-color: #dedede;\r\n  border: none;\r\n  cursor: pointer;\r\n}\r\n\r\n.row {\r\n  width: auto;\r\n  display: table-row;\r\n}\r\n\r\n.cell-container {\r\n  position: relative;\r\n  padding-left: 5px;\r\n  padding-right: 5px;\r\n  display: table-cell;\r\n  /* height: 100%; */\r\n}\r\n\r\n.cell-container-header {\r\n cursor: pointer; \r\n}\r\n\r\n.cell-container::-webkit-scrollbar {\r\n  display: none; /* Chrome Safari */\r\n}\r\n\r\n.xavier-sample-row-btn {\r\n  /* margin-bottom: 10px; */\r\n  position: sticky;\r\n  left: 0;\r\n  height: 30px;\r\n  width: 100%;\r\n  background-color:#f1f1f1;\r\n  border: none;\r\n  cursor: pointer;\r\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/base.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/base.css ***!
  \**************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_complete_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! -!../node_modules/css-loader/dist/cjs.js!./complete.css */ "./node_modules/css-loader/dist/cjs.js!./style/complete.css");
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_SpreadSheet_css__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! -!../node_modules/css-loader/dist/cjs.js!./SpreadSheet.css */ "./node_modules/css-loader/dist/cjs.js!./style/SpreadSheet.css");
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_Cell_css__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! -!../node_modules/css-loader/dist/cjs.js!./Cell.css */ "./node_modules/css-loader/dist/cjs.js!./style/Cell.css");
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_SidePanel_SidePanel_css__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! -!../node_modules/css-loader/dist/cjs.js!./SidePanel/SidePanel.css */ "./node_modules/css-loader/dist/cjs.js!./style/SidePanel/SidePanel.css");
// Imports






var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_complete_css__WEBPACK_IMPORTED_MODULE_2__["default"]);
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_SpreadSheet_css__WEBPACK_IMPORTED_MODULE_3__["default"]);
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_Cell_css__WEBPACK_IMPORTED_MODULE_4__["default"]);
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_SidePanel_SidePanel_css__WEBPACK_IMPORTED_MODULE_5__["default"]);
// Module
___CSS_LOADER_EXPORT___.push([module.id, `/*
    See the JupyterLab Developer Guide for useful CSS Patterns:

    https://jupyterlab.readthedocs.io/en/stable/developer/css.html
*/

/* 隐藏数字输入框的上下按钮 */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/*定义滚动条高宽及背景 高宽分别对应横竖滚动条的尺寸*/
::-webkit-scrollbar {
    width: var(--xavier-scrollbar-width);
    height: var(--xavier-scrollbar-width);
    background-color: #F9F9F9;
}
   
  /*定义滚动条轨道 内阴影+圆角*/
::-webkit-scrollbar-track {
    -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
    box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    background-color: #fff;
}
   
  /*定义滑块 内阴影+圆角*/
::-webkit-scrollbar-thumb {
    border-radius: 3px;
    -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, .3);
    box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
    background-color: #755d5d;
}

:root {
  --xavier-icon-width: 21px;
  --xavier-df-font-size: 14px;
  --xavier-col-font-size: 13px;
  --xavier-value-font-size: 12px;
  --xavier-cate-item-height: 20px;
  --xavier-scrollbar-width: 5px;
}

.column-type-icon {
    margin-left: 10px;
    margin-right: 5px;
}

.column-histogram-cate {
    background: #f5f5f5; /* Removed the quotes around the color value */
    height: 20px;
    width: 150px;
    margin-right: 10px;
    display: flex; /* Removed the quotes */
    align-items: center; /* Corrected the case and removed quotes */
    position: relative; /* Removed the quotes */
  }

  .column-percentage {
    background: #f5f5f5;
    height: 20px;
    width: 75px;
  }

  .hidden-df-message {
    margin-left: 7.5px;
  }

  .hidden-column-message {
    margin-left: 20px;
  }

  .bold-red {
    font-weight: bold;
    color: red;
  }

  .column-sort {
    width: 12px;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .column {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
}

::-webkit-scrollbar-thumb {
    background-color: #ddd;
}`, "",{"version":3,"sources":["webpack://./style/base.css"],"names":[],"mappings":"AAAA;;;;CAIC;;AAOD,iBAAiB;AACjB;;EAEE,wBAAwB;EACxB,SAAS;AACX;;AAEA,4BAA4B;AAC5B;IACI,oCAAoC;IACpC,qCAAqC;IACrC,yBAAyB;AAC7B;;EAEE,iBAAiB;AACnB;IACI,oDAAoD;IACpD,4CAA4C;IAC5C,mBAAmB;IACnB,sBAAsB;AAC1B;;EAEE,cAAc;AAChB;IACI,kBAAkB;IAClB,mDAAmD;IACnD,4CAA4C;IAC5C,yBAAyB;AAC7B;;AAEA;EACE,yBAAyB;EACzB,2BAA2B;EAC3B,4BAA4B;EAC5B,8BAA8B;EAC9B,+BAA+B;EAC/B,6BAA6B;AAC/B;;AAEA;IACI,iBAAiB;IACjB,iBAAiB;AACrB;;AAEA;IACI,mBAAmB,EAAE,8CAA8C;IACnE,YAAY;IACZ,YAAY;IACZ,kBAAkB;IAClB,aAAa,EAAE,uBAAuB;IACtC,mBAAmB,EAAE,0CAA0C;IAC/D,kBAAkB,EAAE,uBAAuB;EAC7C;;EAEA;IACE,mBAAmB;IACnB,YAAY;IACZ,WAAW;EACb;;EAEA;IACE,kBAAkB;EACpB;;EAEA;IACE,iBAAiB;EACnB;;EAEA;IACE,iBAAiB;IACjB,UAAU;EACZ;;EAEA;IACE,WAAW;IACX,YAAY;IACZ,aAAa;IACb,mBAAmB;IACnB,uBAAuB;EACzB;;EAEA;IACE,aAAa;IACb,mBAAmB;IACnB,uBAAuB;AAC3B;;AAEA;IACI,sBAAsB;AAC1B","sourcesContent":["/*\r\n    See the JupyterLab Developer Guide for useful CSS Patterns:\r\n\r\n    https://jupyterlab.readthedocs.io/en/stable/developer/css.html\r\n*/\r\n\r\n@import url('./complete.css');\r\n@import url('./SpreadSheet.css');\r\n@import url('./Cell.css');\r\n@import url('./SidePanel/SidePanel.css');\r\n\r\n/* 隐藏数字输入框的上下按钮 */\r\ninput[type=\"number\"]::-webkit-inner-spin-button,\r\ninput[type=\"number\"]::-webkit-outer-spin-button {\r\n  -webkit-appearance: none;\r\n  margin: 0;\r\n}\r\n\r\n/*定义滚动条高宽及背景 高宽分别对应横竖滚动条的尺寸*/\r\n::-webkit-scrollbar {\r\n    width: var(--xavier-scrollbar-width);\r\n    height: var(--xavier-scrollbar-width);\r\n    background-color: #F9F9F9;\r\n}\r\n   \r\n  /*定义滚动条轨道 内阴影+圆角*/\r\n::-webkit-scrollbar-track {\r\n    -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);\r\n    box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);\r\n    border-radius: 10px;\r\n    background-color: #fff;\r\n}\r\n   \r\n  /*定义滑块 内阴影+圆角*/\r\n::-webkit-scrollbar-thumb {\r\n    border-radius: 3px;\r\n    -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, .3);\r\n    box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);\r\n    background-color: #755d5d;\r\n}\r\n\r\n:root {\r\n  --xavier-icon-width: 21px;\r\n  --xavier-df-font-size: 14px;\r\n  --xavier-col-font-size: 13px;\r\n  --xavier-value-font-size: 12px;\r\n  --xavier-cate-item-height: 20px;\r\n  --xavier-scrollbar-width: 5px;\r\n}\r\n\r\n.column-type-icon {\r\n    margin-left: 10px;\r\n    margin-right: 5px;\r\n}\r\n\r\n.column-histogram-cate {\r\n    background: #f5f5f5; /* Removed the quotes around the color value */\r\n    height: 20px;\r\n    width: 150px;\r\n    margin-right: 10px;\r\n    display: flex; /* Removed the quotes */\r\n    align-items: center; /* Corrected the case and removed quotes */\r\n    position: relative; /* Removed the quotes */\r\n  }\r\n\r\n  .column-percentage {\r\n    background: #f5f5f5;\r\n    height: 20px;\r\n    width: 75px;\r\n  }\r\n\r\n  .hidden-df-message {\r\n    margin-left: 7.5px;\r\n  }\r\n\r\n  .hidden-column-message {\r\n    margin-left: 20px;\r\n  }\r\n\r\n  .bold-red {\r\n    font-weight: bold;\r\n    color: red;\r\n  }\r\n\r\n  .column-sort {\r\n    width: 12px;\r\n    height: 100%;\r\n    display: flex;\r\n    align-items: center;\r\n    justify-content: center;\r\n  }\r\n\r\n  .column {\r\n    display: flex;\r\n    flex-direction: row;\r\n    align-items: flex-start;\r\n}\r\n\r\n::-webkit-scrollbar-thumb {\r\n    background-color: #ddd;\r\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/complete.css":
/*!******************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/complete.css ***!
  \******************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.jp-Completer-item.jp-mod-active {
  background-color: #e9e9ff;
  color: #000000de;
  font-weight: bold;
}

/* .jp-Completer-docpanel {
  width: 530px !important;
  max-height: calc((15 * var(--jp-private-completer-item-height)) - 16px) !important;
  padding: 2px;
  overflow: hidden;
} */

/* .lm-Widget.jp-Completer.jp-HoverBox {
  width: 800px !important;
  height: calc((15 * var(--jp-private-completer-item-height))) !important;
  max-height: calc((15 * var(--jp-private-completer-item-height))) !important;
} */

.lm-Widget.jp-Completer.jp-HoverBox .jp-Completer-list {
  /* width: 270px !important; */
  max-height: calc((15 * var(--jp-private-completer-item-height)));
}

.jp-Completer-item .jp-Completer-match {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jp-Completer-type.jp-Completer-monogram {
  color: rgb(128, 128, 128);
  font-weight: bold;
}

.jp-Completer-type[data-color-index='1'] {
  /* background: #ddf1ff; */
  background: #ebebeb;
}

.jp-Completer-type[data-color-index='2'] {
  /* background: #ffe9d6; */
  background: #ebebeb;
}

.jp-Completer-type[data-color-index='3'] {
  /* background: #e1ffe1; */
  background: #ebebeb;
}

.jp-Completer-type[data-color-index='4'] {
  /* background: #ffdfdf; */
  background: #ebebeb;
}

.jp-Completer-type[data-color-index='5'] {
  /* background: #ebddfa; */
  background: #ebebeb;
}

.jp-Completer-type[data-color-index='6'] {
  /* background: #ffe6e1; */
  background: #ebebeb;
}

.jp-Completer-type[data-color-index='7'] {
  /* background: #ffe0f5; */
  background: #ebebeb;
}

.jp-Completer-type[data-color-index='8'] {
  /* background: #e0e0e0; */
  background: #ebebeb;
}

.jp-Completer-type[data-color-index='9'] {
  /* background: #ffffd8; */
  background: #ebebeb;
}

.jp-Completer-type[data-color-index='10'] {
  /* background: #b2f7ff; */
  background: #ebebeb;
}`, "",{"version":3,"sources":["webpack://./style/complete.css"],"names":[],"mappings":"AAAA;EACE,yBAAyB;EACzB,gBAAgB;EAChB,iBAAiB;AACnB;;AAEA;;;;;GAKG;;AAEH;;;;GAIG;;AAEH;EACE,6BAA6B;EAC7B,gEAAgE;AAClE;;AAEA;EACE,gBAAgB;EAChB,uBAAuB;EACvB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,iBAAiB;AACnB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB;;AAEA;EACE,yBAAyB;EACzB,mBAAmB;AACrB","sourcesContent":[".jp-Completer-item.jp-mod-active {\r\n  background-color: #e9e9ff;\r\n  color: #000000de;\r\n  font-weight: bold;\r\n}\r\n\r\n/* .jp-Completer-docpanel {\r\n  width: 530px !important;\r\n  max-height: calc((15 * var(--jp-private-completer-item-height)) - 16px) !important;\r\n  padding: 2px;\r\n  overflow: hidden;\r\n} */\r\n\r\n/* .lm-Widget.jp-Completer.jp-HoverBox {\r\n  width: 800px !important;\r\n  height: calc((15 * var(--jp-private-completer-item-height))) !important;\r\n  max-height: calc((15 * var(--jp-private-completer-item-height))) !important;\r\n} */\r\n\r\n.lm-Widget.jp-Completer.jp-HoverBox .jp-Completer-list {\r\n  /* width: 270px !important; */\r\n  max-height: calc((15 * var(--jp-private-completer-item-height)));\r\n}\r\n\r\n.jp-Completer-item .jp-Completer-match {\r\n  overflow: hidden;\r\n  text-overflow: ellipsis;\r\n  white-space: nowrap;\r\n}\r\n\r\n.jp-Completer-type.jp-Completer-monogram {\r\n  color: rgb(128, 128, 128);\r\n  font-weight: bold;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='1'] {\r\n  /* background: #ddf1ff; */\r\n  background: #ebebeb;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='2'] {\r\n  /* background: #ffe9d6; */\r\n  background: #ebebeb;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='3'] {\r\n  /* background: #e1ffe1; */\r\n  background: #ebebeb;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='4'] {\r\n  /* background: #ffdfdf; */\r\n  background: #ebebeb;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='5'] {\r\n  /* background: #ebddfa; */\r\n  background: #ebebeb;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='6'] {\r\n  /* background: #ffe6e1; */\r\n  background: #ebebeb;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='7'] {\r\n  /* background: #ffe0f5; */\r\n  background: #ebebeb;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='8'] {\r\n  /* background: #e0e0e0; */\r\n  background: #ebebeb;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='9'] {\r\n  /* background: #ffffd8; */\r\n  background: #ebebeb;\r\n}\r\n\r\n.jp-Completer-type[data-color-index='10'] {\r\n  /* background: #b2f7ff; */\r\n  background: #ebebeb;\r\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/runtime/api.js":
/*!*****************************************************!*\
  !*** ./node_modules/css-loader/dist/runtime/api.js ***!
  \*****************************************************/
/***/ ((module) => {



/*
  MIT License http://www.opensource.org/licenses/mit-license.php
  Author Tobias Koppers @sokra
*/
module.exports = function (cssWithMappingToString) {
  var list = [];

  // return the list of modules as css string
  list.toString = function toString() {
    return this.map(function (item) {
      var content = "";
      var needLayer = typeof item[5] !== "undefined";
      if (item[4]) {
        content += "@supports (".concat(item[4], ") {");
      }
      if (item[2]) {
        content += "@media ".concat(item[2], " {");
      }
      if (needLayer) {
        content += "@layer".concat(item[5].length > 0 ? " ".concat(item[5]) : "", " {");
      }
      content += cssWithMappingToString(item);
      if (needLayer) {
        content += "}";
      }
      if (item[2]) {
        content += "}";
      }
      if (item[4]) {
        content += "}";
      }
      return content;
    }).join("");
  };

  // import a list of modules into the list
  list.i = function i(modules, media, dedupe, supports, layer) {
    if (typeof modules === "string") {
      modules = [[null, modules, undefined]];
    }
    var alreadyImportedModules = {};
    if (dedupe) {
      for (var k = 0; k < this.length; k++) {
        var id = this[k][0];
        if (id != null) {
          alreadyImportedModules[id] = true;
        }
      }
    }
    for (var _k = 0; _k < modules.length; _k++) {
      var item = [].concat(modules[_k]);
      if (dedupe && alreadyImportedModules[item[0]]) {
        continue;
      }
      if (typeof layer !== "undefined") {
        if (typeof item[5] === "undefined") {
          item[5] = layer;
        } else {
          item[1] = "@layer".concat(item[5].length > 0 ? " ".concat(item[5]) : "", " {").concat(item[1], "}");
          item[5] = layer;
        }
      }
      if (media) {
        if (!item[2]) {
          item[2] = media;
        } else {
          item[1] = "@media ".concat(item[2], " {").concat(item[1], "}");
          item[2] = media;
        }
      }
      if (supports) {
        if (!item[4]) {
          item[4] = "".concat(supports);
        } else {
          item[1] = "@supports (".concat(item[4], ") {").concat(item[1], "}");
          item[4] = supports;
        }
      }
      list.push(item);
    }
  };
  return list;
};

/***/ }),

/***/ "./node_modules/css-loader/dist/runtime/sourceMaps.js":
/*!************************************************************!*\
  !*** ./node_modules/css-loader/dist/runtime/sourceMaps.js ***!
  \************************************************************/
/***/ ((module) => {



module.exports = function (item) {
  var content = item[1];
  var cssMapping = item[3];
  if (!cssMapping) {
    return content;
  }
  if (typeof btoa === "function") {
    var base64 = btoa(unescape(encodeURIComponent(JSON.stringify(cssMapping))));
    var data = "sourceMappingURL=data:application/json;charset=utf-8;base64,".concat(base64);
    var sourceMapping = "/*# ".concat(data, " */");
    return [content].concat([sourceMapping]).join("\n");
  }
  return [content].join("\n");
};

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js":
/*!****************************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js ***!
  \****************************************************************************/
/***/ ((module) => {



var stylesInDOM = [];
function getIndexByIdentifier(identifier) {
  var result = -1;
  for (var i = 0; i < stylesInDOM.length; i++) {
    if (stylesInDOM[i].identifier === identifier) {
      result = i;
      break;
    }
  }
  return result;
}
function modulesToDom(list, options) {
  var idCountMap = {};
  var identifiers = [];
  for (var i = 0; i < list.length; i++) {
    var item = list[i];
    var id = options.base ? item[0] + options.base : item[0];
    var count = idCountMap[id] || 0;
    var identifier = "".concat(id, " ").concat(count);
    idCountMap[id] = count + 1;
    var indexByIdentifier = getIndexByIdentifier(identifier);
    var obj = {
      css: item[1],
      media: item[2],
      sourceMap: item[3],
      supports: item[4],
      layer: item[5]
    };
    if (indexByIdentifier !== -1) {
      stylesInDOM[indexByIdentifier].references++;
      stylesInDOM[indexByIdentifier].updater(obj);
    } else {
      var updater = addElementStyle(obj, options);
      options.byIndex = i;
      stylesInDOM.splice(i, 0, {
        identifier: identifier,
        updater: updater,
        references: 1
      });
    }
    identifiers.push(identifier);
  }
  return identifiers;
}
function addElementStyle(obj, options) {
  var api = options.domAPI(options);
  api.update(obj);
  var updater = function updater(newObj) {
    if (newObj) {
      if (newObj.css === obj.css && newObj.media === obj.media && newObj.sourceMap === obj.sourceMap && newObj.supports === obj.supports && newObj.layer === obj.layer) {
        return;
      }
      api.update(obj = newObj);
    } else {
      api.remove();
    }
  };
  return updater;
}
module.exports = function (list, options) {
  options = options || {};
  list = list || [];
  var lastIdentifiers = modulesToDom(list, options);
  return function update(newList) {
    newList = newList || [];
    for (var i = 0; i < lastIdentifiers.length; i++) {
      var identifier = lastIdentifiers[i];
      var index = getIndexByIdentifier(identifier);
      stylesInDOM[index].references--;
    }
    var newLastIdentifiers = modulesToDom(newList, options);
    for (var _i = 0; _i < lastIdentifiers.length; _i++) {
      var _identifier = lastIdentifiers[_i];
      var _index = getIndexByIdentifier(_identifier);
      if (stylesInDOM[_index].references === 0) {
        stylesInDOM[_index].updater();
        stylesInDOM.splice(_index, 1);
      }
    }
    lastIdentifiers = newLastIdentifiers;
  };
};

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/insertBySelector.js":
/*!********************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/insertBySelector.js ***!
  \********************************************************************/
/***/ ((module) => {



var memo = {};

/* istanbul ignore next  */
function getTarget(target) {
  if (typeof memo[target] === "undefined") {
    var styleTarget = document.querySelector(target);

    // Special case to return head of iframe instead of iframe itself
    if (window.HTMLIFrameElement && styleTarget instanceof window.HTMLIFrameElement) {
      try {
        // This will throw an exception if access to iframe is blocked
        // due to cross-origin restrictions
        styleTarget = styleTarget.contentDocument.head;
      } catch (e) {
        // istanbul ignore next
        styleTarget = null;
      }
    }
    memo[target] = styleTarget;
  }
  return memo[target];
}

/* istanbul ignore next  */
function insertBySelector(insert, style) {
  var target = getTarget(insert);
  if (!target) {
    throw new Error("Couldn't find a style target. This probably means that the value for the 'insert' parameter is invalid.");
  }
  target.appendChild(style);
}
module.exports = insertBySelector;

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/insertStyleElement.js":
/*!**********************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/insertStyleElement.js ***!
  \**********************************************************************/
/***/ ((module) => {



/* istanbul ignore next  */
function insertStyleElement(options) {
  var element = document.createElement("style");
  options.setAttributes(element, options.attributes);
  options.insert(element, options.options);
  return element;
}
module.exports = insertStyleElement;

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js":
/*!**********************************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js ***!
  \**********************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {



/* istanbul ignore next  */
function setAttributesWithoutAttributes(styleElement) {
  var nonce =  true ? __webpack_require__.nc : 0;
  if (nonce) {
    styleElement.setAttribute("nonce", nonce);
  }
}
module.exports = setAttributesWithoutAttributes;

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/styleDomAPI.js":
/*!***************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/styleDomAPI.js ***!
  \***************************************************************/
/***/ ((module) => {



/* istanbul ignore next  */
function apply(styleElement, options, obj) {
  var css = "";
  if (obj.supports) {
    css += "@supports (".concat(obj.supports, ") {");
  }
  if (obj.media) {
    css += "@media ".concat(obj.media, " {");
  }
  var needLayer = typeof obj.layer !== "undefined";
  if (needLayer) {
    css += "@layer".concat(obj.layer.length > 0 ? " ".concat(obj.layer) : "", " {");
  }
  css += obj.css;
  if (needLayer) {
    css += "}";
  }
  if (obj.media) {
    css += "}";
  }
  if (obj.supports) {
    css += "}";
  }
  var sourceMap = obj.sourceMap;
  if (sourceMap && typeof btoa !== "undefined") {
    css += "\n/*# sourceMappingURL=data:application/json;base64,".concat(btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap)))), " */");
  }

  // For old IE
  /* istanbul ignore if  */
  options.styleTagTransform(css, styleElement, options.options);
}
function removeStyleElement(styleElement) {
  // istanbul ignore if
  if (styleElement.parentNode === null) {
    return false;
  }
  styleElement.parentNode.removeChild(styleElement);
}

/* istanbul ignore next  */
function domAPI(options) {
  if (typeof document === "undefined") {
    return {
      update: function update() {},
      remove: function remove() {}
    };
  }
  var styleElement = options.insertStyleElement(options);
  return {
    update: function update(obj) {
      apply(styleElement, options, obj);
    },
    remove: function remove() {
      removeStyleElement(styleElement);
    }
  };
}
module.exports = domAPI;

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/styleTagTransform.js":
/*!*********************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/styleTagTransform.js ***!
  \*********************************************************************/
/***/ ((module) => {



/* istanbul ignore next  */
function styleTagTransform(css, styleElement) {
  if (styleElement.styleSheet) {
    styleElement.styleSheet.cssText = css;
  } else {
    while (styleElement.firstChild) {
      styleElement.removeChild(styleElement.firstChild);
    }
    styleElement.appendChild(document.createTextNode(css));
  }
}
module.exports = styleTagTransform;

/***/ }),

/***/ "./style/base.css":
/*!************************!*\
  !*** ./style/base.css ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleDomAPI.js */ "./node_modules/style-loader/dist/runtime/styleDomAPI.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertBySelector.js */ "./node_modules/style-loader/dist/runtime/insertBySelector.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js */ "./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertStyleElement.js */ "./node_modules/style-loader/dist/runtime/insertStyleElement.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleTagTransform.js */ "./node_modules/style-loader/dist/runtime/styleTagTransform.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./base.css */ "./node_modules/css-loader/dist/cjs.js!./style/base.css");

      
      
      
      
      
      
      
      
      

var options = {};

options.styleTagTransform = (_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default());
options.setAttributes = (_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default());

      options.insert = _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default().bind(null, "head");
    
options.domAPI = (_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default());
options.insertStyleElement = (_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default());

var update = _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__["default"], options);




       /* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__["default"] && _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals ? _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals : undefined);


/***/ })

}]);
//# sourceMappingURL=style_base_css.3b27ad6fb7e8bd2c597f.js.map