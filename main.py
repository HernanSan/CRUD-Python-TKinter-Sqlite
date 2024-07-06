from tkinter import *
from tkinter import messagebox
from tkcalendar import *
from datetime import datetime as dt
from PIL import Image, ImageTk

from db_manager import db_manager_f
from sqlite3 import *

app = Tk()
app.title('CONTROL DE FECHAS DE VENCIMIENTO')
app.geometry('700x550')
app.iconphoto(False, PhotoImage(file='icon/f2.png'))

#creacion y preparacion de imagen de bienvenida
image = Image.open('icon/welcome.png')
image = image.resize((440,490))
welcomeimage = ImageTk.PhotoImage(image)


#funciones

#funcion para construir el formulario de registro de productos
def build_register_form():

    #funciones de uso interno para obtener los datos del formulario
    def get_register_data():

        # obtener datos
        try:
            #validar valores numericos
            code = int(product_code.get())
        except ValueError:
            messagebox.showinfo('ALERTA', 'Debe introducir valores númericos en el campo "Código de barra"')
            product_code.delete(0,END)
        
        #Validar existencia de SQL en el nombre del producto
        product = product_name.get()
        if complete_statement(product):
            product_code.delete(0,END)
            product_name.delete(0,END)
            product_amount.delete(0,END)
            messagebox.showinfo('ALERTA "SQL INJECTION"', 'NO INGRESE SQL STAMENTS"')
            return print("ALERT ATTEMPT SQL INJECTION")
        
        try:
            #validar valores numericos
            amount = int(product_amount.get())
        except ValueError:
            messagebox.showinfo('ALERTA', 'Debe introducir valores númericos en el campo "Cantidad Del Producto"')
            product_amount.delete(0, END)

        #no necesita validacion
        date = calendar.get_date()

        #confirmar los datos
        try:    
            answer = messagebox.askyesno('Datos Introducidos',
            f'Quieres guardar estos datos?\n\ncódigo de barra: {code}\n\nNombre: {product}\n\nCantidad: {amount}\n\nFecha: {date}')
        except UnboundLocalError:
            #avisamos que hay errores en lo valores e instamos a corregir
            messagebox.showinfo('ALERTA', 'REVISE LOS VALORES INTRODUCIDOS')
            product_name.delete(0, END)
        
        if answer:
        
            # borrar el formulario
            product_code.delete(0,END)
            product_name.delete(0,END)
            product_amount.delete(0,END)
            
            #comprobar si el producto ya existe en la BD
            sql_comand = f"SELECT * FROM products WHERE bar_code={code}"

            product_exist = db_manager_f("m_vencimiento.db", sql_comand=sql_comand, info_fetch=True)

            if not product_exist:
                #guardamos informacion en la tabla products, columnas bar_code y name

                sql_comand = f"INSERT INTO products (bar_code, name) VALUES ({code},'{product}');"

                db_manager_f("m_vencimiento.db", sql_comand=sql_comand)

            #comprobamos si la fecha relacionada a una cantidad existe
            sql_comand = f"SELECT * FROM expiration_dates WHERE date='{date}' AND quantity={amount}"

            product_exist = db_manager_f("m_vencimiento.db", sql_comand=sql_comand, info_fetch=True)

            if not product_exist:

                #guardamos informacion en la tabla expiration_dates, columnas date y quantity 
                sql_comand = f"INSERT INTO expiration_dates (date, quantity) VALUES ('{date}',{amount});"
                db_manager_f("m_vencimiento.db", sql_comand=sql_comand)

            #guardamos informacion en la tabla products_dates, columnas id_products y id_dates
            sub_comand1=f"SELECT bar_code FROM products WHERE bar_code={code}"
            sub_comand2=f"SELECT id_expiration_date FROM expiration_dates WHERE date='{date}'"

            sql_comand = f"INSERT INTO products_dates (id_products, id_dates) VALUES (({sub_comand1}),({sub_comand2}));"
            db_manager_f("m_vencimiento.db", sql_comand=sql_comand)

#
    # borramos el frame derecho
    right_frame = Frame(father_frame, bg='white', relief='ridge', bd=2)
    right_frame.place(relx=0.35,y=31, relwidth=0.6, height=490)
    
    #widget del titulo
    label_title = Label(right_frame, text='REGISTRO DE PRODUCTO', bg='#3498db', fg='white')
    label_title.place(relx=0, y=0, relwidth=1, height=20)

    #widgets del codigo de barra
    label_code = Label(right_frame, text='           CÓDIGO', bg='white', fg='black')
    product_code = Entry(right_frame, bg='white', fg='black')

    label_code.place(relx=0.02, y=30)
    product_code.place(relx=0.37, y=30, relwidth=0.6)
    
    #widgets del nombre del producto
    label_name = Label(right_frame, text='           NOMBRE', bg='white', fg='black')
    product_name = Entry(right_frame, bg='white', fg='black')

    label_name.place(relx=0.02, y=60)
    product_name.place(relx=0.37, y=60, relwidth=0.6)
    
    #widgets de la cantidad del producto
    label_product_amount = Label(right_frame, text='         CANTIDAD', bg='white', fg='black')
    product_amount = Entry(right_frame, bg='white', fg='black')
    
    label_product_amount.place(relx=0.02, y=90)
    product_amount.place(relx=0.37, y=90, relwidth=0.6)

    #widgets de la fecha de caducidad del producto
    label_product_date = Label(right_frame, text='         CADUCIDAD', bg='white', fg='black')
    calendar = Calendar(right_frame, selectmode='day', year=dt.now().year, month=dt.now().month, day=dt.now().day, date_pattern='y-mm-dd')

    label_product_date.place(relx=0.02, y=180)
    calendar.place(relx=0.37, y=120, relwidth=0.6)

    #boton de guardar
    button_get_info = Button(right_frame, text='Guardar', command=get_register_data, bg='#3498db')

    button_get_info.place(relx=0.05, y=435, relwidth=0.92, height=40)


    #funcion para construir el formulario de modificacion

#funcion para modificar registros
def build_modifier_form():
    
    list_products = None

    #funciones de uso interno

    #funcion para poblar la lista de resultados con los productos
    def print_result_to_screen():

        nonlocal list_result
        
        #borramos informacion anterior
        list_result.delete(0,END)

        #poblamos la caja-lista
        for i,x in enumerate(list_products):
            line = "{a:_<15.15} {b}".format(a=x[0],b=x[1])
            list_result.insert(i,line)
            if i%2:
                list_result.itemconfigure(i, background='black', fg="white")
        
        list_result.bind("<Double-1>", draw_update_form)
    
    #funcion para dibujar el formulario de actualizar datos
    def draw_update_form(*args):

            #funcion para actualizar la seleccion
        def update_selection():

            #obtener el nombre del producto y validar existencia de SQL en él
            new_name = new_name_entry.get()
            if complete_statement(new_name):
                new_name_entry.delete(0,END)
                new_bar_code_entry.delete(0,END)
                messagebox.showinfo('ALERTA "SQL INJECTION"', 'NO INGRESE SQL STAMENTS"')
                return print("ALERT ATTEMPT SQL INJECTION")

            #obtener y validar el código de barra
            try:
                #validar valores numericos
                if new_bar_code_entry.get():
                    code = int(new_bar_code_entry.get())
                else:
                    code = None
            except ValueError:
                messagebox.showinfo('ALERTA', 'Debe introducir valores númericos en el campo "Código de barra"')
                product_code.delete(0,END)
            
            #crear el query segun la informacion enviada por el usuario
            sql_comand = f'UPDATE products SET name="{new_name  }", bar_code={code} WHERE bar_code={selected_product[1]};'
            
            #ejecutamos el query
            if db_manager_f('m_vencimiento.db', sql_comand=sql_comand):
            
                #notificamos al usuario de la operacion
                messagebox.showinfo("Informacion Guardada", "Operacion Ejecutada Exitosamente")
        
        #obtener la seleccion de la lista
        selection = list_result.curselection()

        #segun la seleccion en la lista obtenemos los datos del producto seleccionado
        selected_product = list_products[selection[0]]

        #widget del titulo de nuevos datos
        label_title = Label(right_frame, text='Nuevos Datos', bg='#3454aa', fg='white')
        label_title.place(relx=0.525, y=240, relwidth=0.469)

        #widgets de las entradas para introducir los nuevos datos

            #entrada del nombre y ubicacion
        new_name_entry = Entry(right_frame,bg='white',fg='black')
        new_name_entry.place(relx=0.525, y=265, relwidth=0.469)
        new_name_entry.insert(0,selected_product[0])

            #identificacion de la entrada del nombre y ubicacion
        new_label_name_entry = Label(right_frame, text='Nuevo Nombre', fg='#3454aa', bg='white')
        new_label_name_entry.place(relx=0.525, y=290, relwidth=0.469, height=10)

            #entrada del código y ubicación
        new_bar_code_entry = Entry(right_frame,bg='white',fg='black',)
        new_bar_code_entry.place(relx=0.525, y=315, relwidth=0.469)
        new_bar_code_entry.insert(0,selected_product[1])

            #identificacion de la entrada del código y ubicación
        new_label_bar_code_entry = Label(right_frame, text='Nuevo Código de Barra', fg='#3454aa', bg='white')
        new_label_bar_code_entry.place(relx=0.525, y=340, relwidth=0.469, height=10)

            #widget para buscar segun los datos introducidos por el usuario
        update_button = Button(right_frame, text='ACTUALIZAR', bg='#3454aa',fg='white', command=update_selection)
        update_button.place(relx=0.62, y=375)

    #funcion para ecnontrar los productos para la lista de productos
    def find_products():

        #variable en el scoope superior
        nonlocal list_products
        
        # obtener datos y validarlos
        
        #obtener el nombre del producto y validar existencia de SQL en él
        name_product = name_entry.get()
        if complete_statement(name_product):
            name_entry.delete(0,END)
            bar_code_entry.delete(0,END)
            messagebox.showinfo('ALERTA "SQL INJECTION"', 'NO INGRESE SQL STAMENTS"')
            return print("ALERT ATTEMPT SQL INJECTION")

        #obtener y validar el código de barra
        try:
            #validar valores numericos
            if bar_code_entry.get():
                code = int(bar_code_entry.get())
            else:
                code = None
        except ValueError:
            messagebox.showinfo('ALERTA', 'Debe introducir valores númericos en el campo "Código de barra"')
            product_code.delete(0,END)

        #crear el query y sub_querys segun la informacion enviada por el usuario
        sql_comand = 'SELECT name,bar_code FROM products'

        if name_product and code:
            sub_query = f' WHERE bar_code={code};'
            sql_comand += sub_query

        elif name_product and code == None:
            sub_query = f' WHERE name LIKE "%{name_product}%";'
            sql_comand += sub_query

        elif name_product == '' and code == None:
            messagebox.showinfo('ALERTA', 'Debe introducir información para realizar la busqueda')
            sql_comand = ''

        elif code and name_product == "":
            sub_query = f' WHERE bar_code={code};'
            sql_comand += sub_query
        
        #obtenemos la información de la base de datos y guardamos
        if sql_comand:
            list_products = db_manager_f("m_vencimiento.db", sql_comand=sql_comand, info_fetch=True)

        #Imprimimos los resultados en pantalla
        print_result_to_screen()

#
    #borramos el frame derecho
    right_frame = Frame(father_frame, bg='white', relief='ridge', bd=2)
    right_frame.place(relx=0.35,y=31, relwidth=0.6, height=490)

    #widget del titulo
    label_title = Label(right_frame, text='Modificación De Registros', bg='#3498db', fg='white')
    label_title.place(relx=0, y=0, relwidth=1, height=20)

    #widget del titulo buscar
    label_title = Label(right_frame, text='Buscar', bg='#3498db', fg='white')
    label_title.place(relx=0.525, y=55, relwidth=0.469, height=20)

    #widget caja-lista para mostrar los resultados
    list_result = Listbox(right_frame, bg='white', fg='black')
    list_result.place(relx=0.02, y=30, relwidth=0.5, relheight=0.92)

    #widgets de las entradas para identificar el producto

        #entrada del nombre y ubicacion
    name_entry = Entry(right_frame,bg='white',fg='black')
    name_entry.place(relx=0.525, y=80, relwidth=0.469)

        #identificacion de la entrada del nombre y ubicacion
    label_name_entry = Label(right_frame, text='Nombre', fg='#3498db', bg='white')
    label_name_entry.place(relx=0.525, y=105, relwidth=0.469, height=10)

        #entrada del código y ubicación
    bar_code_entry = Entry(right_frame,bg='white',fg='black')
    bar_code_entry.place(relx=0.525, y=130, relwidth=0.469)

        #identificacion de la entrada del código y ubicación
    label_bar_code_entry = Label(right_frame, text='Código de Barra', fg='#3498db', bg='white')
    label_bar_code_entry.place(relx=0.525, y=160, relwidth=0.469, height=10)

    #widget para buscar segun los datos introducidos por el usuario

    find_button = Button(right_frame, text='BUSCAR', bg='#3498db',fg='white', command=find_products)
    find_button.place(relx=0.65, y=180)

#funcion para construir el formulario de busqueda de productos
def build_viewer_data():
    
    #variables a ser usadas dentro de las funciones internas
    list_products = None # variable que tendra una lista de tuplas con los datos de los productos (name,date,quantity,id,id_dates)
    list_result = None # es una variable que tiene una lista de strings según las tuplas en list_products para mostar al usuario name,date
    order_by = StringVar()
    
    #funciones de uso interno

    #funcion para imprimir en la pantalla la lista de resultados
    def print_result_to_screen():

        nonlocal list_result
        
        #borramos informacion anterior
        list_result.delete(0,END)

        #poblamos la caja-lista
        for i,x in enumerate(list_products):
            line = "{a:_<15.15} {b}".format(a=x[0],b=x[1])
            list_result.insert(i,line)
            if i%2:
                list_result.itemconfigure(i, background='black', fg="white")    
    
    #funcion para imprimir la lista de resultados
    def print_result_to_archive():

        #identificamos el OS

        from pathlib import Path

        #path del archivo a crear
        base_directory = Path.home()
        #nombre del archivo a crear
        name = Path(base_directory, "modulo_vencimiento", f"{dt.now().year}-{dt.now().month}-{dt.now().day}-{dt.now().hour}-{dt.now().minute}.txt")

        #abrimos el archivo
        printer = open(f"{name}",'w')

        #obtenemos la información de la lista
        list_to_print = list_result.get(0,END)

        #imprimos la información
        for x in range(len(list_to_print)):
            printer.write(f'{list_to_print[x]}\n')

        printer.close()

    #funcion para buscar los productos para la lista de resultados
    def search_and_print():

        nonlocal list_products

        # obtener datos y validarlos
        
        #obtener el nombre del producto y validar existencia de SQL en él
        name_product = name_entry.get()
        if complete_statement(name_product):
            name_entry.delete(0,END)
            bar_code_entry.delete(0,END)
            messagebox.showinfo('ALERTA "SQL INJECTION"', 'NO INGRESE SQL STAMENTS"')
            return print("ALERT ATTEMPT SQL INJECTION")

        #obtener y validar el código de barra
        try:
            #validar valores numericos
            if bar_code_entry.get():
                code = int(bar_code_entry.get())
            else:
                code = None
        except ValueError:
            messagebox.showinfo('ALERTA', 'Debe introducir valores númericos en el campo "Código de barra"')
            product_code.delete(0,END)
        
        #obtener los datos de las fechas en el formato adecuado no necesita validation
        init_date = calendar_init.get()
        final_date = calendar_final.get()

        #crear el query y sub_querys segun la informacion enviada por el usuario
        sql_comand = 'SELECT name,date,quantity,id,id_dates FROM products_dates INNER JOIN products ON id_products=bar_code INNER JOIN expiration_dates ON id_dates=id_expiration_date'

        if name_product and code:
            sub_query = f' WHERE bar_code={code} AND date BETWEEN "{init_date}" AND "{final_date}"'
            sql_comand += sub_query

        elif name_product and code == None:
            sub_query = f' WHERE name LIKE "%{name_product}%" AND date BETWEEN "{init_date}" AND "{final_date}"'
            sql_comand += sub_query

        elif name_product == "" and code == None:
            sub_query = f' WHERE date BETWEEN "{init_date}" AND "{final_date}"'
            sql_comand += sub_query

        elif code and name_product == "":
            sub_query = f' WHERE bar_code={code} AND date BETWEEN "{init_date}" AND "{final_date}"'
            sql_comand += sub_query
        
        sql_comand += order_by.get()
        
        #obtenemos la informacion de la base de datos y guardamos
        list_products = db_manager_f("m_vencimiento.db", sql_comand=sql_comand, info_fetch=True)

        #imprimos el resultado en pantalla
        print_result_to_screen()
    
    #funcion para borrar elementos de la lista de resultados
    def delete_selection():

        #obtener la seleccion de la lista
        selection = list_result.curselection()

        #segun la seleccion en la lista obtenemos los datos del producto seleccionado
        selected_product = list_products[selection[0]]

        #creamos y ejecutamos los sql
        
            #sql para borrar el producto de la tabla products
        sql_comand = f'DELETE FROM products WHERE name="{selected_product[0]}";'
        db_manager_f("m_vencimiento.db", sql_comand)
        
            #comprobamos si existe varios productos relacionados a una misma fecha-cantidad
        sql_comand = f'SELECT id_dates FROM products_dates WHERE id_dates={selected_product[4]}'
        many_expiration_date = db_manager_f("m_vencimiento.db", sql_comand, info_fetch=True)
        
        if len(many_expiration_date) <= 1:
            #sql para borrar la fecha si solo existe una fecha relacionada al producto
            sql_comand = f'DELETE FROM expiration_dates WHERE date="{selected_product[1]}" AND quantity={selected_product[2]};'
            db_manager_f("m_vencimiento.db", sql_comand)
        
            #sql para borrar la informacion de la tabla pivote products_dates
        sql_comand = f'DELETE FROM products_dates WHERE id={selected_product[3]};'
        db_manager_f("m_vencimiento.db", sql_comand)
        
        #borramos el elemento seleccionado de la lista mostrada y de la lista de productos para mantener paridad
        list_result.delete(selection[0])
        del list_products[selection[0]]

#   
    # borramos el frame derecho
    right_frame = Frame(father_frame, bg='white', relief='ridge', bd=2)
    right_frame.place(relx=0.35,y=31, relwidth=0.6, height=490)

    #widget del titulo
    label_title = Label(right_frame, text='LISTA DE PRODUCTOS', bg='#3498db', fg='white')
    label_title.place(relx=0, y=0, relwidth=1, height=20)
    
    #widets de los productos
    
        #widget de la etiqueta "productos"
    label_name_product = Label(right_frame, text='PRODUCTO', fg='black', bg='white', font='Helvetica 12 underline')
    label_name_product.place(relx=0.02, y=30)

        #widgets de las entradas para identificar el producto
    name_entry = Entry(right_frame,bg='white',fg='black')
    bar_code_entry = Entry(right_frame,bg='white',fg='black')

    name_entry.place(relx=0.02, y=60, width=180)
    bar_code_entry.place(relx=0.52, y=60, width=180)

        #widgets identificadores de las entradas
    label_name_entry = Label(right_frame, text='nombre', fg='#3498db', bg='white')
    label_bar_code_entry = Label(right_frame, text='código', fg='#3498db', bg='white')

    label_name_entry.place(relx=0.02, y=85)
    label_bar_code_entry.place(relx=0.52, y=85)

    #widget de las fechas

        #widget de la etiqueta "FECHA"
    label_name_date = Label(right_frame, text='FECHA', fg='black', bg='white', font='Helvetica 12 underline')
    label_name_date.place(relx=0.02, y=110)

        #widgets de las entradas para identificar la fecha
    calendar_init = DateEntry(right_frame, selectmode='day', year=dt.now().year, month=dt.now().month, day=dt.now().day, date_pattern='y-mm-dd')
    calendar_final = DateEntry(right_frame, selectmode='day', year=dt.now().year, month=dt.now().month, day=dt.now().day, date_pattern='y-mm-dd')
    
    calendar_init.place(relx=0.02, y=140, width=180)
    calendar_final.place(relx=0.52, y=140, width=180)

        #widgets identificadores de las entradas
    label_date_init_entry = Label(right_frame, text='inicio', fg='#3498db', bg='white')
    label_date_final_entry = Label(right_frame, text='final', fg='#3498db', bg='white')

    label_date_init_entry.place(relx=0.02, y=165)
    label_date_final_entry.place(relx=0.52, y=165)

    #widget boton de busqueda
    search_button = Button(right_frame, text='BUSCAR', bg='#3498db',fg='white', command=search_and_print)
    search_button.place(relx=0.7, y=185)

    #widgets para ordenar los resultados
    order_by_date = Radiobutton(right_frame, text='Por Fecha', value=' ORDER BY date;', bg='white', fg='black',
                                activebackground='white', activeforeground='black', variable=order_by)
    order_by_name = Radiobutton(right_frame, text='Por Nombre', value=' ORDER BY name;', bg='white', fg='black',
                                activebackground='white', activeforeground='black', variable=order_by)

    order_by_date.place(relx=0.02, y=195)
    order_by_name.place(relx=0.3, y=195)

    #widgets para mostrar los resultados

        #widget frame contenedor
    viewer_frame = Frame(right_frame, relief='ridge', bd=1, bg='white')
    viewer_frame.place(relx=0.02, y=225, relwidth=0.97, relheight=0.53)

        #widget del titulo 2
    label_title_2 = Label(viewer_frame, text='RESULTADO', bg='#3498db', fg='white')
    label_title_2.place(relx=0, y=0, relwidth=1, height=20)

        #widget caja-lista para mostrar los resultados
    list_result = Listbox(viewer_frame, bg='white', fg='black')

    list_result.place(relx=0.02, y=30, relwidth=0.5, relheight=0.84)
        
        #widget del boton para borrar
    delete_button = Button(viewer_frame, fg='white', bg='#3498db', text='BORRAR', command=delete_selection)
    delete_button.place(relx=0.77, y=214)

        #widget del boton para imprimir
    delete_button = Button(viewer_frame, fg='white', bg='#3498db', text='IMPRIMIR', command=print_result_to_archive)
    delete_button.place(relx=0.53, y=214)

#main_window()
    
#creacion de los frames generales
father_frame = Frame(app, bg='#f5f3e6')
right_frame = Frame(father_frame, bg='white', relief='ridge', bd=2)
left_frame = Frame(father_frame, relief='sunken', bd=2, bg='#f5f3e6')
bottom_frame = Frame(father_frame, bg='#f5f3e6')
top_frame = Frame(father_frame, bg='#f5f3e6')

# ubicacion y tamaño de los frames
father_frame.place(relwidth=1, relheight=1)
left_frame.place(x=11,y=31, relwidth=0.33, height=490)
right_frame.place(relx=0.35,y=31, relwidth=0.6, height=490)
bottom_frame.place(x=0,y=522, relwidth=1, height=28)
top_frame.place(x=0,y=0, relwidth=1, height=30)

#widgets del frame izquierdo
register_button = Button(left_frame, text='Registrar Productos', bg='#bbbbbb', command=build_register_form, fg='black')
modifier_button = Button(left_frame, text='Modificar Registros', bg='#bbbbbb', command=build_modifier_form, fg='black')
viewer_button = Button(left_frame, text='Ver Registros', bg='#bbbbbb', command=build_viewer_data, fg='black')
exit_button = Button(left_frame, text='Salir', command=app.destroy, bg='#bbbbbb', fg='black')

#ubiacion de los widgets dentro del frame izquierdo
register_button.place(relx=0.02, y=10, relwidth=0.95, height=50)
modifier_button.place(relx=0.02, y=60, relwidth=0.95, height=50)
viewer_button.place(relx=0.02, y=110, relwidth=0.95, height=50)
exit_button.place(relx=0.02, y=435, relwidth=0.95, height=50)

#widget del frame derecho

label_welcome = Label(right_frame, image=welcomeimage)

#ubicacion de los widgets dentro de frame derecho

label_welcome.place(relx=0, rely=0)

app.mainloop()