import psycopg2

class Conexion:

    """Metodo constructor
    """
    def __init__(self):
        self.con = psycopg2.connect("dbname=veterinaria-db user=juandba host=localhost password=admin")

    """getConexion

        retorna la instancia de la base de datos
    """
    def getConexion(self):
        return self.con