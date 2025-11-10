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
            <h3> Our goal </h3>
            <p style={{ textAlign: "left" }}> Our goal is to provide users with an ample amount of information about AI 	and potential issues that are arising with its growing usage. We hope this raises awareness and provides resources for some of the lesser explored downsides of AI usage and development. </p>
            <h3> Our approach </h3>
            <p style={{ textAlign: "left" }}> On our page we hope to provide education on how our increasing AI usage can have negative effects on the environment, mental health, and society. We have done this through providing easy to understand, interactive, and visual information.  </p>
            <p style={{ textAlign: "left" }}> We don’t want this to be a page filled with negativity but rather realistic education. To show a light at the end of the tunnel, we have provided alternate resources for AI and some ways to get involved/advocate for safer AI usage!  </p>
            <h3> What is AI? </h3>
            <p style={{ textAlign: "left" }}> Before we dive into the downsides, we want to provide some simple definitions so that there is a general understanding of what AI is. </p>
            <p style={{ textAlign: "left" }}> AI is a blanket term that encompasses a variety of technologies that enable computers (machines) to mimic human intelligence and decision making. </p>
            <p style={{ textAlign: "left" }}> Here, our focus is on AI that is most commonly used. Think. chatbots like chatgpt, customer service bots, and other ML technologies of the sort </p>
            <p style={{ textAlign: "left" }}> Now that there is a general understanding of what AI is and our focus, feel free to dig into the rest of the site! </p>
        </div>
    )
}

export default Home;
export { TextBlock1 };