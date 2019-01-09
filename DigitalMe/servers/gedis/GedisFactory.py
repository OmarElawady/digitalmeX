import os

from Jumpscale import j

from .GedisServer import GedisServer
from .GedisCmds import GedisCmds
from .GedisChatBot import GedisChatBotFactory

JSConfigFactory = j.application.JSFactoryBaseClass


class GedisFactory(JSConfigFactory):
    __jslocation__ = "j.servers.gedis"
    _CHILDCLASS = GedisServer

    def geventserver_get(self, instance=""):
        """
        return redis_server

        j.servers.gedis.geventserver_get("test")


        """
        server = self.get(instance=instance)
        return server.redis_server

    def configure(self, name="test", port=8889,
                  host="localhost", ssl=False, password="", configureclient=False):

        data = {
            "port": str(port),
            "host": host,
            "password_": password,
            "ssl": ssl,
            "name": name
        }

        server = self.get(**data)
        if configureclient:
            server.client_configure()  # configures the client
        return server

    def _cmds_get(self, key, capnpbin):
        """
        Used in client only, starts from capnpbin (python client)
        """
        namespace, name = key.split("__")
        return GedisCmds(namespace=namespace, name=name, capnpbin=capnpbin)

    def test_server_start(self):
        """
        this method is only used when not used in digitalme
        js_shell 'j.servers.gedis.test_server_start()'

        """
        gedis = self.get(name="test")

        zdb_cl = j.clients.zdb.testdb_server_start_client_get(reset=False)
        bcdb = j.data.bcdb.new(zdbclient=zdb_cl, name="test")
        path = j.clients.git.getContentPathFromURLorPath(
            "https://github.com/threefoldtech/digital_me/tree/master/packages/examples/models")
        bcdb.models_add(path=path)

        path = j.clients.git.getContentPathFromURLorPath(
            "https://github.com/threefoldtech/digital_me/tree/master/packages/examples/actors")
        gedis.actors_add(namespace="gedis_examples", path=path)
        gedis.models_add(namespace="gedis_examples", models=bcdb)

        gedis.start()

    def test(self, zdb_start=True):
        """
        js_shell 'j.servers.gedis.test(zdb_start=False)'
        """
        # raise RuntimeError()
        if zdb_start:
            # remove configuration of the gedis factory
            # self.delete("test")
            cl = j.clients.zdb.test()

        gedis = self.configure(name="test", port=8888, host="localhost", ssl=False,
                               password="123456", interactive=False)

        print("START GEDIS IN TMUX")
        cmd = "js_shell 'j.servers.gedis.test_server_start()'"
        j.tools.tmux.execute(
            cmd,
            window='gedis_test',
            pane='main',
            reset=False,
        )

        res = j.sal.nettools.waitConnectionTest("localhost", int(gedis.port), timeoutTotal=1000)
        if res == False:
            raise RuntimeError("Could not start gedis server on port:%s" % int(gedis.port))
        self._logger.info("gedis server '%s' started" % gedis.name)
        print("[*] testing echo")

        cl = gedis.client_get(namespace="gedis_examples")
        assert cl.gedis_examples.echo("s") == b"s"
        print("- done")
        print("[*] testing set with schemas")
        # print("[1] schema_in as schema url")
        #
        # wallet_out1 = cl.gedis_examples.example1(addr="testaddr")
        # assert wallet_out1.addr == "testaddr"
        # print("[1] Done")
        print("[2] schema_in as inline schema with url")
        wallet_schema = j.data.schema.get("jumpscale.example.wallet")
        wallet_in = wallet_schema.new()
        wallet_in.addr = "testaddr"
        wallet_in.jwt = "testjwt"
        wallet_out = cl.gedis_examples.example2(wallet_in)

        assert wallet_in.addr == wallet_out.addr
        assert wallet_in.jwt == wallet_out.jwt
        print("[2] Done")

        print("[3] inline schema in and inline schema out")
        res = cl.gedis_examples.example3(a='a', b=True, c='2')
        assert res.a == 'a'
        assert res.b is True
        assert res.c == 2

        print("[3] Done")
        print("[4] inline schema for schema out with url")
        res = cl.gedis_examples.example4(wallet_in)
        assert res.result.addr == wallet_in.addr
        assert res.custom == "custom"
        print("[4] Done")

        s = j.clients.gedis.configure("system", port=cl.port, namespace="system", secret="123456")

        assert s.system.ping().lower() == b"pong"

        print("**DONE**")

        # j.shell()

    # def chatbot_test(self):
    #     """
    #     js_shell 'j.servers.gedis.chatbot_test()'
    #     """
    #     bot = GedisChatBotFactory()
    #     bot.test()
    #     #TODO:*1 not working

#     def new(
#             self,
#             instance="test",
#             port=8889,
#             host="localhost",
#             ssl=False,
#             password="",
# ]        ):
#         """
#         creates new server on path, if not specified will be current path
#         will start from example app
#
#         js_shell 'j.servers.gedis.new(path="{{DIRS.TMPDIR}}/jumpscale/gedisapp/",reset=True)'
#
#         """
#
#         if path == "":
#             path = j.sal.fs.getcwd()
#         else:
#             path = j.tools.jinja2.text_render(path)
#
#         if reset:
#             j.sal.fs.remove(path)
#
#         if j.sal.fs.exists("%s/actors" % path) or j.sal.fs.exists("%s/schema" % path):
#             raise RuntimeError("cannot do new app because app or schema dir does exist.")
#
#         # src = j.clients.git.getContentPathFromURLorPath(
#         #     "https://github.com/threefoldtech/jumpscale_lib/tree/development/apps/template")
#         # dest = path
#         # self._logger.info("copy templates to:%s" % dest)
#
#         gedis = self.configure(instance=instance, port=port, host=host, ssl=ssl, password=password)
#
#         # j.tools.jinja2.copy_dir_render(src, dest, reset=reset, j=j, name="aname", config=gedis.config.data,
#         #                                instance=instance)
#
#         self._logger.info("gedis app now in: '%s'\n    do:\n    cd %s;sh start.sh" % (dest, dest))
