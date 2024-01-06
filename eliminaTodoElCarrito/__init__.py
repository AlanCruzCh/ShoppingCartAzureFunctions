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

def main(req: func.HttpRequest) -> func.HttpResponse:
    con = conexionMySQLPaaS()
    cursor = con.cursor()
    Articulos = []
    cantidadCarrito = []
    cantidadExistente = []
    try:
        stmt_1 = "SELECT ID_ARTICULO, CANTIDAD FROM CARRITO_COMPRA"
        cursor.execute(stmt_1)
        data = cursor.fetchall()
        for row in data:
            Articulos.append(int(row[0]))
            cantidadCarrito.append(int(row[1]))
            
        for id_articulo in Articulos:
            stmt_2 = "SELECT CANTIDAD FROM ARTICULOS WHERE ID_ARTICULO=%s"
            cursor.executemany(stmt_2,[(id_articulo)])
            data = cursor.fetchall()
            for row in data:
                cantidadExistente.append(row[0])
            
        for id_articulo in Articulos:
            stmt_3 = "DELETE FROM CARRITO_COMPRA WHERE ID_ARTICULO=%S"
            cursor.executemany(stmt_3,[(id_articulo)])

        for pos in range(len(Articulos)-1):
            stmt_4 = "UPDATE articulos SET cantidad=%s WHERE id_articulo=%s"
            values = [(cantidadCarrito(pos)+cantidadExistente(pos),Articulos(pos))]
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
