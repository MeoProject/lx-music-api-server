#include "des.cpp"
#include <Python.h>
#define PY_SSIZE_T_CLEAN
unsigned char KEY1[] = "!@#)(NHLiuy*$%^&";
unsigned char KEY2[] = "123ZXC!@#)(*$%^&";
unsigned char KEY3[] = "!@#)(*$%^&abcDEF";

int func_des(unsigned char *buff, unsigned char *key, int len)
{
  BYTE schedule[16][6];
  des_key_setup(key, schedule, DES_ENCRYPT);
  for (int i = 0; i < len; i += 8)
    des_crypt(buff + i, buff + i, schedule);
  return 0;
}

int func_ddes(unsigned char *buff, unsigned char *key, int len)
{
  BYTE schedule[16][6];
  des_key_setup(key, schedule, DES_DECRYPT);
  for (int i = 0; i < len; i += 8)
    des_crypt(buff + i, buff + i, schedule);
  return 0;
}

void LyricDecode_(unsigned char *content, int len)
{
  func_ddes(content, KEY1, len);
  func_des(content, KEY2, len);
  func_ddes(content, KEY3, len);
}

static PyObject* lyric_decode(PyObject* self, PyObject* args) {
    const char* content;
    int len;

    // Parse arguments
    if (!PyArg_ParseTuple(args, "s#", &content, &len)) {
        return NULL;
    }

    // Call the C function
    LyricDecode_((unsigned char*)content, len);

    // Return the result as bytes
    return Py_BuildValue("y#", content, len);
}

// Method table
static PyMethodDef module_methods[] = {
    {"LyricDecode", lyric_decode, METH_VARARGS, "QRC Decrypt."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

// Module initialization function
static struct PyModuleDef lyric_decoder_module = {
    PyModuleDef_HEAD_INIT,
    "qdes",
    NULL,
    -1,
    module_methods
};

// Module initialization
PyMODINIT_FUNC PyInit_qdes(void) {
    return PyModule_Create(&lyric_decoder_module);
}
