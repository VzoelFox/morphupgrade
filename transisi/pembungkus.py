# transisi/pembungkus.py

class PythonObject:
    """Wrapper untuk Python object arbitrary."""
    def __init__(self, py_object):
        self.obj = py_object

    def get_attribute(self, attr_name: str):
        try:
            return getattr(self.obj, attr_name)
        except AttributeError as e:
            raise e

    def __await__(self):
        # Mungkinkan `await` pada PythonObject jika objek yang dibungkusnya bisa di-await.
        # Ini akan mendelegasikan `await` ke `self.obj`.
        return self.obj.__await__()

    def __repr__(self):
        return f"<python object: {type(self.obj).__name__}>"
