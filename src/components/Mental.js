import React from "react";
import "../App.css";
import "./mental.css";

function Mental() {
    return(
        <div className="mentalpage font-link">
        <iframe
        src="http://localhost:8501/?embed=true"
        style={{...Mental.style, height: "700px", width: "100%"}}
        ></iframe>
        </div>
    );
}

export default Mental;