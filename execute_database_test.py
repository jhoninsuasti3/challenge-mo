import sys
import psycopg2
from psycopg2 import sql
from os import getenv as env
from dotenv import load_dotenv

load_dotenv()
DB_NAME = str(env("DB_NAME", default=""))
DB_USER = str(env("DB_USER", default=""))
DB_PASS = str(env("DB_PASS", default=""))
DB_PORT = str(env("DB_PORT", default=""))
DB_HOST = str(env("DB_HOST", default=""))


def create_database(db_name):
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

        print(f"Base de datos '{db_name}' creada exitosamente.")
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def drop_database(db_name):
    try:
        DB_NAME = "postgres"
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))

        print(f"Base de datos '{db_name}' eliminada exitosamente.")
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()


def main():
    if len(sys.argv) != 3:
        print("Uso: python script.py <create|delete> <nombre_base_datos>")
        sys.exit(1)

    action = sys.argv[1]
    db_name = sys.argv[2]

    if action == "create":
        create_database(db_name)
    elif action == "delete":
        drop_database(db_name)
    else:
        print("Acción no válida. Use 'create' o 'delete'.")


if __name__ == "__main__":
    main()
