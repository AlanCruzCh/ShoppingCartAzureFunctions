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
    descripcion = req.params.get('descripcion')
    con = conexionMySQLPaaS()
    cursor = con.cursor()
    try:
        stmt_1 = "SELECT CANTIDAD FROM CARRITO_COMPRA WHERE ID_ARTICULO=%s"
        values = [(descripcion)]
        cursor.executemany(stmt_1,values)
        data = cursor.fetchall()
        for row in data:
            elementosCarrito = int(row[0])
        stmt_2 = "SELECT ID_ARTICULO, CANTIDAD FROM ARTICULOS WHERE DESCRIPCION=%s"
        values = [(descripcion)]
        cursor.executemany(stmt_2,values)
        data = cursor.fetchall()
        for row in data:
            idArticulo = int(row[0])
            elementosExistentes = int(row[1])
        stmt_3 = "DELETE FROM CARRITO_COMPRA WHERE ID_ARTICULO=%s"
        values = [(idArticulo)]
        cursor.executemany(stmt_3,values)

        stmt_4 = "UPDATE articulos SET cantidad=%s WHERE id_articulo=%s"
        values = [(elementosExistentes+elementosCarrito,idArticulo)]
        cursor.executemany(stmt_4,values)

        con.commit()
        return func.HttpResponse(f"ok", status_code=200)
    except Exception as e:
        con.rollback()
        return func.HttpResponse(f"{e}\n", status_code=500)
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
