import React from "react";
import "../App.css";
import "./Sources.css"; 



function Sources() {
    return(
        <div className="sourcespage font-link">
            <h2>Safe-AI: Sources</h2>
            <TextBlock2 />
        </div>
    );
}
function TextBlock2(){
    return ( 
        <div className="row"> 
            <div className="column">
            <p style={{ textAlign: "Left" }}>[1]  C. Huang, Z. Zhang, B. Mao, and X. Yao, “An Overview of Artificial Intelligence Ethics,” IEEE Xplore, Aug. 2023. https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9844014 (accessed Sep. 08, 2025). </p>
            <p style={{ textAlign: "left" }}>[2]  R. D. Quint, “Boom in Data Centers: Energy Parks and Technology’s Future,” IEEE Xplore, Aug. 2025. https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=11131371 (accessed Sep. 08, 2025). </p>
            <p style={{ textAlign: "left" }}>[3]  M. T. Baldassarre, D. Caivano, B. Fernández Nieto, and A. Ragone, “Ethics-driven Incentives: Supporting Government Policies for Responsible AI Innovation,” IEEE Intelligent Systems, vol. 40, no. 4, pp. 1–10, 2025, doi: https://doi.org/10.1109/mis.2025.3583222. </p>
            <p style={{ textAlign: "left" }}>[4]  P. Sinlapanuntakul and M. Zachry, “Impacts of AI on Human Designers: A Systematic Literature Review,” IEEE Xplore, Sep. 2025. https://ieeexplore.ieee.org/document/11125867 </p>
            <p style={{ textAlign: "left" }}>[5]  S. Shan, W. Ding, J. Passananti, S. Wu, H. Zheng, and B. Zhao, “Nightshade: Prompt-Specific Poisoning Attacks on Text-to-Image Generative Models,” Oct. 2023. Available: https://people.cs.uchicago.edu/~ravenben/publications/pdf/nightshade-oakland24.pdf </p>
            <p style={{ textAlign: "left" }}>[6]  R. Baeza-Yates and U. M. Fayyad, “Responsible AI: An Urgent Mandate,” IEEE Intelligent Systems, vol. 39, no. 1, pp. 12–17, Jan. 2024, doi: https://doi.org/10.1109/mis.2023.3343488. </p>
            <p style={{ textAlign: "left" }}>[7]  E. Rath, S. Armstrong, and R. Gorman, “AI Chaperones Are (Really) All You Need to Prevent Parasocial Relationships with Chatbots,” Sept. 2025. Available: https://arxiv.org/pdf/2508.15748. </p>
            <p style={{ textAlign: "left" }}>[8]  K. Savchuk, “Microplastics and our health: what the science says,” News Center, Jan. 2025. Available: https://med.stanford.edu/news/insights/2025/01/microplastics-in-body-polluted-tiny-plastic-fragments.html </p>
            <p style={{ textAlign: "left" }}>[9]  UNCTAD, “AI marker projected to hit $4.8 trillion by 2033, emerging as dominant Frontier Technology,” UN Trade and Development (UNCTAD), Jan. 2025. Available: https://unctad.org/news/ai-market-projected-hit-48-trillion-2033-emerging-dominant-frontier-technology </p>
            <p style={{ textAlign: "left" }}>[10] Real Good AI, Available: https://www.realgoodai.org/. </p>
            <p style={{ textAlign: "left" }}>[11] Stop Killer Robots, Available: https://www.stopkillerrobots.org/. </p>
            <p style={{ textAlign: "left" }}>[12] Singh, S. (2025, August 16). CHATGPT statistics (2025) - daily & monthly active users. DemandSage. https://www.demandsage.com/chatgpt-statistics/  </p>
            </div> 
            <div className="column">
            </div>
        </div>
    );
}

export default Sources;
export { TextBlock2 };