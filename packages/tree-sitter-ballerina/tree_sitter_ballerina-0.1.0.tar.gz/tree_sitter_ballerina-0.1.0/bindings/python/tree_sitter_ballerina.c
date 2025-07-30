#include <Python.h>

typedef struct TSLanguage TSLanguage;

TSLanguage *tree_sitter_ballerina(void);

static PyObject* language(PyObject *self, PyObject *args) {
    return PyLong_FromVoidPtr(tree_sitter_ballerina());
}

static PyMethodDef module_methods[] = {
    {
        .ml_name = "language",
        .ml_meth = language,
        .ml_flags = METH_NOARGS,
        .ml_doc = "Get the tree-sitter language for Ballerina"
    },
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module_definition = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_binding",
    .m_doc = "Tree-sitter language bindings for Ballerina",
    .m_size = -1,
    .m_methods = module_methods
};

PyMODINIT_FUNC PyInit__binding(void) {
    return PyModule_Create(&module_definition);
}