from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo, ObjectId, MongoClient
from bson import json_util
from bson.objectid import ObjectId
import json


import pyrebase
import urllib

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = 'myawesomesecretkey'

#app.config['MONGO_URI'] = 'mongodb://localhost:27017/ensayorest'
app.config['MONGO_URI'] ='mongodb+srv://daniel:barcelona10@cluster0.6nfsz.mongodb.net/test'
mongo = PyMongo(app)



firebaseCofing={
        "apiKey": "AIzaSyDofj8eOWYuo_yhBpJotHXM6J9Od2PTNco",
    "authDomain": "autentificacion-75c6f.firebaseapp.com",
    "databaseURL": "https://autentificacion-75c6f-default-rtdb.firebaseio.com",
    "projectId": "autentificacion-75c6f",
    "storageBucket": "autentificacion-75c6f.appspot.com",
    "messagingSenderId": "758528305641",
    "appId": "1:758528305641:web:0ede9eb292776b57d68378"
}

firebase = pyrebase.initialize_app(firebaseCofing)
auth = firebase.auth()
storage = firebase.storage()

@app.route('/', methods=['POST'])
def create_user():
 
    
    #mongodb
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    nameDueno = request.json['nameDueno']
    domicilio = request.json['domicilio']
    activado = request.json['activado']
    createDate = request.json['createDate']
    categoria = request.json['categoria']
    img = request.json['img']
    id =ObjectId()
    #FIREBASE   
    try:
        auth.create_user_with_email_and_password(email,password)
        cluodfilename= name
        storage.child(cluodfilename).put(img)
        img = storage.child(cluodfilename).get_url(None)
        
        if name and email and password and nameDueno:
            hashed_password = generate_password_hash(password)
            
            mongo.db.restaurante.insert(
            {'_id':id,
            'img':img,
            'name': name, 
            'email': email, 
            'password': hashed_password, 
            'nameDueno' : nameDueno,
            "domicilio":domicilio,
            'activado' : activado ,
            'createDate': createDate,
            'categoria':[categoria],
            
            })

            response = jsonify({
                '_id': str(id),
                'name': name
            })

            response.status_code = 201
        return response
    except:
        print('correo ya esta creado')

    
    else:
        return not_found()


#=================================================================
#========ES LA OPCION DE POST ANIDADO EN CATEGORIA================
#=================================================================

@app.route('/<id>', methods=['POST'])
def create_menu(id):
    res = mongo.db.restaurante.find_one({"_id": ObjectId(id)},{"name":1,"menu":1,"domicilio":1,"img":1,"_id":1,"categoria":1,"menu":1})
    #es el id de restaurante y su categoria para la busqueda
    restaurante_name=res["name"]
    #el id para decir que se registro un campo nuevo que agrego el menu
    restaurante_id= res["_id"]
    #==================================
    nombre = request.json['nombre']
    precio = request.json['precio']
    descripcion = request.json['descripcion']
    img = request.json['img']
    activado =request.json['activado']
    createDate = request.json['createDate']
 
    if  nombre and precio and descripcion:
        id = ObjectId()
        cluodfilename= f'{restaurante_name}/{nombre}'     
        storage.child(cluodfilename).put(img)
        img = storage.child(cluodfilename).get_url(None)
        mongo.db.menu.insert({'_id':id, 
            'restaurante':restaurante_name,
            'id_restaurante':restaurante_id,
            "nombre":nombre,
            "precio":precio, 
            "descripcion":descripcion,
            "img":img,
            "activado":activado,
            "createDate":createDate
            })
        
        mongo.db.restaurante.update({"_id":ObjectId(restaurante_id)},{'$push':{'menu':{"id":id,"nombre":nombre,"precio":precio,"descripcion":descripcion,"img":img}}})
        response = jsonify({
                '_id': str(id),
                'nombre': nombre
            })

        response.status_code = 201
        return response
    else:
        return not_found()

#=================================================================
#================MUESTRA TODO LOS RESTAURANTE   ==================
#=================================================================

@app.route('/', methods=['GET'])
def get_users():
    users = mongo.db.restaurante.find({},{'name':1,'domicilio':1,'img':1,'categoria':1,'_id':1})
    response = json_util.dumps(users)
    return Response(response, mimetype="application/json")
    
@app.route('/verficar/<email>/<password>', methods=['GET'])
def verificar(email,password):

    password =check_password_hash(password)
    print(password)
    users = mongo.db.restaurante.find({'email':email},{'email':1,'name':1})
    response = json_util.dumps(users)
    return Response(response, mimetype="application/json")


#=========TARE SOLO LA LISTA DE PLATOS DEL RESTAURANTE============
#trae la lsita de platos solo de ese restaurante por medio del id de ello y del restaurante
#=================================================================

@app.route('/<name>')
def get_restaurante_name(name):
    restaurate_menus = mongo.db.restaurante.find_one({"name": name},{'menu':1,'name':1,'domicilio':1, '_id':0})
    response = json_util.dumps(restaurate_menus)
    return Response(response, mimetype="application/json")
   
#=================================================================
#====TARE SOLO EL PLATO DEL MENU EN ESPECIFICO RESTAURANTE========   
#TRAE EL PLATO EN ESPCIFICO FALTA SOLO ESA NAVEGACION Y HACER PURBA Y PROTOCOLO  HTTP EN SEGURIDAD 
#=================================================================

@app.route('/<name>/<nombre>', methods=['GET'])
def get_menu_name(name,nombre):
    restaurante = mongo.db.restaurante.find_one({"name": name},{"name":1,"_id":0})
    name_restaurante= restaurante["name"]
    menu = mongo.db.menu.find_one({"restaurante": name_restaurante,"nombre":nombre},{"nombre":1,"precio":1,"descripcion":1,"img":1,"_id":0})
    response = json_util.dumps(menu)
    return Response(response, mimetype="application/json")
    
#=================================================================
#============TARE TODO LOS MENU TODO LOS RESTAURANTE==============
#sirve para la busqueda de un plato de cualquier restaurante
#=================================================================

@app.route('/menu', methods=['GET'])
def get_menu():
    menu = mongo.db.menu.find()
    response = json_util.dumps(menu)
    return Response(response, mimetype="application/json")
#=================================================================
#=================================================================
#creacion de usuarios /clientes
#=================================================================
#=================================================================

@app.route('/usuarios',methods=['POST'])
def creacion_clientes():
    # recibe la data del usuario
    name = request.json['name']
    lastname = request.json['lastname']
    email = request.json['email']
    password = request.json['password']
    direction = request.json['direction']
    birthDate = request.json['birthDate']
    activated = request.json['activated']
    createDate = request.json['createDate']
    phone = request.json['phone']
    img = request.json['img']
    id =ObjectId()
    if name and email and password and lastname:
        hashed_password = generate_password_hash(password)
        mongo.db.usuarios.insert({'_id':id,
        'name': name,
        'lastname':lastname,
        'email': email, 
        'password': hashed_password, 
        'direction' : direction,
        "birthDate":birthDate,
        'activated' : activated ,
        'createDate': createDate,
        'phone':phone,
        'img':img
        })

        response = jsonify({
            '_id': str(id),
            'name': name
        })

        response.status_code = 201
        return response
    else:
        return not_found()


@app.route('/usuarios', methods=['GET'])
def post_usuario():
    usuario =mongo.db.usuarios.find({},{'name':1,'_id':1,'direction':1,'phone':1})
    response = json_util.dumps(usuario)
    return Response(response, mimetype="application/json")
#====================================================================================================
#====================================================================================================
#PARTE NUEVA TOMA DE PEDIDO DEL USUARIO DEBE HACER POR INSERT MANY PORQUE PUEDE SER MUHCO PEDIDO A LA VEZ
#nombre restaurante nombre del producto y id del cliente
#====================================================================================================
#====================================================================================================
@app.route('/<name>/<nombre>/<id>', methods=['POST'])
def usuarios_pedido(name,nombre,id):
    print(id)
    usuario= mongo.db.usuarios.find_one({"_id":ObjectId(id)},{"_id":1,"name":0})
    usuario=usuario['_id']
    restaurante = mongo.db.restaurante.find_one({"name": name},{"name":1,"_id":1,"domicilio":1})
    id_restaurante = restaurante["_id"]
    name_restaurante= restaurante["name"]
    domicilio = restaurante['domicilio']
    menu = mongo.db.menu.find_one({"restaurante": name_restaurante,"nombre":nombre},{"nombre":1,"precio":1,"descripcion":1,"img":1,"_id":0})
    descripcion = menu['descripcion']
    precio = menu['precio']
    createDate = request.json['createDate']
    nombre = menu['nombre']
    #eliminar esto
    #total = precio+domicilio
    total =request.json['total']
    id =ObjectId()
    if name and nombre and id :
        if nombre == nombre:
            try:
                mongo.db.compra.insert_many({
                    '_id':id,
                    'usuarioId':usuario,
                    'nameRestaurante': name_restaurante,
                    'idRestaurane': id_restaurante, 
                    'nameProducto': nombre, 
                    'descripcionProducto': descripcion, 
                    'domicilio' : domicilio,
                    "precio":precio,
                    'createDate': createDate,
                    'total':total
                    })


                response = jsonify({
                        '_id': str(id),
                        'usuarioId':str(usuario),
                    })

                response.status_code = 201
            except:
                mongo.db.compra.insert({
                    '_id':id,
                    'usuarioId':usuario,
                    'nameRestaurante': name_restaurante,
                    'idRestaurane': id_restaurante,
                    'nameProducto': nombre, 
                    'descripcionProducto': descripcion, 
                    'domicilio' : domicilio,
                    "precio":precio,
                    'createDate': createDate,
                    'total':total
                    })
     


                response = jsonify({
                        '_id': str(id),
                        'usuarioId':str(usuario),
                        })
                response.status_code = 201
        return response
    else:
        return not_found()


@app.route('/pedido', methods=['GET'])
def pedido_get():
    pedido =mongo.db.compra.find()
    response = json_util.dumps(pedido)
    return Response(response, mimetype="application/json")

@app.route('/pedido/<id>/<value>',methods=['GET'])
def respuesta_pedido(id,value):
    print(value)
    print(type(value))
    if value == '0':
        compra=mongo.db.compra.find_one({'usuarioId':ObjectId(id)},{"usuarioId":1,'nameRestaurante':1,'_id':1,'idRestaurane':1,'total':1}) 
        id_compra= compra['usuarioId']
        id_usuario = compra['usuarioId']
        nombre_restaurante =compra['nameRestaurante']
        id_restaurante = compra['idRestaurane']
        total= compra['total']
        mongo.db.rechazo.insert({'id_compra':id_compra,'id_usuario':id_usuario,'nombre_restaurante':nombre_restaurante,'id_restaurante':id_restaurante,'total':total})
        mongo.db.compra.delete_one({'usuarioId':ObjectId(id)})
        response = jsonify({'message': f'compra { id  } rechazada'})
        response.status_code = 201
        return response
    else:
        pedido =mongo.db.compra.find_one({'usuarioId':ObjectId(id)},{"usuarioId":1,'nameRestaurante':1,'_id':1,'idRestaurane':1,'total':1})
        response =json_util.dumps(pedido)
        if id in response:
            id_pedido = pedido['_id']
            name_pedido = pedido['nameRestaurante']
            id_res = pedido['idRestaurane']
            total = pedido['total']
            pedido = pedido['usuarioId']
            usuario = mongo.db.usuarios.find_one({'_id':ObjectId(pedido)},{'name':1})
            pedidos=mongo.db.usuarios.update({"_id":ObjectId(pedido)},{'$push':{'pedido':{"id":ObjectId(id_pedido),"nombre":name_pedido,"id_restaurante":id_res,"total":total}}})

            #usuario =json_util.dumps(usuario)
            #print(usuario)
        #mongo.db.usuarios.update({'usuarioId':respuesta},{'$push':{'compra':{'nombre_id':nameRestaurante}}})
        return  Response(pedidos, mimetype="application/json")


#=================================================================
#==================ES LA OPCION DE ELIMINAR=======================
#=================================================================

@app.route('/<name>', methods=['DELETE'])
def delete_user(name):
    try:
        restaurate_menu =mongo.db.restaurante.find_one({'name':name},{"menu":1,'_id':1})
        menus = restaurate_menu["menu"]
        for x in menus:
            a=x['id']
            mongo.db.menu.delete_one({'_id':ObjectId(a)})
        restaurate_menu =mongo.db.restaurante.find_one({'name':name},{'_id':1})
        mongo.db.restaurante.delete_one({'_id':ObjectId(restaurate_menu['_id'])})
        response = jsonify({'message':f'Restaurante eliminado y menu'})
        response.status_code = 200
        return response
    except:
        
        restaurate_menu =mongo.db.restaurante.find_one({'name':name},{'_id':1})
        mongo.db.restaurante.delete_one({'_id':ObjectId(restaurate_menu['_id'])})
        response = jsonify({'message':f'Restaurante  eliminado'})
        response.status_code = 200
        return response


@app.route('/restaurante/<id>', methods=['DELETE'])
def delete_restaurante(id):
    try:
        restaurate_menu =mongo.db.restaurante.find_one({'_id':ObjectId(id)},{"menu":1,'_id':1})
        menus = restaurate_menu["menu"]
        for x in menus:
            a=x['id']
            mongo.db.menu.delete_one({'_id':ObjectId(a)})
        mongo.db.restaurante.delete_one({'_id': ObjectId(id)})
        response = jsonify({'message': 'User' + id + ' Deleted Successfully'})
        response.status_code = 200
        return response
    except:
        restaurate_menu =mongo.db.restaurante.find_one({'_id':ObjectId(id)},{"menu":1,'_id':1})
        mongo.db.restaurante.delete_one({'_id': ObjectId(id)})
        response = jsonify({'message': 'User' + id + ' Deleted Successfully'})
        response.status_code = 200
        return response
#===================================================================================================
#esta parte no la he tocado mucho es la parte de eliminar un plato del menu 
#===================================================================================================

@app.route('/restaurante/<id>/<nombre>', methods=['DELETE'])
def delete_categoria(id,nombre):
    restaurante = mongo.db.restaurante.find_one({"_id": ObjectId(id)},{"name":1,"_id":0,"menu":1})
    name_restaurante= restaurante["name"]
    id_menu = restaurante['menu']
    for x in id_menu:
        a=x['id']
        mongo.db.menu.delete_one({"restaurante": name_restaurante,"nombre":nombre})
        if a == restaurante["menu.id"]:
            print(f'estas adentro para elimianr ese valor {a}')
            #mongo.db.restaurante.delete_one({"menu._id":ObjectId(a)})
    response = jsonify({'message': f'categoria{ id , nombre } Deleted Successfully'})
    response.status_code = 200
    return response


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'message': 'Resource Not Found ' + request.url,
        'status': 404
    }
    response = jsonify(message)
    response.status_code = 404
    return response


if __name__ == "__main__":
    app.run(debug=False)



