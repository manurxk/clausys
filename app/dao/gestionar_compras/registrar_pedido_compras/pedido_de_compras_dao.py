from flask import current_app as app
from app.conexion.Conexion import Conexion
from app.dao.gestionar_compras.registrar_pedido_compras.dto.pedido_de_compras_dto import PedidoDeComprasDto

class PedidoDeComprasDao:
    
    def obtener_pedidos(self):
        query_pedidos = """
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
    def agregar(self, pedido_dto: PedidoDeComprasDto):
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
            parametros = (pedido_dto.id_empleado, pedido_dto.id_sucursal, \
                pedido_dto.id_epc, pedido_dto.fecha_pedido, pedido_dto.id_deposito,)
            cur.execute(insertPedidoCompraCabecera, parametros)
            id_pedido_compra = cur.fetchone()[0]

            ## Insertando el detalle del pedido
            if len(pedido_dto.detallePedido) > 0:
                for pedido in pedido_dto.detallePedido:
                    # (id_pedido_compra, id_producto, cantidad)
                    parametrosdetalle = (id_pedido_compra, pedido.id_producto, pedido.cantidad,)
                    cur.execute(insertDetalleCompra, parametrosdetalle)

            # Confirma la transacción
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