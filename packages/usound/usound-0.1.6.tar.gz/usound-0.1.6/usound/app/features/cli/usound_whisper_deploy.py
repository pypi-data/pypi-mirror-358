from cmdbox.app import common, client, feature
from cmdbox.app.commons import redis_client
from cmdbox.app.options import Options
from faster_whisper import WhisperModel
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging
import json


class WhisperDeploy(feature.OneshotNotifyEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return "whisper"

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'deploy'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False,
            discription_ja="音声からテキスト抽出するモデルを配備します。",
            discription_en="Deploy a model to extract text from audio.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスホストを指定します。",
                     discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスポートを指定します。",
                     discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     discription_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     discription_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     discription_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     discription_ja="AIモデルの登録名を指定します。",
                     discription_en="Specify the registration name of the AI model."),
                dict(opt="model_size", type=Options.T_STR, default="small", required=False, multi=False, hide=False, choice=["tiny", "small", "base", "medium", "large-v1", "large-v2", "large-v3-turbo"],
                     discription_ja="モデルのサイズを指定します。",
                     discription_en="Specifies the size of the model."),
                dict(opt="device", type=Options.T_STR, default="cpu", required=False, multi=False, hide=False, choice=["auto", "cpu", "cuda"],
                     discription_ja="計算ディバイスを指定します。",
                     discription_en="Specifies the calculation device."),
                dict(opt="device_index", type=Options.T_INT, default=None, required=False, multi=False, hide=True, choice=None,
                     discription_ja="`device` でGPUが使用されるときのGPUIDを指定します。",
                     discription_en="Specifies the GPUID when the GPU is used in `device`."),
                dict(opt="compute_type", type=Options.T_STR, default="int8", required=False, multi=False, hide=False, choice=["default","auto","int8","int8_float16","int16","float16","float32"],
                     discription_ja="モデルの重みタイプを指定します。",
                     discription_en="Specifies the weight type of the model."),
                dict(opt="cpu_threads", type=Options.T_INT, default=0, required=False, multi=False, hide=True, choice=None,
                     discription_ja="CPU上で実行する際に使用するスレッドの数を指定します。",
                     discription_en="Specifies the number of threads to be used when executing on the CPU."),
                dict(opt="num_workers", type=Options.T_INT, default=1, required=False, multi=False, hide=True, choice=None,
                     discription_ja="テキスト抽出を行うワーカー数を指定します。",
                     discription_en="Specify the number of workers to perform text extraction."),
                dict(opt="overwrite", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="デプロイ済みであっても上書きする指定。",
                     discription_en="Specify to overwrite even if it is already deployed."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     discription_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     discription_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     discription_ja="Redisサーバーに再接続までの秒数を指定します。",
                     discription_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="1800", required=False, multi=False, hide=True, choice=None,
                     discription_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     discription_en="Specify the maximum waiting time until the server responds."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     discription_ja="処理結果jsonの保存先ファイルを指定。",
                     discription_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="処理結果jsonファイルを追記保存します。",
                     discription_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     discription_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ])

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'whisper_deploy'

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.name is None:
            msg = {"warn":f"Please specify the --name option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.model_size is None:
            msg = {"warn":f"Please specify the --model_size option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.device is None:
            msg = {"warn":f"Please specify the --device option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.device_index is not None and not isinstance(args.device_index, int):
            msg = {"warn":f"Please specify the --device_index option as an integer."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.compute_type is None:
            msg = {"warn":f"Please specify the --compute_type option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.cpu_threads is None:
            msg = {"warn":f"Please specify the --cpu_threads option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        elif not isinstance(args.cpu_threads, int) or args.cpu_threads < 0:
            msg = {"warn":f"Please specify the --cpu_threads option as a positive integer."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.num_workers is None:
            msg = {"warn":f"Please specify the --num_workers option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        elif not isinstance(args.num_workers, int) or args.num_workers < 1:
            msg = {"warn":f"Please specify the --num_workers option as a positive integer."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                    [args.name, args.model_size, args.device, str(args.device_index), args.compute_type,
                                     str(args.cpu_threads), str(args.num_workers), str(args.overwrite)],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)

        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return 1, ret, None
        return 0, ret, None

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return True

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        この機能のサーバー側の実行を行います

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            msg (List[str]): 受信メッセージ
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        
        Returns:
            int: 終了コード
        """
        msg = [None if m=="None" or m=="" else m for m in msg]

        reskey = msg[1]
        name = msg[2]
        if name is None:
            logger.warning(f"name is empty.")
            redis_cli.rpush(reskey, dict(warn=f"name is empty."))
            return self.RESP_WARN
        model_size = msg[3]
        if model_size is None:
            logger.warning(f"model_size is empty.")
            redis_cli.rpush(reskey, dict(warn=f"model_size is empty."))
            return self.RESP_WARN
        device = msg[4]
        if device is None:
            logger.warning(f"device is empty.")
            redis_cli.rpush(reskey, dict(warn=f"device is empty."))
            return self.RESP_WARN
        device_index = msg[5]
        if device_index is None:
            device_index = 0
        compute_type = msg[6]
        if compute_type is None:
            logger.warning(f"compute_type is empty.")
            redis_cli.rpush(reskey, dict(warn=f"compute_type is empty."))
            return self.RESP_WARN
        cpu_threads = msg[7]
        if cpu_threads is None:
            logger.warning(f"cpu_threads is empty.")
            redis_cli.rpush(reskey, dict(warn=f"cpu_threads is empty."))
            return self.RESP_WARN
        cpu_threads = int(cpu_threads)
        num_workers = msg[8]
        if num_workers is None:
            logger.warning(f"num_workers is empty.")
            redis_cli.rpush(reskey, dict(warn=f"num_workers is empty."))
            return self.RESP_WARN
        num_workers = int(num_workers)
        overwrite = msg[9].lower() == "true"

        deploy_dir = data_dir / name

        if name in sessions:
            logger.warning(f"{name} has already started a session.")
            redis_cli.rpush(reskey, dict(warn=f"{name} has already started a session."))
            return self.RESP_WARN
        if not overwrite and deploy_dir.exists():
            logger.warning(f"Could not be deployed. '{deploy_dir}' already exists")
            redis_cli.rpush(reskey, dict(warn=f"Could not be deployed. '{deploy_dir}' already exists"))
            return self.RESP_WARN

        common.mkdirs(deploy_dir)
        try:
            model_dir = common.mkdirs(deploy_dir / "model")
            WhisperModel(model_size, device=device, device_index=device_index, compute_type=compute_type,
                         cpu_threads=cpu_threads, num_workers=num_workers, download_root=model_dir)
            with open(deploy_dir / "conf.json", "w") as f:
                conf = dict(name=name, model_size=model_size, device=device, device_index=device_index, compute_type=compute_type,
                            cpu_threads=cpu_threads, num_workers=num_workers, model_dir=model_dir)
                json.dump(conf, f, default=common.default_json_enc, indent=4)
            logger.info(f"Save conf.json to {str(deploy_dir)}")
        except Exception as e:
            logger.warning(f"Failed deploy: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed deploy: {e}"))
            return self.RESP_WARN

        redis_cli.rpush(reskey, dict(success=f"Save conf.json to {str(deploy_dir)}"))
        return self.RESP_SCCESS
