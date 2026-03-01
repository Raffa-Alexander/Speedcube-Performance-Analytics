
# Speedcube-Performance-Analytics

Could data science be a useful tool to plan an efficient training routine for speedcubers?

<img align="right" width="150" src="https://github.com/user-attachments/assets/aac119db-4de2-4152-b8c7-c43ed2ea5f65">
Since 2018 I have solved the Rubik's Cube over 70,000 times and kept tracking each result with a timing software.

This project uses dynamic dashboards written in Python to analyze long-term performance trends, and statistical patterns in order to understand and improve solving efficiency.

Users can dynamically select date ranges, adjust moving average windows, define Sub-X thresholds, and filter minimum session sizes. All visualizations update in real time, enabling exploratory analysis of performance patterns. 

Link to access it: https://speedcube-performance-analytics-kaunryakgyjudrxiqzznvj.streamlit.app/
<p align="center"><img width="1200" alt="image" src="https://github.com/user-attachments/assets/cdc70c77-6673-4dd1-a257-314e8350e31f" /></p>

# How to use
Anyone who wants to measure performance can dowonload this program and substitute the "data.csv" file with their own. It has two columns separated by **semicolon**: "date" with the format "dd/mm/yyyy hh:mm" and "time": "hh:mm.ss". The list of solves doesn't need to be sorted. Be sure following libraries are installed in your computer: streamlit, pandas, plotly. Use the "start.bat" file to run the program.

# Objectives
1. Analyze long-term performance trends
2. Measure consistency and variance over time
3. Identify impact of behavioral patterns on performance:

   a) Day of the week and time of the day

   b) Solves amount per year

   c) Sessions size:
<p align="center"><img width="1000" alt="image" src="https://github.com/user-attachments/assets/9c168e59-0d4f-4bb2-93f3-67d15a82f7b3" /></p>

   d) Weekly sessions distribution: "For a certain amount of solves in a week, is it better to distribute it into several sessions or do fewer larger ones?
<p align="center"><img width="1000" alt="image" src="https://github.com/user-attachments/assets/10a01569-0734-46d3-915f-b3e8560aebe6" /></p>



5. Track probability of sub-8 performance
6. Apply statistical methods to performance modeling

# Technical Stack
- Python
- Pandas (data processing)
- Plotly (interactive visualization)
- Streamlit (dashboard interface)
- Timing software: Prisma Puzzle Timer

# Why This Project?
This project combines:
- Data analysis
- Behavioral performance analysis
- Software development
- It transforms a long-term personal dataset into a quantitative performance study.

My personal goal is to achieve and sustain an average solve time below 8 seconds.

