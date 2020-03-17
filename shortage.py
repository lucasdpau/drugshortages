import sys, os, time
import json, requests, csv

#written with Requests v2.22.0 @https://2.python-requests.org/en/master/

#I created this class to simplify function calling, and api_url_base and headers
#are like global variables
class report_generator:
    def __init__(self, api_url, headers):
        self.api_url_base = api_url
        self.headers = headers
        
    def drug_search(self, drug, offset):
        #input must be a string, Returns a response object
        drug_request = requests.get(self.api_url_base + '/search', headers=self.headers, params={'term': drug, 'offset':offset})
        return drug_request
    
    def drug_search_filter_by_status(self, drug, offset):
        drug_request = requests.get(self.api_url_base + '/search', headers=self.headers, params={'term': drug, 'offset':offset, 'filter_status':"active_confirmed"})
        return drug_request        
    
    def drug_search_all_pages(self, drug):
        #input is a string, returns a list of response objects. May not be necessary if we do it in app.py,
        #since getting all the pages at once is noticeably slow
        pass
    
    
    def drug_search_id_parse_json(self, response):
        #input is a response object, which may contain multiple reports
        #returns a list, containing strings which have a drug name, shortage status, update time and report id
        drug_list = []
        json_report = response.json()
        for i in json_report['data']:
            current_drug = i['en_drug_brand_name'] + ', ' + i['updated_date'] + ', ' + i['status'] + ', ' + str(i['id'])
            drug_list.append(current_drug)
        return drug_list
    
    def search_report_byid(self, reportid):
        # reportid is a string, returns a response object
        report = requests.get(self.api_url_base + '/shortages/' + reportid, headers=self.headers)
        return report
    
    def reportid_json_parse(self, report):
        #response object input.  gets the json-ified format and parses it into a string with
        #the info we want.
        data = report.json()
        info = data['en_drug_brand_name'] + ', ' + data['updated_date'] + ', ' + data['status'] + ', ' + str(data['id'])
        return info
    
    def check_all_reports(self, db, mode):
        #checks all reportids from the database, then
        #returns all results in a list
        check_list = edit_database("", db, "r")	
        info_list = []
        for items in check_list:
            #Check if report is valid, else return "Invalid report id"
            x = self.search_report_byid(items)
            if x.status_code == 200:
                if mode == "string":
                    info_list.append(self.reportid_json_parse(x))            
                elif mode == "json":
                    info_list.append(x)
                else:
                    print("invalid mode")
                    break
            elif x.status_code == 404 or x.status_code == 400:
                print("Invalid report ID")
                
            
        return info_list           
        

api_req = requests.post(api_url_base + '/login', data=login)
apikey = api_req.headers['auth-token']
headers = {'auth-token' : apikey, 'Content-type' : 'application/json'}

#chekcing status codes
if api_req.status_code == 200:
    print('login successful, 200')
elif api_req.status_code == 405:
    print('bad, 405')
else:
    print('bad, misc error: ' + str(api_req.status_code))

def drug_search(drug, offset):
    #drug must be a string, Returns a 'list-type' response object, offset is int
    drug_request = requests.get(api_url_base + '/search', headers=headers, params={'term': drug, 'offset': offset})
    return drug_request

def drug_search_id_parse_json(short_id):
    #input is a jsonified response object, which may contain multiple reports
    #returns a list, containing strings which have a drug name, shortage status, update time and report id
    drug_list = []
    for i in short_id['data']:
        current_drug = i['en_drug_brand_name'] + ', ' + i['updated_date'] + ', ' + i['status'] + ', ' + str(i['id'])
        drug_list.append(current_drug)
    return drug_list


class current_search():
    def __init__(self):
        pass

def read_csv(database):
    #returns a list of reports
    csv_file = open(database, "r")
    database_line_list = []
    for line in csv_file:
        database_line_list.append(line)
    csv_file.close()
    return database_line_list

def add_to_csv(report, database):
    #appends report to database
    csv_file = open(database, "a")
    csv_file.write(report + "\n")
    csv_file.close()
    
def remove_from_csv(database, report):
    csv_file = open(database, "r")
    temp_database_storage = []
    for line in csv_file:
        temp_database_storage.append(line)
    csv_file.close()
    
    db_file = open(database, "w")
    for line in temp_database_storage:
        if not line.strip("\n") == (report):
            db_file.write(line)
    db_file.close()  
    return temp_database_storage    

def edit_database(report_id, database, mode):
    #I thought I was clever for giving the function modes, but I should have split it up.
    #returns a list of report ids if mode = "r"
    #appends report_id to database if mode = "a"
    #removes report_id from database if mode = "w"
    if not mode in ("a", "w", "r"):
        print("Error, edit_database() did not have proper 2nd argument")
        return False
    else:
        #implement csv module here
        if mode == "w":
            #check if .remove() needs to remove \n as well
            db_old_file = open(database, "r")
            database_line_list = []
            for line in db_old_file:
                database_line_list.append(line)   
            db_old_file.close()
            
            db_file = open(database, mode)
            for line in database_line_list:
                if not line.strip("\n") == (report_id):
                    db_file.write(line)
            db_file.close()  
            return database_line_list

        #append a report id to the database
        db_file = open(database, mode)
        if mode == "a":
            db_file.write(report_id +"\n")
            db_file.close()
            
        elif mode == "r":
            database_line_list = []
            for line in db_file:
                database_line_list.append(line)
            db_file.close()
            return database_line_list

        
        

def check_all_reports(api_url, db, headers):
    #checks all reportids from the database, then
    #returns all results in a list
    check_list = edit_database("", "r", db)	
    info_list = []
    for items in check_list:
        #Check if report is valid, else return "Invalid report id"
        x = search_report_byid(api_url, items, headers)
        if x.status_code == 200:
            info_list.append(reportid_json_parse(x))            
        else:
            print("Invalid report ID")
        
    return info_list