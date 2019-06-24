from Jumpscale import j
from selenium import webdriver
from argparse import ArgumentParser


def install_prerequisites():
    j.builders.db.zdb.install()
    j.builders.apps.sonic.install()


def configure_open_publish(gedis_port, name="default"):
    open_publish_tool = j.tools.open_publish.get(name=name, port=gedis_port)
    open_publish_tool.save()


def add_wiikis_repo(gedis_client_name, gedis_port, wikis_name, docs_url, domain, ip):
    gedis_client = j.clients.gedis.get(name=gedis_client_name, port=gedis_port)
    gedis_client.actors.open_publish.publish_wiki(name=wikis_name, repo_url=docs_url, domain=domain, ip=ip)


def start_open_publish():
    j.tools.open_publish.start(background=True)


def gdrive_configuration(path):
    gdrive_client = j.clients.gdrive.main
    gdrive_client.credfile = path
    gdrive_client.save()


def driver():
    driver = webdriver.Firefox()
    return driver


def main(options):
    install_prerequisites()
    configure_open_publish(options.gedis_port, options.gedis_client_name)
    gdrive_configuration(options.credfile_path)
    start_open_publish()
    add_wiikis_repo(
        options.gedis_client_name, options.gedis_port, options.wikis_name, options.docs_url, options.domain, options.ip
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-gp", "--gedis_port", type=str, dest="gedis_port", required=True, help="port of gedis client")
    parser.add_argument(
        "-gn", "--gedis_name", type=str, dest="gedis_client_name", required=True, help="name of gedis clinet"
    )
    parser.add_argument(
        "-p", "--cred_path", type=str, dest="credfile_path", required=True, help="path for gdrive credential file"
    )
    parser.add_argument("-wn", "--wikis_name", type=str, dest="wikis_name", required=True, help="name of wikis")

    parser.add_argument("-dc", "--docs_url", type=str, dest="docs_url", required=True, help="docs repo url")

    parser.add_argument("-d", "--domain", type=str, dest="domain", required=True, help="domain of wikis")

    parser.add_argument("-ip", type=str, dest="ip", required=True, help="local ip")
    options = parser.parse_args()
    main(options)

