var Bn = Object.defineProperty;
var Fn = (e, t, n) => t in e ? Bn(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var $ = (e, t, n) => Fn(e, typeof t != "symbol" ? t + "" : t, n);
import * as Un from "vue";
import { unref as W, watch as G, nextTick as ke, isRef as Gt, ref as Q, shallowRef as H, watchEffect as zt, computed as L, toRaw as qt, customRef as se, toValue as Qe, readonly as Hn, provide as ve, inject as J, shallowReactive as Kn, defineComponent as j, reactive as Gn, h as x, getCurrentInstance as Qt, renderList as zn, TransitionGroup as Jt, normalizeStyle as qn, normalizeClass as Ne, toDisplayString as Ae, cloneVNode as Je, vModelDynamic as Qn, vShow as Jn, withDirectives as Yn, resolveDynamicComponent as Xn, normalizeProps as Zn, onErrorCaptured as er, openBlock as ge, createElementBlock as me, createElementVNode as tr, createVNode as nr, createCommentVNode as rr, Fragment as or, KeepAlive as sr } from "vue";
let Yt;
function ir(e) {
  Yt = e;
}
function Ye() {
  return Yt;
}
function Ve() {
  const { queryPath: e, pathParams: t, queryParams: n } = Ye();
  return {
    path: e,
    ...t === void 0 ? {} : { params: t },
    ...n === void 0 ? {} : { queryParams: n }
  };
}
const dt = /* @__PURE__ */ new Map();
function ar(e) {
  var t;
  (t = e.scopes) == null || t.forEach((n) => {
    dt.set(n.id, n);
  });
}
function Ue(e) {
  return dt.get(e);
}
function Re(e) {
  return e && dt.has(e);
}
function de(e) {
  return typeof e == "function" ? e() : W(e);
}
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const Xe = () => {
};
function Ze(e, t = !1, n = "Timeout") {
  return new Promise((r, o) => {
    setTimeout(t ? () => o(n) : r, e);
  });
}
function et(e, t = !1) {
  function n(u, { flush: f = "sync", deep: h = !1, timeout: m, throwOnTimeout: g } = {}) {
    let v = null;
    const E = [new Promise((R) => {
      v = G(
        e,
        (C) => {
          u(C) !== t && (v ? v() : ke(() => v == null ? void 0 : v()), R(C));
        },
        {
          flush: f,
          deep: h,
          immediate: !0
        }
      );
    })];
    return m != null && E.push(
      Ze(m, g).then(() => de(e)).finally(() => v == null ? void 0 : v())
    ), Promise.race(E);
  }
  function r(u, f) {
    if (!Gt(u))
      return n((C) => C === u, f);
    const { flush: h = "sync", deep: m = !1, timeout: g, throwOnTimeout: v } = f ?? {};
    let _ = null;
    const R = [new Promise((C) => {
      _ = G(
        [e, u],
        ([M, U]) => {
          t !== (M === U) && (_ ? _() : ke(() => _ == null ? void 0 : _()), C(M));
        },
        {
          flush: h,
          deep: m,
          immediate: !0
        }
      );
    })];
    return g != null && R.push(
      Ze(g, v).then(() => de(e)).finally(() => (_ == null || _(), de(e)))
    ), Promise.race(R);
  }
  function o(u) {
    return n((f) => !!f, u);
  }
  function s(u) {
    return r(null, u);
  }
  function i(u) {
    return r(void 0, u);
  }
  function a(u) {
    return n(Number.isNaN, u);
  }
  function l(u, f) {
    return n((h) => {
      const m = Array.from(h);
      return m.includes(u) || m.includes(de(u));
    }, f);
  }
  function d(u) {
    return c(1, u);
  }
  function c(u = 1, f) {
    let h = -1;
    return n(() => (h += 1, h >= u), f);
  }
  return Array.isArray(de(e)) ? {
    toMatch: n,
    toContains: l,
    changed: d,
    changedTimes: c,
    get not() {
      return et(e, !t);
    }
  } : {
    toMatch: n,
    toBe: r,
    toBeTruthy: o,
    toBeNull: s,
    toBeNaN: a,
    toBeUndefined: i,
    changed: d,
    changedTimes: c,
    get not() {
      return et(e, !t);
    }
  };
}
function cr(e) {
  return et(e);
}
function ur(e, t, n) {
  let r;
  Gt(n) ? r = {
    evaluating: n
  } : r = n || {};
  const {
    lazy: o = !1,
    evaluating: s = void 0,
    shallow: i = !0,
    onError: a = Xe
  } = r, l = Q(!o), d = i ? H(t) : Q(t);
  let c = 0;
  return zt(async (u) => {
    if (!l.value)
      return;
    c++;
    const f = c;
    let h = !1;
    s && Promise.resolve().then(() => {
      s.value = !0;
    });
    try {
      const m = await e((g) => {
        u(() => {
          s && (s.value = !1), h || g();
        });
      });
      f === c && (d.value = m);
    } catch (m) {
      a(m);
    } finally {
      s && f === c && (s.value = !1), h = !0;
    }
  }), o ? L(() => (l.value = !0, d.value)) : d;
}
function lr(e, t, n) {
  const {
    immediate: r = !0,
    delay: o = 0,
    onError: s = Xe,
    onSuccess: i = Xe,
    resetOnExecute: a = !0,
    shallow: l = !0,
    throwError: d
  } = {}, c = l ? H(t) : Q(t), u = Q(!1), f = Q(!1), h = H(void 0);
  async function m(_ = 0, ...E) {
    a && (c.value = t), h.value = void 0, u.value = !1, f.value = !0, _ > 0 && await Ze(_);
    const R = typeof e == "function" ? e(...E) : e;
    try {
      const C = await R;
      c.value = C, u.value = !0, i(C);
    } catch (C) {
      if (h.value = C, s(C), d)
        throw C;
    } finally {
      f.value = !1;
    }
    return c.value;
  }
  r && m(o);
  const g = {
    state: c,
    isReady: u,
    isLoading: f,
    error: h,
    execute: m
  };
  function v() {
    return new Promise((_, E) => {
      cr(f).toBe(!1).then(() => _(g)).catch(E);
    });
  }
  return {
    ...g,
    then(_, E) {
      return v().then(_, E);
    }
  };
}
function D(e, t) {
  t = t || {};
  const n = [...Object.keys(t), "__Vue"], r = [...Object.values(t), Un];
  try {
    return new Function(...n, `return (${e})`)(...r);
  } catch (o) {
    throw new Error(o + " in function code: " + e);
  }
}
function fr(e) {
  if (e.startsWith(":")) {
    e = e.slice(1);
    try {
      return D(e);
    } catch (t) {
      throw new Error(t + " in function code: " + e);
    }
  }
}
function Xt(e) {
  return e.constructor.name === "AsyncFunction";
}
class dr {
  toString() {
    return "";
  }
}
const Ee = new dr();
function be(e) {
  return qt(e) === Ee;
}
function hr(e) {
  return Array.isArray(e) && e[0] === "bind";
}
function pr(e) {
  return e[1];
}
function Zt(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...s] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + s[0];
      case "~+":
        return s[0] + e;
    }
  }
  const r = en(t, n);
  return e[r];
}
function en(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      if (!t)
        throw new Error("No bindable function provided");
      return t(r[0]);
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function tn(e, t, n) {
  return t.reduce(
    (r, o) => Zt(r, o, n),
    e
  );
}
function nn(e, t, n, r) {
  t.reduce((o, s, i) => {
    if (i === t.length - 1)
      o[en(s, r)] = n;
    else
      return Zt(o, s, r);
  }, e);
}
function gr(e, t, n) {
  const { paths: r, getBindableValueFn: o } = t, { paths: s, getBindableValueFn: i } = t;
  return r === void 0 || r.length === 0 ? e : se(() => ({
    get() {
      try {
        return tn(
          Qe(e),
          r,
          o
        );
      } catch {
        return;
      }
    },
    set(a) {
      nn(
        Qe(e),
        s || r,
        a,
        i
      );
    }
  }));
}
function ht(e) {
  return se((t, n) => ({
    get() {
      return t(), e;
    },
    set(r) {
      !be(e) && JSON.stringify(r) === JSON.stringify(e) || (e = r, n());
    }
  }));
}
function mr(e, t) {
  const { deepCompare: n = !1 } = e;
  return n ? ht(e.value) : Q(e.value);
}
function vr(e, t, n) {
  const { bind: r = {}, code: o, const: s = [] } = e, i = Object.values(r).map((c, u) => s[u] === 1 ? c : t.getVueRefObject(c));
  if (Xt(new Function(o)))
    return ur(
      async () => {
        const c = Object.fromEntries(
          Object.keys(r).map((u, f) => [u, i[f]])
        );
        return await D(o, c)();
      },
      null,
      { lazy: !0 }
    );
  const a = Object.fromEntries(
    Object.keys(r).map((c, u) => [c, i[u]])
  ), l = D(o, a);
  return L(l);
}
function yr(e) {
  const { init: t, deepEqOnInput: n } = e;
  return n === void 0 ? H(t ?? Ee) : ht(t ?? Ee);
}
function wr(e, t, n) {
  const {
    inputs: r = [],
    code: o,
    slient: s,
    data: i,
    asyncInit: a = null,
    deepEqOnInput: l = 0
  } = e, d = s || Array(r.length).fill(0), c = i || Array(r.length).fill(0), u = r.filter((v, _) => d[_] === 0 && c[_] === 0).map((v) => t.getVueRefObject(v));
  function f() {
    return r.map(
      (v, _) => c[_] === 1 ? v : t.getValue(v)
    );
  }
  const h = D(o), m = l === 0 ? H(Ee) : ht(Ee), g = { immediate: !0, deep: !0 };
  return Xt(h) ? (m.value = a, G(
    u,
    async () => {
      f().some(be) || (m.value = await h(...f()));
    },
    g
  )) : G(
    u,
    () => {
      const v = f();
      v.some(be) || (m.value = h(...v));
    },
    g
  ), Hn(m);
}
function _r(e) {
  return e.tag === "vfor";
}
function Er(e) {
  return e.tag === "vif";
}
function br(e) {
  return e.tag === "match";
}
function rn(e) {
  return !("type" in e);
}
function Rr(e) {
  return "type" in e && e.type === "rp";
}
function pt(e) {
  return "sid" in e && "id" in e;
}
class Pr extends Map {
  constructor(t) {
    super(), this.factory = t;
  }
  getOrDefault(t) {
    if (!this.has(t)) {
      const n = this.factory();
      return this.set(t, n), n;
    }
    return super.get(t);
  }
}
function on(e) {
  return new Pr(e);
}
class Sr {
  async eventSend(t, n) {
    const { fType: r, hKey: o, key: s } = t, i = Ye().webServerInfo, a = s !== void 0 ? { key: s } : {}, l = r === "sync" ? i.event_url : i.event_async_url;
    let d = {};
    const c = await fetch(l, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        bind: n,
        hKey: o,
        ...a,
        page: Ve(),
        ...d
      })
    });
    if (!c.ok)
      throw new Error(`HTTP error! status: ${c.status}`);
    return await c.json();
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, o = Ye().webServerInfo, s = n === "sync" ? o.watch_url : o.watch_async_url, i = t.getServerInputs(), a = {
      key: r,
      input: i,
      page: Ve()
    };
    return await (await fetch(s, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(a)
    })).json();
  }
}
class Or {
  async eventSend(t, n) {
    const { fType: r, hKey: o, key: s } = t, i = s !== void 0 ? { key: s } : {};
    let a = {};
    const l = {
      bind: n,
      fType: r,
      hKey: o,
      ...i,
      page: Ve(),
      ...a
    };
    return await window.pywebview.api.event_call(l);
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, o = t.getServerInputs(), s = {
      key: r,
      input: o,
      fType: n,
      page: Ve()
    };
    return await window.pywebview.api.watch_call(s);
  }
}
let tt;
function kr(e) {
  switch (e) {
    case "web":
      tt = new Sr();
      break;
    case "webview":
      tt = new Or();
      break;
  }
}
function sn() {
  return tt;
}
var K = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.EventContext = 1] = "EventContext", e[e.Data = 2] = "Data", e[e.JsFn = 3] = "JsFn", e))(K || {}), nt = /* @__PURE__ */ ((e) => (e.const = "c", e.ref = "r", e.range = "n", e))(nt || {}), ye = /* @__PURE__ */ ((e) => (e[e.Ref = 0] = "Ref", e[e.RouterAction = 1] = "RouterAction", e[e.ElementRefAction = 2] = "ElementRefAction", e))(ye || {});
function Nr(e, t) {
  const r = {
    ref: {
      id: t.id,
      sid: e
    },
    type: ye.Ref
  };
  return {
    ...t,
    immediate: !0,
    outputs: [r, ...t.outputs || []]
  };
}
function an(e) {
  const { config: t, varGetter: n } = e;
  if (!t)
    return {
      run: () => {
      },
      tryReset: () => {
      }
    };
  const r = t.map((i) => {
    const a = n.getVueRefObject(i.target);
    return i.type === "const" ? {
      refObj: a,
      preValue: a.value,
      newValue: i.value,
      reset: !0
    } : Vr(a, i, n);
  });
  return {
    run: () => {
      r.forEach((i) => {
        i.newValue !== i.preValue && (i.refObj.value = i.newValue);
      });
    },
    tryReset: () => {
      r.forEach((i) => {
        i.reset && (i.refObj.value = i.preValue);
      });
    }
  };
}
function Vr(e, t, n) {
  const r = D(t.code), o = t.inputs.map((s) => n.getValue(s));
  return {
    refObj: e,
    preValue: e.value,
    reset: t.reset ?? !0,
    newValue: r(...o)
  };
}
function Rt(e) {
  return e == null;
}
function $e(e, t, n) {
  if (Rt(t) || Rt(e.values))
    return;
  t = t;
  const r = e.values, o = e.types ?? Array.from({ length: t.length }).fill(0);
  t.forEach((s, i) => {
    const a = o[i];
    if (a === 1)
      return;
    if (s.type === ye.Ref) {
      if (a === 2) {
        r[i].forEach(([c, u]) => {
          const f = s.ref, h = {
            ...f,
            path: [...f.path ?? [], ...c]
          };
          n.updateValue(h, u);
        });
        return;
      }
      n.updateValue(s.ref, r[i]);
      return;
    }
    if (s.type === ye.RouterAction) {
      const d = r[i], c = n.getRouter()[d.fn];
      c(...d.args);
      return;
    }
    if (s.type === ye.ElementRefAction) {
      const d = s.ref, c = n.getVueRefObject(d).value, u = r[i], { method: f, args: h = [] } = u;
      c[f](...h);
      return;
    }
    const l = n.getVueRefObject(
      s.ref
    );
    l.value = r[i];
  });
}
function Cr(e) {
  const { watchConfigs: t, computedConfigs: n, varMapGetter: r, sid: o } = e;
  return new Ir(t, n, r, o);
}
class Ir {
  constructor(t, n, r, o) {
    $(this, "taskQueue", []);
    $(this, "id2TaskMap", /* @__PURE__ */ new Map());
    $(this, "input2TaskIdMap", on(() => []));
    this.varMapGetter = r;
    const s = [], i = (a) => {
      var d;
      const l = new Ar(a, r);
      return this.id2TaskMap.set(l.id, l), (d = a.inputs) == null || d.forEach((c, u) => {
        var h, m;
        if (((h = a.data) == null ? void 0 : h[u]) === 0 && ((m = a.slient) == null ? void 0 : m[u]) === 0) {
          if (!rn(c))
            throw new Error("Non-var input bindings are not supported.");
          const g = `${c.sid}-${c.id}`;
          this.input2TaskIdMap.getOrDefault(g).push(l.id);
        }
      }), l;
    };
    t == null || t.forEach((a) => {
      const l = i(a);
      s.push(l);
    }), n == null || n.forEach((a) => {
      const l = i(
        Nr(o, a)
      );
      s.push(l);
    }), s.forEach((a) => {
      const {
        deep: l = !0,
        once: d,
        flush: c,
        immediate: u = !0
      } = a.watchConfig, f = {
        immediate: u,
        deep: l,
        once: d,
        flush: c
      }, h = this._getWatchTargets(a);
      G(
        h,
        (m) => {
          m.some(be) || (a.modify = !0, this.taskQueue.push(new $r(a)), this._scheduleNextTick());
        },
        f
      );
    });
  }
  _getWatchTargets(t) {
    if (!t.watchConfig.inputs)
      return [];
    const n = t.slientInputs, r = t.constDataInputs;
    return t.watchConfig.inputs.filter(
      (s, i) => !r[i] && !n[i]
    ).map((s) => this.varMapGetter.getVueRefObject(s));
  }
  _scheduleNextTick() {
    ke(() => this._runAllTasks());
  }
  _runAllTasks() {
    const t = this.taskQueue.slice();
    this.taskQueue.length = 0, this._setTaskNodeRelations(t), t.forEach((n) => {
      n.run();
    });
  }
  _setTaskNodeRelations(t) {
    t.forEach((n) => {
      const r = this._findNextNodes(n, t);
      n.appendNextNodes(...r), r.forEach((o) => {
        o.appendPrevNodes(n);
      });
    });
  }
  _findNextNodes(t, n) {
    const r = t.watchTask.watchConfig.outputs;
    if (r && r.length <= 0)
      return [];
    const o = this._getCalculatorTasksByOutput(
      t.watchTask.watchConfig.outputs
    );
    return n.filter(
      (s) => o.has(s.watchTask.id) && s.watchTask.id !== t.watchTask.id
    );
  }
  _getCalculatorTasksByOutput(t) {
    const n = /* @__PURE__ */ new Set();
    return t == null || t.forEach((r) => {
      if (!pt(r.ref))
        throw new Error("Non-var output bindings are not supported.");
      const { sid: o, id: s } = r.ref, i = `${o}-${s}`;
      (this.input2TaskIdMap.get(i) || []).forEach((l) => n.add(l));
    }), n;
  }
}
class Ar {
  constructor(t, n) {
    $(this, "modify", !0);
    $(this, "_running", !1);
    $(this, "id");
    $(this, "_runningPromise", null);
    $(this, "_runningPromiseResolve", null);
    $(this, "_inputInfos");
    this.watchConfig = t, this.varMapGetter = n, this.id = Symbol(t.debug), this._inputInfos = this.createInputInfos();
  }
  createInputInfos() {
    const { inputs: t = [] } = this.watchConfig, n = this.watchConfig.data || Array.from({ length: t.length }).fill(0), r = this.watchConfig.slient || Array.from({ length: t.length }).fill(0);
    return {
      const_data: n,
      slients: r
    };
  }
  get slientInputs() {
    return this._inputInfos.slients;
  }
  get constDataInputs() {
    return this._inputInfos.const_data;
  }
  getServerInputs() {
    const { const_data: t } = this._inputInfos;
    return this.watchConfig.inputs ? this.watchConfig.inputs.map((n, r) => t[r] === 0 ? this.varMapGetter.getValue(n) : n) : [];
  }
  get running() {
    return this._running;
  }
  get runningPromise() {
    return this._runningPromise;
  }
  /**
   * setRunning
   */
  setRunning() {
    this._running = !0, this._runningPromise = new Promise((t) => {
      this._runningPromiseResolve = t;
    }), this._trySetRunningRef(!0);
  }
  /**
   * taskDone
   */
  taskDone() {
    this._running = !1, this._runningPromiseResolve && (this._runningPromiseResolve(), this._runningPromiseResolve = null), this._trySetRunningRef(!1);
  }
  _trySetRunningRef(t) {
    if (this.watchConfig.running) {
      const n = this.varMapGetter.getVueRefObject(
        this.watchConfig.running
      );
      n.value = t;
    }
  }
}
class $r {
  /**
   *
   */
  constructor(t) {
    $(this, "prevNodes", []);
    $(this, "nextNodes", []);
    $(this, "_runningPrev", !1);
    this.watchTask = t;
  }
  /**
   * appendPrevNodes
   */
  appendPrevNodes(...t) {
    this.prevNodes.push(...t);
  }
  /**
   *
   */
  appendNextNodes(...t) {
    this.nextNodes.push(...t);
  }
  /**
   * hasNextNodes
   */
  hasNextNodes() {
    return this.nextNodes.length > 0;
  }
  /**
   * run
   */
  async run() {
    if (this.prevNodes.length > 0 && !this._runningPrev)
      try {
        this._runningPrev = !0, await Promise.all(this.prevNodes.map((t) => t.run()));
      } finally {
        this._runningPrev = !1;
      }
    if (this.watchTask.running) {
      await this.watchTask.runningPromise;
      return;
    }
    if (this.watchTask.modify) {
      this.watchTask.modify = !1, this.watchTask.setRunning();
      try {
        await xr(this.watchTask);
      } finally {
        this.watchTask.taskDone();
      }
    }
  }
}
async function xr(e) {
  const { varMapGetter: t } = e, { outputs: n, preSetup: r } = e.watchConfig, o = an({
    config: r,
    varGetter: t
  });
  try {
    o.run();
    const s = await sn().watchSend(e);
    if (!s)
      return;
    $e(s, n, t);
  } finally {
    o.tryReset();
  }
}
function Pt(e, t) {
  Object.entries(e).forEach(([n, r]) => t(r, n));
}
function xe(e, t) {
  return cn(e, {
    valueFn: t
  });
}
function cn(e, t) {
  const { valueFn: n, keyFn: r } = t;
  return Object.fromEntries(
    Object.entries(e).map(([o, s], i) => [
      r ? r(o, s) : o,
      n(s, o, i)
    ])
  );
}
function Tr(e, t, n) {
  if (Array.isArray(t)) {
    const [o, ...s] = t;
    switch (o) {
      case "!":
        return !e;
      case "+":
        return e + s[0];
      case "~+":
        return s[0] + e;
    }
  }
  const r = Dr(t);
  return e[r];
}
function Dr(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      throw new Error("No bindable function provided");
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function jr(e, t, n) {
  return t.reduce(
    (r, o) => Tr(r, o),
    e
  );
}
function Mr(e, t) {
  return t ? t.reduce((n, r) => n[r], e) : e;
}
const Wr = window.structuredClone || ((e) => JSON.parse(JSON.stringify(e)));
function un(e) {
  return typeof e == "function" ? e : Wr(qt(e));
}
function Lr(e, t) {
  const {
    on: n,
    code: r,
    immediate: o,
    deep: s,
    once: i,
    flush: a,
    bind: l = {},
    onData: d,
    bindData: c
  } = e, u = d || Array.from({ length: n.length }).fill(0), f = c || Array.from({ length: Object.keys(l).length }).fill(0), h = xe(
    l,
    (v, _, E) => f[E] === 0 ? t.getVueRefObject(v) : v
  ), m = D(r, h), g = n.length === 1 ? St(u[0] === 1, n[0], t) : n.map(
    (v, _) => St(u[_] === 1, v, t)
  );
  return G(g, m, { immediate: o, deep: s, once: i, flush: a });
}
function St(e, t, n) {
  return e ? () => t : n.getVueRefObject(t);
}
function Br(e, t) {
  const {
    inputs: n = [],
    outputs: r,
    slient: o,
    data: s,
    code: i,
    immediate: a = !0,
    deep: l,
    once: d,
    flush: c
  } = e, u = o || Array.from({ length: n.length }).fill(0), f = s || Array.from({ length: n.length }).fill(0), h = D(i), m = n.filter((v, _) => u[_] === 0 && f[_] === 0).map((v) => t.getVueRefObject(v));
  function g() {
    return n.map((v, _) => f[_] === 0 ? un(t.getValue(v)) : v);
  }
  G(
    m,
    () => {
      let v = h(...g());
      if (!r)
        return;
      const E = r.length === 1 ? [v] : v, R = E.map((C) => C === void 0 ? 1 : 0);
      $e(
        {
          values: E,
          types: R
        },
        r,
        t
      );
    },
    { immediate: a, deep: l, once: d, flush: c }
  );
}
const rt = on(() => Symbol());
function Fr(e, t) {
  const n = e.sid, r = rt.getOrDefault(n);
  rt.set(n, r), ve(r, t);
}
function Ur(e) {
  const t = rt.get(e);
  return J(t);
}
function Hr() {
  return ln().__VUE_DEVTOOLS_GLOBAL_HOOK__;
}
function ln() {
  return typeof navigator < "u" && typeof window < "u" ? window : typeof globalThis < "u" ? globalThis : {};
}
const Kr = typeof Proxy == "function", Gr = "devtools-plugin:setup", zr = "plugin:settings:set";
let oe, ot;
function qr() {
  var e;
  return oe !== void 0 || (typeof window < "u" && window.performance ? (oe = !0, ot = window.performance) : typeof globalThis < "u" && (!((e = globalThis.perf_hooks) === null || e === void 0) && e.performance) ? (oe = !0, ot = globalThis.perf_hooks.performance) : oe = !1), oe;
}
function Qr() {
  return qr() ? ot.now() : Date.now();
}
class Jr {
  constructor(t, n) {
    this.target = null, this.targetQueue = [], this.onQueue = [], this.plugin = t, this.hook = n;
    const r = {};
    if (t.settings)
      for (const i in t.settings) {
        const a = t.settings[i];
        r[i] = a.defaultValue;
      }
    const o = `__vue-devtools-plugin-settings__${t.id}`;
    let s = Object.assign({}, r);
    try {
      const i = localStorage.getItem(o), a = JSON.parse(i);
      Object.assign(s, a);
    } catch {
    }
    this.fallbacks = {
      getSettings() {
        return s;
      },
      setSettings(i) {
        try {
          localStorage.setItem(o, JSON.stringify(i));
        } catch {
        }
        s = i;
      },
      now() {
        return Qr();
      }
    }, n && n.on(zr, (i, a) => {
      i === this.plugin.id && this.fallbacks.setSettings(a);
    }), this.proxiedOn = new Proxy({}, {
      get: (i, a) => this.target ? this.target.on[a] : (...l) => {
        this.onQueue.push({
          method: a,
          args: l
        });
      }
    }), this.proxiedTarget = new Proxy({}, {
      get: (i, a) => this.target ? this.target[a] : a === "on" ? this.proxiedOn : Object.keys(this.fallbacks).includes(a) ? (...l) => (this.targetQueue.push({
        method: a,
        args: l,
        resolve: () => {
        }
      }), this.fallbacks[a](...l)) : (...l) => new Promise((d) => {
        this.targetQueue.push({
          method: a,
          args: l,
          resolve: d
        });
      })
    });
  }
  async setRealTarget(t) {
    this.target = t;
    for (const n of this.onQueue)
      this.target.on[n.method](...n.args);
    for (const n of this.targetQueue)
      n.resolve(await this.target[n.method](...n.args));
  }
}
function Yr(e, t) {
  const n = e, r = ln(), o = Hr(), s = Kr && n.enableEarlyProxy;
  if (o && (r.__VUE_DEVTOOLS_PLUGIN_API_AVAILABLE__ || !s))
    o.emit(Gr, e, t);
  else {
    const i = s ? new Jr(n, o) : null;
    (r.__VUE_DEVTOOLS_PLUGINS__ = r.__VUE_DEVTOOLS_PLUGINS__ || []).push({
      pluginDescriptor: n,
      setupFn: t,
      proxy: i
    }), i && t(i.proxiedTarget);
  }
}
var P = {};
const q = typeof document < "u";
function fn(e) {
  return typeof e == "object" || "displayName" in e || "props" in e || "__vccOpts" in e;
}
function Xr(e) {
  return e.__esModule || e[Symbol.toStringTag] === "Module" || // support CF with dynamic imports that do not
  // add the Module string tag
  e.default && fn(e.default);
}
const N = Object.assign;
function He(e, t) {
  const n = {};
  for (const r in t) {
    const o = t[r];
    n[r] = B(o) ? o.map(e) : e(o);
  }
  return n;
}
const we = () => {
}, B = Array.isArray;
function S(e) {
  const t = Array.from(arguments).slice(1);
  console.warn.apply(console, ["[Vue Router warn]: " + e].concat(t));
}
const dn = /#/g, Zr = /&/g, eo = /\//g, to = /=/g, no = /\?/g, hn = /\+/g, ro = /%5B/g, oo = /%5D/g, pn = /%5E/g, so = /%60/g, gn = /%7B/g, io = /%7C/g, mn = /%7D/g, ao = /%20/g;
function gt(e) {
  return encodeURI("" + e).replace(io, "|").replace(ro, "[").replace(oo, "]");
}
function co(e) {
  return gt(e).replace(gn, "{").replace(mn, "}").replace(pn, "^");
}
function st(e) {
  return gt(e).replace(hn, "%2B").replace(ao, "+").replace(dn, "%23").replace(Zr, "%26").replace(so, "`").replace(gn, "{").replace(mn, "}").replace(pn, "^");
}
function uo(e) {
  return st(e).replace(to, "%3D");
}
function lo(e) {
  return gt(e).replace(dn, "%23").replace(no, "%3F");
}
function fo(e) {
  return e == null ? "" : lo(e).replace(eo, "%2F");
}
function ie(e) {
  try {
    return decodeURIComponent("" + e);
  } catch {
    P.NODE_ENV !== "production" && S(`Error decoding "${e}". Using original value`);
  }
  return "" + e;
}
const ho = /\/$/, po = (e) => e.replace(ho, "");
function Ke(e, t, n = "/") {
  let r, o = {}, s = "", i = "";
  const a = t.indexOf("#");
  let l = t.indexOf("?");
  return a < l && a >= 0 && (l = -1), l > -1 && (r = t.slice(0, l), s = t.slice(l + 1, a > -1 ? a : t.length), o = e(s)), a > -1 && (r = r || t.slice(0, a), i = t.slice(a, t.length)), r = vo(r ?? t, n), {
    fullPath: r + (s && "?") + s + i,
    path: r,
    query: o,
    hash: ie(i)
  };
}
function go(e, t) {
  const n = t.query ? e(t.query) : "";
  return t.path + (n && "?") + n + (t.hash || "");
}
function Ot(e, t) {
  return !t || !e.toLowerCase().startsWith(t.toLowerCase()) ? e : e.slice(t.length) || "/";
}
function kt(e, t, n) {
  const r = t.matched.length - 1, o = n.matched.length - 1;
  return r > -1 && r === o && Z(t.matched[r], n.matched[o]) && vn(t.params, n.params) && e(t.query) === e(n.query) && t.hash === n.hash;
}
function Z(e, t) {
  return (e.aliasOf || e) === (t.aliasOf || t);
}
function vn(e, t) {
  if (Object.keys(e).length !== Object.keys(t).length)
    return !1;
  for (const n in e)
    if (!mo(e[n], t[n]))
      return !1;
  return !0;
}
function mo(e, t) {
  return B(e) ? Nt(e, t) : B(t) ? Nt(t, e) : e === t;
}
function Nt(e, t) {
  return B(t) ? e.length === t.length && e.every((n, r) => n === t[r]) : e.length === 1 && e[0] === t;
}
function vo(e, t) {
  if (e.startsWith("/"))
    return e;
  if (P.NODE_ENV !== "production" && !t.startsWith("/"))
    return S(`Cannot resolve a relative location without an absolute path. Trying to resolve "${e}" from "${t}". It should look like "/${t}".`), e;
  if (!e)
    return t;
  const n = t.split("/"), r = e.split("/"), o = r[r.length - 1];
  (o === ".." || o === ".") && r.push("");
  let s = n.length - 1, i, a;
  for (i = 0; i < r.length; i++)
    if (a = r[i], a !== ".")
      if (a === "..")
        s > 1 && s--;
      else
        break;
  return n.slice(0, s).join("/") + "/" + r.slice(i).join("/");
}
const Y = {
  path: "/",
  // TODO: could we use a symbol in the future?
  name: void 0,
  params: {},
  query: {},
  hash: "",
  fullPath: "/",
  matched: [],
  meta: {},
  redirectedFrom: void 0
};
var ae;
(function(e) {
  e.pop = "pop", e.push = "push";
})(ae || (ae = {}));
var te;
(function(e) {
  e.back = "back", e.forward = "forward", e.unknown = "";
})(te || (te = {}));
const Ge = "";
function yn(e) {
  if (!e)
    if (q) {
      const t = document.querySelector("base");
      e = t && t.getAttribute("href") || "/", e = e.replace(/^\w+:\/\/[^\/]+/, "");
    } else
      e = "/";
  return e[0] !== "/" && e[0] !== "#" && (e = "/" + e), po(e);
}
const yo = /^[^#]+#/;
function wn(e, t) {
  return e.replace(yo, "#") + t;
}
function wo(e, t) {
  const n = document.documentElement.getBoundingClientRect(), r = e.getBoundingClientRect();
  return {
    behavior: t.behavior,
    left: r.left - n.left - (t.left || 0),
    top: r.top - n.top - (t.top || 0)
  };
}
const Te = () => ({
  left: window.scrollX,
  top: window.scrollY
});
function _o(e) {
  let t;
  if ("el" in e) {
    const n = e.el, r = typeof n == "string" && n.startsWith("#");
    if (P.NODE_ENV !== "production" && typeof e.el == "string" && (!r || !document.getElementById(e.el.slice(1))))
      try {
        const s = document.querySelector(e.el);
        if (r && s) {
          S(`The selector "${e.el}" should be passed as "el: document.querySelector('${e.el}')" because it starts with "#".`);
          return;
        }
      } catch {
        S(`The selector "${e.el}" is invalid. If you are using an id selector, make sure to escape it. You can find more information about escaping characters in selectors at https://mathiasbynens.be/notes/css-escapes or use CSS.escape (https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape).`);
        return;
      }
    const o = typeof n == "string" ? r ? document.getElementById(n.slice(1)) : document.querySelector(n) : n;
    if (!o) {
      P.NODE_ENV !== "production" && S(`Couldn't find element using selector "${e.el}" returned by scrollBehavior.`);
      return;
    }
    t = wo(o, e);
  } else
    t = e;
  "scrollBehavior" in document.documentElement.style ? window.scrollTo(t) : window.scrollTo(t.left != null ? t.left : window.scrollX, t.top != null ? t.top : window.scrollY);
}
function Vt(e, t) {
  return (history.state ? history.state.position - t : -1) + e;
}
const it = /* @__PURE__ */ new Map();
function Eo(e, t) {
  it.set(e, t);
}
function bo(e) {
  const t = it.get(e);
  return it.delete(e), t;
}
let Ro = () => location.protocol + "//" + location.host;
function _n(e, t) {
  const { pathname: n, search: r, hash: o } = t, s = e.indexOf("#");
  if (s > -1) {
    let a = o.includes(e.slice(s)) ? e.slice(s).length : 1, l = o.slice(a);
    return l[0] !== "/" && (l = "/" + l), Ot(l, "");
  }
  return Ot(n, e) + r + o;
}
function Po(e, t, n, r) {
  let o = [], s = [], i = null;
  const a = ({ state: f }) => {
    const h = _n(e, location), m = n.value, g = t.value;
    let v = 0;
    if (f) {
      if (n.value = h, t.value = f, i && i === m) {
        i = null;
        return;
      }
      v = g ? f.position - g.position : 0;
    } else
      r(h);
    o.forEach((_) => {
      _(n.value, m, {
        delta: v,
        type: ae.pop,
        direction: v ? v > 0 ? te.forward : te.back : te.unknown
      });
    });
  };
  function l() {
    i = n.value;
  }
  function d(f) {
    o.push(f);
    const h = () => {
      const m = o.indexOf(f);
      m > -1 && o.splice(m, 1);
    };
    return s.push(h), h;
  }
  function c() {
    const { history: f } = window;
    f.state && f.replaceState(N({}, f.state, { scroll: Te() }), "");
  }
  function u() {
    for (const f of s)
      f();
    s = [], window.removeEventListener("popstate", a), window.removeEventListener("beforeunload", c);
  }
  return window.addEventListener("popstate", a), window.addEventListener("beforeunload", c, {
    passive: !0
  }), {
    pauseListeners: l,
    listen: d,
    destroy: u
  };
}
function Ct(e, t, n, r = !1, o = !1) {
  return {
    back: e,
    current: t,
    forward: n,
    replaced: r,
    position: window.history.length,
    scroll: o ? Te() : null
  };
}
function So(e) {
  const { history: t, location: n } = window, r = {
    value: _n(e, n)
  }, o = { value: t.state };
  o.value || s(r.value, {
    back: null,
    current: r.value,
    forward: null,
    // the length is off by one, we need to decrease it
    position: t.length - 1,
    replaced: !0,
    // don't add a scroll as the user may have an anchor, and we want
    // scrollBehavior to be triggered without a saved position
    scroll: null
  }, !0);
  function s(l, d, c) {
    const u = e.indexOf("#"), f = u > -1 ? (n.host && document.querySelector("base") ? e : e.slice(u)) + l : Ro() + e + l;
    try {
      t[c ? "replaceState" : "pushState"](d, "", f), o.value = d;
    } catch (h) {
      P.NODE_ENV !== "production" ? S("Error with push/replace State", h) : console.error(h), n[c ? "replace" : "assign"](f);
    }
  }
  function i(l, d) {
    const c = N({}, t.state, Ct(
      o.value.back,
      // keep back and forward entries but override current position
      l,
      o.value.forward,
      !0
    ), d, { position: o.value.position });
    s(l, c, !0), r.value = l;
  }
  function a(l, d) {
    const c = N(
      {},
      // use current history state to gracefully handle a wrong call to
      // history.replaceState
      // https://github.com/vuejs/router/issues/366
      o.value,
      t.state,
      {
        forward: l,
        scroll: Te()
      }
    );
    P.NODE_ENV !== "production" && !t.state && S(`history.state seems to have been manually replaced without preserving the necessary values. Make sure to preserve existing history state if you are manually calling history.replaceState:

history.replaceState(history.state, '', url)

You can find more information at https://router.vuejs.org/guide/migration/#Usage-of-history-state`), s(c.current, c, !0);
    const u = N({}, Ct(r.value, l, null), { position: c.position + 1 }, d);
    s(l, u, !1), r.value = l;
  }
  return {
    location: r,
    state: o,
    push: a,
    replace: i
  };
}
function En(e) {
  e = yn(e);
  const t = So(e), n = Po(e, t.state, t.location, t.replace);
  function r(s, i = !0) {
    i || n.pauseListeners(), history.go(s);
  }
  const o = N({
    // it's overridden right after
    location: "",
    base: e,
    go: r,
    createHref: wn.bind(null, e)
  }, t, n);
  return Object.defineProperty(o, "location", {
    enumerable: !0,
    get: () => t.location.value
  }), Object.defineProperty(o, "state", {
    enumerable: !0,
    get: () => t.state.value
  }), o;
}
function Oo(e = "") {
  let t = [], n = [Ge], r = 0;
  e = yn(e);
  function o(a) {
    r++, r !== n.length && n.splice(r), n.push(a);
  }
  function s(a, l, { direction: d, delta: c }) {
    const u = {
      direction: d,
      delta: c,
      type: ae.pop
    };
    for (const f of t)
      f(a, l, u);
  }
  const i = {
    // rewritten by Object.defineProperty
    location: Ge,
    // TODO: should be kept in queue
    state: {},
    base: e,
    createHref: wn.bind(null, e),
    replace(a) {
      n.splice(r--, 1), o(a);
    },
    push(a, l) {
      o(a);
    },
    listen(a) {
      return t.push(a), () => {
        const l = t.indexOf(a);
        l > -1 && t.splice(l, 1);
      };
    },
    destroy() {
      t = [], n = [Ge], r = 0;
    },
    go(a, l = !0) {
      const d = this.location, c = (
        // we are considering delta === 0 going forward, but in abstract mode
        // using 0 for the delta doesn't make sense like it does in html5 where
        // it reloads the page
        a < 0 ? te.back : te.forward
      );
      r = Math.max(0, Math.min(r + a, n.length - 1)), l && s(this.location, d, {
        direction: c,
        delta: a
      });
    }
  };
  return Object.defineProperty(i, "location", {
    enumerable: !0,
    get: () => n[r]
  }), i;
}
function ko(e) {
  return e = location.host ? e || location.pathname + location.search : "", e.includes("#") || (e += "#"), P.NODE_ENV !== "production" && !e.endsWith("#/") && !e.endsWith("#") && S(`A hash base must end with a "#":
"${e}" should be "${e.replace(/#.*$/, "#")}".`), En(e);
}
function Ce(e) {
  return typeof e == "string" || e && typeof e == "object";
}
function bn(e) {
  return typeof e == "string" || typeof e == "symbol";
}
const at = Symbol(P.NODE_ENV !== "production" ? "navigation failure" : "");
var It;
(function(e) {
  e[e.aborted = 4] = "aborted", e[e.cancelled = 8] = "cancelled", e[e.duplicated = 16] = "duplicated";
})(It || (It = {}));
const No = {
  1({ location: e, currentLocation: t }) {
    return `No match for
 ${JSON.stringify(e)}${t ? `
while being at
` + JSON.stringify(t) : ""}`;
  },
  2({ from: e, to: t }) {
    return `Redirected from "${e.fullPath}" to "${Co(t)}" via a navigation guard.`;
  },
  4({ from: e, to: t }) {
    return `Navigation aborted from "${e.fullPath}" to "${t.fullPath}" via a navigation guard.`;
  },
  8({ from: e, to: t }) {
    return `Navigation cancelled from "${e.fullPath}" to "${t.fullPath}" with a new navigation.`;
  },
  16({ from: e, to: t }) {
    return `Avoided redundant navigation to current location: "${e.fullPath}".`;
  }
};
function ce(e, t) {
  return P.NODE_ENV !== "production" ? N(new Error(No[e](t)), {
    type: e,
    [at]: !0
  }, t) : N(new Error(), {
    type: e,
    [at]: !0
  }, t);
}
function z(e, t) {
  return e instanceof Error && at in e && (t == null || !!(e.type & t));
}
const Vo = ["params", "query", "hash"];
function Co(e) {
  if (typeof e == "string")
    return e;
  if (e.path != null)
    return e.path;
  const t = {};
  for (const n of Vo)
    n in e && (t[n] = e[n]);
  return JSON.stringify(t, null, 2);
}
const At = "[^/]+?", Io = {
  sensitive: !1,
  strict: !1,
  start: !0,
  end: !0
}, Ao = /[.+*?^${}()[\]/\\]/g;
function $o(e, t) {
  const n = N({}, Io, t), r = [];
  let o = n.start ? "^" : "";
  const s = [];
  for (const d of e) {
    const c = d.length ? [] : [
      90
      /* PathScore.Root */
    ];
    n.strict && !d.length && (o += "/");
    for (let u = 0; u < d.length; u++) {
      const f = d[u];
      let h = 40 + (n.sensitive ? 0.25 : 0);
      if (f.type === 0)
        u || (o += "/"), o += f.value.replace(Ao, "\\$&"), h += 40;
      else if (f.type === 1) {
        const { value: m, repeatable: g, optional: v, regexp: _ } = f;
        s.push({
          name: m,
          repeatable: g,
          optional: v
        });
        const E = _ || At;
        if (E !== At) {
          h += 10;
          try {
            new RegExp(`(${E})`);
          } catch (C) {
            throw new Error(`Invalid custom RegExp for param "${m}" (${E}): ` + C.message);
          }
        }
        let R = g ? `((?:${E})(?:/(?:${E}))*)` : `(${E})`;
        u || (R = // avoid an optional / if there are more segments e.g. /:p?-static
        // or /:p?-:p2
        v && d.length < 2 ? `(?:/${R})` : "/" + R), v && (R += "?"), o += R, h += 20, v && (h += -8), g && (h += -20), E === ".*" && (h += -50);
      }
      c.push(h);
    }
    r.push(c);
  }
  if (n.strict && n.end) {
    const d = r.length - 1;
    r[d][r[d].length - 1] += 0.7000000000000001;
  }
  n.strict || (o += "/?"), n.end ? o += "$" : n.strict && !o.endsWith("/") && (o += "(?:/|$)");
  const i = new RegExp(o, n.sensitive ? "" : "i");
  function a(d) {
    const c = d.match(i), u = {};
    if (!c)
      return null;
    for (let f = 1; f < c.length; f++) {
      const h = c[f] || "", m = s[f - 1];
      u[m.name] = h && m.repeatable ? h.split("/") : h;
    }
    return u;
  }
  function l(d) {
    let c = "", u = !1;
    for (const f of e) {
      (!u || !c.endsWith("/")) && (c += "/"), u = !1;
      for (const h of f)
        if (h.type === 0)
          c += h.value;
        else if (h.type === 1) {
          const { value: m, repeatable: g, optional: v } = h, _ = m in d ? d[m] : "";
          if (B(_) && !g)
            throw new Error(`Provided param "${m}" is an array but it is not repeatable (* or + modifiers)`);
          const E = B(_) ? _.join("/") : _;
          if (!E)
            if (v)
              f.length < 2 && (c.endsWith("/") ? c = c.slice(0, -1) : u = !0);
            else
              throw new Error(`Missing required param "${m}"`);
          c += E;
        }
    }
    return c || "/";
  }
  return {
    re: i,
    score: r,
    keys: s,
    parse: a,
    stringify: l
  };
}
function xo(e, t) {
  let n = 0;
  for (; n < e.length && n < t.length; ) {
    const r = t[n] - e[n];
    if (r)
      return r;
    n++;
  }
  return e.length < t.length ? e.length === 1 && e[0] === 80 ? -1 : 1 : e.length > t.length ? t.length === 1 && t[0] === 80 ? 1 : -1 : 0;
}
function Rn(e, t) {
  let n = 0;
  const r = e.score, o = t.score;
  for (; n < r.length && n < o.length; ) {
    const s = xo(r[n], o[n]);
    if (s)
      return s;
    n++;
  }
  if (Math.abs(o.length - r.length) === 1) {
    if ($t(r))
      return 1;
    if ($t(o))
      return -1;
  }
  return o.length - r.length;
}
function $t(e) {
  const t = e[e.length - 1];
  return e.length > 0 && t[t.length - 1] < 0;
}
const To = {
  type: 0,
  value: ""
}, Do = /[a-zA-Z0-9_]/;
function jo(e) {
  if (!e)
    return [[]];
  if (e === "/")
    return [[To]];
  if (!e.startsWith("/"))
    throw new Error(P.NODE_ENV !== "production" ? `Route paths should start with a "/": "${e}" should be "/${e}".` : `Invalid path "${e}"`);
  function t(h) {
    throw new Error(`ERR (${n})/"${d}": ${h}`);
  }
  let n = 0, r = n;
  const o = [];
  let s;
  function i() {
    s && o.push(s), s = [];
  }
  let a = 0, l, d = "", c = "";
  function u() {
    d && (n === 0 ? s.push({
      type: 0,
      value: d
    }) : n === 1 || n === 2 || n === 3 ? (s.length > 1 && (l === "*" || l === "+") && t(`A repeatable param (${d}) must be alone in its segment. eg: '/:ids+.`), s.push({
      type: 1,
      value: d,
      regexp: c,
      repeatable: l === "*" || l === "+",
      optional: l === "*" || l === "?"
    })) : t("Invalid state to consume buffer"), d = "");
  }
  function f() {
    d += l;
  }
  for (; a < e.length; ) {
    if (l = e[a++], l === "\\" && n !== 2) {
      r = n, n = 4;
      continue;
    }
    switch (n) {
      case 0:
        l === "/" ? (d && u(), i()) : l === ":" ? (u(), n = 1) : f();
        break;
      case 4:
        f(), n = r;
        break;
      case 1:
        l === "(" ? n = 2 : Do.test(l) ? f() : (u(), n = 0, l !== "*" && l !== "?" && l !== "+" && a--);
        break;
      case 2:
        l === ")" ? c[c.length - 1] == "\\" ? c = c.slice(0, -1) + l : n = 3 : c += l;
        break;
      case 3:
        u(), n = 0, l !== "*" && l !== "?" && l !== "+" && a--, c = "";
        break;
      default:
        t("Unknown state");
        break;
    }
  }
  return n === 2 && t(`Unfinished custom RegExp for param "${d}"`), u(), i(), o;
}
function Mo(e, t, n) {
  const r = $o(jo(e.path), n);
  if (P.NODE_ENV !== "production") {
    const s = /* @__PURE__ */ new Set();
    for (const i of r.keys)
      s.has(i.name) && S(`Found duplicated params with name "${i.name}" for path "${e.path}". Only the last one will be available on "$route.params".`), s.add(i.name);
  }
  const o = N(r, {
    record: e,
    parent: t,
    // these needs to be populated by the parent
    children: [],
    alias: []
  });
  return t && !o.record.aliasOf == !t.record.aliasOf && t.children.push(o), o;
}
function Wo(e, t) {
  const n = [], r = /* @__PURE__ */ new Map();
  t = jt({ strict: !1, end: !0, sensitive: !1 }, t);
  function o(u) {
    return r.get(u);
  }
  function s(u, f, h) {
    const m = !h, g = Tt(u);
    P.NODE_ENV !== "production" && Uo(g, f), g.aliasOf = h && h.record;
    const v = jt(t, u), _ = [g];
    if ("alias" in u) {
      const C = typeof u.alias == "string" ? [u.alias] : u.alias;
      for (const M of C)
        _.push(
          // we need to normalize again to ensure the `mods` property
          // being non enumerable
          Tt(N({}, g, {
            // this allows us to hold a copy of the `components` option
            // so that async components cache is hold on the original record
            components: h ? h.record.components : g.components,
            path: M,
            // we might be the child of an alias
            aliasOf: h ? h.record : g
            // the aliases are always of the same kind as the original since they
            // are defined on the same record
          }))
        );
    }
    let E, R;
    for (const C of _) {
      const { path: M } = C;
      if (f && M[0] !== "/") {
        const U = f.record.path, F = U[U.length - 1] === "/" ? "" : "/";
        C.path = f.record.path + (M && F + M);
      }
      if (P.NODE_ENV !== "production" && C.path === "*")
        throw new Error(`Catch all routes ("*") must now be defined using a param with a custom regexp.
See more at https://router.vuejs.org/guide/migration/#Removed-star-or-catch-all-routes.`);
      if (E = Mo(C, f, v), P.NODE_ENV !== "production" && f && M[0] === "/" && Ko(E, f), h ? (h.alias.push(E), P.NODE_ENV !== "production" && Fo(h, E)) : (R = R || E, R !== E && R.alias.push(E), m && u.name && !Dt(E) && (P.NODE_ENV !== "production" && Ho(u, f), i(u.name))), Pn(E) && l(E), g.children) {
        const U = g.children;
        for (let F = 0; F < U.length; F++)
          s(U[F], E, h && h.children[F]);
      }
      h = h || E;
    }
    return R ? () => {
      i(R);
    } : we;
  }
  function i(u) {
    if (bn(u)) {
      const f = r.get(u);
      f && (r.delete(u), n.splice(n.indexOf(f), 1), f.children.forEach(i), f.alias.forEach(i));
    } else {
      const f = n.indexOf(u);
      f > -1 && (n.splice(f, 1), u.record.name && r.delete(u.record.name), u.children.forEach(i), u.alias.forEach(i));
    }
  }
  function a() {
    return n;
  }
  function l(u) {
    const f = Go(u, n);
    n.splice(f, 0, u), u.record.name && !Dt(u) && r.set(u.record.name, u);
  }
  function d(u, f) {
    let h, m = {}, g, v;
    if ("name" in u && u.name) {
      if (h = r.get(u.name), !h)
        throw ce(1, {
          location: u
        });
      if (P.NODE_ENV !== "production") {
        const R = Object.keys(u.params || {}).filter((C) => !h.keys.find((M) => M.name === C));
        R.length && S(`Discarded invalid param(s) "${R.join('", "')}" when navigating. See https://github.com/vuejs/router/blob/main/packages/router/CHANGELOG.md#414-2022-08-22 for more details.`);
      }
      v = h.record.name, m = N(
        // paramsFromLocation is a new object
        xt(
          f.params,
          // only keep params that exist in the resolved location
          // only keep optional params coming from a parent record
          h.keys.filter((R) => !R.optional).concat(h.parent ? h.parent.keys.filter((R) => R.optional) : []).map((R) => R.name)
        ),
        // discard any existing params in the current location that do not exist here
        // #1497 this ensures better active/exact matching
        u.params && xt(u.params, h.keys.map((R) => R.name))
      ), g = h.stringify(m);
    } else if (u.path != null)
      g = u.path, P.NODE_ENV !== "production" && !g.startsWith("/") && S(`The Matcher cannot resolve relative paths but received "${g}". Unless you directly called \`matcher.resolve("${g}")\`, this is probably a bug in vue-router. Please open an issue at https://github.com/vuejs/router/issues/new/choose.`), h = n.find((R) => R.re.test(g)), h && (m = h.parse(g), v = h.record.name);
    else {
      if (h = f.name ? r.get(f.name) : n.find((R) => R.re.test(f.path)), !h)
        throw ce(1, {
          location: u,
          currentLocation: f
        });
      v = h.record.name, m = N({}, f.params, u.params), g = h.stringify(m);
    }
    const _ = [];
    let E = h;
    for (; E; )
      _.unshift(E.record), E = E.parent;
    return {
      name: v,
      path: g,
      params: m,
      matched: _,
      meta: Bo(_)
    };
  }
  e.forEach((u) => s(u));
  function c() {
    n.length = 0, r.clear();
  }
  return {
    addRoute: s,
    resolve: d,
    removeRoute: i,
    clearRoutes: c,
    getRoutes: a,
    getRecordMatcher: o
  };
}
function xt(e, t) {
  const n = {};
  for (const r of t)
    r in e && (n[r] = e[r]);
  return n;
}
function Tt(e) {
  const t = {
    path: e.path,
    redirect: e.redirect,
    name: e.name,
    meta: e.meta || {},
    aliasOf: e.aliasOf,
    beforeEnter: e.beforeEnter,
    props: Lo(e),
    children: e.children || [],
    instances: {},
    leaveGuards: /* @__PURE__ */ new Set(),
    updateGuards: /* @__PURE__ */ new Set(),
    enterCallbacks: {},
    // must be declared afterwards
    // mods: {},
    components: "components" in e ? e.components || null : e.component && { default: e.component }
  };
  return Object.defineProperty(t, "mods", {
    value: {}
  }), t;
}
function Lo(e) {
  const t = {}, n = e.props || !1;
  if ("component" in e)
    t.default = n;
  else
    for (const r in e.components)
      t[r] = typeof n == "object" ? n[r] : n;
  return t;
}
function Dt(e) {
  for (; e; ) {
    if (e.record.aliasOf)
      return !0;
    e = e.parent;
  }
  return !1;
}
function Bo(e) {
  return e.reduce((t, n) => N(t, n.meta), {});
}
function jt(e, t) {
  const n = {};
  for (const r in e)
    n[r] = r in t ? t[r] : e[r];
  return n;
}
function ct(e, t) {
  return e.name === t.name && e.optional === t.optional && e.repeatable === t.repeatable;
}
function Fo(e, t) {
  for (const n of e.keys)
    if (!n.optional && !t.keys.find(ct.bind(null, n)))
      return S(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
  for (const n of t.keys)
    if (!n.optional && !e.keys.find(ct.bind(null, n)))
      return S(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
}
function Uo(e, t) {
  t && t.record.name && !e.name && !e.path && S(`The route named "${String(t.record.name)}" has a child without a name and an empty path. Using that name won't render the empty path child so you probably want to move the name to the child instead. If this is intentional, add a name to the child route to remove the warning.`);
}
function Ho(e, t) {
  for (let n = t; n; n = n.parent)
    if (n.record.name === e.name)
      throw new Error(`A route named "${String(e.name)}" has been added as a ${t === n ? "child" : "descendant"} of a route with the same name. Route names must be unique and a nested route cannot use the same name as an ancestor.`);
}
function Ko(e, t) {
  for (const n of t.keys)
    if (!e.keys.find(ct.bind(null, n)))
      return S(`Absolute path "${e.record.path}" must have the exact same param named "${n.name}" as its parent "${t.record.path}".`);
}
function Go(e, t) {
  let n = 0, r = t.length;
  for (; n !== r; ) {
    const s = n + r >> 1;
    Rn(e, t[s]) < 0 ? r = s : n = s + 1;
  }
  const o = zo(e);
  return o && (r = t.lastIndexOf(o, r - 1), P.NODE_ENV !== "production" && r < 0 && S(`Finding ancestor route "${o.record.path}" failed for "${e.record.path}"`)), r;
}
function zo(e) {
  let t = e;
  for (; t = t.parent; )
    if (Pn(t) && Rn(e, t) === 0)
      return t;
}
function Pn({ record: e }) {
  return !!(e.name || e.components && Object.keys(e.components).length || e.redirect);
}
function qo(e) {
  const t = {};
  if (e === "" || e === "?")
    return t;
  const r = (e[0] === "?" ? e.slice(1) : e).split("&");
  for (let o = 0; o < r.length; ++o) {
    const s = r[o].replace(hn, " "), i = s.indexOf("="), a = ie(i < 0 ? s : s.slice(0, i)), l = i < 0 ? null : ie(s.slice(i + 1));
    if (a in t) {
      let d = t[a];
      B(d) || (d = t[a] = [d]), d.push(l);
    } else
      t[a] = l;
  }
  return t;
}
function Mt(e) {
  let t = "";
  for (let n in e) {
    const r = e[n];
    if (n = uo(n), r == null) {
      r !== void 0 && (t += (t.length ? "&" : "") + n);
      continue;
    }
    (B(r) ? r.map((s) => s && st(s)) : [r && st(r)]).forEach((s) => {
      s !== void 0 && (t += (t.length ? "&" : "") + n, s != null && (t += "=" + s));
    });
  }
  return t;
}
function Qo(e) {
  const t = {};
  for (const n in e) {
    const r = e[n];
    r !== void 0 && (t[n] = B(r) ? r.map((o) => o == null ? null : "" + o) : r == null ? r : "" + r);
  }
  return t;
}
const Jo = Symbol(P.NODE_ENV !== "production" ? "router view location matched" : ""), Wt = Symbol(P.NODE_ENV !== "production" ? "router view depth" : ""), De = Symbol(P.NODE_ENV !== "production" ? "router" : ""), mt = Symbol(P.NODE_ENV !== "production" ? "route location" : ""), ut = Symbol(P.NODE_ENV !== "production" ? "router view location" : "");
function he() {
  let e = [];
  function t(r) {
    return e.push(r), () => {
      const o = e.indexOf(r);
      o > -1 && e.splice(o, 1);
    };
  }
  function n() {
    e = [];
  }
  return {
    add: t,
    list: () => e.slice(),
    reset: n
  };
}
function X(e, t, n, r, o, s = (i) => i()) {
  const i = r && // name is defined if record is because of the function overload
  (r.enterCallbacks[o] = r.enterCallbacks[o] || []);
  return () => new Promise((a, l) => {
    const d = (f) => {
      f === !1 ? l(ce(4, {
        from: n,
        to: t
      })) : f instanceof Error ? l(f) : Ce(f) ? l(ce(2, {
        from: t,
        to: f
      })) : (i && // since enterCallbackArray is truthy, both record and name also are
      r.enterCallbacks[o] === i && typeof f == "function" && i.push(f), a());
    }, c = s(() => e.call(r && r.instances[o], t, n, P.NODE_ENV !== "production" ? Yo(d, t, n) : d));
    let u = Promise.resolve(c);
    if (e.length < 3 && (u = u.then(d)), P.NODE_ENV !== "production" && e.length > 2) {
      const f = `The "next" callback was never called inside of ${e.name ? '"' + e.name + '"' : ""}:
${e.toString()}
. If you are returning a value instead of calling "next", make sure to remove the "next" parameter from your function.`;
      if (typeof c == "object" && "then" in c)
        u = u.then((h) => d._called ? h : (S(f), Promise.reject(new Error("Invalid navigation guard"))));
      else if (c !== void 0 && !d._called) {
        S(f), l(new Error("Invalid navigation guard"));
        return;
      }
    }
    u.catch((f) => l(f));
  });
}
function Yo(e, t, n) {
  let r = 0;
  return function() {
    r++ === 1 && S(`The "next" callback was called more than once in one navigation guard when going from "${n.fullPath}" to "${t.fullPath}". It should be called exactly one time in each navigation guard. This will fail in production.`), e._called = !0, r === 1 && e.apply(null, arguments);
  };
}
function ze(e, t, n, r, o = (s) => s()) {
  const s = [];
  for (const i of e) {
    P.NODE_ENV !== "production" && !i.components && !i.children.length && S(`Record with path "${i.path}" is either missing a "component(s)" or "children" property.`);
    for (const a in i.components) {
      let l = i.components[a];
      if (P.NODE_ENV !== "production") {
        if (!l || typeof l != "object" && typeof l != "function")
          throw S(`Component "${a}" in record with path "${i.path}" is not a valid component. Received "${String(l)}".`), new Error("Invalid route component");
        if ("then" in l) {
          S(`Component "${a}" in record with path "${i.path}" is a Promise instead of a function that returns a Promise. Did you write "import('./MyPage.vue')" instead of "() => import('./MyPage.vue')" ? This will break in production if not fixed.`);
          const d = l;
          l = () => d;
        } else l.__asyncLoader && // warn only once per component
        !l.__warnedDefineAsync && (l.__warnedDefineAsync = !0, S(`Component "${a}" in record with path "${i.path}" is defined using "defineAsyncComponent()". Write "() => import('./MyPage.vue')" instead of "defineAsyncComponent(() => import('./MyPage.vue'))".`));
      }
      if (!(t !== "beforeRouteEnter" && !i.instances[a]))
        if (fn(l)) {
          const c = (l.__vccOpts || l)[t];
          c && s.push(X(c, n, r, i, a, o));
        } else {
          let d = l();
          P.NODE_ENV !== "production" && !("catch" in d) && (S(`Component "${a}" in record with path "${i.path}" is a function that does not return a Promise. If you were passing a functional component, make sure to add a "displayName" to the component. This will break in production if not fixed.`), d = Promise.resolve(d)), s.push(() => d.then((c) => {
            if (!c)
              throw new Error(`Couldn't resolve component "${a}" at "${i.path}"`);
            const u = Xr(c) ? c.default : c;
            i.mods[a] = c, i.components[a] = u;
            const h = (u.__vccOpts || u)[t];
            return h && X(h, n, r, i, a, o)();
          }));
        }
    }
  }
  return s;
}
function Lt(e) {
  const t = J(De), n = J(mt);
  let r = !1, o = null;
  const s = L(() => {
    const c = W(e.to);
    return P.NODE_ENV !== "production" && (!r || c !== o) && (Ce(c) || (r ? S(`Invalid value for prop "to" in useLink()
- to:`, c, `
- previous to:`, o, `
- props:`, e) : S(`Invalid value for prop "to" in useLink()
- to:`, c, `
- props:`, e)), o = c, r = !0), t.resolve(c);
  }), i = L(() => {
    const { matched: c } = s.value, { length: u } = c, f = c[u - 1], h = n.matched;
    if (!f || !h.length)
      return -1;
    const m = h.findIndex(Z.bind(null, f));
    if (m > -1)
      return m;
    const g = Bt(c[u - 2]);
    return (
      // we are dealing with nested routes
      u > 1 && // if the parent and matched route have the same path, this link is
      // referring to the empty child. Or we currently are on a different
      // child of the same parent
      Bt(f) === g && // avoid comparing the child with its parent
      h[h.length - 1].path !== g ? h.findIndex(Z.bind(null, c[u - 2])) : m
    );
  }), a = L(() => i.value > -1 && ns(n.params, s.value.params)), l = L(() => i.value > -1 && i.value === n.matched.length - 1 && vn(n.params, s.value.params));
  function d(c = {}) {
    if (ts(c)) {
      const u = t[W(e.replace) ? "replace" : "push"](
        W(e.to)
        // avoid uncaught errors are they are logged anyway
      ).catch(we);
      return e.viewTransition && typeof document < "u" && "startViewTransition" in document && document.startViewTransition(() => u), u;
    }
    return Promise.resolve();
  }
  if (P.NODE_ENV !== "production" && q) {
    const c = Qt();
    if (c) {
      const u = {
        route: s.value,
        isActive: a.value,
        isExactActive: l.value,
        error: null
      };
      c.__vrl_devtools = c.__vrl_devtools || [], c.__vrl_devtools.push(u), zt(() => {
        u.route = s.value, u.isActive = a.value, u.isExactActive = l.value, u.error = Ce(W(e.to)) ? null : 'Invalid "to" value';
      }, { flush: "post" });
    }
  }
  return {
    route: s,
    href: L(() => s.value.href),
    isActive: a,
    isExactActive: l,
    navigate: d
  };
}
function Xo(e) {
  return e.length === 1 ? e[0] : e;
}
const Zo = /* @__PURE__ */ j({
  name: "RouterLink",
  compatConfig: { MODE: 3 },
  props: {
    to: {
      type: [String, Object],
      required: !0
    },
    replace: Boolean,
    activeClass: String,
    // inactiveClass: String,
    exactActiveClass: String,
    custom: Boolean,
    ariaCurrentValue: {
      type: String,
      default: "page"
    }
  },
  useLink: Lt,
  setup(e, { slots: t }) {
    const n = Gn(Lt(e)), { options: r } = J(De), o = L(() => ({
      [Ft(e.activeClass, r.linkActiveClass, "router-link-active")]: n.isActive,
      // [getLinkClass(
      //   props.inactiveClass,
      //   options.linkInactiveClass,
      //   'router-link-inactive'
      // )]: !link.isExactActive,
      [Ft(e.exactActiveClass, r.linkExactActiveClass, "router-link-exact-active")]: n.isExactActive
    }));
    return () => {
      const s = t.default && Xo(t.default(n));
      return e.custom ? s : x("a", {
        "aria-current": n.isExactActive ? e.ariaCurrentValue : null,
        href: n.href,
        // this would override user added attrs but Vue will still add
        // the listener, so we end up triggering both
        onClick: n.navigate,
        class: o.value
      }, s);
    };
  }
}), es = Zo;
function ts(e) {
  if (!(e.metaKey || e.altKey || e.ctrlKey || e.shiftKey) && !e.defaultPrevented && !(e.button !== void 0 && e.button !== 0)) {
    if (e.currentTarget && e.currentTarget.getAttribute) {
      const t = e.currentTarget.getAttribute("target");
      if (/\b_blank\b/i.test(t))
        return;
    }
    return e.preventDefault && e.preventDefault(), !0;
  }
}
function ns(e, t) {
  for (const n in t) {
    const r = t[n], o = e[n];
    if (typeof r == "string") {
      if (r !== o)
        return !1;
    } else if (!B(o) || o.length !== r.length || r.some((s, i) => s !== o[i]))
      return !1;
  }
  return !0;
}
function Bt(e) {
  return e ? e.aliasOf ? e.aliasOf.path : e.path : "";
}
const Ft = (e, t, n) => e ?? t ?? n, rs = /* @__PURE__ */ j({
  name: "RouterView",
  // #674 we manually inherit them
  inheritAttrs: !1,
  props: {
    name: {
      type: String,
      default: "default"
    },
    route: Object
  },
  // Better compat for @vue/compat users
  // https://github.com/vuejs/router/issues/1315
  compatConfig: { MODE: 3 },
  setup(e, { attrs: t, slots: n }) {
    P.NODE_ENV !== "production" && ss();
    const r = J(ut), o = L(() => e.route || r.value), s = J(Wt, 0), i = L(() => {
      let d = W(s);
      const { matched: c } = o.value;
      let u;
      for (; (u = c[d]) && !u.components; )
        d++;
      return d;
    }), a = L(() => o.value.matched[i.value]);
    ve(Wt, L(() => i.value + 1)), ve(Jo, a), ve(ut, o);
    const l = Q();
    return G(() => [l.value, a.value, e.name], ([d, c, u], [f, h, m]) => {
      c && (c.instances[u] = d, h && h !== c && d && d === f && (c.leaveGuards.size || (c.leaveGuards = h.leaveGuards), c.updateGuards.size || (c.updateGuards = h.updateGuards))), d && c && // if there is no instance but to and from are the same this might be
      // the first visit
      (!h || !Z(c, h) || !f) && (c.enterCallbacks[u] || []).forEach((g) => g(d));
    }, { flush: "post" }), () => {
      const d = o.value, c = e.name, u = a.value, f = u && u.components[c];
      if (!f)
        return Ut(n.default, { Component: f, route: d });
      const h = u.props[c], m = h ? h === !0 ? d.params : typeof h == "function" ? h(d) : h : null, v = x(f, N({}, m, t, {
        onVnodeUnmounted: (_) => {
          _.component.isUnmounted && (u.instances[c] = null);
        },
        ref: l
      }));
      if (P.NODE_ENV !== "production" && q && v.ref) {
        const _ = {
          depth: i.value,
          name: u.name,
          path: u.path,
          meta: u.meta
        };
        (B(v.ref) ? v.ref.map((R) => R.i) : [v.ref.i]).forEach((R) => {
          R.__vrv_devtools = _;
        });
      }
      return (
        // pass the vnode to the slot as a prop.
        // h and <component :is="..."> both accept vnodes
        Ut(n.default, { Component: v, route: d }) || v
      );
    };
  }
});
function Ut(e, t) {
  if (!e)
    return null;
  const n = e(t);
  return n.length === 1 ? n[0] : n;
}
const os = rs;
function ss() {
  const e = Qt(), t = e.parent && e.parent.type.name, n = e.parent && e.parent.subTree && e.parent.subTree.type;
  if (t && (t === "KeepAlive" || t.includes("Transition")) && typeof n == "object" && n.name === "RouterView") {
    const r = t === "KeepAlive" ? "keep-alive" : "transition";
    S(`<router-view> can no longer be used directly inside <transition> or <keep-alive>.
Use slot props instead:

<router-view v-slot="{ Component }">
  <${r}>
    <component :is="Component" />
  </${r}>
</router-view>`);
  }
}
function pe(e, t) {
  const n = N({}, e, {
    // remove variables that can contain vue instances
    matched: e.matched.map((r) => ms(r, ["instances", "children", "aliasOf"]))
  });
  return {
    _custom: {
      type: null,
      readOnly: !0,
      display: e.fullPath,
      tooltip: t,
      value: n
    }
  };
}
function Oe(e) {
  return {
    _custom: {
      display: e
    }
  };
}
let is = 0;
function as(e, t, n) {
  if (t.__hasDevtools)
    return;
  t.__hasDevtools = !0;
  const r = is++;
  Yr({
    id: "org.vuejs.router" + (r ? "." + r : ""),
    label: "Vue Router",
    packageName: "vue-router",
    homepage: "https://router.vuejs.org",
    logo: "https://router.vuejs.org/logo.png",
    componentStateTypes: ["Routing"],
    app: e
  }, (o) => {
    typeof o.now != "function" && console.warn("[Vue Router]: You seem to be using an outdated version of Vue Devtools. Are you still using the Beta release instead of the stable one? You can find the links at https://devtools.vuejs.org/guide/installation.html."), o.on.inspectComponent((c, u) => {
      c.instanceData && c.instanceData.state.push({
        type: "Routing",
        key: "$route",
        editable: !1,
        value: pe(t.currentRoute.value, "Current Route")
      });
    }), o.on.visitComponentTree(({ treeNode: c, componentInstance: u }) => {
      if (u.__vrv_devtools) {
        const f = u.__vrv_devtools;
        c.tags.push({
          label: (f.name ? `${f.name.toString()}: ` : "") + f.path,
          textColor: 0,
          tooltip: "This component is rendered by &lt;router-view&gt;",
          backgroundColor: Sn
        });
      }
      B(u.__vrl_devtools) && (u.__devtoolsApi = o, u.__vrl_devtools.forEach((f) => {
        let h = f.route.path, m = Nn, g = "", v = 0;
        f.error ? (h = f.error, m = ds, v = hs) : f.isExactActive ? (m = kn, g = "This is exactly active") : f.isActive && (m = On, g = "This link is active"), c.tags.push({
          label: h,
          textColor: v,
          tooltip: g,
          backgroundColor: m
        });
      }));
    }), G(t.currentRoute, () => {
      l(), o.notifyComponentUpdate(), o.sendInspectorTree(a), o.sendInspectorState(a);
    });
    const s = "router:navigations:" + r;
    o.addTimelineLayer({
      id: s,
      label: `Router${r ? " " + r : ""} Navigations`,
      color: 4237508
    }), t.onError((c, u) => {
      o.addTimelineEvent({
        layerId: s,
        event: {
          title: "Error during Navigation",
          subtitle: u.fullPath,
          logType: "error",
          time: o.now(),
          data: { error: c },
          groupId: u.meta.__navigationId
        }
      });
    });
    let i = 0;
    t.beforeEach((c, u) => {
      const f = {
        guard: Oe("beforeEach"),
        from: pe(u, "Current Location during this navigation"),
        to: pe(c, "Target location")
      };
      Object.defineProperty(c.meta, "__navigationId", {
        value: i++
      }), o.addTimelineEvent({
        layerId: s,
        event: {
          time: o.now(),
          title: "Start of navigation",
          subtitle: c.fullPath,
          data: f,
          groupId: c.meta.__navigationId
        }
      });
    }), t.afterEach((c, u, f) => {
      const h = {
        guard: Oe("afterEach")
      };
      f ? (h.failure = {
        _custom: {
          type: Error,
          readOnly: !0,
          display: f ? f.message : "",
          tooltip: "Navigation Failure",
          value: f
        }
      }, h.status = Oe("❌")) : h.status = Oe("✅"), h.from = pe(u, "Current Location during this navigation"), h.to = pe(c, "Target location"), o.addTimelineEvent({
        layerId: s,
        event: {
          title: "End of navigation",
          subtitle: c.fullPath,
          time: o.now(),
          data: h,
          logType: f ? "warning" : "default",
          groupId: c.meta.__navigationId
        }
      });
    });
    const a = "router-inspector:" + r;
    o.addInspector({
      id: a,
      label: "Routes" + (r ? " " + r : ""),
      icon: "book",
      treeFilterPlaceholder: "Search routes"
    });
    function l() {
      if (!d)
        return;
      const c = d;
      let u = n.getRoutes().filter((f) => !f.parent || // these routes have a parent with no component which will not appear in the view
      // therefore we still need to include them
      !f.parent.record.components);
      u.forEach(In), c.filter && (u = u.filter((f) => (
        // save matches state based on the payload
        lt(f, c.filter.toLowerCase())
      ))), u.forEach((f) => Cn(f, t.currentRoute.value)), c.rootNodes = u.map(Vn);
    }
    let d;
    o.on.getInspectorTree((c) => {
      d = c, c.app === e && c.inspectorId === a && l();
    }), o.on.getInspectorState((c) => {
      if (c.app === e && c.inspectorId === a) {
        const f = n.getRoutes().find((h) => h.record.__vd_id === c.nodeId);
        f && (c.state = {
          options: us(f)
        });
      }
    }), o.sendInspectorTree(a), o.sendInspectorState(a);
  });
}
function cs(e) {
  return e.optional ? e.repeatable ? "*" : "?" : e.repeatable ? "+" : "";
}
function us(e) {
  const { record: t } = e, n = [
    { editable: !1, key: "path", value: t.path }
  ];
  return t.name != null && n.push({
    editable: !1,
    key: "name",
    value: t.name
  }), n.push({ editable: !1, key: "regexp", value: e.re }), e.keys.length && n.push({
    editable: !1,
    key: "keys",
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.keys.map((r) => `${r.name}${cs(r)}`).join(" "),
        tooltip: "Param keys",
        value: e.keys
      }
    }
  }), t.redirect != null && n.push({
    editable: !1,
    key: "redirect",
    value: t.redirect
  }), e.alias.length && n.push({
    editable: !1,
    key: "aliases",
    value: e.alias.map((r) => r.record.path)
  }), Object.keys(e.record.meta).length && n.push({
    editable: !1,
    key: "meta",
    value: e.record.meta
  }), n.push({
    key: "score",
    editable: !1,
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.score.map((r) => r.join(", ")).join(" | "),
        tooltip: "Score used to sort routes",
        value: e.score
      }
    }
  }), n;
}
const Sn = 15485081, On = 2450411, kn = 8702998, ls = 2282478, Nn = 16486972, fs = 6710886, ds = 16704226, hs = 12131356;
function Vn(e) {
  const t = [], { record: n } = e;
  n.name != null && t.push({
    label: String(n.name),
    textColor: 0,
    backgroundColor: ls
  }), n.aliasOf && t.push({
    label: "alias",
    textColor: 0,
    backgroundColor: Nn
  }), e.__vd_match && t.push({
    label: "matches",
    textColor: 0,
    backgroundColor: Sn
  }), e.__vd_exactActive && t.push({
    label: "exact",
    textColor: 0,
    backgroundColor: kn
  }), e.__vd_active && t.push({
    label: "active",
    textColor: 0,
    backgroundColor: On
  }), n.redirect && t.push({
    label: typeof n.redirect == "string" ? `redirect: ${n.redirect}` : "redirects",
    textColor: 16777215,
    backgroundColor: fs
  });
  let r = n.__vd_id;
  return r == null && (r = String(ps++), n.__vd_id = r), {
    id: r,
    label: n.path,
    tags: t,
    children: e.children.map(Vn)
  };
}
let ps = 0;
const gs = /^\/(.*)\/([a-z]*)$/;
function Cn(e, t) {
  const n = t.matched.length && Z(t.matched[t.matched.length - 1], e.record);
  e.__vd_exactActive = e.__vd_active = n, n || (e.__vd_active = t.matched.some((r) => Z(r, e.record))), e.children.forEach((r) => Cn(r, t));
}
function In(e) {
  e.__vd_match = !1, e.children.forEach(In);
}
function lt(e, t) {
  const n = String(e.re).match(gs);
  if (e.__vd_match = !1, !n || n.length < 3)
    return !1;
  if (new RegExp(n[1].replace(/\$$/, ""), n[2]).test(t))
    return e.children.forEach((i) => lt(i, t)), e.record.path !== "/" || t === "/" ? (e.__vd_match = e.re.test(t), !0) : !1;
  const o = e.record.path.toLowerCase(), s = ie(o);
  return !t.startsWith("/") && (s.includes(t) || o.includes(t)) || s.startsWith(t) || o.startsWith(t) || e.record.name && String(e.record.name).includes(t) ? !0 : e.children.some((i) => lt(i, t));
}
function ms(e, t) {
  const n = {};
  for (const r in e)
    t.includes(r) || (n[r] = e[r]);
  return n;
}
function vs(e) {
  const t = Wo(e.routes, e), n = e.parseQuery || qo, r = e.stringifyQuery || Mt, o = e.history;
  if (P.NODE_ENV !== "production" && !o)
    throw new Error('Provide the "history" option when calling "createRouter()": https://router.vuejs.org/api/interfaces/RouterOptions.html#history');
  const s = he(), i = he(), a = he(), l = H(Y);
  let d = Y;
  q && e.scrollBehavior && "scrollRestoration" in history && (history.scrollRestoration = "manual");
  const c = He.bind(null, (p) => "" + p), u = He.bind(null, fo), f = (
    // @ts-expect-error: intentionally avoid the type check
    He.bind(null, ie)
  );
  function h(p, w) {
    let y, b;
    return bn(p) ? (y = t.getRecordMatcher(p), P.NODE_ENV !== "production" && !y && S(`Parent route "${String(p)}" not found when adding child route`, w), b = w) : b = p, t.addRoute(b, y);
  }
  function m(p) {
    const w = t.getRecordMatcher(p);
    w ? t.removeRoute(w) : P.NODE_ENV !== "production" && S(`Cannot remove non-existent route "${String(p)}"`);
  }
  function g() {
    return t.getRoutes().map((p) => p.record);
  }
  function v(p) {
    return !!t.getRecordMatcher(p);
  }
  function _(p, w) {
    if (w = N({}, w || l.value), typeof p == "string") {
      const O = Ke(n, p, w.path), I = t.resolve({ path: O.path }, w), ee = o.createHref(O.fullPath);
      return P.NODE_ENV !== "production" && (ee.startsWith("//") ? S(`Location "${p}" resolved to "${ee}". A resolved location cannot start with multiple slashes.`) : I.matched.length || S(`No match found for location with path "${p}"`)), N(O, I, {
        params: f(I.params),
        hash: ie(O.hash),
        redirectedFrom: void 0,
        href: ee
      });
    }
    if (P.NODE_ENV !== "production" && !Ce(p))
      return S(`router.resolve() was passed an invalid location. This will fail in production.
- Location:`, p), _({});
    let y;
    if (p.path != null)
      P.NODE_ENV !== "production" && "params" in p && !("name" in p) && // @ts-expect-error: the type is never
      Object.keys(p.params).length && S(`Path "${p.path}" was passed with params but they will be ignored. Use a named route alongside params instead.`), y = N({}, p, {
        path: Ke(n, p.path, w.path).path
      });
    else {
      const O = N({}, p.params);
      for (const I in O)
        O[I] == null && delete O[I];
      y = N({}, p, {
        params: u(O)
      }), w.params = u(w.params);
    }
    const b = t.resolve(y, w), V = p.hash || "";
    P.NODE_ENV !== "production" && V && !V.startsWith("#") && S(`A \`hash\` should always start with the character "#". Replace "${V}" with "#${V}".`), b.params = c(f(b.params));
    const A = go(r, N({}, p, {
      hash: co(V),
      path: b.path
    })), k = o.createHref(A);
    return P.NODE_ENV !== "production" && (k.startsWith("//") ? S(`Location "${p}" resolved to "${k}". A resolved location cannot start with multiple slashes.`) : b.matched.length || S(`No match found for location with path "${p.path != null ? p.path : p}"`)), N({
      fullPath: A,
      // keep the hash encoded so fullPath is effectively path + encodedQuery +
      // hash
      hash: V,
      query: (
        // if the user is using a custom query lib like qs, we might have
        // nested objects, so we keep the query as is, meaning it can contain
        // numbers at `$route.query`, but at the point, the user will have to
        // use their own type anyway.
        // https://github.com/vuejs/router/issues/328#issuecomment-649481567
        r === Mt ? Qo(p.query) : p.query || {}
      )
    }, b, {
      redirectedFrom: void 0,
      href: k
    });
  }
  function E(p) {
    return typeof p == "string" ? Ke(n, p, l.value.path) : N({}, p);
  }
  function R(p, w) {
    if (d !== p)
      return ce(8, {
        from: w,
        to: p
      });
  }
  function C(p) {
    return F(p);
  }
  function M(p) {
    return C(N(E(p), { replace: !0 }));
  }
  function U(p) {
    const w = p.matched[p.matched.length - 1];
    if (w && w.redirect) {
      const { redirect: y } = w;
      let b = typeof y == "function" ? y(p) : y;
      if (typeof b == "string" && (b = b.includes("?") || b.includes("#") ? b = E(b) : (
        // force empty params
        { path: b }
      ), b.params = {}), P.NODE_ENV !== "production" && b.path == null && !("name" in b))
        throw S(`Invalid redirect found:
${JSON.stringify(b, null, 2)}
 when navigating to "${p.fullPath}". A redirect must contain a name or path. This will break in production.`), new Error("Invalid redirect");
      return N({
        query: p.query,
        hash: p.hash,
        // avoid transferring params if the redirect has a path
        params: b.path != null ? {} : p.params
      }, b);
    }
  }
  function F(p, w) {
    const y = d = _(p), b = l.value, V = p.state, A = p.force, k = p.replace === !0, O = U(y);
    if (O)
      return F(
        N(E(O), {
          state: typeof O == "object" ? N({}, V, O.state) : V,
          force: A,
          replace: k
        }),
        // keep original redirectedFrom if it exists
        w || y
      );
    const I = y;
    I.redirectedFrom = w;
    let ee;
    return !A && kt(r, b, y) && (ee = ce(16, { to: I, from: b }), Et(
      b,
      b,
      // this is a push, the only way for it to be triggered from a
      // history.listen is with a redirect, which makes it become a push
      !0,
      // This cannot be the first navigation because the initial location
      // cannot be manually navigated to
      !1
    )), (ee ? Promise.resolve(ee) : vt(I, b)).catch((T) => z(T) ? (
      // navigation redirects still mark the router as ready
      z(
        T,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? T : Le(T)
    ) : (
      // reject any unknown error
      We(T, I, b)
    )).then((T) => {
      if (T) {
        if (z(
          T,
          2
          /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
        ))
          return P.NODE_ENV !== "production" && // we are redirecting to the same location we were already at
          kt(r, _(T.to), I) && // and we have done it a couple of times
          w && // @ts-expect-error: added only in dev
          (w._count = w._count ? (
            // @ts-expect-error
            w._count + 1
          ) : 1) > 30 ? (S(`Detected a possibly infinite redirection in a navigation guard when going from "${b.fullPath}" to "${I.fullPath}". Aborting to avoid a Stack Overflow.
 Are you always returning a new location within a navigation guard? That would lead to this error. Only return when redirecting or aborting, that should fix this. This might break in production if not fixed.`), Promise.reject(new Error("Infinite redirect in navigation guard"))) : F(
            // keep options
            N({
              // preserve an existing replacement but allow the redirect to override it
              replace: k
            }, E(T.to), {
              state: typeof T.to == "object" ? N({}, V, T.to.state) : V,
              force: A
            }),
            // preserve the original redirectedFrom if any
            w || I
          );
      } else
        T = wt(I, b, !0, k, V);
      return yt(I, b, T), T;
    });
  }
  function Mn(p, w) {
    const y = R(p, w);
    return y ? Promise.reject(y) : Promise.resolve();
  }
  function je(p) {
    const w = Se.values().next().value;
    return w && typeof w.runWithContext == "function" ? w.runWithContext(p) : p();
  }
  function vt(p, w) {
    let y;
    const [b, V, A] = ys(p, w);
    y = ze(b.reverse(), "beforeRouteLeave", p, w);
    for (const O of b)
      O.leaveGuards.forEach((I) => {
        y.push(X(I, p, w));
      });
    const k = Mn.bind(null, p, w);
    return y.push(k), re(y).then(() => {
      y = [];
      for (const O of s.list())
        y.push(X(O, p, w));
      return y.push(k), re(y);
    }).then(() => {
      y = ze(V, "beforeRouteUpdate", p, w);
      for (const O of V)
        O.updateGuards.forEach((I) => {
          y.push(X(I, p, w));
        });
      return y.push(k), re(y);
    }).then(() => {
      y = [];
      for (const O of A)
        if (O.beforeEnter)
          if (B(O.beforeEnter))
            for (const I of O.beforeEnter)
              y.push(X(I, p, w));
          else
            y.push(X(O.beforeEnter, p, w));
      return y.push(k), re(y);
    }).then(() => (p.matched.forEach((O) => O.enterCallbacks = {}), y = ze(A, "beforeRouteEnter", p, w, je), y.push(k), re(y))).then(() => {
      y = [];
      for (const O of i.list())
        y.push(X(O, p, w));
      return y.push(k), re(y);
    }).catch((O) => z(
      O,
      8
      /* ErrorTypes.NAVIGATION_CANCELLED */
    ) ? O : Promise.reject(O));
  }
  function yt(p, w, y) {
    a.list().forEach((b) => je(() => b(p, w, y)));
  }
  function wt(p, w, y, b, V) {
    const A = R(p, w);
    if (A)
      return A;
    const k = w === Y, O = q ? history.state : {};
    y && (b || k ? o.replace(p.fullPath, N({
      scroll: k && O && O.scroll
    }, V)) : o.push(p.fullPath, V)), l.value = p, Et(p, w, y, k), Le();
  }
  let fe;
  function Wn() {
    fe || (fe = o.listen((p, w, y) => {
      if (!bt.listening)
        return;
      const b = _(p), V = U(b);
      if (V) {
        F(N(V, { replace: !0, force: !0 }), b).catch(we);
        return;
      }
      d = b;
      const A = l.value;
      q && Eo(Vt(A.fullPath, y.delta), Te()), vt(b, A).catch((k) => z(
        k,
        12
        /* ErrorTypes.NAVIGATION_CANCELLED */
      ) ? k : z(
        k,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? (F(
        N(E(k.to), {
          force: !0
        }),
        b
        // avoid an uncaught rejection, let push call triggerError
      ).then((O) => {
        z(
          O,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && !y.delta && y.type === ae.pop && o.go(-1, !1);
      }).catch(we), Promise.reject()) : (y.delta && o.go(-y.delta, !1), We(k, b, A))).then((k) => {
        k = k || wt(
          // after navigation, all matched components are resolved
          b,
          A,
          !1
        ), k && (y.delta && // a new navigation has been triggered, so we do not want to revert, that will change the current history
        // entry while a different route is displayed
        !z(
          k,
          8
          /* ErrorTypes.NAVIGATION_CANCELLED */
        ) ? o.go(-y.delta, !1) : y.type === ae.pop && z(
          k,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && o.go(-1, !1)), yt(b, A, k);
      }).catch(we);
    }));
  }
  let Me = he(), _t = he(), Pe;
  function We(p, w, y) {
    Le(p);
    const b = _t.list();
    return b.length ? b.forEach((V) => V(p, w, y)) : (P.NODE_ENV !== "production" && S("uncaught error during route navigation:"), console.error(p)), Promise.reject(p);
  }
  function Ln() {
    return Pe && l.value !== Y ? Promise.resolve() : new Promise((p, w) => {
      Me.add([p, w]);
    });
  }
  function Le(p) {
    return Pe || (Pe = !p, Wn(), Me.list().forEach(([w, y]) => p ? y(p) : w()), Me.reset()), p;
  }
  function Et(p, w, y, b) {
    const { scrollBehavior: V } = e;
    if (!q || !V)
      return Promise.resolve();
    const A = !y && bo(Vt(p.fullPath, 0)) || (b || !y) && history.state && history.state.scroll || null;
    return ke().then(() => V(p, w, A)).then((k) => k && _o(k)).catch((k) => We(k, p, w));
  }
  const Be = (p) => o.go(p);
  let Fe;
  const Se = /* @__PURE__ */ new Set(), bt = {
    currentRoute: l,
    listening: !0,
    addRoute: h,
    removeRoute: m,
    clearRoutes: t.clearRoutes,
    hasRoute: v,
    getRoutes: g,
    resolve: _,
    options: e,
    push: C,
    replace: M,
    go: Be,
    back: () => Be(-1),
    forward: () => Be(1),
    beforeEach: s.add,
    beforeResolve: i.add,
    afterEach: a.add,
    onError: _t.add,
    isReady: Ln,
    install(p) {
      const w = this;
      p.component("RouterLink", es), p.component("RouterView", os), p.config.globalProperties.$router = w, Object.defineProperty(p.config.globalProperties, "$route", {
        enumerable: !0,
        get: () => W(l)
      }), q && // used for the initial navigation client side to avoid pushing
      // multiple times when the router is used in multiple apps
      !Fe && l.value === Y && (Fe = !0, C(o.location).catch((V) => {
        P.NODE_ENV !== "production" && S("Unexpected error when starting the router:", V);
      }));
      const y = {};
      for (const V in Y)
        Object.defineProperty(y, V, {
          get: () => l.value[V],
          enumerable: !0
        });
      p.provide(De, w), p.provide(mt, Kn(y)), p.provide(ut, l);
      const b = p.unmount;
      Se.add(p), p.unmount = function() {
        Se.delete(p), Se.size < 1 && (d = Y, fe && fe(), fe = null, l.value = Y, Fe = !1, Pe = !1), b();
      }, P.NODE_ENV !== "production" && q && as(p, w, t);
    }
  };
  function re(p) {
    return p.reduce((w, y) => w.then(() => je(y)), Promise.resolve());
  }
  return bt;
}
function ys(e, t) {
  const n = [], r = [], o = [], s = Math.max(t.matched.length, e.matched.length);
  for (let i = 0; i < s; i++) {
    const a = t.matched[i];
    a && (e.matched.find((d) => Z(d, a)) ? r.push(a) : n.push(a));
    const l = e.matched[i];
    l && (t.matched.find((d) => Z(d, l)) || o.push(l));
  }
  return [n, r, o];
}
function ws() {
  return J(De);
}
function _s(e) {
  return J(mt);
}
function Es(e) {
  const { immediately: t = !1, code: n } = e;
  let r = D(n);
  return t && (r = r()), r;
}
const _e = /* @__PURE__ */ new Map();
function bs(e) {
  if (!_e.has(e)) {
    const t = Symbol();
    return _e.set(e, t), t;
  }
  return _e.get(e);
}
function le(e, t) {
  var a, l;
  const n = Ue(e), r = Ps(n, t);
  if (r.size > 0) {
    const d = bs(e);
    ve(d, r);
  }
  const o = ne({ attached: { varMap: r, sid: e } });
  Cr({
    watchConfigs: n.py_watch || [],
    computedConfigs: n.web_computed || [],
    varMapGetter: o,
    sid: e
  }), (a = n.js_watch) == null || a.forEach((d) => {
    Br(d, o);
  }), (l = n.vue_watch) == null || l.forEach((d) => {
    Lr(d, o);
  });
  function s(d, c) {
    const u = Ue(d);
    if (!u.vfor)
      return;
    const { fi: f } = u.vfor;
    f && (r.get(f.id).value = c.index);
  }
  function i(d) {
    const { sid: c, value: u } = d;
    if (!c)
      return;
    const f = Ue(c), { id: h } = f.sp, m = r.get(h);
    m.value = u;
  }
  return {
    updateVforInfo: s,
    updateSlotPropValue: i
  };
}
function ne(e) {
  const { attached: t, sidCollector: n } = e || {}, [r, o, s] = Ss(n);
  t && r.set(t.sid, t.varMap);
  const i = o ? _s() : null, a = s ? ws() : null, l = o ? () => i : () => {
    throw new Error("Route params not found");
  }, d = s ? () => a : () => {
    throw new Error("Router not found");
  };
  function c(g) {
    const v = Qe(f(g));
    return tn(v, g.path ?? [], c);
  }
  function u(g) {
    const v = f(g);
    return gr(v, {
      paths: g.path,
      getBindableValueFn: c
    });
  }
  function f(g) {
    return Rr(g) ? () => l()[g.prop] : r.get(g.sid).get(g.id);
  }
  function h(g, v) {
    if (pt(g)) {
      const _ = f(g);
      if (g.path) {
        nn(_.value, g.path, v, c);
        return;
      }
      _.value = v;
      return;
    }
    throw new Error(`Unsupported output binding: ${g}`);
  }
  function m() {
    return d();
  }
  return {
    getValue: c,
    getRouter: m,
    getVueRefObject: u,
    updateValue: h,
    getVueRefObjectWithoutPath: f
  };
}
function An(e) {
  const t = _e.get(e);
  return J(t);
}
function Rs(e) {
  const t = An(e);
  if (t === void 0)
    throw new Error(`Scope not found: ${e}`);
  return t;
}
function Ps(e, t) {
  var o, s, i, a, l;
  const n = /* @__PURE__ */ new Map(), r = ne({
    attached: { varMap: n, sid: e.id }
  });
  if (e.data && e.data.forEach((d) => {
    n.set(d.id, d.value);
  }), e.jsFn && e.jsFn.forEach((d) => {
    const c = Es(d);
    n.set(d.id, () => c);
  }), e.vfor && (t != null && t.initVforInfo)) {
    const { fv: d, fi: c, fk: u } = e.vfor, { index: f = 0, keyValue: h = null, config: m } = t.initVforInfo, { sid: g } = m, v = Ur(g);
    if (d) {
      const _ = se(() => ({
        get() {
          const E = v.value;
          return Array.isArray(E) ? E[f] : Object.values(E)[f];
        },
        set(E) {
          const R = v.value;
          if (!Array.isArray(R)) {
            R[h] = E;
            return;
          }
          R[f] = E;
        }
      }));
      n.set(d.id, _);
    }
    c && n.set(c.id, H(f)), u && n.set(u.id, H(h));
  }
  if (e.sp) {
    const { id: d } = e.sp;
    n.set(d, H(null));
  }
  return (o = e.eRefs) == null || o.forEach((d) => {
    n.set(d.id, H(null));
  }), (s = e.refs) == null || s.forEach((d) => {
    const c = mr(d);
    n.set(d.id, c);
  }), (i = e.web_computed) == null || i.forEach((d) => {
    const c = yr(d);
    n.set(d.id, c);
  }), (a = e.js_computed) == null || a.forEach((d) => {
    const c = wr(
      d,
      r
    );
    n.set(d.id, c);
  }), (l = e.vue_computed) == null || l.forEach((d) => {
    const c = vr(
      d,
      r
    );
    n.set(d.id, c);
  }), n;
}
function Ss(e) {
  const t = /* @__PURE__ */ new Map();
  if (e) {
    const { sids: n, needRouteParams: r = !0, needRouter: o = !0 } = e;
    for (const s of n)
      t.set(s, Rs(s));
    return [t, r, o];
  }
  for (const n of _e.keys()) {
    const r = An(n);
    r !== void 0 && t.set(n, r);
  }
  return [t, !0, !0];
}
const Os = j(ks, {
  props: ["vforConfig", "vforIndex", "vforKeyValue"]
});
function ks(e) {
  const { sid: t, items: n = [] } = e.vforConfig, { updateVforInfo: r } = le(t, {
    initVforInfo: {
      config: e.vforConfig,
      index: e.vforIndex,
      keyValue: e.vforKeyValue
    }
  });
  return () => (r(t, {
    index: e.vforIndex,
    keyValue: e.vforKeyValue
  }), n.length === 1 ? ue(n[0]) : n.map((o) => ue(o)));
}
function Ht(e) {
  const { start: t = 0, end: n, step: r = 1 } = e;
  let o = [];
  if (r > 0)
    for (let s = t; s < n; s += r)
      o.push(s);
  else
    for (let s = t; s > n; s += r)
      o.push(s);
  return o;
}
const $n = j(Ns, {
  props: ["config"]
});
function Ns(e) {
  const { fkey: t, tsGroup: n = {} } = e.config, r = ne(), s = Is(t ?? "index"), i = As(e.config, r);
  return Fr(e.config, i), () => {
    const a = zn(i.value, (...l) => {
      const d = l[0], c = l[2] !== void 0, u = c ? l[2] : l[1], f = c ? l[1] : u, h = s(d, u);
      return x(Os, {
        key: h,
        vforValue: d,
        vforIndex: u,
        vforKeyValue: f,
        vforConfig: e.config
      });
    });
    return n && Object.keys(n).length > 0 ? x(Jt, n, {
      default: () => a
    }) : a;
  };
}
const Vs = (e) => e, Cs = (e, t) => t;
function Is(e) {
  const t = fr(e);
  return typeof t == "function" ? t : e === "item" ? Vs : Cs;
}
function As(e, t) {
  const { type: n, value: r } = e.array, o = n === nt.range;
  if (n === nt.const || o && typeof r == "number") {
    const i = o ? Ht({
      end: Math.max(0, r)
    }) : r;
    return se(() => ({
      get() {
        return i;
      },
      set() {
        throw new Error("Cannot set value to constant array");
      }
    }));
  }
  if (o) {
    const i = r, a = t.getVueRefObject(i);
    return se(() => ({
      get() {
        return Ht({
          end: Math.max(0, a.value)
        });
      },
      set() {
        throw new Error("Cannot set value to range array");
      }
    }));
  }
  return se(() => {
    const i = t.getVueRefObject(
      r
    );
    return {
      get() {
        return i.value;
      },
      set(a) {
        i.value = a;
      }
    };
  });
}
const xn = j($s, {
  props: ["config"]
});
function $s(e) {
  const { sid: t, items: n, on: r } = e.config;
  Re(t) && le(t);
  const o = ne();
  return () => (typeof r == "boolean" ? r : o.getValue(r)) ? n.map((i) => ue(i)) : void 0;
}
const Kt = j(xs, {
  props: ["slotConfig"]
});
function xs(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Re(t) && le(t), () => n.map((r) => ue(r));
}
const qe = ":default", Tn = j(Ts, {
  props: ["config"]
});
function Ts(e) {
  const { on: t, caseValues: n, slots: r, sid: o } = e.config;
  Re(o) && le(o);
  const s = ne();
  return () => {
    const i = s.getValue(t), a = n.map((l, d) => {
      const c = d.toString(), u = r[c];
      return l === i ? x(Kt, { slotConfig: u, key: c }) : null;
    }).filter(Boolean);
    return a.length === 0 && qe in r ? x(Kt, {
      slotConfig: r[qe],
      key: qe
    }) : a;
  };
}
function Ds(e, t) {
  return Object.assign(
    {},
    ...Object.entries(e ?? {}).map(([n, r]) => {
      const o = r.map((a) => {
        if (a.type === "web") {
          const l = js(a, t);
          return Ms(a, l, t);
        } else {
          if (a.type === "vue")
            return Ls(a, t);
          if (a.type === "js")
            return Ws(a, t);
        }
        throw new Error(`unknown event type ${a}`);
      }), i = D(
        " (...args)=> Promise.all(promises(...args))",
        {
          promises: (...a) => o.map(async (l) => {
            await l(...a);
          })
        }
      );
      return { [n]: i };
    })
  );
}
function js(e, t) {
  const { inputs: n = [] } = e;
  return (...r) => n.map(({ value: o, type: s }) => {
    if (s === K.EventContext) {
      const { path: i } = o;
      if (i.startsWith(":")) {
        const a = i.slice(1);
        return D(a)(...r);
      }
      return Mr(r[0], i.split("."));
    }
    return s === K.Ref ? t.getValue(o) : o;
  });
}
function Ms(e, t, n) {
  async function r(...o) {
    const s = t(...o), i = an({
      config: e.preSetup,
      varGetter: n
    });
    try {
      i.run();
      const a = await sn().eventSend(e, s);
      if (!a)
        return;
      $e(a, e.sets, n);
    } finally {
      i.tryReset();
    }
  }
  return r;
}
function Ws(e, t) {
  const { sets: n, code: r, inputs: o = [] } = e, s = D(r);
  function i(...a) {
    const l = o.map(({ value: c, type: u }) => {
      if (u === K.EventContext) {
        if (c.path.startsWith(":")) {
          const f = c.path.slice(1);
          return D(f)(...a);
        }
        return jr(a[0], c.path.split("."));
      }
      if (u === K.Ref)
        return un(t.getValue(c));
      if (u === K.Data)
        return c;
      if (u === K.JsFn)
        return t.getValue(c);
      throw new Error(`unknown input type ${u}`);
    }), d = s(...l);
    if (n !== void 0) {
      const u = n.length === 1 ? [d] : d, f = u.map((h) => h === void 0 ? 1 : 0);
      $e(
        { values: u, types: f },
        n,
        t
      );
    }
  }
  return i;
}
function Ls(e, t) {
  const { code: n, inputs: r = {} } = e, o = xe(
    r,
    (a) => a.type !== K.Data ? t.getVueRefObject(a.value) : a.value
  ), s = D(n, o);
  function i(...a) {
    s(...a);
  }
  return i;
}
function Bs(e, t) {
  const n = [];
  (e.bStyle || []).forEach((s) => {
    Array.isArray(s) ? n.push(
      ...s.map((i) => t.getValue(i))
    ) : n.push(
      xe(
        s,
        (i) => t.getValue(i)
      )
    );
  });
  const r = qn([e.style || {}, n]);
  return {
    hasStyle: r && Object.keys(r).length > 0,
    styles: r
  };
}
function Fs(e, t) {
  const n = e.classes;
  if (!n)
    return null;
  if (typeof n == "string")
    return Ne(n);
  const { str: r, map: o, bind: s } = n, i = [];
  return r && i.push(r), o && i.push(
    xe(
      o,
      (a) => t.getValue(a)
    )
  ), s && i.push(...s.map((a) => t.getValue(a))), Ne(i);
}
function Ie(e, t = !0) {
  if (!(typeof e != "object" || e === null)) {
    if (Array.isArray(e)) {
      t && e.forEach((n) => Ie(n, !0));
      return;
    }
    for (const [n, r] of Object.entries(e))
      if (n.startsWith(":"))
        try {
          e[n.slice(1)] = new Function(`return (${r})`)(), delete e[n];
        } catch (o) {
          console.error(
            `Error while converting ${n} attribute to function:`,
            o
          );
        }
      else
        t && Ie(r, !0);
  }
}
function Us(e, t) {
  const n = e.startsWith(":");
  return n && (e = e.slice(1), t = D(t)), { name: e, value: t, isFunc: n };
}
function Hs(e, t, n) {
  var o;
  const r = {};
  return Pt(e.bProps || {}, (s, i) => {
    const a = n.getValue(s);
    be(a) || (Ie(a), r[i] = Ks(a, i));
  }), (o = e.proxyProps) == null || o.forEach((s) => {
    const i = n.getValue(s);
    typeof i == "object" && Pt(i, (a, l) => {
      const { name: d, value: c } = Us(l, a);
      r[d] = c;
    });
  }), { ...t, ...r };
}
function Ks(e, t) {
  return t === "innerText" ? Ae(e) : e;
}
const Gs = j(zs, {
  props: ["slotPropValue", "config"]
});
function zs(e) {
  const { sid: t, items: n } = e.config, r = Re(t) ? le(t).updateSlotPropValue : qs;
  return () => (r({ sid: t, value: e.slotPropValue }), n.map((o) => ue(o)));
}
function qs() {
}
function Qs(e, t) {
  if (!e.slots)
    return null;
  const n = e.slots ?? {};
  return t ? ft(n[":"]) : cn(n, { keyFn: (i) => i === ":" ? "default" : i, valueFn: (i) => (a) => i.use_prop ? Js(a, i) : ft(i) });
}
function Js(e, t) {
  return x(Gs, { config: t, slotPropValue: e });
}
function Ys(e, t, n) {
  const r = [], { dir: o = [] } = t;
  return o.forEach((s) => {
    const { sys: i, name: a, arg: l, value: d, mf: c } = s;
    if (a === "vmodel") {
      const u = n.getVueRefObject(d);
      if (e = Je(e, {
        [`onUpdate:${l}`]: (f) => {
          u.value = f;
        }
      }), i === 1) {
        const f = c ? Object.fromEntries(c.map((h) => [h, !0])) : {};
        r.push([Qn, u.value, void 0, f]);
      } else
        e = Je(e, {
          [l]: u.value
        });
    } else if (a === "vshow") {
      const u = n.getVueRefObject(d);
      r.push([Jn, u.value]);
    } else
      console.warn(`Directive ${a} is not supported yet`);
  }), Yn(e, r);
}
function Xs(e, t, n) {
  const { eRef: r } = t;
  return r ? Je(e, { ref: n.getVueRefObject(r) }) : e;
}
const Zs = j(ei, {
  props: ["config"]
});
function ei(e) {
  const { config: t } = e, n = ne({
    sidCollector: new ti(t).getCollectInfo()
  }), r = t.props ?? {};
  return Ie(r, !0), () => {
    const { tag: o } = t, s = typeof o == "string" ? o : n.getValue(o), i = Xn(s), a = typeof i == "string", l = Fs(t, n), { styles: d, hasStyle: c } = Bs(t, n), u = Ds(t.events ?? {}, n), f = Qs(t, a), h = Hs(t, r, n), m = Zn({
      ...h,
      ...u
    }) || {};
    c && (m.style = d), l && (m.class = l);
    let g = x(i, { ...m }, f);
    return g = Xs(g, t, n), Ys(g, t, n);
  };
}
class ti {
  constructor(t) {
    $(this, "sids", /* @__PURE__ */ new Set());
    $(this, "needRouteParams", !0);
    $(this, "needRouter", !0);
    this.config = t;
  }
  /**
   * getCollectFn
   */
  getCollectInfo() {
    const { eRef: t, dir: n, classes: r, bProps: o, proxyProps: s, bStyle: i, events: a } = this.config;
    if (t && this._tryExtractSidToCollection(t), n && n.forEach((l) => {
      this._tryExtractSidToCollection(l.value), this._extendWithPaths(l.value);
    }), r && typeof r != "string") {
      const { map: l, bind: d } = r;
      l && Object.values(l).forEach((c) => {
        this._tryExtractSidToCollection(c), this._extendWithPaths(c);
      }), d && d.forEach((c) => {
        this._tryExtractSidToCollection(c), this._extendWithPaths(c);
      });
    }
    return o && Object.values(o).forEach((l) => {
      this._tryExtractSidToCollection(l), this._extendWithPaths(l);
    }), s && s.forEach((l) => {
      this._tryExtractSidToCollection(l), this._extendWithPaths(l);
    }), i && i.forEach((l) => {
      Array.isArray(l) ? l.forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      }) : Object.values(l).forEach((d) => {
        this._tryExtractSidToCollection(d), this._extendWithPaths(d);
      });
    }), a && Object.values(a).forEach((l) => {
      this._handleEventInputs(l), this._handleEventSets(l);
    }), {
      sids: this.sids,
      needRouteParams: this.needRouteParams,
      needRouter: this.needRouter
    };
  }
  _tryExtractSidToCollection(t) {
    rn(t) && this.sids.add(t.sid);
  }
  _handleEventInputs(t) {
    t.forEach((n) => {
      if (n.type === "js" || n.type === "web") {
        const { inputs: r } = n;
        r == null || r.forEach((o) => {
          if (o.type === K.Ref) {
            const s = o.value;
            this._tryExtractSidToCollection(s), this._extendWithPaths(s);
          }
        });
      } else if (n.type === "vue") {
        const { inputs: r } = n;
        if (r) {
          const o = Object.values(r);
          o == null || o.forEach((s) => {
            if (s.type === K.Ref) {
              const i = s.value;
              this._tryExtractSidToCollection(i), this._extendWithPaths(i);
            }
          });
        }
      }
    });
  }
  _handleEventSets(t) {
    t.forEach((n) => {
      if (n.type === "js" || n.type === "web") {
        const { sets: r } = n;
        r == null || r.forEach((o) => {
          pt(o.ref) && (this.sids.add(o.ref.sid), this._extendWithPaths(o.ref));
        });
      }
    });
  }
  _extendWithPaths(t) {
    if (!t.path)
      return;
    const n = [];
    for (n.push(...t.path); n.length > 0; ) {
      const r = n.pop();
      if (r === void 0)
        break;
      if (hr(r)) {
        const o = pr(r);
        this._tryExtractSidToCollection(o), o.path && n.push(...o.path);
      }
    }
  }
}
function ue(e, t) {
  return _r(e) ? x($n, { config: e, key: t }) : Er(e) ? x(xn, { config: e, key: t }) : br(e) ? x(Tn, { config: e, key: t }) : x(Zs, { config: e, key: t });
}
function ft(e, t) {
  return x(Dn, { slotConfig: e, key: t });
}
const Dn = j(ni, {
  props: ["slotConfig"]
});
function ni(e) {
  const { sid: t, items: n } = e.slotConfig;
  return Re(t) && le(t), () => n.map((r) => ue(r));
}
function ri(e, t) {
  const { state: n, isReady: r, isLoading: o } = lr(async () => {
    let s = e;
    const i = t;
    if (!s && !i)
      throw new Error("Either config or configUrl must be provided");
    if (!s && i && (s = await (await fetch(i)).json()), !s)
      throw new Error("Failed to load config");
    return s;
  }, {});
  return { config: n, isReady: r, isLoading: o };
}
function oi(e) {
  const t = Q(!1), n = Q("");
  function r(o, s) {
    let i;
    return s.component ? i = `Error captured from component:tag: ${s.component.tag} ; id: ${s.component.id} ` : i = "Error captured from app init", console.group(i), console.error("Component:", s.component), console.error("Error:", o), console.groupEnd(), e && (t.value = !0, n.value = `${i} ${o.message}`), !1;
  }
  return er(r), { hasError: t, errorMessage: n };
}
const si = {
  class: "app-box insta-themes",
  "data-scaling": "100%"
}, ii = {
  key: 0,
  style: { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
}, ai = {
  key: 0,
  style: { color: "red", "font-size": "1.2em", margin: "1rem", border: "1px dashed red", padding: "1rem" }
}, ci = /* @__PURE__ */ j({
  __name: "App",
  props: {
    config: {},
    meta: {},
    configUrl: {}
  },
  setup(e) {
    const t = e, { debug: n = !1 } = t.meta, { config: r, isLoading: o } = ri(
      t.config,
      t.configUrl
    );
    G(r, (a) => {
      a.url && (ir({
        mode: t.meta.mode,
        version: t.meta.version,
        queryPath: a.url.path,
        pathParams: a.url.params,
        webServerInfo: a.webInfo
      }), kr(t.meta.mode)), ar(a);
    });
    const { hasError: s, errorMessage: i } = oi(n);
    return (a, l) => (ge(), me("div", si, [
      W(o) ? (ge(), me("div", ii, l[0] || (l[0] = [
        tr("p", { style: { margin: "auto" } }, "Loading ...", -1)
      ]))) : (ge(), me("div", {
        key: 1,
        class: Ne(["insta-main", W(r).class])
      }, [
        nr(W(Dn), { "slot-config": W(r) }, null, 8, ["slot-config"]),
        W(s) ? (ge(), me("div", ai, Ae(W(i)), 1)) : rr("", !0)
      ], 2))
    ]));
  }
});
function ui(e, { slots: t }) {
  const { name: n = "fade", tag: r } = e;
  return () => x(
    Jt,
    { name: n, tag: r },
    {
      default: t.default
    }
  );
}
const li = j(ui, {
  props: ["name", "tag"]
});
function fi(e) {
  const { content: t, r: n = 0 } = e, r = ne(), o = n === 1 ? () => r.getValue(t) : () => t;
  return () => Ae(o());
}
const di = j(fi, {
  props: ["content", "r"]
});
function hi(e) {
  return `i-size-${e}`;
}
function pi(e) {
  return e ? `i-weight-${e}` : "";
}
function gi(e) {
  return e ? `i-text-align-${e}` : "";
}
const mi = /* @__PURE__ */ j({
  __name: "Heading",
  props: {
    text: {},
    size: {},
    weight: {},
    align: {}
  },
  setup(e) {
    const t = e, n = L(() => [
      hi(t.size ?? "6"),
      pi(t.weight),
      gi(t.align)
    ]);
    return (r, o) => (ge(), me("h1", {
      class: Ne(["insta-Heading", n.value])
    }, Ae(r.text), 3));
  }
});
function vi(e) {
  if (!e.router)
    throw new Error("Router config is not provided.");
  const { routes: t, kAlive: n = !1 } = e.router;
  return t.map(
    (o) => jn(o, n)
  );
}
function jn(e, t) {
  var a;
  const { server: n = !1, vueItem: r } = e, o = () => {
    if (n)
      throw new Error("Server-side rendering is not supported yet.");
    return Promise.resolve(yi(e, t));
  }, s = (a = r.children) == null ? void 0 : a.map(
    (l) => jn(l, t)
  ), i = {
    ...r,
    children: s,
    component: o
  };
  return r.component.length === 0 && delete i.component, s === void 0 && delete i.children, i;
}
function yi(e, t) {
  const { sid: n, vueItem: r } = e, { path: o, component: s } = r, i = ft(
    {
      items: s,
      sid: n
    },
    o
  ), a = x(or, null, i);
  return t ? x(sr, null, () => i) : a;
}
function wi(e, t) {
  const { mode: n = "hash" } = t.router, r = n === "hash" ? ko() : n === "memory" ? Oo() : En();
  e.use(
    vs({
      history: r,
      routes: vi(t)
    })
  );
}
function bi(e, t) {
  e.component("insta-ui", ci), e.component("vif", xn), e.component("vfor", $n), e.component("match", Tn), e.component("ts-group", li), e.component("content", di), e.component("heading", mi), t.router && wi(e, t);
}
export {
  Ie as convertDynamicProperties,
  bi as install
};
//# sourceMappingURL=insta-ui.js.map
