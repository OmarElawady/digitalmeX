from Jumpscale import j
from .ZOS import ZOS
from .ZOSContainer import ZOSContainer
JSBASE = j.application.JSBaseClass

class ZOSFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.tools.zos"
        JSBASE.__init__(self)
        self._logger_enable()

        self.code_location_source="/sandbox/code/github/threefoldtech"
        self.code_location_dest="/root/code/github/threefoldtech"
        self._list = []
        self._logger_enable()

    def build(self):
        """
        js_shell 'j.tools.zos.build()'
        :return:
        """
        path=j.clients.git.getContentPathFromURLorPath("git@github.com:threefoldtech/zos.git")
        script="""
        set -ex
        cd $PATH
        bash build.sh
        """
        args={"PATH":path}
        script = j.core.text.strip(script,args=args)
        j.sal.process.execute(script,profile=False)

    def _exec(self,cmd):
        cmd="cd /sandbox/var;zos %s" % cmd
        self._logger.debug(cmd)
        rc,out,err = j.sal.process.execute(cmd)
        return out


    def _cmd(self,cmd):
        cmd+=" --json"
        out= self._exec(cmd)
        data = j.data.serializers.json.loads(out)
        return data

    def cache_reset(self):
        """
        js_shell 'j.tools.zos.cache_reset()'
        :return:
        """
        for item in ["ZOS","ZOSContainer","ZOSFactory"]:
            for key in j.core.db.keys("cache:%s:*"%item):
                j.core.db.delete(key)

    @property
    def list(self):
        data = self.config
        data.pop("app")
        items = [item for item  in data.keys()]
        return items

    @property
    def config(self):
        def do():
            out = self._exec("showconfig")
            res={}
            for line in out.split("\n"):
                if line.strip()=="":
                    continue
                if line.startswith("["):
                    key = line.split("[",1)[1].split("]")[0]
                    if not key.startswith("container"):
                        res[key]={}
                    else:
                        key=""
                else:
                    if key != "":
                        key2,val2=line.split("=")
                        res[key][key2.strip()]=val2
            return res
        return self._cache.get("config", method=do, expire=300, refresh=False, retry=2, die=True)



    def zos_get(self,name=""):
        """
        get zos object, get the default one if not specified
        :param name:
        :return:
        """
        if name == "":
            name = self.list[0]
        return ZOS(name=name,data=self.config[name])

    def test(self):
        """
        js_shell 'j.tools.zos.test()'
        """

        print(self.list)
        zos = j.tools.zos.zos_get()
        print(zos.container_list_hr)

        c = zos.container_get()
        c.sync(monitor=True)

        # j.shell()