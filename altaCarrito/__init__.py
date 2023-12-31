import logging
import pathlib
import mysql
import azure.functions as func

def conexionMySQLPaaS():
    servidor = "t8-2015110269-bd.mysql.database.azure.com"
    puerto = "3306"
    usuario = "Alan"
    contrasenia = "contrasea-del-usuario-Alan"
    bd = "database_shopping_cart"
    return mysql.connector.connect(host=servidor, port=puerto, user=usuario, passwd=contrasenia, db=bd)

def main(req: func.HttpRequest) -> func.HttpResponse:
    descripc = req.params.get('descripcion')
    cantidad = int(req.params.get('cantidad'))
    con = conexionMySQLPaaS()
    cursor = con.cursor()
    try:
        stmt_1 = "SELECT ID_ARTICULO, CANTIDAD FROM ARTICULOS WHERE DESCRIPCION=%s"
        values = [(descripc)]
        cursor.executemany(stmt_1,values)
        data = cursor.fetchall()
        for row in data:
            id_articulo = int(row[0])
            cantidadActual = int(row[1])
        if cantidad <= cantidadActual:
            stmt_2 = "UPDATE articulos SET cantidad=%s WHERE id_articulo=%s"
            values = [(cantidadActual-cantidad,id_articulo)]
            cursor.executemany(stmt_2,values)            
            stmt_3 = "INSERT INTO CARRITO_COMPRA(ID_ARTICULO,CANTIDAD) VALUES (%s,%s)"
            values = [(id_articulo,cantidad)]
            cursor.executemany(stmt_3,values)
            con.commit()
            return func.HttpResponse(f"ok", status_code=200)
    except Exception as e:
        con.rollback()
        return func.HttpResponse(f"{e}\n", status_code=500)
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
