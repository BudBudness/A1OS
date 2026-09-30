export async function GET(){return Response.json({status:"ready",service:"little-oaks-web",checks:{application:"ok"},timestamp:new Date().toISOString()});}
