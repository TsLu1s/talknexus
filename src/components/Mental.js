import React from "react";
// import "../App.css";
import "./mental.css";
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import dataset from "../images/dataset.png";
import models from "../images/models.png";
import confusion from "../images/confusion.png";
import { List, ListItem } from "@mui/material";
const theme = createTheme({
  palette: {
    primary: {
      main: '#344F1F',
      // light: will be calculated from palette.primary.main,
      // dark: will be calculated from palette.primary.main,
      // contrastText: will be calculated to contrast with palette.primary.main
    },
    secondary: {
      main: '#F2EAD3',
    //   light: '#F5EBFF',
      // dark: will be calculated from palette.secondary.main,
    //   contrastText: '#47008F',
    },
  },
});

export default function Accordions() {
  return (
     <div>
    <ThemeProvider theme={theme}>
      <Accordion defaultExpanded  sx={{ 
  }}>
        <AccordionSummary
        color="primary"
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1-content"
          id="panel1-header"
          sx={{backgroundColor: 'primary.dark',
                color: 'secondary.light',
                '&hover': {
                    backgroundColor: 'primary.dark',
                }
          }}    
        >
          <Typography component="span">Background</Typography>
        </AccordionSummary>
        <AccordionDetails sx={{backgroundColor: 'secondary.light', textAlign: 'left'}}>
          <Typography>
            <h3>Mental Health effects of AI-specific parasocial bonding and AI Psychosis</h3>
            AI Psychosis, though it may sound like the grim spectre of a cyberpunk sci-fi dystopia, has emerged as a frighteningly real term in the scientific vernacular of the present [7].
            In the paper which inspired the demonstration app embedded within this page, Emma Rath, Stuart Armstrong, and Rebecca Gorman cite specific cases of LLM interaction which incited self-harming behaviors among teens, deadly delusions in an elderly man, and tragic suicidal ideation in vulnerable individuals [7].
            Rath et al. place the blame for these dire events squarely on a lack of safeguards against parasocial interaction [7].
            <br></br>
            <br></br>
            A parasocial relationship, in the traditional sense, is a one-sided attachment or perceived social bond between an individual human and the public persona of another human--usually a celebrity or micro-celebrity--and can prove to be dangerous for individuals affected by delusionally parasocial fans [7].
            Humans who regularly interact with AI agents, however, are themselves at risk of developing dangerously parasocial trust, bonds, and emotional attachments [7].The term "AI Psychosis" has even emerged to describe this phenomenon [7]. In their work, Rath et al. describe how the same anthropomorphic, often sycophantic, language features designed to help LLMs approximate human conversation can inadvertently deceive users into believing they are experiencing "reciprocal interaction" [7]. These foundations for parasocial interaction can then be further compounded by the tendency of LLMs to hallucinate false or misleading information, further negatively impacting the mental or physical health of the user [7].
            <br></br>
            <br></br>
            In the interest of developing safeguards against the formation of such parasocial bonds with agentic applications, Rath et al. prototyped a chaperone overlay system, itself an AI agent with specific constraints, designed to detect parasocial dynamics in chatbot conversations and actively replace potentially harmful responses with non-harmful alternatives [7].
            Inspired by this work, we have closely followed their methodology, with some differences documented below on this page, to create a working proof-of-concept embedded below.
            <br></br>
            <br></br>
            <h3>The interactive demonstration</h3>
            This chatbot demonstration application presents familiar LLM interface design with a few key differences:
            <br></br>
            <List>
            <ListItem>
            - A single prompt entry will query two instances of the same chat model--multiple models are available through the dropdown selector on the left.
            </ListItem>
            <ListItem>
            - The left column will display an unfiltered response directly from the selected chat model.
            </ListItem>
            <ListItem>
            - The right column will pass the initial response to a chaperone agent, which will analyze the response and conversation context against criteria for parasocial and non-parasocial conversation dynamics.
            </ListItem>
            <ListItem>
            - Responses flagged by the chaperone agent are not displayed, and the underlying chat model is re-prompted with specific instructions to avoid the type of response which was just flagged.
            </ListItem>
            <ListItem>
            - Re-prompted responses are again analyzed by the chaperone. If the response receives a passing grade, it is shown to the user.
            </ListItem>
            <ListItem>
            - For a quick demonstration of this function, we recommend selecting sarahv2, an 'AI Girlfriend' chat model available through the Ollama API, and asking simple questions.
            </ListItem>
            </List>
          


            
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel2-content"
          id="panel2-header"
          sx={{backgroundColor: 'primary.dark',
                color: 'secondary.light',
                '&hover': {
                    backgroundColor: 'primary.dark',
                }
          }}    
        >
          <Typography component="span">Chatbot Demonstration</Typography>
        </AccordionSummary>
        <AccordionDetails sx={{backgroundColor: 'secondary.light'}}>
          <Mental></Mental>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel2-content"
          id="panel2-header"
          sx={{backgroundColor: 'primary.dark',
                color: 'secondary.light',
                '&hover': {
                    backgroundColor: 'primary.dark',
                }
          }}    
        >
          <Typography component="span">Chatbot Methodology</Typography>
        </AccordionSummary>
        <AccordionDetails sx={{backgroundColor: 'secondary.light', textAlign: 'left'}}>
          In the interest of developing a working proof-of-concept with minimal use of cloud-based AI resources, we have closely, but not explicitly, followed Rath et al.'s methodology for evaluating chaperone effectiveness. Due to the lack of available organic data on genuine human-AI parasocial dynamics [7], we have chosen to rely on simulated conversations to provide the basis for testing the effectiveness of chaperone model candidates and prompt structures. While Rath et al. used a set of 30 simulated conversations (10 parasocial and 20 non-parasocial) generated via Claude Sonnet [7], we chose to extend this method to a pool of 50 simulated conversations, each containing an initial user prompt, a parasocial response, and a non-parasocial alternative response.
          <br></br>
          <br></br>
          <img src={dataset} width={850}></img>
          <br></br>
          This snippet of our simulated conversations dataset shows the structure of our sample data.
          <br></br>
          <br></br>
          After de-labeling the response entries, we broke the dataset into separate 50-sample sections of true and false responses and designed an isolated copy of the chaperone overlay’s program structure to iteratively test potential model choices and prompt designs on each sample pool. In their original chaperone work, Rath et al. used the Claude API as the base model for their chaperone design but indicated a potential for small-parameter Ollama models to demonstrate equal performance with additional analysis iterations. With this in mind, we used Llama 3.2 8B Instruct to prototype our prompt design into its current state. After prototyping on the initial model, we tested the prompt structure and sample data against four additional small-parameter models from various developers available through Ollama Server’s fetch API. 
          <br></br>
          <br></br>
          <img src={models} width={850}></img>
          <br></br>
          Additional candidate models with descriptions.
          <br></br>
          <br></br>
          During testing of additional model candidates, we strived to maintain the same prompt structure as was developed using Llama3.2. Apart from minor changes in section tagging and prompt placement between models, such as Deepseek’s requirement to place system prompts within the model’s chat invocation instead of as a separate template, we made no major changes to the original prompt structure, and any minor changes were tested in reverse on our original development model with no negative impact to results. 
          <br></br>
          <br></br>
          <img src={confusion} width={850}></img>
          <br></br>
          This table shows the combined results from all candidate chaperone models on the testing set of 50 parasocial (positive) and 50 non-parasocial (negative) sample responses.
          <br></br>
          <br></br>
          As can be seen here, Marco-o1 slightly outperformed Llama3.2 by producing a lower number of false negatives. Both models correctly classified all 50 parasocial conversation samples, which is consistent with the results Rath et al. produced using the Claude API [7]. Our results, however, differ slightly from Rath et al’s in a higher rate of false positives. While Rath et al. listed 0 false positives for their chaperone when operating on unanimous sensitivity, where all five analysis iterations must report a parasocial dynamic [7], we produced between a 4% and 14% rate of false positives on our two top-performing models. It is worth noting that although Rath et al. suggested that smaller parameter models ought to require additional chaperone analysis passes to produce equitable results to larger models, we were able to closely adhere to the authors’ results without use of additional passes while testing on a larger dataset.  
          This suggests that, in future work, additional tweaks to prompt structure and further exploration into the potential of small-parameter chain-of-thought reasoning models may yield a 0% rate of false positives. Although it is not a concern for our project, which was developed using local computing resources, future work which relies on cloud APIs could benefit from small-parameter chaperones with a lower overhead token cost. 
        </AccordionDetails>
      </Accordion>
      </ThemeProvider>
    </div>
  );
}

function Mental() {
    return(
        <div className="mentalpage font-link">
        <iframe
        title="Chatbot"
        src="http://localhost:8501/?embed=true"
        style={{...Mental.style, height: "700px", width: "100%"}}
        ></iframe>
        </div>
    );
}

// export default Body;