import datetime
import platform
from LibHanger.Library.uwDeclare import uwDeclare as de

class datetimeFormat():
    
    """
    日付書式
    """
    
    yyyyMMddhhmmss = '%Y%m%d%H%M%S'
    """ yyyyMMddhhmmss """

    yyyyMMddhhmm = '%Y%m%d%H%M%'
    """ yyyyMMddhhmm """

    yyyyMMdd = '%Y%m%d'
    """ yyyyMMdd """

    yyMMdd = '%y%m%d'
    """ yyMMdd """

    MMdd = '%m%d'
    """ MMdd """

    updinfo = '%Y/%m/%d %H:%M:%S'
    """ updinfo列用 """

def getPlatform():

    """ 
    プラットフォーム取得
    
    Parameters
    ----------
    none
    """

    # プラットフォーム取得
    pf = platform.system()

    # 戻り値を返す
    pfs = de.platFormStruct()
    if pf == 'Windows':
        return pfs.win
    elif pf == 'Darwin':
        return pfs.mac
    elif pf == 'Linux':
        return pfs.linux

def getNow(fmt:str=''):

    """ 
    現在日時取得
    
    Parameters
    ----------
    fmt : str
        変換する日付書式
    """
    
    # 日本時刻取得
    nowDateTime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

    return nowDateTime if fmt == '' else nowDateTime.strftime(fmt)

def addDays(targetDate, addDays: int):
    
    """ 
    対象日付の日数を加算する
    
    Parameters
    ----------
    targetDate :
        加算対象日付
    addDays : int
        加算する日数
    """

    # 戻り値を返す
    return targetDate + datetime.timedelta(days=addDays)

def getListMargeString(delimiter:str, targetList:list):

    """ 
    対象リストを特定の文字列で連結して返す
    
    Parameters
    ----------
    delimiter : str
        デリミタ文字
    targetList : list
        対象リスト
    """

    return delimiter.join(targetList) if len(targetList) > 1 else targetList[0]
