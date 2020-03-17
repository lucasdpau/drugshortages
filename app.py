import json, requests, os
import shortage
from flask import Flask, render_template, request, redirect
#apscheduler allows the app to schedule tasks automatically
#from apscheduler.schedulers.background import BackgroundScheduler  

#change these values according to login info and the website's documentation
DRUG_SHORT_URL = 'https://www.drugshortagescanada.ca/api/v1'
#hardcoded login should be changed TODO
LOGIN = {'email':"REDACTED", "password":"REDACTED"}
DATABASE = "druglist.csv"

def get_auth(api_url_base, login_info):
    try:
        api_req = requests.post(api_url_base + '/login', data=login_info)
        api_key = api_req.headers['auth-token']
        return api_key
    except:
        print("error in getting API key")

def add_reportid():
    pass

#gets an auth-token from the api
api_key = get_auth(DRUG_SHORT_URL, LOGIN)
headers = {'auth-token' : api_key, 'Content-type' : 'application/json'}

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

#a 'report_generator' object that stores the current api key and URL.
reports = shortage.report_generator(DRUG_SHORT_URL, headers)
#a list of strings, each has the info we need for each report in the database
report_check_str = reports.check_all_reports('druglist.csv', 'string')
#a list of response objects of each report in the database. use json() method to use it
report_check_json = reports.check_all_reports('druglist.csv', 'json')

#scheduler = BackgroundScheduler()
#scheduler.add_job(reports.check_all_reports('druglist.csv', 'string') , trigger='interval', hours=6)
#scheduler.start() TODO, goto https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flask

@app.after_request
def after_request(response):
    #Disable caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/', methods=['GET'])
def get_index():
    report_check_str = reports.check_all_reports('druglist.csv', 'string')
    report_list = []
    for strings in report_check_str:
        temp_str_list = strings.split(',')
        report_list.append(temp_str_list)
    return render_template('index.html', reports=report_list)

@app.route('/', methods=['POST'])
def add_to_database():
    # in the form in index.html, report_id is the name of the text field for the new report
    new_report = request.form.get("report_entry")
    if not new_report:
        print("invalid report input")
    if new_report.isdigit():
        shortage.edit_database(new_report, DATABASE, "a")
    else:
        print("invalid report ID")
    report_check_str = reports.check_all_reports('druglist.csv', 'string')
    report_list = []
    for strings in report_check_str:
        temp_str_list = strings.split(',')
        report_list.append(temp_str_list)    
    return render_template('index.html', reports=report_list)


@app.route('/search.html', methods=['GET'])
def load_search_page():
    req_header = request.args
    print(req_header)
    return render_template('search.html')

@app.route('/search.html', methods=['POST'])
def search_for_drugs():
    drug_search_term = request.form.get("search_entry")
    #offset will let us check different pages in the search
    offset = 0
    response = reports.drug_search(drug_search_term, offset)
    response_j = response.json()
    response_list = reports.drug_search_id_parse_json(response)
    #input is a json list response object, which may contain multiple reports
    #returns a list, containing strings which have a drug name, shortage status, update time and report id    
    
    return render_template('search.html', response_list=response_list, response_j=response_j)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    Flask.run(app, debug=True, host="0.0.0.0", port=port)



# request.args.get("querystring") 
# https://stackoverflow.com/questions/24292766/how-to-process-get-query-string-with-flask TODO
