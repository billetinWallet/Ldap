from ldap3 import Server, Connection, SIMPLE, SYNC, ALL, SUBTREE,MODIFY_ADD, ALL_ATTRIBUTES
from typing import Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from fastapi import FastAPI,status





class userData(BaseModel):
    username: str
    password: str


#Authentication user method 
def SimpleAuth(username, password):
    server = Server('ldap://localhost:389') 
    connection = Connection(server, user=f'uid={username},ou=users,dc=billetin,dc=com', password=password, authentication=SIMPLE)

    try:
        # Intentar establecer la conexión
        if not connection.bind():
            print('Error connection:', connection.result)
            return False

        # Realizar búsqueda del usuario en el directorio LDAP
        search_filter = f'(uid={username})'
        base_dn = f'uid={username},ou=users,dc=billetin,dc=com'
        attributes = ['cn', 'uid']

        connection.search(search_base=base_dn,
                          search_filter=search_filter,
                          search_scope=SUBTREE,
                          attributes=attributes)

        # Verificar las credenciales del usuario
        if connection.entries and connection.rebind(user=connection.entries[0].entry_dn, password=password):
            return True
        else:
            return False
        
    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        # Cerrar la conexión
        connection.unbind()


#Register user method
def Register(username, password):
    # Configurar la conexión LDAP
    server = Server('ldap://localhost:389')  # Ajusta la URL y el puerto según tu configuración
    connection = Connection(server, user='cn=admin,dc=billetin,dc=com', password='admin', authentication='SIMPLE')

    try:
        # Intentar establecer la conexión
        if not connection.bind():
            print('Error connection:', connection.result)
            return False

        # Crear la entrada LDIF para el nuevo usuario
        dn = f'uid={username},ou=users,dc=billetin,dc=com'
        entry = {
            'objectClass': ['top', 'person', 'organizationalPerson', 'inetOrgPerson'],
            'uid': username,
            'cn': f'{username}',
            'sn': 'Apellido',
            'givenName': username.capitalize(),
            'userPassword': password,
        }

        # Agregar el nuevo usuario al servidor LDAP
        connection.add(dn, attributes=entry)

        # Verificar que el usuario se haya agregado correctamente
        if connection.result['result'] == 0:
            return True
        else:
            print('Error:', connection.result)
            return False

    except Exception as e:
        return f"Error: {str(e)}"
    
    finally:
        # Cerrar la conexión
        connection.unbind()



# test login method 
# username = 'nuevo_usuario_2'
# password = 'nueva_contraseña_2'

# if ldap_login(username, password):
#    print('¡Inicio de sesión exitoso!')
# else:
#    print('Inicio de sesión fallido.')

#test add a new user in directory
# nuevo_usuario = 'nuevo_usuario_2'
# nueva_contraseña = 'nueva_contraseña_2'

# agregar_usuario(nuevo_usuario, nueva_contraseña)

app = FastAPI()


# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}   


# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


@app.post("/auth")
async def ldapAuth(request:userData):
    response = SimpleAuth(request.username, request.password)
    if (response == True):
        return JSONResponse(status_code=status.HTTP_200_OK,content=response)
    
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content=response)  


@app.post("/register")
async def ldapRegister(request:userData):
    response = Register(request.username, request.password) 
    if(response == True):
        return JSONResponse(status_code=status.HTTP_201_CREATED,content = response)

    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content=response) 