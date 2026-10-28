// Simule l'API Google Sheets (fetch) au-dessus des données de mock.js
(function(){
  const mcpP = window.claude.use("mcp"); delete window.claude;
  const J = o => new Response(JSON.stringify(o), {status:200, headers:{"Content-Type":"application/json"}});
  const of = window.fetch.bind(window); window.__api = [];
  window.fetch = async (url, opt = {}) => {
    url = String(url); const m = opt.method || "GET";
    if (url.includes("oauth2/v3/userinfo")) return J({email:"alane@test.be"});
    if (url.includes("oauth2.googleapis.com/revoke")) return J({});
    if (!url.startsWith("https://sheets.googleapis.com/v4/spreadsheets")) return of(url, opt);
    window.__api.push(m + " " + decodeURIComponent(url.slice(46, 160)));
    if (window.__hang) return new Promise((_, rej) => opt.signal && opt.signal.addEventListener("abort", () => rej(new DOMException("Aborted", "AbortError"))));
    if (window.__down) throw new TypeError("Failed to fetch");
    if (window.__fail) return new Response(JSON.stringify({error:{message:"x"}}), {status:window.__fail});
    const mcp = await mcpP, call = (t, i) => mcp.callTool("x", t, i).then(r => r.payload);
    const u = new URL(url), path = decodeURIComponent(u.pathname.replace("/v4/spreadsheets", "")), body = opt.body ? JSON.parse(opt.body) : null;
    if (path === "" || path === "/") { const id = "NEW" + Date.now(); const b = {}; body.sheets.forEach(s => b[s.properties.title] = [[]]); window.__sheets[id] = b; return J({spreadsheetId:id}); }
    let mm;
    if ((mm = path.match(/^\/([^/]+)\/values:batchGet$/))) return J({valueRanges:await Promise.all(u.searchParams.getAll("ranges").map(r => call("get_values", {spreadsheetId:mm[1], range:r})))});
    if ((mm = path.match(/^\/([^/]+)\/values:batchUpdate$/))) { for (const d of body.data) await call("update_values", {spreadsheetId:mm[1], range:d.range, values:d.values}); return J({}); }
    if ((mm = path.match(/^\/([^/]+):batchUpdate$/))) { (window.__req = window.__req || []).push(...body.requests);
      const replies = body.requests.map(r => { if (!r.addSheet) return {}; window.__sheets[mm[1]][r.addSheet.properties.title] = [[]]; return {addSheet:{properties:{sheetId:4242, title:r.addSheet.properties.title}}}; });
      return J({replies}); }
    if ((mm = path.match(/^\/([^/]+)\/values\/(.+):append$/))) return J(await call("append_values", {spreadsheetId:mm[1], range:mm[2], values:body.values}));
    if ((mm = path.match(/^\/([^/]+)\/values\/(.+)$/))) {
      if (!window.__sheets[mm[1]]) return new Response("{}", {status:404});
      return J(await call(m === "PUT" ? "update_values" : "get_values", {spreadsheetId:mm[1], range:mm[2], values:body && body.values}));
    }
    if ((mm = path.match(/^\/([^/]+)$/))) { if (!window.__sheets[mm[1]]) return new Response("{}", {status:404}); return J(await call("get_spreadsheet", {spreadsheetId:mm[1]})); }
    return new Response("{}", {status:400});
  };
})();
