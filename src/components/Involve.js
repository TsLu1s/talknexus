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
            <p style={{ textAlign: "left" }}> If you feel like you are turning to AI for help on tasks like organizing, brainstorming, problem solving, studying, or anything else. There are a plethora of platforms that can provide you with resources that are much less harmful than generative AI.</p>
            <p style={{ textAlign: "left" }}> <a href="https://www.tgwstudio.com/five-alternatives-to-ai-and-chatgpt/">https://www.tgwstudio.com/five-alternatives-to-ai-and-chatgpt/</a> </p>
            <h4 style={{ textAlign: "left" }}> Local Involvement</h4>
            <p style={{ textAlign: "left" }}> No matter where you are there are ways that you can get involved in the push for safe ai. Listed below are some ways you can get involved locally! </p>
            <p style={{ textAlign: "left" }}> ** insert local movements </p>
            <p style={{ textAlign: "left" }}> ** insert local petitions</p>
            <p style={{ textAlign: "left" }}> ** insert local organizations </p>

        </div>
    )
}
export default Involve;
export { TextBlock4 };