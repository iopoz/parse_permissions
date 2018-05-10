from errno import errorcode

import MySQLdb

db_host = "127.0.0.1"
db_user = "root"
db_password = "aA!23456"
db_name = "permissions"

TABLES = {}

TABLES['app'] = (
    """CREATE TABLE app (
      id INT(11) NOT NULL AUTO_INCREMENT, 
      name VARCHAR(100) NOT NULL, 
      PRIMARY KEY (id))""")

TABLES['permissions'] = (
    """CREATE TABLE permissions (
      id INT(11) NOT NULL AUTO_INCREMENT, 
      url VARCHAR(3000), 
      name VARCHAR(200), 
      parent_id INT(11), 
      PRIMARY KEY (id), 
      CONSTRAINT permissions_ibfk_1 FOREIGN KEY (parent_id) REFERENCES permissions (id) ON DELETE CASCADE) """)

TABLES['app_perm'] = (
    """CREATE TABLE app_perm (
      app_id INT(11) NOT NULL, 
      perm_id INT(11) NOT NULL, 
      language INT(1), 
      CONSTRAINT app_perm_ibfk_1 FOREIGN KEY (app_id) REFERENCES app (id) ON DELETE CASCADE, 
      CONSTRAINT app_perm_ibfk_2 FOREIGN KEY (perm_id) REFERENCES permissions (id) ON DELETE CASCADE) """)


def create_db(cursor):
    try:
        sql = "CREATE DATABASE %s DEFAULT CHARACTER SET 'utf8'" % db_name
        cursor.execute(sql)
    except:
        print('Failed to create')


def create_connection():
    db = MySQLdb.connect(host=db_host, user=db_user, password=db_password)
    cursor = db.cursor()
    db.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    try:
        db.select_db(db_name)
    except:
        create_db(cursor)
        db.select_db(db_name)

    for name, ddl in TABLES.items():
        try:
            print("Creating table {}: ".format(name), end='')
            cursor.execute(ddl)
        except:
            print('Table is exist')
    return cursor, db


def terminate_connection(cursor, db):
    cursor.close()
    db.close()

def get_permissions(app, lng):
    db_connect = create_connection()
    cursor = db_connect[0]
    res_dict = {}
    cursor.execute("""Select permissions.permissions.id, permissions.permissions.name, url
                        FROM permissions 
                        JOIN app_perm ON app_perm.perm_id=permissions.id
                        JOIN app ON app_perm.app_id = app.id
                        WHERE app.name=%s AND app_perm.language=%s AND parent_id is NULL """, [app, lng])
    res = cursor.fetchall()
    if len(res) > 0:
        for item in res:
            res_dict[item[1]] = {}
            res_dict[item[1]]['img'] = item[2]
            cursor.execute("""Select name 
                                  from permissions
                                  WHERE parent_id=%s""", [item[0]])
            chld_res = cursor.fetchall()
            res_dict[item[1]]['perm'] = []
            for child in chld_res:
                res_dict[item[1]]['perm'].append(child[0])
    terminate_connection(cursor, db_connect[1])
    return res_dict


def add_new(app, lng, items):
    db_connect = create_connection()
    cursor = db_connect[0]
    db = db_connect[1]
    perm_id = []
    #create permissions
    for item in items:
        cursor.execute("""Select * from permissions where name=%s""", [item])
        res_check = cursor.fetchall()
        if len(res_check) > 0:
            print('parent permission is exist')
            perm_id.append(res_check[0])
        else:
            cursor.execute("""INSERT INTO permissions (url, name) VALUES (%s,%s)""", [items[item]['img'], item])
            db.commit()
        cursor.execute("""Select id from permissions where name=%s""", [item])
        res = cursor.fetchall()
        perm_id.append(res[0][0])
        for perm in items[item]['perm']:
            cursor.execute("""Select * from permissions where name=%s AND parent_id=%s""", [perm,res[0][0]])
            res_check = cursor.fetchall()
            if len(res_check) > 0:
                print('permission is exist')
                perm_id.append(res_check[0][0])
            else:
                cursor.execute("""Insert into permissions(name, parent_id) VALUES (%s, %s)""", [perm, res[0][0]])
                db.commit()
                cursor.execute("""Select id from permissions where name=%s""", [perm])
                res_chld = cursor.fetchall()
                perm_id.append(res_chld[0][0])
    #create app

    if cursor.execute("""Select id from app where name=%s""", [app]) == 0:
        cursor.execute("""Insert into app (name) VALUES (%s)""", [app])
        db.commit()
        cursor.execute("""Select id from app WHERE name=%s""", [app])
    app_id = cursor.fetchall()[0][0]
    for perm in perm_id:
        if type(perm) == int:
            cursor.execute("""Insert into app_perm (app_id, perm_id, language) VALUES (%s, %s, %s)""", [app_id, perm, lng])
            db.commit()
    terminate_connection(cursor, db)








