import requests
import xml.etree.ElementTree as ET

# disable ssl warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def getClients(host, username, password):
    with requests.Session() as s:
        s.verify = False
        s.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # login
        url=host+'/admin/login.jsp'
        data = {
            "username": username,
            "password": password,
            "ok": "Log on",
            }
        login_resp = s.post(url, data=data, allow_redirects=False)
        # check for valid auth
        csrf_token = login_resp.headers.get('HTTP_X_CSRF_TOKEN')
        if not csrf_token:
            ## TODO throw warning or error
            return []
        s.headers['X-CSRF-Token'] = csrf_token

        # get clients
        url=host+"/admin/_cmdstat.jsp"
        clients_resp = s.post(url, data=_clients_request_data())
        if clients_resp.status_code != 200:
            ## TODO throw warning or error
            return []

        clients = _parse_clients_resp(clients_resp.text)
    return clients


def _parse_clients_resp(xml_text):
    clients = []
    root = ET.fromstring(xml_text)
    clients_xml = root.find('response').find('apstamgr-stat').findall('client')

    for client in clients_xml:
        status = client.get('status')
        #0:Unauthorized, 1:Authorized, 2:Authenticating, 3:PSKExpired, 4:AuthorizedDeny, 5:AuthorizedPermit, 6:Disconnected
        if status != '1':
          continue
        mac = client.get('mac')
        name = client.get('hostname')
        clients.append({
            "name": name,
            "mac": mac,
        })

    return clients


def _clients_request_data():
    # post data
    ajax = ET.Element('ajax-request')
    ajax.set('action', 'getstat')
    ajax.set('comp', 'stamgr')
    client = ET.SubElement(ajax, 'client')
    client.set('LEVEL', '1')
    client.set('TRIM', 'true')
    client.set('client-type', '3')
    return  ET.tostring(ajax)

