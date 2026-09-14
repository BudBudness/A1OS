import React from "react";
import {HashRouter,Routes,Route,Link} from "react-router-dom";
import Artists from "./pages/Artists.jsx";
import Releases from "./pages/Releases.jsx";
import Catalog from "./pages/Catalog.jsx";
import Events from "./pages/Events.jsx";
import Fans from "./pages/Fans.jsx";
import Media from "./pages/Media.jsx";
import Revenue from "./pages/Revenue.jsx";
import Analytics from "./pages/Analytics.jsx";

export default function App() {
  return <HashRouter><main className="app">
    <header><h1>Music / Artist</h1><p>A1OS frontend vertical</p></header>
    <nav><Link to="/">Dashboard</Link><Link to="/artists">Artists</Link>
<Link to="/releases">Releases</Link>
<Link to="/catalog">Catalog</Link>
<Link to="/events">Events</Link>
<Link to="/fans">Fans</Link>
<Link to="/media">Media</Link>
<Link to="/revenue">Revenue</Link>
<Link to="/analytics">Analytics</Link></nav>
    <Routes><Route path="/" element={<section><h2>Dashboard</h2><p>Music / Artist platform dashboard.</p></section>} />
      <Route path="/artists" element={<Artists />} />
<Route path="/releases" element={<Releases />} />
<Route path="/catalog" element={<Catalog />} />
<Route path="/events" element={<Events />} />
<Route path="/fans" element={<Fans />} />
<Route path="/media" element={<Media />} />
<Route path="/revenue" element={<Revenue />} />
<Route path="/analytics" element={<Analytics />} />
    </Routes>
  </main></HashRouter>;
}
