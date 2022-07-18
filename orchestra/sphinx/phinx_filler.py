from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from settings import AppConfig


class SphinxFiller:
    __slots__ = ['conf', 'tpl_env']
    conf: AppConfig
    tpl_env: Environment

    def __init__(self, conf: AppConfig):
        self.conf = conf
        self.tpl_env = Environment(loader=FileSystemLoader('orchestra/templates'))

    def create_addrobj_index_conf(self, out_filename: str, local_temp: Path, sphinx_var_dir: str) -> None:
        conf_data = self.tpl_env.get_template('idx_addrobj.conf').render(
            db_host=self.conf.pg.host,
            db_port=self.conf.pg.port,
            db_user=self.conf.pg.user,
            db_password=self.conf.pg.password,
            db_name=self.conf.pg.name,
            sql_query=self.tpl_env.get_template('query_sphinx.sql').render().replace("\n", " \\\n"),
            index_name=self.conf.sphinx.index_addrobj,
            sphinx_var_path=sphinx_var_dir,
            min_length_to_star=self.conf.sphinx.min_length_to_star
        )

        with Path(local_temp, out_filename).open('w') as f:
            f.write(conf_data)
