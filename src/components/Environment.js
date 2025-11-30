import React from "react";
import "../App.css";
import "./Environment.css"; 
import EnvImpact from "../images/EnvImpact.jpeg";



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
        <div className="ENVrow"> 
            <div className="ENVcolumn">
            <h3 style={{ textAlign: "left" }}> Overview </h3>
            <p style={{ textAlign: "left" }}> Most have heard that AI has negative impacts on the environment, but is there an understanding of how signifcant it is? </p>
            <h4 style={{ textAlign: "left" }}> Energy</h4>
            <p style={{ textAlign: "left" }}> One of the largest contributers to environemental impacts is the energy consumption that AI requires. </p>
            <p style={{ textAlign: "left" }}> Generally, every step in AI usage requires an immesnse amount of energy. This extends to the building of data centers, training the AI, and then the maintaince required for the AI to function. </p>
            <h4 style={{ textAlign: "left" }}> Water</h4>
            <p style={{ textAlign: "left" }}> All major steps of the AI supply chain from data center cooling systems to semiconductor production compete with communities for the same municipal fresh water used for drinking.​ </p>
            <p style={{ textAlign: "left" }}> AI's water consumption is measured in three categories according to Li et al. (2025):​ 
                <br />Scope 1: On-site​ Water drawn from source and evaporated through data center cooling systems​ 
                <br />Scope 2: Off-site​ Water drawn from source and evaporated during electricity generation​ 
                <br />Scope 3: Supply chain​ Water evaporated or otherwise consumed across chip manufacturing and other primary AI computing supply chain elements​ </p>
            <h4 style={{ textAlign: "left" }}> Summary</h4>
            <p style={{ textAlign: "left" }}> Overall, AI usage and its rapid expansion are having significant effects on our environment. It has been seen that these issues are primarily affecting communities that are already at high risks, social, economically, and environmentally. Drawing attention to this issues and understanding the role we play is crucial to making change in this field.  </p>
            </div>
            <div className="ENVcolumn">
            <img src={EnvImpact} alt="Environmental Impact" />
            </div>
        </div>
    );
}



export default Environment;
export { TextBlock2 };



/* function TextBlock2(){
    return ( 
        <div className='environmentText2'> 
            <h3 style={{ textAlign: "left" }}> Overview </h3>
            <p style={{ textAlign: "left" }}> Most have heard that AI has negative impacts on the environment, but is there an understanding of how signifcant it is? </p>
            <h4 style={{ textAlign: "left" }}> Energy</h4>
            <p style={{ textAlign: "left" }}> One of the largest contributers to environemental impacts is the energy consumption that AI requires. </p>
            <p style={{ textAlign: "left" }}> Generally, every step in AI usage requires an immesnse amount of energy. This extends to the building of data centers, training the AI, and then the maintaince required for the AI to function. </p>
            <h4 style={{ textAlign: "left" }}> Water</h4>
            <p style={{ textAlign: "left" }}> All major steps of the AI supply chain from data center cooling systems to semiconductor production compete with communities for the same municipal fresh water used for drinking.​ </p>
            <p style={{ textAlign: "left" }}> AI's water consumption is measured in three categories according to Li et al. (2025):​ 
                <br />Scope 1: On-site​ Water drawn from source and evaporated through data center cooling systems​ 
                <br />Scope 2: Off-site​ Water drawn from source and evaporated during electricity generation​ 
                <br />Scope 3: Supply chain​ Water evaporated or otherwise consumed across chip manufacturing and other primary AI computing supply chain elements​ </p>
            <h4 style={{ textAlign: "left" }}> Summary</h4>
            <p style={{ textAlign: "left" }}> Overall, AI usage and its rapid expansion are having significant effects on our environment. It has been seen that these issues are primarily affecting communities that are already at high risks, social, economically, and environmentally. Drawing attention to this issues and understanding the role we play is crucial to making change in this field.  </p>
            <img src={imagePlaceholder} alt="Environmental Impact" />
        </div>
    );
} */