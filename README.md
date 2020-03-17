# Drugshortages
Drugshortages my first web app. While working in pharmacy, my colleagues and I noticed that certain medications were becoming difficult to keep in stock. Wholesalers simply listed these medications as unavailable. The problem only got worse halfway through 2018, when carcinogenic contaminants were found in several medications in the ARB class, leading to them being recalled by manufacturers. 

Ever since then things have gotten chaotic. It seems like there's a new medication shortage each week and it all becomes difficult to keep track of. This problem inspired me to create this app.

Drugshortages uses the drugshortagescanada.ca API. While drugshortagescanada.ca is a fine website on its own, I still wanted to create my own app to learn and improve my skills.
Using the website is simple. The search page lets you search for drug shortage reports by drug name. You are given a list of reports that match the search. Copy the report number and go back to the homepage and follow this new report. The home/index page will then list all your followed reports in one convenient place.

### Technical Details
This app is run on Flask, and written in Python, HTML and CSS. The list of followed drug reports is simply stored in a CSV file.
