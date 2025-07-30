from cmdbox.app import common
from usound import version
from pathlib import Path
import getpass
import logging
import platform
import shutil
import yaml


class Install(object):
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        common.set_debug(self.logger, True)

    def server(self, data:Path, install_cmdbox_tgt:str='cmdbox', install_usound_tgt:str='usound',
               install_from:str=None, install_no_python:bool=False,
               install_tag:str=None, install_use_gpu:bool=False):
        """
        usoundが含まれるdockerイメージをインストールします。

        Args:
            data (Path): usound-serverのデータディレクトリ
            install_cmdbox_tgt (str): cmdboxのインストール元
            install_usound_tgt (str): usoundのインストール元
            install_from (str): インストール元dockerイメージ
            install_no_python (bool): pythonをインストールしない
            install_tag (str): インストールタグ
            install_use_gpu (bool): GPUを使用するモジュール構成でインストールします。

        Returns:
            dict: 処理結果
        """
        #if platform.system() == 'Windows':
        #    return {"warn": f"Build server command is Unsupported in windows platform."}
        from importlib.resources import read_text
        user = getpass.getuser()
        install_tag = f"_{install_tag}" if install_tag is not None else ''
        with open('Dockerfile', 'w', encoding='utf-8') as fp:
            text = read_text(f'usound.docker', 'Dockerfile')
            # cmdboxのインストール設定
            wheel_cmdbox = Path(install_cmdbox_tgt)
            if wheel_cmdbox.exists() and wheel_cmdbox.suffix == '.whl':
                shutil.copy(wheel_cmdbox, Path('.').resolve() / wheel_cmdbox.name)
                install_cmdbox_tgt = f'/home/{user}/{wheel_cmdbox.name}'
                text = text.replace('#{COPY_CMDBOX}', f'COPY {wheel_cmdbox.name} {install_cmdbox_tgt}')
            else:
                text = text.replace('#{COPY_CMDBOX}', '')
            # usoundのインストール設定
            wheel_usound = Path(install_usound_tgt)
            if wheel_usound.exists() and wheel_usound.suffix == '.whl':
                shutil.copy(wheel_usound, Path('.').resolve() / wheel_usound.name)
                install_usound_tgt = f'/home/{user}/{wheel_usound.name}'
                text = text.replace('#{COPY_USOUND}', f'COPY {wheel_usound.name} {install_usound_tgt}')
            else:
                text = text.replace('#{COPY_USOUND}', '')

            start_sh_src = Path(__file__).parent.parent / 'docker' / 'scripts'
            start_sh_tgt = f'scripts'
            shutil.copytree(start_sh_src, start_sh_tgt, dirs_exist_ok=True)
            text = text.replace('#{COPY_USOUND_START}', f'COPY {start_sh_tgt} {start_sh_tgt}')

            install_use_gpu_opt = '--install_use_gpu' if install_use_gpu else ''
            base_image = 'python:3.11.9-slim' #'python:3.8.18-slim'
            if install_use_gpu:
                base_image = 'nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04'
                # https://qiita.com/keisuke-okb/items/a531c7aaf91025de399d
                text = text.replace('#{INSTALL_CTRANSLATE2}', f'RUN pip install ctranslate2==3.24.0')
            if install_from is not None and install_from != '':
                base_image = install_from
                text = text.replace('#{INSTALL_CTRANSLATE2}', f'')
            text = text.replace('#{FROM}', f'FROM {base_image}')
            text = text.replace('${MKUSER}', user)
            #text = text.replace('#{INSTALL_PYTHON}', f'RUN apt-get update && apt-get install -y python3.8 python3.8-distutils python3-pip python-is-python3' if install_use_gpu else '')
            if not install_no_python:
                text = text.replace('#{INSTALL_PYTHON}', f'RUN apt-get update && apt-get install -y python3-all-dev python-is-python3 python3-pip python3-venv libopencv-dev')
            else:
                text = text.replace('#{INSTALL_PYTHON}', '')
            text = text.replace('#{INSTALL_TAG}', install_tag)
            text = text.replace('#{INSTALL_CMDBOX}', install_cmdbox_tgt)
            text = text.replace('#{INSTALL_USOUND}', install_usound_tgt)
            fp.write(text)
        docker_compose_path = Path('docker-compose.yml')
        if not docker_compose_path.exists():
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                text = read_text(f'usound.docker', 'docker-compose.yml')
                fp.write(text)
        with open(f'docker-compose.yml', 'r+', encoding='utf-8') as fp:
            comp = yaml.safe_load(fp)
            services = comp['services']
            common.mkdirs(data)
            services[f'usound_server{install_tag}'] = dict(
                image=f'hamacom/usound:{version.__version__}{install_tag}',
                container_name=f'usound_server{install_tag}',
                environment=dict(
                    TZ='Asia/Tokyo',
                    USOUND_DEBUG='false',
                    REDIS_HOST='${REDIS_HOST:-redis}',
                    REDIS_PORT='${REDIS_PORT:-6379}',
                    REDIS_PASSWORD='${REDIS_PASSWORD:-password}',
                    SVNAME='${SVNAME:-server'+install_tag+'}',
                    LISTEN_PORT='${LISTEN_PORT:-8081}',
                    SVCOUNT='${SVCOUNT:-2}',
                ),
                user=user,
                ports=['${LISTEN_PORT:-8081}:${LISTEN_PORT:-8081}'],
                privileged=True,
                restart='always',
                working_dir=f'/home/{user}',
                devices=['/dev/bus/usb:/dev/bus/usb'],
                volumes=[
                    f'{data}:/home/{user}/.usound',
                    f'/home/{user}/scripts:/home/{user}/scripts',
                    f'/home/{user}:/home/{user}'
                ]
            )
            if install_use_gpu:
                services[f'usound_server{install_tag}']['deploy'] = dict(
                    resources=dict(reservations=dict(devices=[dict(
                        driver='nvidia',
                        count=1,
                        capabilities=['gpu']
                    )]))
                )
            fp.seek(0)
            yaml.dump(comp, fp)
        cmd = f'docker build -t hamacom/usound:{version.__version__}{install_tag} -f Dockerfile .'

        if platform.system() == 'Linux':
            returncode, _, _cmd = common.cmd(f"{cmd}", self.logger, slise=-1)
            #os.remove('Dockerfile')
            if returncode != 0:
                self.logger.warning(f"Failed to install usound-server. cmd:{_cmd}")
                return {"error": f"Failed to install usound-server. cmd:{_cmd}"}
            return {"success": f"Success to install usound-server. and docker-compose.yml is copied. cmd:{_cmd}"}

        else:
            return {"warn":f"Unsupported platform."}
