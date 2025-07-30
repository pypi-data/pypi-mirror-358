from cmdbox.app import common, edge, edge_tool, feature
from cmdbox.app.commons import convert
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import datetime
import logging
import io
import soundfile
import time
import threading


class SpeakerCapture(feature.Feature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return "speaker"

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'capture'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            discription_ja="指定したスピーカーから出力される音声を録音します。",
            discription_en="Record audio output from the specified speaker.",
            choice=[
                dict(opt="spid", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="録音するスピーカーをIDで指定します。指定しなかった場合最初に見つかったスピーカーを使用します。",
                     discription_en="Specify the speaker to record by ID. If not specified, the first speaker found will be used."),
                dict(opt="spname", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="録音するスピーカーを名前で指定します。指定しなかった場合最初に見つかったスピーカーを使用します。",
                     discription_en="Specify the speaker to be recorded by name. If not specified, the first speaker found will be used."),
                dict(opt="samplerate", type=Options.T_INT, default=48000, required=False, multi=False, hide=False, choice=[48000, 44100, 22050, 16000, 11025, 8000],
                     discription_ja="サンプリングレートを指定します。",
                     discription_en="Specifies the sampling rate."),
                dict(opt="duration", type=Options.T_FLOAT, default=10.0, required=False, multi=False, hide=False, choice=None,
                     discription_ja="録音時のバッファリングする最大秒数を指定します。この時間内でチャンキングされます。",
                     discription_en="Specifies the maximum number of seconds to buffer during recording. It will be chunked within this time."),
                dict(opt="rectime", type=Options.T_FLOAT, default=30.0, required=False, multi=False, hide=False, choice=None,
                     discription_ja="録音時間を指定します。0以下の場合はコマンドが停止されるまで続けます。",
                     discription_en="Specifies the recording time; if it is less than or equal to 0, it continues until the command is stopped."),
                dict(opt="output_dir", type=Options.T_DIR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="録音ファイルを保存するディレクトリを指定します。",
                     discription_en="Specifies the directory where the recording files are stored."),
                dict(opt="output_csv", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="録音ファイルをcsvファイルとして保存します。指定した場合、標準出力は行いません。",
                     discription_en="Saves the recording file as a csv file. If specified, no standard output is performed."),
                dict(opt="output_format", type=Options.T_STR, default="wav", required=False, multi=False, hide=False,
                     choice=["aiff", "au", "flac", "mat", "ogg", "paf", "mp3", "raw", "sph", "svx", "wav", "voc"],
                     discription_ja="音声ファイルのフォーマットを指定します。",
                     discription_en="Specifies the format of the audio file."),
            ])

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
        import soundcard
        output_dir = None
        output_format = args.output_format
        spname = None
        if args.spid is None and args.spname is None:
            sl = soundcard.all_speakers()
            if len(sl) == 0:
                raise ValueError("No speakers.")
            spname = sl[0].name
        elif args.spid is not None:
            for s in soundcard.all_speakers():
                if s.id == args.spid:
                    spname = s.name
                    break
        elif args.spname is not None:
            for s in soundcard.all_speakers():
                if s.name == args.spname:
                    spname = s.name
                    break
        if output_format is None:
            output_format = 'wav'
        if args.output_dir is not None:
            output_dir = Path(args.output_dir)
            common.mkdirs(output_dir)
        try:
            rectime = 0
            append = False
            with soundcard.get_microphone(id=spname, include_loopback=True).recorder(samplerate=args.samplerate) as mic:
                while rectime < args.rectime:
                    st = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    rec = mic.record(numframes=args.samplerate * args.duration)
                    et = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    rectime += args.duration
                    with io.BytesIO() as fo:
                        soundfile.write(fo, rec, args.samplerate, format=output_format)
                        val = fo.getvalue()
                        if output_dir is not None:
                            wav_file = output_dir / Path(f'{st}.{output_format}')
                            with open(wav_file, 'wb') as f:
                                f.write(val)
                        b64 = convert.bytes2b64str(val)
                        ret = f'{output_format},{st},{et},{st}.{output_format},'+b64
                        if args.output_csv is not None:
                            def write_csv(output_csv, row, append):
                                with open(output_csv, 'a' if append else 'w', encoding="utf-8") as f:
                                    print(row, file=f)
                            th = threading.Thread(target=write_csv, args=(args.output_csv, ret, append))
                            th.start()
                            append = True
                        else: common.print_format(ret, False, tm, None, False, pf=pf)
                        tm = time.perf_counter()
        except KeyboardInterrupt as e:
            logger.info(f'stop record. {e}')
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
        common.print_format("", False, tm, None, False, pf=pf)
        return 0, "", None

    def edgerun(self, opt:Dict[str, Any], tool:edge_tool.Tool, logger:logging.Logger, timeout:int, prevres:Any=None):
        """
        この機能のエッジ側の実行を行います

        Args:
            opt (Dict[str, Any]): オプション
            tool (edge.Tool): 通知関数などedge側のUI操作を行うためのクラス
            logger (logging.Logger): ロガー
            timeout (int): タイムアウト時間
            prevres (Any): 前コマンドの結果。pipeline実行の実行結果を参照する時に使用します。

        Yields:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果
        """
        import soundcard
        self.spname = None if not hasattr(self, 'spname') else self.spname
        if self.spname is None:
            if not opt['spid'] and not opt['spname']:
                sl = soundcard.all_speakers()
                if len(sl) == 0:
                    raise ValueError("No speakers.")
                self.spname = sl[0].name
            elif opt['spid']:
                for s in soundcard.all_speakers():
                    if s.id == opt['spid']:
                        self.spname = s.name
                        break
            elif opt['spname']:
                for s in soundcard.all_speakers():
                    if s.name == opt['spname']:
                        self.spname = s.name
                        break
        try:
            rectime = 0
            with soundcard.get_microphone(id=self.spname, include_loopback=True).recorder(samplerate=opt['samplerate']) as mic:
                while rectime < opt['rectime']:
                    st = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    rec = mic.record(numframes=opt['samplerate'] * opt['duration'])
                    et = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    rectime += opt['duration']
                    with io.BytesIO() as fo:
                        soundfile.write(fo, rec, opt['samplerate'], format=opt['output_format'])
                        val = fo.getvalue()
                        b64 = convert.bytes2b64str(val)
                        ret = f"{opt['output_format']},{st},{et},{st}.{opt['output_format']},"+b64
                        yield 0 if rectime < opt['rectime'] else 1, ret
                yield 1, ""
        except KeyboardInterrupt as e:
            logger.info(f'stop record. {e}')
        except Exception as e:
            logger.error(f'{e}', exc_info=True)
