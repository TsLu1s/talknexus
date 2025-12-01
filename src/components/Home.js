import React from "react";
import App from "../App";
import "../App.css";
import "./Home.css";
import AIUse from "../images/AI_Usage.png"
import AIAware from "../images/AI_Awareness_chart.png"
import Prior from "../images/Prior_Knowledge.png"

function Home() {
    return(
        <>
            <div className="homepage font-link">
                <h2>Safe-AI Initiative</h2>
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
            <div className="HomePictures">
                <p>To further emphasize the motivations for this project, we have conducted a survey among college students to guage perceptions of the AI industry. 
                    We recieved 41 responses for this survey from students with a variety of academic backgrounds.
                </p>
                <img className = "homeImage1" src = {AIUse} alt="AI usage among college students" />
                <p>The graph above displays the reported amount of AI usage among respondents with a majority of 63.4% reporting at least moderate use.</p>
                <img className = "homeImage2" src = {Prior} alt="Ratings of prior knowledge of AI systems" />
                <p>The graph above depicts responses on a 1 to 5 scale of understanding of AI models and their operations. 
                    We see an almost ideal curve in this data, indicating an adequate sample to represent college students in general. 
                </p>
                <img className = "homeImage3" src = {AIAware} alt ="Comparison of issue awareness and issue concern"/>
                <p>Respondents were asked to rate their awareness of the AI industry's impacts on 5 highlighted issues and then asked to rate their personal concern for said issues on the same 1 to 5 scale. 
                    The table above contains the average rating of awareness and concern for each category. 
                </p>
                <p>The average rating of awareness for all but one of the highlighted issues was lower than the average rating of conern. 
                    This emphasizes the importance of our mission as frequent users of AI tools are not aware of the effects increased AI usage is already having. 
                </p>
            </div>
        </div>
    )
}

export default Home;
export { TextBlock1 };