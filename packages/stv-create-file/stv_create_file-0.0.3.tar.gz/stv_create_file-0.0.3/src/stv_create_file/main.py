from stv_create_file.core.FileCreator import FileCreator

def main():
    try:
        fc = FileCreator()
        fc.run()
    except KeyboardInterrupt:
        print("\n^C", end='')