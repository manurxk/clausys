# Data access object - DAO
from flask import current_app as app
from app.conexion.Conexion import Conexion

class LoginDao:

    def buscarUsuario(self, usu_nick: str):

        buscar_usuario_sql = """
        SELECT
            u.id_usuario,
            TRIM(u.usu_nick) AS nick,
            u.usu_clave,
            u.usu_nro_intentos,
            u.id_funcionario,
            u.id_grupo,
            u.usu_estado,
            CONCAT(p.per_nombre, ' ', p.per_apellido) AS nombre_persona,
            g.des_grupo AS grupo
        FROM usuarios u
        LEFT JOIN funcionarios f ON f.id_funcionario = u.id_funcionario
        LEFT JOIN personas p ON p.id_persona = f.id_persona
        LEFT JOIN grupos g ON g.id_grupo = u.id_grupo
        WHERE u.usu_nick = %s AND u.usu_estado IS TRUE
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(buscar_usuario_sql, (usu_nick,))
            usuario_encontrado = cur.fetchone()
            if usuario_encontrado:
                return {
                    "id_usuario": usuario_encontrado[0],
                    "usu_nick": usuario_encontrado[1],
                    "usu_clave": usuario_encontrado[2],
                    "usu_nro_intentos": usuario_encontrado[3],
                    "id_funcionario": usuario_encontrado[4],
                    "id_grupo": usuario_encontrado[5],
                    "usu_estado": usuario_encontrado[6],
                    "nombre_persona": usuario_encontrado[7],
                    "grupo": usuario_encontrado[8]
                }
            else:
                return None
        except Exception as e:
            app.logger.error(f"Error al obtener usuario: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()
