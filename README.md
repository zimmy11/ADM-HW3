# **HomeWork 3 - Michelin restaurants in Italy**
The goal of this project is to develop a **Michelin Restaurant Search Engine** that allows food enthusiasts to discover Michelin-starred restaurants across Italy based on their unique preferences.

This search engine will help users explore Italy’s finest dining experiences by offering two types of search options: a **Conjunctive Search Engine** and a **Ranked Search Engine**. In addition, we were asked to visualize the most relevant restaurant through *folium* returned by our Search Engine.

All the data we've worked on was crawled from the [Michelin Guide website](https://guide.michelin.com/en/it/restaurants) to retrieve their HTML content, then parsed the HTML to extract relevant information, and finally stored the extracted data in a TSV file for further analysis.
___
<div style="text-align: center;">
  <img src="https://camo.githubusercontent.com/b6ea01a634e081edbcb6c43ccf1284bc9280e42a07712f8c766a980c69dc5d29/68747470733a2f2f612e73746f7279626c6f6b2e636f6d2f662f3132353537362f3234343878313232302f333237626232346433322f6865726f5f7570646174655f6d696368656c696e2e6a70672f6d2f3132323478302f66696c746572733a666f726d6174287765627029" alt="Michelin Picture"/>
</div>

____

## **Project Structure**
___
- In this repository you can find:

    <br>


  > __main.ipynb__:
  
    <br>

    
    - A Jupyter Notebook where we gather all the answers and the explanations to the Research and Algorithmic Questions.
 
    <br>
     
  > __functions.py__:
    
    <br>

    - A python script where we have define the functions we have used in the `main.ipynb`
    
    <br>

  > __DataCollections/*__:

    <br>

    - We gather all the Python functions such as `engine.py`, `parser.py` and `crawler.py` to crawl from the website and parse the relevant information 
     
    <be>
[Click here to have access to the whole Project Directory Structure](https://uithub.com/zimmy11/ADM-HW3/edit/main)
___
## Visualizing the Most Relevant Restaurants with Folium
The map is available at the [following link](https://nbviewer.org/github/zimmy11/ADM-HW3/blob/main/restaurants_map.html)

Detailed explanation of the Folium Plug-in used is in Part 4 of Main.ipynb Notebook, while some example on how to use its most interesting functionalities are explained [here](https://github.com/zimmy11/ADM-HW3/tree/main/Examples/FoliumMap_Plugins)
## Streamlit Interface
To enhance user interaction with the Michelin Restaurant Search Engine, we developed a Streamlit application. This interface allows users to input search queries, view results, and visualize restaurant locations dynamically.

### If u want to try run it locally
clone the repository from GitHub to your local machine:

```bash
https://github.com/zimmy11/ADM-HW3.git
```
Move into the project directory:
```bash
cd ADM-HW3
```
Install the required packages using requirements.txt:
```bash
pip install -r requirements.txt
```

### Part 2: Search Engine
```bash
streamlit run Part2Streamlit.py
```
<p float="left">
  <img src="Examples/StreamLit%20Example/Pt2_SearchEngine.png" alt="Part 2 - Search Engine" width="433"/>
  <img src="Examples/StreamLit%20Example/Pt2_Output.png" alt="Part 2 - Output" width="433"/>
</p>





### Part 3: Search Engine with Custom Score
```bash
streamlit run Part3Streamlit.py
```
<p float="left">
  <img src="Examples/StreamLit%20Example/Pt3_SearchEngineCustomScore.png" alt="Part 3 - Search Engine" width="300"/>
  <img src="Examples/StreamLit%20Example/Pt3_Output.png" alt="Part 3 - Output" width="400"/>
</p>
___

### Part 4: Search Engine on Custome Score to Display on Map
```bash
streamlit run Part4Streamlit.py
```
<p float="left">
  <img src="Examples/StreamLit%20Example/Pt4_DisplayonMap.png" alt="Part 4 - Search Engine" width="400"/>
  <img src="Examples/StreamLit%20Example/Pt4_Output.png" alt="Part 4 - Output" height="300"/>
</p>
___

### Part 5: Advanced Search Engine
```bash
streamlit run Part5Streamlit.py
```
<p float="left">
  <img src="Examples/StreamLit%20Example/Pt5_AdvancedSE.png" alt="Part 5 - Search Engine" width="400"/>
  <img src="Examples/StreamLit%20Example/Pt5_Output.png" alt="Part 5 - Output" height="400"/>
</p>
___


## **Collaborators - Group 20**
- [Marco Zimmatore](https://github.com/zimmy11)
- [Emanuele Iaccarino](https://github.com/emanueleiacca)
- [Gabriele Cabibbo](https://github.com/cabibbo2196717)
- [Emre Yeşil](https://github.com/1emreyesil)
