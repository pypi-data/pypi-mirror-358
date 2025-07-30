import unittest
from hashlib import md5
from tempfile import gettempdir


class Test(unittest.TestCase):
    def test_link(self):
        import string
        from os.path import join, split, exists
        from os import makedirs
        from shutil import rmtree

        tmp = join(gettempdir(), "dupln")

        data = dict(
            filter(
                (lambda _: isinstance(_[1], str)),
                ((k, getattr(string, k)) for k in dir(string) if k[0].isalpha()),
            )
        )

        # pprint.pprint(data)

        def test(sepins=[2, 5, 8]):
            exists(tmp) and rmtree(tmp)
            same_file = {}

            def put_bytes(b, path):
                h = md5()
                h.update(b)
                q = (len(b), h.hexdigest())
                if q in same_file:
                    same_file[q] += 1
                else:
                    same_file[q] = 1
                dir = split(path)[0]
                exists(dir) or makedirs(dir)
                with open(path, "wb") as o:
                    o.write(b)

            for k, v in data.items():
                b = v.encode("UTF-8")
                put_bytes(b[::-1], join(tmp, k))  # reversed
                for i in sepins:
                    if i < len(k):
                        k = k[:i] + "/" + k[i:]
                        put_bytes(b, join(tmp, k))

            return dict(
                same_file=sum(1 for count in same_file.values() if count > 1),
                uniques=len(same_file),
                disk_size=sum(size_hash[0] for size_hash in same_file.keys()),
                size=sum(
                    size_hash[0] * count for size_hash, count in same_file.items()
                ),
                files=sum(same_file.values()),
                same_size=len(set(size_hash[0] for size_hash in same_file.keys())),
                linked=sum(count - 1 for count in same_file.values() if count > 1),
            )

        v = test()

        from dupln.__main__ import App

        #######
        a = App()
        a.main(["stat", tmp])
        total = a._arg_final.total
        self.assertEqual(total.disk_size, v["size"])
        self.assertEqual(total.files, v["files"])
        self.assertEqual(total.inodes, v["files"])
        self.assertEqual(total.same_size, v["same_size"])
        self.assertEqual(total.size, v["size"])
        a = App()
        a.main(["uniques", tmp])
        total = a._arg_final.total
        self.assertRegex(a._arg_final.__class__.__name__.lower(), "unique")
        self.assertEqual(total.disk_size, v["size"], v)
        self.assertEqual(total.files, v["files"])
        self.assertEqual(total.inodes, v["files"])
        self.assertEqual(total.size, v["size"])
        self.assertEqual(total.unique_size, v["same_size"])
        #######
        a = App()
        a.main(["link", tmp])
        total = a._arg_final.total
        self.assertEqual(total.disk_size, v["disk_size"])
        self.assertEqual(total.files, v["files"])
        self.assertEqual(total.inodes, v["files"])
        self.assertEqual(total.linked, v["linked"])
        self.assertEqual(total.same_hash, v["same_file"])
        self.assertEqual(total.same_size, v["same_size"])
        self.assertEqual(total.size, v["size"])
        #######
        a = App()
        a.main(["stat", tmp])
        total = a._arg_final.total
        self.assertEqual(total.disk_size, v["disk_size"])
        self.assertEqual(total.files, v["files"])
        self.assertEqual(total.same_size, v["same_size"])
        self.assertEqual(total.inodes, v["uniques"])
        self.assertEqual(total.size, v["size"])
        a = App()
        a.main(["uniques", tmp])
        total = a._arg_final.total
        self.assertEqual(total.disk_size, v["disk_size"])
        self.assertEqual(total.files, v["files"])
        self.assertEqual(total.inodes, v["uniques"])
        self.assertEqual(total.size, v["size"])
        self.assertEqual(total.unique_size, v["same_size"])
