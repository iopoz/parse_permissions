import requests
import json

from flask import Flask, render_template

from db import get_permissions, add_new

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/app_perm/<app_id>/<hl>', methods=['GET', 'POST'])
def app_permission(app_id, hl):
    res = get_permissions(app_id, hl)
    res_dict = {}
    error = False
    if len(res) == 0:
        if int(hl):
            hl_t = 'ru'
        else:
            hl_t = 'en'
        session = requests.Session()
        url = 'https://play.google.com/_/PlayStoreUi/data?ds.extension=163726509&f.sid=9186978011704125010&hl=%s&soc-app' \
              '=121&soc-platform=1&soc-device=1&authuser&_reqid=272415&rt=c' % hl_t
        data = {'f.req': "[[[163726509,[{163726509:[[null,[\"%s\",7],[]]]}],null,null,0]]]" % app_id}  # com.viber.voip

        response = session.request('POST', url, data=data)

        all_text = response.text
        int_res = all_text[all_text.find('{'):]
        int_res = int_res[: int_res.find('}') + 1]
        json_acceptable_string = int_res.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        list_perm = list(d.values())[0]

        if len(list_perm) > 2:
            new_list_perm = list_perm[:2]
            for item in list_perm[2]:
                new_list_perm[1][0][2].append(item)
        else:
            new_list_perm = list_perm


        try:
            for perms in new_list_perm:
                for perm in perms:
                    if len(perm) > 0:
                        res_dict[perm[0]] = {}
                        res_dict[perm[0]]['img'] = perm[1][3][2]
                        res_dict[perm[0]]['perm'] = []
                        for perm_item in perm[2]:
                            res_dict[perm[0]]['perm'].append(perm_item[1])
            add_new(app_id, int(hl), res_dict)
        except:
            error = True
            res_dict['err'] = 'Something went wrong!'
    else:
        res_dict = res

    return render_template('app_perm.html', res=res_dict, err=error)


if __name__ == '__main__':
    app.run()
