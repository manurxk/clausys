-- QUE ES DDL, DML
-- snake case

CREATE TABLE estado_de_pedido_compras(
    id_epc SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE depositos(
    id_deposito SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE productos(
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(60) UNIQUE NOT NULL,
    cantidad INTEGER,
    precio_unitario INTEGER
);

CREATE TABLE sucursales(
    id_sucursal SERIAL PRIMARY KEY,
    descripcion VARCHAR(60) UNIQUE NOT NULL,
    id_deposito INTEGER NOT NULL,
    FOREIGN KEY(id_deposito) REFERENCES
    depositos(id_deposito)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE personas(
    id_persona SERIAL PRIMARY KEY,
    nombres VARCHAR(70) NOT NULL,
    apellidos VARCHAR(70) NOT NULL,
    ci TEXT NOT NULL,
    fechanac DATE,
    creacion_fecha DATE NOT NULL,
    creacion_hora TIME NOT NULL,
    creacion_usuario INTEGER NOT NULL,
    modificacion_fecha DATE,
    modificacion_hora TIME,
    modificacion_usuario INTEGER--,
    /*FOREIGN KEY(creacion_usuario) REFERENCES
    usuarios(id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE
    FOREIGN KEY(modificacion_usuario) REFERENCES
    usuarios(id_usuario)
    ON DELETE RESTRICT ON UPDATE CASCADE*/
);

CREATE TABLE empleados(
    id_empleado INTEGER PRIMARY KEY,
    fecha_ingreso DATE NOT NULL,
    FOREIGN KEY(id_empleado) REFERENCES personas(id_persona)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE usuarios(
    id_usuario INTEGER PRIMARY KEY,
    nickname TEXT NOT NULL,
    clave TEXT NOT NULL,
    estado BOOLEAN NOT NULL,
    FOREIGN KEY(id_usuario) REFERENCES personas(id_persona)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE pedido_de_compra(
    id_pedido_compra SERIAL PRIMARY KEY,
    id_empleado INTEGER NOT NULL,

);