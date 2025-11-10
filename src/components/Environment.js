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
            <p style={{ textAlign: "left" }}> Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class </p>
            <h4 style={{ textAlign: "left" }}> Energy</h4>
            <p style={{ textAlign: "left" }}> aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. bus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class </p>
            <h4 style={{ textAlign: "left" }}> Water</h4>
            <p style={{ textAlign: "left" }}> aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. bus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class </p>
        </div>
    )
}

export default Environment;
export { TextBlock2 };