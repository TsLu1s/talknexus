import React from "react";
import "../App.css";
import "./involve.css";

function Involve() {
    return(
        <div className="involvepage font-link">
            <h2>Safe-AI: Get involved</h2>
            <p>AI might not be the best thing ever!</p>
            <TextBlock4 />
        </div>

    );
}

function TextBlock4(){
    return ( 
        <div className='involveText4'> 
            <h3 style={{ textAlign: "left" }}> Overview </h3>
            <p style={{ textAlign: "left" }}> Along with providing education information, we want to encourage seeking out more education, alternates to using AI, and ways to get involved. </p>
            <h4 style={{ textAlign: "left" }}> More Info</h4>
            <p style={{ textAlign: "left" }}> We aren't the only site pushing for this education, here are some resources that we used as inspiration and will provide you with more info!</p>
            <p style={{ textAlign: "left" }}> <a href="https://www.realgoodai.org/">https://www.realgoodai.org/</a> </p>
            <p style={{ textAlign: "left" }}> <a href="https://www.stopkillerrobots.org/">https://www.stopkillerrobots.org/</a> </p>
            <h4 style={{ textAlign: "left" }}> Alternate Resources</h4>
            <p style={{ textAlign: "left" }}> aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. bus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class </p>
            <h4 style={{ textAlign: "left" }}> Local Involvement</h4>
            <p style={{ textAlign: "left" }}> ** insert local movements, petitions, organizations, etc. ** </p>

        </div>
    )
}
export default Involve;
export { TextBlock4 };