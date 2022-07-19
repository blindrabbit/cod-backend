#Usado no COMPUTE node com as seguintes depedencias e configurações:
# (venv) [renancs@openstack-serra-compute01 psutil_monitor]$ pip freeze
# aiocontextvars==0.2.2
# certifi==2022.6.15
# charset-normalizer==2.0.12
# clask==0.0.5
# click==8.0.4
# contextvars==2.4
# databases==0.5.5
# dataclasses==0.8
# Flask==2.0.3
# greenlet==1.1.2
# idna==3.3
# immutables==0.18
# importlib-metadata==4.8.3
# itsdangerous==2.0.1
# Jinja2==3.0.3
# MarkupSafe==2.0.1
# mysql-connector==2.2.9
# peewee==3.15.1
# psutil==5.9.1
# PyMySQL==1.0.2
# requests==2.27.1
# SQLAlchemy==1.4.39
# typing_extensions==4.1.1
# urllib3==1.26.10
# Werkzeug==2.0.3
# zipp==3.6.0

#criar arquivo requeiriments.txt com os requisitos a cima, e carregar com "pip -r requeiriments.txt"

#para executar
#  python3 -m venv venv
#  source venv/bin/activate
#  flask run --host 0.0.0.0

from flask import Flask
import psutil as ps
import mysql.connector
from mysql.connector import Error
import peewee as pw
from peewee import *
from datetime import datetime
import requests

app = Flask(__name__)


def create_connection_db(database,user, password, host, port): 
    myDB = pw.MySQLDatabase(database,user=user,passwd=password, host=host,port=port)
    return myDB


db = create_connection_db('odb','root2', "root2", '10.50.1.122', 3306)


class BaseModel(Model):
    class Meta:
        database = db


class ComputeNodeData(BaseModel):
    id_compute_node_data = AutoField(primary_key=True)
    compute_node_data_date = DateTimeField()
    compute_node_data_cpu_percent = FloatField()
    compute_node_data_memory_percent = FloatField()
    
    class Meta:
        table_name = 'computenodedata'


class Services(BaseModel):
    id_service = AutoField(primary_key=True)
    name = CharField(max_length=100)
    token = CharField(max_length=100)
    creation_date = DateField()
    test_mode = BooleanField(default=False)

    class Meta:
        table_name = 'service'

db.create_tables([ComputeNodeData])

def is_testing_enable():
    service_id = 1
    try:
        is_testing = (Services
                                .select()
                                .where(Services.id_service == service_id))
        var = is_testing.dicts().get()
        if var['test_mode']:
            return True
        else:
            return False

    except Exception as error:
        print("error", error)
        return False

    
@app.route('/')
def hello():
    
#    while True:
#        cpu_percent = psutil.cpu_percent(interval=1)
#        data = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#        memory_percent = round(100 -(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total),2)
#        print(data+ ' - cpu '+str(cpu_percent)+'% |', 'memory '+ str(memory_percent) +'%')
    print(is_testing_enable())
    return '<h1>Hello, World!!!</h1>'


@app.route('/psutil')
def psutil():
    is_testing = True
    
    while is_testing:
        is_testing = is_testing_enable()

        cpu_percent = ps.cpu_percent(interval=1)
    #    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory_percent = round(100 -(ps.virtual_memory().available * 100 / ps.virtual_memory().total),2)
    #    retorno = (data+ ' - cpu '+str(cpu_percent)+'% | memory '+ str(memory_percent) +'%')
        
        retorno = "{'datetime':"+ data +", 'cpu_percent': "+ str(cpu_percent) +", 'memory_percent': "+ str(memory_percent) +"}"
        
        print(data)
        query = ComputeNodeData.create(compute_node_data_date=data,
                                        compute_node_data_cpu_percent=cpu_percent,
                                        compute_node_data_memory_percent=memory_percent)
                                    
#    retorno = 'teste'

    return retorno

# app.debug = True
app.config["DEBUG"] = True


if __name__ == "__main__":
    main()
