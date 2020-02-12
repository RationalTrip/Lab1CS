import math
import os
import weakref

import base64_self

import libyaz0
import zlib
import zipfile
import lzma
import bz2
import lz4.frame



class EntropyInfo:
    def __init__(self, text):
        self.__text        = None
        self.__chance_dict = None
        self.__entropy     = None
        self.__inf_count   = None

        self._calculate_fields(text)

    @property
    def text(self):
        return self.__text

    @property
    def chance_dict(self):
        return self.__chance_dict

    @property
    def entropy(self):
        return self.__entropy

    @property
    def information_size(self):
        return self.__inf_count

    def change_text(self, new_text):
        self._calculate_fields(new_text)

    def _calculate_fields(self, text):
        self.__text = text
        self.__chance_dict = EntropyInfo.create_chance_symbol_dict(text)
        self.__entropy = EntropyInfo.get_entropy_from_dict(self.chance_dict)
        self.__inf_count = EntropyInfo.get_inf_count(self.__entropy, text)
    
    @staticmethod
    def create_chance_symbol_dict(text):
        res = {}
        for i in text:
            if i in res:
                res[i] += 1
            else:
                res[i] = 1
        text_len = len(text)
        for i in res:
            res[i] /= text_len
        return res

    @staticmethod
    def get_entropy_from_dict(char_dict):
        res = sum( -i * math.log2(i) for i in char_dict.values())
        return res

    @staticmethod
    def get_inf_count(entropy, text):
        return entropy * len(text)


class CompresionInf:
    def __init__(self, byte_to_compr):
        self.__bytes = byte_to_compr

        self.__gzip_inf    = None
        self.__lz4_inf     = None
        self.__lzma_inf    = None
        self.__bz2_inf     = None
        self.__libyaz0_inf  = None

        self._calc_all()

    def _calc_all(self):
        self.__gzip_inf = len(self.zlib_content)

        self.__lz4_inf = len(self.lz4_content)

        self.__lzma_inf = len(self.lzma_content)

        self.__bz2_inf = len(self.bz2_content)

        self.__libyaz0_inf = len(self.libyaz0_content)

    def get_enumerator(self):
        yield ("zlib", self.zlib_content, self.zlib_inf)
        yield ("lzma", self.lzma_content, self.lzma_inf)
        yield ("bz2", self.bz2_content, self.bz2_inf)
        yield ("yaz0", self.libyaz0_content, self.libyaz0_inf)
        yield ("lz4", self.lz4_content, self.lz4_inf)

    #region InfoProperties
    @property
    def zlib_inf(self):
        return self.__gzip_inf
    
    @property
    def lzma_inf(self):
        return self.__lzma_inf

    @property
    def bz2_inf(self):
        return self.__bz2_inf

    @property
    def libyaz0_inf(self):
        return self.__libyaz0_inf

    @property
    def lz4_inf(self):
        return self.__lz4_inf
    # endregion infoProperties
    
    #region ContentProperties
    @property
    def zlib_content(self):
        res = CompresionInf.get_comp_bytes(zlib, self.__bytes)
        self.__gzip_inf = len(res)
        return res
    
    @property
    def lzma_content(self):
        res = CompresionInf.get_comp_bytes(lzma, self.__bytes)
        self.__lzma_inf = len(res)
        return res

    @property
    def bz2_content(self):
        res = CompresionInf.get_comp_bytes(bz2, self.__bytes)
        self.__bz2_inf = len(res)
        return res

    @property
    def libyaz0_content(self):
        res = CompresionInf.get_comp_bytes(libyaz0, self.__bytes)
        self.__snappy_inf = len(res)
        return res

    @property
    def lz4_content(self):
        res = CompresionInf.get_comp_bytes(lz4.frame, self.__bytes)
        self.__lz4_inf = len(res)
        return res

    #endregion

    @staticmethod
    def get_comp_bytes(compresion, byt):
        byte = compresion.compress(byt)
        return byte

    @staticmethod
    def get_zip_len(byte):
        some_name = "sfjdpjjagoesojfd.zip"
        with zipfile.ZipFile(some_name, "wb") as zipf:
            zipf.write(byte)

        res = None
        with open(some_name, "wb") as f:
            res = f.read()
        os.remove(some_name)

        return res


def main_1(file_list, res_f_name = "result.txt"):
    if os.path.exists(res_f_name):
        os.remove(res_f_name)

    for f_name in file_list:
        text = None
        with open(f_name, encoding="utf-8") as file:
            text = file.read()
        
        with open(res_f_name, "ab") as res_file:
            res_file.write(f_name.encode("utf-8"))
            res_file.write("\n\n".encode("utf-8"))

            ent = EntropyInfo(text)
            for i in ent.chance_dict:
                key = i if i != '\n' else '\\n'
                res_file.write(f"char {key} = {ent.chance_dict[i]}\n".encode("utf-8"))
            res_file.write("\n\n".encode("utf-8"))
            
            res_file.write(f"Entropy = {ent.entropy}\n\n".encode("utf-8"))

            res_file.write(f"Information = {ent.information_size} bit or {ent.information_size / 8} byte\n\n".encode("utf-8"))

            res_file.write(f"Total len = {len(ent.text)}\n\n".encode("utf-8"))

            b64_full = base64_self.encode_to_base64(text.encode("utf-8"))

            ent = EntropyInfo(b64_full)
            
            res_file.write(f"Entropy b64 = {ent.entropy}\n\n".encode("utf-8"))

            res_file.write(f"Information b64 = {ent.information_size} bit or {ent.information_size / 8} byte\n\n".encode("utf-8"))

            res_file.write(f"Total len b64 = {len(ent.text)}\n\n".encode("utf-8"))


            compres = CompresionInf(text.encode("utf-8"))

            for com in compres.get_enumerator():
                res_file.write(f"Compress name {com[0]}: \n".encode("utf-8"))

                res_file.write(f"\tlen = {com[2]}\n".encode("utf-8"))

                b64 = base64_self.encode_to_base64(com[1])

                einf = EntropyInfo(b64)

                res_file.write(f"\tEntropy b64 = {einf.entropy}\n".encode("utf-8"))

                res_file.write(f"\tInformation b64 = {einf.information_size} bit or {einf.information_size / 8} byte\n".encode("utf-8"))

                res_file.write(f"\tTotal len = {len(einf.text)}\n\n".encode("utf-8"))



            #res_file.write(f"lz4 len = {compres.lz4_inf}\n\n".encode("utf-8"))
            #res_file.write(f"zlib len = {compres.zlib_inf}\n\n".encode("utf-8"))
            #res_file.write(f"lzma len = {compres.lzma_inf}\n\n".encode("utf-8"))
            #res_file.write(f"bz2 len = {compres.bz2_inf}\n\n".encode("utf-8"))
            #res_file.write(f"libyaz0 len = {compres.libyaz0_inf}\n\n".encode("utf-8"))


            
            res_file.write(("-".join("-" for i in range(40))).encode("utf-8"))
            res_file.write("\n\n".encode("utf-8"))



if __name__ == "__main__":
    filels = ["hymn.txt", "wiki.txt", "quest_ansv.txt"]
    main_1(filels)