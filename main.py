from argparse import ArgumentParser
import os
from tsvloader import DEFAULT_SRC
from tsvloader import ConfigLoader


def get_attr(obj, attr):
    if hasattr(obj, attr):
        return getattr(obj, attr)
    return None


class MainExecutor:
    @staticmethod
    def list(loader: ConfigLoader, args):
        keyword: str = get_attr(args, "keyword")
        loader.print(keyword=keyword)

    @staticmethod
    def make(loader: ConfigLoader, args):
        loader.make(write=True)

    @staticmethod
    def open(loader: ConfigLoader, args):
        loader.open_in_editor(target=args.target)

    @staticmethod
    def add(loader: ConfigLoader, args):
        loader.add_item_interactive()
        loader.make(write=True)

    @staticmethod
    def remove(loader: ConfigLoader, args):
        if loader.remove_item(key=args.key):
            loader.make(write=True)

    @staticmethod
    def update(loader: ConfigLoader, args):
        if loader.update(key=args.key, col=args.col, val=args.val):
            loader.make(write=True)

    @staticmethod
    def clean(loader: ConfigLoader, args):
        loader.clean_all_backups()

    @staticmethod
    def update_password(loader: ConfigLoader, args):
        loader.update_password(args.new_password, args.password)


from password import PasswordManager


def update_password(args):
    pm = PasswordManager(srctsv=args.filepath)
    pm.set_password(args.new_password, args.old_password)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filepath", default=DEFAULT_SRC, help=f"default: {DEFAULT_SRC}")
    parser.add_argument("-p", "--password", dest="password_0")
    subparsers = parser.add_subparsers()

    subparser = subparsers.add_parser("ps", aliases=("ls", "list"), help="打印所有主机信息")
    subparser.add_argument("-p", "--password")
    subparser.set_defaults(func=MainExecutor.list)

    subparser = subparsers.add_parser("get", help="在主机键名和主机名称中搜索")
    subparser.add_argument("keyword", help="搜索关键字")
    subparser.add_argument("-p", "--password")
    subparser.set_defaults(func=MainExecutor.list)

    subparser = subparsers.add_parser("make", help="制作 ~/.ssh/config 文件")
    # subparser.add_argument("-w", "--write", action="store_true", help="写入到文件")
    subparser.add_argument("-p", "--password")
    subparser.set_defaults(func=MainExecutor.make)

    subparser = subparsers.add_parser("open", help="在默认文本编辑器中打开文件")
    subparser.add_argument("-t", "--target", choices=("default", "config"), default="default", help="要打开的文件")
    subparser.set_defaults(func=MainExecutor.open)

    subparser = subparsers.add_parser("add", aliases=("create", "new"), help="添加一个主机")
    subparser.add_argument("-p", "--password")
    subparser.set_defaults(func=MainExecutor.add)

    subparser = subparsers.add_parser("remove", aliases=("rm", "delete", "destroy"), help="删除一个主机")
    subparser.add_argument("key", help="要删除的主机键名")
    subparser.add_argument("-p", "--password")
    subparser.set_defaults(func=MainExecutor.remove)

    subparser = subparsers.add_parser("update", help="更新主机信息")
    subparser.add_argument("key", help="要更新的主机")
    subparser.add_argument("col", help="要更新的列")
    subparser.add_argument("val", help="要更新的值")
    subparser.add_argument("-p", "--password")
    subparser.set_defaults(func=MainExecutor.update)

    subparser = subparsers.add_parser("clean", help="清除所有备份文件")
    subparser.set_defaults(func=MainExecutor.clean)

    subparser = subparsers.add_parser("password", aliases=("passwd",))
    subparser.add_argument("new_password")
    subparser.add_argument("-p", "--password")
    subparser.set_defaults(func=MainExecutor.update_password)

    args = parser.parse_args()
    args.password = args.password or args.password_0 or os.environ.get("SSHCONFIG_PASSWORD")

    if hasattr(args, "func"):
        loader = ConfigLoader(args.filepath, password=args.password)
        args.func(loader, args)
    else:
        parser.print_help()
