import React from "react";
import App from "../App";
import "../App.css";
import "./Home.css";

function Home() {
    return(
        <>
            <div className="homepage font-link">
                <h2>Safe-AI Initiative</h2>
                <p>AI might not be the best thing ever!</p>
                <TextBlock1 />
            </div>

        </>
    );
}

function TextBlock1(){
    return ( 
        <div className='homepageText1'> 
            <p style={{ textAlign: "left" }}> Welcome to Safe-AI Initiative! </p>
            <p style={{ textAlign: "left" }}> Here, our goal is to raise awareness about some of the explored downsides to AI usage. Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. Lorem ipsum dolor sit amet consectetur adipiscing elit. Quisque faucibus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class </p>
            <p style={{ textAlign: "left" }}> aptent taciti sociosqu. Ad litora torquent per conubia nostra inceptos himenaeos. bus ex sapien vitae pellentesque sem placerat. In id cursus mi pretium tellus duis convallis. Tempus leo eu aenean sed diam urna tempor. Pulvinar vivamus fringilla lacus nec metus bibendum egestas. Iaculis massa nisl malesuada lacinia integer nunc posuere. Ut hendrerit semper vel class </p>
        </div>
    )
}

export default Home;
export { TextBlock1 };