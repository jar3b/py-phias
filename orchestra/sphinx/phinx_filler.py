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

    def __get_addrobj_conf_body(self, sphinx_var_dir: str) -> str:
        return self.tpl_env.get_template('idx_addrobj.conf').render(
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

    def __get_suggest_conf_body(self, sphinx_var_dir: str) -> str:
        return self.tpl_env.get_template('idx_suggest.conf').render(
            db_host=self.conf.pg.host,
            db_port=self.conf.pg.port,
            db_user=self.conf.pg.user,
            db_password=self.conf.pg.password,
            db_name=self.conf.pg.name,
            index_name=self.conf.sphinx.index_sugg,
            sphinx_var_path=sphinx_var_dir,
        )

    def create_addrobj_index_conf(self, out_filename: str, local_temp: Path, sphinx_var_dir: str) -> None:
        with Path(local_temp, out_filename).open('w') as f:
            f.write(self.__get_addrobj_conf_body(sphinx_var_dir))

    def create_sphinx_conf(self, out_filename: Path, sphinx_var_dir: str) -> None:
        main_conf = self.tpl_env.get_template('sphinx.conf').render(
            sphinx_listen=self.conf.sphinx.listen_port(),
            sphinx_var_path=sphinx_var_dir,
        )
        idx_addrobj = self.__get_addrobj_conf_body(sphinx_var_dir)
        idx_suggest = self.__get_suggest_conf_body(sphinx_var_dir)

        with out_filename.open('w') as sphinx_conf:
            sphinx_conf.write(main_conf)
            sphinx_conf.write('\n\n')
            sphinx_conf.write(idx_addrobj)
            sphinx_conf.write('\n\n')
            sphinx_conf.write(idx_suggest)
            sphinx_conf.write('\n')

        #out_filename.chmod(0x777)
