from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import os
from datetime import datetime
import secrets
from django.views.decorators.http import require_http_methods
import json
from django.middleware.csrf import get_token

# Create your views here.


def get_auths(request):

  if not (request.session and "username" in request.session.keys()):
    return HttpResponseRedirect("")

  csrf_token = get_token(request)

  values = settings.AUTH_HISTORY_SHEET.get_all_values()

  def getDuration(then, now=datetime.now(), interval="default"):

    # Returns a duration as specified by variable interval
    # Functions, except totalDuration, returns [quotient, remainder]

    duration = now - then  # For build-in functions
    duration_in_s = duration.total_seconds()

    def years():
      return divmod(duration_in_s, 31536000)  # Seconds in a year=31536000.

    def days(seconds=None):
      return divmod(seconds if seconds != None else duration_in_s,
                    86400)  # Seconds in a day = 86400

    def hours(seconds=None):
      return divmod(seconds if seconds != None else duration_in_s,
                    3600)  # Seconds in an hour = 3600

    def minutes(seconds=None):
      return divmod(seconds if seconds != None else duration_in_s,
                    60)  # Seconds in a minute = 60

    def seconds(seconds=None):
      if seconds != None:
        return divmod(seconds, 1)
      return duration_in_s

    def totalDuration():
      y = years()
      d = days(y[1])  # Use remainder to calculate next variable
      h = hours(d[1])
      m = minutes(h[1])
      s = seconds(m[1])

      return "{} years, {} days, {} hours, {} minutes and {} seconds ago".format(
        int(y[0]), int(d[0]), int(h[0]), int(m[0]), int(s[0]))

    return {
      'years': int(years()[0]),
      'days': int(days()[0]),
      'hours': int(hours()[0]),
      'minutes': int(minutes()[0]),
      'seconds': int(seconds()),
      'default': totalDuration()
    }[interval]

  html = """
<!DOCTYPE html>
<html>
<head>
    <title>SC Control Panel</title>
    <link rel="shortcut icon" type="image/x-icon" href="/favicon"/>
    <meta charset="utf-8">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <!-- <link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet"> -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js" integrity="sha384-IQsoLXl5PILFhosVNubq5LC7Qb9DXgDA9i+tQ8Zj3iwWAwPtgFTxbJ8NT4GN1R8p" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>    
  <style>
  /* Media Query for Mobile Devices */
  @media (max-width: 480px) {
    body {
      font-size: 2.5em;
    }
    .approvalbutton {
      font-size: 1.3em;
      margin-top: 30px;
    }
    .authcard {
      width: 80%;
    }
    #logoutbutton {
      position: fixed;
      top: 0px;
      width:100%;
      font-size: 1.3em;
      z-index: 1;
    }
  }
    
  /* Media Query for low resolution  Tablets, Ipads */
  @media (min-width: 481px) and (max-width: 767px) {
    body, .approvalbutton {
      font-size: 2.5em;
    }
    .approvalbutton {
      font-size: 1.3em;
      margin-top: 30px;
    }
    .authcard {
      width: 80%;
    }
    #logoutbutton {
      position: fixed;
      top: 0px;
      width:100%;
      font-size: 1.3em;
      z-index: 1;
    }
  }
    
  /* Media Query for Tablets Ipads portrait mode */
  @media (min-width: 768px) and (max-width: 1024px){
    body, .approvalbutton {
      font-size: 2.5em;
    }
    .approvalbutton {
      font-size: 1.3em;
      margin-top: 30px;
    }
    .authcard {
      width: 80%;
    }
    #logoutbutton {
      position: fixed;
      top: 0px;
      width:100%;
      font-size: 1.3em;
      z-index: 1;
    }
  }
    
  /* Media Query for Laptops and Desktops */
  @media (min-width: 1025px) and (max-width: 1280px){
    .authcard {
      width: 50%;
    }
  }
    
  /* Media Query for Large screens */
  @media (min-width: 1281px) {
    .authcard {
      width: 50%;
    }
  }
</style>
</head>
<body>
    <a href="/logout" class="btn btn-secondary" id="logoutbutton" style="position:fixed; top:5px; right:5px;">Logout</a>
    <br>
"""
  values.pop(0)
  values.reverse()
  for row in values:
    auth_id = row[0]
    client_code = row[1]
    if row[2] in ["Pending", "Denied", "Expired"]:
      auth_status = row[2]
      if auth_status == "Pending":
        colortype = "warning"
      elif auth_status == "Denied":
        colortype = "danger"
      elif auth_status == "Expired":
        colortype = "secondary"
    else:
      auth_status = "Approved"
      colortype = "success"
    timestamp = row[3]

    card_template = f"""

<br>

<center>
    <div class="card text-center border-3 border-{colortype} authcard">
      <div class="card-header bg-{colortype} text-light font-weight-bold">
        <b>{auth_status}</b>
      </div>
      <div class="card-body">
        <center>
        <table class="table">
        <tr>
            <th>Auth ID</th>
            <td>{auth_id}</td>
        </tr>
        <tr>
            <th>Client Code</th>
            <td>{client_code}</td>
        </tr>
        </table>
        </center>
      <!--  
        <h5 class="card-title"></h5>
        <p class="card-text"></p> 
      -->
      </div>
"""

    if auth_status == "Pending":
      card_template += f"""
        <div class="row">
          <div class="col-12 col-md-6" style="padding-right: 0;">
            <form action="/control_panel/set_token/" method="POST" style="display: inline;">
                <input type="hidden" value="{csrf_token}" name="csrfmiddlewaretoken"> 
                <input type="hidden" value="{auth_id}" name="AUTH_ID">
                <input type="hidden" value='{client_code}' name="CLIENT_CODE">
                <input type="hidden" value=1 name="APPROVAL">
                <input type="submit" class="btn btn-primary approvalbutton" value="Approve" style="width:100%; border-radius: 0px;">
            </form>
          </div>
          <div class="col-12 col-md-6" style="padding-left: 0;">
            <form action="/control_panel/set_token/" method="POST" style="display: inline;">
                <input type="hidden" value="{csrf_token}" name="csrfmiddlewaretoken"> 
                <input type="hidden" value="{auth_id}" name="AUTH_ID">
                <input type="hidden" value='{client_code}' name="CLIENT_CODE">
                <input type="hidden" value=0 name="APPROVAL">
                <input type="submit" class="btn btn-secondary approvalbutton" value="Deny" style="width:100%; border-radius: 0px;"">
            </form>
          </div>
        </div>
"""
    elif auth_status == "Approved":
      card_template += f"""
        <div class="row">
            <form action="/control_panel/set_token/" method="POST" style="display: inline;">
                <input type="hidden" value="{csrf_token}" name="csrfmiddlewaretoken"> 
                <input type="hidden" value="{auth_id}" name="AUTH_ID">
                <input type="hidden" value='{client_code}' name="CLIENT_CODE">
                <input type="hidden" value=0 name="APPROVAL">
                <input type="submit" class="btn btn-danger approvalbutton" value="Revoke" style="width:100%; border-radius: 0px;"">
            </form>
        </div>
"""

    card_template += f"""
      <div class="card-footer bg-dark text-light">
        Requested {getDuration(datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S.%f"))} ({timestamp})
      </div>
    </div>
</center>

"""
    html += card_template
  html += """
</body>
</html>
"""
  return HttpResponse(html)


def download_client(request):
  jsoncontent_dict = {
    "CLIENT_CODE": request.GET.get("CLIENT_CODE"),
    "SERVER_URL": request.get_host()
  }
  jsoncontent = json.dumps(jsoncontent_dict)
  response = HttpResponse(jsoncontent, content_type='application/json')
  response['Content-Disposition'] = 'attachment; filename=fp.json'
  return response


@require_http_methods(["POST"])
def set_token(request):  # 3 API Calls

  if request.session and "username" in request.session.keys():

    values = settings.AUTH_HISTORY_SHEET.get_all_values()

    for row in values:
      if values.index(row) == 0:
        continue
      if int(row[0]) == int(
          request.POST["AUTH_ID"]) and row[1] == request.POST["CLIENT_CODE"]:
        row_index = values.index(row)
        this_id = int(row[0])
        if bool(int(request.POST["APPROVAL"])) == False:
          auth_token = "Denied"
        else:
          auth_token = secrets.token_hex(32)
        break
    values.pop(row_index)
    row_index2 = False
    for row in values:
      if row[1] == request.POST["CLIENT_CODE"] and row[2] not in [
          "Pending", "Denied"
      ] and auth_token != "Denied":
        row_index2 = values.index(row)
    if row_index2 is not False:
      settings.AUTH_HISTORY_SHEET.update(f'C{row_index2+1}', "Expired")
    settings.AUTH_HISTORY_SHEET.update(
      f'A{row_index+1}:C{row_index+1}',
      [[this_id, request.POST["CLIENT_CODE"], auth_token]])
    # return JsonResponse({"AUTH_TOKEN":auth_token, "TIMESTAMP": current_timestamp})
    return HttpResponseRedirect("/control_panel")

  else:

    return HttpResponseRedirect("index")


def get_favicon(request):
  image_data = open(os.path.join(settings.BASE_DIR, "favicon.ico"),
                    "rb").read()
  return HttpResponse(image_data, content_type="image/png")
