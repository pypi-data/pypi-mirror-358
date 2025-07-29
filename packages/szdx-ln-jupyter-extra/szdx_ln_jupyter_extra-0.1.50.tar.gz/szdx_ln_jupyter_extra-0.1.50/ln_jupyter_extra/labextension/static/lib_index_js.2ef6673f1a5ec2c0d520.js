"use strict";
(self["webpackChunkln_jupyter_extra"] = self["webpackChunkln_jupyter_extra"] || []).push([["lib_index_js"],{

/***/ "./lib/api/project.js":
/*!****************************!*\
  !*** ./lib/api/project.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   addProjectVersion: () => (/* binding */ addProjectVersion),
/* harmony export */   getFileList: () => (/* binding */ getFileList),
/* harmony export */   getFileProxyToken: () => (/* binding */ getFileProxyToken),
/* harmony export */   getProjectDetail: () => (/* binding */ getProjectDetail),
/* harmony export */   getProjectVersionList: () => (/* binding */ getProjectVersionList),
/* harmony export */   getTaskDetail: () => (/* binding */ getTaskDetail),
/* harmony export */   loadProjectVersion: () => (/* binding */ loadProjectVersion),
/* harmony export */   submitStudentWork: () => (/* binding */ submitStudentWork)
/* harmony export */ });
/* harmony import */ var _request_index__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../request/index */ "./lib/request/index.js");

const _baseUrlCommon = '/gateway/foundation/api/v1';
const _baseUrlTraining = '/gateway/training/api/v1';
const _baseUrl = '/gateway/foundation/api/v1';
const _baseUrlToken = '/gateway/foundation/api/v1';
const _baseUrlFile = '/gateway/file-proxy/api/v1';
const getProjectVersionList = async (data) => {
    return await _request_index__WEBPACK_IMPORTED_MODULE_0__["default"].post(_baseUrl + '/teaching/action/notebookVersionPage', {
        data
    });
};
/** 获取项目详情*/
const getProjectDetail = async (id) => {
    return await _request_index__WEBPACK_IMPORTED_MODULE_0__["default"].get(_baseUrlCommon + '/teaching/notebook/project/' + id);
};
// 查询文件列表
const getFileList = async (data, authToken, clusterId = 'local') => {
    const headers = {
        Authorization: `Bearer ${authToken}`
    };
    const region = clusterId;
    return await _request_index__WEBPACK_IMPORTED_MODULE_0__.customRequest.get(_baseUrlFile + '/list', {
        params: { ...data, region },
        headers
    });
};
// 获取文件代理服务token（查询共享对象（模型或数据集）的文件token）
const getFileProxyToken = async (data) => {
    return await _request_index__WEBPACK_IMPORTED_MODULE_0__["default"].post(_baseUrlToken + '/shares/action/file/token', {
        data
    });
};
/** 新增版本 公开内容*/
const addProjectVersion = async (data) => {
    return await _request_index__WEBPACK_IMPORTED_MODULE_0__["default"].post(_baseUrlCommon + '/teaching/action/publishVersion', {
        data
    });
};
/** 新增版本 发布作业*/
const submitStudentWork = async (data) => {
    return await _request_index__WEBPACK_IMPORTED_MODULE_0__["default"].post(_baseUrlCommon + '/teaching/action/submitStudentWork', {
        data
    });
};
/** 获取任务详情 */
const getTaskDetail = async (id) => {
    return await _request_index__WEBPACK_IMPORTED_MODULE_0__["default"].get(_baseUrlTraining + '/job/teaching/notebook/' + id);
};
/** 加载选定版本到默认版本 */
const loadProjectVersion = async (data) => {
    return await _request_index__WEBPACK_IMPORTED_MODULE_0__["default"].post(_baseUrlCommon + '/teaching/version/action/load', {
        data
    });
};


/***/ }),

/***/ "./lib/components/DatasetListPanel.js":
/*!********************************************!*\
  !*** ./lib/components/DatasetListPanel.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var lucide_react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! lucide-react */ "webpack/sharing/consume/default/lucide-react/lucide-react");
/* harmony import */ var lucide_react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(lucide_react__WEBPACK_IMPORTED_MODULE_1__);


const DatasetListPanel = ({ title, files, onFileClick = fileName => console.log(`Clicked file: ${fileName}`) }) => {
    const [isExpanded, setIsExpanded] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(true);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "ln-dataset-list-panel" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "panel-header", onClick: () => setIsExpanded(prev => !prev) },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "panel-title" }, title),
            isExpanded ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(lucide_react__WEBPACK_IMPORTED_MODULE_1__.ChevronDown, { size: 18, className: "icon" })) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(lucide_react__WEBPACK_IMPORTED_MODULE_1__.ChevronRight, { size: 18, className: "icon" }))),
        isExpanded && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("ul", { className: "file-list" }, files.length > 0 ? (files.map((file, index) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("li", { key: `${file.fileName}-${index}`, className: "file-item", onClick: () => onFileClick(file.fileName) }, file.fileName)))) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("li", { className: "no-files" }, "\u6682\u65E0\u6587\u4EF6"))))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (DatasetListPanel);


/***/ }),

/***/ "./lib/components/VersionList.js":
/*!***************************************!*\
  !*** ./lib/components/VersionList.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   VersionList: () => (/* binding */ VersionList)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var dayjs__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! dayjs */ "webpack/sharing/consume/default/dayjs/dayjs");
/* harmony import */ var dayjs__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(dayjs__WEBPACK_IMPORTED_MODULE_1__);

// import { Notification } from '@jupyterlab/apputils';

const VersionList = ({ id, version, createTime, app, projectId }) => {
    // const handleVersionClick = async (id: string) => {
    //   try {
    //     await loadProjectVersion({
    //       versionId: id,
    //       projectId: projectId || ''
    //     });
    //     // 重置工作区域
    //     await refreshFn(app);
    //   } catch (e) {
    //     Notification.error('加载失败', { autoClose: 3000 });
    //     console.log(e);
    //   }
    // };
    // const refreshFn = async (app: JupyterFrontEnd) => {
    //   // 使用传入的 app 实例
    //   for (const widget of app.shell.widgets('main')) {
    //     widget.close();
    //   }
    //   await app.commands.execute('workspace-ui:reset');
    //   Notification.success('版本加载成功', { autoClose: 3000 });
    // };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "ln-version-list-item" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "ln-version-list-item__name" }, version),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "ln-version-list-item__time" }, dayjs__WEBPACK_IMPORTED_MODULE_1___default()(createTime).format('YYYY-MM-DD HH:mm:ss')))));
};


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _widgets_createVersion__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./widgets/createVersion */ "./lib/widgets/createVersion.js");
/* harmony import */ var _widgets_version__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./widgets/version */ "./lib/widgets/version.js");
/* harmony import */ var _widgets_dataset__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./widgets/dataset */ "./lib/widgets/dataset.js");
/* harmony import */ var _widgets_time__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./widgets/time */ "./lib/widgets/time.js");
/* harmony import */ var _widgets_title__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./widgets/title */ "./lib/widgets/title.js");
/* harmony import */ var _api_project__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./api/project */ "./lib/api/project.js");
/* harmony import */ var _widgets_variable_index__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./widgets/variable/index */ "./lib/widgets/variable/index.js");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__);












/**
 * 更新自动保存时间间隔
 * @param settingRegistry - JupyterLab 的设置注册实例
 * @param interval - 自动保存时间间隔（以毫秒为单位，例如 30000 表示 30 秒）
 */
async function updateAutosaveInterval(settingRegistry, interval) {
    const settingId = '@jupyterlab/docmanager-extension:plugin'; // 设置插件的 ID
    try {
        // 加载当前的设置
        const settings = await settingRegistry.load(settingId);
        // 更新 autosaveInterval 配置
        await settings.set('autosaveInterval', interval);
    }
    catch (error) {
        console.error('Failed to update autosave interval:', error);
    }
}
/**
 * Activate the ln-notebook extension.
 *
 * @param app - The JupyterLab Application instance
 * @param palette - The command palette instance
 * @param restorer - The application layout restorer
 * @param statusBar - The status bar instance
 *
 * @returns A promise that resolves when the extension has been activated
 */
async function activate(app, palette, restorer, statusBar, router, settingRegistry) {
    var _a;
    console.log('Activating szdx-ln-jupyter-extra extension...');
    updateAutosaveInterval(settingRegistry, 30);
    await new Promise(resolve => setTimeout(resolve, 100));
    if (router) {
        // 尝试获取路由信息的备选方案
        const currentUrl = window.location.href;
        const pathSegments = currentUrl.split('/');
        const taskId = pathSegments[4];
        const taskData = await (0,_api_project__WEBPACK_IMPORTED_MODULE_4__.getTaskDetail)(taskId);
        const notebookProjectId = taskData.notebookProjectId;
        const inputVolumeItem = taskData.jobStorageList.find((item) => item.businessType === 0);
        const inputVolume = (inputVolumeItem === null || inputVolumeItem === void 0 ? void 0 : inputVolumeItem.volumeTo) || '';
        if (inputVolume) {
            app.serviceManager.contents
                .get(inputVolume)
                .then(result => {
                if (result.content[0].path) {
                    app.commands.execute('filebrowser:open-path', {
                        path: result.content[0].path
                    });
                }
                console.log(result.content[0].path);
            })
                .catch(error => {
                console.error('路径不存在或无法访问:', error);
            });
        }
        if (!notebookProjectId) {
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Notification.error('项目ID未获取到', { autoClose: 3000 });
        }
        else {
            try {
                console.log('Initial route:', notebookProjectId || 'Route not ready');
                const projectData = await (0,_api_project__WEBPACK_IMPORTED_MODULE_4__.getProjectDetail)(notebookProjectId || '');
                const teachingId = projectData.originId;
                const roleType = projectData.roleType;
                const originVersionId = ((_a = projectData.projectVersionList[0]) === null || _a === void 0 ? void 0 : _a.id) || '';
                const timeWidget = new _widgets_time__WEBPACK_IMPORTED_MODULE_5__["default"](taskId);
                timeWidget.install(app);
                const sidebarVersion = new _widgets_version__WEBPACK_IMPORTED_MODULE_6__["default"](app, notebookProjectId);
                sidebarVersion.install(app);
                const sidebarDataSet = new _widgets_dataset__WEBPACK_IMPORTED_MODULE_7__["default"]({ projectData });
                sidebarDataSet.install(app);
                const titleWidget = new _widgets_title__WEBPACK_IMPORTED_MODULE_8__["default"]({ projectData });
                titleWidget.install(app);
                const createVersionBtn = new _widgets_createVersion__WEBPACK_IMPORTED_MODULE_9__["default"](app, notebookProjectId, teachingId, roleType, originVersionId);
                createVersionBtn.install(app);
                console.log('szdx-ln-jupyter-extra extension activated successfully!');
            }
            catch (error) {
                console.error('Error during activation:', error);
                _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Notification.error('插件激活失败');
            }
        }
    }
}
const lnPlugin = {
    id: 'ln-notebook:plugin',
    description: 'leinao extra jupyter plugin',
    autoStart: true,
    requires: [
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer,
        _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_2__.IStatusBar,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.IRouter,
        _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__.ISettingRegistry
    ],
    activate: activate
};
const plugins = [lnPlugin, ..._widgets_variable_index__WEBPACK_IMPORTED_MODULE_10__["default"]];
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugins);


/***/ }),

/***/ "./lib/request/baseConfig.js":
/*!***********************************!*\
  !*** ./lib/request/baseConfig.js ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   baseConfig: () => (/* binding */ baseConfig)
/* harmony export */ });
// 1. 从当前页面的 URL 中获取查询参数
const urlParams = new URLSearchParams(window.location.search);
// 2. 获取 'type' 参数的值
let domain = urlParams.get('type');
const authToken = urlParams.get('auth');
// 3. 修正不规范的 URL (http:/... -> http://...)
if (domain && domain.startsWith('http:/') && !domain.startsWith('http://')) {
    domain = domain.replace('http:/', 'http://');
}
console.log('baseConfig domain:', domain);
console.log('baseConfig authToken:', authToken);
const baseConfig = {
    baseURL: domain !== null && domain !== void 0 ? domain : window.location.origin,
    timeout: 60000,
    headers: {
        Authorization: authToken ? `Bearer ${authToken}` : '' // 授权头
    }
};


/***/ }),

/***/ "./lib/request/index.js":
/*!******************************!*\
  !*** ./lib/request/index.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Request: () => (/* binding */ Request),
/* harmony export */   customErrorRequest: () => (/* binding */ customErrorRequest),
/* harmony export */   customNotAuthRequest: () => (/* binding */ customNotAuthRequest),
/* harmony export */   customRequest: () => (/* binding */ customRequest),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   noAllRequest: () => (/* binding */ noAllRequest),
/* harmony export */   noAuthFormatRequest: () => (/* binding */ noAuthFormatRequest),
/* harmony export */   notAuthRequest: () => (/* binding */ notAuthRequest),
/* harmony export */   otherRequest: () => (/* binding */ otherRequest)
/* harmony export */ });
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! axios */ "webpack/sharing/consume/default/axios/axios");
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _baseConfig__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./baseConfig */ "./lib/request/baseConfig.js");
/* harmony import */ var _interceptor__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./interceptor */ "./lib/request/interceptor.js");



/**
 * axios 封装
 * 20230217
 */
class Request {
    /**
     *
     * @param config 默认配置
     * @param flag 是否是第三方接口 默认为第三方接口 true
     */
    constructor(config, apiHookConfig) {
        const { flag = true, auth = true, skipErrorResponseInterceptor = false } = apiHookConfig;
        this.flag = flag;
        this.auth = auth;
        this.skipErrorResponseInterceptor = skipErrorResponseInterceptor;
        this.instance = axios__WEBPACK_IMPORTED_MODULE_0___default().create(config);
        this.initRequestInterceptor(this.instance);
        this.initResponseInterceptor(this.instance);
    }
    // 请求拦截器
    initRequestInterceptor(instance) {
        instance.interceptors.request.use((config) => {
            // 一般会请求拦截里面加token，用于后端的验证
            return (0,_interceptor__WEBPACK_IMPORTED_MODULE_1__.handlerRequest)(config, {
                flag: this.flag,
                auth: this.auth
            });
        }, async (err) => await Promise.reject(err));
    }
    // response拦截器
    initResponseInterceptor(instance) {
        instance.interceptors.response.use((res) => {
            // 系统如果有自定义code也可以在这里处理
            if (!this.flag) {
                return (0,_interceptor__WEBPACK_IMPORTED_MODULE_1__.handleResponse)(res);
            }
            return res;
        }, async (err) => {
            // 根据skipErrorResponseInterceptor决定是否跳过错误处理
            if (this.skipErrorResponseInterceptor) {
                return Promise.reject(err);
            }
            else {
                return await (0,_interceptor__WEBPACK_IMPORTED_MODULE_1__.handleResponseErr)(err, this.flag); // 状态码返回内容
            }
        });
    }
    // 请求方法
    async request(config) {
        return await this.instance
            .request(config)
            .then((res) => (this.flag ? res : res.data));
    }
    async get(url, config) {
        return await this.request({ method: 'get', url, ...config });
    }
    async post(url, config) {
        return await this.request({ method: 'post', url, ...config });
    }
    async put(url, config) {
        return await this.request({ method: 'put', url, ...config });
    }
    async delete(url, config) {
        return await this.request({ method: 'delete', url, ...config });
    }
}
// 默认导出Request实例
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (new Request(_baseConfig__WEBPACK_IMPORTED_MODULE_2__.baseConfig, { flag: false }));
// 自定义处理接口200时报错信息Request实例
const customRequest = new Request(_baseConfig__WEBPACK_IMPORTED_MODULE_2__.baseConfig, { flag: true });
// 自定义处理接口非200时报错信息Request实例
const customErrorRequest = new Request(_baseConfig__WEBPACK_IMPORTED_MODULE_2__.baseConfig, {
    flag: false,
    skipErrorResponseInterceptor: true
});
// 不需要token但是需要拦截器
const notAuthRequest = new Request(_baseConfig__WEBPACK_IMPORTED_MODULE_2__.baseConfig, {
    flag: false,
    auth: false
});
// 不需要token不用在意返回格式但是需要拦截器
const noAuthFormatRequest = new Request(_baseConfig__WEBPACK_IMPORTED_MODULE_2__.baseConfig, {
    flag: true,
    auth: false
});
// 不需要token不用在意返回格式不需要返回拦截器
const noAllRequest = new Request(_baseConfig__WEBPACK_IMPORTED_MODULE_2__.baseConfig, {
    flag: true,
    auth: false,
    skipErrorResponseInterceptor: true
});
// 第三方接口导出Request实例; 也可以直接引入Request类，然后传入不同的config
const otherRequest = new Request({}, {});
// 不需要token但是需要拦截器
const customNotAuthRequest = new Request(_baseConfig__WEBPACK_IMPORTED_MODULE_2__.baseConfig, {
    flag: true,
    auth: false
});


/***/ }),

/***/ "./lib/request/interceptor.js":
/*!************************************!*\
  !*** ./lib/request/interceptor.js ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   handleResponse: () => (/* binding */ handleResponse),
/* harmony export */   handleResponseErr: () => (/* binding */ handleResponseErr),
/* harmony export */   handlerRequest: () => (/* binding */ handlerRequest)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../utils */ "./lib/utils/storage.js");
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../utils */ "./lib/utils/message/error.js");
// 拦截器操作


// message中的错误码
// const MessageCodeDic = [
//   -3, 10133, 10117, 10119, 10121, 10122, 10124, 10134, 10157, 10307, 10315,
//   61000
// ];
// message中的错误码
const MessageCodeDic = [1027];
// 处理请求头，一般比如在header加token
const handlerRequest = (config, apiHookConfig) => {
    if (!apiHookConfig.auth) {
        return config;
    }
    const USREINFO = JSON.parse((0,_utils__WEBPACK_IMPORTED_MODULE_1__.getStorage)('USREINFO') || '{}') || {};
    // eslint-disable-next-line @typescript-eslint/strict-boolean-expressions
    if (USREINFO.token) {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        config.headers.token = USREINFO.token;
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        config.headers['X-Agent-Token'] =
            'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwidG9rZW5fdHlwZSI6ImFjY2Vzc190b2tlbiIsImlhdCI6MTY3MzIzMTUzNiwiaXNzIjoia3ViZXNwaGVyZSIsIm5iZiI6MTY3MzIzMTUzNn0.7O9n5M-qzJPgl2gILJ8hXNuwDPlrxdrl8CEDMLCfTyQ';
    }
    return config;
};
// 根据情况处理返回数据
const handleResponse = (res) => {
    // 如果后端返回的是code为0，则直接返回.data.data；如果不为0，则把massage也返回出去
    // todo 在某些情况下instance可能会有用处
    const { data } = res;
    const { code, message } = data.message;
    // 正常状态返回
    if (code === 0) {
        return data;
    }
    // 异常状态返回 根据不同的code判断接下来的操作
    switch (true) {
        // 未登录
        case MessageCodeDic.includes(code):
            console.log('未登录');
            break;
        case code === 401:
            // 未授权
            // noAuthError(JSON.parse(getStorage('USREINFO') || '{}') || {});
            if (message) {
                void _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.error(message, { autoClose: 3000 });
            }
            break;
        case code !== 0:
            if (message) {
                void _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.error(message, { autoClose: 3000 });
            }
    }
    return Promise.reject(res);
};
const handleResponseErr = async (error, flag = false) => {
    const { response, request } = error;
    if (response !== null) {
        // 当响应状态码为非2xx时，可以在这里进行错误处理
        // console.log(response.status);
        // console.log(response.data);
        // console.log(response.headers);
        // 判断http状态码非2xx时 是否存在业务代码的code
        //                     存在code 匹配全局message 匹配不上 判断是否有message
        //                                                          有：提示message
        //                                                          否：根据http状态码提示
        const { data: { message } } = response;
        if (!flag) {
            const { code = undefined, message = undefined } = (response === null || response === void 0 ? void 0 : response.data)
                ? response.data.message || {}
                : {};
            // 登录过期 需要重新登录
            if (MessageCodeDic.includes(code)) {
                console.log('登录过期');
            }
            else if ((response === null || response === void 0 ? void 0 : response.status) === 401 && code === 401) {
                // 未授权
                if (message) {
                    void _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.error(message, { autoClose: 3000 });
                }
                // noAuthError(JSON.parse(getStorage('USREINFO') || '{}') || {});
            }
            else if (code !== 0) {
                // 现在的逻辑是 返回的数据code不是0 http状态码可能也不是0 所以需要在这里进行拦截
                if (message) {
                    void _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.error(message, { autoClose: 3000 });
                }
            }
            else {
                void _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.error((0,_utils__WEBPACK_IMPORTED_MODULE_2__.MessageCodeError)(message, (0,_utils__WEBPACK_IMPORTED_MODULE_2__.MessageCodeError)({ code: response === null || response === void 0 ? void 0 : response.status })));
            }
        }
        if (message === null || message === void 0 ? void 0 : message.code) {
            // 异常状态返回 根据不同的code判断接下来的操作
            switch (true) {
                // 未登录
                case MessageCodeDic.includes(message === null || message === void 0 ? void 0 : message.code):
                    console.log('未登录');
                    break;
            }
        }
        // if (data) {
        //   return (await Promise.reject(data)) as any;
        // }
    }
    else if (error.code === 'ECONNABORTED' &&
        error.message.includes('timeout')) {
        // 超时处理
        void _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.warning('请求超时，请检查网络连接并重新尝试！');
    }
    else if (request !== null) {
        // 当没有响应时，可以在这里进行错误处理：个人建议无需处理
        void _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.error((0,_utils__WEBPACK_IMPORTED_MODULE_2__.MessageCodeError)({}));
    }
    else {
        // 其他错误，可以在这里进行错误处理
        void _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.error((0,_utils__WEBPACK_IMPORTED_MODULE_2__.MessageCodeError)({}));
        console.log('Error', error.message);
    }
    // 超时判断
    return await Promise.reject(error);
};


/***/ }),

/***/ "./lib/utils/message/error.js":
/*!************************************!*\
  !*** ./lib/utils/message/error.js ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   MessageCodeError: () => (/* binding */ MessageCodeError),
/* harmony export */   codeDic: () => (/* binding */ codeDic)
/* harmony export */ });
// 错误码对应字典值 code => message
// 注：涉及具体业务的code不要放到这里 例如：code为1001 在A业务中提示的是参数不能为空
//                                               在B业务中提示的是删除失败...
const codeDic = {
    1001: '参数不能为空',
    1002: '参数不能为null',
    1003: '参数类型错误',
    1004: '空指针错误',
    1005: '参数验证失败',
    1020: '不支持表情符号',
    1021: '用户名错误',
    1022: '帐号错误',
    1023: '密码错误',
    1024: '用户名或密码错误',
    1025: '帐号或密码错误',
    1026: '验证码错误',
    1200: '资源操作错误',
    1201: '资源添加错误',
    1202: '资源删除错误',
    1203: '资源更新错误',
    1204: '资源查询错误',
    1205: '资源查询数据为空',
    1206: '不允许重复资源',
    1300: '文件操作错误',
    1301: '文件未找到',
    1302: '文件访问被拒绝',
    1303: '文件读取失败',
    1304: '文件写入失败',
    1305: '文件创建失败',
    1306: '文件删除失败',
    1307: '文件复制错误',
    1308: '文件移动失败',
    1309: '文件目录未找到',
    1310: '文件目录拒绝访问',
    1311: '文件目录读取失败',
    1312: '文件目录写入失败',
    1400: '请求第三方组件失败',
    1401: '请求第三方组件超时',
    1402: '第三方组件响应错误',
    1403: '请求内部组件错误',
    1404: '请求内部组件超时',
    1405: '内部组件响应错误',
    400: '请求失败',
    401: '未经授权',
    403: '被禁止的',
    404: '请求不存在',
    405: '不允许此请求方法',
    500: '内部服务器错误',
    502: '网关错误',
    503: '服务不可用',
    504: '网关超时'
};
/**
 *
 * @param data 服务端返回数据结构 {code: 0, message: 'message'}
 * @returns error message
 * @description 判断code是否为number 是：优先匹配code 在字典中对应的提示文字 其次提示data.message 最后提示defaultMsg
 *                                  否：提示defaultMsg
 */
const MessageCodeError = (data, defaultMsg = '系统异常，请联系管理员！') => {
    var _a;
    return typeof data.code === 'number'
        ? (_a = (codeDic[data.code] || data.message)) !== null && _a !== void 0 ? _a : defaultMsg
        : defaultMsg;
    // return (codeDic[data.code] || data.message) ?? defaultMsg
};


/***/ }),

/***/ "./lib/utils/storage.js":
/*!******************************!*\
  !*** ./lib/utils/storage.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   clearStorage: () => (/* binding */ clearStorage),
/* harmony export */   getStorage: () => (/* binding */ getStorage),
/* harmony export */   removeStorage: () => (/* binding */ removeStorage),
/* harmony export */   setStorage: () => (/* binding */ setStorage)
/* harmony export */ });
// Web storage API
// localStorage用的较多，所以在创建和获取的时候默认为storage，如果是用sessionStorage请传另一个参数flag为false
const getStorage = (key, flag = true) => {
    return flag ? localStorage.getItem(key) : sessionStorage.getItem(key);
};
const setStorage = (key, value, flag = true) => {
    flag ? localStorage.setItem(key, value) : sessionStorage.setItem(key, value);
};
const removeStorage = (key, flag = true) => {
    flag ? localStorage.removeItem(key) : sessionStorage.removeItem(key);
};
const clearStorage = (flag = true) => {
    flag ? localStorage.clear() : sessionStorage.clear();
};


/***/ }),

/***/ "./lib/widgets/createVersion.js":
/*!**************************************!*\
  !*** ./lib/widgets/createVersion.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react_dom_client__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-dom/client */ "./node_modules/react-dom/client.js");
/* harmony import */ var _api_project__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../api/project */ "./lib/api/project.js");





// 版本创建表单组件
const VersionCreationForm = ({ onClose, onSubmit, roleType }) => {
    // const [formData, setFormData] = useState({
    //   name: '',
    //   description: ''
    // });
    // const [errors, setErrors] = useState({
    //   name: '',
    //   description: ''
    // });
    // // 校验版本名称
    // const validateName = (name: string) => {
    //   const nameRegex = /^[a-zA-Z0-9.]+$/;
    //   if (!name) {
    //     return '版本名称不能为空';
    //   }
    //   if (name.length > 10) {
    //     return '版本名称长度不能超过10个字符';
    //   }
    //   if (!nameRegex.test(name)) {
    //     return '版本名称只能包含英文、数字和.';
    //   }
    //   return '';
    // };
    // // 校验描述
    // const validateDescription = (description: string) => {
    //   if (description.length > 300) {
    //     return '版本描述不能超过300个字符';
    //   }
    //   return '';
    // };
    // 处理输入变化
    // const handleChange = (
    //   e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    // ) => {
    //   const { name, value } = e.target;
    //   setFormData(prev => ({
    //     ...prev,
    //     [name]: value
    //   }));
    // };
    // 提交表单
    const handleSubmit = async () => {
        // const nameError = validateName(formData.name);
        // const descriptionError = validateDescription(formData.description);
        // // 设置错误信息
        // setErrors({
        //   name: nameError,
        //   description: descriptionError
        // });
        // // 如果有错误，阻止提交
        // if (nameError || descriptionError) {
        //   return;
        // }
        try {
            // 调用提交接口
            await onSubmit();
            // 成功后关闭弹框
            onClose();
        }
        catch (error) {
            console.error('提交失败', error);
        }
    };
    return (react__WEBPACK_IMPORTED_MODULE_2___default().createElement("div", { style: {
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000
        } },
        react__WEBPACK_IMPORTED_MODULE_2___default().createElement("div", { style: {
                backgroundColor: 'white',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                width: '300px'
            } },
            react__WEBPACK_IMPORTED_MODULE_2___default().createElement("h2", { style: { marginTop: 0, marginBottom: '20px', textAlign: 'center' } },
                "\u662F\u5426",
                roleType === 1 ? '公开' : '提交作业',
                "?"),
            react__WEBPACK_IMPORTED_MODULE_2___default().createElement("div", { style: { marginBottom: '15px' } }),
            react__WEBPACK_IMPORTED_MODULE_2___default().createElement("div", null),
            react__WEBPACK_IMPORTED_MODULE_2___default().createElement("div", { style: {
                    display: 'flex',
                    justifyContent: 'center',
                    marginTop: '20px'
                } },
                react__WEBPACK_IMPORTED_MODULE_2___default().createElement("button", { onClick: onClose, style: {
                        padding: '8px 16px',
                        marginRight: '28px',
                        backgroundColor: '#f0f0f0',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    } }, "\u53D6\u6D88"),
                react__WEBPACK_IMPORTED_MODULE_2___default().createElement("button", { onClick: handleSubmit, style: {
                        padding: '8px 16px',
                        backgroundColor: '#4194fc',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    } }, "\u786E\u5B9A")))));
};
class SaveButton extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.CommandToolbarButton {
    constructor(app, notebookProjectId, teachingId, roleType, originVersionId) {
        const COMMAND_ID = 'version:create';
        app.commands.addCommand(COMMAND_ID, {
            label: roleType === 1 ? '公开' : '提交作业',
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.saveIcon,
            execute: () => {
                this.handleSave(app, notebookProjectId, teachingId, roleType, originVersionId);
            }
        });
        super({
            commands: app.commands,
            id: COMMAND_ID
        });
        this.dialogContainer = null;
        this.dialogRoot = null;
        this.id = 'version-list-save-button';
        this._app = app;
        this.notebookProjectId = notebookProjectId;
        this.teachingId = teachingId;
        this.roleType = roleType;
        this.originVersionId = originVersionId;
        this.node.classList.add('custom-save-button');
    }
    install(app) {
        app.shell.add(this, 'top', {
            rank: 1000
        });
    }
    handleSave(app, notebookProjectId, teachingId, roleType, originVersionId) {
        // 创建对话框容器
        this.dialogContainer = document.createElement('div');
        document.body.appendChild(this.dialogContainer);
        // 创建 React 根
        this.dialogRoot = (0,react_dom_client__WEBPACK_IMPORTED_MODULE_3__.createRoot)(this.dialogContainer);
        const closeDialog = () => {
            if (this.dialogRoot && this.dialogContainer) {
                this.dialogRoot.unmount();
                document.body.removeChild(this.dialogContainer);
                this.dialogContainer = null;
                this.dialogRoot = null;
            }
        };
        const submitVersion = async () => {
            const api = roleType === 1 ? _api_project__WEBPACK_IMPORTED_MODULE_4__.addProjectVersion : _api_project__WEBPACK_IMPORTED_MODULE_4__.submitStudentWork;
            const params = this.roleType === 1
                ? {
                    originVersionId,
                    originTeachingId: teachingId || '',
                    version: ''
                }
                : {
                    notebookId: notebookProjectId || '',
                    teachingId,
                    originVersionId,
                    workVersion: ''
                };
            try {
                await api(params);
                this.refreshData(this._app);
            }
            catch (error) {
                console.error('版本创建失败:', error);
            }
        };
        // 渲染对话框
        this.dialogRoot.render(react__WEBPACK_IMPORTED_MODULE_2___default().createElement(VersionCreationForm, { onClose: closeDialog, onSubmit: submitVersion, roleType: this.roleType }));
    }
    refreshData(app) {
        const widgets = Array.from(app.shell.widgets('left'));
        console.log(widgets);
        const versionListWidget = widgets.find(widget => widget.id === 'ln-version-list-sidebar');
        if (versionListWidget) {
            // 直接调用 getVersions 方法刷新列表
            versionListWidget.getVersions(this.notebookProjectId);
        }
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SaveButton);


/***/ }),

/***/ "./lib/widgets/dataset.js":
/*!********************************!*\
  !*** ./lib/widgets/dataset.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _api_project__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../api/project */ "./lib/api/project.js");
/* harmony import */ var _components_DatasetListPanel__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../components/DatasetListPanel */ "./lib/components/DatasetListPanel.js");
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-dom */ "webpack/sharing/consume/default/react-dom");
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_dom__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_3__);






class DataSetListSidebarWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor(options) {
        super();
        this.addClass('ln-dataset-list-sidebar'); // 使用 ln- 前缀
        this.id = 'ln-dataset-list-dataset';
        this.title.caption = '数据集';
        this.title.label = '数据集';
        this.title.icon = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.tableRowsIcon;
        this.title.closable = true; // 允许关闭
        this.projectData = options.projectData || {};
        this.datasetList = options.projectData.storageList || [];
        this.listContainer = document.createElement('div');
        this.listContainer.className = 'ln-dataset-list';
        this.node.appendChild(this.listContainer);
        this.params = {
            searchKey: '',
            pageSize: 15,
            pageNum: 1,
            tagLabels: [],
            sortType: 'deployTime'
        };
        // 调用获取版本的函数
        this.getVersions();
    }
    async getToken(id) {
        try {
            this.token = await (0,_api_project__WEBPACK_IMPORTED_MODULE_4__.getFileProxyToken)({
                expires: 3600,
                businessId: id,
                businessType: 1
            });
        }
        catch (error) {
            console.error('Error in getToken:', error);
            throw error;
        }
    }
    async queryFileList(dataset, token) {
        var _a;
        const queryParams = {
            bucketName: dataset.bucketCrName,
            storageType: 'filesystem',
            dir: dataset.bucketPath.slice(1) + '/',
            pageNumber: 1,
            pageSize: 2147483647
        };
        try {
            if (!token) {
                throw new Error('No valid auth token');
            }
            const res = await (0,_api_project__WEBPACK_IMPORTED_MODULE_4__.getFileList)(queryParams, token, dataset.clusterId);
            if ((_a = res.data) === null || _a === void 0 ? void 0 : _a.data.fileList) {
                dataset.fileList = res.data.data.fileList;
            }
            else {
                console.warn('File list is empty or undefined');
                dataset.fileList = [];
            }
        }
        catch (error) {
            console.error('Error in getFileListData:', error);
            throw error;
        }
    }
    async getVersions() {
        try {
            await Promise.all(this.datasetList.map(async (item) => {
                await this.getToken(item.businessId);
                await this.queryFileList(item, this.token);
            }));
            this.updateDatasetList(this.datasetList);
        }
        catch (error) {
            console.error('请求数据时出错:', error);
            throw error; // 重新抛出错误
        }
    }
    updateDatasetList(data) {
        if (data.length > 0) {
            react_dom__WEBPACK_IMPORTED_MODULE_2___default().render(react__WEBPACK_IMPORTED_MODULE_3___default().createElement("div", null, data.map((dataset, index) => (react__WEBPACK_IMPORTED_MODULE_3___default().createElement(_components_DatasetListPanel__WEBPACK_IMPORTED_MODULE_5__["default"], { key: `${dataset.name}-${index}`, title: dataset.name, files: dataset.fileList || [], onFileClick: fileName => {
                    console.log(`Clicked file: ${fileName}`);
                } })))), this.listContainer);
        }
        else {
            react_dom__WEBPACK_IMPORTED_MODULE_2___default().render(react__WEBPACK_IMPORTED_MODULE_3___default().createElement("div", { style: { textAlign: 'center', marginTop: '30px' } }, "\u6682\u65E0\u6570\u636E"), this.listContainer);
        }
    }
    install(app) {
        app.shell.add(this, 'left', {
            rank: 900,
            type: 'tab'
        });
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (DataSetListSidebarWidget);


/***/ }),

/***/ "./lib/widgets/time.js":
/*!*****************************!*\
  !*** ./lib/widgets/time.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _api_project__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../api/project */ "./lib/api/project.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);



function computedDurTime(time) {
    if (time) {
        if (time <= 1) {
            return '1s';
        }
        const elapsedTime = Math.round(time / 1000);
        let result = '';
        const elapsedDay = parseInt((elapsedTime / (24 * 60 * 60)));
        if (elapsedDay > 0) {
            result += elapsedDay + 'd ';
        }
        const elapsedHour = parseInt(((elapsedTime % (24 * 60 * 60)) / (60 * 60)));
        if (result !== '' || (result === '' && elapsedHour > 0)) {
            result += elapsedHour + 'h ';
        }
        const elapsedMinute = parseInt(((elapsedTime % (60 * 60)) / 60));
        if (result !== '' || (result === '' && elapsedMinute > 0)) {
            result += elapsedMinute + 'm ';
        }
        const elapsedSecond = parseInt((elapsedTime % 60));
        result += elapsedSecond + 's';
        return result;
    }
    else {
        return '--';
    }
}
class UsageTimeWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor(taskId) {
        super();
        this.taskId = taskId;
        this.id = 'usage-time-widget';
        this.title.label = '使用时间';
        this.title.closable = true;
        this.addClass('usage-time-widget');
        this.startTime = 0; // 记录启动时间
        this.updateUsageTime();
        setInterval(() => this.updateUsageTime(), 60000); // 每秒更新
    }
    async updateUsageTime() {
        const taskId = this.taskId || '';
        if (taskId) {
            const taskData = await (0,_api_project__WEBPACK_IMPORTED_MODULE_2__.getTaskDetail)(taskId);
            const { completedTime, startedTime, state } = taskData;
            const usedTime = completedTime
                ? computedDurTime(completedTime - startedTime)
                : state === 'Running'
                    ? computedDurTime(new Date().getTime() - startedTime)
                    : undefined;
            this.node.innerText = `已使用时间: ${usedTime} `;
        }
        else {
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Notification.error('任务ID未获取到', { autoClose: 3000 });
        }
    }
    install(app) {
        app.shell.add(this, 'top', {
            rank: 998
        });
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (UsageTimeWidget);


/***/ }),

/***/ "./lib/widgets/title.js":
/*!******************************!*\
  !*** ./lib/widgets/title.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);

class TitleWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor(options) {
        super();
        this.nodeTitle = document.createElement('div');
        this.nodeTitle.textContent = options.projectData.name || '';
        this.nodeTitle.style.cssText = 'margin-left:350px;margin-top:5px';
        this.widget = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget({ node: this.nodeTitle });
        this.widget.id = 'jupyter-title';
    }
    install(app) {
        app.shell.add(this.widget, 'top', { rank: 501 });
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (TitleWidget);


/***/ }),

/***/ "./lib/widgets/variable/handler.js":
/*!*****************************************!*\
  !*** ./lib/widgets/variable/handler.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   DummyHandler: () => (/* binding */ DummyHandler),
/* harmony export */   VariableInspectionHandler: () => (/* binding */ VariableInspectionHandler)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_datagrid__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/datagrid */ "webpack/sharing/consume/default/@lumino/datagrid");
/* harmony import */ var _lumino_datagrid__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_datagrid__WEBPACK_IMPORTED_MODULE_1__);


class AbstractHandler {
    constructor(connector) {
        this._isDisposed = false;
        this._disposed = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._inspected = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._rendermime = null;
        this._connector = connector;
        this._enabled = false;
    }
    get enabled() {
        return this._enabled;
    }
    set enabled(value) {
        this._enabled = value;
    }
    get disposed() {
        return this._disposed;
    }
    get isDisposed() {
        return this._isDisposed;
    }
    get inspected() {
        return this._inspected;
    }
    get rendermime() {
        return this._rendermime;
    }
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this._isDisposed = true;
        this._disposed.emit();
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal.clearData(this);
    }
    performDelete(varName) {
        //noop
    }
}
/**
 * An object that handles code inspection.
 */
class VariableInspectionHandler extends AbstractHandler {
    constructor(options) {
        var _a;
        super(options.connector);
        /*
         * Handle query response. Emit new signal containing the IVariableInspector.IInspectorUpdate object.
         * (TODO: query resp. could be forwarded to panel directly)
         */
        this._handleQueryResponse = (response) => {
            const msgType = response.header.msg_type;
            switch (msgType) {
                case 'execute_result': {
                    const payload = response.content;
                    let content = payload.data['text/plain'];
                    if (content.slice(0, 1) === "'" || content.slice(0, 1) === '"') {
                        content = content.slice(1, -1);
                        content = content.replace(/\\"/g, '"').replace(/\\'/g, "'");
                    }
                    const update = JSON.parse(content);
                    const title = {
                        contextName: '',
                        kernelName: this._connector.kernelName || ''
                    };
                    this._inspected.emit({ title: title, payload: update });
                    break;
                }
                case 'display_data': {
                    const payloadDisplay = response.content;
                    let contentDisplay = payloadDisplay.data['text/plain'];
                    if (contentDisplay.slice(0, 1) === "'" ||
                        contentDisplay.slice(0, 1) === '"') {
                        contentDisplay = contentDisplay.slice(1, -1);
                        contentDisplay = contentDisplay
                            .replace(/\\"/g, '"')
                            .replace(/\\'/g, "'");
                    }
                    const updateDisplay = JSON.parse(contentDisplay);
                    const titleDisplay = {
                        contextName: '',
                        kernelName: this._connector.kernelName || ''
                    };
                    this._inspected.emit({ title: titleDisplay, payload: updateDisplay });
                    break;
                }
                default:
                    break;
            }
        };
        /*
         * Invokes a inspection if the signal emitted from specified session is an 'execute_input' msg.
         */
        this._queryCall = (sess, msg) => {
            const msgType = msg.header.msg_type;
            switch (msgType) {
                case 'execute_input': {
                    const code = msg.content.code;
                    if (!(code === this._queryCommand) &&
                        !(code === this._matrixQueryCommand) &&
                        !code.startsWith(this._widgetQueryCommand)) {
                        this.performInspection();
                    }
                    break;
                }
                default:
                    break;
            }
        };
        this._id = options.id;
        this._rendermime = (_a = options.rendermime) !== null && _a !== void 0 ? _a : null;
        this._queryCommand = options.queryCommand;
        this._matrixQueryCommand = options.matrixQueryCommand;
        this._widgetQueryCommand = options.widgetQueryCommand;
        this._changeSettingsCommand = options.changeSettingsCommand;
        this._deleteCommand = options.deleteCommand;
        this._initScript = options.initScript;
        this._setting = options.setting;
        this._ready = this._connector.ready.then(() => {
            this._initOnKernel().then((msg) => {
                this.performSettingsChange();
                this._connector.iopubMessage.connect(this._queryCall);
                return;
            });
        });
        const onKernelReset = (sender, kernelReady) => {
            const title = {
                contextName: '<b>Waiting for kernel...</b> '
            };
            this._inspected.emit({
                title: title,
                payload: []
            });
            this._ready = kernelReady.then(() => {
                this._initOnKernel().then((msg) => {
                    this.performSettingsChange();
                    this._connector.iopubMessage.connect(this._queryCall);
                    this.performInspection();
                });
            });
        };
        this._setting.changed.connect(async () => {
            await this._ready;
            this.performSettingsChange();
            this.performInspection();
        });
        this._connector.kernelRestarted.connect(onKernelReset);
        this._connector.kernelChanged.connect(onKernelReset);
    }
    get id() {
        return this._id;
    }
    get ready() {
        return this._ready;
    }
    /**
     * Performs an inspection by sending an execute request with the query command to the kernel.
     */
    performInspection() {
        if (!this.enabled) {
            return;
        }
        const content = {
            code: this._queryCommand,
            stop_on_error: false,
            store_history: false
        };
        this._connector.fetch(content, this._handleQueryResponse);
    }
    /**
     * Performs an inspection of a Jupyter Widget
     */
    performWidgetInspection(varName) {
        const request = {
            code: this._widgetQueryCommand + '(' + varName + ')',
            stop_on_error: false,
            store_history: false
        };
        return this._connector.execute(request);
    }
    /**
     * Performs an inspection of the specified matrix.
     */
    performMatrixInspection(varName, maxRows = 100000) {
        const request = {
            code: this._matrixQueryCommand + '(' + varName + ', ' + maxRows + ')',
            stop_on_error: false,
            store_history: false
        };
        const con = this._connector;
        return new Promise((resolve, reject) => {
            con.fetch(request, (response) => {
                const msgType = response.header.msg_type;
                switch (msgType) {
                    case 'execute_result': {
                        const payload = response.content;
                        let content = payload.data['text/plain'];
                        content = content.replace(/^'|'$/g, '');
                        content = content.replace(/\\"/g, '"');
                        content = content.replace(/\\'/g, "\\\\'");
                        const modelOptions = JSON.parse(content);
                        const jsonModel = new _lumino_datagrid__WEBPACK_IMPORTED_MODULE_1__.JSONModel(modelOptions);
                        resolve(jsonModel);
                        break;
                    }
                    case 'error':
                        console.log(response);
                        reject("Kernel error on 'matrixQuery' call!");
                        break;
                    default:
                        break;
                }
            });
        });
    }
    /**
     * Send a kernel request to delete a variable from the global environment
     */
    performDelete(varName) {
        const content = {
            code: this._deleteCommand + "('" + varName + "')",
            stop_on_error: false,
            store_history: false
        };
        this._connector.fetch(content, this._handleQueryResponse);
    }
    /**
     * Send a kernel request to change settings
     */
    performSettingsChange() {
        if (!this._changeSettingsCommand) {
            return;
        }
        const settings = {
            maxItems: this._setting.get('maxItems').composite
        };
        const content = {
            code: this._changeSettingsCommand(settings),
            stop_on_error: false,
            store_history: false
        };
        this._connector.fetch(content, this._handleQueryResponse);
    }
    /**
     * Initializes the kernel by running the set up script located at _initScriptPath.
     */
    _initOnKernel() {
        const content = {
            code: this._initScript,
            stop_on_error: false,
            silent: true
        };
        return this._connector.fetch(content, () => {
            //no op
        });
    }
}
class DummyHandler extends AbstractHandler {
    constructor(connector) {
        super(connector);
    }
    performInspection() {
        const title = {
            contextName: '. <b>Language currently not supported.</b> ',
            kernelName: this._connector.kernelName || ''
        };
        this._inspected.emit({
            title: title,
            payload: []
        });
    }
    performMatrixInspection(varName, maxRows) {
        return new Promise((resolve, reject) => {
            reject('Cannot inspect matrices w/ the DummyHandler!');
        });
    }
    performWidgetInspection(varName) {
        const request = {
            code: '',
            stop_on_error: false,
            store_history: false
        };
        return this._connector.execute(request);
    }
}


/***/ }),

/***/ "./lib/widgets/variable/index.js":
/*!***************************************!*\
  !*** ./lib/widgets/variable/index.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   consoles: () => (/* binding */ consoles),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   notebooks: () => (/* binding */ notebooks),
/* harmony export */   variableinspector: () => (/* binding */ variableinspector)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_console__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/console */ "webpack/sharing/consume/default/@jupyterlab/console");
/* harmony import */ var _jupyterlab_console__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_console__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./handler */ "./lib/widgets/variable/handler.js");
/* harmony import */ var _inspectorscripts__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./inspectorscripts */ "./lib/widgets/variable/inspectorscripts.js");
/* harmony import */ var _kernelconnector__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./kernelconnector */ "./lib/widgets/variable/kernelconnector.js");
/* harmony import */ var _manager__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./manager */ "./lib/widgets/variable/manager.js");
/* harmony import */ var _variableinspector__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./variableinspector */ "./lib/widgets/variable/variableinspector.js");
/* harmony import */ var _tokens__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./tokens */ "./lib/widgets/variable/tokens.js");
/* harmony import */ var _jupyter_web_components__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyter/web-components */ "webpack/sharing/consume/default/@jupyter/web-components/@jupyter/web-components");
/* harmony import */ var _jupyter_web_components__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyter_web_components__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_8__);















(0,_jupyter_web_components__WEBPACK_IMPORTED_MODULE_6__.addJupyterLabThemeChangeListener)();
var CommandIDs;
(function (CommandIDs) {
    CommandIDs.toggleVariableMonitor = 'variableMonitor:toggle';
})(CommandIDs || (CommandIDs = {}));
const SETTINGS_ID = 'ln-jupyter-extra:plugin';
/**
 * A service providing variable introspection.
 */
const variableinspector = {
    id: '@ln/jupyterlab-variablemonitor',
    requires: [
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__.ILayoutRestorer,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__.ILabShell,
        _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__.ISettingRegistry,
        _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_7__.IStatusBar
    ],
    provides: _tokens__WEBPACK_IMPORTED_MODULE_9__.IVariableInspectorManager,
    autoStart: true,
    activate: (app, palette, restorer, labShell, settings, statusBar) => {
        const manager = new _manager__WEBPACK_IMPORTED_MODULE_10__.VariableInspectorManager();
        const category = '变量监控';
        const command = CommandIDs.toggleVariableMonitor;
        const label = '切换变量监控面板';
        const namespace = 'variablemonitor';
        const tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.WidgetTracker({ namespace });
        /**
         * Create and track a new inspector.
         */
        function newPanel() {
            const panel = new _variableinspector__WEBPACK_IMPORTED_MODULE_11__.VariableInspectorPanel();
            panel.id = 'ln-variablemonitor';
            panel.title.label = '变量监控';
            panel.title.icon = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_5__.inspectorIcon;
            panel.title.closable = true;
            panel.node.style.cssText = `
      height: 250px !important;
      overflow-y: auto ;
      width: 100%;
    `;
            labShell.add(panel, 'down');
            panel.disposed.connect(() => {
                if (manager.panel === panel) {
                    manager.panel = null;
                }
            });
            //Track the inspector panel
            tracker.add(panel);
            return panel;
        }
        // Enable state restoration
        restorer.restore(tracker, {
            command,
            args: () => ({}),
            name: () => 'variablemonitor'
        });
        // Add command to palette
        app.commands.addCommand(command, {
            label,
            execute: () => {
                if (!manager.panel || manager.panel.isDisposed) {
                    manager.panel = newPanel();
                }
                // 确保面板在底部区域
                if (!manager.panel.isAttached) {
                    labShell.add(manager.panel, 'down');
                }
                if (manager.source) {
                    manager.source.performInspection();
                }
                // 激活底部区域的变量检查器
                labShell.activateById(manager.panel.id);
            }
        });
        palette.addItem({ command, category });
        const statusBarItem = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_8__.Widget();
        statusBarItem.addClass('jp-mod-highlighted');
        // Create the button content
        const logButton = document.createElement('div');
        logButton.innerHTML = `
        <span class="jp-StatusBar-TextItem">
          变量监控
        </span>
      `;
        statusBarItem.node.appendChild(logButton);
        statusBarItem.node.onclick = () => {
            app.commands.execute(CommandIDs.toggleVariableMonitor);
        };
        statusBar.registerStatusItem('variable-inspector', {
            item: statusBarItem,
            align: 'left',
            rank: 1001
        });
        console.log('JupyterLab extension @ln/jupyterlab_variablemonitor is activated!');
        return manager;
    }
};
/**
 * An extension that registers consoles for variable inspection.
 */
const consoles = {
    id: '@ln/jupyterlab-variablemonitor:consoles',
    requires: [
        _tokens__WEBPACK_IMPORTED_MODULE_9__.IVariableInspectorManager,
        _jupyterlab_console__WEBPACK_IMPORTED_MODULE_2__.IConsoleTracker,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__.ILabShell,
        _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__.ISettingRegistry
    ],
    autoStart: true,
    activate: async (app, manager, consoles, labShell, settings) => {
        const handlers = {};
        const setting = await settings.load(SETTINGS_ID);
        /**
         * Subscribes to the creation of new consoles. If a new notebook is created, build a new handler for the consoles.
         * Adds a promise for a instanced handler to the 'handlers' collection.
         */
        consoles.widgetAdded.connect((sender, consolePanel) => {
            if (manager.hasHandler(consolePanel.sessionContext.path)) {
                handlers[consolePanel.id] = new Promise((resolve, reject) => {
                    resolve(manager.getHandler(consolePanel.sessionContext.path));
                });
            }
            else {
                handlers[consolePanel.id] = new Promise((resolve, reject) => {
                    const session = consolePanel.sessionContext;
                    // Create connector and init w script if it exists for kernel type.
                    const connector = new _kernelconnector__WEBPACK_IMPORTED_MODULE_12__.KernelConnector({ session });
                    const scripts = connector.ready.then(() => {
                        return connector.kernelLanguage.then(lang => {
                            return _inspectorscripts__WEBPACK_IMPORTED_MODULE_13__.Languages.getScript(lang);
                        });
                    });
                    scripts.then((result) => {
                        const initScript = result.initScript;
                        const queryCommand = result.queryCommand;
                        const matrixQueryCommand = result.matrixQueryCommand;
                        const widgetQueryCommand = result.widgetQueryCommand;
                        const deleteCommand = result.deleteCommand;
                        const changeSettingsCommand = result.changeSettingsCommand;
                        const options = {
                            queryCommand,
                            matrixQueryCommand,
                            widgetQueryCommand,
                            deleteCommand,
                            connector,
                            initScript,
                            changeSettingsCommand,
                            id: session.path,
                            setting
                        };
                        const handler = new _handler__WEBPACK_IMPORTED_MODULE_14__.VariableInspectionHandler(options);
                        manager.addHandler(handler);
                        consolePanel.disposed.connect(() => {
                            delete handlers[consolePanel.id];
                            handler.dispose();
                        });
                        handler.ready.then(() => {
                            resolve(handler);
                        });
                    });
                    //Otherwise log error message.
                    scripts.catch((result) => {
                        console.log(result);
                        const handler = new _handler__WEBPACK_IMPORTED_MODULE_14__.DummyHandler(connector);
                        consolePanel.disposed.connect(() => {
                            delete handlers[consolePanel.id];
                            handler.dispose();
                        });
                        resolve(handler);
                    });
                });
            }
            setSource(labShell);
        });
        const setSource = (sender, args) => {
            var _a;
            const widget = (_a = args === null || args === void 0 ? void 0 : args.newValue) !== null && _a !== void 0 ? _a : sender.currentWidget;
            if (!widget || !consoles.has(widget)) {
                return;
            }
            const future = handlers[widget.id];
            future.then((source) => {
                if (source) {
                    manager.source = source;
                    manager.source.performInspection();
                }
            });
        };
        /**
         * If focus window changes, checks whether new focus widget is a console.
         * In that case, retrieves the handler associated to the console after it has been
         * initialized and updates the manager with it.
         */
        setSource(labShell);
        labShell.currentChanged.connect(setSource);
        // app.contextMenu.addItem({
        //   command: CommandIDs.toggleVariableMonitor,
        //   selector: '.jp-CodeConsole'
        // });
    }
};
/**
 * An extension that registers notebooks for variable inspection.
 */
const notebooks = {
    id: '@ln/jupyterlab-variablemonitor:notebooks',
    requires: [
        _tokens__WEBPACK_IMPORTED_MODULE_9__.IVariableInspectorManager,
        _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.INotebookTracker,
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_1__.ILabShell,
        _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__.ISettingRegistry
    ],
    autoStart: true,
    activate: async (app, manager, notebooks, labShell, settings) => {
        const handlers = {};
        const setting = await settings.load(SETTINGS_ID);
        /**
         * Subscribes to the creation of new notebooks. If a new notebook is created, build a new handler for the notebook.
         * Adds a promise for a instanced handler to the 'handlers' collection.
         */
        notebooks.widgetAdded.connect((sender, nbPanel) => {
            //A promise that resolves after the initialization of the handler is done.
            handlers[nbPanel.id] = new Promise((resolve, reject) => {
                const session = nbPanel.sessionContext;
                const connector = new _kernelconnector__WEBPACK_IMPORTED_MODULE_12__.KernelConnector({ session });
                const rendermime = nbPanel.content.rendermime;
                const scripts = connector.ready.then(async () => {
                    const lang = await connector.kernelLanguage;
                    return _inspectorscripts__WEBPACK_IMPORTED_MODULE_13__.Languages.getScript(lang);
                });
                scripts.then((result) => {
                    const initScript = result.initScript;
                    const queryCommand = result.queryCommand;
                    const matrixQueryCommand = result.matrixQueryCommand;
                    const widgetQueryCommand = result.widgetQueryCommand;
                    const deleteCommand = result.deleteCommand;
                    const changeSettingsCommand = result.changeSettingsCommand;
                    const options = {
                        queryCommand,
                        matrixQueryCommand,
                        widgetQueryCommand,
                        deleteCommand,
                        connector,
                        rendermime,
                        initScript,
                        changeSettingsCommand,
                        id: session.path,
                        setting
                    };
                    const handler = new _handler__WEBPACK_IMPORTED_MODULE_14__.VariableInspectionHandler(options);
                    manager.addHandler(handler);
                    nbPanel.disposed.connect(() => {
                        delete handlers[nbPanel.id];
                        handler.dispose();
                    });
                    handler.ready.then(() => {
                        resolve(handler);
                    });
                });
                //Otherwise log error message.
                scripts.catch((result) => {
                    reject(result);
                });
            });
            setSource(labShell);
        });
        const setSource = (sender, args) => {
            var _a;
            const widget = (_a = args === null || args === void 0 ? void 0 : args.newValue) !== null && _a !== void 0 ? _a : sender.currentWidget;
            if (!widget || !notebooks.has(widget) || widget.isDisposed) {
                return;
            }
            const future = handlers[widget.id];
            future === null || future === void 0 ? void 0 : future.then((source) => {
                if (source) {
                    manager.source = source;
                    manager.source.performInspection();
                }
            });
        };
        /**
         * If focus window changes, checks whether new focus widget is a notebook.
         * In that case, retrieves the handler associated to the notebook after it has been
         * initialized and updates the manager with it.
         */
        setSource(labShell);
        labShell.currentChanged.connect(setSource);
        // app.contextMenu.addItem({
        //   command: CommandIDs.toggleVariableMonitor,
        //   selector: '.jp-Notebook'
        // });
    }
};
/**
 * Export the plugins as default.
 */
const plugins = [
    variableinspector,
    consoles,
    notebooks
];

/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugins);


/***/ }),

/***/ "./lib/widgets/variable/inspectorscripts.js":
/*!**************************************************!*\
  !*** ./lib/widgets/variable/inspectorscripts.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   Languages: () => (/* binding */ Languages)
/* harmony export */ });
class Languages {
    static getScript(lang) {
        return new Promise((resolve, reject) => {
            if (lang in Languages.scripts) {
                resolve(Languages.scripts[lang]);
            }
            else {
                reject('Language ' + lang + ' not supported yet!');
            }
        });
    }
}
/**
 * Init and query script for supported languages.
 */
Languages.py_script = `import json
import sys
from importlib import __import__
from itertools import islice
import collections
from IPython import get_ipython
from IPython.core.magics.namespace import NamespaceMagics


_jupyterlab_variableinspector_nms = NamespaceMagics()
_jupyterlab_variableinspector_Jupyter = get_ipython()
_jupyterlab_variableinspector_nms.shell = _jupyterlab_variableinspector_Jupyter.kernel.shell

_jupyterlab_variableinspector_maxitems = 10

__np = None
__pd = None
__pyspark = None
__tf = None
__K = None
__torch = None
__ipywidgets = None
__xr = None


def _attempt_import(module):
    try:
        # Only "import" if it was already imported
        if module in sys.modules:
            return __import__(module)
    except ImportError:
        return None


def _check_imported():
    global __np, __pd, __pyspark, __tf, __K, __torch, __ipywidgets, __xr

    __np = _attempt_import('numpy')
    __pd = _attempt_import('pandas')
    __pyspark = _attempt_import('pyspark')
    __tf = _attempt_import('tensorflow')
    __K = _attempt_import('keras.backend') or _attempt_import('tensorflow.keras.backend')
    __torch = _attempt_import('torch')
    __ipywidgets = _attempt_import('ipywidgets')
    __xr = _attempt_import('xarray')


def _jupyterlab_variableinspector_changesettings(maxitems, **kwargs):
    global _jupyterlab_variableinspector_maxitems

    _jupyterlab_variableinspector_maxitems = maxitems


def _jupyterlab_variableinspector_getsizeof(x):
    if type(x).__name__ in ['ndarray', 'Series']:
        return x.nbytes
    elif __pyspark and isinstance(x, __pyspark.sql.DataFrame):
        return "?"
    elif __tf and isinstance(x, __tf.Variable):
        return "?"
    elif __torch and isinstance(x, __torch.Tensor):
        return x.element_size() * x.nelement()
    elif __pd and type(x).__name__ == 'DataFrame':
        # DO NOT CALL df.memory_usage() for big dataframes as this can be very costly
        # to the point of making the kernel unresponsive or crashing it
        if len(x.columns) < 10_000:
            return x.memory_usage().sum()
        else:
            return "?"
    else:
        return sys.getsizeof(x)


def _jupyterlab_variableinspector_getshapeof(x):
    if __pd and isinstance(x, __pd.DataFrame):
        return "%d rows x %d cols" % x.shape
    if __pd and isinstance(x, __pd.Series):
        return "%d rows" % x.shape
    if __np and isinstance(x, __np.ndarray):
        shape = " x ".join([str(i) for i in x.shape])
        return "%s" % shape
    if __pyspark and isinstance(x, __pyspark.sql.DataFrame):
        return "? rows x %d cols" % len(x.columns)
    if __tf and isinstance(x, __tf.Variable):
        shape = " x ".join([str(int(i)) for i in x.shape])
        return "%s" % shape
    if __tf and isinstance(x, __tf.Tensor):
        shape = " x ".join([str(int(i)) for i in x.shape])
        return "%s" % shape
    if __torch and isinstance(x, __torch.Tensor):
        shape = " x ".join([str(int(i)) for i in x.shape])
        return "%s" % shape
    if __xr and isinstance(x, __xr.DataArray):
        shape = " x ".join([str(int(i)) for i in x.shape])
        return "%s" % shape
    if isinstance(x, list):
        return "%s" % len(x)
    if isinstance(x, dict):
        return "%s keys" % len(x)
    return None


def _jupyterlab_variableinspector_getcontentof(x):
    # returns content in a friendly way for python variables
    # pandas and numpy
    if isinstance(x, (bool, str, int, float, type(None))):
        content = str(x)
    elif isinstance(x, (list, tuple)):
        if len(x) <= _jupyterlab_variableinspector_maxitems:
            content = str(x)
        else:
            content = "["
            for i in range(_jupyterlab_variableinspector_maxitems):
                content += f"{x[i]}, "
            content += "...]"
    elif isinstance(x, collections.abc.Mapping):
        if len(x.keys()) <= _jupyterlab_variableinspector_maxitems:
            content = str(x)
        else:
            first_ten_keys = list(islice(x.keys(), _jupyterlab_variableinspector_maxitems))
            content = "{"
            for idx, key in enumerate(first_ten_keys):
                if idx > 0:
                    content += ", "
                content += f'"{key}": {x[key]}'
            content += ", ...}"
    elif __pd and isinstance(x, __pd.DataFrame):
        if len(x.columns) <= _jupyterlab_variableinspector_maxitems:
            colnames = ', '.join(x.columns.map(str))
            content = "Columns: %s" % colnames
        else:
            content = "Columns: "
            for idx in range(_jupyterlab_variableinspector_maxitems):
                if idx > 0:
                    content += ", "
                content += str(x.columns[idx])
            content += ", ..."
            return content
    elif __pd and isinstance(x, __pd.Series):
        content = str(x.values).replace(" ", ", ")[1:-1]
        content = content.replace("\\n", "")
    elif __np and isinstance(x, __np.ndarray):
        content = x.__repr__()
    elif __xr and isinstance(x, __xr.DataArray):
        content = x.values.__repr__()
    else:
        content = str(x)

    if len(content) > 150:
        return content[:150] + " ..."
    else:
        return content


def _jupyterlab_variableinspector_is_matrix(x):
    # True if type(x).__name__ in ["DataFrame", "ndarray", "Series"] else False
    if __pd and isinstance(x, __pd.DataFrame):
        return True
    if __pd and isinstance(x, __pd.Series):
        return True
    if __np and isinstance(x, __np.ndarray) and len(x.shape) <= 2:
        return True
    if __pyspark and isinstance(x, __pyspark.sql.DataFrame):
        return True
    if __tf and isinstance(x, __tf.Variable) and len(x.shape) <= 2:
        return True
    if __tf and isinstance(x, __tf.Tensor) and len(x.shape) <= 2:
        return True
    if __torch and isinstance(x, __torch.Tensor) and len(x.shape) <= 2:
        return True
    if __xr and isinstance(x, __xr.DataArray) and len(x.shape) <= 2:
        return True
    if isinstance(x, list):
        return True
    return False


def _jupyterlab_variableinspector_is_widget(x):
    return __ipywidgets and issubclass(x, __ipywidgets.DOMWidget)


def _jupyterlab_variableinspector_dict_list():
    _check_imported()
    def keep_cond(v):
        try:
            obj = eval(v)
            if isinstance(obj, (bool, str, list, tuple, collections.abc.Mapping, int, float, type(None))):
                return True
            if __tf and isinstance(obj, __tf.Variable):
                return True
            if __pd and __pd is not None and (
                isinstance(obj, __pd.core.frame.DataFrame)
                or isinstance(obj, __pd.core.series.Series)):
                return True
            if __xr and __xr is not None and isinstance(obj, __xr.DataArray):
                return True
            if str(obj)[0] == "<":
                return False
            if  v in ['__np', '__pd', '__pyspark', '__tf', '__K', '__torch', '__ipywidgets', '__xr']:
                return obj is not None
            if str(obj).startswith("_Feature"):
                # removes tf/keras objects
                return False
            return True
        except:
            return False
    values = _jupyterlab_variableinspector_nms.who_ls()
    vardic = [
        {
            'varName': _v,
            'varType': type(eval(_v)).__name__,
            'varSize': str(_jupyterlab_variableinspector_getsizeof(eval(_v))),
            'varShape': str(_jupyterlab_variableinspector_getshapeof(eval(_v))) if _jupyterlab_variableinspector_getshapeof(eval(_v)) else '',
            'varContent': str(_jupyterlab_variableinspector_getcontentof(eval(_v))),
            'isMatrix': _jupyterlab_variableinspector_is_matrix(eval(_v)),
            'isWidget': _jupyterlab_variableinspector_is_widget(type(eval(_v)))
        }
        for _v in values if keep_cond(_v)
    ]
    return json.dumps(vardic, ensure_ascii=False)


def _jupyterlab_variableinspector_getmatrixcontent(x, max_rows=10000):
    # to do: add something to handle this in the future
    threshold = max_rows

    if __pd and __pyspark and isinstance(x, __pyspark.sql.DataFrame):
        df = x.limit(threshold).toPandas()
        return _jupyterlab_variableinspector_getmatrixcontent(df.copy())
    elif __np and __pd and type(x).__name__ == "DataFrame":
        if threshold is not None:
            x = x.head(threshold)
        x.columns = x.columns.map(str)
        return x.to_json(orient="table", default_handler=_jupyterlab_variableinspector_default, force_ascii=False)
    elif __np and __pd and type(x).__name__ == "Series":
        if threshold is not None:
            x = x.head(threshold)
        return x.to_json(orient="table", default_handler=_jupyterlab_variableinspector_default, force_ascii=False)
    elif __np and __pd and type(x).__name__ == "ndarray":
        df = __pd.DataFrame(x)
        return _jupyterlab_variableinspector_getmatrixcontent(df)
    elif __tf and (isinstance(x, __tf.Variable) or isinstance(x, __tf.Tensor)):
        df = __K.get_value(x)
        return _jupyterlab_variableinspector_getmatrixcontent(df)
    elif __torch and isinstance(x, __torch.Tensor):
        df = x.cpu().numpy()
        return _jupyterlab_variableinspector_getmatrixcontent(df)
    elif __xr and isinstance(x, __xr.DataArray):
        df = x.to_numpy()
        return _jupyterlab_variableinspector_getmatrixcontent(df)
    elif isinstance(x, list):
        s = __pd.Series(x)
        return _jupyterlab_variableinspector_getmatrixcontent(s)


def _jupyterlab_variableinspector_displaywidget(widget):
    display(widget)


def _jupyterlab_variableinspector_default(o):
    if isinstance(o, __np.number): return int(o)
    raise TypeError


def _jupyterlab_variableinspector_deletevariable(x):
    exec("del %s" % x, globals())
`;
Languages.r_script = `library(repr)

.ls.objects = function (pos = 1, pattern, order.by, decreasing = FALSE, head = FALSE,
    n = 5)
{
    napply <- function(names, fn) sapply(names, function(x) fn(get(x,
        pos = pos)))
    names <- ls(pos = pos, pattern = pattern)
    if (length(names) == 0) {
        return(jsonlite::toJSON(data.frame()))
    }
    obj.class <- napply(names, function(x) as.character(class(x))[1])
    obj.mode <- napply(names, mode)
    obj.type <- ifelse(is.na(obj.class), obj.mode, obj.class)
    obj.size <- napply(names, object.size)
    obj.dim <- t(napply(names, function(x) as.numeric(dim(x))[1:2]))
    obj.content <- rep("NA", length(names))
    has_no_dim <- is.na(obj.dim)[1:length(names)]
    obj.dim[has_no_dim, 1] <- napply(names, length)[has_no_dim]
    vec <- (obj.type != "function")
    obj.content[vec] <- napply(names[vec], function(x) toString(x, width = 154)[1])

    obj.rownames <- napply(names, rownames)
    has_rownames <- obj.rownames != "NULL"
    obj.rownames <- sapply(obj.rownames[has_rownames], function(x) paste(x,
        collapse=", "))
    obj.rownames.short <- sapply(obj.rownames, function(x) paste(substr(x, 1, 150), "...."))
    obj.rownames <- ifelse(nchar(obj.rownames) > 154, obj.rownames.short, obj.rownames)
    obj.rownames <- sapply(obj.rownames, function(x) paste("Row names: ",x))
    obj.content[has_rownames] <- obj.rownames


    obj.colnames <- napply(names, colnames)
    has_colnames <- obj.colnames != "NULL"
    obj.colnames <- sapply(obj.colnames[has_colnames], function(x) paste(x,
        collapse = ", "))
    obj.colnames.short <- sapply(obj.colnames, function(x) paste(substr(x,
        1, 150), "...."))
    obj.colnames <- ifelse(nchar(obj.colnames) > 154, obj.colnames.short,
        obj.colnames)
    obj.colnames <- sapply(obj.colnames, function(x) paste("Column names: ",x))

    obj.content[has_colnames] <- obj.colnames

    is_function <- (obj.type == "function")
    obj.content[is_function] <- napply(names[is_function], function(x) paste(strsplit(repr_text(x),")")[[1]][1],")",sep=""))
    obj.content <- unlist(obj.content, use.names = FALSE)


    out <- data.frame(obj.type, obj.size, obj.dim)
    names(out) <- c("varType", "varSize", "Rows", "Columns")
    out$varShape <- paste(out$Rows, " x ", out$Columns)
    out$varContent <- obj.content
    out$isMatrix <- FALSE
    out$varName <- row.names(out)
    out <- out[, !(names(out) %in% c("Rows", "Columns"))]
    rownames(out) <- NULL
    print(out)
    if (!missing(order.by))
        out <- out[order(out[[order.by]], decreasing = decreasing),
            ]
    if (head)
        out <- head(out, n)
    jsonlite::toJSON(out)
}

.deleteVariable <- function(x) {
    remove(list=c(x), envir=.GlobalEnv)
}
    `;
Languages.scripts = {
    python3: {
        initScript: Languages.py_script,
        queryCommand: '_jupyterlab_variableinspector_dict_list()',
        matrixQueryCommand: '_jupyterlab_variableinspector_getmatrixcontent',
        widgetQueryCommand: '_jupyterlab_variableinspector_displaywidget',
        deleteCommand: '_jupyterlab_variableinspector_deletevariable',
        changeSettingsCommand: (settings) => `_jupyterlab_variableinspector_changesettings(maxitems=${settings.maxItems})`
    },
    python2: {
        initScript: Languages.py_script,
        queryCommand: '_jupyterlab_variableinspector_dict_list()',
        matrixQueryCommand: '_jupyterlab_variableinspector_getmatrixcontent',
        widgetQueryCommand: '_jupyterlab_variableinspector_displaywidget',
        deleteCommand: '_jupyterlab_variableinspector_deletevariable',
        changeSettingsCommand: (settings) => `_jupyterlab_variableinspector_changesettings(maxitems=${settings.maxItems})`
    },
    python: {
        initScript: Languages.py_script,
        queryCommand: '_jupyterlab_variableinspector_dict_list()',
        matrixQueryCommand: '_jupyterlab_variableinspector_getmatrixcontent',
        widgetQueryCommand: '_jupyterlab_variableinspector_displaywidget',
        deleteCommand: '_jupyterlab_variableinspector_deletevariable',
        changeSettingsCommand: (settings) => `_jupyterlab_variableinspector_changesettings(maxitems=${settings.maxItems})`
    },
    R: {
        initScript: Languages.r_script,
        queryCommand: '.ls.objects()',
        matrixQueryCommand: '.ls.objects',
        widgetQueryCommand: 'TODO',
        deleteCommand: '.deleteVariable'
    },
    scala: {
        initScript: '_root_.almond.api.JupyterAPIHolder.value.VariableInspector.init()',
        queryCommand: '_root_.almond.api.JupyterAPIHolder.value.VariableInspector.dictList()',
        matrixQueryCommand: '',
        widgetQueryCommand: '',
        deleteCommand: '' // TODO
    }
};



/***/ }),

/***/ "./lib/widgets/variable/kernelconnector.js":
/*!*************************************************!*\
  !*** ./lib/widgets/variable/kernelconnector.js ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   KernelConnector: () => (/* binding */ KernelConnector)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);

/**
 * Connector class that handles execute request to a kernel
 */
class KernelConnector {
    constructor(options) {
        this._kernelChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._kernelRestarted = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._session = options.session;
        this._session.statusChanged.connect((sender, newStatus) => {
            switch (newStatus) {
                case 'restarting':
                case 'autorestarting':
                    this._kernelRestarted.emit(this._session.ready);
                    break;
                default:
                    break;
            }
        });
        this._session.kernelChanged.connect(() => this._kernelChanged.emit(this._session.ready));
    }
    get kernelChanged() {
        return this._kernelChanged;
    }
    get kernelRestarted() {
        return this._kernelRestarted;
    }
    get kernelLanguage() {
        var _a;
        if (!((_a = this._session.session) === null || _a === void 0 ? void 0 : _a.kernel)) {
            return Promise.resolve('');
        }
        return this._session.session.kernel.info.then(infoReply => {
            return infoReply.language_info.name;
        });
    }
    get kernelName() {
        return this._session.kernelDisplayName;
    }
    /**
     *  A Promise that is fulfilled when the session associated w/ the connector is ready.
     */
    get ready() {
        return this._session.ready;
    }
    /**
     *  A signal emitted for iopub messages of the kernel associated with the kernel.
     */
    get iopubMessage() {
        return this._session.iopubMessage;
    }
    /**
     * Executes the given request on the kernel associated with the connector.
     * @param content: IExecuteRequestMsg to forward to the kernel.
     * @param ioCallback: Callable to forward IOPub messages of the kernel to.
     * @returns Promise<KernelMessage.IExecuteReplyMsg>
     */
    fetch(content, ioCallback) {
        var _a;
        const kernel = (_a = this._session.session) === null || _a === void 0 ? void 0 : _a.kernel;
        if (!kernel) {
            return Promise.reject(new Error('Require kernel to perform variable inspection!'));
        }
        const future = kernel.requestExecute(content);
        future.onIOPub = (msg) => {
            ioCallback(msg);
        };
        return future.done;
    }
    execute(content) {
        var _a;
        if (!((_a = this._session.session) === null || _a === void 0 ? void 0 : _a.kernel)) {
            throw new Error('No session available.');
        }
        return this._session.session.kernel.requestExecute(content);
    }
}


/***/ }),

/***/ "./lib/widgets/variable/manager.js":
/*!*****************************************!*\
  !*** ./lib/widgets/variable/manager.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   VariableInspectorManager: () => (/* binding */ VariableInspectorManager)
/* harmony export */ });
/**
 * A class that manages variable inspector widget instances and offers persistent
 * `IVariableInspector` instance that other plugins can communicate with.
 */
class VariableInspectorManager {
    constructor() {
        this._source = null;
        this._panel = null;
        this._handlers = {};
    }
    hasHandler(id) {
        if (this._handlers[id]) {
            return true;
        }
        else {
            return false;
        }
    }
    getHandler(id) {
        return this._handlers[id];
    }
    addHandler(handler) {
        this._handlers[handler.id] = handler;
    }
    /**
     * The current inspector panel.
     */
    get panel() {
        return this._panel;
    }
    set panel(panel) {
        if (this.panel === panel) {
            return;
        }
        this._panel = panel;
        if (panel && !panel.source) {
            panel.source = this._source;
        }
    }
    /**
     * The source of events the inspector panel listens for.
     */
    get source() {
        return this._source;
    }
    set source(source) {
        if (this._source === source) {
            return;
        }
        // remove subscriptions
        if (this._source) {
            this._source.disposed.disconnect(this._onSourceDisposed, this);
        }
        this._source = source;
        if (this._panel && !this._panel.isDisposed) {
            this._panel.source = this._source;
        }
        // Subscribe to new source
        if (this._source) {
            this._source.disposed.connect(this._onSourceDisposed, this);
        }
    }
    _onSourceDisposed() {
        this._source = null;
    }
}


/***/ }),

/***/ "./lib/widgets/variable/tokens.js":
/*!****************************************!*\
  !*** ./lib/widgets/variable/tokens.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   IVariableInspector: () => (/* binding */ IVariableInspector),
/* harmony export */   IVariableInspectorManager: () => (/* binding */ IVariableInspectorManager)
/* harmony export */ });
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);

const IVariableInspectorManager = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.Token('jupyterlab_extension/variableinspector:IVariableInspectorManager');
/**
 * The inspector panel token.
 */
const IVariableInspector = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.Token('jupyterlab_extension/variableinspector:IVariableInspector');


/***/ }),

/***/ "./lib/widgets/variable/variableinspector.js":
/*!***************************************************!*\
  !*** ./lib/widgets/variable/variableinspector.js ***!
  \***************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   VariableInspectorPanel: () => (/* binding */ VariableInspectorPanel)
/* harmony export */ });
/* harmony import */ var _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/outputarea */ "webpack/sharing/consume/default/@jupyterlab/outputarea");
/* harmony import */ var _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyter/web-components */ "webpack/sharing/consume/default/@jupyter/web-components/@jupyter/web-components");
/* harmony import */ var _jupyter_web_components__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var wildcard_match__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! wildcard-match */ "webpack/sharing/consume/default/wildcard-match/wildcard-match");
/* harmony import */ var wildcard_match__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(wildcard_match__WEBPACK_IMPORTED_MODULE_4__);


// import { DataGrid, DataModel } from '@lumino/datagrid';


(0,_jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__.provideJupyterDesignSystem)().register((0,_jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__.jpDataGrid)(), (0,_jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__.jpDataGridRow)(), (0,_jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__.jpDataGridCell)(), (0,_jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__.jpTextField)(), (0,_jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__.jpOption)(), (0,_jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__.jpSelect)(), (0,_jupyter_web_components__WEBPACK_IMPORTED_MODULE_3__.jpButton)());

const TITLE_CLASS = 'jp-VarInspector-title';
const PANEL_CLASS = 'jp-VarInspector';
const TABLE_CLASS = 'jp-VarInspector-table';
const TABLE_ROW_CLASS = 'jp-VarInspector-table-row';
const TABLE_ROW_HIDDEN_CLASS = 'jp-VarInspector-table-row-hidden';
const TABLE_TYPE_CLASS = 'jp-VarInspector-type';
const TABLE_NAME_CLASS = 'jp-VarInspector-varName';
const FILTER_TYPE_CLASS = 'filter-type';
const FILTER_INPUT_CLASS = 'filter-input';
const FILTER_BUTTON_CLASS = 'filter-button';
const FILTER_LIST_CLASS = 'filter-list';
const FILTERED_BUTTON_CLASS = 'filtered-variable-button';
/**
 * A panel that renders the variables
 */
class VariableInspectorPanel extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__.Widget {
    constructor() {
        super();
        this._source = null;
        this.addClass(PANEL_CLASS);
        this._title = Private.createTitle();
        this._title.className = TITLE_CLASS;
        this._table = Private.createTable();
        this._table.className = TABLE_CLASS;
        this._filteredTable = Private.createFilterTable();
        // this.node.appendChild(this._title as HTMLElement);
        this.node.appendChild(this._filteredTable);
        this.node.appendChild(this._table);
        this._filtered = { type: [], name: [] };
        this.intializeFilteredTable();
    }
    //Sets up the filter table so when the filter button is pressed, a new filter is created
    intializeFilteredTable() {
        const filterType = this._filteredTable.querySelector('.' + FILTER_TYPE_CLASS);
        const filterInput = this._filteredTable.querySelector('.' + FILTER_INPUT_CLASS);
        const filterButton = this._filteredTable.querySelector('.' + FILTER_BUTTON_CLASS);
        filterButton.addEventListener('click', () => {
            this.onFilterChange(filterType.value, filterInput.value, true);
        });
    }
    // Checks if string is in the filtered array
    stringInFilter(string, filterType) {
        // console.log(this._filtered[filterType]);
        for (let i = 0; i < this._filtered[filterType].length; i++) {
            const isMatch = wildcard_match__WEBPACK_IMPORTED_MODULE_4___default()(this._filtered[filterType][i]);
            if (isMatch(string)) {
                return true;
            }
        }
        return false;
    }
    /*
      Either adds a new filter or removes a previously existing filter based
      Params:
      filterType: By what type the varName is filtering on
      varName: The name of the variable we are trying to filter out
      isAdding: If we are adding a new filter or removing a previous filter
    */
    onFilterChange(filterType, varName, isAdding) {
        if (varName === '') {
            return;
        }
        if (isAdding) {
            if (this._filtered[filterType].includes(varName)) {
                return;
            }
            this._filtered[filterType].push(varName);
            const filterList = this._filteredTable.querySelector('.' + FILTER_LIST_CLASS);
            const newFilteredButton = Private.createFilteredButton(varName, filterType);
            newFilteredButton.addEventListener('click', () => {
                const filterText = newFilteredButton.querySelector('.filtered-variable-button-text');
                this.onFilterChange(filterType, filterText.innerHTML, false);
                this.addFilteredOutRows();
                newFilteredButton.remove();
            });
            filterList.appendChild(newFilteredButton);
            this.filterOutTable();
        }
        else {
            this._filtered[filterType] = this._filtered[filterType].filter(filter => filter !== varName);
        }
    }
    /*
    Goes through each filtered out row and checks if they should still be filtered
    If not, the row becomes visible again
    */
    addFilteredOutRows() {
        const rows = this._table.querySelectorAll('.' + TABLE_ROW_HIDDEN_CLASS);
        for (let i = 0; i < rows.length; i++) {
            const rowName = rows[i].querySelector('.' + TABLE_NAME_CLASS);
            const rowType = rows[i].querySelector('.' + TABLE_TYPE_CLASS);
            if (!this.stringInFilter(rowName.innerHTML, 'name') &&
                !this._filtered['type'].includes(rowType.innerHTML)) {
                rows[i].className = TABLE_ROW_CLASS;
            }
        }
    }
    /*
    Goes through each row and checks if the row should be filtered out
    A row is filtered out if it matches any of the values in the _filtered object
    */
    filterOutTable() {
        const rows = this._table.querySelectorAll('.' + TABLE_ROW_CLASS);
        for (let i = 0; i < rows.length; i++) {
            const rowName = rows[i].querySelector('.' + TABLE_NAME_CLASS);
            const rowType = rows[i].querySelector('.' + TABLE_TYPE_CLASS);
            if (this.stringInFilter(rowName.innerHTML, 'name') ||
                this._filtered['type'].includes(rowType.innerHTML)) {
                rows[i].className = TABLE_ROW_HIDDEN_CLASS;
            }
        }
    }
    /*
    Goes through each row and if it finds a variable with name 'name', then it deletes it
    */
    removeRow(name) {
        const rows = this._table.querySelectorAll('.' + TABLE_ROW_CLASS);
        for (let i = 0; i < rows.length; i++) {
            const cell = rows[i].querySelector('.' + TABLE_NAME_CLASS);
            if (cell.innerHTML === name) {
                rows[i].remove();
                return;
            }
        }
    }
    get source() {
        return this._source;
    }
    set source(source) {
        if (this._source === source) {
            // this._source.performInspection();
            return;
        }
        //Remove old subscriptions
        if (this._source) {
            this._source.enabled = false;
            this._source.inspected.disconnect(this.onInspectorUpdate, this);
            this._source.disposed.disconnect(this.onSourceDisposed, this);
        }
        this._source = source;
        //Subscribe to new object
        if (this._source) {
            this._source.enabled = true;
            this._source.inspected.connect(this.onInspectorUpdate, this);
            this._source.disposed.connect(this.onSourceDisposed, this);
            this._source.performInspection();
        }
    }
    /**
     * Dispose resources
     */
    dispose() {
        if (this.isDisposed) {
            return;
        }
        if (this.source) {
            this.source.enabled = false;
        }
        this.source = null;
        super.dispose();
    }
    onCloseRequest(msg) {
        super.onCloseRequest(msg);
        if (this._source) {
            this._source.enabled = false;
        }
    }
    onAfterShow(msg) {
        super.onAfterShow(msg);
        if (this._source) {
            this._source.enabled = true;
            this._source.performInspection();
        }
    }
    onInspectorUpdate(sender, allArgs) {
        var _a;
        if (!this.isAttached) {
            return;
        }
        const args = allArgs.payload;
        this._table.innerHTML = '';
        // 添加样式标签来控制表格布局
        const styleTag = document.createElement('style');
        styleTag.textContent = `
      jp-data-grid-cell {
        min-width: 200px;
        white-space: normal;
        word-break: break-all;
        overflow: auto;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .column-header {
        font-weight: bold;
        background-color: #f0f0f0;
      }
      .jp-VarInspector-deleteButton {
        display: flex;
        align-items: center;
        justify-content: center;
      }
    `;
        this._table.appendChild(styleTag);
        const headerRow = document.createElement('jp-data-grid-row');
        headerRow.className = 'sticky-header';
        const columns = ['', '变量名', '变量类型', '变量值'];
        for (let i = 0; i < columns.length; i++) {
            const headerCell = document.createElement('jp-data-grid-cell');
            headerCell.className = 'column-header';
            headerCell.textContent = columns[i];
            headerCell.gridColumn = (i + 1).toString();
            headerRow.appendChild(headerCell);
        }
        this._table.appendChild(headerRow);
        for (let index = 0; index < args.length; index++) {
            const item = args[index];
            const name = item.varName;
            const varType = item.varType;
            const row = document.createElement('jp-data-grid-row');
            row.className = TABLE_ROW_CLASS;
            if (this._filtered['type'].includes(varType)) {
                row.className = TABLE_ROW_HIDDEN_CLASS;
            }
            else if (this.stringInFilter(name, 'name')) {
                row.className = TABLE_ROW_HIDDEN_CLASS;
            }
            // 删除按钮单元格
            let cell = document.createElement('jp-data-grid-cell');
            cell.title = 'Delete Variable';
            cell.className = 'jp-VarInspector-deleteButton';
            cell.gridColumn = '1';
            const closeButton = document.createElement('jp-button');
            closeButton.appearance = 'stealth';
            const ico = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.closeIcon.element();
            ico.className = 'icon-button';
            ico.onclick = (ev) => {
                this.removeRow(name);
            };
            closeButton.append(ico);
            cell.append(closeButton);
            row.appendChild(cell);
            // 变量名单元格
            cell = document.createElement('jp-data-grid-cell');
            cell.className = TABLE_NAME_CLASS;
            cell.innerHTML = name;
            cell.gridColumn = '2';
            row.appendChild(cell);
            // 变量类型单元格
            cell = document.createElement('jp-data-grid-cell');
            cell.innerHTML = varType;
            cell.className = TABLE_TYPE_CLASS;
            cell.gridColumn = '3';
            row.appendChild(cell);
            // 变量值单元格
            cell = document.createElement('jp-data-grid-cell');
            const rendermime = (_a = this._source) === null || _a === void 0 ? void 0 : _a.rendermime;
            if (item.isWidget && rendermime) {
                const model = new _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_0__.OutputAreaModel({ trusted: true });
                const output = new _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_0__.SimplifiedOutputArea({ model, rendermime });
                output.future = this._source.performWidgetInspection(item.varName);
                _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__.Widget.attach(output, cell);
            }
            else {
                cell.innerHTML = Private.escapeHtml(item.varContent).replace(/\\n/g, '</br>');
            }
            cell.gridColumn = '4';
            row.appendChild(cell);
            this._table.appendChild(row);
        }
    }
    /**
     * Handle source disposed signals.
     */
    onSourceDisposed(sender, args) {
        this.source = null;
    }
}
var Private;
(function (Private) {
    const entityMap = new Map(Object.entries({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '/': '&#x2F;'
    }));
    function escapeHtml(source) {
        return String(source).replace(/[&<>"'/]/g, (s) => entityMap.get(s));
    }
    Private.escapeHtml = escapeHtml;
    function createTable() {
        const table = document.createElement('jp-data-grid');
        table.generateHeader = 'sticky';
        table.gridTemplateColumns = '1fr 1fr 6fr 4fr 4fr 5fr 16fr';
        return table;
    }
    Private.createTable = createTable;
    function createTitle(header = '') {
        const title = document.createElement('p');
        title.innerHTML = header;
        return title;
    }
    Private.createTitle = createTitle;
    function createFilterTable() {
        const container = document.createElement('div');
        container.className = 'filter-container';
        const filterType = document.createElement('jp-select');
        filterType.className = FILTER_TYPE_CLASS;
        filterType.selectedIndex = 0;
        const varTypeOption = document.createElement('jp-option');
        varTypeOption.value = 'type';
        varTypeOption.innerHTML = 'Type';
        const nameOption = document.createElement('jp-option');
        nameOption.value = 'name';
        nameOption.innerHTML = 'Name';
        filterType.appendChild(varTypeOption);
        filterType.appendChild(nameOption);
        const searchContainer = document.createElement('div');
        searchContainer.className = 'filter-search-container';
        const input = document.createElement('jp-text-field');
        input.setAttribute('type', 'text');
        input.setAttribute('placeholder', 'Filter out variable');
        input.className = FILTER_INPUT_CLASS;
        const filterButton = document.createElement('jp-button');
        filterButton.textContent = 'Filter';
        filterButton.className = FILTER_BUTTON_CLASS;
        filterButton.appearance = 'accent';
        const list = document.createElement('ul');
        list.className = FILTER_LIST_CLASS;
        searchContainer.appendChild(filterType);
        searchContainer.appendChild(input);
        searchContainer.appendChild(filterButton);
        searchContainer.style.display = 'none';
        container.appendChild(searchContainer);
        container.appendChild(list);
        return container;
    }
    Private.createFilterTable = createFilterTable;
    //Creates a button with given filter information displayed on the button
    function createFilteredButton(filterName, filterType) {
        const filteredButton = document.createElement('jp-button');
        filteredButton.value = filterType;
        filteredButton.title = filterType;
        filteredButton.className = FILTERED_BUTTON_CLASS;
        const filterButtonContent = document.createElement('div');
        filterButtonContent.className = 'filter-button-content';
        const buttonText = document.createElement('div');
        buttonText.className = 'filtered-variable-button-text';
        buttonText.innerHTML = filterName;
        _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.closeIcon.element({
            container: filterButtonContent
        });
        filterButtonContent.insertAdjacentElement('afterbegin', buttonText);
        filteredButton.appendChild(filterButtonContent);
        filteredButton.className = FILTERED_BUTTON_CLASS;
        return filteredButton;
    }
    Private.createFilteredButton = createFilteredButton;
})(Private || (Private = {}));


/***/ }),

/***/ "./lib/widgets/version.js":
/*!********************************!*\
  !*** ./lib/widgets/version.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _api_project__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../api/project */ "./lib/api/project.js");
/* harmony import */ var react_dom_client__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-dom/client */ "./node_modules/react-dom/client.js");
/* harmony import */ var _components_VersionList__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../components/VersionList */ "./lib/components/VersionList.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_3__);






class VersionListSidebarWidget extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor(app, notebookProjectId) {
        super();
        this._app = app;
        this._notebookProjectId = notebookProjectId;
        this.addClass('ln-version-list-sidebar'); // 使用 ln- 前缀
        this.id = 'ln-version-list-sidebar';
        this.title.caption = '版本';
        this.title.label = '版本';
        this.title.icon = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.listIcon;
        this.title.closable = true; // 允许关闭
        // 创建列表容器
        this.listContainer = document.createElement('div');
        this.listContainer.className = 'ln-version-list';
        this.node.appendChild(this.listContainer);
        this.params = {
            searchKey: '',
            pageSize: 15,
            pageNum: 1,
            tagLabels: [],
            sortType: 'deployTime'
        };
        // 调用获取版本的函数
        this.getVersions(notebookProjectId);
    }
    async getVersions(notebookProjectId) {
        const params = {
            notebookId: notebookProjectId || '',
            pageSize: 1,
            pageNum: 1
        };
        try {
            const res = await (0,_api_project__WEBPACK_IMPORTED_MODULE_4__.getProjectVersionList)(params);
            const list = res.list;
            this.updateVersionList(list); // 更新版本列表
        }
        catch (error) {
            console.error('Failed to fetch versions:', error);
        }
    }
    updateVersionList(data) {
        this.listContainer.innerHTML = '';
        const versions = data || [];
        // 确保正确处理空数组情况
        if (versions.length === 0) {
            this.listContainer.innerHTML =
                '<div style="width:100%;text-align:center;margin-top:20px">暂无版本</div>';
            return;
        }
        // 使用 createRoot 替代 ReactDOM.render（推荐）
        const root = (0,react_dom_client__WEBPACK_IMPORTED_MODULE_2__.createRoot)(this.listContainer);
        root.render(react__WEBPACK_IMPORTED_MODULE_3___default().createElement("div", null, versions.map(version => (react__WEBPACK_IMPORTED_MODULE_3___default().createElement(_components_VersionList__WEBPACK_IMPORTED_MODULE_5__.VersionList, { key: version.version, id: version.id, version: version.version, createTime: version.createTime, app: this._app, projectId: this._notebookProjectId })))));
    }
    install(app) {
        app.shell.add(this, 'left', {
            rank: 900,
            type: 'tab'
        });
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (VersionListSidebarWidget);


/***/ }),

/***/ "./node_modules/react-dom/client.js":
/*!******************************************!*\
  !*** ./node_modules/react-dom/client.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {



var m = __webpack_require__(/*! react-dom */ "webpack/sharing/consume/default/react-dom");
if (false) {} else {
  var i = m.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED;
  exports.createRoot = function(c, o) {
    i.usingClientEntryPoint = true;
    try {
      return m.createRoot(c, o);
    } finally {
      i.usingClientEntryPoint = false;
    }
  };
  exports.hydrateRoot = function(c, h, o) {
    i.usingClientEntryPoint = true;
    try {
      return m.hydrateRoot(c, h, o);
    } finally {
      i.usingClientEntryPoint = false;
    }
  };
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.2ef6673f1a5ec2c0d520.js.map