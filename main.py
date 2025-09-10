# main.py
from app.container import Container
from ui.app import App

def main():
    c = Container()
    app = App(container=c)   # App injeta popup em c.versions_uc, etc.
    app.mainloop()

if __name__ == "__main__":
    main()
