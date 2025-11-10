import React from "react";
import "../App.css";
import "./Environment.css"; 

function Environment() {
    return(
        <div className="environmentpage font-link">
            <h2>Safe-AI: Environmental concerns</h2>
            <p>AI might not be the best thing ever!</p>
            <TextBlock2 />
        </div>
    );
}
function TextBlock2(){
    return ( 
        <div className='environmentText2'> 
            <h3 style={{ textAlign: "left" }}> Overview </h3>
            <p style={{ textAlign: "left" }}> Most have heard that AI has negative impacts on the environment, but is there an understanding of how signifcant it is? </p>
            <h4 style={{ textAlign: "left" }}> Energy</h4>
            <p style={{ textAlign: "left" }}> AI requires a huge amount of energy to train and maintain AI models. </p>
            <h4 style={{ textAlign: "left" }}> Water</h4>
            <p style={{ textAlign: "left" }}> All major steps of the AI supply chain from data center cooling systems to semiconductor production compete with communities for the same municipal fresh water used for drinking.​ </p>
            <p style={{ textAlign: "left" }}> AI's water consumption is measured in three categories according to Li et al. (2025):​ Scope 1: On-site​ Water drawn from source and evaporated through data center cooling systems​ Scope 2: Off-site​ Water drawn from source and evaporated during electricity generation​ Scope 3: Supply chain​ Water evaporated or otherwise consumed across chip manufacturing and other primary AI computing supply chain elements​ </p>
        </div>
    );
}

export default Environment;
export { TextBlock2 };