import React from "react";
// import "../App.css";
import "./mental.css";
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { createTheme, ThemeProvider } from '@mui/material/styles';

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
        <AccordionDetails sx={{backgroundColor: 'secondary.light'}}>
          <Typography>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse
            malesuada lacus ex, sit amet blandit leo lobortis eget.
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
        <AccordionDetails sx={{backgroundColor: 'secondary.light'}}>
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