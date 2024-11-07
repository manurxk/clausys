CREATE TABLE grupos(
    gru_id SERIAL PRIMARY KEY
    , gru_des VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE modulos(
    mod_id SERIAL PRIMARY KEY
    , mod_des VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE cargos(
    car_id SERIAL PRIMARY KEY
    , car_des VARCHAR(60) UNIQUE NOT NULL
);

CREATE TABLE usuarios(
    usu_id SERIAL PRIMARY KEY
    , usu_nick VARCHAR(10) UNIQUE NOT NULL
    , usu_clave VARCHAR(300) NOT NULL
    , usu_nro_intentos INTEGER NOT NULL
    , fun_id INTEGER NOT NULL
    , gru_id INTEGER NOT NULL
    /*
    hola soy yo de nuevo, ayer escribi esto,
    me encanta, pero seguis vos ahora.
    */
);


CREATE TABLE paginas(
    pag_id SERIAL PRIMARY KEY
    , pag_nombre VARCHAR(60) UNIQUE NOT NULL
    , pag_direcc TEXT NOT NULL
    , pag_estado BOOLEAN NOT NULL
    , mod_id INTEGER NOT NULL
    , FOREIGN KEY(mod_id) REFERENCES modulos(mod_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE permisos(
    pag_id INTEGER
    , gru_id INTEGER
    , leer BOOLEAN NOT NULL
    , insertar BOOLEAN NOT NULL
    , editar BOOLEAN NOT NULL
    , borrar BOOLEAN NOT NULL
    , PRIMARY KEY(pag_id, gru_id)
    , FOREIGN KEY(pag_id) REFERENCES paginas(pag_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
    , FOREIGN KEY(gru_id) REFERENCES grupos(gru_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
);