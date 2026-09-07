const baseUrl="/v1/construction";
async function request(path,options={}){const r=await fetch(`${baseUrl}${path}`,{...options,headers:{"Content-Type":"application/json",...(options.headers||{})}});if(!r.ok)throw new Error(`Construction API ${r.status}`);return r.status===204?null:r.json()}
export const api={provider:"a1os-platform-api",baseUrl,get:p=>request(p),post:(p,b)=>request(p,{method:"POST",body:JSON.stringify({data:b})}),delete:p=>request(p,{method:"DELETE"})};
