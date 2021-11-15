<html>
    <head>
        <title>El Noursicot fabric login</title>
    <body>
    <form name="loginForm" method="post" action="/login">
<table width="20%" bgcolor="0099CC" align="center">

<tr>
<td colspan=2><center><font size=4><b>ACI Login Page</b></font></center></td>
</tr>

<tr>
<td>Fabric IP</td>
<td><input type="text" size=25 name="fabric" value="dom-apic1-f1.cisco.com"></td>
</tr>


<tr>
<td>Username:</td>
<td><input type="text" size=25 name="username" value="admin"></td>
</tr>

<tr>
<td>Password:</td>
<td><input type="Password" size=25 name="password"></td>
</tr>

<tr>
<td ><input type="Reset"></td>
<td><input type="submit" onclick="return check(this.form)" value="Login"></td>
</tr>

<tr>
<td>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    {% for message in messages %}
      <b align="center">{{ message }}</b>
    {% endfor %}
  {% endif %}
{% endwith %}
</td>
</tr>

</table>

</form>

    </body>
    </html>