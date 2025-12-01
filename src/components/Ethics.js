import React from "react";
import "../App.css";
import "./Ethics.css";
import AIEthics from "../images/AIEthics.png";
import humanEffects from "../images/humanEffects.png";
import { List, ListItem, ListSubheader } from "@mui/material";


function Ethics() {
    return(
        <div className="ethicspage font-link">
            <h2>Safe-AI: Ethical concerns</h2>
            <TextBlock3 />
        </div>
    );
}

function TextBlock3(){
    return ( 
        <div className="Ethicsrow"> 
            <div className="Ethicscolumn">
            <h2 style={{ textAlign: "left" }}> Overview </h2>
            <p style={{ textAlign: "left" }}>In their 2023 paper titled "An Overview of Artificial Intelligence Ethics", Huang et al. [1] provide a simplified (yet comprehensive) breakdown of AI ethics issues in three levels of scope. These scopes provide form and structure for the organization of this website. Each scope is listed here with some corresponding examples of ethical topics:</p>
            <p style={{textAlign: "left"}}>
                <List>
                    <ListSubheader sx={{backgroundColor: '#344F1F', color: '#F5EBFF'}}><h3>Individual level:</h3></ListSubheader>
                    <ListItem divider='true'>
                        <p>AI Psychosis, data mining, individual overreliance on AI assistance [4][7][10].</p></ListItem>
                    <ListSubheader sx={{backgroundColor: '#344F1F', color: '#F5EBFF'}}><h3>Societal level:</h3></ListSubheader>
                    <ListItem divider='true'><p>AI-assisted weapons or policing, implicit and explicit algorithmic bias, mass surveillance tools, targeted spread of misinformation through social media, intellectual property theft, elimination of high-skill human creative professions [4][5][11].</p></ListItem>
                    <ListSubheader sx={{backgroundColor: '#344F1F', color: '#F5EBFF'}}><h3>Environmental level:</h3></ListSubheader>
                    <ListItem divider='true'><p>Water and energy demand, carbon footprint, effects of data centers on surrounding communities​ [1][2][10][13].</p></ListItem>
                </List>
            </p>
            <p style={{textAlign: 'left'}}>
                When addressing the overarching term "AI Ethics," scopes such as these are indispensable for effective education, as they keep discussion grounded in real-world issues. Although unfriendly superintelligences may be a concern of the more distant future, rampant AI development poses much more pressing threats in the present to humanity and the planet. And these threats we are already equpped to deal with, given enough popular support and public awareness.
            </p>
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