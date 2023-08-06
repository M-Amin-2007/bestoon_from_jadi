# bestoon_from_jadi
now this site is in this host: http://amin2007.pythonanywhere.com/<br>
**Note:** this is a trail website and its not **secure** to Enter **real** datas and Informations here
<h3>run this site locall.</h3>
<ol>
  <li>make a gmail</li>
  <li>Enable [2-step verification.](https://myaccount.google.com/signinoptions/two-step-verification/enroll-welcome)</li>
  <li>make an app password [here.](https://myaccount.google.com/u/1/apppasswords)</li>
  [image1](/images/img1.png)
  [image2](/images/img2.png)
  [image3](/images/img3.png)
  <li>put the email adress and password gave you in [this file](/account_manager/static/account_manager/secret.json) in `""` signs.</li>
  <li>run this commands on your project directory after installing python 3.7.9:
  <ul><li>`python -m pip install -r requirements.txt`</li>
    <li>`python manage.py makemigrations`</li>
    <li>`python manage.py migrate`</li>
    <li>`python manage.py runserver`</li>
  </ul></li>
  <li>open the locall IP gived you cmd in browser.</li>
</ol>
