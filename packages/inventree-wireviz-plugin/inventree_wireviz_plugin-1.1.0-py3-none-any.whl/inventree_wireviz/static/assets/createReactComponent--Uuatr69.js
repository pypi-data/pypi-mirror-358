const l="0.2.3";function p(e){var t;const o=((t=e==null?void 0:e.version)==null?void 0:t.inventree)||"";l!=o&&console.info(`Plugin version mismatch! Expected version ${l}, got ${o}`)}/**
 * @license @tabler/icons-react v3.34.0 - MIT
 *
 * This source code is licensed under the MIT license.
 * See the LICENSE file in the root directory of this source tree.
 */var f={outline:{xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"},filled:{xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"currentColor",stroke:"none"}};/**
 * @license @tabler/icons-react v3.34.0 - MIT
 *
 * This source code is licensed under the MIT license.
 * See the LICENSE file in the root directory of this source tree.
 */const k=window.React.forwardRef,r=window.React.createElement,E=(e,t,o,c)=>{const i=k(({color:w="currentColor",size:s=24,stroke:d=2,title:a,className:u,children:n,...v},h)=>r("svg",{ref:h,...f[e],width:s,height:s,className:["tabler-icon",`tabler-icon-${t}`,u].join(" "),strokeWidth:d,stroke:w,...v},[a&&r("title",{key:"svg-title"},a),...c.map(([g,m])=>r(g,m)),...Array.isArray(n)?n:[n]]));return i.displayName=`${o}`,i};export{p as a,E as c};
