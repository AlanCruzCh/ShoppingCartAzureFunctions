import json
import logging
import mysql
import pathlib
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

def main(req: func.HttpRequest) -> func.HttpResponse:
    busqueda = req.params.get('busqueda')
    con = conexionMySQLPaaS()
    cursor = con.cursor()
    try:
        stmt_1 = "SELECT a.descripcion, a.cantidad, a.precio, b.imagen FROM articulos a LEFT OUTER JOIN imagenes_articulo b ON a.id_articulo=b.id_articulo WHERE descripcion LIKE '%'%s'%'"
        values = [(busqueda)]
        cursor.executemany(stmt_1,values)
        data = cursor.fetchall()
        if len(data) != 0:
            articulos = []
            for row in data:
                articulo = {
                    'descripcion': row[0],
                    'cantidad': row[1],
                    'precio': row[2],
                    'imagen': row[3]
                }
                articulos.append(articulo)
            return func.HttpResponse(json.dumps(articulos), status_code=200)
        else:
            return func.HttpResponse(f"No se encontraron resultados", status_code=202)
    except Exception as e:
        return func.HttpResponse(f"{e}\n", status_code=500)
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
    
