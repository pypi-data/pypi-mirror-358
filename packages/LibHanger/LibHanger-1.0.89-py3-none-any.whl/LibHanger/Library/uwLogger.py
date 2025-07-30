import os
import logging
import LibHanger.Library.uwGetter as Getter
import functools
from LibHanger.Library.uwGlobals import *
from .uwConfig import cmnConfig
from .uwDeclare import uwDeclare as nd

# ネストの深さを管理する変数
local_depth = 0

def loggerDecorator(outputString, args_print = []):

    """
    関数の開始～終了でコンソールに文字列を出力するデコレーター
    """

    def _loggerDecorator(func):

        """
        関数の開始～終了でコンソールに文字列を出力するデコレーター
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            """
            デコレーターのラッパー
            """
            
            # 関数名の出力
            funcName = '(🟢 {0}) ... Execute'.format(outputString)
            print(funcName)
            logging.info(funcName)

            # 引数の出力
            if len(args_print) > 0 and len(kwargs) > 0:
                for argsStr in args_print:
                    if kwargs.get(argsStr) == None : continue
                    argsValue = 'args:{0}={1}'.format(str(argsStr), str(kwargs.get(argsStr)))
                    print(argsValue)
                    logging.info(argsValue)

            try:
                # 関数本体の実行
                ret = func(*args, **kwargs)
                
                # 実行終了の出力
                funcEnded = '(🔵 {0}) ... OK'.format(outputString)
                print(funcEnded)
                logging.info(funcEnded)

            except Exception as e:
                
                # 例外時エラーメッセージ
                errorInfo = "( 🔴 ERROR ) " + func.__name__ + "\n"\
                            "=== エラー内容 ===\n"\
                            "type: {0}\n"\
                            "args: {1}\n"\
                            "e自身: {2}".format(str(type(e)), str(e.args), str(e))
                            
                # エラーメッセージの出力
                logging.error(errorInfo)

                # 例外スロー
                raise 
            
            return ret

        return wrapper

    return _loggerDecorator

def setting(config: cmnConfig):

    """
    ロガー設定

    Parameters
    ----------
    config : cmnConfig
        共通設定クラス
    """

    # ログ出力先がない場合、作成する
    if os.path.exists(config.LogFolderName) == False:
        os.mkdir(config.LogFolderName)

    # ログファイル名サフィックス設定
    logFileName = getLogFileName(config)
    
    # ロガー設定
    logging.basicConfig(
        filename=os.path.join(config.LogFolderName, logFileName),
        level=config.LogLevel, 
        format=config.LogFormat)

def getLogFileName(config: cmnConfig):
    
    """
    ログファイル名取得

    Parameters
    ----------
    config : cmnConfig
        共通設定クラス
    """
    
    # 既定ログファイル名取得
    logFileName = config.LogFileName
    # ログファイル名サフィックス判定
    if config.LogFileNameSuffix != nd.logFileNameSuffix.suffixNone.value:
        
        # 拡張子を除いたファイル名取得
        logFileName_format = os.path.splitext(logFileName)[0] + '_{0}' + os.path.splitext(logFileName)[1]
        
        # ログファイル名にサフィックスを付与する
        fmt = getattr(Getter.datetimeFormat, nd.logFileNameSuffix.value_of(config.LogFileNameSuffix))
        logFileName = logFileName_format.format(Getter.getNow(fmt))

    # 戻り値を返す
    return logFileName

def setDepth(depth: int):
    
    # local_depthをグローバル変数として宣言
    global local_depth
    
    # ネストの深さを設定
    local_depth = depth

def getIndent(depth: int) -> str:
    """
    ネストの深さに応じたインデント文字列を生成する
    
    Parameters
    ----------
    depth : int
        ネストの深さ
    """
    return gv.config.LogDepth * depth + " "

def consoleLog(message: str):
    """
    コンソールにメッセージを出力する
    
    Parameters
    ----------
    message : str
        出力するメッセージ
    """
    print(message)

def getLogPrefix(prefixEmoji: str, prefixString: str):
    """
    ログプレフィックスを取得する
    
    Parameters
    ----------
    prefixEmoji : str
        ログプレフィックスとして出力する絵文字
    prefixString : str
        ログプレフィックスとして出力する文字列
    """
    return gv.config.LogPrefixFormat.format(prefixEmoji, prefixString.ljust(6) if prefixString else "(unknown)")

def getMethodStartPrefix():
    """
    メソッドStartログのプレフィックスを取得する
    """
    return getLogPrefix(gv.config.LogMethodStartEmoji, gv.config.LogMethodStartString)

def getMethodEndPrefix():
    """
    メソッドEndログのプレフィックスを取得する
    """
    return getLogPrefix(gv.config.LogMethodEndEmoji, gv.config.LogMethodEndString)

def getErrorPrefix():
    """
    Errorログのプレフィックスを取得する
    """
    return getLogPrefix(gv.config.LogErrorEmoji, gv.config.LogErrorString)

def getErrorCaption():
    """
    ErrorログのCaptionを取得する
    """
    return getLogPrefix(gv.config.LogErrorCaptionEmoji, gv.config.LogErrorCaptionString)

def getWarningPrefix():
    """
    Warningログのプレフィックスを取得する
    """
    return getLogPrefix(gv.config.LogWarningEmoji, gv.config.LogWarningString)

def getProcPrefix():
    """
    Procログのプレフィックスを取得する
    """
    return getLogPrefix(gv.config.LogProcEmoji, gv.config.LogProcString)

def startMethod(method_name: str, args_repr: str = ""):
    """
    メソッドの開始ログを出力する
    
    Parameters
    ----------
    method_name : str
        メソッド名
    args_repr : str, optional
        引数の文字列表現
    """
    # メッセージ生成
    logMessage = getIndent(local_depth) + f"{getMethodStartPrefix()} { method_name }" + ("" if args_repr == "" else " | args=(" + args_repr + ")")
    # コンソール出力
    consoleLog(logMessage)
    # ログ出力
    return logging.info(logMessage)

def endMethod(method_name: str, returnVal = None):
    """
    メソッドの終了ログを出力する
    
    Parameters
    ----------
    method_name : str
        メソッド名
    args_repr : str, optional
        メソッドの戻り値
    """
    # メッセージ生成
    logMessage = getIndent(local_depth) + f"{getMethodEndPrefix()} { method_name }" + ("" if returnVal == None else f" | return=({ returnVal })")
    # コンソール出力
    consoleLog(logMessage)
    # ログ出力
    return logging.info(logMessage)

def error(method_name, e: Exception):
    """
    メソッドのエラーログを出力する
    
    Parameters
    ----------
    method_name : str
        メソッド名
    e : Exception
        発生した例外
    """
    # エラーメッセージ生成
    errorInfoArray = [
        f"{ getErrorPrefix() } { method_name }",
        f"{ getErrorCaption() }",
        "type: {0}",
        "args: {1}",
        "exception: {2}"
    ]
    # ネストの深さに応じてインデントを追加
    errorInfo = ''
    for info in errorInfoArray:
        # エラーメッセージ文字列の前後にインデントと改行を追加
        errorInfo += getIndent(local_depth) + info + "\n"
    errorInfo = errorInfo.format(str(type(e)), str(e.args), str(e))
    # コンソール出力
    consoleLog(errorInfo)
    # ログ出力
    return logging.error(errorInfo, exc_info=True)

def warning(message: str, consoleLogging: bool = True):
    """
    警告ログを出力する

    Parameters
    ----------
    message : str
        出力するメッセージ
    consoleLogging : bool
        コンソール出力有無
    """
    # メッセージ生成
    logMessage = getIndent(local_depth) + f"{ getWarningPrefix() } { message }"
    # コンソール出力
    if consoleLogging:
        consoleLog(logMessage)
    # ログ出力
    return logging.warning(logMessage)

def info(message: str, consoleLogging: bool = True):
    """
    処理ログを出力する

    Parameters
    ----------
    message : str
        出力するメッセージ
    consoleLogging : bool
        コンソール出力有無
    """
    # メッセージ生成
    logMessage = getIndent(local_depth) + f"{ getProcPrefix() } { message }"
    # コンソール出力
    if consoleLogging:
        consoleLog(logMessage)
    # ログ出力
    return logging.info(logMessage)