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
      <header className="App-header">
      </header>
      <nav>
        <button onClick={() => setPage("Home")}>Home</button>
        <button onClick={() => setPage("Environment")}>Environment</button>
        <button onClick={() => setPage("Ethics")}>Ethics</button>
        <button onClick={() => setPage("Mental")}>Mental</button>
        <button onClick={() => setPage("Involve")}>Involve</button>
      </nav>
      <hr />
      {renderPage()}
    </div>
  );
}

export default App;
