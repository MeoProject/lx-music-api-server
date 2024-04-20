#include "des.cpp"
#include <pybind11/pybind11.h>

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

namespace py = pybind11;

// 修改 LyricDecode 函数，接受和返回字节数组
py::bytes LyricDecode(py::bytes input)
{
    // 获取输入字节数组的指针和长度
    const char *input_ptr = PyBytes_AsString(input.ptr());
    Py_ssize_t input_len = PyBytes_Size(input.ptr());

    // 复制输入数据以便修改
    std::vector<unsigned char> data(input_ptr, input_ptr + input_len);

    // 调用 LyricDecode 函数进行解密
    LyricDecode_(data.data(), data.size());

    // 创建输出字节数组
    py::bytes output(reinterpret_cast<const char *>(data.data()), data.size());

    return output;
}

PYBIND11_MODULE(qdes, m) {
    m.def("LyricDecode", &LyricDecode, "Decrypt a string");
}
