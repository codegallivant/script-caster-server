from django.conf import settings
import os
import exterior_connection
from datetime import datetime
import time
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from cryptography.fernet import Fernet
from django.http import JsonResponse
from github import Github 


# Create your views here.
@require_http_methods(["POST"])
@csrf_exempt
def get_token(request): # 1 API Call
    f = Fernet(settings.AUTH_ID_KEY)
    auth_token = False
    values = settings.AUTH_HISTORY_SHEET.get_all_values()
    values.pop(0)
    values.reverse()
    for row in values:
        if int(row[0]) == int(f.decrypt(str(request.POST["AUTH_ID"]).encode()).decode()) and row[1] == request.POST["CLIENT_CODE"]:
            auth_token = row[2]
            break
    return JsonResponse({"AUTH_TOKEN": auth_token, "TIMESTAMP": row[3]})

@require_http_methods(["POST"])
@csrf_exempt 
def auth_client(request): # 2 API Calls
  if request.POST["CLIENT_CODE"] not in settings.CLIENT_CODE_LIST:
    return JsonResponse({})
  current_timestamp = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f"))
  values = settings.AUTH_HISTORY_SHEET.get_all_values()
  f = Fernet(settings.AUTH_ID_KEY)
  for row in values:
      if row[1]==request.POST["CLIENT_CODE"] and row[2]=="Pending":
          return JsonResponse({})
  row_count = len(values)
  last_id = values[-1][0]
  if last_id == "AUTH_ID":
      last_id = 0
  else:
      last_id = int(last_id)
  this_id = last_id+1
  settings.AUTH_HISTORY_SHEET.update(f'A{row_count+1}:D{row_count+1}', [[this_id, request.POST["CLIENT_CODE"], "Pending", current_timestamp ]])
  return JsonResponse({"AUTH_ID": f.encrypt(str(this_id).encode()).decode()})


    # client = exterior_connection.authenticate(creds_path)
    # sheet = exterior_connection.open_sheet("Exterior", "AuthHistory", client)
    # Add value to sheet with auth token pending
    # When auth token generated (by manual auth /set_token), return the token (client is supposed to keep sending requests to /get_token after sending 1 req to /auth_client)


def verify_auth_token(SUBMITTED_AUTH_ID, SUBMITTED_CLIENT_CODE, SUBMITTED_AUTH_TOKEN, authvalues):
    
    f = Fernet(settings.AUTH_ID_KEY)

    SUBMITTED_AUTH_ID = f.decrypt(SUBMITTED_AUTH_ID.encode()).decode()

    for row in authvalues:
        if str(SUBMITTED_AUTH_ID)==str(row[0]) and SUBMITTED_CLIENT_CODE==row[1] and SUBMITTED_AUTH_TOKEN==row[2] and row[2] not in ["Pending","Denied","Expired"]:
            return True

    return False



@require_http_methods(["POST"])
@csrf_exempt
def get_tasks(request):
    #If update local tasks is true then fetch repo contents from github and send
    #Find script parameters which are true
    #Return them and their subparameters in json string
    #Change script parameter status to Running    

    authvalues = settings.AUTH_HISTORY_SHEET.get_all_values()
    
    CLIENT_CODE = request.POST["CLIENT_CODE"]

    if verify_auth_token(request.POST["AUTH_ID"], CLIENT_CODE, request.POST["AUTH_TOKEN"], authvalues) is False:
        return JsonResponse({})

    sheet = settings.ALL_SHEETS_DICT[CLIENT_CODE]
    all_sheet_values, parameter_dict = exterior_connection.get_parameter_values(sheet)
    exterior_connection.update_parameter_value(sheet,'LAST_CONTACT_TIME', datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %H:%M:%S'), all_sheet_values)

    if bool(int(request.POST["SCRIPTS_REQUIRED"]))==True or parameter_dict["UPDATE_LOCAL_CLIENT_SCRIPTS"] == "ON":
        #Get data from GitHub
        #send contents along with stuff below at end
        if settings.GITHUB_ACCESS_TOKEN == "":
            g = Github()
        else:
            g = Github(settings.GITHUB_ACCESS_TOKEN)
        repo = g.get_repo(f"{settings.GITHUB_USERNAME}/{settings.GITHUB_REPO_NAME}")
        contents = repo.get_contents("")

        user_scripts_dict = dict()

        while len(contents) > 0:
            file_content = contents.pop(0)
            # print(file_content.path)
            if file_content.type=="dir":
                if file_content.name == "venv":
                    continue
                contents.extend(repo.get_contents(file_content.path))
            else:
                if os.path.basename(file_content.name).upper() in [".GITIGNORE",".REPLIT","REPLIT.NIX"]:
                    continue
                user_scripts_dict[file_content.path] = file_content.decoded_content.decode('utf-8')
    else:
        user_scripts_dict = dict()
    
    # active_tasks = [key for key in parameter_dict.keys() if parameter_dict[key]=="ON"]
    # Set tasks to running

    # Writing file contents from GitHub

    # for task in active_tasks:
    #     exterior_connection.update_parameter_status(sheet, task)

    return JsonResponse({"PARAMETER_DICT": parameter_dict, "ALL_SHEET_VALUES": all_sheet_values , "SCRIPTS": user_scripts_dict})



def convert_col_index(column_int):
    start_index = 1   #  it can start either at 0 or at 1
    letter = ''
    while column_int > 25 + start_index:   
        letter += chr(65 + int((column_int-start_index)/26) - 1)
        column_int = column_int - (int((column_int-start_index)/26))*26
    letter += chr(65 - start_index + (int(column_int)))
    return letter


@require_http_methods(["POST"])
@csrf_exempt
def send_data(request):
    # Sent by script on client
    # Input form : {"script_name":, "subparameter1":, "subparameter2":, ...}
    '''
    sheet.update()
    '''
    authvalues = settings.AUTH_HISTORY_SHEET.get_all_values()
    
    CLIENT_CODE = request.POST["CLIENT_CODE"]

    if verify_auth_token(request.POST["AUTH_ID"], CLIENT_CODE, request.POST["AUTH_TOKEN"], authvalues) is False:
        return JsonResponse({})

    print(CLIENT_CODE)
    sheet = settings.ALL_SHEETS_DICT[CLIENT_CODE]
    print(sheet)

    all_sheet_values = request.POST["ALL_SHEET_VALUES"]
    if all_sheet_values != "":
        all_sheet_values, parameter_dict = exterior_connection.get_parameter_values(sheet, all_sheet_values)
    else:
        all_sheet_values, parameter_dict = exterior_connection.get_parameter_values(sheet)
    print(all_sheet_values)

    SCRIPT_NAME = request.POST["SCRIPT_NAME"]
    SCRIPT_PARAMETERS = json.loads(request.POST["ROW_PARAMETERS"])
    print(SCRIPT_NAME)
    print(type(SCRIPT_PARAMETERS))
    print(SCRIPT_PARAMETERS)

    row, col = exterior_connection.find_parameter_cells(sheet, SCRIPT_NAME, sheet_values = all_sheet_values)
    print(row, col)
    col = convert_col_index(col)
    row_parameters = all_sheet_values[row-1]
    row_values = all_sheet_values[row]
    row_dict = dict(zip(row_parameters, row_values))
    for parameter in row_parameters:
        if parameter in SCRIPT_PARAMETERS:
            row_values[row_parameters.index(parameter)] = SCRIPT_PARAMETERS[parameter] 
    print(row_values)
    col_count = len(row_parameters)
    col2 = convert_col_index(col_count)
    print(f"{col}{row+1}:{col2}{row+1}")
    sheet.update(f"{col}{row+1}:{col2}{row+1}", [row_values])

    return JsonResponse({})


# API Call Review

"""

/auth_client 2 API calls
/get_token every a seconds 1a API calls until token got. Then /get_token by server to verify every API call by client. therefore each api call due to client is accompanied by this one too.
/set_token 3 API Calls
/get_tasks every b seconds 1b API Calls
/switch_script every time script is run 1 API Call per script x per minute
/send_data every time script outputs 1 API Call per outputing script y per minute

Maximum API Calls in 1 minute: 
2+1+1+1+((1*(60/10)+x+y)*2 taking b=10
5+12+2x+2y
If every script is outputing then
17+4x
Max API calls per minute = 60
Max x = gif (60-17)/4 = 10.75 scripts
For cap to be reached, around 10 scripts must be run in the same minute


"""