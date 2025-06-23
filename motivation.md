# Project Motivation & Learnings

> *A reflection on building a real-world data analytics pipeline during the final*
> *month of a 3-month Data Analytics Bootcamp at neuefische, Germany.*

---

## 1. Project work background

The project was completed during the final month of our 3-month Data Analytics Bootcamp at neuefische.  
In the 2-month learning phase, we deepened our skills in Python and Pandas, SQL and Tableau in practically organized lessons.  
There were a total of 12 students in our course and the focus was on coding challenges on the respective topics, which had to be mastered in alternating 2-3 groups.  
After the learning phase, we were then given 4 weeks to implement our project.

---

## 2. Why We Chose This Project

Our team brought complementary expertise to this capstone project. **Artur's 10+ years in the automotive** industry—including roles as a Quality Engineer at Ford and other OEMs—provided deep domain knowledge,  
while **Jan's 5+ years in Finance and 2+ years in Business Operations** brought analytical rigor and strategic thinking to market analysis.  
We didn't want to analyze toy datasets or recreate existing case studies. We wanted to tackle a real problem in a market we could understand from both technical and business perspectives.

Germany's automotive landscape represents one of Europe's most complex and rapidly evolving markets. Between 2020 and 2025, the industry faced unprecedented challenges: electrification mandates, supply chain disruptions, changing consumer preferences, and regulatory shifts. Having experienced these changes from industry and financial operations viewpoints, we were determined to quantify their impact using **official KBA (Kraftfahrt-Bundesamt) registration data**.

Our objectives were threefold:
- **Domain-driven analysis**: Leverage our combined automotive and business backgrounds to ask the right questions and interpret results meaningfully
- **Technical skill development**: Master Python, SQL, and Tableau through hands-on application on complex, real-world datasets  
- **Portfolio creation**: Build a public project that demonstrates both analytical capabilities and cross-functional collaboration for future data-related job applications

This wasn't just an academic exercise—it was about combining our diverse professional experiences with new technical skills to create something genuinely valuable.

---

## 3. Timeline and Pivot

Initially, we planned to analyze **vehicle defects and repair patterns**—a topic directly aligned with Artur's quality engineering background and highly relevant for both consumers and manufacturers from a business risk perspective that resonated with Jan's operations experience.

However, we quickly discovered the harsh reality of data availability: **comprehensive vehicle failure data simply isn't publicly accessible** in Germany. This forced a strategic pivot that, in retrospect, became an opportunity rather than a setback.

We shifted focus to **new vehicle registrations (Neuzulassungen)** and **fleet composition (Bestand)** data—both rich, publicly available datasets from the KBA. This pivot enabled a broader market-level analysis covering:
- Electrification trends across different vehicle segments
- Regional adoption patterns for alternative fuel types  
- Brand market share evolution during critical industry transition years
- Commercial vs. private vehicle registration patterns

Jan's business operations background proved invaluable in reframing our research questions around market dynamics and stakeholder impact rather than just technical failure analysis. The lesson learned: sometimes the most valuable insights come from adapting your approach to available data rather than forcing unavailable data to fit your original hypothesis.

---

## 4. Technical Challenges & Solutions

Building this pipeline was a masterclass in "learning by doing"—and unlearning assumptions about data quality.

### Data Collection & Schema Evolution
The KBA publishes data across spanning multiple statistical series. Each series follows different formatting conventions, and—crucially—the schema evolved between 2020-2022 and 2023-2025 periods.  
**Challenge**: Automating extraction from inconsistent file formats while handling German-specific formatting (decimal separators, special characters, encoding issues).

### Data Cleaning at Scale
Every time we thought the data was clean, the next analysis step revealed new inconsistencies. Processing **822,248 records** across 15 datasets meant small errors compounded quickly.  
**Challenge**: Inconsistent headers, mixed data types, regional naming variations, and temporal format differences across datasets.  

### Pivot for Visualization
To create meaningful visualizations in Tableau, we needed to restructure the data from wide format (multiple columns per time period) to long format (single column with date dimension).  
**Challenge**: Complex pivot operations across multiple datasets while preserving data integrity and relationships.  

### Time Management Under Pressure
With only 4 weeks for the complete project, we had to make tough scoping decisions. Originally planned to implement `dbt` for transformation governance, but ultimately prioritized core functionality.  
**Learning**: Project scoping and prioritization are as important as technical skills. Better to deliver a complete, working solution than an incomplete ambitious one. Having two perspectives helped us make more balanced trade-off decisions.

---

## 5. Key Learnings

### Technical Insights
- **Data is never as clean as it appears initially**: Every new analysis revealed additional data quality issues requiring iterative improvement
- **End-to-end thinking matters**: Building a pipeline from raw government files to interactive dashboards highlighted dependencies and integration challenges often missed in isolated exercises  
- **Documentation as a forcing function**: Writing comprehensive documentation improved our code quality and made debugging significantly easier

### Professional Development
- **Complementary expertise accelerates analysis**: Artur's automotive background helped us ask better technical questions, while Jan's business operations experience ensured we framed results meaningfully for different stakeholders
- **Real datasets teach different lessons than clean samples**: Working with government data formats, encoding issues, and schema evolution provided insights no classroom exercise could replicate
- **Pressure testing reveals gaps**: Time constraints exposed which skills were truly internalized versus superficially understood
- **Cross-functional collaboration improves outcomes**: Our different professional backgrounds led to more comprehensive analysis and better business relevance

### Process Improvements
- **Validation early and often**: Implementing data quality checks at each pipeline stage prevented downstream issues
- **Modular code pays dividends**: Reusable functions made iterative improvements manageable  
- **Balance perfection with delivery**: Knowing when to stop refining and start sharing results
- **Divide and conquer works**: Splitting responsibilities based on strengths allowed us to tackle more complex challenges than either could handle alone

---

## 6. What's Next?

This project serves as both a portfolio piece for data-related job applications and a foundation for continued development. It demonstrates not just technical capabilities, but also cross-functional collaboration and the ability to deliver results under constraints.

### Immediate Enhancements
- **dbt Integration**: Implement proper transformation governance with testing and documentation
- **Data Pipeline Automation**: Schedule regular updates as new KBA data becomes available
- **Enhanced Visualizations**: Expand Tableau dashboards with interactive storytelling features

### Strategic Extensions  
- **Multi-source Integration**: Incorporate charging infrastructure data, demographic information, and economic indicators
- **Predictive Modeling**: Apply forecasting techniques to registration trends and market evolution
- **International Expansion**: Extend analysis to other European markets for comparative insights

### Career Integration
This project bridges our diverse professional backgrounds with our data analytics future. It showcases the unique value proposition we bring as a team: **technical skills grounded in deep industry understanding and business acumen**. For potential employers, it demonstrates not just what we can do with data, but how we think about complex business problems across domains we know intimately.

The repository remains actively maintained and will evolve alongside our continued learning in the data space—a living demonstration of both technical growth and cross-functional collaboration.

---

*This project reflects both who we are (automotive professional and business operations expert, systematic thinkers) and who we're becoming (data-driven analysts, continuous learners). It represents the intersection of domain knowledge, business understanding, and technical capability that we believe creates the most valuable analytical insights.*




