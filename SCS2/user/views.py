from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect
from django.middleware.csrf import get_token

  
ht1 = """    
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">

  <title>SC Server Login</title>


  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
  <!-- <link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet"> -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
  <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js" integrity="sha384-IQsoLXl5PILFhosVNubq5LC7Qb9DXgDA9i+tQ8Zj3iwWAwPtgFTxbJ8NT4GN1R8p" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
""" 
ht2="""
</head>

<body class="container" style="padding:20px">

  <br/>
  <br>
  <br>
  <center>

      <form action="/login/" method="POST">
        <input type="hidden" name="csrfmiddlewaretoken" value="{}">
        <div class="input-group mb-3" style="margin: 10px;">
          <div class="input-group-prepend" style="border-radius: 6px 0px 0px 6px;">
            <span class="input-group-text" id="basic-addon1" style="border-radius: 6px 0px 0px 6px;">@</span>
          </div>
          <input type="text" name="username"  placeholder="Username" class="form-control" aria-label="Username" aria-describedby="basic-addon1" style="border-radius: 0px 6px 6px 0px;">
        </div>
        <div class="input-group mb-3" style="margin: 10px;">
          <div class="input-group-prepend" style="border-radius: 6px 0px 0px 6px;">
            <span class="input-group-text" id="basic-addon1" style="border-radius: 6px 0px 0px 6px;">*</span>
          </div>
          <input type="password" name="password" placeholder="Password" class="form-control" aria-label="Password" aria-describedby="basic-addon2" style="border-radius: 0px 6px 6px 0px;"> 
        </div>
    
        <button class="btn btn-primary" type="submit" style="margin:20px"><span class="glyphicon glyphicon-log-in"></span> &nbsp; Login</button>
      </form>

</center>
    
</body>

</html>

"""


def index(request):
    csrf_token = get_token(request)
    if request.session:
        if "username" in request.session.keys():
            return HttpResponseRedirect('/control_panel')
    return HttpResponse((ht1+ht2).format(csrf_token))
  

def login_user(request):
    if request.method == 'POST':
  
        # AuthenticationForm_can_also_be_used__
        csrf_token = get_token(request)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            form = login(request, user)
            request.session["username"]=username
            return HttpResponseRedirect('/control_panel')
        else:
            hts = """
<script>
alert("Incorrect username/password.")
</script>
"""
            return HttpResponse((ht1+hts+ht2).format(csrf_token))


def logout(request):
    del request.session["username"]
    return HttpResponseRedirect("/")
