from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from faster_whisper import WhisperModel, tokenizer
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging
import io
import sys


class WhisperTranscribe(feature.ResultEdgeFeature):
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
        return 'transcribe'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False,
            discription_ja="配備済みモデルを使用してテキスト抽出を行います。",
            discription_en="Perform text extraction using the deployed model.",
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
                dict(opt="input_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="テキスト抽出する音声をファイルで指定します。",
                     discription_en="Specify the audio file from which to extract text."),
                dict(opt="input_format", type=Options.T_STR, default="capture", required=True, multi=False, hide=False,
                     choice=["capture", "aiff", "au", "flac", "mat", "ogg", "paf", "mp3", "raw", "sph", "svx", "wav", "voc"],
                     discription_ja="入力ファイルの形式を指定します。",
                     discription_en="Specifies the format of the input file."),
                dict(opt="stdin", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     discription_ja="テキスト抽出する音声を標準入力から読み込む。",
                     discription_en="Read the audio to be text extracted from the standard input."),
                dict(opt="task", type=Options.T_STR, default="transcribe", required=False, multi=False, hide=False, choice=['transcribe','translate'],
                     discription_ja="実行するタスクを指定します。",
                     discription_en="Specifies the task to be performed."),
                dict(opt="best_of", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     discription_ja="temperatureが0でないときにサンプリングする候補の数。",
                     discription_en="Number of candidates to sample when temperature is non-zero."),
                dict(opt="beam_size", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     discription_ja="ビームサーチのパラメータ。この数の探索を行い一番良い単語の繋ぎを選択する。",
                     discription_en="Parameters of the beam search. This number of searches is used to select the best word connection."),
                dict(opt="patience", type=Options.T_FLOAT, default=1.0, required=False, multi=False, hide=True, choice=None,
                     discription_ja="ビームサーチのパラメータ。忍耐度係数 1.0の場合最良の結果が見つかると探索を打ち切る。0.5の場合は50％で探索を打ち切る。",
                     discription_en="Parameters for beam search. A patience factor of 1.0 terminates the search when the best result is found; a patience factor of 0.5 terminates the search at 50 percent."),
                dict(opt="length_penalty", type=Options.T_FLOAT, default=1.0, required=False, multi=False, hide=True, choice=None,
                     discription_ja="ビームサーチのパラメータ。生成される系列の長さに罰則を設ける。1より小さいと長い系列が選好されやすくなる。",
                     discription_en="Parameters for beam search. Penalty on the length of the generated series; if less than 1, longer series are more likely to be preferred."),
                dict(opt="temperature", type=Options.T_FLOAT, default=0.2, required=False, multi=False, hide=True, choice=None,
                     discription_ja="信頼度。0に近いほど確実な選択を行い、0から離れると多様な選択肢を行う。",
                     discription_en="Confidence. the closer to 0, the more certain the choice, and the further away from 0, the more diverse the choices."),
                dict(opt="compression_ratio_threshold", type=Options.T_FLOAT, default=2.4, required=False, multi=False, hide=True, choice=None,
                     discription_ja="gzip 圧縮率がこの値より高い場合は、デコードした文字列が冗長であるため失敗として扱います。",
                     discription_en="If the gzip compression ratio is higher than this value, the decoded string is treated as a failure because it is redundant."),
                dict(opt="log_prob_threshold", type=Options.T_FLOAT, default=-1.0, required=False, multi=False, hide=True, choice=None,
                     discription_ja="平均ログ確率がこの値より低い場合は、デコードを失敗として扱います。",
                     discription_en="If the average log probability is lower than this value, the decoding is treated as a failure."),
                dict(opt="no_speech_threshold", type=Options.T_FLOAT, default=-1.0, required=False, multi=False, hide=True, choice=None,
                     discription_ja="トークンの確率がこの値よりも高く、'logprob_threshold' が原因でデコードが失敗した場合は、セグメントを無音と見なす。",
                     discription_en="If the token probability is higher than this value and decoding fails due to 'logprob_threshold', the segment is considered silent."),
                dict(opt="condition_on_previous_text", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="指定した場合、モデルの前の出力を次のウィンドウのプロンプトとして指定し一貫した出力を行う。",
                     discription_en="If specified, the previous output of the model is specified as the prompt for the next window for consistent output."),
                dict(opt="initial_prompt", type=Options.T_STR, default=None, required=False, multi=False, hide=True, choice=None,
                     discription_ja="モデルの初期のウィンドウのプロンプト。",
                     discription_en="The model's initial window prompts."),
                dict(opt="prefix", type=Options.T_STR, default=None, required=False, multi=False, hide=True, choice=None,
                     discription_ja="音声の初期のウィンドウのプレフィックスとして使用するテキスト。",
                     discription_en="Text to be used as the initial window prefix for the audio."),
                dict(opt="suppress_blank", type=Options.T_STR, default="True", required=False, multi=False, hide=True, choice=["True", "False"],
                     discription_ja="サンプリングの始まりの空白出力を抑制する。",
                     discription_en="Suppress blank output at the beginning of sampling."),
                dict(opt="without_timestamps", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="タイムスタンプを含むテキストを出力しない。",
                     discription_en="Do not output text containing timestamps."),
                dict(opt="max_initial_timestamp", type=Options.T_FLOAT, default=1.0, required=False, multi=False, hide=True, choice=None,
                     discription_ja="音声の初期タイムスタンプがこの値よりも遅くならないことを指定します。",
                     discription_en="Specifies that the initial timestamp of the audio will not be later than this value."),
                dict(opt="word_timestamps", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="各単語に対応するタイムスタンプを生成します。",
                     discription_en="Generate a timestamp for each word."),
                dict(opt="vad_filter", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="音声活動検出（VAD）を有効にして、音声のないオーディオの部分をフィルタリングする。",
                     discription_en="Enable Voice Activity Detection (VAD) to filter out unvoiced portions of audio."),
                dict(opt="output_lang", type=Options.T_STR, default="ja", required=False, multi=False, hide=False, choice=list(tokenizer._LANGUAGE_CODES),
                     discription_ja="出力する言語を指定します。",
                     discription_en="Specify the audio file from which to extract text."),
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
        return 'whisper_transcribe'

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
            msg = dict(warn=f"Please specify the --name option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.input_format is None:
            msg = dict(warn=f"Please specify the --input_format option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        try:
            b64str = None
            def capture_proc(f):
                for line in f:
                    line = line.decode('utf-8') if isinstance(line, bytes) else line
                    capture_data = line.strip().split(',')
                    if len(capture_data) < 5: continue
                    t = capture_data[0]
                    st = int(capture_data[1])
                    et = int(capture_data[2])
                    fn = Path(capture_data[3].strip())
                    b64str = capture_data[4]
                    ret = self.send_cmd(cl, args, t, b64str)
                    yield ret
            if args.input_file is not None:
                if not Path(args.input_file).exists():
                    self.logger.warning(f"Not found input_file. {args.input_file}.")
                    return dict(warn=f"Not found input_file. {args.input_file}.")
                if args.input_format != 'capture':
                    with open(args.input_file, "rb") as f:
                        b64str = convert.bytes2b64str(f.read())
                        ret = self.send_cmd(cl, args, args.input_format, b64str)
                else:
                    with open(args.input_file, "r", encoding='utf-8') as f:
                        last = None
                        for res in capture_proc(f):
                            if res is None: continue
                            last = res
                            msg = dict(success=res)
                            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        if last is None:
                            msg = dict(warn=f"capture file is no data.")
                            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                            return 1, msg, cl
                        return 0, "", cl
            elif args.stdin:
                if args.input_format != 'capture':
                    b64str = convert.bytes2b64str(sys.stdin.buffer.read())
                    ret = self.send_cmd(cl, args, args.input_format, b64str)
                    msg = dict(success=ret)
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return 0, msg, cl
                else:
                    last = None
                    for res in capture_proc(sys.stdin):
                        if res is None: continue
                        last = res
                        msg = dict(success=res)
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    if last is None:
                        msg = dict(warn=f"capture file is no data.")
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return 1, msg, cl
                    return 0, "", cl
            else:
                msg = dict(warn=f"Please specify the --input_file option or --stdin option.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return 1, msg, None
        except Exception as e:
            msg = dict(warn=f"warning: {e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None

    def send_cmd(self, cl:client.Client, args:argparse.Namespace, ftype:str, b64str:str) -> Dict[str, Any]:

        ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                    [args.name, ftype, b64str, args.task, str(args.best_of), str(args.beam_size), str(args.patience),
                                     str(args.length_penalty), str(args.temperature), str(args.compression_ratio_threshold), str(args.log_prob_threshold),
                                     str(args.no_speech_threshold), str(args.condition_on_previous_text), args.initial_prompt, args.prefix,
                                     str(args.suppress_blank), str(args.without_timestamps), str(args.max_initial_timestamp), str(args.word_timestamps),
                                     str(args.vad_filter), args.output_lang],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)

        return ret

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

    def is_float(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

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
        if name not in sessions:
            logger.warning(f"{name} has not yet started a session.")
            redis_cli.rpush(reskey, dict(warn=f"{name} has not yet started a session."))
            return self.RESP_WARN
        ftype = msg[3]
        if ftype is None:
            logger.warning(f"ftype is empty.")
            redis_cli.rpush(reskey, dict(warn=f"ftype is empty."))
            return self.RESP_WARN
        b64str = msg[4]
        if b64str is None:
            logger.warning(f"input_file is empty.")
            redis_cli.rpush(reskey, dict(warn=f"input_file is empty."))
            return self.RESP_WARN
        task = msg[5]
        if task is None:
            logger.warning(f"task is empty.")
            redis_cli.rpush(reskey, dict(warn=f"task is empty."))
            return self.RESP_WARN
        best_of = msg[6]
        if best_of is None or not best_of.isdigit():
            logger.warning(f"best_of is empty or not digit.")
            redis_cli.rpush(reskey, dict(warn=f"best_of is empty or not digit."))
            return self.RESP_WARN
        best_of = int(best_of)
        beam_size = msg[7]
        if beam_size is None or not beam_size.isnumeric():
            logger.warning(f"beam_size is empty or not digit.")
            redis_cli.rpush(reskey, dict(warn=f"beam_size is empty or not digit."))
            return self.RESP_WARN
        beam_size = int(beam_size)
        patience = msg[8]
        if patience is None or not self.is_float(patience):
            logger.warning(f"patience is empty or not float.")
            redis_cli.rpush(reskey, dict(warn=f"patience is empty or not float."))
            return self.RESP_WARN
        patience = float(patience)
        length_penalty = msg[9]
        if length_penalty is None or not self.is_float(length_penalty):
            logger.warning(f"length_penalty is empty or not float.")
            redis_cli.rpush(reskey, dict(warn=f"length_penalty is empty or not float."))
            return self.RESP_WARN
        length_penalty = float(length_penalty)
        temperature = msg[10]
        if temperature is None or not self.is_float(temperature):
            logger.warning(f"temperature is empty or not float.")
            redis_cli.rpush(reskey, dict(warn=f"temperature is empty or not float."))
            return self.RESP_WARN
        temperature = float(temperature)
        compression_ratio_threshold = msg[11]
        if compression_ratio_threshold is None or not self.is_float(compression_ratio_threshold):
            logger.warning(f"compression_ratio_threshold is empty or not float.")
            redis_cli.rpush(reskey, dict(warn=f"compression_ratio_threshold is empty or not float."))
            return self.RESP_WARN
        compression_ratio_threshold = float(compression_ratio_threshold)
        log_prob_threshold = msg[12]
        if log_prob_threshold is None or not self.is_float(log_prob_threshold):
            logger.warning(f"log_prob_threshold is empty or not float.")
            redis_cli.rpush(reskey, dict(warn=f"log_prob_threshold is empty or not float."))
            return self.RESP_WARN
        log_prob_threshold = float(log_prob_threshold)
        no_speech_threshold = msg[13]
        if no_speech_threshold is None or not self.is_float(no_speech_threshold):
            logger.warning(f"no_speech_threshold is empty or not float.")
            redis_cli.rpush(reskey, dict(warn=f"no_speech_threshold is empty or not float."))
            return self.RESP_WARN
        no_speech_threshold = float(no_speech_threshold)
        condition_on_previous_text = True if msg[14]=="True" else False
        initial_prompt = msg[15]
        prefix = msg[16]
        suppress_blank = True if msg[17]=="True" else False
        without_timestamps = True if msg[18]=="True" else False
        max_initial_timestamp = msg[19]
        if max_initial_timestamp is None or not self.is_float(max_initial_timestamp):
            logger.warning(f"max_initial_timestamp is empty or not float.")
            redis_cli.rpush(reskey, dict(warn=f"max_initial_timestamp is empty or not float."))
            return self.RESP_WARN
        max_initial_timestamp = float(max_initial_timestamp)
        word_timestamps = True if msg[20]=="True" else False
        vad_filter = True if msg[21]=="True" else False
        output_lang = msg[22]
        try:
            model:WhisperModel = sessions[name].get('session', None)
            if model is None:
                logger.warning(f"Model is not found.")
                redis_cli.rpush(reskey, dict(warn=f"Model is not found."))
                return self.RESP_WARN
            data = convert.b64str2bytes(b64str)
            segments, info = model.transcribe(io.BytesIO(data),
                                              language=output_lang,
                                              task=task,
                                              best_of=best_of,
                                              beam_size=beam_size,
                                              patience=patience,
                                              length_penalty=length_penalty,
                                              temperature=temperature,
                                              compression_ratio_threshold=compression_ratio_threshold,
                                              log_prob_threshold=log_prob_threshold,
                                              no_speech_threshold=no_speech_threshold,
                                              condition_on_previous_text=condition_on_previous_text,
                                              initial_prompt=initial_prompt,
                                              prefix=prefix,
                                              suppress_blank=suppress_blank,
                                              without_timestamps=without_timestamps,
                                              max_initial_timestamp=max_initial_timestamp,
                                              word_timestamps=word_timestamps,
                                              vad_filter=vad_filter,
                                              vad_parameters=dict(
                                                threshold=0.5,
                                                min_speech_duration_ms=250,
                                                max_speech_duration_s=float("inf"),
                                                min_silence_duration_ms=2000,
                                                window_size_samples=1024,
                                                speech_pad_ms=400))
            rows = []
            for segment in segments:
                rows.append(dict(text=segment.text, start=round(segment.start, 1), end=round(segment.end, 1)))
            msg = dict(success=dict(rows=rows))
            redis_cli.rpush(reskey, msg)
            return self.RESP_SCCESS
        except Exception as e:
            logger.warning(f"Failed transcribe of {name} session.: {e}", exc_info=True)
            redis_cli.rpush(reskey, {"warn": f"Failed transcribe of {name} session.: {e}"})
            return self.RESP_WARN
