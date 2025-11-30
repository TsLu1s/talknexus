import React from "react";
import "../App.css";
import "./Ethics.css";
import AIEthics from "../images/AIEthics.png";
import humanEffects from "../images/humanEffects.png";


function Ethics() {
    return(
        <div className="ethicspage font-link">
            <h2>Safe-AI: Ethical concerns</h2>
            <p>AI might not be the best thing ever!</p>
            <TextBlock3 />
        </div>
    );
}

function TextBlock3(){
    return ( 
        <div className="Ethicsrow"> 
            <div className="Ethicscolumn">
            <h3 style={{ textAlign: "left" }}> Overview </h3>
            <p style={{ textAlign: "left" }}> Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class </p>
            <h4 style={{ textAlign: "left" }}> Misinformation</h4>
            <p style={{ textAlign: "left" }}> aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. bus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class </p>
            <h4 style={{ textAlign: "left" }}> Stealing Work</h4>
            <p style={{ textAlign: "left" }}> aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. bus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class </p>
        </div>
        <div className= "Ethicscolumn">
            <img src={AIEthics} alt="Ethical Impact" />
            <p>Generative AI risks and Challenges that could result in human effects </p>
            <img src={humanEffects} alt="Human Effects" />
        </div>
    </div>
    )
}

export default Ethics;
export { TextBlock3 };