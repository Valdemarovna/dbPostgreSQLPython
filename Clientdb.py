import psycopg2

# 1 СОЗДАНИЕ БАЗЫ ДАННЫХ
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS client (
                    client_id SERIAL PRIMARY KEY, 
                    first_name VARCHAR (40) NOT NULL,
                    last_name VARCHAR (40) NOT NULL,
                    email VARCHAR (60) NOT NULL);
                     """)
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS phone(
                    client_id INTEGER NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,
                    phone_number INTEGER NOT NULL);
                    """)
        conn.commit()

# 2 ДОБАВЛЕНИЕ КЛИЕНТА
def add_client(conn, first_name, last_name, email, phone_number=None):
    with (conn.cursor() as cur):
        cur.execute("""
                    INSERT INTO client (first_name, last_name, email) 
                    VALUES (%s, %s, %s) RETURNING client_id;
                    """, (first_name, last_name, email))
        new_client_id = cur.fetchone()[0]

        if phone_number:
            cur.execute("""
                        INSERT INTO phone (client_id, phone_number) 
                        VALUES (%s, %s);
                        """, (new_client_id, phone_number))
        conn.commit()

# 3 ДОБАВЛЕНИЕ НОМЕРА ТЕЛЕФОНА
def add_phone(conn, client_id, phone):
    with (conn.cursor() as cur):
        cur.execute("""
                    INSERT INTO phone (client_id, phone_number) 
                    VALUES (%s, %s);""", (client_id, phone))
        conn.commit()

# 4 ИЗМЕНЕНИЕ ДАННЫХ КЛИЕНТА
def change_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None):
    with (conn.cursor() as cur):
        if first_name and first_name != '':
            cur.execute("""
                        UPDATE client SET first_name=%s WHERE client_id=%s;
                        """, (first_name, client_id))
        if last_name and last_name != '':
            cur.execute("""
                        UPDATE client SET last_name=%s WHERE client_id=%s;
                        """, (last_name, client_id))
        if email and email != '':
            cur.execute("""
                        UPDATE client SET email=%s WHERE client_id=%s;
                        """, (email, client_id))
        if phone and phone != '':
            change_client_phone(client_id)
    conn.commit()
def change_client_phone (conn, client_id):
    with (conn.cursor() as cur):
        cur.execute("""
                    SELECT phone_number FROM phone WHERE client_id=%s;
                    """, (client_id,))
        for i in cur.fetchall():
            print(i[0])
        old_number = input(f'Введите номер телефона, который вы хотите изменить:\n')
        new_number = input(f'Введите новый номер телефона:\n')
        cur.execute("""
                    UPDATE phone SET phone_number=%s WHERE client_id=%s AND phone_number=%s;
                    """, (new_number, client_id, old_number))
    conn.commit()

# 5 УДАЛЕНИЕ ТЕЛЕФОНА
def delete_phone(conn, client_id):
    with (conn.cursor() as cur):
        cur.execute("""
                    SELECT phone_number FROM phone WHERE client_id=%s;
                    """, (client_id,))
        for i in cur.fetchall():
            print(i[0])
        old_number = input(f'Введите номер телефона, который вы хотите удалить:\n')
        cur.execute("""
                    DELETE FROM phone WHERE client_id=%s AND phone_number=%s;
                    """, (client_id, old_number))
    conn.commit()

# 6 УДАЛЕНИЕ КЛИЕНТА
def delete_client(conn, client_id):
    with (conn.cursor() as cur):
        cur.execute("""
                    DELETE FROM client WHERE client_id=%s;
                    """, (client_id))
    conn.commit()

# 7 НАЙТИ КЛИЕНТА
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with (conn.cursor() as cur):
        if first_name and first_name != '':
            cur.execute("""SELECT client_id, first_name, last_name, email, phone_number
                        FROM client
                        JOIN phone USING (client_id)
                        WHERE first_name=%s;
                        """, (first_name,))
            for i in cur.fetchall():
                print(i)
        if last_name and last_name != '':
            cur.execute("""SELECT client_id, first_name, last_name, email, phone_number
                        FROM client
                        JOIN phone USING (client_id)
                        WHERE last_name=%s;
                        """, (last_name,))
            for i in cur.fetchall():
                print(i)
        if email and email != '':
            cur.execute("""SELECT client_id, first_name, last_name, email, phone_number
                        FROM client
                        JOIN phone USING (client_id)
                        WHERE email=%s;
                        """, (email,))
            for i in cur.fetchall():
                print(i)
        if phone and phone != '':
            cur.execute("""SELECT client_id, first_name, last_name, email, phone_number
                        FROM client
                        JOIN phone USING (client_id)
                        WHERE phone=%s;
                        """, (phone,))
            for i in cur.fetchall():
                print(i)
    conn.commit()

# ВЫЗОВ ФУНКЦИЙ
with psycopg2.connect(database="client", user="postgres", password="postgres") as conn:
    try:
        what_next = int(input(f'Укажите необходимое действие:\n'
                              f'1. Создать базу клентов\n'
                              f'2. Добавить нового клиента\n'
                              f'3. Добавить телефон для клиента\n'
                              f'4. Изменить данные о клиенте\n'
                              f'5. Удалить телефон клиента\n'
                              f'6. Удалить клиента\n'
                              f'7. Найти клиента по его данным\n'))
    except:
        print ('Введен не корректный идентификатор.')
        exit(1)

    if what_next == 1:
        create_db(conn)
        print('\nБаза данных создана')

    elif what_next == 2:
        first_name = input(f'Введите имя клиента:\n')
        last_name = input(f'Введите фамилию клиента:\n')
        email = input(f'Введите email клиента:\n')
        try:
            phone_number = int(input(f'Введите номер телефона клиента, только цифры (не обязательно)\n'))
            add_client(conn, first_name, last_name, email, phone_number)
            print('\nНовый клиент добавлен')
        except:
            print('Номер телефона не введен ;)')
            add_client(conn, first_name, last_name, email)

    elif what_next == 3:
        client_id = input(f'Введите ID клиента:\n')
        try:
            phone_number = int(input(f'Введите номер телефона клиента, только цифры:\n'))
            add_phone(conn, client_id, phone_number)
            print('\nТелефон добавлен в базу')
        except:
            print('Введен некорректный номер телефона или ID пользователя')
            exit(1)

    elif what_next == 4:
        xxxx = input(f'Введите ID клиента:\n')
        try:
            change_information = int(input(f'Укажите какие данные вы хотите изменить:\n'
                                       f'1. Имя клиента\n'
                                       f'2. Фамилию клиента\n'
                                       f'3. Email клиента\n'
                                       f'4. Телефон клиента\n'))
        except:
            print('Введен не корректный идентификатор')
            exit(1)
        if change_information == 1:
            new_name = input(f'Введите новое имя клиента:\n')
            change_client(conn, xxxx, new_name)
            print('\nИмя клиента обнавлено')
        elif change_information == 2:
            new_info = input(f'Введите новую фамилию клиента:\n')
            change_client(conn, xxxx, last_name=new_info)
            print('\nФамилия клиента обнавлена')
        elif change_information == 3:
            new_info = input(f'Введите новый email клиента:\n')
            change_client(conn, xxxx, email=new_info)
            print('\nEmail клиента обнавлен')
        elif change_information == 4:
            change_client_phone(conn, xxxx)
            print('\nТелефон клиента обнавлен')

    elif what_next == 5:
        xxxx = input(f'Введите ID клиента:\n')
        delete_phone(conn, xxxx)
        print('\nТелефон клиента удален')

    elif what_next == 6:
        xxxx = input(f'Введите ID клиента:\n')
        delete_client(conn, xxxx)
        print('\nДанные клиента удалены')

    elif what_next == 7:
        try:
            find_information = int(input(f'Укажите по каким данным вы хотите искать клиента:\n'
                                       f'1. Имя\n'
                                       f'2. Фамилия\n'
                                       f'3. Email\n'
                                       f'4. Телефон\n'))
        except:
            print('Введен не корректный идентификатор')
            exit(1)
        if find_information == 1:
            find_info = input(f'Введите имя клиента:\n')
            find_client(conn, first_name=find_info)
        elif find_information == 2:
            find_info = input(f'Введите фамилию клиента:\n')
            find_client(conn, last_name=find_info)
        elif find_information == 3:
            find_info = input(f'Введите email клиента:\n')
            find_client(conn, email=find_info)
        elif find_information == 4:
            find_info = input(f'Введите телефон клиента:\n')
            find_client(conn, phone=find_info)

conn.close()
