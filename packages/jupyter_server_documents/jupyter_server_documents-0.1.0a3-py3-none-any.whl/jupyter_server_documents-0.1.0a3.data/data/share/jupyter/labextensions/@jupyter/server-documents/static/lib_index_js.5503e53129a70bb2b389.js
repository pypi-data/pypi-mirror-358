"use strict";
(self["webpackChunk_jupyter_server_documents"] = self["webpackChunk_jupyter_server_documents"] || []).push([["lib_index_js"],{

/***/ "./lib/codemirror-binding/plugin.js":
/*!******************************************!*\
  !*** ./lib/codemirror-binding/plugin.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   codemirrorYjsPlugin: () => (/* binding */ codemirrorYjsPlugin)
/* harmony export */ });
/* harmony import */ var _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/codemirror */ "webpack/sharing/consume/default/@jupyterlab/codemirror");
/* harmony import */ var _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _ybinding__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./ybinding */ "./lib/codemirror-binding/ybinding.js");
/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */


/**
 * CodeMirror shared model binding provider.
 */
const codemirrorYjsPlugin = {
    id: '@jupyter/server-documents:ybinding',
    description: 'Register the CodeMirror extension factory binding the editor and the shared model.',
    autoStart: true,
    requires: [_jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_0__.IEditorExtensionRegistry],
    activate: (app, extensions) => {
        extensions.addExtension({
            name: 'shared-model-binding',
            factory: options => {
                var _a;
                const sharedModel = options.model.sharedModel;
                return _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_0__.EditorExtensionRegistry.createImmutableExtension((0,_ybinding__WEBPACK_IMPORTED_MODULE_1__.ybinding)({
                    getYText: () => sharedModel.ysource,
                    ytextResetSignal: sharedModel.resetSignal,
                    undoManager: (_a = sharedModel.undoManager) !== null && _a !== void 0 ? _a : undefined
                }));
            }
        });
    }
};


/***/ }),

/***/ "./lib/codemirror-binding/ybinding.js":
/*!********************************************!*\
  !*** ./lib/codemirror-binding/ybinding.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   YRange: () => (/* binding */ YRange),
/* harmony export */   YSyncConfig: () => (/* binding */ YSyncConfig),
/* harmony export */   ySync: () => (/* binding */ ySync),
/* harmony export */   ySyncAnnotation: () => (/* binding */ ySyncAnnotation),
/* harmony export */   ySyncFacet: () => (/* binding */ ySyncFacet),
/* harmony export */   ybinding: () => (/* binding */ ybinding)
/* harmony export */ });
/* harmony import */ var _codemirror_state__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @codemirror/state */ "webpack/sharing/consume/default/@codemirror/state");
/* harmony import */ var _codemirror_state__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_codemirror_state__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _codemirror_view__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @codemirror/view */ "webpack/sharing/consume/default/@codemirror/view");
/* harmony import */ var _codemirror_view__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_codemirror_view__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _yundomanager__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./yundomanager */ "./lib/codemirror-binding/yundomanager.js");
/* harmony import */ var yjs__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! yjs */ "webpack/sharing/consume/default/yjs");
/* harmony import */ var yjs__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(yjs__WEBPACK_IMPORTED_MODULE_2__);
/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 *
 * Binding for yjs and codemirror
 *
 * It is a simplification of https://github.com/yjs/y-codemirror.next
 * licensed under MIT License by Kevin Jahns
 */


// TODO: for some reason undo doesn't work when we import these from
// '@jupyterlab/codemirror/lib/extensions/yundomanager'.
// Therefore we import from './yundomanager.ts', whose contents are copied from
// '@jupyterlab/codemirror'.
// Reference: issue #85


/**
 * Defines a range on text using relative positions that can be transformed back to
 * absolute positions. (https://docs.yjs.dev/api/relative-positions)
 */
class YRange {
    /**
     * @param yanchor
     * @param yhead
     */
    constructor(yanchor, yhead) {
        this.yanchor = yanchor;
        this.yhead = yhead;
    }
    /**
     * Convert the position to JSON
     */
    toJSON() {
        return {
            yanchor: (0,yjs__WEBPACK_IMPORTED_MODULE_2__.relativePositionToJSON)(this.yanchor),
            yhead: (0,yjs__WEBPACK_IMPORTED_MODULE_2__.relativePositionToJSON)(this.yhead)
        };
    }
    /**
     * Convert a JSON range to a YRange
     * @param json Range to convert
     * @return The range as YRange
     */
    static fromJSON(json) {
        return new YRange((0,yjs__WEBPACK_IMPORTED_MODULE_2__.createRelativePositionFromJSON)(json.yanchor), (0,yjs__WEBPACK_IMPORTED_MODULE_2__.createRelativePositionFromJSON)(json.yhead));
    }
}
/**
 * Yjs binding configuration
 */
class YSyncConfig {
    /**
     * Create a new binding configuration
     *
     * @param ytext Yjs text to synchronize
     */
    constructor(getYText, ytextResetSignal) {
        this.getYText = getYText;
        this.ytextResetSignal = ytextResetSignal;
    }
    /**
     * Helper function to transform an absolute index position to a Yjs-based relative position
     * (https://docs.yjs.dev/api/relative-positions).
     *
     * A relative position can be transformed back to an absolute position even after the document has changed. The position is
     * automatically adapted. This does not require any position transformations. Relative positions are computed based on
     * the internal Yjs document model. Peers that share content through Yjs are guaranteed that their positions will always
     * synced up when using relative positions.
     *
     * ```js
     * import { ySyncFacet } from 'y-codemirror'
     *
     * ..
     * const ysync = view.state.facet(ySyncFacet)
     * // transform an absolute index position to a ypos
     * const ypos = ysync.getYPos(3)
     * // transform the ypos back to an absolute position
     * ysync.fromYPos(ypos) // => 3
     * ```
     *
     * It cannot be guaranteed that absolute index positions can be synced up between peers.
     * This might lead to undesired behavior when implementing features that require that all peers see the
     * same marked range (e.g. a comment plugin).
     *
     * @param pos
     * @param assoc
     */
    toYPos(pos, assoc = 0) {
        return (0,yjs__WEBPACK_IMPORTED_MODULE_2__.createRelativePositionFromTypeIndex)(this.getYText(), pos, assoc);
    }
    /**
     * @param rpos
     */
    fromYPos(rpos) {
        const pos = (0,yjs__WEBPACK_IMPORTED_MODULE_2__.createAbsolutePositionFromRelativePosition)((0,yjs__WEBPACK_IMPORTED_MODULE_2__.createRelativePositionFromJSON)(rpos), this.getYText().doc);
        if (pos === null || pos.type !== this.getYText()) {
            throw new Error('[y-codemirror] The position you want to retrieve was created by a different document');
        }
        return {
            pos: pos.index,
            assoc: pos.assoc
        };
    }
    /**
     * @param range
     * @return
     */
    toYRange(range) {
        const assoc = range.assoc;
        const yanchor = this.toYPos(range.anchor, assoc);
        const yhead = this.toYPos(range.head, assoc);
        return new YRange(yanchor, yhead);
    }
    /**
     * @param yrange
     */
    fromYRange(yrange) {
        const anchor = this.fromYPos(yrange.yanchor);
        const head = this.fromYPos(yrange.yhead);
        if (anchor.pos === head.pos) {
            return _codemirror_state__WEBPACK_IMPORTED_MODULE_0__.EditorSelection.cursor(head.pos, head.assoc);
        }
        return _codemirror_state__WEBPACK_IMPORTED_MODULE_0__.EditorSelection.range(anchor.pos, head.pos);
    }
}
/**
 * Yjs binding facet
 */
const ySyncFacet = _codemirror_state__WEBPACK_IMPORTED_MODULE_0__.Facet.define({
    combine(inputs) {
        return inputs[inputs.length - 1];
    }
});
/**
 * Yjs binding annotation
 *
 * It is used to track the origin of the document changes
 */
const ySyncAnnotation = _codemirror_state__WEBPACK_IMPORTED_MODULE_0__.Annotation.define();
/**
 * Yjs binding view plugin to synchronize the
 * editor state with the Yjs document.
 */
const ySync = _codemirror_view__WEBPACK_IMPORTED_MODULE_1__.ViewPlugin.fromClass(class {
    constructor(view) {
        // Bind instance properties
        this.view = view;
        this.conf = view.state.facet(ySyncFacet);
        this._getYText = this.conf.getYText;
        this._ytext = this._getYText();
        this._resetSignal = this.conf.ytextResetSignal;
        // Add observer on YText
        this._ytext_observer = (e, t) => this._handle_ytext_update(e, t);
        this._ytext.observe(this._ytext_observer);
        // Add signal listener to reset YText
        this._resetSignalSlot = () => {
            this._handle_reset();
        };
        if (this._resetSignal) {
            this._resetSignal.connect(this._resetSignalSlot);
        }
    }
    _handle_ytext_update(event, tr) {
        var _a;
        if (tr.origin !== this.conf) {
            const delta = event.delta;
            const changes = [];
            let pos = 0;
            for (let i = 0; i < delta.length; i++) {
                const d = delta[i];
                // eslint-disable-next-line eqeqeq
                if (d.insert != null) {
                    changes.push({ from: pos, to: pos, insert: d.insert });
                    // eslint-disable-next-line eqeqeq
                }
                else if (d.delete != null) {
                    changes.push({ from: pos, to: pos + d.delete, insert: '' });
                    pos += d.delete;
                }
                else {
                    pos += (_a = d.retain) !== null && _a !== void 0 ? _a : 0;
                }
            }
            this.view.dispatch({
                changes,
                // Specified the changes origin to not loop when synchronizing
                annotations: [ySyncAnnotation.of(this.conf)]
            });
        }
    }
    _handle_reset() {
        // Remove observer
        this._ytext.unobserve(this._ytext_observer);
        // Clear the editor
        // From: https://stackoverflow.com/questions/16378355/how-to-reset-codemirror-editor
        this.view.dispatch({
            changes: {
                from: 0,
                to: this.view.state.doc.toString().length,
                insert: ''
            }
        });
        // Get new YText and add observer
        this._ytext = this._getYText();
        this._ytext.observe(this._ytext_observer);
    }
    update(update) {
        if (!update.docChanged ||
            (update.transactions.length > 0 &&
                update.transactions[0].annotation(ySyncAnnotation) === this.conf)) {
            return;
        }
        const ytext = this._ytext;
        ytext.doc.transact(() => {
            /**
             * This variable adjusts the fromA position to the current position in the Y.Text type.
             */
            let adj = 0;
            update.changes.iterChanges((fromA, toA, fromB, toB, insert) => {
                const insertText = insert.sliceString(0, insert.length, '\n');
                if (fromA !== toA) {
                    ytext.delete(fromA + adj, toA - fromA);
                }
                if (insertText.length > 0) {
                    ytext.insert(fromA + adj, insertText);
                }
                adj += insertText.length - (toA - fromA);
            });
            // Set the configuration as origin to not loop when synchronizing
        }, this.conf);
    }
    destroy() {
        this._ytext.unobserve(this._ytext_observer);
        if (this._resetSignal) {
            this._resetSignal.disconnect(this._resetSignalSlot);
        }
    }
});
/**
 * Extension for CodeMirror 6 binding the Yjs text (source of truth)
 * and the editor state.
 *
 * @param ytext Y.Text shared type to bind
 * @param undoManager Yjs text undo manager
 * @returns CodeMirror 6 extension
 */
function ybinding(args) {
    const ySyncConfig = new YSyncConfig(args.getYText, args.ytextResetSignal);
    const plugins = [ySyncFacet.of(ySyncConfig), ySync];
    if (args.undoManager) {
        plugins.push(
        // We need to add a new origin to the undo manager to ensure text updates
        // are tracked; we also need to restore selection after undo/redo.
        _yundomanager__WEBPACK_IMPORTED_MODULE_3__.yUndoManagerFacet.of(new _yundomanager__WEBPACK_IMPORTED_MODULE_3__.YUndoManagerConfig(args.undoManager)), _yundomanager__WEBPACK_IMPORTED_MODULE_3__.yUndoManager);
    }
    return plugins;
}


/***/ }),

/***/ "./lib/codemirror-binding/yundomanager.js":
/*!************************************************!*\
  !*** ./lib/codemirror-binding/yundomanager.js ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   YUndoManagerConfig: () => (/* binding */ YUndoManagerConfig),
/* harmony export */   yUndoManager: () => (/* binding */ yUndoManager),
/* harmony export */   yUndoManagerFacet: () => (/* binding */ yUndoManagerFacet)
/* harmony export */ });
/* harmony import */ var _codemirror_view__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @codemirror/view */ "webpack/sharing/consume/default/@codemirror/view");
/* harmony import */ var _codemirror_view__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_codemirror_view__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _codemirror_state__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @codemirror/state */ "webpack/sharing/consume/default/@codemirror/state");
/* harmony import */ var _codemirror_state__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_codemirror_state__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _ybinding__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./ybinding */ "./lib/codemirror-binding/ybinding.js");
/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 *
 * Vendored from https://github.com/yjs/y-codemirror.next
 * licensed under MIT License by Kevin Jahns.
 *
 * Ideally we would depend on the y-codemirror.next, but it is impractical
 * until https://github.com/yjs/y-codemirror.next/issues/27 is resolved.
 *
 * Modifications compared to upstream:
 * - removed spurious mutex (https://github.com/yjs/y-codemirror.next/issues/15)
 * - added TypeScript types
 * - simplified `YUndoManagerConfig` by removing public methods
 * - moved `_onStackItemAdded`, `_onStackItemPopped` and `_storeSelection` definitions out of constructor
 */



class YUndoManagerConfig {
    constructor(undoManager) {
        this.undoManager = undoManager;
    }
}
const yUndoManagerFacet = _codemirror_state__WEBPACK_IMPORTED_MODULE_1__.Facet.define({
    combine(inputs) {
        return inputs[inputs.length - 1];
    }
});
class YUndoManagerPluginValue {
    constructor(view) {
        this._onStackItemAdded = ({ stackItem, changedParentTypes }) => {
            // only store metadata if this type was affected
            if (changedParentTypes.has(this._syncConf.getYText()) &&
                this._beforeChangeSelection &&
                !stackItem.meta.has(this)) {
                // do not overwrite previous stored selection
                stackItem.meta.set(this, this._beforeChangeSelection);
            }
        };
        this._onStackItemPopped = ({ stackItem }) => {
            const sel = stackItem.meta.get(this);
            if (sel) {
                const selection = this._syncConf.fromYRange(sel);
                this._view.dispatch(this._view.state.update({
                    selection,
                    effects: [_codemirror_view__WEBPACK_IMPORTED_MODULE_0__.EditorView.scrollIntoView(selection)]
                }));
                this._storeSelection();
            }
        };
        this._storeSelection = () => {
            // store the selection before the change is applied so we can restore it with the undo manager.
            this._beforeChangeSelection = this._syncConf.toYRange(this._view.state.selection.main);
        };
        this._view = view;
        this._conf = view.state.facet(yUndoManagerFacet);
        this._undoManager = this._conf.undoManager;
        this._syncConf = view.state.facet(_ybinding__WEBPACK_IMPORTED_MODULE_2__.ySyncFacet);
        this._beforeChangeSelection = null;
        this._undoManager.on('stack-item-added', this._onStackItemAdded);
        this._undoManager.on('stack-item-popped', this._onStackItemPopped);
        this._undoManager.addTrackedOrigin(this._syncConf);
    }
    update(update) {
        if (update.selectionSet &&
            (update.transactions.length === 0 ||
                update.transactions[0].annotation(_ybinding__WEBPACK_IMPORTED_MODULE_2__.ySyncAnnotation) !== this._syncConf)) {
            // This only works when YUndoManagerPlugin is included before the sync plugin
            this._storeSelection();
        }
    }
    destroy() {
        this._undoManager.off('stack-item-added', this._onStackItemAdded);
        this._undoManager.off('stack-item-popped', this._onStackItemPopped);
        this._undoManager.removeTrackedOrigin(this._syncConf);
    }
}
const yUndoManager = _codemirror_view__WEBPACK_IMPORTED_MODULE_0__.ViewPlugin.fromClass(YUndoManagerPluginValue);


/***/ }),

/***/ "./lib/docprovider/awareness.js":
/*!**************************************!*\
  !*** ./lib/docprovider/awareness.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   WebSocketAwarenessProvider: () => (/* binding */ WebSocketAwarenessProvider)
/* harmony export */ });
/* harmony import */ var y_websocket__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! y-websocket */ "webpack/sharing/consume/default/y-websocket/y-websocket");
/* harmony import */ var y_websocket__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(y_websocket__WEBPACK_IMPORTED_MODULE_0__);
/* -----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/

/**
 * A class to provide Yjs synchronization over WebSocket.
 *
 * We specify custom messages that the server can interpret. For reference please look in yjs_ws_server.
 *
 */
class WebSocketAwarenessProvider extends y_websocket__WEBPACK_IMPORTED_MODULE_0__.WebsocketProvider {
    /**
     * Construct a new WebSocketAwarenessProvider
     *
     * @param options The instantiation options for a WebSocketAwarenessProvider
     */
    constructor(options) {
        super(options.url, options.roomID, options.awareness.doc, {
            awareness: options.awareness
        });
        this._isDisposed = false;
        this._awareness = options.awareness;
        this._user = options.user;
        this._user.ready
            .then(() => this._onUserChanged(this._user))
            .catch(e => console.error(e));
        this._user.userChanged.connect(this._onUserChanged, this);
    }
    get isDisposed() {
        return this._isDisposed;
    }
    dispose() {
        if (this._isDisposed) {
            return;
        }
        this._user.userChanged.disconnect(this._onUserChanged, this);
        this._isDisposed = true;
        this.destroy();
    }
    _onUserChanged(user) {
        this._awareness.setLocalStateField('user', user.identity);
    }
}


/***/ }),

/***/ "./lib/docprovider/custom_ydocs.js":
/*!*****************************************!*\
  !*** ./lib/docprovider/custom_ydocs.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   YFile: () => (/* binding */ YFile),
/* harmony export */   YNotebook: () => (/* binding */ YNotebook)
/* harmony export */ });
/* harmony import */ var _jupyter_ydoc__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyter/ydoc */ "webpack/sharing/consume/default/@jupyter/ydoc");
/* harmony import */ var _jupyter_ydoc__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyter_ydoc__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var yjs__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! yjs */ "webpack/sharing/consume/default/yjs");
/* harmony import */ var yjs__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(yjs__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var y_protocols_awareness__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! y-protocols/awareness */ "./node_modules/y-protocols/awareness.js");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_3__);




class YFile extends _jupyter_ydoc__WEBPACK_IMPORTED_MODULE_0__.YFile {
    constructor() {
        super();
        this._resetSignal = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__.Signal(this);
    }
    /**
     * Resets the YDoc to an empty state and emits an event for consumers to
     * respond to via the `YFile.resetSignal`.
     *
     * This method should be called when the server's YDoc history changes. This
     * may happen when the server detects an out-of-band change to the file on
     * disk, or when the server needs to erase YDoc history to save memory.
     */
    reset() {
        // TODO (?): Remove *all* observers, including those added by consumers,
        // then re-add them. We only do this for observers added by default for now.
        // The issue is that Yjs does not provide methods for accessing the list of
        // observers or migrating them to a new `Y.Doc()` instance.
        // Remove default observers
        this._ystate.unobserve(this.onStateChanged);
        this.ysource.unobserve(this._modelObserver);
        // Reset `this._ydoc` to an empty state
        this._ydoc = new yjs__WEBPACK_IMPORTED_MODULE_1__.Doc();
        // Reset all properties derived from `this._ydoc`
        this.ysource = this.ydoc.getText('source');
        this._ystate = this.ydoc.getMap('state');
        this._undoManager = new yjs__WEBPACK_IMPORTED_MODULE_1__.UndoManager([], {
            trackedOrigins: new Set([this]),
            doc: this._ydoc
        });
        this._undoManager.addToScope(this.ysource);
        this._awareness = new y_protocols_awareness__WEBPACK_IMPORTED_MODULE_2__.Awareness(this.ydoc);
        // Emit to `this.resetSignal` to inform consumers immediately
        this._resetSignal.emit(null);
        // Add back default observers
        this._ystate.observe(this.onStateChanged);
        this.ysource.observe(this._modelObserver);
    }
    /**
     * Signal that is emitted to whenever the YDoc is reset. Consumers should
     * listen to this signal if they need to act when the YDoc is reset.
     *
     * The Codemirror Yjs extension defined in `ybinding.ts` listens to this
     * signal to clear the editor when the YDoc is reset.
     */
    get resetSignal() {
        return this._resetSignal;
    }
}
class YNotebook extends _jupyter_ydoc__WEBPACK_IMPORTED_MODULE_0__.YNotebook {
    constructor(options) {
        super(options);
        this._resetSignal = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__.Signal(this);
    }
    /**
     * See `YFile.reset()`.
     */
    reset() {
        // Remove default observers
        this._ycells.unobserve(this._onYCellsChanged);
        this.ymeta.unobserveDeep(this._onMetaChanged);
        this._ystate.unobserve(this.onStateChanged);
        // Reset `this._ydoc` to an empty state
        this._ydoc = new yjs__WEBPACK_IMPORTED_MODULE_1__.Doc();
        // Reset all properties derived from `this._ydoc`
        this._ystate = this.ydoc.getMap('state');
        this._ycells = this.ydoc.getArray('cells');
        this.cells = [];
        this.ymeta = this.ydoc.getMap('meta');
        this._undoManager = new yjs__WEBPACK_IMPORTED_MODULE_1__.UndoManager([], {
            trackedOrigins: new Set([this]),
            doc: this._ydoc
        });
        this._undoManager.addToScope(this._ycells);
        this._awareness = new y_protocols_awareness__WEBPACK_IMPORTED_MODULE_2__.Awareness(this.ydoc);
        // Emit to `this.resetSignal` to inform consumers immediately
        this._resetSignal.emit(null);
        // Add back default observers
        this._ycells.observe(this._onYCellsChanged);
        this.ymeta.observeDeep(this._onMetaChanged);
        this._ystate.observe(this.onStateChanged);
    }
    /**
     * See `YFile.resetSignal`.
     */
    get resetSignal() {
        return this._resetSignal;
    }
}


/***/ }),

/***/ "./lib/docprovider/filebrowser.js":
/*!****************************************!*\
  !*** ./lib/docprovider/filebrowser.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   logger: () => (/* binding */ logger),
/* harmony export */   rtcContentProvider: () => (/* binding */ rtcContentProvider),
/* harmony export */   yfile: () => (/* binding */ yfile),
/* harmony export */   ynotebook: () => (/* binding */ ynotebook)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/fileeditor */ "webpack/sharing/consume/default/@jupyterlab/fileeditor");
/* harmony import */ var _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_logconsole__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/logconsole */ "webpack/sharing/consume/default/@jupyterlab/logconsole");
/* harmony import */ var _jupyterlab_logconsole__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_logconsole__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _custom_ydocs__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./custom_ydocs */ "./lib/docprovider/custom_ydocs.js");
/* harmony import */ var _jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyter/collaborative-drive */ "webpack/sharing/consume/default/@jupyter/collaborative-drive/@jupyter/collaborative-drive");
/* harmony import */ var _jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _ydrive__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./ydrive */ "./lib/docprovider/ydrive.js");
/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */









const TWO_SESSIONS_WARNING = 'The file %1 has been opened with two different views. ' +
    'This is not supported. Please close this view; otherwise, ' +
    'some of your edits may not be saved properly.';
const rtcContentProvider = {
    id: '@jupyter/server-documents:rtc-content-provider',
    description: 'The RTC content provider',
    provides: _jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_6__.ICollaborativeContentProvider,
    requires: [_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5__.ITranslator],
    optional: [_jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_6__.IGlobalAwareness],
    activate: (app, translator, globalAwareness) => {
        const trans = translator.load('jupyter_collaboration');
        const defaultDrive = app.serviceManager.contents
            .defaultDrive;
        if (!defaultDrive) {
            throw Error('Cannot initialize content provider: default drive property not accessible on contents manager instance.');
        }
        const registry = defaultDrive.contentProviderRegistry;
        if (!registry) {
            throw Error('Cannot initialize content provider: no content provider registry.');
        }
        const rtcContentProvider = new _ydrive__WEBPACK_IMPORTED_MODULE_7__.RtcContentProvider({
            app,
            apiEndpoint: '/api/contents',
            serverSettings: defaultDrive.serverSettings,
            user: app.serviceManager.user,
            trans,
            globalAwareness
        });
        registry.register('rtc', rtcContentProvider);
        return rtcContentProvider;
    }
};
/**
 * Plugin to register the shared model factory for the content type 'file'.
 */
const yfile = {
    id: '@jupyter/server-documents:yfile',
    description: "Plugin to register the shared model factory for the content type 'file'",
    autoStart: true,
    requires: [_jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_6__.ICollaborativeContentProvider, _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_1__.IEditorWidgetFactory],
    activate: (app, contentProvider, editorFactory) => {
        const yFileFactory = () => {
            return new _custom_ydocs__WEBPACK_IMPORTED_MODULE_8__.YFile();
        };
        contentProvider.sharedModelFactory.registerDocumentFactory('file', yFileFactory);
        editorFactory.contentProviderId = 'rtc';
    }
};
/**
 * Plugin to register the shared model factory for the content type 'notebook'.
 */
const ynotebook = {
    id: '@jupyter/server-documents:ynotebook',
    description: "Plugin to register the shared model factory for the content type 'notebook'",
    autoStart: true,
    requires: [_jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_6__.ICollaborativeContentProvider, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.INotebookWidgetFactory],
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_4__.ISettingRegistry],
    activate: (app, contentProvider, notebookFactory, settingRegistry) => {
        let disableDocumentWideUndoRedo = true;
        // Fetch settings if possible.
        if (settingRegistry) {
            settingRegistry
                .load('@jupyterlab/notebook-extension:tracker')
                .then(settings => {
                const updateSettings = (settings) => {
                    const enableDocWideUndo = settings === null || settings === void 0 ? void 0 : settings.get('experimentalEnableDocumentWideUndoRedo').composite;
                    disableDocumentWideUndoRedo = !(enableDocWideUndo !== null && enableDocWideUndo !== void 0 ? enableDocWideUndo : false);
                };
                updateSettings(settings);
                settings.changed.connect((settings) => updateSettings(settings));
            });
        }
        const yNotebookFactory = () => {
            return new _custom_ydocs__WEBPACK_IMPORTED_MODULE_8__.YNotebook({
                disableDocumentWideUndoRedo
            });
        };
        contentProvider.sharedModelFactory.registerDocumentFactory('notebook', yNotebookFactory);
        notebookFactory.contentProviderId = 'rtc';
    }
};
/**
 * The default collaborative drive provider.
 */
const logger = {
    id: '@jupyter/server-documents:rtc-drive-logger',
    description: 'A logging plugin for debugging purposes.',
    autoStart: true,
    optional: [_jupyterlab_logconsole__WEBPACK_IMPORTED_MODULE_2__.ILoggerRegistry, _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_1__.IEditorTracker, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.INotebookTracker, _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5__.ITranslator],
    activate: (app, loggerRegistry, fileTracker, nbTracker, translator) => {
        const trans = (translator !== null && translator !== void 0 ? translator : _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_5__.nullTranslator).load('jupyter_collaboration');
        const schemaID = 'https://schema.jupyter.org/jupyter_collaboration/session/v1';
        if (!loggerRegistry) {
            app.serviceManager.events.stream.connect((_, emission) => {
                var _a, _b;
                if (emission.schema_id === schemaID) {
                    console.debug(`[${emission.room}(${emission.path})] ${(_a = emission.action) !== null && _a !== void 0 ? _a : ''}: ${(_b = emission.msg) !== null && _b !== void 0 ? _b : ''}`);
                    if (emission.level === 'WARNING') {
                        (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                            title: trans.__('Warning'),
                            body: trans.__(TWO_SESSIONS_WARNING, emission.path),
                            buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]
                        });
                    }
                }
            });
            return;
        }
        const loggers = new Map();
        const addLogger = (sender, document) => {
            const logger = loggerRegistry.getLogger(document.context.path);
            loggers.set(document.context.localPath, logger);
            document.disposed.connect(document => {
                loggers.delete(document.context.localPath);
            });
        };
        if (fileTracker) {
            fileTracker.widgetAdded.connect(addLogger);
        }
        if (nbTracker) {
            nbTracker.widgetAdded.connect(addLogger);
        }
        void (async () => {
            var _a, _b;
            const { events } = app.serviceManager;
            for await (const emission of events.stream) {
                if (emission.schema_id === schemaID) {
                    const logger = loggers.get(emission.path);
                    logger === null || logger === void 0 ? void 0 : logger.log({
                        type: 'text',
                        level: emission.level.toLowerCase(),
                        data: `[${emission.room}] ${(_a = emission.action) !== null && _a !== void 0 ? _a : ''}: ${(_b = emission.msg) !== null && _b !== void 0 ? _b : ''}`
                    });
                    if (emission.level === 'WARNING') {
                        (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                            title: trans.__('Warning'),
                            body: trans.__(TWO_SESSIONS_WARNING, emission.path),
                            buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.warnButton({ label: trans.__('Ok') })]
                        });
                    }
                }
            }
        })();
    }
};


/***/ }),

/***/ "./lib/docprovider/requests.js":
/*!*************************************!*\
  !*** ./lib/docprovider/requests.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/* -----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.error('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/docprovider/ydrive.js":
/*!***********************************!*\
  !*** ./lib/docprovider/ydrive.js ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   RtcContentProvider: () => (/* binding */ RtcContentProvider)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _yprovider__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./yprovider */ "./lib/docprovider/yprovider.js");
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.




const DISABLE_RTC = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.PageConfig.getOption('disableRTC') === 'true' ? true : false;
/**
 * The url for the default drive service.
 */
const DOCUMENT_PROVIDER_URL = 'api/collaboration/room';
class RtcContentProvider extends _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.RestContentProvider {
    constructor(options) {
        super(options);
        this._onCreate = (options, sharedModel) => {
            var _a, _b;
            if (typeof options.format !== 'string') {
                return;
            }
            try {
                const provider = new _yprovider__WEBPACK_IMPORTED_MODULE_3__.WebSocketProvider({
                    app: this._app,
                    url: _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(this._serverSettings.wsUrl, DOCUMENT_PROVIDER_URL),
                    path: options.path,
                    format: options.format,
                    contentType: options.contentType,
                    model: sharedModel,
                    user: this._user,
                    translator: this._trans
                });
                // Add the document path in the list of opened ones for this user.
                const state = ((_a = this._globalAwareness) === null || _a === void 0 ? void 0 : _a.getLocalState()) || {};
                const documents = state.documents || [];
                if (!documents.includes(options.path)) {
                    documents.push(options.path);
                    (_b = this._globalAwareness) === null || _b === void 0 ? void 0 : _b.setLocalStateField('documents', documents);
                }
                const key = `${options.format}:${options.contentType}:${options.path}`;
                this._providers.set(key, provider);
                sharedModel.changed.connect(async (_, change) => {
                    var _a;
                    if (!change.stateChange) {
                        return;
                    }
                    const hashChanges = change.stateChange.filter(change => change.name === 'hash');
                    if (hashChanges.length === 0) {
                        return;
                    }
                    if (hashChanges.length > 1) {
                        console.error('Unexpected multiple changes to hash value in a single transaction');
                    }
                    const hashChange = hashChanges[0];
                    // A change in hash signifies that a save occurred on the server-side
                    // (e.g. a collaborator performed the save) - we want to notify the
                    // observers about this change so that they can store the new hash value.
                    const newPath = (_a = sharedModel.state.path) !== null && _a !== void 0 ? _a : options.path;
                    const model = await this.get(newPath, { content: false });
                    this._ydriveFileChanged.emit({
                        type: 'save',
                        newValue: { ...model, hash: hashChange.newValue },
                        // we do not have the old model because it was discarded when server made the change,
                        // we only have the old hash here (which may be empty if the file was newly created!)
                        oldValue: { hash: hashChange.oldValue }
                    });
                });
                sharedModel.disposed.connect(() => {
                    var _a, _b;
                    const provider = this._providers.get(key);
                    if (provider) {
                        provider.dispose();
                        this._providers.delete(key);
                    }
                    // Remove the document path from the list of opened ones for this user.
                    const state = ((_a = this._globalAwareness) === null || _a === void 0 ? void 0 : _a.getLocalState()) || {};
                    const documents = state.documents || [];
                    const index = documents.indexOf(options.path);
                    if (index > -1) {
                        documents.splice(index, 1);
                    }
                    (_b = this._globalAwareness) === null || _b === void 0 ? void 0 : _b.setLocalStateField('documents', documents);
                });
            }
            catch (error) {
                // Falling back to the contents API if opening the websocket failed
                //  This may happen if the shared document is not a YDocument.
                console.error(`Failed to open websocket connection for ${options.path}.\n:${error}`);
            }
        };
        this._ydriveFileChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__.Signal(this);
        this._app = options.app;
        this._user = options.user;
        this._trans = options.trans;
        this._globalAwareness = options.globalAwareness;
        this._serverSettings = options.serverSettings;
        this.sharedModelFactory = new SharedModelFactory(this._onCreate);
        this._providers = new Map();
    }
    get providers() {
        return this._providers;
    }
    /**
     * Get a file or directory.
     *
     * @param localPath: The path to the file.
     *
     * @param options: The options used to fetch the file.
     *
     * @returns A promise which resolves with the file content.
     */
    async get(localPath, options) {
        if (options && options.format && options.type) {
            const key = `${options.format}:${options.type}:${localPath}`;
            const provider = this._providers.get(key);
            if (provider) {
                // If the document doesn't exist, `super.get` will reject with an
                // error and the provider will never be resolved.
                // Use `Promise.all` to reject as soon as possible. The Context will
                // show a dialog to the user.
                const [model] = await Promise.all([
                    super.get(localPath, { ...options, content: false }),
                    provider.ready
                ]);
                // The server doesn't return a model with a format when content is false,
                // so set it back.
                return { ...model, format: options.format };
            }
        }
        return super.get(localPath, options);
    }
    /**
     * Save a file.
     *
     * @param localPath - The desired file path.
     *
     * @param options - Optional overrides to the model.
     *
     * @returns A promise which resolves with the file content model when the
     *   file is saved.
     */
    async save(localPath, options = {}) {
        // Check that there is a provider - it won't e.g. if the document model is not collaborative.
        if (options.format && options.type) {
            const key = `${options.format}:${options.type}:${localPath}`;
            const provider = this._providers.get(key);
            if (provider) {
                // Save is done from the backend
                const fetchOptions = {
                    type: options.type,
                    format: options.format,
                    content: false
                };
                return this.get(localPath, fetchOptions);
            }
        }
        return super.save(localPath, options);
    }
    /**
     * A signal emitted when a file operation takes place.
     */
    get fileChanged() {
        return this._ydriveFileChanged;
    }
}
/**
 * Yjs sharedModel factory for real-time collaboration.
 */
class SharedModelFactory {
    /**
     * Shared model factory constructor
     *
     * @param _onCreate Callback on new document model creation
     */
    constructor(_onCreate) {
        this._onCreate = _onCreate;
        /**
         * Whether the IDrive supports real-time collaboration or not.
         */
        this.collaborative = !DISABLE_RTC;
        this.documentFactories = new Map();
    }
    /**
     * Register a SharedDocumentFactory.
     *
     * @param type Document type
     * @param factory Document factory
     */
    registerDocumentFactory(type, factory) {
        if (this.documentFactories.has(type)) {
            throw new Error(`The content type ${type} already exists`);
        }
        this.documentFactories.set(type, factory);
    }
    /**
     * Create a new `ISharedDocument` instance.
     *
     * It should return `undefined` if the factory is not able to create a `ISharedDocument`.
     */
    createNew(options) {
        var _a;
        if (typeof options.format !== 'string') {
            console.warn(`Only defined format are supported; got ${options.format}.`);
            return;
        }
        /**
         * Whether RTC is enabled on the YDrive.
         */
        const ydriveRtcEnabled = this.collaborative;
        /**
         * Whether RTC is enabled on this document. This defaults to `true` to align
         * with the docstring on `options.collaborative`.
         */
        const docRtcEnabled = (_a = options.collaborative) !== null && _a !== void 0 ? _a : true;
        if (!ydriveRtcEnabled || !docRtcEnabled) {
            // Bail if the document model does not support collaboration
            // the `sharedModel` will be the default one.
            return;
        }
        if (this.documentFactories.has(options.contentType)) {
            const factory = this.documentFactories.get(options.contentType);
            const sharedModel = factory(options);
            this._onCreate(options, sharedModel);
            return sharedModel;
        }
        return;
    }
}


/***/ }),

/***/ "./lib/docprovider/yprovider.js":
/*!**************************************!*\
  !*** ./lib/docprovider/yprovider.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   WebSocketProvider: () => (/* binding */ WebSocketProvider)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var y_websocket__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! y-websocket */ "webpack/sharing/consume/default/y-websocket/y-websocket");
/* harmony import */ var y_websocket__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(y_websocket__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _requests__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./requests */ "./lib/docprovider/requests.js");
/* harmony import */ var _jupyterlab_docregistry__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/docregistry */ "webpack/sharing/consume/default/@jupyterlab/docregistry");
/* harmony import */ var _jupyterlab_docregistry__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docregistry__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/fileeditor */ "webpack/sharing/consume/default/@jupyterlab/fileeditor");
/* harmony import */ var _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_6__);
/* -----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/









/**
 * A class to provide Yjs synchronization over WebSocket.
 *
 * We specify custom messages that the server can interpret. For reference please look in yjs_ws_server.
 *
 */
class WebSocketProvider {
    /**
     * Construct a new WebSocketProvider
     *
     * @param options The instantiation options for a WebSocketProvider
     */
    constructor(options) {
        /**
         * Handles disconnections from the YRoom Websocket.
         *
         * TODO: Issue #45.
         */
        this._onConnectionClosed = (event) => {
            // Handle close events based on code
            const close_code = event.code;
            // 4000 := indicates out-of-band change
            if (close_code === 4000) {
                this._handleOobChange();
                return;
            }
            // 4001 := indicates out-of-band move/deletion
            if (close_code === 4001) {
                this._handleOobMove();
                return;
            }
            // 4002 := indicates in-band deletion
            if (close_code === 4002) {
                this._handleIbDeletion();
                return;
            }
            // If the close code is unhandled, log an error to the browser console and
            // show a popup asking user to refresh the page.
            console.error('WebSocket connection was closed. Close event: ', event);
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)(this._trans.__('Document session error'), 'Please refresh the browser tab.', [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]);
            // Stop `y-websocket` from re-connecting by disposing of the shared model.
            // This seems to be the only way to halt re-connection attempts.
            this._sharedModel.dispose();
        };
        this._onSync = (isSynced) => {
            if (isSynced) {
                if (this._yWebsocketProvider) {
                    this._yWebsocketProvider.off('sync', this._onSync);
                }
                this._ready.resolve();
            }
        };
        this._ready = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__.PromiseDelegate();
        this._fileId = null;
        this._app = options.app;
        this._isDisposed = false;
        this._path = options.path;
        this._contentType = options.contentType;
        this._format = options.format;
        this._serverUrl = options.url;
        this._sharedModel = options.model;
        this._yWebsocketProvider = null;
        this._trans = options.translator;
        const user = options.user;
        user.ready
            .then(() => {
            this._onUserChanged(user);
        })
            .catch(e => console.error(e));
        user.userChanged.connect(this._onUserChanged, this);
        this._connect().catch(e => console.warn(e));
    }
    /**
     * Returns the awareness object within the shared model.
     */
    get awareness() {
        return this._sharedModel.awareness;
    }
    /**
     * Test whether the object has been disposed.
     */
    get isDisposed() {
        return this._isDisposed;
    }
    /**
     * Returns the **document widget** containing this provider's shared model.
     * Returns `null` if the document widget is not open (i.e. the tab was already
     * closed).
     */
    get parentDocumentWidget() {
        var _a;
        const shell = this._app.shell;
        // Iterate through all main area widgets
        for (const docWidget of shell.widgets()) {
            // Skip non-document widgets, i.e. widgets that aren't editing a file
            if (!(docWidget instanceof _jupyterlab_docregistry__WEBPACK_IMPORTED_MODULE_4__.DocumentWidget)) {
                continue;
            }
            // Skip widgets that don't contain a YFile / YNotebook
            const widget = docWidget.content;
            if (!(widget instanceof _jupyterlab_fileeditor__WEBPACK_IMPORTED_MODULE_5__.FileEditor || widget instanceof _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_6__.Notebook)) {
                continue;
            }
            // Return the document widget if found in this iteration
            // @ts-expect-error: TSC complains here, but reference equality checks are
            // always safe.
            if (((_a = widget.model) === null || _a === void 0 ? void 0 : _a.sharedModel) === this._sharedModel) {
                return docWidget;
            }
        }
        // If document widget was not found, return `null`.
        // This indicates that the tab containing this provider's shared model has
        // already been closed.
        return null;
    }
    /**
     * A promise that resolves when the document provider is ready.
     */
    get ready() {
        return this._ready.promise;
    }
    get contentType() {
        return this._contentType;
    }
    get format() {
        return this._format;
    }
    /**
     * Dispose of the resources held by the object.
     */
    dispose() {
        var _a, _b, _c;
        if (this.isDisposed) {
            return;
        }
        this._isDisposed = true;
        (_a = this._yWebsocketProvider) === null || _a === void 0 ? void 0 : _a.off('connection-close', this._onConnectionClosed);
        (_b = this._yWebsocketProvider) === null || _b === void 0 ? void 0 : _b.off('sync', this._onSync);
        (_c = this._yWebsocketProvider) === null || _c === void 0 ? void 0 : _c.destroy();
        this._disconnect();
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_2__.Signal.clearData(this);
    }
    async reconnect() {
        this._disconnect();
        this._connect();
    }
    /**
     * Gets the file ID for this path. This should only be called once when the
     * provider connects for the first time, because any future in-band moves may
     * cause `this._path` to not refer to the correct file.
     */
    async _getFileId() {
        let fileId = null;
        try {
            const resp = await (0,_requests__WEBPACK_IMPORTED_MODULE_7__.requestAPI)(`api/fileid/index?path=${this._path}`, {
                method: 'POST'
            });
            if (resp && 'id' in resp && typeof resp['id'] === 'string') {
                fileId = resp['id'];
            }
        }
        catch (e) {
            console.error(`Could not get file ID for path '${this._path}'.`);
            return null;
        }
        return fileId;
    }
    async _connect() {
        // Fetch file ID from the file ID service, if not cached
        if (!this._fileId) {
            this._fileId = await this._getFileId();
        }
        // If file ID could not be retrieved, show an error dialog asking for a bug
        // report, as this error is irrecoverable.
        if (!this._fileId) {
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showErrorMessage)(this._trans.__('File ID error'), `The file '${this._path}' cannot be opened because its file ID could not be retrieved. Please report this issue on GitHub.`, [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]);
            return;
        }
        // Otherwise, initialize the `YWebsocketProvider` to connect
        this._yWebsocketProvider = new y_websocket__WEBPACK_IMPORTED_MODULE_3__.WebsocketProvider(this._serverUrl, `${this._format}:${this._contentType}:${this._fileId}`, this._sharedModel.ydoc, {
            disableBc: true,
            // params: { sessionId: session.sessionId },
            awareness: this.awareness
        });
        this._yWebsocketProvider.on('sync', this._onSync);
        this._yWebsocketProvider.on('connection-close', this._onConnectionClosed);
    }
    get wsProvider() {
        return this._yWebsocketProvider;
    }
    _disconnect() {
        var _a, _b, _c;
        (_a = this._yWebsocketProvider) === null || _a === void 0 ? void 0 : _a.off('connection-close', this._onConnectionClosed);
        (_b = this._yWebsocketProvider) === null || _b === void 0 ? void 0 : _b.off('sync', this._onSync);
        (_c = this._yWebsocketProvider) === null || _c === void 0 ? void 0 : _c.destroy();
        this._yWebsocketProvider = null;
    }
    _onUserChanged(user) {
        this.awareness.setLocalStateField('user', user.identity);
    }
    /**
     * Handles an out-of-band change indicated by close code 4000. This requires
     * resetting the YDoc and re-connecting. A notification is emitted to the user
     * if the document widget containing the shared model is open & visible.
     */
    _handleOobChange() {
        // Reset YDoc
        // TODO: is it safe to assume that we only need YFile & YNotebook?
        const sharedModel = this._sharedModel;
        sharedModel.reset();
        // Re-connect
        this.reconnect();
        // Emit notification if document is open & visible to the user (i.e. the tab
        // exists & the content of that tab is being shown)
        const docWidget = this.parentDocumentWidget;
        if (docWidget && docWidget.isVisible) {
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.info(`The file '${this._path}' was modified on disk. The document tab has been reset.`, {
                autoClose: 10000
            });
        }
    }
    /**
     * Handles an out-of-band move/deletion indicated by close code 4001.
     *
     * This always stops the provider from reconnecting. If the parent document
     * widget is open, this method also closes the tab and emits a warning
     * notification to the user.
     *
     * No notification is emitted if the document isn't open, since the user does
     * not need to be notified.
     */
    _handleOobMove() {
        this._stopCloseAndNotify(`The file '${this._path}' no longer exists, and was either moved or deleted. The document tab has been closed.`);
    }
    /**
     * Handles an in-band deletion indicated by close code 4002. This behaves
     * similarly to `_handleOobMove()`, but with a different notification message.
     */
    _handleIbDeletion() {
        this._stopCloseAndNotify(`The file '${this._path}' was deleted. The document tab has been closed.`);
    }
    /**
     * Stops the provider from reconnecting. If the parent document widget is
     * open, this method also closes the tab and emits a warning notification to
     * the user with the given message.
     */
    _stopCloseAndNotify(message) {
        this._sharedModel.dispose();
        const documentWidget = this.parentDocumentWidget;
        if (documentWidget) {
            documentWidget.close();
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Notification.warning(message, {
                autoClose: 10000
            });
        }
    }
}


/***/ }),

/***/ "./lib/executionindicator.js":
/*!***********************************!*\
  !*** ./lib/executionindicator.js ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AwarenessExecutionIndicator: () => (/* binding */ AwarenessExecutionIndicator)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.




/**
 * A VDomRenderer widget for displaying the execution status.
 */
class AwarenessExecutionIndicator extends _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.VDomRenderer {
    /**
     * Construct the kernel status widget.
     */
    constructor(translator, showProgress = true) {
        super(new AwarenessExecutionIndicator.Model());
        this.translator = translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__.nullTranslator;
        this.addClass('jp-mod-highlighted');
    }
    /**
     * Render the execution status item.
     */
    render() {
        if (this.model === null || !this.model.renderFlag) {
            return react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null);
        }
        else {
            const nb = this.model.currentNotebook;
            if (!nb) {
                return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.ExecutionIndicatorComponent, { displayOption: this.model.displayOption, state: undefined, translator: this.translator }));
            }
            return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.ExecutionIndicatorComponent, { displayOption: this.model.displayOption, state: this.model.executionState(nb), translator: this.translator }));
        }
    }
}
(function (AwarenessExecutionIndicator) {
    class Model extends _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.ExecutionIndicator.Model {
        /**
         * A weak map to hold execution status of multiple notebooks.
         */
        // (this as any) casts are required to avoid
        // ts errors when accessing private methods
        attachNotebook(data) {
            var _a;
            const nb = data === null || data === void 0 ? void 0 : data.content;
            if (!nb) {
                return;
            }
            this._currentNotebook = nb;
            this._notebookExecutionProgress.set(nb, {
                executionStatus: 'idle',
                kernelStatus: 'idle',
                totalTime: 0,
                interval: 0,
                timeout: 0,
                scheduledCell: new Set(),
                scheduledCellNumber: 0,
                needReset: true
            });
            const state = this._notebookExecutionProgress.get(nb);
            const contextStatusChanged = (ctx) => {
                var _a;
                if (state) {
                    const awarenessStates = (_a = nb === null || nb === void 0 ? void 0 : nb.model) === null || _a === void 0 ? void 0 : _a.sharedModel.awareness.getStates();
                    if (awarenessStates) {
                        for (const [, clientState] of awarenessStates) {
                            if ('kernel' in clientState) {
                                state.kernelStatus = clientState['kernel']['execution_state'];
                                this.stateChanged.emit(void 0);
                                return;
                            }
                        }
                    }
                }
            };
            (_a = nb === null || nb === void 0 ? void 0 : nb.model) === null || _a === void 0 ? void 0 : _a.sharedModel.awareness.on('change', contextStatusChanged);
            super.attachNotebook(data);
        }
    }
    AwarenessExecutionIndicator.Model = Model;
})(AwarenessExecutionIndicator || (AwarenessExecutionIndicator = {}));


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, endPoint.startsWith('/') ? '' : 'jupyter-server-documents', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    const contentType = response.headers.get('Content-Type') || '';
    let data;
    // Read response text
    const responseText = await response.text();
    if (contentType.includes('application/x-ndjson')) {
        data = responseText
            .trim()
            .split('\n')
            .map(line => JSON.parse(line));
    }
    else if (responseText.length > 0) {
        try {
            data = JSON.parse(responseText);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   backupCellExecutorPlugin: () => (/* binding */ backupCellExecutorPlugin),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   executionIndicator: () => (/* binding */ executionIndicator),
/* harmony export */   kernelStatus: () => (/* binding */ kernelStatus),
/* harmony export */   plugin: () => (/* binding */ plugin),
/* harmony export */   rtcGlobalAwarenessPlugin: () => (/* binding */ rtcGlobalAwarenessPlugin)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _executionindicator__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./executionindicator */ "./lib/executionindicator.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _docprovider__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! ./docprovider */ "./lib/docprovider/filebrowser.js");
/* harmony import */ var _jupyterlab_statedb__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/statedb */ "webpack/sharing/consume/default/@jupyterlab/statedb");
/* harmony import */ var _jupyterlab_statedb__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statedb__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @jupyter/collaborative-drive */ "webpack/sharing/consume/default/@jupyter/collaborative-drive/@jupyter/collaborative-drive");
/* harmony import */ var _jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(_jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var yjs__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! yjs */ "webpack/sharing/consume/default/yjs");
/* harmony import */ var yjs__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(yjs__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var y_protocols_awareness__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! y-protocols/awareness */ "./node_modules/y-protocols/awareness.js");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_10___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_10__);
/* harmony import */ var _docprovider_awareness__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./docprovider/awareness */ "./lib/docprovider/awareness.js");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_11___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_11__);
/* harmony import */ var _kernelstatus__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! ./kernelstatus */ "./lib/kernelstatus.js");
/* harmony import */ var _codemirror_binding_plugin__WEBPACK_IMPORTED_MODULE_18__ = __webpack_require__(/*! ./codemirror-binding/plugin */ "./lib/codemirror-binding/plugin.js");
/* harmony import */ var _notebook_factory__WEBPACK_IMPORTED_MODULE_17__ = __webpack_require__(/*! ./notebook-factory */ "./lib/notebook-factory/plugin.js");





















/**
 * Initialization data for the @jupyter/server-documents extension.
 */
const plugin = {
    id: '@jupyter/server-documents:plugin',
    description: 'A JupyterLab extension that provides RTC capabilities.',
    autoStart: true,
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__.ISettingRegistry],
    activate: (app, settingRegistry) => {
        console.log('JupyterLab extension @jupyter/server-documents is activated!');
        if (settingRegistry) {
            settingRegistry
                .load(plugin.id)
                .then(settings => {
                console.log('@jupyter/server-documents settings loaded:', settings.composite);
            })
                .catch(reason => {
                console.error('Failed to load settings for @jupyter/server-documents.', reason);
            });
        }
        (0,_handler__WEBPACK_IMPORTED_MODULE_12__.requestAPI)('get-example')
            .then(data => {
            console.log(data);
        })
            .catch(reason => {
            console.error(`The jupyter_server_documents server extension appears to be missing.\n${reason}`);
        });
    }
};
/**
 * Jupyter plugin creating a global awareness for RTC.
 */
const rtcGlobalAwarenessPlugin = {
    id: '@jupyter/server-documents:rtc-global-awareness',
    description: 'Add global awareness to share working document of users.',
    requires: [_jupyterlab_statedb__WEBPACK_IMPORTED_MODULE_6__.IStateDB],
    provides: _jupyter_collaborative_drive__WEBPACK_IMPORTED_MODULE_7__.IGlobalAwareness,
    activate: (app, state) => {
        const { user } = app.serviceManager;
        const ydoc = new yjs__WEBPACK_IMPORTED_MODULE_8__.Doc();
        const awareness = new y_protocols_awareness__WEBPACK_IMPORTED_MODULE_9__.Awareness(ydoc);
        // TODO: Uncomment once global awareness is working
        const server = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_10__.ServerConnection.makeSettings();
        const url = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_11__.URLExt.join(server.wsUrl, 'api/collaboration/room');
        new _docprovider_awareness__WEBPACK_IMPORTED_MODULE_13__.WebSocketAwarenessProvider({
            url: url,
            roomID: 'JupyterLab:globalAwareness',
            awareness: awareness,
            user: user
        });
        state.changed.connect(async () => {
            var _a, _b;
            const data = await state.toJSON();
            const current = ((_b = (_a = data['layout-restorer:data']) === null || _a === void 0 ? void 0 : _a.main) === null || _b === void 0 ? void 0 : _b.current) || '';
            // For example matches `notebook:Untitled.ipynb` or `editor:untitled.txt`,
            // but not when in launcher or terminal.
            if (current.match(/^\w+:.+/)) {
                awareness.setLocalStateField('current', current);
            }
            else {
                awareness.setLocalStateField('current', null);
            }
        });
        return awareness;
    }
};
class AwarenessExecutionIndicatorIcon {
    createNew(panel) {
        const item = new _executionindicator__WEBPACK_IMPORTED_MODULE_14__.AwarenessExecutionIndicator();
        const nb = panel.content;
        item.model.attachNotebook({ content: nb });
        panel.toolbar.insertAfter('kernelName', 'awarenessExecutionProgress', item);
        return item;
    }
}
/**
 * A plugin that provides a execution indicator item to the status bar.
 */
const executionIndicator = {
    id: '@jupyter/server-documents:awareness-execution-indicator',
    description: 'Adds a notebook execution status widget.',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.INotebookTracker, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILabShell, _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4__.ITranslator, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.IToolbarWidgetRegistry],
    optional: [_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_3__.IStatusBar, _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__.ISettingRegistry],
    activate: (app, notebookTracker, labShell, translator, statusBar, settingRegistry, toolbarRegistry) => {
        console.log('JupyterLab extension activated: Awareness Execution Indicator');
        app.docRegistry.addWidgetExtension('Notebook', new AwarenessExecutionIndicatorIcon());
    }
};
/**
 * A plugin that provides a kernel status item to the status bar.
 */
const kernelStatus = {
    id: '@jupyter/server-documents:awareness-kernel-status',
    description: 'Provides the kernel status indicator model.',
    autoStart: true,
    requires: [_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_3__.IStatusBar],
    provides: _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.IKernelStatusModel,
    optional: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ISessionContextDialogs, _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4__.ITranslator, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILabShell],
    activate: (app, statusBar, sessionDialogs_, translator_, labShell) => {
        console.log('JupyterLab extension activated: Awareness Kernel Status Indicator');
        const translator = translator_ !== null && translator_ !== void 0 ? translator_ : _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4__.nullTranslator;
        const sessionDialogs = sessionDialogs_ !== null && sessionDialogs_ !== void 0 ? sessionDialogs_ : new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.SessionContextDialogs({ translator });
        // When the status item is clicked, launch the kernel
        // selection dialog for the current session.
        const changeKernel = async () => {
            if (!item.model.sessionContext) {
                return;
            }
            await sessionDialogs.selectKernel(item.model.sessionContext);
        };
        const changeKernelOnKeyDown = async (event) => {
            if (event.key === 'Enter' ||
                event.key === 'Spacebar' ||
                event.key === ' ') {
                event.preventDefault();
                event.stopPropagation();
                return changeKernel();
            }
        };
        // Create the status item.
        const item = new _kernelstatus__WEBPACK_IMPORTED_MODULE_15__.AwarenessKernelStatus({ onClick: changeKernel, onKeyDown: changeKernelOnKeyDown }, translator);
        const providers = new Set();
        const addSessionProvider = (provider) => {
            providers.add(provider);
            if (app.shell.currentWidget) {
                updateSession(app.shell, {
                    newValue: app.shell.currentWidget,
                    oldValue: null
                });
            }
        };
        function updateSession(shell, changes) {
            var _a;
            const { oldValue, newValue } = changes;
            // Clean up after the old value if it exists,
            // listen for changes to the title of the activity
            if (oldValue) {
                oldValue.title.changed.disconnect(onTitleChanged);
            }
            item.model.attachDocument(newValue);
            item.model.sessionContext =
                (_a = [...providers]
                    .map(provider => provider(changes.newValue))
                    .filter(session => session !== null)[0]) !== null && _a !== void 0 ? _a : null;
            if (newValue && item.model.sessionContext) {
                onTitleChanged(newValue.title);
                newValue.title.changed.connect(onTitleChanged);
            }
        }
        // When the title of the active widget changes, update the label
        // of the hover text.
        const onTitleChanged = (title) => {
            item.model.activityName = title.label;
        };
        if (labShell) {
            labShell.currentChanged.connect(updateSession);
        }
        statusBar.registerStatusItem(kernelStatus.id, {
            priority: 1,
            item,
            align: 'left',
            rank: 1,
            isActive: () => true
        });
        return { addSessionProvider };
    }
};
/**
 * Notebook cell executor plugin, provided by JupyterLab by default. Re-provided
 * to ensure compatibility with `jupyter_collaboration`.
 *
 * The `@jupyter/docprovider-extension` disables this plugin to override it, but
 * we disable that labextension, leaving `INotebookCellExecutor` un-implemented.
 * This plugin fixes that issue by re-providing this plugin with `autoStart:
 * false`, which specifies that this plugin only gets activated if no other
 * implementation exists, e.g. only when `jupyter_collaboration` is installed.
 */
const backupCellExecutorPlugin = {
    id: '@jupyter/server-documents:backup-cell-executor',
    description: 'Provides a backup default implementation of the notebook cell executor.',
    autoStart: false,
    provides: _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.INotebookCellExecutor,
    activate: () => {
        return Object.freeze({ runCell: _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.runCell });
    }
};
const plugins = [
    _docprovider__WEBPACK_IMPORTED_MODULE_16__.rtcContentProvider,
    _docprovider__WEBPACK_IMPORTED_MODULE_16__.yfile,
    _docprovider__WEBPACK_IMPORTED_MODULE_16__.ynotebook,
    _docprovider__WEBPACK_IMPORTED_MODULE_16__.logger,
    rtcGlobalAwarenessPlugin,
    plugin,
    executionIndicator,
    kernelStatus,
    _notebook_factory__WEBPACK_IMPORTED_MODULE_17__.notebookFactoryPlugin,
    _codemirror_binding_plugin__WEBPACK_IMPORTED_MODULE_18__.codemirrorYjsPlugin,
    backupCellExecutorPlugin
];
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugins);


/***/ }),

/***/ "./lib/kernelstatus.js":
/*!*****************************!*\
  !*** ./lib/kernelstatus.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AwarenessKernelStatus: () => (/* binding */ AwarenessKernelStatus)
/* harmony export */ });
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/statusbar */ "webpack/sharing/consume/default/@jupyterlab/statusbar");
/* harmony import */ var _jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.





/**
 * A pure functional component for rendering kernel status.
 */
function KernelStatusComponent(props) {
    const translator = props.translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__.nullTranslator;
    const trans = translator.load('jupyterlab');
    let statusText = '';
    if (props.status) {
        statusText = ` | ${props.status}`;
    }
    return (react__WEBPACK_IMPORTED_MODULE_3___default().createElement(_jupyterlab_statusbar__WEBPACK_IMPORTED_MODULE_0__.TextItem, { onClick: props.handleClick, onKeyDown: props.handleKeyDown, source: `${props.kernelName}${statusText}`, title: trans.__('Change kernel for %1', props.activityName), tabIndex: 0 }));
}
class AwarenessKernelStatus extends _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.VDomRenderer {
    /**
     * Construct the kernel status widget.
     */
    constructor(opts, translator) {
        super(new AwarenessKernelStatus.Model(translator));
        this.translator = translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__.nullTranslator;
        this._handleClick = opts.onClick;
        this._handleKeyDown = opts.onKeyDown;
        this.addClass('jp-mod-highlighted');
    }
    /**
     * Render the kernel status item.
     */
    render() {
        if (this.model === null) {
            return null;
        }
        else {
            return (react__WEBPACK_IMPORTED_MODULE_3___default().createElement(KernelStatusComponent, { status: this.model.status, kernelName: this.model.kernelName, activityName: this.model.activityName, handleClick: this._handleClick, handleKeyDown: this._handleKeyDown, translator: this.translator }));
        }
    }
}
(function (AwarenessKernelStatus) {
    class Model extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_4__.KernelStatus.Model {
        attachDocument(widget) {
            var _a;
            if (!widget) {
                return;
            }
            const panel = widget;
            const stateChanged = () => {
                var _a;
                if (this) {
                    const awarenessStates = (_a = panel === null || panel === void 0 ? void 0 : panel.model) === null || _a === void 0 ? void 0 : _a.sharedModel.awareness.getStates();
                    if (awarenessStates) {
                        for (const [, clientState] of awarenessStates) {
                            if ('kernel' in clientState) {
                                this._kernelStatus =
                                    clientState['kernel']['execution_state'];
                                this.stateChanged.emit(void 0);
                                return;
                            }
                        }
                    }
                }
            };
            (_a = panel.model) === null || _a === void 0 ? void 0 : _a.sharedModel.awareness.on('change', stateChanged);
        }
        set sessionContext(sessionContext) {
            var _a;
            const oldState = this._getAllState();
            this._sessionContext = sessionContext;
            this._kernelName =
                (_a = sessionContext === null || sessionContext === void 0 ? void 0 : sessionContext.kernelDisplayName) !== null && _a !== void 0 ? _a : this._trans.__('No Kernel');
            this._triggerChange(oldState, this._getAllState());
            sessionContext === null || sessionContext === void 0 ? void 0 : sessionContext.kernelChanged.connect(this._onKernelDisplayNameChanged, this);
        }
        /**
         * React to changes in the kernel.
         */
        _onKernelDisplayNameChanged(_sessionContext, change) {
            const oldState = this._getAllState();
            // sync setting of status and display name
            this._kernelName = _sessionContext.kernelDisplayName;
            this._triggerChange(oldState, this._getAllState());
        }
    }
    AwarenessKernelStatus.Model = Model;
})(AwarenessKernelStatus || (AwarenessKernelStatus = {}));


/***/ }),

/***/ "./lib/notebook-factory/notebook-factory.js":
/*!**************************************************!*\
  !*** ./lib/notebook-factory/notebook-factory.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   RtcNotebookContentFactory: () => (/* binding */ RtcNotebookContentFactory)
/* harmony export */ });
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/cells */ "webpack/sharing/consume/default/@jupyterlab/cells");
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyter_ydoc__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyter/ydoc */ "webpack/sharing/consume/default/@jupyter/ydoc");
/* harmony import */ var _jupyter_ydoc__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyter_ydoc__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/outputarea */ "webpack/sharing/consume/default/@jupyterlab/outputarea");
/* harmony import */ var _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _notebook__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./notebook */ "./lib/notebook-factory/notebook.js");






const globalModelDBMutex = (0,_jupyter_ydoc__WEBPACK_IMPORTED_MODULE_2__.createMutex)();
/**
 * The class name added to the cell when dirty.
 */
const DIRTY_CLASS = 'jp-mod-dirty';
_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_0__.CodeCellModel.prototype._onSharedModelChanged = function (slot, change) {
    if (change.streamOutputChange) {
        globalModelDBMutex(() => {
            for (const streamOutputChange of change.streamOutputChange) {
                if ('delete' in streamOutputChange) {
                    this._outputs.removeStreamOutput(streamOutputChange.delete);
                }
                if ('insert' in streamOutputChange) {
                    this._outputs.appendStreamOutput(streamOutputChange.insert.toString());
                }
            }
        });
    }
    if (change.outputsChange) {
        globalModelDBMutex(() => {
            var _a;
            let retain = 0;
            for (const outputsChange of change.outputsChange) {
                if ('retain' in outputsChange) {
                    retain += outputsChange.retain;
                }
                if ('delete' in outputsChange) {
                    for (let i = 0; i < outputsChange.delete; i++) {
                        this._outputs.remove(retain);
                    }
                }
                if ('insert' in outputsChange) {
                    // Inserting an output always results in appending it.
                    for (const output of outputsChange.insert) {
                        // For compatibility with older ydoc where a plain object,
                        // (rather than a Map instance) could be provided.
                        // In a future major release the use of Map will be required.
                        if ('toJSON' in output) {
                            const json = output.toJSON();
                            if ((_a = json.metadata) === null || _a === void 0 ? void 0 : _a.url) {
                                // fetch the output from ouputs service
                                (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)(json.metadata.url).then(data => {
                                    this._outputs.add(data);
                                });
                            }
                            else {
                                this._outputs.add(json);
                            }
                        }
                        else {
                            this._outputs.add(output);
                        }
                    }
                }
            }
        });
    }
    if (change.executionCountChange) {
        if (change.executionCountChange.newValue &&
            (this.isDirty || !change.executionCountChange.oldValue)) {
            this._setDirty(false);
        }
        this.stateChanged.emit({
            name: 'executionCount',
            oldValue: change.executionCountChange.oldValue,
            newValue: change.executionCountChange.newValue
        });
    }
    if (change.executionStateChange) {
        this.stateChanged.emit({
            name: 'executionState',
            oldValue: change.executionStateChange.oldValue,
            newValue: change.executionStateChange.newValue
        });
    }
    if (change.sourceChange && this.executionCount !== null) {
        this._setDirty(this._executedCode !== this.sharedModel.getSource().trim());
    }
};
_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_0__.CodeCellModel.prototype.onOutputsChange = function (sender, event) {
    // no-op
};
/* An OutputAreaModel that loads outputs from outputs service */
class RtcOutputAreaModel extends _jupyterlab_outputarea__WEBPACK_IMPORTED_MODULE_3__.OutputAreaModel {
    constructor(options = {}) {
        var _a, _b;
        super({ ...options, values: [] }); // Don't pass values to OutputAreaModel
        if ((_a = options.values) === null || _a === void 0 ? void 0 : _a.length) {
            const firstValue = options.values[0];
            if ((_b = firstValue.metadata) === null || _b === void 0 ? void 0 : _b.url) {
                let outputsUrl = firstValue.metadata.url;
                // Skip the last section with *.output
                outputsUrl = outputsUrl.substring(0, outputsUrl.lastIndexOf('/'));
                (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)(outputsUrl)
                    .then(outputs => {
                    outputs.forEach((output) => {
                        if (!this.isDisposed) {
                            const index = this._add(output) - 1;
                            const item = this.list.get(index);
                            item.changed.connect(this._onGenericChange, this);
                        }
                    });
                })
                    .catch(error => {
                    console.error('Error fetching output:', error);
                });
            }
            else {
                options.values.forEach((output) => {
                    if (!this.isDisposed) {
                        const index = this._add(output) - 1;
                        const item = this.list.get(index);
                        item.changed.connect(this._onGenericChange, this);
                    }
                });
            }
        }
    }
}
/**
 * NOTE: We should upstream this fix. This is a bug in JupyterLab.
 *
 * The execution count comes back from the kernel immediately
 * when the execute request is made by the client, even thought
 * cell might still be running. JupyterLab holds this value in
 * memory with a Promise to set it later, once the execution
 * state goes back to Idle.
 *
 * In CRDT world, we don't need to do this gymnastics, holding
 * the state in a Promise. Instead, we can just watch the
 * executionState and executionCount in the CRDT being maintained
 * by the server-side model.
 *
 * This is a big win! It means user can close and re-open a
 * notebook while a list of executed cells are queued.
 */
_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_0__.CodeCell.prototype.onStateChanged = function (model, args) {
    switch (args.name) {
        case 'executionCount':
            // NOTE: This code should not be here. It's a bandaid
            // fix because executionState and executionCount
            // aren't handled in a single message without CRDT/YNotebook.
            // if (args.newValue !== null) {
            //   // Mark execution state if execution count was set.
            //   this.model.executionState = 'idle';
            // }
            this._updatePrompt();
            break;
        case 'executionState':
            this._updatePrompt();
            break;
        case 'isDirty':
            if (model.isDirty) {
                this.addClass(DIRTY_CLASS);
            }
            else {
                this.removeClass(DIRTY_CLASS);
            }
            break;
        default:
            break;
    }
};
_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_0__.CodeCellModel.ContentFactory.prototype.createOutputArea = function (options) {
    return new RtcOutputAreaModel(options);
};
class RtcNotebookContentFactory extends _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.NotebookPanel.ContentFactory {
    createCodeCell(options) {
        return new _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_0__.CodeCell(options).initializeState();
    }
    createNotebook(options) {
        return new _notebook__WEBPACK_IMPORTED_MODULE_5__.ResettableNotebook(options);
    }
}


/***/ }),

/***/ "./lib/notebook-factory/notebook.js":
/*!******************************************!*\
  !*** ./lib/notebook-factory/notebook.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ResettableNotebook: () => (/* binding */ ResettableNotebook)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);

/**
 * A custom implementation of `Notebook` that resets the notebook to an empty
 * state when `YNotebook.resetSignal` is emitted to.
 *
 * This requires the custom `YNotebook` class defined by this labextension.
 */
class ResettableNotebook extends _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.Notebook {
    constructor(options) {
        super(options);
        this._resetSignalSlot = () => this._onReset();
    }
    get model() {
        return super.model;
    }
    set model(newModel) {
        // if there is an existing model, remove the `resetSignal` observer
        const oldModel = this.model;
        if (oldModel) {
            const ynotebook = oldModel.sharedModel;
            ynotebook.resetSignal.disconnect(this._resetSignalSlot);
        }
        // call parent property setter
        super.model = newModel;
        // return early if `newValue === null`
        if (!newModel) {
            return;
        }
        // otherwise, listen to `YNotebook.resetSignal`.
        const ynotebook = newModel.sharedModel;
        ynotebook.resetSignal.connect(this._resetSignalSlot);
    }
    /**
     * Function called when the YDoc has been reset. This simply refreshes the UI
     * to reflect the new YDoc state.
     */
    _onReset() {
        if (!this.model) {
            console.warn('The notebook was reset without a model. This should never happen.');
            return;
        }
        // Refresh the UI by emitting to the `modelContentChanged` signal
        this.onModelContentChanged(this.model);
    }
}


/***/ }),

/***/ "./lib/notebook-factory/plugin.js":
/*!****************************************!*\
  !*** ./lib/notebook-factory/plugin.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   notebookFactoryPlugin: () => (/* binding */ notebookFactoryPlugin)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/codeeditor */ "webpack/sharing/consume/default/@jupyterlab/codeeditor");
/* harmony import */ var _jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _notebook_factory__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./notebook-factory */ "./lib/notebook-factory/notebook-factory.js");



/**
 * Custom `Notebook` factory plugin.
 */
const notebookFactoryPlugin = {
    id: '@jupyter/server-documents:notebook-factory',
    description: 'Provides the notebook cell factory.',
    provides: _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookPanel.IContentFactory,
    requires: [_jupyterlab_codeeditor__WEBPACK_IMPORTED_MODULE_1__.IEditorServices],
    autoStart: true,
    activate: (app, editorServices) => {
        const editorFactory = editorServices.factoryService.newInlineEditor;
        return new _notebook_factory__WEBPACK_IMPORTED_MODULE_2__.RtcNotebookContentFactory({ editorFactory });
    }
};


/***/ })

}]);
//# sourceMappingURL=lib_index_js.5503e53129a70bb2b389.js.map