import logging
import pathlib
import mysql
import azure.functions as func

def obtenerSSLMySQL():
    path = pathlib.Path(__file__).parent.parent
    return str(path / 'BaltimoreCyberTrustRoot.crt.pem')

def conexionMySQLPaaS():
    servidor = "mysql2015170921.mysql.database.azure.com"
    puerto = "3306"
    usuario = "KarinaRG@mysql2015170921"
    contrasenia = "sisdis_KRG99"
    bd = "carrito"
    certificado = obtenerSSLMySQL()
    return mysql.connector.connect(host=servidor, port=puerto, user=usuario, passwd=contrasenia, db=bd,ssl_ca=certificado )

def convertirABinario(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def main(req: func.HttpRequest) -> func.HttpResponse:
    articulo = req.get_json().get('articulo')
    descripcion = articulo.descripcion    
    precio = float(articulo.precio)
    cantidad = int(articulo.cantidad)
    imagen = convertirABinario(articulo.imagen)
    con = conexionMySQLPaaS()
    cursor = con.cursor()
    try:
        stmt_1 = "SELECT ID_ARTICULO FROM ARTICULOS WHERE DESCRIPCION=%s"
        values = [(descripcion)]
        cursor.executemany(stmt_1,values)
        data = cursor.fetchall()
        if len(data) == 0:
            stmt_2 = "INSERT INTO ARTICULOS(DESCRIPCION,PRECIO,CANTIDAD) VALUES(%s,%s,%s)"
            values = [(descripcion,precio,cantidad)]
            cursor.executemany(stmt_2,values)                
            if imagen:
                stmt_3 = "INSERT INTO IMAGENES_ARTICULO(IMAGEN,ID_ARTICULO) VALUES (%s,(SELECT ID_ARTICULO FROM ARTICULOS WHERE DESCRIPCION=%s))"
                values = [(imagen,descripcion)]
                cursor.executemany(stmt_3,values)
                
            con.commit()
            return func.HttpResponse(f"ok", status_code=200)
        else:
            return func.HttpResponse(f"El Articulo ya existe", status_code=202)
    except Exception as e:
        con.rollback()
        return func.HttpResponse(f"{e}\n", status_code=500)
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
    

    
