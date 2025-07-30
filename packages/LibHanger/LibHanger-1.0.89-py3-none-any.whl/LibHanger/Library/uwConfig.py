import sys
import configparser
import os
import pathlib
import logging
import functools
from .uwDeclare import uwDeclare as ud
from .uwException import * 

class cmnConfigBase():
    
    def __init__(self):
        
        """
        コンストラクタ
        """
        
        self.config_ini = None
        """ iniファイル読込内容 """

        self.configFileList = []
        """ 設定ファイルリスト """
        
        self.config_ini = []
        """ 設定ファイル読込内容リスト """
        
    def setConfigValue(
        self,
        insVariableName: str, 
        config_ini: list, 
        section: str, 
        key: str, 
        dataType: type):
        
        """ 
        iniファイルから読み取った値をインスタンス変数セットする \n
        指定したセクション、キーが存在しない場合はインスタンス変数の元値を保持する
        
        Parameters
        ----------
        self : LibHanger.cmnConfig
            共通設定クラス
        insVariableName : str
            インスタンス変数名
        config_ini : list
            iniファイル読込内容List
        section : str
            iniファイルセクション名
        key : str
            iniファイルキー名
        dataType : type
            インスタンス変数のデータ型
        
        Notes
        -----
        
            @insVariableName
            ----------------
                インスタンス変数名をネストする場合は"."コロンで区切る 
                例:self.STRUCT.Test1の場合 ⇒ insVariableNameに"STRUCT.Test1"を指定する 
        
        """
        
        for ci in config_ini:
            keyExists = section in ci
            if keyExists and ci[section].get(key) != None:
                
                if dataType is str:
                    self.rsetattr(self, insVariableName, ci[section][key])
                elif dataType is int:
                    self.rsetattr(self, insVariableName, int(ci[section][key]))
                elif dataType is float:
                    self.rsetattr(self, insVariableName, float(ci[section][key]))
                elif dataType is list:
                    valueList:list = str(ci[section][key]).split(',')
                    self.rsetattr(self, insVariableName, valueList)

    def setInstanceMemberValues(self):

        """ 
        インスタンス変数に読み取った設定値をセットする
        
        Parameters
        ----------
        None
        """
        
        pass
    
    def rsetattr(self, obj, attr, val):
        
        """ 
        インスタンス変数の値を書き換える(ネスト用setattr)

        Parameters
        ----------
        obj : LibHanger.cmnConfig
            cmnConfigインスタンス
        attr : str
            インスタンス変数名
        val : object
            置き換える値
        """
        
        pre, _, post = attr.rpartition('.')
        return setattr(self.rgetattr(obj, pre) if pre else obj, post, val)

    def rgetattr(self, obj, attr, *args):
        
        """ 
        インスタンス変数を参照する(ネスト用getattr)

        Parameters
        ----------
        obj : LibHanger.cmnConfig
            cmnConfigインスタンス
        attr : str
            インスタンス変数名
        *args : object
            Unknown
        """
        
        def _getattr(obj, attr):
            return getattr(obj, attr, *args)
        return functools.reduce(_getattr, [obj] + attr.split('.'))
    
class cmnConfig(cmnConfigBase):

    """
    共通設定クラス
    """ 

    class settingValueStruct():

        """
        設定値構造体
        """ 

        class ConnectionString:
            
            """
            接続文字列
            """ 
            
            def __init__(self):
                
                """ 
                コンストラクタ
                """ 

                # メンバ変数初期化

                self.DatabaseKind = 'postgresql+psycopg2'
                """ データベース種類 """

                self.User = ''
                """ 接続ユーザー """
                
                self.Password = ''
                """ 接続パスワード """
                
                self.Host = ''
                """ 接続先ホスト """
                
                self.Port = ''
                """ 接続先ポート番号 """
                
                self.DatabaseName = ''
                """ 接続先データベース名 """

        class MailConfig:
            
            """
            メール設定
            """ 
            
            def __init__(self):
                
                """ 
                コンストラクタ
                """ 

                # メンバ変数初期化

                self.User = ''
                """ ユーザーアカウント """

                self.Password = ''
                """ ユーザーパスワード """

                self.Host = ''
                """ ホスト """

                self.SmtpPort = '587'
                """ 送信サーバーポート番号 """

    class startupConfig(cmnConfigBase):
        
        """
        スタートアップConfigクラス
        """

        def __init__(self):

            """
            コンストラクタ
            """
            
            self.configFolderPath = ''
            """ Configファイルが格納されているフォルダパス """

        def setInstanceMemberValues(self):

            """ 
            インスタンス変数に読み取った設定値をセットする
            
            Parameters
            ----------
            startupConfig_ini : ConfigParser
                スタートアップConfig用のConfigParser
            
            """
            
            # Configファイル格納場所
            self.setConfigValue('configFolderPath', self.config_ini,'PATH','CONFIG_FOLDER_PATH', str)

    def __init__(self):

        """
        コンストラクタ
        """

        # 基底側コンストラクタ
        super().__init__()
        
        self.LogFileName = 'default.log'
        """ ログファイル名 """

        self.LogFileNameSuffix:int = ud.logFileNameSuffix.suffixNone
        """ ログファイル名サフィックス """

        self.LogFolderName = 'log'
        """ ログ出力先フォルダ名 """

        self.LogFormat = '%(levelname)-7s : %(asctime)s : %(message)s'
        """ ログフォーマット定義 """

        self.LogLevel:int = logging.DEBUG
        """ ログレベル """

        self.LogPrefixFormat = '[ {} {} ]'
        """ ログプレフィックスフォーマット """

        self.LogMethodStartEmoji = '🟢'
        """ ログメソッドStart絵文字 """
        self.LogMethodStartString = 'START '
        """ ログメソッドStart文字列 """

        self.LogMethodEndEmoji = '🟢'
        """ ログメソッドEnd絵文字 """
        self.LogMethodEndString = 'END   '
        """ ログメソッドEnd文字列 """

        self.LogErrorEmoji = '❌'
        """ ログError絵文字 """
        self.LogErrorString = 'ERROR '
        """ ログError文字列 """

        self.LogErrorCaptionEmoji = '🔴'
        """ ログErrorCaption絵文字 """
        self.LogErrorCaptionString = 'Error Occurred'
        """ ログErrorCaption文字列 """

        self.LogWarningEmoji = '⚠️'
        """ ログWarning絵文字 """
        self.LogWarningString = 'WARN  '
        """ ログWarning文字列 """

        self.LogProcEmoji = '🔵'
        """ ログProc絵文字 """
        self.LogProcString = 'PROC  '
        """ ログProc文字列 """

        self.LogDepth = '+'
        """ ログdepth文字列 """

        self.ErrorLogFileName = 'error.log'
        """ エラーログファイル名 """
        
        self.ConnectionString = self.settingValueStruct.ConnectionString()
        """ 接続文字列 """

        self.MailConfig = self.settingValueStruct.MailConfig()
        """ メール設定 """

        self.scriptFilePath = ''
        """ スクリプトファイルパス """

        self.startupCfg = self.startupConfig()
        """ スタートアップConfig """

        self.setConfigFileName('LibHanger.ini')
        """ 設定ファイル追加 """
        
    def setConfigFileName(self, fileName):
        
        """ 
        設定ファイル名を設定する
        """
        self.configFileList.append(fileName)
    
    def getConfig(self, _scriptFilePath: str, configFileDir: str = ''):
        
        """
        共通設定を取得する
        
        Parameters
        ----------

        _scriptFilePath : str
            スクリプトファイルパス
        configFileDir : str
            iniファイルがあるディレクトリ(相対パス)
        """
        
        # iniファイルをconfig_iniにセット
        for configFileName in self.configFileList:
            self.setConfig(_scriptFilePath, configFileDir, configFileName)
        
        # 各設定値をインスタンス変数にセット
        self.setInstanceMemberValues()
        
    def setConfig(self, _scriptFilePath: str, configFileDir: str = '', configFileName: str = ''):

        """ 
        設定ファイルを読み込む 
        
        Parameters
        ----------
        self : LibHanger.cmnConfig
            共通設定クラス
        _scriptFilePath : str
            スクリプトファイルパス
        configFileDir : str
            iniファイルがあるディレクトリ(相対パス)
        
        """
        
        # configparser宣言
        config_ini = configparser.ConfigParser()

        # Configファイル読込前の設定情報取得([呼び出し元pythonファイル名.ini])
        self.startupCfg = self.getStartupConfig(_scriptFilePath)
        if configFileDir == '':
            configFileDir = self.startupCfg.configFolderPath
            
        # スクリプトファイルパスをセット
        self.scriptFilePath = _scriptFilePath
        
        # スクリプトファイルの場所から見たiniファイル相対パス取得
        iniFileDirPath = configFileName \
            if configFileDir == '' else os.path.join(configFileDir, configFileName)
        # スクリプトファイルの絶対パス取得
        iniScriptPathAbs = pathlib.Path(os.path.abspath(os.path.dirname(_scriptFilePath)))
        # iniファイルパス取得
        iniFilePath = os.path.join(iniScriptPathAbs, iniFileDirPath)

        # iniファイル存在確認
        if os.path.exists(iniFilePath): 
            
            # iniファイル読込
            config_ini.read(iniFilePath, encoding='utf-8')
            
            # 読込内容をインスタンス変数に設定する
            self.config_ini.append(config_ini)
        
    def getStartupConfig(self, _scriptFilePath: str):

        """ 
        スタートアップ設定ファイル読込
        
        Parameters
        ----------
        _scriptFilePath : str
            スクリプトファイルパス
        
        """

        # startupConfigクラス
        startupCfg = self.startupConfig()
        # configparser宣言
        startupCfg.config_ini = []
        
        # configparser宣言
        config_ini = configparser.ConfigParser()
        
        # ファイル名(拡張子なし)取得
        startupConfigFileNameNotExtention = pathlib.Path(_scriptFilePath).stem
        # スタートアップ設定ファイル名取得
        startupConfigFileName = startupConfigFileNameNotExtention + '.ini'
        # スタートアップ設定ファイルのパス取得
        startupConfigFilePath = os.path.join(os.path.dirname(_scriptFilePath), startupConfigFileName)
        # スタートアップ設定ファイルの存在有無
        if os.path.exists(startupConfigFilePath):
            
            # iniファイル読込
            config_ini.read(startupConfigFilePath, encoding='utf-8')

            # 読込内容をインスタンス変数に設定する
            startupCfg.config_ini.append(config_ini)
            
            # メンバ変数に値セット
            startupCfg.setInstanceMemberValues()
            
        return startupCfg

    def setInstanceMemberValues(self):
        
        """ 
        インスタンス変数に読み取った設定値をセットする
        
        Parameters
        ----------
        None
        """
        
        # ログファイル名
        self.setConfigValue('LogFileName', self.config_ini,'DEFAULT','LOGFILE_NAME', str)
        # ログファイル名サフィックス
        self.setConfigValue('LogFileNameSuffix', self.config_ini,'DEFAULT','LOGFILE_NAME_SUFFIX', int)
        # ログファイル格納先ディレクトリ
        self.setConfigValue('LogFolderName', self.config_ini,'DEFAULT','LOGFOLDER_NAME', str)
        # ログフォーマット
        self.setConfigValue('LogFormat', self.config_ini,'DEFAULT','LOGFORMAT', str)
        # ログレベル
        self.setConfigValue('LogLevel', self.config_ini,'DEFAULT','LOGLEVEL', int)
        # ログプレフィックスフォーマット
        self.setConfigValue('LogPrefixFormat', self.config_ini,'DEFAULT','LOG_PREFIX_FORMAT', str)
        # ログメソッドStart絵文字
        self.setConfigValue('LogMethodStartEmoji', self.config_ini,'DEFAULT','LOG_METHOD_START_EMOJI', str)
        # ログメソッドStart文字列
        self.setConfigValue('LogMethodStartString', self.config_ini,'DEFAULT','LOG_METHOD_START_STRING', str)
        # ログメソッドEnd絵文字
        self.setConfigValue('LogMethodEndEmoji', self.config_ini,'DEFAULT','LOG_METHOD_END_EMOJI', str)
        # ログメソッドEnd文字列
        self.setConfigValue('LogMethodEndString', self.config_ini,'DEFAULT','LOG_METHOD_END_STRING', str)
        # ログError絵文字
        self.setConfigValue('LogErrorEmoji', self.config_ini,'DEFAULT','LOG_ERROR_EMOJI', str)
        # ログError文字列
        self.setConfigValue('LogErrorString', self.config_ini,'DEFAULT','LOG_ERROR_STRING', str)
        # ログErrorCaption絵文字
        self.setConfigValue('LogErrorCaptionEmoji', self.config_ini,'DEFAULT','LOG_ERROR_CAPTION_EMOJI', str)
        # ログErrorCaption文字列
        self.setConfigValue('LogErrorCaptionString', self.config_ini,'DEFAULT','LOG_ERROR_CAPTION_STRING', str)
        # ログWarning絵文字
        self.setConfigValue('LogWarningEmoji', self.config_ini,'DEFAULT','LOG_WARNING_EMOJI', str)
        # ログWarning文字列
        self.setConfigValue('LogWarningString', self.config_ini,'DEFAULT','LOG_WARNING_STRING', str)
        # ログProc絵文字
        self.setConfigValue('LogProcEmoji', self.config_ini,'DEFAULT','LOG_PROC_EMOJI', str)
        # ログProc文字列
        self.setConfigValue('LogProcString', self.config_ini,'DEFAULT','LOG_PROC_STRING', str)
        # ログdepth文字列
        self.setConfigValue('LogDepth', self.config_ini,'DEFAULT','LOG_DEPTH', str)

        # データベース種類
        self.setConfigValue('ConnectionString.DatabaseKind', self.config_ini,'CONNECTION_STRING','DATABASE_KIND', str)
        # 接続ユーザー
        self.setConfigValue('ConnectionString.User', self.config_ini,'CONNECTION_STRING','USER', str)
        # 接続パスワード
        self.setConfigValue('ConnectionString.Password', self.config_ini,'CONNECTION_STRING','PASSWORD', str)
        # ホスト名
        self.setConfigValue('ConnectionString.Host', self.config_ini,'CONNECTION_STRING','HOST', str)
        # ポート番号
        self.setConfigValue('ConnectionString.Port', self.config_ini,'CONNECTION_STRING','PORT', str)
        # データベース名
        self.setConfigValue('ConnectionString.DatabaseName', self.config_ini,'CONNECTION_STRING','DATABASE_NAME', str)

        # メールユーザーアカウント
        self.setConfigValue('MailConfig.User', self.config_ini,'MAIL','USER', str)
        # メールユーザーパスワード
        self.setConfigValue('MailConfig.Password', self.config_ini,'MAIL','PASSWORD', str)
        # メールホスト
        self.setConfigValue('MailConfig.Host', self.config_ini,'MAIL','HOST', str)
        # 受信サーバーポート
        self.setConfigValue('MailConfig.Port', self.config_ini,'MAIL','PORT', str)

    def getErrorLogFilaPath(self):
        
        """
        エラーログ出力先パスを取得する
        """
        
        # エラーログ出力先
        return os.path.join(self.LogFolderName, self.ErrorLogFileName)