from flask import current_app as app
from app.conexion.Conexion import Conexion
from app.dao.gestionarcompras.registrarpedidocompras.dto import PedidoDeComprasDto

class PedidoDeComprasDao:
    
    def obtenerTodosLosPedidos(self):
        todoslospedidosSQL = """
        SELECT
            pdc.id_pedido_compra
            , pdc.id_empleado, p.nombres, p.apellidos,
            , pdc.id_sucursal
            , pdc.id_epc, edpc.descripcion,
            , pdc.fecha_pedido
            , pdc.id_deposito
        FROM
            public.pedido_de_compra AS pdc
        LEFT JOIN empleados e
            ON e.id_empleado = pdc.id_empleado
        LEFT JOIN personas p
            ON p.id_persona = e.id_empleado
        LEFT JOIN estado_de_pedido_compras edpc
        ON pdc.id_epc = edpc.id_epc
        """

    # agregar
    def agregar(self, pedidoDto: PedidoDeComprasDto):
        insertPedidoCompraCabecera = """
        INSERT INTO public.pedido_de_compra
        (id_empleado, id_sucursal, id_epc, fecha_pedido, id_deposito)
        VALUES(%s, %s, %s, %s, %s)
        RETURNING id_pedido_compra
        """

        insertDetalleCompra = """
        INSERT INTO public.pedido_de_compra_detalle
        (id_pedido_compra, id_producto, cantidad)
        VALUES(%s, %s, %s)
        """

        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        con.autocommit = False
        cur = con.cursor()
        try:
            ## Insertando la cabecera
            # (id_empleado, id_sucursal, id_epc, fecha_pedido, id_deposito)
            parametros = (pedidoDto.id_empleado, pedidoDto.id_sucursal, \
                pedidoDto.id_epc, pedidoDto.fecha_pedido, pedidoDto.id_deposito,)
            cur.execute(insertPedidoCompraCabecera, parametros)
            id_pedido_compra = cur.fetchone()[0]

            ## Insertando el detalle del pedido
            if len(pedidoDto.detallePedido) > 0:
                for pedido in pedidoDto.detallePedido:
                    # (id_pedido_compra, id_producto, cantidad)
                    parametrosdetalle = (id_pedido_compra, pedido.id_producto, pedido.cantidad,)
                    cur.execute(insertDetalleCompra, parametrosdetalle)

            # el ricolin, commit
            con.commit()

        except Exception as e:
            app.logger.error(f"Error a agregar un nuevo pedido: {str(e)}")
            con.rollback()
            return False
        finally:
            con.autocommit = True
            cur.close()
            con.close()

    # modificar
    def modificar(self):
        pass

    # anular
    def anular(self):
        pass