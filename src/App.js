import logo from './logo.svg';
import './App.css';
import { useState } from "react";
import Home from "./components/Home";
import Environment from "./components/Environment";
import Ethics from "./components/Ethics";
import Involve from "./components/Involve";
import Mental from "./components/Mental";


function App() {
  const [page, setPage] = useState("Home");
  const renderPage = () => {
    if (page === "Home") return <Home />;
    if (page === "Environment") return <Environment />;
    if (page === "Ethics") return <Ethics />;
    if (page === "Mental") return <Mental />;
    if (page === "Involve") return <Involve />;
  };
  
  return (
    <div className="App">
      <div className="Side_column"><nav className="Main_Navigation">
        <ul className="Left_Nav">
          <li><button onClick={() => setPage("Home")}>Home</button></li>
          <li><button onClick={() => setPage("Environment")}>Environment</button></li>
          <li><button onClick={() => setPage("Ethics")}>Ethics</button></li>
          <li><button onClick={() => setPage("Mental")}>Mental</button></li>
          <li><button onClick={() => setPage("Involve")}>Involve</button></li>
        </ul>
      </nav></div>
      <hr />
      {renderPage()}
    </div>
  );
}

export default App;
