#define PY_SSIZE_T_CLEAN
#include <Python.h>



static PyObject *method_mach(PyObject *self, PyObject *args) {
    char *str, *filename = NULL;
    int bytes_copied = -1;

    /* Parse arguments */
    if(!PyArg_ParseTuple(args, "ss", &str, &filename)) {
        return NULL;
    }

    FILE *fp = fopen(filename, "w");
    bytes_copied = fputs(str, fp);
    fclose(fp);

    return PyLong_FromLong(bytes_copied);
}


static PyMethodDef MachMethods[] = {
    {"mach", method_mach, METH_VARARGS, "Python interface for machines"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef machmodule = {
    PyModuleDef_HEAD_INIT,
    "mach",
    "Python interface for machines",
    -1,
    MachMethods
};


PyMODINIT_FUNC PyInit_mach(void) {
    return PyModule_Create(&machmodule);
}


////

/* static PyObject * */
/* spam_system(PyObject *self, PyObject *args) */
/* { */
/*     const char *command; */
/*     int sts; */

/*     if (!PyArg_ParseTuple(args, "s", &command)) */
/*         return NULL; */
/*     sts = system(command); */
/*     if (sts < 0) { */
/*         PyErr_SetString(SpamError, "System command failed"); */
/*         return NULL; */
/*     } */
/*     return PyLong_FromLong(sts); */
/* } */

/* static PyObject *SpamError; */

/* PyMODINIT_FUNC */
/* PyInit_spam(void) */
/* { */
/*     PyObject *m; */

/*     m = PyModule_Create(&spammodule); */
/*     if (m == NULL) */
/*         return NULL; */

/*     SpamError = PyErr_NewException("spam.error", NULL, NULL); */
/*     Py_XINCREF(SpamError); */
/*     if (PyModule_AddObject(m, "error", SpamError) < 0) { */
/*         Py_XDECREF(SpamError); */
/*         Py_CLEAR(SpamError); */
/*         Py_DECREF(m); */
/*         return NULL; */
/*     } */

/*     return m; */
/* } */
