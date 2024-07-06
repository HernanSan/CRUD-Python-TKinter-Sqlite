import sqlite3

def save_info(db_name, table_name, args_colums, args_values, select_data=None):

    """guarda información en tablas de sqlite3 con INSERT.

    útiliza el comando SQL INSERT  para crear registros en
    la base de datos y tabla que le indiquemos usando la 
    sintaxis de INSERT-VALUES e INSERT-SELECT propia
    de la base de datos sqlite en su version 3.34.

    Parámetros:
    db_name -- nombre de la base de datos a conectarse (obligatorio, tipo str)
    table_name -- nombre de la tabla en la base de datos (obligatorio, tipo str)
    args_colums -- nombre de las columnas a ser afectadas (tupla con los nombres 
                    de la columna tipo str)
    args_values -- valores a introducir en las columnas afectadas (tipo tupla)
    select_data -- datos para crear el query con un SELECT stament almacenados en 
                    diccionarios y estos en una tupla

    la estructura del select_data debe ser así:
        
        ({"from_column":"<name_coumn>",
        "from_table":"<table_name>",
        "column_constrain":"<name_column>",
        "data":"<data>"}, {...}, ...)
    
    """

    #abrimos la base de datos y creamos el promt
    conection = sqlite3.connect(db_name)
    promt = conection.cursor()

    #creamos el query
    # comprobamos si se paso el parametro select data
    if select_data:
        #creamos un sub_query vacio
        sub_query = ""
        #poblamos el sub_query segun la cantidad de diccionarios recibido 
        for x in range(len(select_data)):
            #identificamos el ultimo diccionario para formatear correctamente el query
            if x == (len(select_data)-1):
                
                sub_query += f"(SELECT {select_data[x]['from_column']} FROM {select_data[x]['from_table']} WHERE {select_data[x]['column_constrain']}={select_data[x]['data']})"
            #select staments intermedios
            else:
                sub_query += f"(SELECT {select_data[x]['from_column']} FROM {select_data[x]['from_table']} WHERE {select_data[x]['column_constrain']}={select_data[x]['data']}), "
        #creamos el query principal e insertamos el sub_query
        query = f"INSERT INTO {db_name}.{table_name} {args_colums} ({sub_query});"

    else:
        #query con la estructura basica de columns y valores para la columna 
        query = f"INSERT INTO {db_name}.{table_name} {args_colums} VALUES {args_values};"
        
    #ejecutamos el query
    #promt.execute(query)
    
    #comitiamos los cambios y cerramos la coneccion
    #conection.commit()
    #conection.close()

    #corroboracion
    print(query)
 
def get_data(db_name, args_colums, table, info_joing=None, info_where=None, info_and=None):
    """obtener información en tablas de sqlite3 con SELECT.

    útiliza el comando SQL SELECT  para obterner informacion en
    la base de datos y tabla que le indiquemos usando la 
    sintaxis de **** propia
    de la base de datos sqlite en su version 3.34.

    Parámetros:
    db_name     -- nombre de la base de datos a conectarse (obligatorio, tipo str)
    args_colums -- nombre de las columnas a ser afectadas (tupla con los nombres de la columna tipo str)
    table       -- nombre de la tabla de donde proviene los datos (tipo str)
    info_joing  -- diccionario con la informacion necesario para construir un select-joing-stament (tipo diccionario)
    info_where  -- diccionario con la informacion necesario para filtrar la informacion optenida (ripo diccionario)
    info_and    -- diccionario con la informacion necesario para agregar mas de un filtro (tipo diccionario)
    
    la estructura del info_joing debe ser así:
        
        {"joing_type":"<type_joing>",
        "joing_table":"<table_name>",
        "key_column":"<key_column>",
        "fk_column":"<fk_column>"}

        DONDE: "joing_type" es un str con el tipo de JOING que se quiere hacer
        "joing_table" es un str con el nombre de la tabla con la que se va hacer JOING
        "key_column" es un str con el nombre de la columna primary key
        "fk_column"  es un str con el nombre de la columna foreign key 
    
    la estructura del info_where debe ser así:
        
        {"column_constrain":"<column_constrain>",
        "type_where":"<type_where>"}

        DONDE: "column_constrain" es un str con el nombre de columna que se va usar como filtro
        "type_where" es un str con el tipo de where que se va usar segun el lenguaje SQL

    la estructura del info_and debe ser así:
        
        {"amount":"<amount>",
        "column_constrain":"<column_constrain>"}

        DONDE: "amount" es un int con el numero de and que vamos a usar
        "column_constrain" es un str con el nombre de columna que se va usar como filtro
        "type_and" es un str con el tipo de and que se va usar segun el lenguaje SQL

    """

    #abrimos la base de datos y creamos el promt
    conection = sqlite3.connect(db_name)
    promt = conection.cursor()

    #creamos el query

    try:
    
        query = f"SELECT {args_colums} FROM {table}"    

        if info_joing:

            sub_query = f" {info_joing['joing_type']} {info_joing['joing_table']} ON {info_joing['key_column']} = {info_joing['fk_column']}"

            query += sub_query

        if info_where:

            sub_query = f" WHERE {info_where['column_constrain']} {info_where['type_where']}"

            query += sub_query

        if info_and:

            for x in range(info_and["amount"]):

                query += f" AND {info_and['column_constrain']} {info_and['type_and']}"

    finally:
        query+= ";"
        
    #ejecutamos el query
    #promt.execute(query)
    
    #comitiamos los cambios y cerramos la coneccion
    #conection.commit()
    #conection.close()

    #corroboracion
    print(query)

def db_manager_f(db_name, sql_comand=None, info_fetch=False):

    try:
        #abrimos la base de datos y creamos el cursor
        conection = sqlite3.connect(db_name)
        cursor = conection.cursor()

        #ejecutamos el query
        cursor.execute(sql_comand)

        if info_fetch:
            
            info = cursor.fetchall()

            #comitiamos los cambios y cerramos la coneccion
            conection.commit()
            conection.close()
            
            return info

        #comitiamos los cambios y cerramos la coneccion
        conection.commit()
        conection.close()

        return True
        
    except:
        return False 