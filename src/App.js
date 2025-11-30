import logo from './logo.svg';
import './App.css';
import { useState } from "react";
import Home from "./components/Home";
import Environment from "./components/Environment";
import Ethics from "./components/Ethics";
import Involve from "./components/Involve";
import Mental from "./components/Mental";
import Sources from "./components/Sources";


function App() {
  const [page, setPage] = useState("Home");
  const renderPage = () => {
    if (page === "Home") return <Home />;
    if (page === "Environment") return <Environment />;
    if (page === "Ethics") return <Ethics />;
    if (page === "Mental") return <Mental />;
    if (page === "Involve") return <Involve />;
    if (page === "Sources") return <Sources />;
  };
  
  return (
    <div className="App">
      <div className="Side_column"><nav className="Main_Navigation">
        <ul className="Left_Nav">
          <li><button className={page==="Home" ? "active" : ""}onClick={() => setPage("Home")}>Home</button></li>
          <li><button className={page==="Environment" ? "active" : ""}onClick={() => setPage("Environment")}>Environmental</button></li>
          <li><button className={page==="Ethics" ? "active" : ""}onClick={() => setPage("Ethics")}>Ethics</button></li>
          <li><button className={page==="Mental" ? "active" : ""}onClick={() => setPage("Mental")}>Mental Health</button></li>
          <li><button className={page==="Involve" ? "active" : ""}onClick={() => setPage("Involve")}>Get Involved</button></li>
          <li><button className={page==="Sources" ? "active" : ""}onClick={() => setPage("Sources")}>Sources</button></li>
        </ul>
      </nav></div>
      <hr />
      {renderPage()}
    </div>
  );
}

export default App;
